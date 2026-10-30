import logging
import re

from flask import g

from database.mongo import history_collection
from models.soil_model import get_soil_data
from services.crop_service import predict_crop
from services.fertilizer_service import recommend_fertilizer
from services.location_service import find_nearest_location
from services.reference_service import cards_for
from services.weather_service import geocode, get_weather_by_coords, reverse_geocode
from utils.validation import validate_crop_input

logger = logging.getLogger(__name__)

_SOIL_PH = {"loamy": 6.5, "sandy": 5.5, "clay": 7.5, "silty": 6.0, "silt": 6.0, "peaty": 5.8}


def _as_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp_nutrient(value):
    number = _as_float(value)
    if number is None:
        return None
    return max(0.0, min(150.0, number))


def _crop_names(records):
    names = []
    for record in records or []:
        if isinstance(record, str):
            names.append(record)
        elif isinstance(record, dict) and record.get("crop"):
            names.append(record["crop"])
    return names


def _crop_key(crop):
    return re.sub(r"[^a-z0-9]", "", str(crop or "").casefold())


def _resolve_coordinates(data):
    latitude = _as_float(data.get("latitude"))
    longitude = _as_float(data.get("longitude"))
    label = data.get("location") or "Selected place"
    if latitude is not None and longitude is not None:
        named = reverse_geocode(latitude, longitude)
        place = named.get("place") or {}
        return {
            "latitude": latitude,
            "longitude": longitude,
            "name": place.get("name") or label,
            "state": place.get("state") or "",
            "country": place.get("country") or "",
        }

    found = geocode(label, limit=1)
    if not found.get("success"):
        return {"error": found.get("msg", "Could not resolve the place")}
    place = found["results"][0]
    return {
        "latitude": place["lat"],
        "longitude": place["lon"],
        "name": place.get("name") or label,
        "state": place.get("state") or "",
        "country": place.get("country") or "",
    }


def _soil_from_profile(profile, soil_type):
    profile_ph = _as_float(profile.get("ph"))
    return {
        "N": _clamp_nutrient(profile.get("N")),
        "P": _clamp_nutrient(profile.get("P")),
        "K": _clamp_nutrient(profile.get("K")),
        "ph": profile_ph if profile_ph is not None else _SOIL_PH.get(soil_type.lower(), 6.5),
        "soil_source": "nearest_profile",
    }


def _stored_soil_profile(names, soil_type):
    seen = set()
    for name in names:
        key = str(name or "").strip().casefold()
        if not key or key in seen:
            continue
        seen.add(key)
        try:
            profile = get_soil_data(name, soil_type)
        except Exception as error:
            logger.warning(
                "Stored soil profile lookup failed",
                extra={
                    "event": "soil_profile_lookup_error",
                    "location": name,
                    "error": str(error),
                },
            )
            continue
        if profile:
            return profile
    return None


def _suitable_crops(profile, fallback_crops):
    found = (profile.get("crops") or []) if profile is not None else (fallback_crops or [])
    unique = []
    seen = set()
    for crop in found:
        key = _crop_key(crop)
        if key and key not in seen:
            seen.add(key)
            unique.append(str(crop).strip())
    return unique


