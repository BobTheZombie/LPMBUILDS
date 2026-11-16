#!/usr/bin/env bash
# Source-tree and buildpkg smoke test; run from the LPMBUILDS checkout.
set -euo pipefail
cd "$(dirname "$0")"
bash -n plasma-aurora.lpmbuild
AURORA_THEME_DIR="$PWD/theme"
export AURORA_THEME_DIR
pkgdir="$(mktemp -d)"
trap 'rm -rf "$pkgdir"' EXIT
export pkgdir
source ./plasma-aurora.lpmbuild
prepare
build
staging
test -s "$pkgdir/usr/share/wallpapers/PlasmaAurora/contents/images/2560x1440.png"
test -x "$pkgdir/usr/bin/aurora-profile"
printf '[OK] Plasma Aurora source-tree staging test passed\n'
