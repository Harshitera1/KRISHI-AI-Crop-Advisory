"""OpenWeather geocoding, current conditions, and a short forecast."""
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

TIMEOUT = 8
_GEO_CACHE = {}
_NOMINATIM = "https://nominatim.openstreetmap.org/search"
_NOMINATIM_REVERSE = "https://nominatim.openstreetmap.org/reverse"


def _api_key():
    return os.getenv("WEATHER_API_KEY")


def _missing_key():
    return {"success": False, "msg": "WEATHER_API_KEY is not configured"}


def _get(url, params):
    response = requests.get(url, params=params, timeout=TIMEOUT)
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    return response.status_code, payload


def _same_point(left, right):
    try:
        return abs(float(left["lat"]) - float(right["lat"])) < 0.02 and abs(float(left["lon"]) - float(right["lon"])) < 0.02
    except (KeyError, TypeError, ValueError):
        return False


def _best_name_score(query, places):
    return max((_name_score(query, place) for place in places), default=0)


def _name_score(query, place):
    needle = " ".join((query or "").lower().replace(",", " ").split())
    if not needle:
        return 0
    haystack = " ".join(
        part.lower()
        for part in (place.get("name"), place.get("state"), place.get("country"))
        if part
    )
    if needle == (place.get("name") or "").lower():
        return 100
    if needle in haystack:
        return 80
    tokens = [token for token in needle.split() if len(token) > 2]
    if tokens and all(token in haystack for token in tokens):
        return 70
    return 30


def _place_from_openweather(item):
    return {
        "name": item.get("name") or "Selected place",
        "state": item.get("state") or "",
        "country": item.get("country") or "",
        "lat": item.get("lat"),
        "lon": item.get("lon"),
        "source": "openweather",
    }


def geocode(query, limit=5):
    """Resolve a place name. OpenWeather first, OpenStreetMap if that is empty."""
    text = (query or "").strip()
    if not text:
        return {"success": False, "msg": "A place name is required"}

    cache_key = ("q", text.lower(), limit)
    if cache_key in _GEO_CACHE:
        return _GEO_CACHE[cache_key]

    key = _api_key()
    results = []
    try:
        from services.location_service import match_voice_location

        known = match_voice_location(text)
    except Exception:
        known = None
    if known and known.get("match_type") == "exact":
        results.append({
            "name": known.get("district") or known.get("location"),
            "state": known.get("state") or "",
            "country": "IN",
            "lat": known.get("latitude"),
            "lon": known.get("longitude"),
            "source": "gazetteer",
        })
    if key:
        for query in (f"{text},IN", text):
            status, payload = _get(
                "https://api.openweathermap.org/geo/1.0/direct",
                {"q": query, "limit": limit, "appid": key},
            )
            if status == 200 and isinstance(payload, list):
                for item in payload:
                    place = _place_from_openweather(item)
                    if not any(_same_point(place, existing) for existing in results):
                        results.append(place)
            if _best_name_score(text, results) >= 80:
                break

    if _best_name_score(text, results) < 80:
        response = requests.get(
            _NOMINATIM,
            params={"q": f"{text}, India", "format": "jsonv2", "limit": limit, "addressdetails": 1, "countrycodes": "in"},
            headers={"User-Agent": "KRISHI-AI-Crop/1.0 (educational capstone)"},
            timeout=TIMEOUT,
        )
        payload = response.json() if response.status_code == 200 else []
        if isinstance(payload, list):
            for item in payload:
                address = item.get("address") or {}
                place = {
                    "name": item.get("name") or item.get("display_name", "Selected place").split(",")[0],
                    "state": address.get("state", ""),
                    "country": (address.get("country_code") or "").upper(),
                    "lat": float(item["lat"]),
                    "lon": float(item["lon"]),
                    "source": "nominatim",
                }
                if not any(_same_point(place, existing) for existing in results):
                    results.append(place)

    if not results:
        result = {"success": False, "msg": f"Could not find a place named '{text}'"}
    else:
        ranked = sorted(results, key=lambda place: _name_score(text, place), reverse=True)
        result = {"success": True, "results": ranked[:limit]}
    _GEO_CACHE[cache_key] = result
    return result


