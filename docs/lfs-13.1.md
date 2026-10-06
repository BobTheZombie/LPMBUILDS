# LFS 13.1 package baseline

This branch imports the package collection from https://gitlab.com/lpm-org/packages.git
at commit `adde13683f091cb9bd519be085bae35408632224`, then aligns 84 recipes
with the LFS 13.1 systemd book. GitHub commit ancestry is retained from LPMBUILDS;
this is an imported GitLab snapshot, not an import of its entire commit history.

## Sources

- Package list: https://www.linuxfromscratch.org/lfs/view/13.1-systemd/chapter03/packages.html
- Required patches: https://www.linuxfromscratch.org/lfs/view/13.1-systemd/chapter03/patches.html
- Build instructions: https://www.linuxfromscratch.org/lfs/view/13.1-systemd/chapter08/chapter08.html
- Download mirror used when upstream was unavailable: https://ftp.osuosl.org/pub/lfs/lfs-packages/13.1/

All 86 archives in the book's source list were downloaded and matched against
its published MD5 values. The recipes use SHA-256 digests calculated from those
verified archives. All local patches and configuration sources in the updated
recipes have SHA-256 values too. Documentation archives other than systemd's
prebuilt manual pages are optional and are not packaged separately.

`metadata/lfs-13.1.json` records the exact versions and source digests. SQLite's
upstream archive number `3530400` is represented as package version `3.53.4`.

## Arch adaptations

The following Arch PKGBUILDs were reviewed:
https://gitlab.archlinux.org/archlinux/packaging/packages/ (glibc, gcc, binutils,
bash, readline, systemd, openssl, coreutils, shadow, util-linux, zlib, libmnl).

- zlib: upstream commit `36ff1be48ef696cc67b0855f7c8537ce0276210d`, used by Arch,
  fixes the missing header. The recipe also builds and installs contrib/minizip,
  including its shared library, headers and pkg-config metadata.
- OpenSSL: Arch's `ca-dir.patch` sets CA helper defaults to `/etc/ssl`.
- systemd: Arch's device access groups patch retains optical/uucp/storage group
  naming. The recipe also removes the previous hard dependency on a locally generated `vmlinux.h`.
- Readline: Arch's RPATH removal is applied to `support/shobj-conf`.
- GCC: LFS/Arch `/usr/lib` layout and PIE/stack protector defaults are retained.
- libmnl: Arch's 1.0.5 source and SHA-256 add the missing iproute2 dependency.

The Arch binutils fat-IR stripping patch was tested and rejected because it
conflicts with the 2.47 release sources and includes changes already represented
in that tree. Current Arch GCC/glibc Git snapshots and Bash/Readline point-patch
versions were not substituted for the book's releases. Versions remain at the
requested LFS baseline.

`metadata/patches-lfs-13.1.json` records exact patch URLs, SHA-256 hashes and
application results. All eleven included patches apply to the selected release
sources; the book's Coreutils/Kbd patches and Arch's OpenSSL patch require the
normal GNU patch context fuzz allowance. No failed hunks are ignored.

## Packaging repairs

26 original unresolved merge conflicts were resolved, four decorative separator
lines were converted to comments, and the filesystem recipe's multiline brace
expansions were repaired. The base recipes now use their actual source directories
and build systems (including Meson for D-Bus, kmod and systemd, and wheel builds
for Python modules).

GCC and gcc-libs use the same release source; gcc-libs owns the shared runtime
libraries. The standalone gcc-libs recipe builds from source rather than copying
the host compiler's libraries. This currently means building GCC twice.

util-linux tools and the split util-linux-libs output use the same source version.
Compatibility packages libcom_err, libudev, udev and util-linux-libs-extra delegate
to the package owning their payload, avoiding duplicate library installations.
Kernel headers belong to linux-headers; the kernel recipe installs only the kernel
image, configuration and modules and reuses the repository's config with olddefconfig.
The systemd manuals are installed from the matching LFS prebuilt archive.

This branch updates the LFS base. Existing BLFS/desktop recipes retain their
versions. Their remaining build/dependency problems have not been comprehensively
audited. The old shadow-bootstrap recipe is also outside this final-system update.

## Validation and rebuild

Run `python3 tools/check-lfs-baseline.py` for recipe syntax and baseline checks.
Pass `--source-dir /path/to/downloads` to verify all updated recipe source hashes.

Completed: all recipe syntax checks, baseline version/source checks, included
patch application checks, and host build/staging smoke checks for libmnl, bc,
bzip2 and filesystem. Patched zlib passes its upstream tests and the contrib/minizip
programs compile. The full autotools minizip installation has not been tested here.

A complete LFS 13.1 chroot rebuild, GCC/glibc test suites, systemd integration tests,
and VM boot test have not been run. These are required before treating this branch
as a validated distribution release. The toolchain, OpenSSL 4 and Python 3.14
changes require coordinated rebuilds of dependent libraries and Python extensions.

Build the base in the order described by the selected LFS book. For an existing
LPM system, build in a clean chroot first and generate the package repository from
that build. Dependency names describe the final installed system; bootstrap build
ordering still uses an existing toolchain and staged libraries. Keep dbus-broker
as the selected system bus implementation when installing the broader LPM system.
