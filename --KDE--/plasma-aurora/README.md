# LPM Plasma Aurora — patchset 0.1

Aurora is the LPM Linux visual patchset for KDE Plasma 6. Development is
**build-time**, not a shell script rewriting a user's files after installation.
The first deliverable is a separately versioned LPM package and an opt-in global
theme, keeping upstream Plasma and KWin binaries intact.

## Version 0.1 deliverable

- Sapphire-violet semi-transparent Plasma panel 9-slice SVG
- High-opacity fallback for adaptive panel opacity
- Aurora dark KDE color scheme
- Selectable Plasma Style: **Aurora Glass**
- Selectable Global Theme: **Aurora**
- Opt-in bottom, centered, fit-content task dock layout
- Uses the installed icons-only task manager; does not monkey-patch its QML
- All assets written to LPM's `$pkgdir` during `staging()`; no user-home writes

Build from the LPMBUILDS checkout:

```sh
lpm buildpkg --KDE--/plasma-aurora/plasma-aurora.lpmbuild
```

Then install the resulting signed package with `lpm installpkg` (or publish it
to the official binary repository and use `lpm install plasma-aurora`).

Select **Aurora Glass** under System Settings > Colors & Themes > Plasma Style.
Select **Aurora** under Global Theme to apply its color/style combination.
Select the *desktop layout* only if you intend to replace your existing panels;
applying layouts may replace current panel configuration.

## Boundaries and next phases

v0.1 is a real, staged KDE theme, **not yet** a KWin blur or 3D animation patch.
Translucent SVG fill is not the same as GPU backdrop blur. The actual blur effect
depends on KWin composition and effect settings. A floating dock also needs
the panel's floating option enabled in Plasma's panel editor; the first
layout script does not promise to override its internal floating state.

Planned follow-ons, independently guarded by upstream tag:

1. **0.2 KWin backdrop blur** — tested blur regions and rounded floating panels,
   with GPU-safe fallbacks and reduced-effects mode.
2. **0.3 Aurora task manager** — spring animations, parallax icon lift,
   perspective transform, active glow and hover response; configurable and
   reduced-motion aware, using Qt Quick Scene Graph rather than CPU polling.
3. **0.4 Aurora launcher and OSD** — matching glass/lighting and accessible
   contrast, no changes to core shell permissions or applet protocols.
4. **0.5 System integration** — defaults for *new* accounts via an explicitly
   selected LPM profile, not an unconditional overwrite of existing users.

The patchset must never replace Plasma's QML or KWin binaries at runtime.
Future upstream source patches should live beside the exact matching
`plasma-workspace`, `plasma-desktop` or `kwin` recipe, with strict patch
application, build-time gating and clear version bumps.

## Validation

The package staging function validates JSON metadata and SVG element IDs.
**Not yet tested** in an actual LPM chroot, KPackage loader, or running Plasma
6.8.1 session. Before production: run `bash -n` on the recipe, stage the
package and inspect the resulting archive; apply the theme in a non-critical
test user session; verify KWin blur and panel scaling visually.
