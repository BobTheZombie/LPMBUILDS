#!/usr/bin/env python3
"""Validate Plasma Aurora package payload, original SVG icons and frame assets."""
import configparser
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
icons = share / "icons"
wall = share / "wallpapers/PlasmaAurora"

def metadata(path, expected):
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["KPlugin"]["Id"] == expected, (path, data)
    assert data["KPlugin"]["Version"] == "0.4.0", path

def svg_ids(path):
    tree = ET.parse(path)
    return {e.get("id") for e in tree.iter() if e.get("id")}

positions = {"topleft", "top", "topright", "left", "center", "right",
             "bottomleft", "bottom", "bottomright"}
metadata(style / "metadata.json", "org.lpm.aurora")
metadata(look / "metadata.json", "org.lpm.aurora.desktop")
metadata(wall / "metadata.json", "PlasmaAurora")
for name in ("widgets/panel-background.svg", "widgets/background.svg",
             "dialogs/background.svg", "solid/widgets/panel-background.svg"):
    assert positions <= svg_ids(style / name), name

states = {
    "listitem.svg": ["normal", "hover", "pressed", "section"],
    "viewitem.svg": ["normal", "hover", "selected", "selected+hover"],
    "tasks.svg": ["normal", "focus", "hover", "attention", "minimized"],
    "button.svg": ["normal", "hover", "pressed", "focus",
                   "toolbutton-hover", "toolbutton-pressed", "toolbutton-focus"],
    "menubaritem.svg": ["normal", "hover", "pressed"],
    "tabbar.svg": ["north-active-tab", "south-active-tab",
                   "east-active-tab", "west-active-tab"],
}
for filename, names in states.items():
    ids = svg_ids(style / "widgets" / filename)
    for state in names:
        required = {f"{state}-{p}" for p in positions}
        assert required <= ids, (filename, state, sorted(required - ids))
    if filename in {"listitem.svg", "viewitem.svg", "tasks.svg"}:
        path = style / "widgets" / filename
        contents = path.read_text(encoding="utf-8")
        assert 'fill-opacity="0.001"' in contents, filename

assert colors.is_file()
defaults = (look / "contents/defaults").read_text(encoding="utf-8")
assert "ColorScheme=Aurora" in defaults
assert "name=org.lpm.aurora" in defaults
assert "Theme=PlasmaAurora" in defaults
assert (look / "contents/layouts/org.kde.plasma.desktop-layout.js").is_file()
min_icons = {"categories":20, "apps":18, "actions":14, "places":10, "status":10}
for pack in ("PlasmaAurora", "PlasmaAuroraViolet"):
    location = icons / pack
    config = configparser.ConfigParser(interpolation=None)
    assert config.read(location / "index.theme"), pack
    section = config["Icon Theme"]
    assert section.get("Name"), pack
    dirs = set(section.get("Directories", "").split(","))
    for category in min_icons:
        assert f"scalable/{category}" in dirs, (pack, category)
    assert "hicolor" in section.get("Inherits", "").lower(), pack
    count = 0
    for file in location.glob("scalable/**/*.svg"):
        ET.parse(file)
        count += 1
    if pack == "PlasmaAurora":
        assert count >= 80, (pack, count)
        for cat, minimum in min_icons.items():
            assert len(list((location / "scalable" / cat).glob("*.svg"))) >= minimum, cat
    else:
        assert count >= 15, count
        assert "PlasmaAurora" in section["Inherits"]

for png in (wall / "contents/images/2560x1440.png",
            wall / "contents/screenshot.png",
            look / "contents/previews/preview.png"):
    raw = png.read_bytes()[:24]
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", png
    assert all(i > 0 for i in struct.unpack(">II", raw[16:24])), png
assert (root / "usr/bin/aurora-profile").is_file()
print("[OK] Aurora 0.4: KDE SVG frames, icon packs, KPackage metadata, wallpaper and profiles")
