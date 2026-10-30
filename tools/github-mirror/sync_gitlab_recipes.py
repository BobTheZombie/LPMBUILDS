#!/usr/bin/env python3
"""Copy GitLab's tracked package tree into the GitHub mirror, preserving automation."""
import argparse
from pathlib import Path
import shutil
import subprocess

KEEP_PREFIXES = ('.github/', 'tools/github-mirror/')
KEEP_FILES = {'README-GITHUB-MIRROR.md'}

def reserved(path):
    return (path == '.git' or path.startswith('.git/')
            or any(path == p.rstrip('/') or path.startswith(p) for p in KEEP_PREFIXES)
            or path in KEEP_FILES)

def run(source, target):
    if not (source / '.git').exists() or not (target / '.git').exists():
        raise SystemExit('Both GitLab source and GitHub target must be git checkouts')
    raw = subprocess.check_output(['git', '-C', str(source), 'ls-files', '-z'])
    upstream = {}
    for entry in raw.split(b'\0'):
        if not entry: continue
        rel = entry.decode('utf-8')
        if reserved(rel): continue
        origin = source / rel
        if not origin.is_file() or origin.is_symlink():
            raise SystemExit(f'Unsupported GitLab entry: {rel}')
        upstream[rel] = origin
    if not any(p.endswith('.lpmbuild') for p in upstream):
        raise SystemExit('GitLab checkout contains no .lpmbuild files; refusing sync')
    tracked = subprocess.check_output(['git', '-C', str(target), 'ls-files', '-z'])
    old = {e.decode('utf-8') for e in tracked.split(b'\0') if e}
    removed = 0
    for rel in sorted(old - upstream.keys()):
        if reserved(rel): continue
        dest = target / rel
        if dest.is_file() or dest.is_symlink():
            dest.unlink()
            removed += 1
    updated = 0
    for rel, origin in upstream.items():
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_dir() or dest.is_symlink():
            raise SystemExit(f'Unsafe mirror destination: {rel}')
        if not dest.exists() or dest.read_bytes() != origin.read_bytes():
            shutil.copy2(origin, dest)
            updated += 1
    print(f'GitLab tracked: {len(upstream)}; updated: {updated}; removed stale: {removed}')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--target', type=Path, default=Path('.'))
    a = p.parse_args()
    run(a.source.resolve(), a.target.resolve())
