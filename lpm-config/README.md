# lpm-config

Non-destructive baseline configuration for LPM Linux, designed to complement
(but **not** replace) the existing filesystem, bash, shadow, PAM, and init packages.

## What it seeds

On initial installation, its LPM package transaction hook creates missing:
- /etc/profile, /etc/profile.d/10-lpm-path.sh
- /etc/skel/.profile, .bash_profile and .bashrc, .bash_logout for future user homes
- /etc/default/useradd, /etc/login.defs (only if shadow has not installed them)
- /etc/shells, listing only executable shells found on the target
- /etc/nsswitch.conf, /etc/hosts, /etc/issue, /etc/motd, /etc/locale.conf
- /etc/xdg/user-dirs.defaults

Templates are installed under /usr/share/lpm-config/defaults and are owned by
this package. Actual /etc files are generated, not package-owned: local changes
and symlinks are preserved on installation and upgrade. Another package
(notably bash) may own /etc/skel/.bashrc; that file is left untouched.
The legacy lpm --sysconfig helper may also create similar defaults, but
neither tool should overwrite a file already present.

The seeder does not modify:
- /etc/passwd, /etc/group, /etc/shadow or existing user homes
- PAM policy, systemd enablement and other init system state
- /etc/fstab, /etc/hostname, /etc/resolv.conf, time zones or bootloader files

It is not a substitute for full package ownership/conflict validation.

## Administration

Install through LPM so the post-transaction hook runs:

    lpm install lpm-config

Or invoke it manually:

    /usr/libexec/lpm-config/apply
    /usr/libexec/lpm-config/apply --dry-run
    /usr/libexec/lpm-config/apply --verify

For a prepared offline root filesystem tree:

    /usr/libexec/lpm-config/apply --root /path/to/rootfs

It reads templates from the target root, not from the executing host. The
--verify mode exits nonzero if any default is missing.

Use shadow for normal interactive account provisioning:

    useradd -m -s /bin/bash username

This copies /etc/skel into *new* homes. It does not rewrite pre-existing
homes; sysusers should be reserved for system accounts, not interactive users.

## Locale, firmware, and networking

The initial locale fallback is LANG=C, avoiding unsupported C.UTF-8 warnings
until a UTF-8 locale has been generated. This package does not generate
locales, enable network services, modify /etc/resolv.conf, or select firmware.

## Implementation and ownership notes

The install hook is a Package trigger for lpm-config Install and Upgrade.
It calls /usr/libexec/lpm-config/apply and honors LPM_ROOT (or --root).
Because template files live in /usr/share, packaging them has no collision
with /etc/skel owned by bash or with configuration from shadow/glibc.
The seeder always skips existing files and symlinks, uses noclobber on new
files and rejects symlinked parent directories in a target root.
It does not depend on systemd, preserving LPM's multi-init support.

Runtime requirements: bash, coreutils, shadow. Config-only arch: any.
