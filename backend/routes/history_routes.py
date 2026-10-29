from flask import Blueprint, jsonify, g
from auth.auth_middleware import token_required
from database.mongo import history_collection

history_bp = Blueprint("history", __name__)

@history_bp.route("/", methods=["GET"])
@token_required
def get_history():
    try:
        user = g.get("user")

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found in token"
            }), 401

        if history_collection is None:
            return jsonify({
                "success": False,
                "message": "Database not connected"
            }), 500

        records = list(history_collection.find(
            {"user": user},
            {"_id": 0}
        ))

        return jsonify({
            "success": True,
            "history": records
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500