# LPM Linux: Flatpak filesystem prerequisites

This directory contains the Flatpak 1.18.4 recipe. FUSE3 and OSTree have
matching fixes in `fuse3/fuse3.lpmbuild` and `ostree/ostree.lpmbuild`.

## Rebuild order

1. Rebuild **LPM** from LPM.Org (release 1.0.1-3), using the signed
   file-mode policy. It must be installed first, otherwise Python's safe
   tar extraction removes the FUSE helper's setuid bit.
2. Rebuild and install `fuse3` 3.18.3-2 (official release tar with pinned
   SHA-256). It stages /usr/bin/fusermount3 mode 4755, /etc/fuse.conf and
   /usr/lib/udev/rules.d/99-fuse3.rules. The installed helper must be root-owned.
3. Rebuild and install `ostree` 2026.4-2 to explicitly compile
   `rofiles-fuse` against FUSE3.
4. Rebuild and install `flatpak` 1.18.4-3 to ship
   `/usr/libexec/revokefs-fuse` and the diagnostic helper.

Using existing LPM buildpkg conventions:

```sh
lpm buildpkg fuse3
lpm buildpkg ostree
lpm buildpkg flatpak
```

The system installation must have an operational /dev/fuse character device,
the `99-fuse3.rules` device rule, the 4755/root:root `fusermount3` executable
on a filesystem not mounted `nosuid`, and accessible /var/tmp.

## Troubleshooting

```sh
/usr/libexec/lpm/flatpak-fuse-check
flatpak -vv install --system flathub org.kde.kmines
journalctl -b --no-pager | grep -Ei 'fuse|flatpak|revokefs'
```

The diagnostic script **does not** chmod a live file, remount a filesystem,
create a device node or remove a Flatpak cache. It exits nonzero when
it detects an incomplete setup.

The package is safe to stage with Meson `-Duseroot=false`: the signed
LPM package manager alone restores the allowlisted privilege during
the actual installation. LPM must be updated **before** rebuilding FUSE3.
