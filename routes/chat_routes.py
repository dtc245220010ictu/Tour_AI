"""
AI Chatbot and RAG Consultation API Routes.
Exposes POST /api/chat for frontend chat interface.
"""

from flask import Blueprint, render_template, request, jsonify, session
from services.rag_service import RAGService

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat")
def chatbot_page():
    return render_template("chatbot.html")

@chat_bp.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Định dạng dữ liệu không hợp lệ. Cần gửi JSON chứa trường 'question'."}), 400

    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Vui lòng nhập câu hỏi của bạn."}), 400

    session_id = session.get("session_id", request.remote_addr or "guest")

    try:
        # `role` lets the RAG pipeline gate admin-only intents such as
        # "Tóm tắt phản hồi khách hàng".
        result = RAGService.answer_question(question, session_id=session_id, role=session.get("role"))
        return jsonify({
            "answer": result["answer"],
            "tours": result["tours"]
        }), 200
    except Exception:
        # Never leak exception stack trace or internal details to the client
        return jsonify({
            "error": "Hệ thống tư vấn hiện đang bận hoặc gặp sự cố xử lý. Vui lòng thử lại sau giây lát.",
            "answer": "Rất tiếc! Hệ thống đang gặp chút gián đoạn kết nối. Bạn vui lòng thử lại hoặc xem trực tiếp các tour tại danh mục nhé!",
            "tours": []
        }), 500

