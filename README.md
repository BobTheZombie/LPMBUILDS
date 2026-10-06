# LPM package recipes

LPM `.lpmbuild` package collection imported from the lpm-org GitLab repository.
The `lfs-13.1` branch aligns the base with LFS 13.1-systemd and includes selected
compatible Arch fixes.

See [baseline and validation notes](docs/lfs-13.1.md),
[version/source manifest](metadata/lfs-13.1.json), and
[patch provenance](metadata/patches-lfs-13.1.json).

```sh
python3 tools/check-lfs-baseline.py
python3 tools/check-lfs-baseline.py --source-dir /path/to/source-cache
```

Full base-system rebuild and boot validation remain necessary before release.
