# LPM Plasma Aurora — patchset 0.2

Aurora is the LPM Linux visual patchset for KDE Plasma 6. Development is
**build-time**, not a shell script rewriting a user's files after installation.
The first deliverable is a separately versioned LPM package and an opt-in global
theme, keeping upstream Plasma and KWin binaries intact.

## Versions 0.1 and 0.2 deliverables

- Sapphire-violet semi-transparent Plasma panel 9-slice SVG
- High-opacity fallback for adaptive panel opacity
- Aurora dark KDE color scheme
- Selectable Plasma Style: **Aurora Glass**
- Selectable Global Theme: **Aurora**
- Opt-in bottom, centered, fit-content task dock layout
- Uses the installed icons-only task manager; does not monkey-patch its QML
- All assets written to LPM's `$pkgdir` during `staging()`; no user-home writes
- v0.2 compositor-aware `[BlurBehindEffect]` preferences in the theme `plasmarc`
- v0.2 nine-slice `mask-*` geometry for rounded KWin blur clipping
- v0.2 separate translucent and solid SVG panels for compositor fallback
- Optional `aurora-kwin-effects apply|status|restore` helper; opt-in only

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

v0.2 integrates Plasma's existing compositor-backed blur request and mask API.
This uses KWin's built-in blur effect, **not** a new or modified KWin GPU shader.
Actual blur requires a functioning composited KWin session and the blur effect
enabled in KWin. If composition or effect support is unavailable, the themed
SVG remains visible; the solid variant gives an opaque fallback. A floating dock also needs
the panel's floating option enabled in Plasma's panel editor; the first
layout script does not promise to override its internal floating state.

Planned follow-ons, independently guarded by upstream tag:

1. **0.2 compositor blur integration** — now implemented using Plasma's
   theme hooks and SVG alpha masks; KWin must already support the effect.
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
`tests/test_plasma_aurora.py` runs `bash -n`, stages the package into a temporary
root and validates all nine compositor-mask slices and optional helper syntax.
**The tests have been added but not executed here**; the theme has also not
been tested in a running Plasma 6.8.1/KWin session. Before production: run `bash -n` on the recipe, stage the
package and inspect the resulting archive; apply the theme in a non-critical
test user session; verify KWin blur and panel scaling visually.

## Optional GPU compositor configuration

The Aurora theme advertises `[BlurBehindEffect] enabled=true` and ships a
rounded background blur mask. Plasma requests KWin to blur behind the panel
when its compositor and blur effect are enabled; KWin chooses the GPU render
path. This does not need an external CPU polling loop or a separate daemon.

To opt in to the bundled profile in an **active KDE session**:

```sh
aurora-kwin-effects status
aurora-kwin-effects apply
```

The helper backs up an existing `~/.config/kwinrc` at
`~/.config/kwinrc.aurora-before-0.2` on its first run, sets blur enabled
and a moderate KWin BlurStrength of 4, and requests compositor reconfiguration.
It does **not** run as root, does not modify config during installation and
does not auto-enable a KWin plugin on existing users. The `restore` mode
reports the saved backup location rather than automatically overwriting any
later configuration edits.

For low-power/reduced-effects sessions, disable Blur in KDE's Desktop Effects
settings. Aurora remains usable without blur.

**Future work:** tighter KWin-side effect controls, per-panel blur radius,
performance measurement on Renoir integrated graphics, and an automated
non-destructive restore workflow.
