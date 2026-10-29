from database.mongo import db

farm_collection = db["farms"] if db is not None else None

def create_farm(data):
    if farm_collection is None:
        return None
    return farm_collection.insert_one(data)

def get_farms_by_user(username):
    if farm_collection is None:
        return []
    return list(farm_collection.find({"username": username}, {"_id": 0}))