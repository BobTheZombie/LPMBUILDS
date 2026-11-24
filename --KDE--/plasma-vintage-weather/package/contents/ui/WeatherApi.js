.pragma library

function codeType(code) {
    if (code === 0) return "sun";
    if (code === 1 || code === 2) return "partly";
    if (code === 3) return "cloud";
    if (code === 45 || code === 48) return "fog";
    if (code >= 95) return "storm";
    if (code >= 71 && code <= 86) return "snow";
    if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) return "rain";
    return "cloud";
}
function description(code, day) {
    if (code === 0) return day ? "Clear sunshine" : "Clear night";
    if (code === 1) return "Mainly clear";
    if (code === 2) return "Partly cloudy";
    if (code === 3) return "Overcast skies";
    if (code === 45 || code === 48) return "Misty & foggy";
    if (code >= 95) return "Thunderstorms";
    if (code === 71 || code === 73 || code === 75 || code === 77 || code === 85 || code === 86) return "Snowfall";
    if (code >= 56 && code <= 57) return "Freezing drizzle";
    if (code >= 66 && code <= 67) return "Freezing rain";
    if (code >= 51 && code <= 55) return "Light drizzle";
    if (code >= 61 && code <= 65) return "Rain showers";
    if (code >= 80 && code <= 82) return "Rain showers";
    return "Changing weather";
}
function glyph(code, day) {
    var type = codeType(code);
    if (type === "storm") return "ϟ";
    if (type === "snow") return "❄";
    if (type === "rain") return "☂";
    if (type === "fog") return "≋";
    if (type === "cloud") return "☁";
    if (type === "partly") return "⛅";
    return day ? "☀" : "☾";
}
function requestJson(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState !== XMLHttpRequest.DONE) return;
        if (xhr.status !== 200) {
            callback(null, "HTTP " + xhr.status);
            return;
        }
        try {
            callback(JSON.parse(xhr.responseText), "");
        } catch (e) {
            callback(null, "Invalid weather response");
        }
    };
    try {
        xhr.open("GET", url, true);
        xhr.send();
    } catch (e) {
        callback(null, "Network unavailable");
    }
}
function forecastUrl(latitude, longitude, unit) {
    var base = "https://api.open-meteo.com/v1/forecast";
    var query = [
        "latitude=" + encodeURIComponent(latitude),
        "longitude=" + encodeURIComponent(longitude),
        "current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,is_day,wind_speed_10m",
        "daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset",
        "temperature_unit=" + (unit === "celsius" ? "celsius" : "fahrenheit"),
        "wind_speed_unit=" + (unit === "celsius" ? "kmh" : "mph"),
        "timezone=auto",
        "forecast_days=5"
    ];
    return base + "?" + query.join("&");
}
function geocodeUrl(location, countryCode) {
    var name = location.split(",")[0].trim();
    return "https://geocoding-api.open-meteo.com/v1/search?name=" +
        encodeURIComponent(name) + "&count=10&language=en&format=json" +
        (countryCode ? "&countryCode=" + encodeURIComponent(countryCode) : "");
}
function bestLocation(results, location) {
    if (!results || !results.length) return null;
    var desired = location.split(",").slice(1).join(",").trim().toLowerCase();
    if (!desired) return results[0];
    for (var i = 0; i < results.length; i++) {
        var admin = (results[i].admin1 || "").toLowerCase();
        if (admin === desired || admin.indexOf(desired) >= 0) return results[i];
    }
    return results[0];
}
function formatDegree(number) {
    return number === undefined || number === null ? "—" : Math.round(number) + "°";
}
