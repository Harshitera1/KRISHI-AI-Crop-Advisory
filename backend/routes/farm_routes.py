from flask import Blueprint, g, jsonify, request

from auth.auth_middleware import token_required
from controllers.farm_controller import add_farm, list_farms

farm_bp = Blueprint("farm", __name__)


@farm_bp.route("/add", methods=["POST"])
@token_required
def add():
    data = request.get_json(silent=True) or {}
    data["username"] = g.get("user")
    return jsonify(add_farm(data))


@farm_bp.route("/list", methods=["GET"])
@token_required
def listing():
    return jsonify(list_farms(g.get("user")))
