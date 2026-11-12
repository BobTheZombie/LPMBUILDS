# LPM Plasma Aurora — patchset 0.4

Aurora is the LPM Linux visual patchset for KDE Plasma 6. Development is
**build-time**, not a shell script rewriting a user's files after installation.
The first deliverable is a separately versioned LPM package and an opt-in global
theme, keeping upstream Plasma and KWin binaries intact.

## Version 0.4 deliverables (including 0.1–0.3)

- Sapphire-violet semi-transparent Plasma panel 9-slice SVG
- High-opacity fallback for adaptive panel opacity
- Aurora dark KDE color scheme
- Selectable Plasma Style: **Aurora Glass**
- Selectable Global Theme: **Aurora**
- Opt-in bottom, centered, fit-content task dock layout
- Uses KDE TaskManager window and launcher model; does not monkey-patch its QML
- All assets written to LPM's `$pkgdir` during `staging()`; no user-home writes
- v0.2 compositor-aware `[BlurBehindEffect]` preferences in the theme `plasmarc`
- v0.2 nine-slice `mask-*` geometry for rounded KWin blur clipping
- v0.2 separate translucent and solid SVG panels for compositor fallback
- Optional `aurora-kwin-effects apply|status|restore` helper; opt-in only
- A separate Plasma 6 applet `org.lpm.aurora.dock` using KDE `TaskManager.TasksModel`
- Spring-based hover scaling, adjacent-item response, lift and perspective tilt
- Active task glow and running indicator, middle-click new application instance
- User-configurable magnification, icon size, glow and reduced-motion mode
- New org.lpm.aurora.launcher applet backed by KDE KRunner search
- Version-pinned optional Plasma 6.8.1 source patch for sapphire-violet volume/brightness OSD

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
2. **0.3 Aurora task manager** — implemented as a separate applet with
   spring-driven hover, 3D tilt, glow and motion preferences; not yet
   full parity with KDE’s built-in icons-only task manager.
3. **0.4 Aurora launcher and OSD** — source implementation committed, runtime testing pending.
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

## Aurora animated dock (0.3)

Plasma recognizes **Aurora Animated Dock** as the applet
`org.lpm.aurora.dock`. You can add it manually to an existing panel without
replacing the rest of the desktop. Selecting Aurora's *desktop layout* creates
a new centered panel with the applet, launcher, system tray and clock.
This is optional and can replace prior panel layout when explicitly selected.

The dock is a real KDE task-model frontend, not a list of launch buttons:
`org.kde.taskmanager.TasksModel` supplies tasks, launchers, active state,
and application icons. Left-click activates a task (or starts a launcher);
middle-click requests a new instance. It uses Qt Quick's scene-graph
transforms and spring animations, without shell polling or an animation loop.

Settings in the widget's **Motion** configuration page:

- **Reduced motion:** disables magnification, lift and perspective tilt
- **Hover magnification:** default 1.38x (range 1.0–1.8)
- **Icon size:** default 42 px (range 28–64)
- **Glow:** optional highlight for active and hovered tasks

The applet ships default launchers for Dolphin, Konsole and Firefox;
missing desktop files won't launch until installed. Unlike KDE's stock
task manager, the initial v0.3 applet does **not yet** implement the full
context menu, drag/drop task reordering, pinned-launcher editing, previews,
or group popups. Task grouping is disabled so activation always targets one
window. Use the original KDE icons-only task manager when those features
are required.

**Plasma API compatibility:** the QML model is part of Plasma's task manager
implementation and may change across releases. This package targets the
LPM Plasma 6.8.1 stack and needs a runtime smoke test before general use.

Recommended smoke-test procedure in a test account:

```sh
python3 -m pytest tests/test_plasma_aurora.py -q
lpm buildpkg --KDE--/plasma-aurora/plasma-aurora.lpmbuild
# After installing the resulting .zst through LPM:
kpackagetool6 --type Plasma/Applet --list | grep -i aurora
```

Then add **Aurora Animated Dock** to a panel and verify task activation,
new-instance launching, hover, Wayland animation smoothness and reduced
motion. KDE's full icons-only task manager remains separately available.

## 0.4 Search Launcher

The new Aurora Launcher (org.lpm.aurora.launcher) is a separate Plasma applet. It uses KDE's Kicker RunnerModel, not shell commands, to search and launch applications. The popup displays matching results, icons and descriptions. Click or press Enter to activate a selected result; Escape closes the popup. The Aurora global-theme layout selects it, but installation never overwrites existing user panels. Stock Kickoff remains installed.

## 0.4 Opt-in KWin/Plasma OSD styling

A version-pinned patch for Plasma Workspace 6.8.1 changes shell/qml/Osd.qml by wrapping the existing OsdItem in a rounded translucent violet Rectangle, preserving its signal aliases, progress bar, volume and brightness controls. It is applied at source build time only, not by modifying installed QML after packaging. Build an Aurora-patched Workspace with:

```sh
LPM_AURORA_PATCHSET=1 lpm buildpkg --KDE--/plasma-workspace/plasma-workspace.lpmbuild
```

That sets RELEASE=7 and declares PATCHES=(0001-aurora-0.4-glass-osd.patch). Normal Workspace builds do not enable the patch. The patch must be ported and reviewed before any change to Plasma 6.8.1. Real KWin backdrop blur for OSD windows is dependent on compositor handling; this initial source patch guarantees only rounded translucent tinted styling, not sampled backdrop blur.

## Verification

Staging and syntax tests, plus a dry-run/application test for the Workspace source patch, have been added to tests/test_plasma_aurora.py. They have not been run in this session. A live Plasma 6.8.1 test is needed to verify Kicker model result activation, launcher focus, and OSD readability before merging the draft PR.
