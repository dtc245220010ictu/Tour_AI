"""
Internal AI Tools Routes for Staff/Admin.
Provides endpoints to generate tour marketing descriptions and summarize feedback.
"""

from flask import Blueprint, request, jsonify
from routes.auth_routes import roles_required
from services.ai_content_service import AIContentService
from services.feedback_service import FeedbackService

ai_tools_bp = Blueprint("ai_tools", __name__, url_prefix="/api/ai")

@ai_tools_bp.route("/generate-description", methods=["POST"])
@roles_required("ADMIN", "STAFF")
def generate_tour_description():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    destination = data.get("destination", "").strip()
    highlights = data.get("highlights", "").strip()
    duration_days = int(data.get("duration_days", 3))

    if not title:
        return jsonify({"error": "Vui lòng nhập tên tour."}), 400

    try:
        result = AIContentService.generate_tour_description(title, destination, highlights, duration_days)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Lỗi khi sinh nội dung: {str(e)}"}), 500

@ai_tools_bp.route("/summarize-feedbacks", methods=["POST"])
@roles_required("ADMIN", "STAFF")
def summarize_feedbacks():
    try:
        feedbacks = FeedbackService.get_all_feedbacks(limit=50)
        summary = AIContentService.summarize_feedbacks(feedbacks)
        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": f"Lỗi khi phân tích phản hồi: {str(e)}"}), 500

