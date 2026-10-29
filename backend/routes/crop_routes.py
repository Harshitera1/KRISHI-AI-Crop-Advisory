from flask import Blueprint, request, jsonify, send_file
from services.agentic_service import answer_farmer_question, export_advisory_pdf, run_advisory_pipeline
from auth.auth_middleware import token_required


crop_bp = Blueprint("crop", __name__)

@crop_bp.route("/recommend", methods=["POST"])
@token_required   # 🔥 ADD THIS
def recommend():
    data = request.get_json(silent=True) or {}
    result = run_advisory_pipeline(data)
    return jsonify(result)


@crop_bp.route("/advisory", methods=["POST"])
@token_required
def advisory():
    data = request.get_json(silent=True) or {}
    result = run_advisory_pipeline(data)
    return jsonify(result)


@crop_bp.route("/ask", methods=["POST"])
@token_required
def ask():
    data = request.get_json(silent=True) or {}
    result = answer_farmer_question(
        data.get("question", ""),
        language=data.get("language") or "en",
        context=data.get("context") or {},
    )
    status = 200 if result.get("success") else 400
    return jsonify(result), status


@crop_bp.route("/advisory/pdf", methods=["POST"])
@token_required
def advisory_pdf():
    data = request.get_json(silent=True) or {}
    # Reuse the advisory already shown on screen when the client sends it back.
    if data.get("advisory_text") and data.get("recommended_crop"):
        result = data
    else:
        result = run_advisory_pipeline(data)
        if not result.get("success"):
            return jsonify(result), 400

    pdf_path = export_advisory_pdf(result.get("advisory_text", ""), result)
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="krishi_advisory.pdf",
        mimetype="application/pdf",
    )