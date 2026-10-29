from flask import Blueprint, jsonify, request

from services.weather_service import geocode, get_weather, get_weather_by_coords

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/search", methods=["GET"])
def search_place():
    result = geocode(request.args.get("q", ""), limit=5)
    status = 200 if result.get("success") else 404
    return jsonify(result), status


@weather_bp.route("/at", methods=["GET"])
def weather_at():
    result = get_weather_by_coords(request.args.get("lat"), request.args.get("lon"))
    status = 200 if result.get("success") else 400
    return jsonify(result), status


@weather_bp.route("/<city>", methods=["GET"])
def get_weather_route(city):
    result = get_weather(city)
    status = 200 if result.get("success") else 400
    return jsonify(result), status
