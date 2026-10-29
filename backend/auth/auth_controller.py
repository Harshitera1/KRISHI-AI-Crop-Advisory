from auth.auth_service import signup_user, login_user
from auth.jwt_handler import generate_token

def signup(data):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {
            "success": False,
            "message": "Username and password required"
        }

    return signup_user(username, password)


def login(data):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {
            "success": False,
            "message": "Username and password required"
        }

    result = login_user(username, password)

    if not result["success"]:
        return result

    # 🔥 generate JWT token
    token = generate_token(username)

    return {
        "success": True,
        "message": "Login successful",
        "token": token
    }