# lpm-filesystem

Base filesystem and integration package for LPM.

After install:

```bash
sudo systemd-sysusers /usr/lib/sysusers.d/lpm.conf
sudo systemd-tmpfiles --create /usr/lib/tmpfiles.d/lpm.conf
```

Verify:

```bash
getent group lpm
getent passwd lpm
ls -ld /etc/lpm /var/lib/lpm /var/cache/lpm /var/log/lpm /tmp/lpm-build
```

Suggested split:

- `filesystem`: core OS filesystem skeleton
- `lpm-filesystem`: LPM-specific dirs, users, tmpfiles, sysusers
- `lpm`: actual package manager implementation
- `lpm-hooks`: default hooks for kernel, mkinitcpio, grub, icon cache, schemas, etc.
