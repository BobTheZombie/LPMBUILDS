# Aurora Vintage Weather — native KDE Plasma 6 widget

An original QML weather dashboard for **LPM Linux / KDE Plasma 6.8**. No flip clock: a hand-painted, **antique Roman-numeral analog dial** with brass bezel, ivory face, sweeping seconds, and a subtle glass reflection. The weather scene uses animated sun, drifting cloud banks, rain, snow, mist, stars, moon, and occasional lightning, influenced by classic HTC Sense weather visuals, but drawn from scratch (no HTC assets).

## Features

- Live current conditions, feels-like, humidity, wind, four-day highs/lows.
- Local device time on the analog dial (not forecast-city time).
- Automatic weather refresh every 20 minutes (configurable 10–60) and manual refresh.
- Editable city and region (default Watervliet, Michigan), country code, °F / °C, animations, second hand, footer format.
- Open-Meteo HTTPS forecast and geocoding APIs: no key needed for eligible **noncommercial** usage.
- Stale weather remains visible with an error status if connectivity fails. No account, telemetry, or background process.
- QML-only package: works without rebuilding Plasma, KWin, or Qt.

## Install directly

From this repository checkout:

```sh
kpackagetool6 --type Plasma/Applet --install ./--KDE--/plasma-vintage-weather/package
```

On an existing installation, use `--upgrade` instead. Add **Aurora Vintage Weather** in Plasma's *Add Widgets* interface, then open *Configure* to set your city.

If `kpackagetool6` is unavailable, copy the entire `package` directory under `~/.local/share/plasma/plasmoids/org.lpm.vintageweather/` (the files `metadata.json` and `contents/` must be at that top level). Log out and back in if Plasma has cached old metadata.

## Build with LPM

```sh
lpm buildpkg plasma-vintage-weather
# install the resulting signed .lpminstall file:
lpm installpkg /path/to/plasma-vintage-weather-1.0.0-1.any.lpminstall
```

The recipe fetches a **pinned** Git source commit containing this widget. Package files are staged in `$pkgdir/usr/share/plasma/plasmoids/org.lpm.vintageweather/`. No post-install scripts alter a user's layout.

## Diagnostics

Run `python3 --KDE--/plasma-vintage-weather/tests/static-check.py` to verify the metadata, KConfig XML, file structure, forecast endpoints, and clock/animation markers. For a live test run `plasmoidviewer -a org.lpm.vintageweather` (package `plasma-sdk`) under a working Plasma session. QML behavior and network access require actual Plasma/Qt 6 testing.

## Attribution and service conditions

The widget source and original artwork are MIT licensed. Forecast data © [Open-Meteo](https://open-meteo.com/) under its attribution terms; geocoding data GeoNames via Open-Meteo. The hosted free API is intended for eligible noncommercial use and may have rate limits. For commercial distribution evaluate the [Open-Meteo terms](https://open-meteo.com/en/terms) and use an appropriate licensed/self-hosted service.

This project is not affiliated with HTC and does not include proprietary HTC Sense graphics or branding.