def reverse_geocode(latitude, longitude):
    """Name a coordinate pair."""
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return {"success": False, "msg": "Latitude and longitude must be numbers"}

    cache_key = ("rev", round(latitude, 3), round(longitude, 3))
    if cache_key in _GEO_CACHE:
        return _GEO_CACHE[cache_key]

    key = _api_key()
    place = None
    if key:
        status, payload = _get(
            "https://api.openweathermap.org/geo/1.0/reverse",
            {"lat": latitude, "lon": longitude, "limit": 1, "appid": key},
        )
        if status == 200 and isinstance(payload, list) and payload:
            place = _place_from_openweather(payload[0])
            place["lat"] = latitude
            place["lon"] = longitude

    if place is None:
        response = requests.get(
            _NOMINATIM_REVERSE,
            params={"lat": latitude, "lon": longitude, "format": "jsonv2"},
            headers={"User-Agent": "KRISHI-AI-Crop/1.0 (educational capstone)"},
            timeout=TIMEOUT,
        )
        if response.status_code == 200:
            payload = response.json()
            address = payload.get("address") or {}
            place = {
                "name": payload.get("name") or address.get("village") or address.get("town") or address.get("city") or "Selected place",
                "state": address.get("state", ""),
                "country": (address.get("country_code") or "").upper(),
                "lat": latitude,
                "lon": longitude,
                "source": "nominatim",
            }

    if place is None:
        place = {
            "name": "Selected place",
            "state": "",
            "country": "",
            "lat": latitude,
            "lon": longitude,
            "source": "coordinates",
        }
    result = {"success": True, "place": place}
    _GEO_CACHE[cache_key] = result
    return result


def _daily_forecast(entries):
    buckets = {}
    for entry in entries:
        stamp = entry.get("dt_txt") or ""
        day = stamp.split(" ")[0]
        if not day:
            continue
        rain = float((entry.get("rain") or {}).get("3h") or 0)
        temp = float((entry.get("main") or {}).get("temp") or 0)
        bucket = buckets.setdefault(day, {"date": day, "rain_mm": 0.0, "temps": []})
        bucket["rain_mm"] += rain
        bucket["temps"].append(temp)

    daily = []
    for day in sorted(buckets):
        bucket = buckets[day]
        temps = bucket["temps"] or [0]
        daily.append({
            "date": day,
            "rain_mm": round(bucket["rain_mm"], 1),
            "temp_min": round(min(temps), 1),
            "temp_max": round(max(temps), 1),
        })
    return daily


def seasonal_rainfall_mm(forecast_rain_5d):
    """Scale a 5-day rain total to a 90-day figure in the model's rainfall units.

    The saved model was trained on seasonal rainfall, not a single day's rain.
    A dry or wet week is therefore expanded to a 90-day proxy and labeled as such.
    """
    daily = float(forecast_rain_5d or 0) / 5.0
    return round(daily * 90.0, 1)


def get_weather_by_coords(latitude, longitude):
    key = _api_key()
    if not key:
        return _missing_key()
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return {"success": False, "msg": "Latitude and longitude must be numbers"}

    status, current = _get(
        "https://api.openweathermap.org/data/2.5/weather",
        {"lat": latitude, "lon": longitude, "appid": key, "units": "metric"},
    )
    if status != 200:
        return {"success": False, "msg": current.get("message", "Weather request failed")}

    forecast_status, forecast = _get(
        "https://api.openweathermap.org/data/2.5/forecast",
        {"lat": latitude, "lon": longitude, "appid": key, "units": "metric"},
    )
    entries = forecast.get("list", []) if forecast_status == 200 else []
    daily = _daily_forecast(entries)
    forecast_rain = round(sum(day["rain_mm"] for day in daily), 1)
    seasonal = seasonal_rainfall_mm(forecast_rain)
    weather_rows = current.get("weather") or [{}]
    return {
        "success": True,
        "city": current.get("name") or "Selected place",
        "latitude": round(latitude, 4),
        "longitude": round(longitude, 4),
        "temperature": current.get("main", {}).get("temp"),
        "humidity": current.get("main", {}).get("humidity"),
        "condition": weather_rows[0].get("description", ""),
        "rainfall": seasonal,
        "forecast_rain_5d_mm": forecast_rain,
        "seasonal_rainfall_mm": seasonal,
        "rainfall_note": (
            "Seasonal rainfall sent to the model is the next five days of forecast rain, "
            "scaled to 90 days. It is a proxy, not a full monsoon total."
        ),
        "daily": daily,
        "fetched_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def get_weather(city):
    """Backward-compatible city lookup. Resolves the name, then reads coordinates."""
    found = geocode(city, limit=1)
    if not found.get("success"):
        return {"success": False, "msg": found.get("msg", "Place not found")}
    place = found["results"][0]
    weather = get_weather_by_coords(place["lat"], place["lon"])
    if weather.get("success"):
        weather["city"] = place["name"] or weather.get("city")
        weather["latitude"] = place["lat"]
        weather["longitude"] = place["lon"]
    return weather
