# Validation — 2026-10-16

Completed:

- Fetched kernel.org's releases.json: stable release 7.2.11, dated 2026-10-15.
- Downloaded the actual 160,421,420-byte linux-7.2.11.tar.xz and verified SHA-256:
  fd0fc479f983a8c05313f13e9c36330fe6651cf725396748c40d5cd93fa1e6a4.
  This matches kernel.org/pub/linux/kernel/v7.x/sha256sums.asc. The OpenPGP
  signature on that published list was not independently verified here.
- Built the source tree's Kconfig host tools using GCC 13.3, flex 2.6.4,
  bison 3.8.2 and m4 1.4.19.
- Ran the actual recipe prepare() against that source: x86_64_defconfig,
  upstream merge_config.sh, olddefconfig and every essential-symbol assertion.
- All enabled/string fragment values survive dependency resolution exactly.
  The resolved reference config is included as config-7.2.11.resolved.
  The recipe generates its config from the fragment; the reference is not
  used as an additional source input.
- Ran kernelrelease: 7.2.11-lpm1.
- Validated Bash syntax of linux.lpmbuild and Python syntax of linux-maintain.
- Ran 10 isolated hook tests: payload creation, loader policy preservation,
  owned-entry cleanup, missing-initramfs preservation, refusal to overwrite
  unmanaged entries, rejection of symlink escapes, initramfs error handling,
  non-owned removal targets, alternate-root skipping and disabled boot updates.
  All bootctl/mkinitcpio/depmod invocations were mocked in these tests.
- Parsed both .hook files using the available LPM source's actual load_hooks().
  Tested its dependency sorter with reversed hook input: kernel-install runs
  before update-systemd-boot. Depends names use stems, not the .hook suffix.
- Checked SOURCE/SHA256SUMS counts and hashes of every local source asset.

Not performed:

- Complete bzImage/modules compilation with GCC 16.2.0.
- Actual modules_install, mkinitcpio execution, ESP writing, firmware boot
  selection or booting a Ryzen 4800U.
- Discovery of the user's Wi-Fi/storage hardware, root UUID or Secure Boot keys.

This is a configuration-tested source recipe and hook bundle, not a prebuilt
kernel or a claim that it has booted on the target hardware.

Primary release/checksum references:
https://www.kernel.org/releases.json
https://cdn.kernel.org/pub/linux/kernel/v7.x/sha256sums.asc