def get_crop(data):
    errors = validate_crop_input(data)
    if errors:
        return {"success": False, "errors": errors}

    city = data.get("location") or "Selected place"
    soil_type = data.get("soil") or "Loamy"
    resolved = _resolve_coordinates(data)
    if resolved.get("error"):
        return {"success": False, "message": resolved["error"]}

    latitude = resolved["latitude"]
    longitude = resolved["longitude"]
    location_match = find_nearest_location(latitude, longitude)
    if not location_match:
        return {"success": False, "message": "Could not match this point to a district profile"}

    region = location_match.get("region", "North")
    nearest_city = location_match.get("location", "Unknown")
    logger.info(
        "Location determined for filtering",
        extra={
            "event": "location_determined",
            "nearest_city": nearest_city,
            "region": region,
            "distance_km": location_match.get("distance_km"),
            "user_provided_location": city,
        },
    )

    weather = get_weather_by_coords(latitude, longitude)
    if not weather.get("success"):
        logger.error(
            "Weather fetch failed",
            extra={"event": "weather_error", "request_id": g.get("request_id"), "response": weather},
        )
        return {
            "success": False,
            "message": weather.get("message") or weather.get("msg") or "Weather request failed",
        }

    requested_source = str(data.get("soil_source") or "farmer").lower()
    farmer_npk = {
        "N": _clamp_nutrient(data.get("N")),
        "P": _clamp_nutrient(data.get("P")),
        "K": _clamp_nutrient(data.get("K")),
        "ph": _as_float(data.get("ph")),
    }
    stored_profile = _stored_soil_profile(
        (city, resolved.get("name"), nearest_city),
        soil_type,
    )
    if requested_source == "estimate" or any(value is None for value in farmer_npk.values()):
        selected_profile = stored_profile or location_match
        soil_values = _soil_from_profile(selected_profile, soil_type)
        soil_values["soil_source"] = "stored_profile" if stored_profile else "nearest_profile"
        for key, value in farmer_npk.items():
            if value is not None and requested_source != "estimate":
                soil_values[key] = value
                soil_values["soil_source"] = "mixed"
    else:
        soil_values = {**farmer_npk, "soil_source": "farmer"}

    suitable_crops = _suitable_crops(
        stored_profile,
        location_match.get("crops"),
    )
    rainfall = weather.get("seasonal_rainfall_mm")
    ml_input = {
        "N": soil_values["N"],
        "P": soil_values["P"],
        "K": soil_values["K"],
        "temperature": weather.get("temperature", 25),
        "humidity": weather.get("humidity", 50),
        "ph": soil_values["ph"],
        "rainfall": rainfall if rainfall is not None else 0,
    }

    result = predict_crop(ml_input, top_n=22)
    if not isinstance(result, list):
        return {"success": False, "message": result}

    suitable_keys = {_crop_key(crop) for crop in suitable_crops}
    filtered = [
        {**item, "fit": "soil_profile"}
        for item in result
        if _crop_key(item["crop"]) in suitable_keys and item["confidence"] > 0
    ]
    if stored_profile is not None or suitable_crops:
        result = filtered[:3]
    else:
        result = [{**item, "fit": "model"} for item in result[:3]]

    if not result:
        return {
            "success": True,
            "recommendation_available": False,
            "recommended_crop": None,
            "top_3": [],
            "message": (
                "The selected soil profile does not overlap the preserved model classes "
                "with a non-zero probability, so no crop recommendation is shown."
            ),
            "weather": weather,
            "ml_input": ml_input,
            "soil_info": {
                "city": resolved["name"],
                "state": resolved.get("state") or location_match.get("state"),
                "soil_type": soil_type,
                "region": region,
                "suitable_crops": suitable_crops,
                "soil_source": soil_values["soil_source"],
                "N": ml_input["N"],
                "P": ml_input["P"],
                "K": ml_input["K"],
                "ph": ml_input["ph"],
            },
            "fertilizer": None,
            "mapped_location": nearest_city,
            "user_selected_location": resolved["name"],
            "resolved_place": resolved,
            "region": region,
            "proximity": location_match,
            "nearby_crops": location_match.get("crops", []),
            "crop_cards": [],
            "advisory_basis": "unavailable",
        }

    top_confidence = result[0]["confidence"]
    if (
        location_match.get("proximity_level") == "distant"
        or top_confidence < 0.45
        or soil_values["soil_source"] != "farmer"
    ):
        advisory_basis = "nearest_trend"
    else:
        advisory_basis = "field"

    try:
        if history_collection is not None:
            history_collection.insert_one({
                "user": g.get("user"),
                "input": {
                    "location": resolved["name"],
                    "latitude": latitude,
                    "longitude": longitude,
                    "soil": soil_type,
                    "soil_source": soil_values["soil_source"],
                    "N": ml_input["N"],
                    "P": ml_input["P"],
                    "K": ml_input["K"],
                    "ph": ml_input["ph"],
                },
                "result": result,
                "weather": {
                    "temperature": float(weather.get("temperature") or 0),
                    "humidity": float(weather.get("humidity") or 0),
                    "city": weather.get("city"),
                    "condition": weather.get("condition"),
                    "seasonal_rainfall_mm": rainfall,
                },
                "soil_type": soil_type,
                "region": region,
                "nearest_district": nearest_city,
                "distance_km": location_match.get("distance_km"),
            })
    except Exception as error:
        logger.error(
            "History save failed",
            extra={"event": "history_error", "request_id": g.get("request_id"), "error": str(error)},
        )

    recommended_crop = result[0]["crop"]
    try:
        fertilizer_rec = recommend_fertilizer(
            recommended_crop,
            latitude=latitude,
            longitude=longitude,
            city=nearest_city,
        )
    except Exception as error:
        logger.error(
            "Fertilizer recommendation error",
            extra={"event": "fertilizer_error", "request_id": g.get("request_id"), "error": str(error)},
        )
        fertilizer_rec = {
            "crop": recommended_crop,
            "fertilizer_type": "General NPK",
            "description": "General purpose fertilizer",
            "npk_values": {"N": 100, "P": 50, "K": 40},
            "region": region,
            "dosage": "Confirm the rate with a soil test before applying fertilizer.",
        }

    return {
        "success": True,
        "recommended_crop": recommended_crop,
        "top_3": result,
        "weather": weather,
        "ml_input": ml_input,
        "soil_info": {
            "city": resolved["name"],
            "state": resolved.get("state") or location_match.get("state"),
            "soil_type": soil_type,
            "region": region,
            "suitable_crops": suitable_crops,
            "soil_source": soil_values["soil_source"],
            "N": ml_input["N"],
            "P": ml_input["P"],
            "K": ml_input["K"],
            "ph": ml_input["ph"],
        },
        "fertilizer": fertilizer_rec,
        "mapped_location": nearest_city,
        "user_selected_location": resolved["name"],
        "resolved_place": resolved,
        "region": region,
        "proximity": location_match,
        "nearby_crops": location_match.get("crops", []),
        "crop_cards": cards_for(result),
        "advisory_basis": advisory_basis,
    }
