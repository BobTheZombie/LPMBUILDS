LPM Linux — qt5-base 5.15.19-1
=================================

Qt 5.15.19 source (last upstream OSS maintenance release, 2026-05-19):
https://download.qt.io/archive/qt/5.15/5.15.19/submodules/qtbase-everywhere-opensource-src-5.15.19.tar.xz
SHA-256: 51e91c73abacab81e64efd01bf95794e79c0e605ad80947a024769f0dd620a32

Install this recipe as qt5-base/qt5-base.lpmbuild in the LPM recipe tree.
Build: lpm buildpkg qt5-base

Qt 5 is required for kwayland-integration 6.8.1 (Qt5/KF5 compatibility).
Qt5 Base alone is NOT the complete stack. That package also requires:
- qt5-wayland (including Qt5WaylandClient and private headers)
- kf5-kwindowsystem
- kf5-kwayland
- plasma-wayland-protocols, wayland, wayland-protocols and xkbcommon

Qt5 qmake is installed in /usr/lib/qt5/bin/qmake with /usr/bin/qmake-qt5
as a convenience symlink. The package deliberately does not install
/usr/bin/qmake, avoiding conflicts with your Qt6 toolchain.

Note: Qt 5.15 is end-of-life upstream. This is for legacy compatibility,
not a recommended default development framework. Package dependency names
may need adjustment to match the exact providers in your LPM repository.

Validation: bash -n and tar archive contents were checked. Compilation
was not tested in an LPM chroot.
