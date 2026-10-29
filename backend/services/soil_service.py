import logging
from models.soil_model import get_soil_data, get_all_cities, get_soil_types_for_city
from flask import g

logger = logging.getLogger(__name__)

def fetch_soil_data(city, soil_type):
    """Fetch soil NPK values for a given city and soil type"""
    try:
        soil_data = get_soil_data(city, soil_type)

        if soil_data:
            logger.info(
                "Soil data found",
                extra={
                    "event": "soil_data_found",
                    "request_id": g.get("request_id"),
                    "city": city,
                    "soil_type": soil_type,
                    "N": soil_data.get("N"),
                    "P": soil_data.get("P"),
                    "K": soil_data.get("K")
                }
            )

            return {
                "success": True,
                "data": {
                    "city": soil_data.get("city"),
                    "soil_type": soil_data.get("soil_type"),
                    "N": soil_data.get("N"),
                    "P": soil_data.get("P"),
                    "K": soil_data.get("K"),
                    "ph": soil_data.get("ph"),
                    "crops": soil_data.get("crops", []),
                    "region": soil_data.get("region"),
                    "season": soil_data.get("season")
                }
            }
        else:
            from services.location_service import profile_for_name

            profile = profile_for_name(city)
            if profile:
                return {
                    "success": True,
                    "source": "nearest_profile",
                    "data": {
                        "city": profile.get("district"),
                        "soil_type": profile.get("soil"),
                        "N": profile.get("N"),
                        "P": profile.get("P"),
                        "K": profile.get("K"),
                        "ph": profile.get("ph"),
                        "crops": profile.get("crops", []),
                        "region": profile.get("region"),
                        "season": profile.get("season"),
                        "distance_km": profile.get("distance_km"),
                        "note": "Estimate from the district profile, not a laboratory test for this field.",
                    },
                }
            logger.warning(
                "Soil data not found",
                extra={
                    "event": "soil_data_not_found",
                    "request_id": g.get("request_id"),
                    "city": city,
                    "soil_type": soil_type
                }
            )

            return {
                "success": False,
                "message": f"Soil data not found for {city} ({soil_type})",
                "data": None
            }

    except Exception as e:
        logger.error(
            "Soil data fetch error",
            extra={
                "event": "soil_data_error",
                "request_id": g.get("request_id"),
                "error": str(e)
            }
        )

        return {
            "success": False,
            "message": f"Error fetching soil data: {str(e)}",
            "data": None
        }

def get_available_cities():
    """Get list of available cities, including the local district gazetteer."""
    try:
        cities = set(get_all_cities() or [])
        from services.location_service import list_district_names
        cities.update(list_district_names())
        return {
            "success": True,
            "cities": sorted(cities)
        }
    except Exception as e:
        logger.error(
            "Error fetching cities",
            extra={
                "event": "cities_fetch_error",
                "error": str(e)
            }
        )
        return {
            "success": False,
            "message": str(e),
            "cities": []
        }

def get_available_soil_types(city):
    """Get available soil types for a city"""
    try:
        soil_types = get_soil_types_for_city(city)
        return {
            "success": True,
            "soil_types": soil_types
        }
    except Exception as e:
        logger.error(
            "Error fetching soil types",
            extra={
                "event": "soil_types_fetch_error",
                "city": city,
                "error": str(e)
            }
        )
        return {
            "success": False,
            "message": str(e),
            "soil_types": []
        }
