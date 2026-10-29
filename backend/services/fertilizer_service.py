from models.npk_region_model import get_npk_for_crop_region, get_fertilizer_for_crop, get_region_from_coordinates, get_nearby_region


def recommend_fertilizer(crop, latitude=None, longitude=None, city=None):
    """
    Enhanced fertilizer recommendation with region-based NPK values

    Args:
        crop: Crop name
        latitude: Optional farmer latitude
        longitude: Optional farmer longitude
        city: Optional city name for fallback

    Returns:
        Dictionary with fertilizer type and NPK values
    """
    crop_lower = crop.lower()

    # Get region and NPK values
    npk = None

    if latitude is not None and longitude is not None:
        # Use coordinates
        try:
            npk = get_npk_for_crop_region(crop_lower, latitude, longitude)
        except Exception as e:
            print(f"Error in get_npk_for_crop_region: {e}")
            npk = None

    if npk is None and city:
        # Use city to determine region
        region = get_nearby_region(city)
        npk_data = {"N": 100, "P": 50, "K": 40}

        # Try to get from recommendations
        from models.npk_region_model import NPK_RECOMMENDATIONS
        if region in NPK_RECOMMENDATIONS and crop_lower in NPK_RECOMMENDATIONS[region]:
            npk_data = NPK_RECOMMENDATIONS[region][crop_lower].copy()

        npk = {**npk_data, "region": region, "crop": crop_lower}

    if npk is None:
        # Default
        npk = {"N": 100, "P": 50, "K": 40, "region": "Unknown", "crop": crop_lower}

    # Get fertilizer type
    try:
        fertilizer = get_fertilizer_for_crop(crop_lower)
    except Exception as e:
        print(f"Error in get_fertilizer_for_crop: {e}")
        fertilizer = {"type": "General NPK", "description": "General purpose fertilizer"}

    return {
        "crop": crop,
        "fertilizer_type": fertilizer.get("type", "General NPK"),
        "description": fertilizer.get("description", "General purpose fertilizer"),
        "npk_values": {
            "N": npk.get("N", 100),
            "P": npk.get("P", 50),
            "K": npk.get("K", 40)
        },
        "region": npk.get("region", "Unknown"),
        "dosage": f"{npk.get('N', 100)} kg/ha Nitrogen, {npk.get('P', 50)} kg/ha Phosphorus, {npk.get('K', 40)} kg/ha Potassium"
    }