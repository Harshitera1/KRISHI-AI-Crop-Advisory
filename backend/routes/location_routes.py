from flask import Blueprint, jsonify, request

from auth.auth_middleware import token_required
from services.location_service import find_nearest_location, list_district_names
from services.weather_service import geocode, get_weather_by_coords, reverse_geocode

location_bp = Blueprint("location", __name__)


@location_bp.route("/districts", methods=["GET"])
@token_required
def districts():
    return jsonify({"success": True, "districts": list_district_names()})


@location_bp.route("/resolve", methods=["GET"])
@token_required
def resolve():
    """Geocode a name or a map point, then attach the nearest district and live weather."""
    latitude = request.args.get("lat")
    longitude = request.args.get("lon")
    query = (request.args.get("q") or "").strip()
    alternatives = []

    if latitude and longitude:
        named = reverse_geocode(latitude, longitude)
        if not named.get("success"):
            return jsonify(named), 400
        place = named["place"]
        alternatives = [place]
    elif query:
        found = geocode(query, limit=5)
        if not found.get("success"):
            return jsonify(found), 404
        alternatives = found["results"]
        place = alternatives[0]
    else:
        return jsonify({"success": False, "msg": "Provide a place name or latitude and longitude"}), 400

    nearest = find_nearest_location(place.get("lat"), place.get("lon"))
    weather = get_weather_by_coords(place.get("lat"), place.get("lon"))
    return jsonify({
        "success": True,
        "place": place,
        "alternatives": alternatives,
        "nearest": nearest,
        "weather": weather,
    })
