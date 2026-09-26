"""
RAG Orchestration Service for TourAI.
Integrates Question Analyzer, Tour Retriever, Context Builder, Prompt Builder,
and Gemini Service into a seamless, hallucination-free pipeline.

Requests asking to summarize CUSTOMER FEEDBACK are routed to a dedicated
branch (ADMIN only) so the assistant answers with a real feedback report
instead of tour consultation text.
"""

import json
from services.question_analyzer import QuestionAnalyzer
from services.tour_retriever import TourRetriever
from services.context_builder import ContextBuilder
from services.prompt_builder import PromptBuilder
from services.gemini_service import GeminiService
from services.grounded_answer_builder import GroundedAnswerBuilder
from services.feedback_service import FeedbackService
from services.ai_content_service import AIContentService
from database.db import execute_query

class RAGService:
    @staticmethod
    def answer_question(question: str, session_id: str = "guest", role: str | None = None) -> dict:
        """
        Executes the full RAG pipeline:
        question -> analyze -> retrieve -> context -> prompt -> gemini -> answer + cards

        `role` is the logged-in user role (None for guests) and is used to gate
        the feedback-summary branch to ADMIN accounts.
        """
        if not question or not question.strip():
            return {
                "answer": "Vui lòng nhập câu hỏi của bạn để TourAI tư vấn nhé!",
                "tours": [],
                "intent": {}
            }

        clean_q = question.strip()

        # Step 1: Question Analysis
        intent = QuestionAnalyzer.analyze_question(clean_q)

        # Step 1b: Feedback-summary intent ("Tóm tắt phản hồi khách hàng", ...)
        if QuestionAnalyzer.is_feedback_summary_question(clean_q):
            return RAGService._answer_feedback_summary(clean_q, session_id, role)

        # Step 2: Tour Retrieval
        tours = TourRetriever.retrieve_tours(intent)
        alternatives = []
        if not tours:
            alternatives = TourRetriever.retrieve_alternative_tours(intent)

        # Step 3: Context Building
        context = ContextBuilder.build_context(tours, alternatives)

        # Step 4: Prompt Construction
        prompt = PromptBuilder.build_prompt(clean_q, context)

        # Step 4b: Precompute a Gemini-style answer grounded STRICTLY in retrieved data.
        # Used whenever the Gemini API is unavailable (no key / network error),
        # so the chat stays helpful without ever inventing information.
        grounded_answer = GroundedAnswerBuilder.build(clean_q, intent, tours, alternatives)

        # Step 5: Gemini AI Generation (falls back to the grounded answer above)
        answer = GeminiService.generate_content(prompt, fallback_answer=grounded_answer)

        # Step 6: Log chat interaction for analytics and auditing
        tour_ids_str = ",".join([str(t["id"]) for t in (tours or alternatives)])
        RAGService._log_interaction(session_id, clean_q, intent, tour_ids_str, answer)

        displayed_tours = tours if tours else alternatives
        return {
            "answer": answer,
            "tours": displayed_tours,
            "intent": intent
        }

    @staticmethod
    def _log_interaction(session_id: str, user_message: str, intent: dict, tour_ids: str, bot_response: str):
        """Stores one chat turn in `chat_logs` for analytics/auditing (never blocks)."""
        try:
            execute_query(
                """INSERT INTO chat_logs 
                (session_id, user_message, intent_json, retrieved_tour_ids, bot_response)
                VALUES (?, ?, ?, ?, ?);""",
                (session_id, user_message, json.dumps(intent or {}, ensure_ascii=False), tour_ids, bot_response),
                commit=True
            )
        except Exception:
            pass # Non-blocking logging

    @staticmethod
    def _answer_feedback_summary(question: str, session_id: str, role: str | None) -> dict:
        """
        Answers a request to summarize CUSTOMER FEEDBACK.

        Viewing/summarizing all customer feedbacks is an ADMIN-only capability
        (same rule as /admin/feedbacks and /api/ai/summarize-feedbacks), so other
        users receive a polite notice instead of the report - and never a
        misleading tour-consultation answer.
        """
        is_admin = (role or "").upper() == "ADMIN"
        intent = {
            "intent_type": "feedback_summary",
            "authorized": is_admin,
            "raw_question": question,
        }

        if not is_admin:
            answer = (
                "🔒 Tổng hợp phản hồi khách hàng là chức năng dành cho tài khoản "
                "**Quản trị viên (ADMIN)**. Với vai trò hiện tại, tôi chỉ có thể tư vấn tour du lịch — "
                "bạn thử hỏi tôi về điểm đến, ngân sách hoặc số ngày dự kiến nhé!"
            )
            RAGService._log_interaction(session_id, question, intent, "", answer)
            return {"answer": answer, "tours": [], "intent": intent}

        feedbacks = FeedbackService.get_all_feedbacks(limit=50)
        if not feedbacks:
            answer = (
                "📭 Hiện chưa có phản hồi nào từ khách hàng để phân tích. "
                "Khi khách hàng gửi đánh giá sau chuyến đi, tôi sẽ tổng hợp báo cáo "
                "chất lượng dịch vụ ngay giúp bạn!"
            )
        else:
            ratings = [int(f.get("rating", 5) or 5) for f in feedbacks]
            avg_rating = sum(ratings) / len(ratings)
            summary = AIContentService.summarize_feedbacks(feedbacks)
            answer = (
                f"📊 **Báo cáo tổng hợp phản hồi khách hàng** — {len(feedbacks)} phản hồi, "
                f"điểm trung bình {avg_rating:.1f}/5 ⭐\n\n{summary}"
            )

        RAGService._log_interaction(session_id, question, intent, "", answer)
        return {"answer": answer, "tours": [], "intent": intent}

