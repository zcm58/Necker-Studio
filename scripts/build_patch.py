"""Create direct sparse Inno payloads from an exact retained release inventory.

Never reconstruct an old baseline from its source tag. Authenticate the preserved
installer against GitHub, and supply the SHA-256 of its installed inventory.
"""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from updates import PREFIX, version_key


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(path):
    records = json.loads(path.read_text(encoding='utf-8'))
    seen = set()
    if not isinstance(records, dict) or not records:
        raise ValueError('Invalid inventory.')
    for name, value in records.items():
        parts = name.split('/')
        if PureWindowsPath(name).is_absolute() or '\\' in name or any(
            part in ('', '.', '..') or part.endswith(('.', ' ')) or any(c in part for c in ':";|<>?*\r\n') or
            PureWindowsPath(part).is_reserved() for part in parts):
            raise ValueError('Unsafe inventory path.')
        if parts[0] not in ('app', 'runtime', 'licenses') and name not in ('NeckerExperiment.exe', 'NeckerUpdater.exe'):
            raise ValueError('Unknown inventory root.')
        if name.casefold() in seen or not isinstance(value, str) or not re.fullmatch('[a-f0-9]{64}', value):
            raise ValueError('Invalid inventory record.')
        seen.add(name.casefold())
    return records


def prepare(bundle, output, baseline=None, baseline_sha256=None, from_version=None):
    version = json.loads((bundle / 'app/release.json').read_text())['version']
    version_key(version)
    target = inventory(bundle / 'manifest.json')
    if any(digest(bundle / path) != sha for path, sha in target.items()):
        raise ValueError('Target bundle changed after verification.')
    source = {}
    if baseline is not None:
        if digest(baseline) != baseline_sha256:
            raise ValueError('Source inventory does not match its authenticated digest.')
        source = inventory(baseline)
        if version_key(from_version) >= version_key(version):
            raise ValueError('Patch target must be newer than its source.')
        if set(source) - set(target):
            raise ValueError('Removed or renamed files require a full installer.')
    output.mkdir(parents=True, exist_ok=False)
    changed = {path: sha for path, sha in target.items() if source.get(path) != sha}
    # Separate runtime compression from app files. Full repair can skip unchanged
    # runtime bytes; a patch never contains unchanged dependency files at all.
    names = sorted(changed, key=lambda name: (0 if name.startswith('runtime/') else 1, name))
    lines = []
    previous_group = None
    for name in names:
        group = name.split('/')[0]
        flags = 'ignoreversion' + (' solidbreak' if group != previous_group else '')
        directory = str(PureWindowsPath(name).parent)
        destination = '{app}' + (('\\' + directory) if directory != '.' else '')
        relative = str(PureWindowsPath(name)).replace("'", "''")
        lines.append(f'Source: "{bundle / name}"; DestDir: "{destination}"; Flags: {flags}; Check: NeedsFile(\'{relative}\', \'{target[name]}\')')
        previous_group = group
    (output / 'payload.iss').write_text('\n'.join(lines) + '\n', encoding='utf-8-sig')
    record = {'version': version, 'from_version': from_version, 'source_inventory_sha256': baseline_sha256,
              'payload_files': len(changed), 'retained_files': len(target) - len(changed),
              'payload_bytes': sum((bundle / path).stat().st_size for path in changed)}
    (output / 'build.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    return record


def release_metadata(dist, version, records):
    full = dist / f'{PREFIX}-Setup-{version}-x64.exe'
    if not full.is_file():
        raise ValueError('Every release must retain a full installer.')
    entries, artifacts = [], [full]
    for record in records:
        source = record['from_version']
        name = f'{PREFIX}-Patch-{source}-to-{version}-x64.exe'
        path = dist / name
        entries.append({'from_version': source, 'source_inventory_sha256': record['source_inventory_sha256'],
                        'asset_name': name, 'size_bytes': path.stat().st_size, 'sha256': digest(path)})
        artifacts.append(path)
    metadata = dist / f'{PREFIX}-Update-{version}.json'
    metadata.write_text(json.dumps({'schema_version': 1, 'target_version': version,
                         'platform': 'windows-x64', 'patches': entries}, indent=2), encoding='utf-8')
    artifacts.append(metadata)
    (dist / 'SHA256SUMS.txt').write_text(''.join(f'{digest(path)}  {path.name}\n' for path in artifacts), encoding='ascii')
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--finalize', action='store_true')
    parser.add_argument('--dist', type=Path)
    parser.add_argument('--version')
    parser.add_argument('--records', type=Path, nargs='*', default=[])
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--baseline-sha256')
    parser.add_argument('--from-version')
    args = parser.parse_args()
    if args.finalize:
        print(release_metadata(args.dist, args.version, [json.loads(path.read_text()) for path in args.records]))
        return
    if args.output is None or args.bundle is None:
        parser.error('--bundle and --output are required.')
    if not args.output.resolve().is_relative_to(PROJECT / 'build'):
        parser.error('Output must be a new folder inside build/.')
    print(json.dumps(prepare(args.bundle.resolve(), args.output.resolve(), args.baseline, args.baseline_sha256, args.from_version)))


if __name__ == '__main__':
    main()
