from auth.auth_service import login_user, signup_user
from auth.jwt_handler import generate_token

def signup(username, password):
    return signup_user(username, password)

def login(username, password):
    result = login_user(username, password)
    if not result["success"]:
        return result
    return {"success": True, "message": "Login successful", "token": generate_token(username)}