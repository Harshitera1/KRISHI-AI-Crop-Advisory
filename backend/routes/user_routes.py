from flask import Blueprint, request, jsonify
from controllers.user_controller import signup, login

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/signup", methods=["POST"])
def signup_route():
    data = request.json
    return jsonify(signup(data["username"], data["password"]))

@user_bp.route("/login", methods=["POST"])
def login_route():
    data = request.json
    return jsonify(login(data["username"], data["password"]))