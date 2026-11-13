# KWin 6.8.1 / LPM Zen 2 optimization experiment

**Status: build-time experimental variant, not an installed compositor.**

This is specifically for the LPM Linux Plasma 6.8.1 stack, GCC 16, Qt 6.12
and Ryzen 5 4500U (Zen 2 / AMD Renoir). Do not distribute the tuned package
as a generic x86_64 KWin build: `-march=znver2` can generate instructions
unavailable on older processors.

## Build profiles

- `debug` (default, release 3): original `RelWithDebInfo`, `-O2 -g`,
  frame pointers, original KWin source. Works as a recovery build.
- `zen2` (explicit, release 4): `-O3 -g`, Zen 2 architecture and tuning,
  `-fno-plt`, frame pointers, CMake IPO/LTO, and two source patches.
  Serial Ninja link jobs avoid simultaneous memory-hungry LTO links.
  ABI-facing KWin interfaces, KDE plugin APIs, X11 support, Wayland
  protocols, color transforms, and lock-screen support are unchanged.

The compiler flags and source optimizations are intended to reduce CPU
work. The *actual* renderer is still KWin's upstream OpenGL / Mesa pipeline
and does not secretly switch to Vulkan, force VRR, disable VSync, modify
scheduling policy, or use unreviewed inline assembly. **No measured
performance improvement is claimed without profiling on Renoir.**

### Source patches

1. `0001-kwin-blur-cache-clip-transforms.patch`: in the multiple-damage-rectangle
   case, pretransform each blur shape once, then intersect with each damage
   rectangle in the original clipping order. The common 0–1-clip case
   retains the original allocation-free path.
2. `0002-kwin-blur-share-kawase-projection.patch`: create the identical
   orthographic projection matrix once for both downsample and upsample
   blur passes.

Both patches target **exactly upstream KDE/kwin tag `v6.8.1`** and are applied
with the LPM strict `patch -p1` machinery before configure/build. If the
targeted source changes, patch application must fail instead of applying
a best-effort patch to another release.

## Validate before building

From the LPMBUILDS feature branch:

```sh
bash -n ./--KDE--/kwin/kwin.lpmbuild
python3 -m pytest -q tests/test_kwin_zen2.py
```

A GitHub Actions workflow checks both patches against the exact upstream
`KDE/kwin v6.8.1` tag, in sequence. This is **not** a full KWin build or
desktop session test.

## Build in LPM Linux

```sh
git clone --branch feature/kwin-6.8.1-zen2-optimization \
  https://github.com/BobTheZombie/LPMBUILDS.git
cd LPMBUILDS

# Use a value appropriate for RAM capacity and GCC 16 LTO:
LPM_BUILD_JOBS=4 LPM_KWIN_PROFILE=zen2 \
  lpm buildpkg ./--KDE--/kwin/kwin.lpmbuild
```

Do **not** accidentally build the default debug profile: check the output
for `KWin Zen 2 profile` and the resulting KWin package version
`6.8.1-4`. The build must pass before replacing the installed compositor.

Retain an installable copy of the existing **6.8.1-3** package first.
The fallback must include the entire KWin package, not just the
`kwin_wayland` executable (KWin libraries and effects must match).

## Installation / emergency recovery on bare metal

**PLM uses KWin Wayland for its login greeter**, so changing KWin while a
graphical session or login greeter is running is unsafe. Plan a console-only
boot and ensure a verified fallback KWin package is available offline.

1. Copy the existing 6.8.1-3 `.lpminstall` package to a known safe folder
   outside disposable build directories (e.g. `/root/kwin-recovery/`).
2. Enable a recovery console with
   `systemctl enable getty@tty3.service`, then
   `systemctl set-default multi-user.target` and `reboot`.
3. Log in on a text console. Confirm PLM/SDDM and any KWin session have
   stopped (`pgrep -a kwin_wayland`). Install the built 6.8.1-4 package
   through `lpm installpkg /absolute/path/to/kwin-6.8.1-4*.lpminstall`,
   replacing the example path with the *actual file*.
4. Check package integrity, `ldd -r /usr/bin/kwin_wayland` for missing
   libraries, and `systemctl status plmd` before testing.
5. Start PLM explicitly from the text console (`systemctl start plmd`).
   Verify the greeter, login, logout, screen locking, screen unlocking,
   displays, and animations. Only then restore
   `systemctl set-default graphical.target`.

**Rollback** from the recovery TTY: stop PLM and SDDM; reinstall the saved
KWin 6.8.1-3 package through `lpm installpkg /full/path/to/saved.lpminstall`;
verify library resolution; then start PLM (or SDDM). Do not remove
the fallback package until multiple successful cold boots.

### Verify performance and stability

Capture a baseline and tuned run at identical resolution, scale, refresh
rate and effects:
- frame time percentiles / stutter during normal desktop and blur-heavy
  workloads (not simply claimed FPS improvement)
- CPU usage and RSS of `kwin_wayland`
- GPU busy/clock/thermals, shader and Mesa errors, direct scanout behavior
- session stability, hotplug, screen-lock/unlock and long-running uptime

If the tuned build shows more memory use, increased 99th percentile frame
time, compiler regressions, or crashes, revert to 6.8.1-3 and compare.
