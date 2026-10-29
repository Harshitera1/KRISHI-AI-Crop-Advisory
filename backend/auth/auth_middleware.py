from flask import request, jsonify, g
from auth.jwt_handler import verify_token
from functools import wraps

def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"success": False, "message": "Token missing"}), 401

        try:
            token = auth_header.split(" ")[1]
        except:
            return jsonify({"success": False, "message": "Invalid token format"}), 401

        decoded = verify_token(token)

        if not decoded:
            return jsonify({"success": False, "message": "Invalid or expired token"}), 401

        # store user info
        g.user = decoded["user_id"]

        return func(*args, **kwargs)

    return wrapper