from flask import Blueprint, request, jsonify
from auth.auth_controller import signup, login

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup_route():
    data = request.get_json(silent=True) or {}
    result = signup(data)
    return jsonify(result)


@auth_bp.route("/login", methods=["POST"])
def login_route():
    data = request.get_json(silent=True) or {}
    result = login(data)
    return jsonify(result)