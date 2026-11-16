#!/usr/bin/env python3
"""Validate generated KDE KPackage files in LPM $pkgdir."""
import json
import pathlib
import struct
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(sys.argv[1])
share = root / "usr/share"
style = share / "plasma/desktoptheme/org.lpm.aurora"
look = share / "plasma/look-and-feel/org.lpm.aurora.desktop"
colors = share / "color-schemes/Aurora.colors"
icons = share / "icons/PlasmaAurora"
wall = share / "wallpapers/PlasmaAurora"

def metadata(path, expected):
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["KPlugin"]["Id"] == expected, (path, data)

metadata(style / "metadata.json", "org.lpm.aurora")
metadata(look / "metadata.json", "org.lpm.aurora.desktop")
metadata(wall / "metadata.json", "PlasmaAurora")
required_svg = {"topleft", "top", "topright", "left", "center", "right",
                "bottomleft", "bottom", "bottomright"}
for name in ("widgets/panel-background.svg", "widgets/background.svg",
             "dialogs/background.svg", "solid/widgets/panel-background.svg"):
    e = ET.parse(style / name)
    ids = {node.get("id") for node in e.iter()}
    assert required_svg.issubset(ids), (name, required_svg - ids)

assert colors.is_file()
assert "ColorScheme=Aurora" in (look / "contents/defaults").read_text()
assert "name=org.lpm.aurora" in (look / "contents/defaults").read_text()
assert (look / "contents/layouts/org.kde.plasma.desktop-layout.js").is_file()
assert (icons / "index.theme").is_file()
for name in ("scalable/places/start-here.svg", "scalable/apps/plasma-aurora.svg"):
    ET.parse(icons / name)
for png in (wall / "contents/images/2560x1440.png",
            wall / "contents/screenshot.png",
            look / "contents/previews/preview.png"):
    raw = png.read_bytes()[:24]
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", png
    assert struct.unpack(">II", raw[16:24])[0] > 0, png
assert (root / "usr/bin/aurora-profile").is_file()
print("[OK] Aurora metadata, SVGs, icons, scheme, PNGs, dock and helper validated")
