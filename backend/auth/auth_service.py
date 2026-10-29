from flask_bcrypt import Bcrypt
from database.mongo import users_collection

bcrypt = Bcrypt()

def signup_user(username, password):
    if users_collection is None:
        return {"success": False, "message": "Database connection failed. Please try again."}

    try:
        existing_user = users_collection.find_one({"username": username})

        if existing_user:
            return {"success": False, "message": "User already exists"}

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        users_collection.insert_one({
            "username": username,
            "password": hashed_password
        })

        return {"success": True, "message": "User created successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error during signup: {str(e)}"}


def login_user(username, password):
    if users_collection is None:
        return {"success": False, "message": "Database connection failed. Please try again."}

    try:
        user = users_collection.find_one({"username": username})

        if not user:
            return {"success": False, "message": "User not found"}

        if not bcrypt.check_password_hash(user["password"], password):
            return {"success": False, "message": "Invalid password"}

        return {"success": True}
    except Exception as e:
        return {"success": False, "message": f"Error during login: {str(e)}"}