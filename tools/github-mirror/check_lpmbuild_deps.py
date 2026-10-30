#!/usr/bin/env python3
"""Audit LPM hard dependency arrays against NAME and PROVIDES without executing recipes."""
import argparse
from collections import defaultdict
import difflib
from pathlib import Path
import re
import shlex
import sys

def parse_array(content, field):
    m = re.search(r'(?ms)^' + re.escape(field) + r'\s*=\s*\((.*?)\)', content)
    if not m: return []
    lex = shlex.shlex(m.group(1), posix=True)
    lex.whitespace_split = True
    lex.commenters = '#'
    try:
        return [x for x in lex if re.fullmatch(r'[A-Za-z0-9_.+:-]+', x)]
    except ValueError:
        # PROVIDES sometimes contains shell expansions; don't evaluate recipes.
        if field == 'PROVIDES':
            return []
        raise

def scan(root):
    index = defaultdict(list)
    placeholders = set()
    for path in root.rglob('*.lpmbuild'):
        text = path.read_text(encoding='utf-8', errors='replace')
        m = re.search(r'(?m)^NAME\s*=\s*["\']([^"\']+)', text)
        name = m.group(1) if m else path.stem
        names = [name] + parse_array(text, 'PROVIDES')
        for value in names:
            if '$' not in value:
                index[value].append(path)
        if 'Placeholder package for' in text or 'https://example.com/' in text:
            placeholders.add(path)
    return index, placeholders

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--recipe', type=Path, required=True)
    a = p.parse_args()
    index, stubs = scan(a.repo)
    if not index:
        raise SystemExit('No package names indexed')
    text = a.recipe.read_text()
    print(f'Indexed {len(index)} package/provider identifiers')
    failures = 0
    for field in ('BUILD_REQUIRES', 'REQUIRES', 'RECOMMENDS', 'SUGGESTS'):
        deps = list(dict.fromkeys(parse_array(text, field)))
        missing, stubbed = [], []
        for dep in deps:
            locations = index.get(dep, [])
            if not locations:
                missing.append(dep)
            elif all(x in stubs for x in locations):
                stubbed.append(dep)
        print(f'{field}: total={len(deps)} missing={len(missing)} placeholder-only={len(stubbed)}')
        for dep in missing:
            suggestions = difflib.get_close_matches(dep, index.keys(), n=3, cutoff=0.65)
            print('MISSING', dep, 'possible:', ', '.join(suggestions) or 'none')
        for dep in stubbed:
            print('STUB', dep, 'provider:', ', '.join(str(x.relative_to(a.repo)) for x in index[dep]))
        if field in ('REQUIRES', 'BUILD_REQUIRES'):
            failures += len(missing) + len(stubbed)
    if failures:
        print(f'FAIL: {failures} unresolved hard dependencies or placeholder-only providers')
        return 1
    print('PASS: all declared hard dependencies have non-placeholder recipe providers')
    print('NOTE: static name audit only, not a successful source build or version check')
    return 0

if __name__ == '__main__':
    sys.exit(main())
