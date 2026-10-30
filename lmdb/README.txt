LMDB 0.9.37 -- LPM Linux package recipe

Contents:
  lmdb.lpmbuild       The LPM Linux source build recipe.

Usage:
  tar -xf lmdb-0.9.37-lpm.tar
  lpm buildpkg lmdb.lpmbuild

The upstream source is downloaded by LPM when you build this recipe.
The upstream source tarball is not bundled in this archive.

Dependencies: gcc, GNU make, binutils (build); glibc (runtime).
Includes shared liblmdb, C header, utility tools, man pages and pkg-config metadata.

NOTICE: SHA256SUMS is set to SKIP because the fresh upstream GitLab snapshot
could not be downloaded for hash verification in this environment. Pin a real
SHA256 after fetching and verifying the source before publishing this recipe
in a signed production repository.

This recipe was syntax-checked, but not end-to-end compiled in LPM Linux.
