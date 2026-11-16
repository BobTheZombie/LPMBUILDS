# LPM PackageKit backend: native packages and Flatpak refs

PackageKit 1.4.0-`5` keeps **native LPM** transactions as the default:
PackageKit uses `pk_backend_lpm.so`, the Python spawn helper, and the
existing SAT-backed `/usr/bin/lpm install`/`removepkg`/`upgrade`
commands.

## Explicit Flatpak references

The Python helper additionally recognizes names beginning with
`flatpak:` when resolving, inspecting or installing an application.
Examples:

```sh
pkcon resolve flatpak:org.mozilla.firefox
pkcon install flatpak:org.mozilla.firefox
pkcon remove flatpak:org.mozilla.firefox
```

The helper probes only the **system** Flatpak installation and the official
`flathub` remote. Mutations are routed to the LPM CLI, **not** directly
to the Flatpak executable:

```text
PackageKit / pkcon
  -> /usr/share/PackageKit/helpers/lpm/lpmBackend.py
  -> /usr/bin/lpm flatpak install --system --yes org.mozilla.firefox
  -> Flatpak/libflatpak + OSTree + Flathub signatures and permissions
```

Flatpak IDs use a separate PackageKit virtual name, e.g.
`flatpak:org.mozilla.firefox;0;noarch;flathub`, with strict ID
validation. Mixed native+Flatpak PackageKit transactions are rejected,
because no atomic rollback is available across the two package stores.
Flatpak records are **not** inserted into LPM's native SQLite database
or reported as native packages.

Discover's dedicated Flatpak backend remains the standard way to
**browse and install Flatpaks graphically**. The native PackageKit
backend only resolves Flatpak applications with the explicit
`flatpak:` prefix. This avoids duplicate applications in Discover
and keeps ordinary native package search and updates unchanged.

The PackageKit backend uses system-scope operations because it executes
as a privileged system service. For user-scoped applications, run
`lpm flatpak install --user org.mozilla.firefox` instead.

## Build, install and verify

Build and install the updated PackageKit 1.4.0-`5` recipe with LPM.
It now requires `flatpak` and `flatpak-flathub` in addition to the
native PackageKit dependencies.

```sh
lpm buildpkg packagekit
grep '^DefaultBackend=lpm$' /etc/PackageKit/PackageKit.conf
ls /usr/lib/packagekit-backend/libpk_backend_lpm.so
lpm flatpak remotes
pkcon resolve flatpak:org.mozilla.firefox
```

The included test `tests/test_packagekit_flatpak.py` verifies that all
Flatpak writes pass through `/usr/bin/lpm`, confirms the native route
is unchanged, and exercises invalid package IDs and transaction flags.

**Limitations:** Native package search remains separate from Flatpak
discovery. The integration tests are mocked and cannot confirm the
system D-Bus/PackageKit daemon or live Flathub availability; verify
these in a running LPM Linux installation.
