from flask import Blueprint, request, jsonify
from controllers.user_controller import signup, login

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/signup", methods=["POST"])
def signup_route():
    data = request.get_json(silent=True) or {}
    return jsonify(signup(data.get("username"), data.get("password")))

@user_bp.route("/login", methods=["POST"])
def login_route():
    data = request.get_json(silent=True) or {}
    return jsonify(login(data.get("username"), data.get("password")))