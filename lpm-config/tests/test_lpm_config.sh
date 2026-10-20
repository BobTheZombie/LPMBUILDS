#!/bin/sh
# Regression tests for the LPM config-only seed script; no root required.
set -eu
pkg=$(CDPATH= cd "$(dirname "$0")/.." && pwd -P)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

root="$tmp/root"
mkdir -p "$root/usr/share/lpm-config/defaults" "$root/usr/bin" "$root/etc/skel"
chmod 755 "$root/usr/bin"
# Mimic package staging of the templates, without touching the executing host.
mkdir -p "$root/usr/share/lpm-config/defaults/etc/default"
mkdir -p "$root/usr/share/lpm-config/defaults/etc/profile.d"
mkdir -p "$root/usr/share/lpm-config/defaults/etc/skel"
mkdir -p "$root/usr/share/lpm-config/defaults/etc/xdg"
template="$root/usr/share/lpm-config/defaults"
cp "$pkg/profile" "$template/etc/profile"
cp "$pkg/path.sh" "$template/etc/profile.d/10-lpm-path.sh"
cp "$pkg/skel.profile" "$template/etc/skel/.profile"
cp "$pkg/skel.bash_profile" "$template/etc/skel/.bash_profile"
cp "$pkg/skel.bashrc" "$template/etc/skel/.bashrc"
cp "$pkg/useradd" "$template/etc/default/useradd"
cp "$pkg/login.defs" "$template/etc/login.defs"
cp "$pkg/nsswitch.conf" "$template/etc/nsswitch.conf"
cp "$pkg/hosts" "$template/etc/hosts"
cp "$pkg/issue" "$template/etc/issue"
cp "$pkg/motd" "$template/etc/motd"
cp "$pkg/locale.conf" "$template/etc/locale.conf"
cp "$pkg/user-dirs.defaults" "$template/etc/xdg/user-dirs.defaults"

printf '%s\n' 'user customized' > "$root/etc/skel/.bashrc"
printf '#!/bin/sh\nexit 0\n' > "$root/usr/bin/bash"
chmod 755 "$root/usr/bin/bash"

if sh "$pkg/lpm-config-init" --root "$root" --verify > "$tmp/pre.log"; then
    echo "verify should fail when defaults are absent" >&2
    exit 1
fi
sh "$pkg/lpm-config-init" --root "$root" --dry-run > "$tmp/dry.log"
[ ! -e "$root/etc/profile" ] || exit 1
sh "$pkg/lpm-config-init" --root "$root" > "$tmp/install.log"
grep -qx 'user customized' "$root/etc/skel/.bashrc"
grep -qx '/usr/bin/bash' "$root/etc/shells"
[ -s "$root/etc/profile" ] || exit 1
[ -s "$root/etc/nsswitch.conf" ] || exit 1
sh "$pkg/lpm-config-init" --root "$root" --verify > "$tmp/verify.log"
sh "$pkg/lpm-config-init" --root "$root" > "$tmp/again.log"
grep -q 'created=0' "$tmp/again.log"

# Ensure symlinked configuration is preserved.
rm "$root/etc/hosts"
ln -s /dev/null "$root/etc/hosts"
sh "$pkg/lpm-config-init" --root "$root" > "$tmp/symlink.log"
[ -L "$root/etc/hosts" ] || exit 1
echo "PASS: seeding is safe, idempotent and validates missing defaults"
