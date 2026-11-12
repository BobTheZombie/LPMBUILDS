"""Aurora 0.2 recipe staging smoke tests, no KDE runtime required."""
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "--KDE--/plasma-aurora/plasma-aurora.lpmbuild"
SLICES = {"topleft", "top", "topright", "left", "center", "right",
          "bottomleft", "bottom", "bottomright"}


def test_shell_syntax():
    subprocess.run(["bash", "-n", str(RECIPE)], check=True)


def test_staged_aurora_theme_and_compositor_opt_in(tmp_path):
    env = os.environ.copy()
    env["pkgdir"] = str(tmp_path / "stage")
    # Run only the stage function: LPM invokes it after unpack/build.
    subprocess.run(
        ["bash", "-c", 'source "$1"; staging', "aurora-test", str(RECIPE)],
        env=env, check=True, capture_output=True, text=True,
    )
    root = Path(env["pkgdir"])
    theme = root / "usr/share/plasma/desktoptheme/org.lpm.aurora"
    look = root / "usr/share/plasma/look-and-feel/org.lpm.aurora.desktop"
    assert json.loads((theme / "metadata.json").read_text())["KPlugin"]["Id"] == "org.lpm.aurora"
    assert json.loads((look / "metadata.json").read_text())["KPlugin"]["Id"] == "org.lpm.aurora.desktop"
    assert "[BlurBehindEffect]\nenabled=true" in (theme / "plasmarc").read_text()
    for opacity in ("widgets", "translucent/widgets", "solid/widgets"):
        svg = theme / opacity / "panel-background.svg"
        ids = {e.get("id") for e in ET.parse(svg).getroot().iter()}
        assert (SLICES | {"mask-" + p for p in SLICES}) <= ids
    assert (root / "usr/share/color-schemes/Aurora.colors").is_file()
    helper = root / "usr/bin/aurora-kwin-effects"
    assert os.access(helper, os.X_OK)
    subprocess.run(["sh", "-n", str(helper)], check=True)
    assert not (root / "etc/xdg/kwinrc").exists()
