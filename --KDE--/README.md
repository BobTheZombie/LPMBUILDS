# LPM Linux — KDE Plasma 6.8.1 package chain

**Status: source-version-verified draft, NOT build-tested or approved for production.**

Created 2026-10-25; contains 158 LPM `.lpmbuild` files. GitLab `lpm-org/packages` was inaccessible via available public tools: this is an **import set**, not an edit or a confirmed audit of that GitLab repository. The older `BobTheZombie/LPMBUILDS` mirror had Qt 6.7.2, KDE 6.1.2 and placeholder `kcoreaddons6`, hence the need for a thorough rebuild.

## Version alignment

* Qt **6.11.2** (upstream 6.11.2 release 18 August 2026)
* KDE Frameworks **6.31.0** (release 9 October 2026)
* Plasma **6.8.1** (release 20 October 2026)
* Gear **26.08.2** (release 8 October 2026)
* Plasma Wayland Protocols **1.23.0** (release 24 September 2026)
* polkit-qt6 **0.201.1** and SDDM **0.21.0**.

Upstream KDE Plasma 6.8 requires Qt 6.11 and Frameworks >= 6.30.0.

## Packaging contract

Every real package:

1. References an upstream source tarball, not a synthetic placeholder.
2. Uses LPM fields `NAME`, `VERSION`, `RELEASE`, `ARCH`, `SOURCE`, `SHA256SUMS`, `REQUIRES`, `BUILD_REQUIRES`, `REQUIRES_PYTHON_DEPENDENCIES` where needed.
3. Expects LPM to normalize the primary archive into `$SRCROOT/$NAME-$VERSION`.
4. Configures CMake/Ninja out-of-source, installs to `/usr/lib`, stages with `DESTDIR=$pkgdir`, and honors LPM_BUILD_JOBS.
5. Generates a nonempty payload or, for source-free meta packages, an **intentionally empty** staging directory. LPM recognizes the `REQUIRES` on an empty payload as a meta package.

**IMPORTANT: checksums are SKIP pending acquisition!** Do not upload these recipes to a production LPM repo yet. The container cannot download upstream sources, so SHA256 cannot be truthfully populated. `scripts/lock_sources.py` downloads through HTTPS and replaces SKIP with actual SHA-256. For high-assurance distribution use, independently compare digest values to signed release metadata, validate the KDE `.sig` files, and audit licenses. Qt 6.11.2 has additional upstream CVE patches in the Qt archive (October 2026), so do a security review before wide deployment.

## Suggested workflow

```sh
unzip lpm-kde-plasma-6.8.1-chain.zip
cd lpm-plasma-6.8.1
python3 scripts/lock_sources.py --jobs 3
python3 scripts/audit.py
# Compare these recipes against your ACTUAL GitLab repo; do not blindly overwrite.
# Preview changes against a local GitLab clone:
python3 scripts/import_overlay.py /path/to/gitlab-packages-checkout
# After reviewing, import:
python3 scripts/import_overlay.py /path/to/gitlab-packages-checkout --apply
# Use build-order.txt as a bootstrap guide, not as proof of a complete graph.
# Build packages via LPM and test on a real LPM chroot/VM first.
```

## Meta packages

- `plasma-core`: basic Wayland desktop, KWin, workspace, panels, integration, NetworkManager, PipeWire, power management, SDDM, portal.
- `plasma-meta`: full desktop plus GUI administration, icons, tools, wallpapers and Gear (Dolphin, Konsole, Kate, Ark, Gwenview, KDE Connect). **Install this package** for full desktop.
- KDE Discover is intentionally not in the mandatory `plasma-meta` closure: LPM does not yet establish a PackageKit-compatible backend. Build it separately or add it when PackageKit integration exists. Printing, bluez, udisks etc. are external dependencies; see `external-requirements.txt`.

### Once installed

```sh
systemctl enable sddm.service
systemctl set-default graphical.target
# reboot and select Plasma (Wayland) from SDDM
```

Before enabling SDDM, verify `/usr/share/wayland-sessions/plasma.desktop` (or installed equivalent), that `startplasma-wayland` exists, `/usr/lib/qt6` plugin paths are correct, user session DBus/PAM works, `/run/user/$UID` works, the portal is started, and PipeWire/WirePlumber services are active. **Do not execute systemctl inside an LPM chroot to enable a host service.** Run on the booted LPM system or use `systemctl --root=<mountpoint> enable sddm` when appropriate.

## Major external build blockers

The generated set does **not** package every third-party dependency: Wayland, Mesa, libinput, PipeWire, WirePlumber, libseat, libdisplay-info, polkit, xorg-xwayland, xdg-desktop-portal, libqaccessibilityclient, Kirigami-independent system utilities etc. Every unique external package from the generated dependency graph is listed in `external-requirements.txt`; your actual GitLab catalog must be checked. Some CMake modules may request further upstream dependencies that are not represented in the draft graph.

This bundle should be treated as a broad **source/version and package metadata starting point**. It is not a claim that each package compiles, that the per-module dependency lists are exhaustive, or that the full desktop is installable before those third-party prerequisites are implemented. Run LPM's resolver, package validator, and build tests for each layer.

## Source references

- Qt module sources: https://download.qt.io/archive/qt/6.11/6.11.2/submodules/
- KDE Frameworks: https://download.kde.org/stable/frameworks/6.31/
- KDE Plasma: https://download.kde.org/stable/plasma/6.8.1/
- KDE Gear: https://download.kde.org/stable/release-service/26.08.2/src/
- KDE Plasma version requirements: https://community.kde.org/Schedules/Plasma_6
- KDE Wayland protocols: https://download.kde.org/stable/plasma-wayland-protocols/
- Qt 6.11 security updates: https://download.qt.io/official_releases/qt/6.11/
