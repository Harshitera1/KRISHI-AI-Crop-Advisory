"""Nearest-district matching for any farmer-selected coordinates."""
import json
import logging
import math
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "district_gazetteer.json"
_LOCAL_KM = 40
_NEAR_KM = 150


@lru_cache(maxsize=1)
def _gazetteer():
    with _DATA_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["districts"]


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def _proximity_level(distance_km):
    if distance_km <= _LOCAL_KM:
        return "local"
    if distance_km <= _NEAR_KM:
        return "near"
    return "distant"


def _note(district, distance_km, level):
    place = f"{district['district']}, {district['state']}"
    if level == "local":
        return (
            f"This point is about {distance_km:.0f} km from {place}. "
            "The nearby crop list is a local planning reference."
        )
    if level == "near":
        return (
            f"This point is about {distance_km:.0f} km from {place}. "
            "Advice uses that district as the closest known profile, not a soil test of this exact field."
        )
    return (
        f"This point is about {distance_km:.0f} km from the closest profile ({place}). "
        "Treat the crop list as the nearest known trend and confirm it locally before sowing."
    )


def _public_match(district, distance_km):
    level = _proximity_level(distance_km)
    return {
        "location": district["district"],
        "district": district["district"],
        "state": district["state"],
        "latitude": district["lat"],
        "longitude": district["lng"],
        "region": district["zone"],
        "distance": round(distance_km / 111.0, 3),
        "distance_km": round(distance_km, 1),
        "proximity_level": level,
        "note": _note(district, distance_km, level),
        "soil": district["soil"],
        "N": district["N"],
        "P": district["P"],
        "K": district["K"],
        "ph": district["ph"],
        "crops": district["crops"],
        "season": district["season"],
    }


def find_nearest_location(latitude, longitude):
    """Return the closest gazetteer district for a coordinate pair."""
    if latitude is None or longitude is None:
        return None
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return None

    best = None
    best_distance = float("inf")
    for district in _gazetteer():
        distance = haversine_km(latitude, longitude, district["lat"], district["lng"])
        if distance < best_distance:
            best = district
            best_distance = distance
    if best is None:
        return None

    result = _public_match(best, best_distance)
    logger.info(
        "Nearest district found",
        extra={
            "event": "location_matched",
            "input_coords": {"lat": latitude, "lng": longitude},
            "matched_location": result["district"],
            "distance_km": result["distance_km"],
        },
    )
    return result


def match_voice_location(location_text):
    """Match a spoken or typed name to a district, state, or alias."""
    if not location_text:
        return None
    text = " ".join(location_text.lower().split())
    districts = _gazetteer()

    for district in districts:
        names = [district["district"].lower(), *district.get("aliases", [])]
        if text in names:
            return {**_public_match(district, 0.0), "match_type": "exact"}

    for district in districts:
        haystack = [district["district"].lower(), district["state"].lower(), *district.get("aliases", [])]
        if any(name in text or text in name for name in haystack if len(name) > 2):
            return {**_public_match(district, 0.0), "match_type": "partial"}
    return None


def profile_for_name(name):
    """Return a district profile by district or alias, if one exists."""
    matched = match_voice_location(name)
    if not matched:
        return None
    return matched


def list_district_names():
    return sorted(district["district"] for district in _gazetteer())


def get_all_locations():
    return list_district_names()


def get_region_locations(region):
    return [
        district["district"]
        for district in _gazetteer()
        if district["zone"].lower() == str(region).lower()
    ]
