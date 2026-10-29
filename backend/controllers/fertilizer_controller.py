from services.fertilizer_service import recommend_fertilizer

def get_fertilizer(crop):
    fertilizer = recommend_fertilizer(crop)

    return {
        "success": True,
        "crop": crop,
        "fertilizer": fertilizer
    }