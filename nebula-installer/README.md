# Nebula Installer for LPM Linux (Qt6 preview)

This LPM recipe installs Nebula's Python modules into system site-packages,
a root-owned executable at `/usr/bin/nebula-installer` and a desktop launcher.

The source is pinned to a specific commit in the Nebula-Installer feature branch
so the polkit-authorized worker cannot drift to newer unreviewed source.

## Launch

```bash
lpm buildpkg nebula-installer --yes
nebula-installer --gui
```

The normal KDE desktop user runs the GUI. Polkit authorizes the system-owned
worker only after the install plan has been reviewed and the exact target path
typed. Source packages are built *inside* the target chroot with
`lpm buildpkg PACKAGE --yes`; repository packages use
`lpm install --root TARGET PACKAGE`.

**Limitations:** The root filesystem and additional partitions must already be
created and mounted, with /dev, /proc and /sys prepared in the target. Nebula
does not partition/format disks, write a bootloader, or reboot. After LPM
installation, manually check /etc/fstab, kernel/initramfs and boot entries.
Use a disposable VM to validate the entire procedure before real hardware.

Upstream development PR:
https://github.com/BobTheZombie/Nebula-Installer/pull/11
