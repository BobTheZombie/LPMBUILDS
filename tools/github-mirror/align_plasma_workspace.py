#!/usr/bin/env python3
"""Align Plasma 6.8.1 dependency names against real GitLab NAME/PROVIDES entries."""
import argparse
from pathlib import Path
import re
import shlex

HARD_BUILD = """qt6-base qt6-declarative qt6-location qt6-positioning qt6-svg
qt6-shadertools qt6-wayland qcoro libplasma kwayland plasma-activities
plasma-activities-stats libksysguard libkscreen layer-shell-qt knighttime
union kwin plasma-wayland-protocols dbus libudev wayland libqalculate
libcanberra zlib extra-cmake-modules cmake ninja pkgconf""".split()
OPTIONAL = "flatpak accountsservice pipewire appstream".split()
BUILD_ONLY = {"cmake", "ninja", "pkgconf", "extra-cmake-modules", "plasma-wayland-protocols"}

def array(text, field):
    match = re.search(r'(?ms)^' + re.escape(field) + r'\s*=\s*\((.*?)\)', text)
    if not match:
        return None, []
    lex = shlex.shlex(match.group(1), posix=True)
    lex.whitespace_split = True
    lex.commenters = '#'
    try:
        return match, list(lex)
    except ValueError:
        # Some source recipes use shell expansions with internal ')' characters.
        # Ignore unparseable provider aliases rather than evaluating shell code.
        if field == 'PROVIDES':
            return match, []
        raise

def provider_index(root):
    index = {}
    stubs = set()
    for file in root.rglob('*.lpmbuild'):
        text = file.read_text(errors='replace')
        m = re.search(r'(?m)^NAME\s*=\s*["\']([^"\']+)', text)
        name = m.group(1) if m else file.stem
        _, aliases = array(text, 'PROVIDES')
        if 'Placeholder package for' in text or 'https://example.com/' in text:
            stubs.add(file)
        for value in [name] + aliases:
            if '$' not in value:
                index.setdefault(value, []).append(file)
    return index, stubs

def resolve(name, index, stubs):
    # Only unambiguous literal provider matches; never invent a name.
    normalize = lambda s: re.sub('[^a-z0-9]', '', s.lower())
    candidates = [name] if name in index else [k for k in index if normalize(k) == normalize(name)]
    valid = [k for k in candidates if any(p not in stubs for p in index[k])]
    return valid[0] if len(valid) == 1 else None

def append_array(text, field, extra):
    m, existing = array(text, field)
    if m is None:
        raise ValueError(f'Missing {field} array in GitLab Plasma recipe')
    unique = [d for d in extra if d not in existing]
    if not unique:
        return text, []
    new = field + '=(\n' + ''.join(f'    "{d}"\n' for d in existing + unique) + ')'
    return text[:m.start()] + new + text[m.end():], unique

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--recipe', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    index, stubs = provider_index(a.repo)
    if not index:
        raise SystemExit('Empty GitLab package index')
    text = a.recipe.read_text()
    if not re.search(r'(?m)^VERSION\s*=\s*["\']6\.8\.1["\']', text):
        a.report.write_text('GitLab Plasma Workspace is not 6.8.1; preserving its original recipe.\n')
        print('Plasma version differs from 6.8.1; original GitLab recipe preserved')
        return
    missing = [x for x in HARD_BUILD if resolve(x, index, stubs) is None]
    build = [resolve(x, index, stubs) for x in HARD_BUILD if resolve(x, index, stubs)]
    runtime = [resolve(x, index, stubs) for x in HARD_BUILD if x not in BUILD_ONLY and resolve(x, index, stubs)]
    optional = [resolve(x, index, stubs) for x in OPTIONAL if resolve(x, index, stubs)]
    text, build_added = append_array(text, 'BUILD_REQUIRES', build)
    text, runtime_added = append_array(text, 'REQUIRES', runtime)
    if array(text, 'RECOMMENDS')[0] is not None:
        text, _ = append_array(text, 'RECOMMENDS', optional)
    # Explicitly turn on SDDM's Wayland compositor greeter for LPM Linux.
    if re.search(r'-DINSTALL_SDDM_WAYLAND_SESSION=(?:ON|OFF)', text):
        text = re.sub(r'-DINSTALL_SDDM_WAYLAND_SESSION=(?:ON|OFF)',
                      '-DINSTALL_SDDM_WAYLAND_SESSION=ON', text)
    else:
        match = re.search(r'(?m)^([ \t]*)-DBUILD_TESTING=(?:ON|OFF)', text)
        if match:
            text = (text[:match.start()] + match.group(1)
                    + '-DINSTALL_SDDM_WAYLAND_SESSION=ON \\\n' + text[match.start():])
        else:
            print('WARNING: Could not find safe insertion point for SDDM Wayland flag')
    a.recipe.write_text(text)
    lines = ['# Plasma Workspace 6.8.1 dependency audit', '',
             f'Indexed {len(index)} NAME / PROVIDES identifiers.', '',
             '## Added build dependencies', '', *[f'- {x}' for x in build_added], '',
             '## Added runtime dependencies', '', *[f'- {x}' for x in runtime_added], '',
             '## Missing or placeholder-only upstream build requirements', '',
             *[f'- {x}' for x in missing], '']
    a.report.write_text('\n'.join(lines))
    print(f'Added {len(build_added)} build / {len(runtime_added)} runtime; unresolved: {len(missing)}')
    for dep in missing:
        print('UNRESOLVED:', dep)

if __name__ == '__main__':
    main()
