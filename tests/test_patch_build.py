"""Sparse packaging must preserve the runtime and use authenticated baselines."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'scripts'))
import build_patch as b


class PatchBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.bundle = self.root / 'bundle'
        (self.bundle / 'app').mkdir(parents=True)
        (self.bundle / 'runtime').mkdir()
        (self.bundle / 'runtime/python.exe').write_bytes(b'unchanged runtime')
        (self.bundle / 'app/main.py').write_text('new source')
        (self.bundle / 'app/release.json').write_text('{"version":"1.2"}')
        self.records = {p.relative_to(self.bundle).as_posix(): b.digest(p) for p in self.bundle.rglob('*') if p.is_file()}
        (self.bundle / 'manifest.json').write_text(json.dumps(self.records))
        source = dict(self.records, **{'app/main.py': hashlib.sha256(b'old source').hexdigest()})
        self.source = self.root / 'source.json'; self.source.write_text(json.dumps(source))

    def tearDown(self): self.temporary.cleanup()

    def test_patch_excludes_identical_runtime_and_full_uses_hash_checks(self):
        record = b.prepare(self.bundle, self.root / 'patch', self.source, b.digest(self.source), '1.1')
        self.assertEqual(record['payload_files'], 1)
        self.assertEqual(record['retained_files'], 2)
        payload = (self.root / 'patch/payload.iss').read_text(encoding='utf-8-sig')
        self.assertNotIn('python.exe', payload)
        self.assertIn('NeedsFile', payload)
        b.prepare(self.bundle, self.root / 'full')
        self.assertIn('solidbreak', (self.root / 'full/payload.iss').read_text(encoding='utf-8-sig'))

    def test_bad_baseline_or_modified_target_is_rejected(self):
        with self.assertRaises(ValueError): b.prepare(self.bundle, self.root / 'bad', self.source, 'a'*64, '1.1')
        (self.bundle / 'app/main.py').write_text('tampered')
        with self.assertRaises(ValueError): b.prepare(self.bundle, self.root / 'bad')

    def test_removal_or_downgrade_requires_full_installer(self):
        with self.assertRaises(ValueError): b.prepare(self.bundle, self.root / 'bad', self.source, b.digest(self.source), '1.3')
        source = json.loads(self.source.read_text()); source['app/removed.py'] = 'b'*64
        self.source.write_text(json.dumps(source))
        with self.assertRaises(ValueError): b.prepare(self.bundle, self.root / 'bad', self.source, b.digest(self.source), '1.1')

    def test_unsafe_or_duplicate_inventory_paths_rejected(self):
        for name in ('../settings.json', 'app/../../secret', 'app/COM1.txt', 'app/x:stream', 'app/x.', 'app//x'):
            with self.subTest(name=name):
                self.source.write_text(json.dumps({name:'a'*64}))
                with self.assertRaises(ValueError): b.inventory(self.source)
        self.source.write_text(json.dumps({'app/main.py':'a'*64,'app/MAIN.py':'b'*64}))
        with self.assertRaises(ValueError): b.inventory(self.source)


if __name__ == '__main__': unittest.main()
