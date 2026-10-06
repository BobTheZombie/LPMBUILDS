# RyzenOS filesystem

Build/install:

```bash
sudo lpm buildpkg filesystem/filesystem.lpmbuild
```

After install, initialize sysusers/tmpfiles manually if LPM hooks do not do it yet:

```bash
sudo systemd-sysusers /usr/lib/sysusers.d/filesystem.conf
sudo systemd-tmpfiles --create /usr/lib/tmpfiles.d/filesystem.conf
```

This package intentionally does not own LPM-specific directories. Use `lpm-filesystem` for `/etc/lpm`, `/var/lib/lpm`, `/var/cache/lpm`, hooks, repos, and build roots.
