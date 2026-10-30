#!/usr/bin/env python3
"""Preview or copy LPM Plasma recipes into an EXISTING local git checkout.

Never overwrites by default. Before --apply, commit/stash local changes and
review `git diff` afterwards. GitLab access is not required by this script.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

BUNDLE = Path(__file__).resolve().parent.parent

def main():
    p = argparse.ArgumentParser()
    p.add_argument('checkout',type=Path,help='Existing git clone of lpm-org/packages')
    p.add_argument('--apply',action='store_true',help='Actually copy changed/new recipes')
    args=p.parse_args()
    target=args.checkout.expanduser().resolve()
    if not (target/'.git').exists():
        p.error('Expected an existing git checkout, including .git')
    specs=json.loads((BUNDLE/'package-chain.json').read_text())['packages']
    changed=added=identical=0
    for name in sorted(specs):
        source=BUNDLE/name/(name+'.lpmbuild')
        dest=target/name/(name+'.lpmbuild')
        if dest.exists() and dest.read_bytes()==source.read_bytes():
            identical+=1
            continue
        status='REPLACE' if dest.exists() else 'ADD'
        print(status,dest.relative_to(target))
        changed+=dest.exists();added+=not dest.exists()
        if args.apply:
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,dest)
    print(f'Existing and changed: {changed}, new: {added}, identical: {identical}')
    if not args.apply:print('Dry run; rerun with --apply to copy. Review package names and dependency differences first.')
    else:print('Copied recipes; review git diff. Source hashes MUST be locked first.')

if __name__=='__main__':main()
