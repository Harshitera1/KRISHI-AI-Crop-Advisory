from database.mongo import db

users_collection = db["users"]

def create_user(user):
    return users_collection.insert_one(user)

def find_user_by_username(username):
    return users_collection.find_one({"username": username})