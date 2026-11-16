# Plasma Aurora 0.3.0 — LPM Linux KDE Plasma 6 Global Theme

Plasma Aurora is an installable, tracked-asset KDE Plasma 6 Global Theme
for LPM Linux. The LPBUILD installs **real files from a pinned Git source**,
rather than synthesizing metadata and SVGs in the shell. This supports
both local checkout builds and LPM's package-name remote LPBUILD resolution.

## Build and install on LPM Linux

Use the remote package-name build directly on LPM Linux:

```bash
lpm buildpkg plasma-aurora
```

Or use the recipe checked out from GitHub:

```bash
lpm buildpkg ./--KDE--/plasma-aurora/plasma-aurora.lpmbuild
```

LPM fetches the recipe into a temporary location if building by package
name. The recipe declares `SOURCE` as a **Git source pinned to the
Aurora 0.3.0 asset commit** (`32d42ce6d6c4b46eea2e92d65e4c15b66eae6382`).
LPM clones that source into `$SRCROOT/aurora-src`. It is intentionally
independent of `/tmp/lpm-plasma-aurora.lpmbuild` and its directory.

The Git commit hash fixes asset contents; `SHA256SUMS=("SKIP")` is expected
for a Git source because it is **not** a downloaded tar archive. LPM needs
the `git` build dependency and network access for an uncached clone.

Install the resulting **0.3.0-2** signed `.lpminstall` artifact with
`lpm installpkg /path/to/plasma-aurora-0.3.0-2.any.lpminstall`,
replacing the example path with LPM's actual output. Once you publish
the binary package to LPM's repository, `lpm install plasma-aurora`
can install it from the binary index.

For deliberate local development, `AURORA_THEME_DIR` still supports an
absolute path to the checked-out `theme/` folder. Normal package builds
do **not** require this override or a checkout beside the recipe.

## What is installed

- `/usr/share/plasma/look-and-feel/org.lpm.aurora.desktop/` — Global Theme
  metadata, defaults, opt-in dock layout, generated PNG preview.
- `/usr/share/plasma/desktoptheme/org.lpm.aurora/` — Aurora Glass Plasma Style,
  panel/widget/dialog SVGs, solid opacity fallback and color palette.
- `/usr/share/color-schemes/Aurora.colors` — Aurora KDE dark color scheme.
- `/usr/share/icons/PlasmaAurora/` — accent icons with Breeze fallback.
- `/usr/share/wallpapers/PlasmaAurora/` — original vector wallpaper source
  plus generated 2560×1440 PNG and 960×540 screenshot.
- `/usr/bin/aurora-profile` — opt-in reversible KWin effects/animations utility.

No per-user files or KWin binaries are modified when installing this package.
All staged files are owned by the `plasma-aurora` LPM package.

## Apply

Log into Plasma 6, then open **System Settings → Colors & Themes → Global Theme**,
select **Aurora**, and optionally apply the desktop layout. **Applying a desktop
layout replaces your panel arrangement.** Save
`~/.config/plasma-org.kde.plasma.desktop-appletsrc` first if you need it.

The panel layout uses KDE's own Kickoff, icons-only task manager, tray, clock,
and Show Desktop. After applying, enable **Floating** in Plasma's panel editor
if not enabled automatically. KWin Blur must be supported and enabled for
real backdrop blur; SVG translucency by itself is not live blur.

## Optional performance configuration

Run as a non-root desktop user:

```bash
aurora-profile status
aurora-profile balanced
aurora-profile performance
aurora-profile ultra
aurora-profile restore
```

The helper stores a rollback record for
`kwinrc/[Plugins]/blurEnabled`, `kwinrc/[Plugins]/contrastEnabled`,
and `kdeglobals/[KDE]/AnimationDurationFactor`. It does not alter the CPU
governor, GPU clocks, system services, kernel settings or KWin binary.
`restore` preserves manually edited keys. Run `restore` before uninstalling
if you've applied a profile.

## Staging and tests

The recipe's `staging()` function copies every tracked theme component from
`$SRCROOT/aurora-src/--KDE--/plasma-aurora/theme` to `$pkgdir`, runs the
deterministic stdlib-only PNG generator, and invokes
`tools/validate_stage.py` to verify package IDs, 9-slice SVG elements,
icons, layout and actual generated PNG file headers.

The wallpaper PNGs are created **at package build time**; the editable
vector source and standard-library renderer are checked into Git.
A C++ compiler, ImageMagick, Pillow or host-side Meson are not needed for
this asset-only LPBUILD. Python 3 and Git are declared build dependencies;
Python 3 is also a runtime dependency for `aurora-profile`.

### Regression test

From an LPMBUILDS checkout, run:

```bash
bash ./--KDE--/plasma-aurora/smoke-test.sh
```

The smoke test creates a fake `$SRCROOT/aurora-src` with symlinked
theme assets, copies the recipe into a separate temporary location,
and invokes prepare, build, and staging in separate shells. This
simulates the exact `/tmp/lpm-plasma-aurora.lpmbuild` failure mode
without fetching from GitHub. It checks the generated PNG, executable
profile helper, and staged package structure.

If an older cached recipe still prints
`Missing Aurora assets: /tmp/theme`, refresh the remote LPBUILD
to the **0.3.0-2** recipe. That message is from version 0.3.0-1.

## Current scope

This is a complete distributable first-generation Aurora **theme package**,
not the planned future Aurora KWin source-patch suite. Custom 3D dock icon
magnification and custom shader effects are not implemented. Runtime testing
on LPM Linux Plasma 6.8.x Wayland and AMD Renoir remains required.

## License

MIT; see `theme/LICENSE`.
