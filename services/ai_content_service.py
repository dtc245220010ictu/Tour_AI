"""
AI Content Generation and Feedback Summarization Service.
Generates tour descriptions, daily itineraries, and summarizes customer reviews.
"""

from services.gemini_service import GeminiService

class AIContentService:
    @staticmethod
    def generate_tour_description(title: str, destination: str, highlights: str, duration_days: int) -> dict:
        """
        Generates marketing description and daily itinerary for a tour.
        """
        prompt = f"""Bạn là chuyên gia marketing du lịch hàng đầu.
Hãy viết nội dung giới thiệu tour du lịch và gợi ý lịch trình chi tiết theo từng ngày:
- Tên tour: {title}
- Điểm đến: {destination}
- Thời lượng: {duration_days} ngày
- Điểm nhấn / Hoạt động chính: {highlights}

YÊU CẦU:
1. Viết một đoạn văn mô tả tour (khoảng 100-150 từ) hấp dẫn, lôi cuốn, chuẩn SEO.
2. Gợi ý lịch trình chi tiết từ Ngày 1 đến Ngày {duration_days} với các mốc thời gian sáng, trưa, chiều, tối.
3. Sử dụng tiếng Việt chuẩn mực, giàu cảm xúc.

HÃY TRẢ VỀ THEO ĐỊNH DẠNG:
[MÔ TẢ TOUR]
(Đoạn văn mô tả)

[LỊCH TRÌNH CHI TIẾT]
(Chi tiết từng ngày)
"""
        response_text = GeminiService.generate_content(prompt, temperature=0.7)

        # Parse sections
        desc = ""
        itinerary = ""
        if "[MÔ TẢ TOUR]" in response_text and "[LỊCH TRÌNH CHI TIẾT]" in response_text:
            parts = response_text.split("[LỊCH TRÌNH CHI TIẾT]")
            desc = parts[0].replace("[MÔ TẢ TOUR]", "").strip()
            itinerary = parts[1].strip()
        else:
            desc = response_text[:300].strip()
            itinerary = response_text.strip()

        return {
            "description": desc,
            "itinerary": itinerary,
            "full_content": response_text
        }

    @staticmethod
    def summarize_feedbacks(feedbacks: list) -> str:
        """
        Summarizes multiple customer reviews into positive points and improvement areas.
        """
        if not feedbacks:
            return "Chưa có phản hồi nào từ khách hàng để phân tích."

        reviews_text = ""
        for i, f in enumerate(feedbacks, 1):
            reviews_text += f"{i}. Đánh giá: {f.get('rating', 5)} sao - Nhận xét: \"{f.get('comment', '')}\"\n"

        prompt = f"""Bạn là Chuyên gia Quản lý Chất lượng Dịch vụ Du lịch.
Dưới đây là danh sách các phản hồi và đánh giá thực tế của khách hàng sau khi đi tour:

{reviews_text}

HÃY PHÂN TÍCH VÀ TỔNG HỢP:
1. ĐIỂM KHEN NGỢI (Ưu điểm nổi bật được nhiều khách nhắc tới).
2. ĐIỂM CẦN CẢI THIỆN (Các phàn nàn, góp ý hoặc hạn chế cần khắc phục).
3. ĐỀ XUẤT HÀNH ĐỘNG CỤ THỂ cho ban quản lý tour.

Viết ngắn gọn, súc tích bằng tiếng Việt theo các tiêu đề rõ ràng."""
        
        return GeminiService.generate_content(prompt, temperature=0.3)

