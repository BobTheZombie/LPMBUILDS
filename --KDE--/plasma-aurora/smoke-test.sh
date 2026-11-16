#!/usr/bin/env bash
# Exercise the real remote-buildpkg layout without downloading from GitHub.
# LPM fetches only the .lpmbuild into /tmp and stages the Git SOURCE into SRCROOT.
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
bash -n plasma-aurora.lpmbuild
test -r theme/global-theme/org.lpm.aurora.desktop/metadata.json
test -r theme/tools/validate_stage.py

work="$(mktemp -d)"
trap 'rm -rf -- "$work"' EXIT

# The remote recipe is deliberately outside the source checkout.
cp plasma-aurora.lpmbuild "$work/lpm-plasma-aurora.lpmbuild"
mkdir -p "$work/src/aurora-src/--KDE--/plasma-aurora" "$work/pkg"
ln -s "$PWD/theme" "$work/src/aurora-src/--KDE--/plasma-aurora/theme"

export SRCROOT="$work/src"
export pkgdir="$work/pkg"
unset AURORA_THEME_DIR

# Separate shells match LPM's isolated phases. This catches missing exports
# or accidental reuse of the script's /tmp directory.
bash -c 'source "$1"; prepare' bash "$work/lpm-plasma-aurora.lpmbuild"
bash -c 'source "$1"; build' bash "$work/lpm-plasma-aurora.lpmbuild"
bash -c 'source "$1"; staging' bash "$work/lpm-plasma-aurora.lpmbuild"

test -s "$pkgdir/usr/share/wallpapers/PlasmaAurora/contents/images/2560x1440.png"
test -x "$pkgdir/usr/bin/aurora-profile"

# Development override still resolves to the checked-out theme.
AURORA_THEME_DIR="$PWD/theme" \
    bash -c 'source "$1"; test "$(_aurora_theme_dir)" = "$AURORA_THEME_DIR"' \
    bash "$work/lpm-plasma-aurora.lpmbuild"

printf '[OK] Plasma Aurora remote-recipe staging smoke test passed\n'
