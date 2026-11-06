LPM Linux — libssh 0.12.2
=========================
This package supplies the SSH library required by KDE Konsole. The relevant
CMake package is named lowercase "libssh", not "libssh2".

Build prerequisites:
    cmake, ninja, openssl (development headers), zlib, pkgconf
Runtime:
    openssl, zlib, glibc

Uses the official libssh-0.12.2.tar.xz release, checked against the
published SHA-256 recorded by FreeBSD ports:
49560f677d96e3706a904ac2de1116e25f3680937d51e5c92198fcba4a1c1e9f

Expected installed files:
    /usr/lib/libssh.so
    /usr/include/libssh/libssh.h
    /usr/lib/pkgconfig/libssh.pc
    /usr/lib/cmake/libssh/libssh-config.cmake
    /usr/lib/cmake/libssh/libssh-config-version.cmake

After installing:
    pkg-config --modversion libssh
    ls /usr/lib/cmake/libssh/libssh-config.cmake

Build recipe syntax and archive structure were verified. A complete
compile in the LPM chroot has not been performed.
