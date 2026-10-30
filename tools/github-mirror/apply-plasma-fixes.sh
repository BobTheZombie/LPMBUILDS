#!/usr/bin/env bash
# Apply Plasma 6.8.1 dependency and CSS theming fixes to canonical GitLab recipes.
# Run from a CLEAN checkout of https://gitlab.com/lpm-org/packages
# bash apply-plasma-fixes.sh --push  (commit + push changes with your credentials)
set -euo pipefail

if [[ ! -d .git ]]; then
    echo "Run from the root of your GitLab lpm-org/packages checkout." >&2
    exit 1
fi
origin="$(git remote get-url origin)"
if [[ ! "$origin" =~ gitlab\.com[:/]lpm-org/packages(\.git)?$ ]]; then
    echo "Refusing to modify unexpected git remote: $origin" >&2
    exit 1
fi
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Working tree has changes; commit or stash them first." >&2
    exit 1
fi

base="https://raw.githubusercontent.com/BobTheZombie/LPMBUILDS/main"
paths=(
    "--KDE--/qt6-location/qt6-location.lpmbuild"
    "--KDE--/qcoro/qcoro.lpmbuild"
    "corrosion/corrosion.lpmbuild"
    "--KDE--/cxx-rust-cssparser/cxx-rust-cssparser.lpmbuild"
    "--KDE--/union/union.lpmbuild"
    "libqalculate/libqalculate.lpmbuild"
)
for path in "${paths[@]}"; do
    mkdir -p "$(dirname "$path")"
    tmp="$(mktemp)"
    if ! curl --fail --location --silent --show-error "$base/$path" -o "$tmp"; then
        rm -f "$tmp"
        exit 1
    fi
    bash -n "$tmp"
    mv -f "$tmp" "$path"
    echo "Installed $path"
done
# Fetch the full build recipe rather than the unaligned mirrored copy.
path="--KDE--/plasma-workspace/plasma-workspace.lpmbuild"
tmp="$(mktemp)"
curl --fail --location --silent --show-error \
     "$base/tools/github-mirror/plasma-workspace.fixed.lpmbuild" -o "$tmp"
bash -n "$tmp"
mv -f "$tmp" "$path"
echo "Installed $path"

grep -q -- '-DBUILD_INPUT_CSS=ON' --KDE--/union/union.lpmbuild
grep -q '"cxx-rust-cssparser"' --KDE--/union/union.lpmbuild
grep -q -- '-DINSTALL_SDDM_WAYLAND_SESSION=ON' "$path"
git add -- "${paths[@]}" "$path"
git diff --cached --stat

if [[ "${1:-}" == "--push" ]]; then
    git commit -m "Fix Plasma Workspace 6.8.1 dependencies and enable Rust CSS theming"
    git push origin HEAD
    echo "Pushed to canonical GitLab. Clear LPM's cached recipe snapshot before building."
else
    echo
    echo "Review staged edits using: git diff --cached"
    echo "Then publish with:"
    echo "  git commit -m 'Fix Plasma 6.8.1 dependencies and CSS theming'"
    echo "  git push origin HEAD"
fi
