from database.mongo import soil_collection

def _key(value):
    return " ".join(str(value or "").strip().lower().split())


def get_soil_data(city, soil_type):
    """Fetch soil data for a specific city and soil type"""
    city_key = _key(city)
    soil_key = _key(soil_type)
    if soil_collection is None or not city_key or not soil_key:
        return None

    soil_data = soil_collection.find_one({
        "city": city_key,
        "soil_type": soil_key
    })

    return soil_data

def create_or_update_soil_data(data):
    """Create or update soil data"""
    if soil_collection is None:
        return None

    normalized = {
        **data,
        "city": _key(data.get("city")),
        "soil_type": _key(data.get("soil_type")),
    }
    result = soil_collection.update_one(
        {
            "city": normalized["city"],
            "soil_type": normalized["soil_type"]
        },
        {"$set": normalized},
        upsert=True
    )

    return result

def initialize_soil_data():
    """Initialize database with real soil data for different Indian regions"""
    if soil_collection is None:
        print("❌ Soil collection not available")
        return

    # Real-world soil data for Indian agricultural regions
    soil_data = [
        # DELHI REGION
        {
            "city": "delhi",
            "soil_type": "loamy",
            "N": 25,
            "P": 12,
            "K": 140,
            "ph": 7.8,
            "crops": ["Wheat", "Rice", "Potato"],
            "region": "NCR (National Capital Region)",
            "season": "Rabi"
        },
        {
            "city": "delhi",
            "soil_type": "sandy",
            "N": 15,
            "P": 8,
            "K": 80,
            "ph": 7.2,
            "crops": ["Jowar", "Bajra"],
            "region": "NCR",
            "season": "Kharif"
        },
        {
            "city": "delhi",
            "soil_type": "clay",
            "N": 35,
            "P": 18,
            "K": 200,
            "ph": 8.0,
            "crops": ["Rice", "Cotton"],
            "region": "NCR",
            "season": "Kharif"
        },
        # PUNJAB REGION
        {
            "city": "amritsar",
            "soil_type": "loamy",
            "N": 45,
            "P": 22,
            "K": 180,
            "ph": 7.5,
            "crops": ["Wheat", "Rice", "Basmati Rice"],
            "region": "Punjab",
            "season": "Rabi/Kharif"
        },
        {
            "city": "ludhiana",
            "soil_type": "loamy",
            "N": 48,
            "P": 25,
            "K": 190,
            "ph": 7.6,
            "crops": ["Wheat", "Rice", "Cotton", "Sugarcane"],
            "region": "Punjab",
            "season": "Rabi/Kharif"
        },
        # MAHARASHTRA REGION
        {
            "city": "pune",
            "soil_type": "loamy",
            "N": 35,
            "P": 16,
            "K": 150,
            "ph": 7.2,
            "crops": ["Sugarcane", "Jowar", "Cotton"],
            "region": "Maharashtra",
            "season": "Kharif/Rabi"
        },
        {
            "city": "nagpur",
            "soil_type": "clay",
            "N": 40,
            "P": 20,
            "K": 170,
            "ph": 6.8,
            "crops": ["Cotton", "Rice", "Gram"],
            "region": "Maharashtra",
            "season": "Kharif"
        },
        # KARNATAKA REGION
        {
            "city": "bangalore",
            "soil_type": "sandy",
            "N": 32,
            "P": 15,
            "K": 140,
            "ph": 6.5,
            "crops": ["Sugarcane", "Arecanut", "Coconut", "Maize"],
            "region": "Karnataka",
            "season": "Kharif"
        },
        {
            "city": "belgaum",
            "soil_type": "loamy",
            "N": 38,
            "P": 18,
            "K": 155,
            "ph": 6.8,
            "crops": ["Cotton", "Jowar", "Sugarcane"],
            "region": "Karnataka",
            "season": "Kharif/Rabi"
        },
        # TAMIL NADU REGION
        {
            "city": "coimbatore",
            "soil_type": "loamy",
            "N": 40,
            "P": 19,
            "K": 165,
            "ph": 6.3,
            "crops": ["Cotton", "Sugarcane", "Coconut", "Groundnut"],
            "region": "Tamil Nadu",
            "season": "Kharif/Rabi"
        },
        # RAJASTHAN REGION
        {
            "city": "jaipur",
            "soil_type": "sandy",
            "N": 20,
            "P": 10,
            "K": 100,
            "ph": 7.8,
            "crops": ["Bajra", "Jowar", "Groundnut", "Mustard"],
            "region": "Rajasthan",
            "season": "Rabi"
        },
        {
            "city": "jodhpur",
            "soil_type": "sandy",
            "N": 18,
            "P": 9,
            "K": 90,
            "ph": 8.0,
            "crops": ["Bajra", "Camel", "Mustard"],
            "region": "Rajasthan",
            "season": "Rabi"
        },
        # UTTAR PRADESH REGION
        {
            "city": "lucknow",
            "soil_type": "loamy",
            "N": 42,
            "P": 20,
            "K": 175,
            "ph": 7.3,
            "crops": ["Wheat", "Rice", "Sugarcane", "Potato"],
            "region": "Uttar Pradesh",
            "season": "Rabi/Kharif"
        },
        {
            "city": "kanpur",
            "soil_type": "loamy",
            "N": 44,
            "P": 22,
            "K": 180,
            "ph": 7.4,
            "crops": ["Wheat", "Rice", "Sugarcane"],
            "region": "Uttar Pradesh",
            "season": "Rabi/Kharif"
        },
        # ANDHRA PRADESH REGION
        {
            "city": "hyderabad",
            "soil_type": "loamy",
            "N": 38,
            "P": 17,
            "K": 160,
            "ph": 6.9,
            "crops": ["Cotton", "Sugarcane", "Groundnut", "Rice"],
            "region": "Andhra Pradesh",
            "season": "Kharif/Rabi"
        },
        # WEST BENGAL REGION
        {
            "city": "kolkata",
            "soil_type": "clay",
            "N": 50,
            "P": 26,
            "K": 200,
            "ph": 7.1,
            "crops": ["Rice", "Jute", "Potato", "Sugarcane"],
            "region": "West Bengal",
            "season": "Kharif/Rabi"
        },
    ]

    if soil_collection.count_documents({}) == 0:
        result = soil_collection.insert_many(soil_data)
        print(f"✅ Initialized {len(result.inserted_ids)} soil data records")
    else:
        print("ℹ️ Soil data already initialized")

def get_all_cities():
    """Get list of all cities in the database"""
    if soil_collection is None:
        return []

    cities = soil_collection.distinct("city")
    return sorted(list(set([city.title() for city in cities])))

def get_soil_types_for_city(city):
    """Get available soil types for a specific city"""
    if soil_collection is None:
        return []

    soil_types = soil_collection.find(
        {"city": _key(city)},
        {"soil_type": 1}
    )

    return list(set([doc["soil_type"].title() for doc in soil_types]))
