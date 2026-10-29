from flask import Blueprint, request, jsonify
from controllers.soil_controller import get_soil_by_location, list_cities, list_soil_types
from auth.auth_middleware import token_required

soil_bp = Blueprint("soil", __name__)

@soil_bp.route("/data", methods=["GET"])
@token_required
def get_soil_data():
    """Get soil data for a specific city and soil type"""
    city = request.args.get("city")
    soil_type = request.args.get("soil_type")

    result = get_soil_by_location(city, soil_type)
    return jsonify(result)

@soil_bp.route("/cities", methods=["GET"])
@token_required
def get_cities():
    """Get list of available cities"""
    result = list_cities()
    return jsonify(result)

@soil_bp.route("/soil-types", methods=["GET"])
@token_required
def get_soil_types():
    """Get soil types for a specific city"""
    city = request.args.get("city")

    result = list_soil_types(city)
    return jsonify(result)
