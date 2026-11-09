# KDE application recipe coverage for LPM Linux

As of November 8, 2026.

## KDE Gear 26.08.3
This repository contains an individual source recipe for all **252 entries**
from the KDE Gear 26.08.3 release archive list. This includes libraries, KIO
plugins, PIM components, games, utility applications and desktop applications.

- 239 new KDE Gear recipes and 13 updated recipes from earlier 26.08.2 versions.
- Every Gear 26.08.3 recipe has a version-specific SHA-256 checksum matching
  KDE's published release manifests, cross-checked against
  NixOS/nixpkgs pkgs/kde/generated/sources/gear.json.
- Existing Plasma and Frameworks recipes are preserved and use their own
  release schedules; do not mistake KDE Gear for the whole KDE catalog.
- The older --KDE--/package-chain.json is an October 2026 Plasma bootstrap
  planning artifact and not the complete current KDE Gear inventory.

## Independently released KDE applications
Separate source recipes are included for:
- krita 6.0.4.1
- digikam 9.1.0
- kstars 3.8.5
- amarok 3.3.3
- kmymoney 5.2.2
- kdiff3 1.12.6

- haruna 1.9.0
- kid3 3.10.2
- kphotoalbum 6.2.0
- krusader 2.9.0
- labplot 2.12.1
- tellico 4.3
- gcompris 26.2

- calligraplan 4.0.1
- glaxnimate 0.6.0
- marknote 1.6.0
- liquidshell 1.10.1
- rkward 0.8.3
- rsibreak 0.13.0
- ruqola 2.9.0
- subtitlecomposer 0.8.2
- skrooge 26.8.0

- crow-translate 4.1.0
- drawy 1.0.2
- hana 1.0.0
- kgeotag 2.0.0
- klevernotes 1.3.1
- komodo 1.6.0
- kookbook 0.3.0
- ktimetracker 6.0.0

- heaptrack 1.5.0
- index-fm 4.0.2
- kaidan 0.16.0
- kodaskanna 0.2.3
- optiimage 1.0.0
- smb4k 4.0.7
- vvave 4.0.2

## Status and limitations

These are **packaging drafts**, not a claim that all 289 build in one pass.
Version/source SHA-256 is checked, but dependency closures, package naming,
license metadata, source-specific CMake flags, runtime assets, build options,
plugins and tests need package-by-package validation in a real LPM chroot.
Some KDE apps require external libraries not yet in LPMBUILDS. Confirm builds
with lpm buildpkg <name> --yes, capture missing CMake requirements, and update
REQUIRES and BUILD_REQUIRES rather than disabling mandatory functionality.

apps.kde.org also lists apps that are not in KDE Gear and may use independent
release sources, distributions, app bundles or multiple binary apps per source.
Therefore 252 source entries are not the same thing as every application on
apps.kde.org. Continue catalog-to-package mapping for remaining independent
projects before claiming complete website coverage.

## Upstream source references
- https://kde.org/info/releases-26.08.3/
- https://download.kde.org/stable/release-service/26.08.3/src/
- https://apps.kde.org/
