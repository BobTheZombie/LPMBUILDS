LPM Linux: libfakekey 0.3+git20170516
======================================
This X11 library synthesizes keyboard input via the XTest extension.
It is not a native Wayland input injection API, though X11/XWayland
applications may use it as supported by their X server.

Source: the unmodified libfakekey source archive used by Debian,
  https://deb.debian.org/debian/pool/main/libf/libfakekey/
Checksum: SHA-256 from the corresponding source package metadata.

Build system: GNU Autotools. Run autoreconf only when ./configure is
not available, then configure/make/DESTDIR install. Shared library only.

Build-time dependencies: gcc, make, pkgconf, autoconf, automake,
libtool, gettext, libX11 and libXtst. The LPM names must match your
repository's providers; do not create fake -dev/-devel dependencies.

After installation verify:
    pkg-config --modversion libfakekey
    ls -l /usr/lib/libfakekey.so*
    ls -l /usr/include/fakekey/fakekey.h

LPM source resolution: _libfakekey_src searches for configure.ac or
configure.in; it does not assume an upstream archive directory name.

Validated: bash -n and archive integrity. Not compilation-tested in
an LPM Linux chroot.
