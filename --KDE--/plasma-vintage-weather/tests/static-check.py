#!/usr/bin/env python3
"""Static structural checks; these do not substitute for a real Plasma runtime."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

base = Path(__file__).resolve().parents[1]
package = base / "package"
metadata = json.loads((package / "metadata.json").read_text())
assert metadata["KPlugin"]["Id"] == "org.lpm.vintageweather"
assert metadata["KPackageStructure"] == "Plasma/Applet"
assert metadata["X-Plasma-API-Minimum-Version"] == "6.0"
config = ET.parse(package / "contents/config/main.xml")
entries = {e.get("name") for e in config.iter() if e.tag.endswith("entry")}
assert {"location","countryCode","temperatureUnit","refreshMinutes",
        "animations","showSeconds","use24Hour"} <= entries
main = (package / "contents/ui/main.qml").read_text()
clock = (package / "contents/ui/AntiqueClock.qml").read_text()
weather = (package / "contents/ui/WeatherScene.qml").read_text()
api = (package / "contents/ui/WeatherApi.js").read_text()
for marker in ("PlasmoidItem", "WeatherScene", "AntiqueClock", "refreshNow",
               "requestForecast", "Weather by Open-Meteo"):
    assert marker in main, marker
for marker in ("XII","roman","bezel","seconds"):
    assert marker in clock, marker
for marker in ('"rain"', '"snow"', '"storm"', '"fog"', "createLinearGradient"):
    assert marker in weather, marker
assert "api.open-meteo.com/v1/forecast" in api
assert "geocoding-api.open-meteo.com/v1/search" in api
assert "XMLHttpRequest" in api
assert (package / "contents/config/config.qml").exists()
assert (package / "contents/ui/configGeneral.qml").exists()
print("Aurora Vintage Weather structural checks passed")
