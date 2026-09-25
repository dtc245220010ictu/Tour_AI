"""
Google Gemini AI Service.
Handles API requests to Gemini with timeouts, error handling, and rule-based fallback.
Strict isolation: Does NOT touch database.
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

class GeminiService:
    @staticmethod
    def get_api_key():
        return os.environ.get("GEMINI_API_KEY", "").strip()

    @staticmethod
    def is_configured():
        key = GeminiService.get_api_key()
        if not key:
            return False
        # Reject placeholder values from .env.example (e.g. "your_google_gemini_api_key_here")
        # so the app never calls the API with a fake key.
        return not key.lower().startswith("your_")

    @staticmethod
    def generate_content(prompt: str, temperature: float = 0.4, fallback_answer: str | None = None) -> str:
        """
        Sends prompt to Gemini API.
        If API key is missing or request fails, falls back gracefully to the
        precomputed `fallback_answer` (a data-grounded answer built by
        GroundedAnswerBuilder), or to the canned rule-based text when no
        fallback_answer was provided (e.g. staff AI content tools).
        """
        api_key = GeminiService.get_api_key()
        
        if not GeminiService.is_configured():
            logger.info("GEMINI_API_KEY not configured. Using grounded fallback answer.")
            return fallback_answer or GeminiService._generate_fallback(prompt)

        # Gemini REST API endpoint
        model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                # Thinking models spend tokens on internal reasoning first
                # (e.g. thoughtsTokenCount ~100+), so keep enough budget that
                # long multi-tour answers are never truncated mid-sentence.
                "maxOutputTokens": 4096,
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=12.0)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
            
            logger.warning(f"Gemini API returned status {response.status_code}: {response.text[:200]}")
            return fallback_answer or GeminiService._generate_fallback(prompt)

        except Exception as e:
            logger.error(f"Error connecting to Gemini API: {str(e)}")
            return fallback_answer or GeminiService._generate_fallback(prompt)

    @staticmethod
    def _generate_fallback(prompt: str) -> str:
        """
        Smart fallback response generator when Gemini API is offline or unconfigured.
        Synthesizes a helpful, grammatically correct Vietnamese response grounded in the prompt context.
        """
        if "[KHÔNG TÌM THẤY TOUR THỎA MÃN TIÊU CHÍ TRONG CƠ SỞ DỮ LIỆU]" in prompt:
            return (
                "Chào bạn! Rất tiếc hiện tại TourAI chưa có tour nào đáp ứng hoàn toàn chính xác "
                "mức giá hoặc tiêu chí bạn đang tìm kiếm. Bạn có thể tham khảo các tour tương tự trên website "
                "hoặc liên hệ hotline 1900-6868 để nhân viên tư vấn gói tour tùy chỉnh nhé!"
            )

        if "=== KHÔNG CÓ TOUR ĐÚNG TIÊU CHÍ, DƯỚI ĐÂY LÀ CÁC TOUR GẦN NHẤT" in prompt:
            return (
                "Chào bạn! Rất tiếc hiện tại hệ thống **chưa có tour nào đáp ứng đúng hoàn toàn** "
                "ngân sách hoặc tiêu chí bạn yêu cầu.\n\n"
                "Để bạn không lỡ chuyến đi, dưới đây TourAI xin **giới thiệu các tour khác** đang mở bán "
                "và còn chỗ với mức giá hấp dẫn nhất — bạn hãy tham khảo và chọn tour phù hợp nhé! "
                "Nếu cần tùy chỉnh lịch trình theo ngân sách của mình, hãy liên hệ hotline 1900-6868 "
                "để được tư vấn riêng ạ!"
            )

        # Extract tour info if available
        return (
            "Chào bạn! Dựa trên yêu cầu của bạn, TourAI đã tìm thấy các chuyến du lịch phù hợp nhất "
            "đang mở bán và còn chỗ trong hệ thống:\n\n"
            "Các tour trên đều có lịch trình chi tiết và được tổ chức trọn gói với dịch vụ chất lượng cao. "
            "Bạn có thể xem thông tin chi tiết từng chuyến đi ở các thẻ tour bên dưới và chọn ngày khởi hành "
            "phù hợp để đặt chỗ trực tiếp nhé! Chúc bạn có một chuyến đi thật tuyệt vời!"
        )

