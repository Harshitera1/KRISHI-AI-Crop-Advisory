import jwt
import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import create_user, find_user_by_username

SECRET_KEY = os.getenv("SECRET_KEY", "krishi_secret")

def signup(username, password):
    if find_user_by_username(username):
        return {"success": False, "msg": "User already exists"}

    hashed_pw = generate_password_hash(password)
    create_user({"username": username, "password": hashed_pw})

    return {"success": True, "msg": "Signup successful"}

def login(username, password):
    user = find_user_by_username(username)

    if not user or not check_password_hash(user["password"], password):
        return {"success": False, "msg": "Invalid credentials"}

    token = jwt.encode({
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }, SECRET_KEY, algorithm="HS256")

    return {"success": True, "token": token}