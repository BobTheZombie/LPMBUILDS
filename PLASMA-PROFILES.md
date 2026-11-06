# LPM Plasma 6.8.1 packaging profiles

The goal is a complete Plasma Wayland desktop **without mandatory Qt WebEngine**.

## Deterministic installation

```sh
lpm buildpkg plasma6-full --yes
lpm buildpkg plasma6-extras --yes
```

- `plasma6-full` is the everyday desktop meta-package. Its `REQUIRES` includes the core Plasma/Frameworks/Qt stack, KDE Gear utilities, PackageKit with the LPM backend, Discover, Flatpak permissions KCM, Wayland on-screen keyboard, SDL2 for controller integration, printing, network and audio support.
- `plasma6-extras` is an opt-in meta-package. Its explicit `REQUIRES` pulls `plasma6-full`, Plasma SDK, first-run setup, SMB/network file support, UDisks, desktop interoperability helpers, fonts and metadata tools.
- Recipes may list other components under `RECOMMENDS` or `SUGGESTS`. These are SAT soft preferences; **not guaranteed installed**. Use a meta-package `REQUIRES` for functionality that must be present.

## Qt WebEngine exclusion

No hard dependency in either meta-package names `qt6-webengine`.

Plasma's optional CMake feature probes are allowed to discover already-installed integration libraries; no global disable switches for KAccounts or PackageKit. However **`signon-ui` itself requires Qt WebEngine**, and must not be added to either meta-package. KAccounts can be built independently when desired; without a suitable alternative UI, certain online-account login flows may be unavailable.

## Current optional recipes still outstanding

`krdp` needs FreeRDP 3 development libraries and its KPipeWire/PAM stack. `kup` needs libgit2 and a supported backup backend. They are not included as hard requirements until their complete recipe chains are available and validated.

SDDM is retained; Plasma Login Manager is an alternative, not an additional requirement.

## GitLab/GitHub sync

The GitHub repository is currently mirrored *from* the GitLab canonical package source. The new/updated GitHub recipes must be carried back to GitLab before `lpm buildpkg <name>` resolves them through the usual remote dependency fetch. The GitHub sync workflow may overwrite local-only changes on its next run.

No full chroot build has been performed for these new recipe additions. Run the dependency SAT plan and test staging on LPM before making them release-blocking.
