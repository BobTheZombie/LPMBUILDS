# LPM Plasma Aurora — Global Theme 0.2

Plasma Aurora is the native, **build-time staged** visual theme for KDE Plasma 6
on LPM Linux. It does not replace or patch KWin at runtime.

## Version 0.2 deliverables

- Original sapphire/violet semi-transparent Plasma Style panel assets
- Solid/high-opacity fallback and matching KDE dark color scheme
- Selectable Plasma Style **Aurora Glass**
- Selectable KDE Global Theme **Aurora** (`org.lpm.aurora.desktop`)
- Optional, centered, fit-content dock layout, using upstream Plasma widgets
- **New:** `aurora-profile` with reversible Performance, Balanced, and Ultra presets
- Staged installation into `$pkgdir`, with **no user-home writes** on package install

## Build and install

```sh
lpm buildpkg --KDE--/plasma-aurora/plasma-aurora.lpmbuild
```

Install the resulting signed package with `lpm installpkg` or, once published
to the binary repository, use `lpm install plasma-aurora`.

In **System Settings → Colors & Themes**, select **Aurora** under Global Theme.
Apply the desktop layout only if you want to replace your existing panels.
Selecting a Global Theme does not automatically enable the profile helper.

## Opt-in performance profiles

Run these **as your regular desktop user**, never with sudo:

```sh
aurora-profile status
aurora-profile balanced
aurora-profile performance
aurora-profile ultra
aurora-profile restore
```

`--dry-run` is supported for preset and restore operations. Presets adjust only
three user KConfig keys: `kwinrc/[Plugins]/blurEnabled`,
`kwinrc/[Plugins]/contrastEnabled`, and
`kdeglobals/[KDE]/AnimationDurationFactor`.

- **Performance:** blur off, background contrast off, shorter animation duration
- **Balanced:** blur and contrast on, responsive animation duration
- **Ultra:** blur and contrast on, slightly longer animation duration

The first preset stores original values under
`${XDG_STATE_HOME:-~/.local/state}/plasma-aurora/profile-backup.json`
with owner-only permissions. `restore` will not overwrite keys manually
modified since Aurora last applied its settings. Profile switches refuse to
overwrite manually changed keys. The profile helper never changes CPU
governors, kernel parameters, GPU clocks, services, KWin binaries, or global
machine configuration.

**Important:** The profile values are design defaults, not a measured speedup.
Actual blur and animation performance requires live Plasma/KWin testing.

## Scope and limitations

- A translucent SVG is not backdrop blur; real blur is provided by KWin.
- The dock uses the upstream icons-only task manager, with no 3D magnification
  or custom task manager implementation yet.
- The layout does not guarantee that Plasma's internal floating-panel state
  is enabled; it can be set in the panel editor.
- This package does not yet contain the separate high-resolution wallpaper,
  extra icon assets, or custom GPU KWin shaders from the portable Aurora
  prototype; those should be imported as tracked assets in a follow-up update.
- Tests validate metadata/SVG at staging time and parse the Python helper.
  An actual LPM chroot package build and Plasma 6.8 Wayland session test remain
  outstanding.

## Roadmap

1. Track the reusable Global Theme assets directly in LPMBUILDS instead of
   maintaining a monolithic inline recipe
2. Add original wallpaper, icon resources, and compatible window decorations
3. Develop a separately opt-in QML task manager with reduced-motion support
4. Benchmark and separately package Ryzen/KWin source-level optimizations
5. Test on LPM Linux bare metal (Plasma 6.8.x, AMD Renoir, Wayland)

## Project principles

Aurora is entirely **opt-in**; package installation must never rewrite
a user's existing plasma-appletsrc or other account settings. Keep the
same package name and KDE plugin IDs through iterative releases so upgrades
remain compatible.

License: MIT.
