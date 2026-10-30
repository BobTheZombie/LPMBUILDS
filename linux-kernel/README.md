# LPM Linux 7.2.11

Stable kernel release checked on 2026-10-16 against kernel.org/releases.json.
Source SHA-256 matches kernel.org's published v7.x/sha256sums.asc.

## Build

Keep all bundle files beside linux.lpmbuild, then run inside the target chroot:

    lpm buildpkg "$PWD/linux.lpmbuild" --install-default y

Runtime dependencies include mkinitcpio, kmod, systemd, Python and LPM. Their
recipes must be available to LPM. Build dependencies include bc, bison, flex,
OpenSSL and elfutils development files, in addition to the normal toolchain.
This bundle does not supply those separate dependency recipes.

The default build parallelism is limited by CPUs and available memory (about
1.5 GiB per job). LPM_BUILD_JOBS overrides it. Kbuild controls architecture flags:
LPM's userland -march=znver2/-fPIC/LTO options are not imported into kernel CFLAGS.
AMD Ryzen 4800U/Zen 2 runtime power management is enabled without making this
kernel require a Zen 2 CPU. Generic x86-64 is the distribution target.

## Configuration

The recipe generates x86_64_defconfig, adds config-lpm.fragment and runs
olddefconfig. This is a distribution seed, not your hardware inventory.
Includes systemd/cgroups/namespaces/seccomp, EFI stub, initramfs, audit,
IPv4/IPv6, nftables/connection sharing, Wi-Fi, common Ethernet drivers,
AMD/Intel graphics, built-in AHCI/NVMe/ext4 and modular Btrfs/XFS/device encryption.
Review/extend the fragment for your actual Wi-Fi/storage/display hardware.
Other root storage, filesystems, ZFS, unusual RAID, etc. need additional support.

The initramfs uses base/udev/modconf/keyboard/block/filesystems/fsck and omits
host autodetection because this is a chroot build. Filesystem fsck helpers must
be supplied by the corresponding filesystem-tools packages (e.g. e2fsprogs).
Encrypted root/LVM needs the relevant userspace packages and encrypt/lvm2 hooks
in /usr/lib/lpm/linux/mkinitcpio.conf, ideally maintained as a local recipe change.
Do not boot an encrypted-root machine with the plain-root default.
Early AMD microcode loading requires adding mkinitcpio's microcode hook and
installing the AMD microcode files. Kernel hardware support alone is not microcode.

Full debug/BTF and Rust are disabled for this bootstrap recipe. Module signing
is disabled; the produced kernel is not signed for a Secure Boot chain. Supply
an appropriate signing workflow if Secure Boot is enabled.

## Payload and integration

Kernel release is 7.2.11-lpm1. Canonical files are under:

    /usr/lib/modules/7.2.11-lpm1/vmlinuz
    /usr/lib/modules/7.2.11-lpm1/config
    /usr/lib/modules/7.2.11-lpm1/System.map
    /usr/lib/modules/7.2.11-lpm1/kernel/

No userspace headers are installed over /usr/include/linux, no /lib symlink is
created, and make install is not used. /lib -> usr/lib is filesystem-package
policy and must already be correct. Modules are stripped by Kbuild; vmlinuz is
not stripped by generic package processing. Kernel-devel/DKMS headers are not
included in this kernel package.

This package installs /etc/lpm/hooks/kernel-install.hook and
/etc/lpm/hooks/update-systemd-boot.hook as overrides of LPM's same-named vendor
hooks. Save any pre-existing administrator overrides before installing.
The supplied hooks replace the old mkinitcpio/GRUB workflow for these names;
no GRUB configuration is regenerated. Existing depmod hooks may also run safely.
The boot update explicitly depends on kernel-install.hook so initramfs completes
first. Both run PostTransaction, never during staging. Removal is also handled.
The script ignores alternate-root transactions: run it inside the target chroot.

On install/upgrade the initramfs is generated atomically at:

    /boot/initrd-7.2.11-lpm1.img

A failed initramfs command is reported; it is not hidden with `|| true`.
The script keeps working images until their replacements are generated.
Only kernels with pkgbase=linux are managed. This assumes LPM's normal
same-name admin hook override behavior; tested with the source available here.

## ESP at /boot/efi

Nothing writes the ESP until explicitly enabled. The package installs a config
example under /usr/share/doc/linux/linux.conf.example; it never replaces your
administrator-owned /etc/lpm/linux.conf or /etc/kernel/cmdline on upgrades.

Your previously supplied ESP UUID was D080-4232. If it is still the correct ESP,
its /etc/fstab entry is:

    UUID=D080-4232  /boot/efi  vfat  umask=0077  0  2

Mount that ESP inside the target chroot before boot maintenance:

    mkdir -p /boot/efi
    mount /boot/efi
    findmnt /boot/efi

Create /etc/kernel/cmdline containing one line with your ACTUAL root UUID:

    root=UUID=YOUR-ROOT-FILESYSTEM-UUID rw

The root UUID is not the ESP UUID. Use blkid/findmnt to identify your real root.
Add any required rootflags, encryption/LVM or other hardware parameters.
Do not copy the host's /proc/cmdline blindly while inside a chroot.

Enable configuration once (preserve an existing customized file):

    install -Dm644 /usr/share/doc/linux/linux.conf.example /etc/lpm/linux.conf
    sed -i 's/^enabled = false$/enabled = true/' /etc/lpm/linux.conf

For an existing systemd-boot installation:

    /usr/libexec/lpm/linux-maintain --initramfs --boot

For the first explicit systemd-boot installation:

    /usr/libexec/lpm/linux-maintain --initramfs --install-bootloader

bootctl uses --esp-path=/boot/efi --no-variables, so no UEFI NVRAM entry is
created/changed. First-time firmware boot selection may require a separate
explicit bootctl/efibootmgr action. These commands must run INSIDE the target
chroot, not on the host with a guessed alternate root.

Generated files on the ESP:

    /lpm-kernels/7.2.11-lpm1/vmlinuz
    /lpm-kernels/7.2.11-lpm1/initrd.img
    /loader/entries/lpm-linux-7.2.11-lpm1.conf

An existing loader.conf is preserved. Set its default to `lpm-linux-*` yourself
if it currently points elsewhere. The script only removes its own marked
entries and known payload files for removed kernel versions. It does not touch
unmanaged entries, firmware variables or unrelated ESP files.

The 821 MiB ESP must have room for kernel + initramfs and temporary copies during
updates. Keep a separate rescue/LTS kernel and boot entry. Normal replacement
of a single linux package removes its previous module tree; this does not offer
automatic multi-version package retention or firmware-level rollback.

## Verification

See VALIDATION.md. Configuration parsing, metadata and isolated hook tests can
be done here; a complete kernel build and boot on your Ryzen hardware cannot.

config-7.2.11.resolved is the tested configuration result for reference. The
recipe consumes config-lpm.fragment and regenerates the config, so local changes
belong in that fragment. Every local source checksum must be updated if edited.
