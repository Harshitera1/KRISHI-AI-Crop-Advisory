from services.soil_service import fetch_soil_data, get_available_cities, get_available_soil_types
import logging
from flask import g

logger = logging.getLogger(__name__)

def get_soil_by_location(city, soil_type):
    """Controller to get soil data by location and soil type"""

    if not city or not soil_type:
        return {
            "success": False,
            "message": "City and soil_type parameters are required"
        }

    result = fetch_soil_data(city, soil_type)
    return result

def list_cities():
    """Controller to list all available cities"""
    result = get_available_cities()
    return result

def list_soil_types(city):
    """Controller to list soil types for a city"""

    if not city:
        return {
            "success": False,
            "message": "City parameter is required"
        }

    result = get_available_soil_types(city)
    return result
