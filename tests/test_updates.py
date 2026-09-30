"""Updater trust, cancellation, patch selection and cache regressions; no network."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
from urllib.request import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import updates as u


def raw_asset(name, payload=b'installer', version='1.3', identity=11):
    return dict(name=name, id=identity, size=len(payload), state='uploaded',
                digest='sha256:' + hashlib.sha256(payload).hexdigest(),
                url=u.API + f'/assets/{identity}')


def raw_release(version='1.3'):
    return dict(tag_name='v' + version, draft=False, prerelease=False,
                assets=[raw_asset(f'{u.PREFIX}-Setup-{version}-x64.exe', b'x' * 100)])


class ReleaseTests(unittest.TestCase):
    def test_numeric_versions_and_no_downgrades_or_prereleases(self):
        releases = [raw_release('1.9'), raw_release('1.10')]
        self.assertEqual(u.select_release(releases, '1.8')[0].version, '1.10')
        self.assertIsNone(u.select_release(releases, '1.10')[0])
        releases[1]['prerelease'] = True
        self.assertEqual(u.select_release(releases, '1.8')[0].version, '1.9')
        releases[0]['draft'] = True
        self.assertIsNone(u.select_release(releases, '1.8')[0])

    def test_missing_digest_is_available_but_not_downloadable(self):
        raw = raw_release()
        raw['assets'][0]['digest'] = None
        result, _ = u.select_release([raw], '1.2')
        self.assertEqual(result.version, '1.3')
        self.assertIsNone(result.asset)
        self.assertIn('SHA-256', result.reason)

    def test_asset_identity_and_limits(self):
        name = f'{u.PREFIX}-Setup-1.3-x64.exe'
        for replacement in ({'url': 'https://evil.example/a'}, {'size': True}, {'size': u.MAX_BYTES+1},
                            {'id': -1}, {'digest': 'md5:' + 'a'*32}, {'state': 'new'}, {'name': 'other.exe'}):
            with self.subTest(replacement=replacement):
                raw = raw_asset(name); raw.update(replacement)
                with self.assertRaises(u.UpdateError): u.parse_asset(raw, name, '1.3')

    def test_redirect_rejects_other_hosts_and_does_not_forward_tokens(self):
        request = Request(u.API + '/assets/11', headers={'Authorization': 'Bearer private'})
        handler = u.SafeRedirect()
        result = handler.redirect_request(request, None, 302, '', {}, 'https://release-assets.githubusercontent.com/example')
        self.assertIsNone(result.get_header('Authorization'))
        for url in ('http://github.com/file', 'https://github.com.evil.example/a', 'https://api.github.com:444/a', 'https://evil.example/a'):
            with self.subTest(url=url), self.assertRaises(u.UpdateError):
                handler.redirect_request(request, None, 302, '', {}, url)

    def test_small_direct_patch_requires_matching_inventory(self):
        raw = raw_release()
        result, _ = u.select_release([raw], '1.2')
        name = f'{u.PREFIX}-Patch-1.2-to-1.3-x64.exe'
        patch_raw = raw_asset(name, identity=12)
        raw['assets'].append(patch_raw)
        document = dict(schema_version=1, target_version='1.3', platform='windows-x64', patches=[dict(
            from_version='1.2', asset_name=name, size_bytes=patch_raw['size'],
            sha256=patch_raw['digest'][7:], source_inventory_sha256='b'*64)])
        selected = u.choose_patch(result, raw, document, '1.2', 'b'*64)
        self.assertEqual(selected.asset.kind, 'patch')
        self.assertEqual(u.choose_patch(result, raw, document, '1.2', 'c'*64).asset.kind, 'full')
        document['patches'][0]['sha256'] = 'a'*64
        with self.assertRaises(u.UpdateError): u.choose_patch(result, raw, document, '1.2', 'b'*64)

    def test_oversized_or_wrong_repository_metadata_never_runs(self):
        with self.assertRaises(u.UpdateError): u._url('https://evil.example/releases')
        self.assertIsNone(u.registered_install(Path(tempfile.gettempdir())))


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.cache = Path(self.temporary.name) / 'updates'
        self.payload = b'checked installer'
        self.raw = raw_asset(f'{u.PREFIX}-Setup-1.3-x64.exe', self.payload)
        self.asset = u.parse_asset(self.raw, self.raw['name'], '1.3')

    def tearDown(self):
        self.temporary.cleanup()

    def response(self, payload):
        response = io.BytesIO(payload)
        response.geturl = lambda: 'https://release-assets.githubusercontent.com/asset'
        return response

    def test_verified_download_reuse_and_bounded_cleanup(self):
        self.cache.mkdir()
        unrelated = self.cache / 'results.txt'; unrelated.write_text('keep')
        old = self.cache / ('download-' + 'a'*64 + '.exe'); old.write_text('old')
        with patch.object(u, 'refresh_asset'), patch.object(u, '_open', return_value=self.response(self.payload)) as network:
            path = u.download(self.asset, cache=self.cache)
            self.assertEqual(path.read_bytes(), self.payload)
            self.assertFalse(old.exists())
            self.assertTrue(unrelated.exists())
            self.assertEqual(u.download(self.asset, cache=self.cache), path)
            network.assert_called_once()

    def test_corruption_extra_short_bytes_and_cancellation_leave_no_partial(self):
        for payload in (self.payload + b'!', b'bad', b'X'*len(self.payload)):
            with self.subTest(payload=payload), patch.object(u, 'refresh_asset'), patch.object(u, '_open', return_value=self.response(payload)):
                with self.assertRaises(u.UpdateError): u.download(self.asset, cache=self.cache)
                self.assertEqual(list(self.cache.glob('*.part')), [])
                self.assertEqual(list(self.cache.glob('*.exe')), [])
        cancel = threading.Event(); cancel.set()
        with patch.object(u, 'refresh_asset'), patch.object(u, '_open', return_value=self.response(self.payload)):
            with self.assertRaises(u.Cancelled): u.download(self.asset, cache=self.cache, cancel=cancel)
        self.assertEqual(list(self.cache.glob('*.part')), [])

    def test_cache_lock_blocks_second_writer(self):
        with u.cache_lock(self.cache):
            with self.assertRaises(u.UpdateError):
                with u.cache_lock(self.cache): pass

    def test_hardlinked_cache_file_is_rejected(self):
        self.cache.mkdir()
        original = self.cache / 'original'; original.write_text('user data')
        link = self.cache / ('download-' + self.asset.digest + '.exe')
        link.hardlink_to(original)
        with patch.object(u, 'refresh_asset'), self.assertRaises(u.UpdateError):
            u.download(self.asset, cache=self.cache)
        self.assertEqual(original.read_text(), 'user data')

    def test_asset_replaced_on_github_blocks_reuse_and_install(self):
        raw = raw_release(); raw['assets'] = [dict(self.raw, digest='sha256:'+'a'*64)]
        with patch.object(u, '_json', return_value=raw), self.assertRaises(u.UpdateError):
            u.refresh_asset(self.asset, '', None)

    def test_source_checkout_cannot_launch_installer(self):
        with patch.object(u, 'registered_install', return_value=None), patch.object(u.subprocess, 'Popen') as spawn:
            with self.assertRaises(u.UpdateError): u.begin_install(self.asset, self.cache / 'installer.exe')
            spawn.assert_not_called()


if __name__ == '__main__': unittest.main()
