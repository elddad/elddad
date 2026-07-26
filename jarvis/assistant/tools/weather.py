"""Weather via the free Open-Meteo API (no API key required)."""

import json
import urllib.parse
import urllib.request

_WEATHER_CODES = {
    0: "clear sky", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "icy fog", 51: "light drizzle", 53: "drizzle",
    55: "heavy drizzle", 61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 80: "rain showers",
    81: "heavy rain showers", 82: "violent rain showers", 95: "thunderstorm",
    96: "thunderstorm with hail", 99: "severe thunderstorm with hail",
}


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "jarvis-assistant"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def get_weather(city: str) -> str:
    """Return a short human-readable weather summary for a city (works with Hebrew names too)."""
    geo = _get_json(
        "https://geocoding-api.open-meteo.com/v1/search?"
        + urllib.parse.urlencode({"name": city, "count": 1, "format": "json"})
    )
    results = geo.get("results")
    if not results:
        return f"Could not find a city named '{city}'."

    place = results[0]
    lat, lon = place["latitude"], place["longitude"]
    name = place.get("name", city)
    country = place.get("country", "")

    data = _get_json(
        "https://api.open-meteo.com/v1/forecast?"
        + urllib.parse.urlencode({
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "forecast_days": 1,
            "timezone": "auto",
        })
    )

    cur = data["current"]
    daily = data["daily"]
    desc = _WEATHER_CODES.get(cur.get("weather_code", -1), "unknown conditions")

    return (
        f"Weather in {name}, {country}: {desc}, {cur['temperature_2m']}°C "
        f"(feels like {cur['apparent_temperature']}°C), humidity {cur['relative_humidity_2m']}%, "
        f"wind {cur['wind_speed_10m']} km/h. "
        f"Today: {daily['temperature_2m_min'][0]}°C to {daily['temperature_2m_max'][0]}°C, "
        f"{daily['precipitation_probability_max'][0]}% chance of rain."
    )
