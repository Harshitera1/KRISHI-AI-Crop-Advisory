from flask import Blueprint, jsonify
from controllers.fertilizer_controller import get_fertilizer

fertilizer_bp = Blueprint("fertilizer", __name__)

@fertilizer_bp.route("/<crop>", methods=["GET"])
def fertilizer(crop):
    result = get_fertilizer(crop)
    return jsonify(result)