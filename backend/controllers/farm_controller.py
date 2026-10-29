from models.farm_model import create_farm, get_farms_by_user

def add_farm(data):
    if not data or not data.get("username"):
        return {"success": False, "msg": "Username required"}

    saved = create_farm(data)
    if saved is None:
        return {"success": False, "msg": "Database not connected"}
    return {"success": True, "msg": "Farm added successfully"}

def list_farms(username):
    if not username:
        return {"success": False, "msg": "Username required", "farms": []}
    return {"success": True, "farms": get_farms_by_user(username)}