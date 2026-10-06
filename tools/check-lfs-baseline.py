#!/usr/bin/env python3
"""Check declarative LFS recipe metadata without sourcing executable recipes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def array(text, key):
    match = re.search(r'^' + re.escape(key) + r'=\((.*?)\)\s*$', text, re.M | re.S)
    if not match:
        raise ValueError(f'missing {key} array')
    # Baseline recipe arrays intentionally use quoted literal strings.
    return re.findall(r'"([^"\n]*)"', match.group(1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, help='directory of downloaded archives')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'metadata/lfs-13.1.json').read_text())
    errors = []
    recipes = sorted(ROOT.rglob('*.lpmbuild'))
    for path in recipes:
        result = subprocess.run(['bash', '-n', str(path)], text=True, capture_output=True)
        if result.returncode:
            errors.append(f'{path.relative_to(ROOT)}: {result.stderr.strip()}')
        if re.search(r'^(?:<{7}|={7}|>{7})', path.read_text(), re.M):
            errors.append(f'{path.relative_to(ROOT)}: unresolved conflict marker')
    for item in manifest['packages'] + manifest['additional_packages']:
        path = ROOT / item['package'] / (item['package'] + '.lpmbuild')
        text = path.read_text()
        if f'VERSION="{item["version"]}"' not in text:
            errors.append(f'{item["package"]}: version differs from manifest')
        try:
            sources, digests = array(text, 'SOURCE'), array(text, 'SHA256SUMS')
        except ValueError as exc:
            errors.append(f'{item["package"]}: {exc}')
            continue
        if len(sources) != len(digests):
            errors.append(f'{item["package"]}: source/checksum counts differ')
        for source, digest in zip(sources, digests):
            if not re.fullmatch(r'[a-f0-9]{64}', digest):
                errors.append(f'{item["package"]}: invalid SHA-256 for {source}')
                continue
            remote = source.startswith('https://')
            if remote and args.source_dir is None:
                continue
            source_path = args.source_dir / source.rsplit('/', 1)[1] if remote else path.parent / source
            if not source_path.is_file():
                errors.append(f'{item["package"]}: missing source {source_path}')
                continue
            actual = hashlib.file_digest(source_path.open('rb'), 'sha256').hexdigest()
            if actual != digest:
                errors.append(f'{item["package"]}: checksum mismatch for {source}')
        if sources and item['sha256'] != digests[0]:
            errors.append(f'{item["package"]}: primary digest differs from manifest')
    for item in manifest['compatibility_packages']:
        text = (ROOT / item['package'] / (item['package'] + '.lpmbuild')).read_text()
        if f'VERSION="{item["version"]}"' not in text or item['requires'] not in array(text, 'REQUIRES'):
            errors.append(f'{item["package"]}: compatibility dependency mismatch')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(recipes)} recipes parse; {len(manifest["packages"])} LFS recipes match the baseline.')
    if args.source_dir:
        print('PASS: downloaded archives and local sources match their SHA-256 digests.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
