# 🌾 Regional NPK Database for Indian Crops
# This database contains optimal NPK values for different regions and crops

# Region coordinates for identification
REGION_COORDINATES = {
    "Delhi": {"lat": 28.7041, "lng": 77.1025, "region": "North"},
    "Punjab": {"lat": 31.1471, "lng": 74.8550, "region": "North"},
    "Haryana": {"lat": 29.0588, "lng": 77.0745, "region": "North"},
    "Uttar Pradesh": {"lat": 26.8467, "lng": 80.9462, "region": "North"},
    "Bihar": {"lat": 25.0961, "lng": 85.3131, "region": "East"},
    "West Bengal": {"lat": 24.8355, "lng": 88.2635, "region": "East"},
    "Jharkhand": {"lat": 23.6102, "lng": 85.2799, "region": "East"},
    "Maharashtra": {"lat": 19.7515, "lng": 75.7139, "region": "Central"},
    "Madhya Pradesh": {"lat": 22.9375, "lng": 78.6553, "region": "Central"},
    "Karnataka": {"lat": 15.3173, "lng": 75.7139, "region": "South"},
    "Tamil Nadu": {"lat": 11.1271, "lng": 78.6569, "region": "South"},
    "Telangana": {"lat": 18.1124, "lng": 79.0193, "region": "South"},
    "Andhra Pradesh": {"lat": 15.9129, "lng": 78.4855, "region": "South"},
}

# NPK Recommendations for different crops by region
# N, P, K values in kg/hectare
NPK_RECOMMENDATIONS = {
    "North": {
        "wheat": {"N": 120, "P": 60, "K": 40},
        "rice": {"N": 80, "P": 40, "K": 40},
        "maize": {"N": 150, "P": 75, "K": 40},
        "sugarcane": {"N": 150, "P": 80, "K": 80},
        "potato": {"N": 100, "P": 80, "K": 120},
        "cotton": {"N": 120, "P": 60, "K": 60},
        "chickpea": {"N": 20, "P": 50, "K": 20},
        "mustard": {"N": 60, "P": 40, "K": 20},
    },
    "East": {
        "wheat": {"N": 100, "P": 50, "K": 35},
        "rice": {"N": 100, "P": 50, "K": 40},
        "maize": {"N": 120, "P": 60, "K": 35},
        "sugarcane": {"N": 140, "P": 75, "K": 75},
        "jute": {"N": 80, "P": 40, "K": 40},
        "potato": {"N": 120, "P": 90, "K": 150},
        "lentil": {"N": 20, "P": 60, "K": 20},
        "tobacco": {"N": 100, "P": 50, "K": 50},
    },
    "Central": {
        "wheat": {"N": 110, "P": 55, "K": 35},
        "rice": {"N": 90, "P": 45, "K": 40},
        "maize": {"N": 140, "P": 70, "K": 40},
        "sugarcane": {"N": 160, "P": 85, "K": 85},
        "cotton": {"N": 150, "P": 75, "K": 75},
        "soybean": {"N": 0, "P": 60, "K": 40},
        "gram": {"N": 15, "P": 45, "K": 15},
        "groundnut": {"N": 20, "P": 40, "K": 20},
    },
    "South": {
        "rice": {"N": 120, "P": 60, "K": 40},
        "maize": {"N": 130, "P": 65, "K": 35},
        "sugarcane": {"N": 170, "P": 90, "K": 90},
        "coconut": {"N": 80, "P": 40, "K": 60},
        "coffee": {"N": 100, "P": 50, "K": 50},
        "pepper": {"N": 60, "P": 40, "K": 60},
        "groundnut": {"N": 25, "P": 50, "K": 25},
        "cotton": {"N": 140, "P": 70, "K": 70},
    },
}

