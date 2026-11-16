# Plasma Aurora 0.3.0 — LPM Linux KDE Plasma 6 Global Theme

Plasma Aurora is an installable, tracked-asset KDE Plasma 6 Global Theme,
targeted at LPM Linux. The recipe installs **real files from this checkout**
rather than synthesizing its metadata and SVGs in the shell.

## Build and install on LPM Linux

Clone or update your LPMBUILDS checkout and run from its root:

```bash
lpm buildpkg --KDE--/plasma-aurora/plasma-aurora.lpmbuild
```

Install the resulting signed `.lpminstall` artifact with
`lpm installpkg /path/to/plasma-aurora-0.3.0-1.any.lpminstall`
(using the actual output path emitted by buildpkg). Once you publish it
to the LPM binary repo, `lpm install plasma-aurora` can use the repo index.

**For this development release**, use the branch
`feat/plasma-aurora-profiles-0.2` until it is merged into `main`.
The recipe uses the adjacent `theme/` directory. It must be built from the
LPMBUILDS checkout with that directory present; alternatively export
`AURORA_THEME_DIR=/absolute/path/to/theme` before calling buildpkg.

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

The recipe's `staging()` function copies every tracked theme component
to `$pkgdir`, runs the deterministic stdlib-only PNG generator, and invokes
`tools/validate_stage.py` to verify package IDs, 9-slice SVG elements,
icons, layout and actual generated PNG file headers.

The wallpaper PNGs are created **at package build time**; the editable
vector source and standard-library renderer are checked into Git.
A C++ compiler, ImageMagick, Pillow or host-side Meson are not needed for
this asset-only LPBUILD. Python 3 is a declared build/runtime dependency.

## Current scope

This is a complete distributable first-generation Aurora **theme package**,
not the planned future Aurora KWin source-patch suite. Custom 3D dock icon
magnification and custom shader effects are not implemented. Runtime testing
on LPM Linux Plasma 6.8.x Wayland and AMD Renoir remains required.

## License

MIT; see `theme/LICENSE`.