# Fertilizer recommendations based on crop
FERTILIZER_TYPES = {
    "wheat": {"type": "Urea + DAP", "description": "High Nitrogen & Phosphorus"},
    "rice": {"type": "NPK 16:16:16 + Zinc", "description": "Balanced with Micronutrients"},
    "maize": {"type": "DAP + Urea", "description": "Nitrogen Heavy"},
    "sugarcane": {"type": "NPK 10:26:26", "description": "High K for juice quality"},
    "potato": {"type": "NPK 20:20:20 + Potash", "description": "Very High Potassium"},
    "cotton": {"type": "DAP + Urea + Potash", "description": "Balanced mixture"},
    "chickpea": {"type": "DAP + Organic compost", "description": "Low Nitrogen legume"},
    "mustard": {"type": "Urea + DAP", "description": "Moderate NPK"},
    "jute": {"type": "NPK 15:15:15", "description": "Balanced"},
    "lentil": {"type": "DAP + Organic", "description": "Low Nitrogen"},
    "tobacco": {"type": "Urea + Potash", "description": "High K, Low N"},
    "soybean": {"type": "DAP", "description": "Phosphorus for nodulation"},
    "gram": {"type": "DAP only", "description": "Low N legume"},
    "groundnut": {"type": "DAP + Gypsum", "description": "Phosphorus & Ca"},
    "coconut": {"type": "NPK 10:10:10 + Mg", "description": "Micronutrient rich"},
    "coffee": {"type": "NPK 12:12:17", "description": "K heavy for quality"},
    "pepper": {"type": "NPK 10:10:20", "description": "High Potassium"},
}


def get_npk_for_crop_region(crop, latitude, longitude):
    """
    Get optimal NPK values based on crop and region (from coordinates)

    Args:
        crop: Crop name
        latitude: Farmer's latitude
        longitude: Farmer's longitude

    Returns:
        Dictionary with N, P, K values
    """
    crop_lower = crop.lower()

    # First get nearest location to understand better
    nearest = get_nearest_location(latitude, longitude)
    region = nearest.get("region", "North")

    # Get recommendations from NPK database
    if region in NPK_RECOMMENDATIONS:
        if crop_lower in NPK_RECOMMENDATIONS[region]:
            npk = NPK_RECOMMENDATIONS[region][crop_lower].copy()
            npk["region"] = region
            npk["crop"] = crop_lower
            npk["nearest_city"] = nearest.get("city")
            return npk

    # Default fallback
    return {
        "N": 100,
        "P": 50,
        "K": 40,
        "region": region,
        "crop": crop_lower,
        "nearest_city": nearest.get("city")
    }


def get_fertilizer_for_crop(crop):
    """
    Get optimal fertilizer type for a crop
    """
    crop_lower = crop.lower()

    if crop_lower in FERTILIZER_TYPES:
        return FERTILIZER_TYPES[crop_lower]

    return {"type": "NPK 10:10:10", "description": "General Purpose"}


def get_nearest_location(latitude, longitude):
    """Find the nearest district profile. Delegates to the shared gazetteer."""
    from services.location_service import find_nearest_location

    if not latitude or not longitude:
        return {"city": "Unknown", "region": "North"}

    nearest = find_nearest_location(latitude, longitude)
    if not nearest:
        return {"city": "Unknown", "region": "North"}
    return {
        "city": nearest.get("location"),
        "region": nearest.get("region", "North"),
        "distance_km": nearest.get("distance_km"),
    }


def get_region_from_coordinates(latitude, longitude):
    """
    Determine region from coordinates using simple lat/lng ranges
    """
    if latitude > 24 and longitude < 78:  # North
        return "North"
    elif latitude < 24 and longitude > 82:  # East
        return "East"
    elif latitude > 20 and 74 < longitude < 82:  # Central
        return "Central"
    elif latitude < 20:  # South
        return "South"
    else:
        return "North"  # Default


def get_nearby_region(city_name):
    """
    Get region from city name
    """
    city_lower = city_name.lower()

    for city, coords in REGION_COORDINATES.items():
        if city_lower in city.lower() or city.lower() in city_lower:
            return coords["region"]

    return "North"  # Default
