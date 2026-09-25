"""
AI Content Generation and Feedback Summarization Service.
Generates tour descriptions, daily itineraries, and summarizes customer reviews.

Never returns the generic customer-chat fallback text: when Gemini is offline,
unconfigured, or answers in an unexpected format, a structured rule-based
content built from the actual tour inputs is used instead, so the staff form
always receives a real description plus a day-by-day itinerary.
"""

import re
import time

from services.gemini_service import GeminiService

# The Gemini endpoint occasionally returns transient errors (e.g. 503
# UNAVAILABLE under high demand), so retry a couple of times before falling
# back to the locally generated content.
_MAX_AI_ATTEMPTS = 3
_RETRY_DELAY_SECONDS = 0.5

# Markers may come back as plain "[MÔ TẢ TOUR]", markdown "**[MÔ TẢ TOUR]**"
# or a heading "## MÔ TẢ TOUR". Match them only at line start so words like
# "lịch trình" inside the description never trigger a false split.
_DESC_MARKER = re.compile(
    r"^[ \t]*(?:#{1,6}[ \t]*)?(?:\*{0,2}\[)?[ \t]*MÔ TẢ TOUR[ \t]*\]?(?:\*{0,2})?",
    re.IGNORECASE | re.MULTILINE,
)
_ITIN_MARKER = re.compile(
    r"^[ \t]*(?:#{1,6}[ \t]*)?(?:\*{0,2}\[)?[ \t]*LỊCH TRÌNH(?:[ \t]+CHI TIẾT)?[ \t]*\]?(?:\*{0,2})?",
    re.IGNORECASE | re.MULTILINE,
)
_DAY_ONE = re.compile(r"ngày[ \t]*1\b", re.IGNORECASE)
_DAY_HEADING = re.compile(r"^[ \t]*#{0,6}[ \t]*(?:\*{0,2})?Ngày[ \t]*(\d+)\b", re.IGNORECASE | re.MULTILINE)
_EDGE_JUNK = re.compile(r"^[\s\-*#:\[\]]+|[\s\-*#:\[\]]+$")


class AIContentService:
    @staticmethod
    def generate_tour_description(title: str, destination: str, highlights: str, duration_days: int) -> dict:
        """
        Generates marketing description and daily itinerary for a tour.

        Returns a dict with `description`, `itinerary`, `full_content` and
        `source` ("ai" when Gemini produced the content, "template" when the
        built-in structured template was used because AI was unavailable or
        returned unusable output).
        """
        try:
            duration_days = int(duration_days)
        except (TypeError, ValueError):
            duration_days = 3
        duration_days = max(1, min(duration_days, 30))

        highlights = (highlights or "").strip()
        prompt = f"""Bạn là chuyên gia marketing du lịch hàng đầu.
Hãy viết nội dung giới thiệu tour du lịch và gợi ý lịch trình chi tiết theo từng ngày:
- Tên tour: {title}
- Điểm đến: {destination}
- Thời lượng: {duration_days} ngày
- Điểm nhấn / Hoạt động chính: {highlights or "các điểm tham quan nổi bật, ẩm thực đặc sản, nghỉ dưỡng cao cấp"}

YÊU CẦU:
1. Viết một đoạn văn mô tả tour (khoảng 100-150 từ) hấp dẫn, lôi cuốn, chuẩn SEO.
2. Gợi ý lịch trình chi tiết từ Ngày 1 đến Ngày {duration_days}, mỗi ngày viết đủ các mốc thời gian Sáng, Trưa, Chiều, Tối.
3. Sử dụng tiếng Việt chuẩn mực, giàu cảm xúc, chỉ dựa trên thông tin được cung cấp.

HÃY TRẢ VỀ THEO ĐỊNH DẠNG CHÍNH XÁC, giữ nguyên hai dòng tiêu đề trong ngoặc vuông:
[MÔ TẢ TOUR]
(Đoạn văn mô tả)

[LỊCH TRÌNH CHI TIẾT]
Ngày 1: ...
...
Ngày {duration_days}: ...

LƯU Ý: KHÔNG viết thêm lời chào hay bất kỳ phần nào ngoài hai phần trên.
"""
        local_desc, local_itin = AIContentService._build_local_content(
            title, destination, highlights, duration_days
        )
        local_content = AIContentService._format_content(local_desc, local_itin)

        # Structured fallback passed to GeminiService so a failed API call
        # never falls through to the canned customer-chat answer.
        response_text = local_content
        source = "template"
        if GeminiService.is_configured():
            for attempt in range(_MAX_AI_ATTEMPTS):
                response_text = GeminiService.generate_content(
                    prompt, temperature=0.7, fallback_answer=local_content
                )
                # GeminiService returns `fallback_answer` unchanged when the
                # API call failed -> treat as a retryable miss.
                if response_text != local_content:
                    source = "ai"
                    break
                if attempt < _MAX_AI_ATTEMPTS - 1:
                    time.sleep(_RETRY_DELAY_SECONDS * (attempt + 1))

        parsed = AIContentService._parse_content(response_text, duration_days)
        if parsed is None:
            # AI answered in an unusable format (too short, missing days, or
            # the generic chat sentence) -> never ship it to the tour form.
            parsed = (local_desc, local_itin)
            response_text = local_content
            source = "template"

        desc, itinerary = parsed
        return {
            "description": desc,
            "itinerary": itinerary,
            "full_content": response_text,
            "source": source,
        }

    @staticmethod
    def _format_content(description: str, itinerary: str) -> str:
        return f"[MÔ TẢ TOUR]\n{description}\n\n[LỊCH TRÌNH CHI TIẾT]\n{itinerary}"

    @staticmethod
    def _parse_content(text: str, expected_days: int):
        """
        Splits an AI answer into (description, itinerary).
        Returns None when the text has no valid description + complete
        day-by-day plan for the requested duration.
        """
        if not text or not text.strip():
            return None

        day_split = re.search(
            r"^[ \t]*#{0,6}[ \t]*(?:\*{0,2})?Ngày 1\b.*$", text, re.MULTILINE
        )
        desc_match = _DESC_MARKER.search(text)
        if desc_match:
            itin_match = _ITIN_MARKER.search(text, desc_match.end())
            if itin_match:
                desc = text[desc_match.end():itin_match.start()].strip()
                itinerary = text[itin_match.end():].strip()
            elif day_split:
                desc = text[desc_match.end():day_split.start()].strip()
                itinerary = text[day_split.start():].strip()
            else:
                return None
        elif day_split:
            # Model ignored the [MÔ TẢ TOUR] marker entirely -> split at "Ngày 1".
            desc = text[:day_split.start()].strip()
            itinerary = text[day_split.start():].strip()
        else:
            return None

        desc = _EDGE_JUNK.sub("", desc).strip()
        itinerary = _EDGE_JUNK.sub("", itinerary).strip()

        # Validation: a usable answer has a real paragraph AND a complete
        # sequence from "Ngày 1" to the requested final day. Anything else
        # (e.g. a one-sentence canned reply or an API response cut off after
        # the first day) must be rejected in favour of the structured template.
        if len(desc) < 40 or not _DAY_ONE.search(itinerary) or len(itinerary) < 80:
            return None
        expected_days = max(1, int(expected_days))
        itinerary_days = {int(day) for day in _DAY_HEADING.findall(itinerary)}
        if not all(day in itinerary_days for day in range(1, expected_days + 1)):
            return None
        return desc, itinerary

    @staticmethod
    def _build_local_content(title: str, destination: str, highlights: str, duration_days: int) -> tuple:
        """
        Rule-based (description, itinerary) builder used whenever the AI is
        unavailable or its answer fails validation.
        """
        title = (title or "").strip() or "tour du lịch"
        destination = (destination or "").strip() or "điểm đến"
        highlights = (highlights or "").strip().rstrip(".") or (
            "các điểm tham quan nổi bật, ẩm thực đặc sản và trải nghiệm văn hoá địa phương"
        )
        days = max(1, int(duration_days))

        description = (
            f"Khám phá {title} — hành trình {days} ngày đến với {destination}, "
            f"chuyến đi được thiết kế dành cho những ai muốn tận hưởng trọn vẹn vẻ đẹp "
            f"và nhịp sống địa phương. Tour đưa bạn đến {highlights}, kết hợp nghỉ dưỡng "
            f"thư giãn, ẩm thực đặc sản và những trải nghiệm khó quên bên gia đình, "
            f"bạn bè. Với lịch trình cân đối, phương tiện di chuyển thoải mái cùng đội ngũ "
            f"hướng dẫn viên nhiệt tình và dịch vụ chu đáo, bạn hoàn toàn yên tâm tận hưởng "
            f"từng khoảnh khắc của chuyến đi. Hãy đồng hành cùng chúng tôi để biến {title} "
            f"thành hành trình đáng nhớ nhất trong năm nay!"
        )

        day_blocks = []
        for day in range(1, days + 1):
            if days == 1:
                heading = f"Ngày 1: TRẢI NGHIỆM {destination.upper()} TRONG 1 NGÀY"
                activities = [
                    f"- Sáng: Đón khách tại điểm hẹn, khởi hành đến {destination}, bắt đầu tham quan {highlights}.",
                    "- Trưa: Nghỉ ngơi và thưởng thức bữa trưa đặc sản địa phương tại nhà hàng.",
                    f"- Chiều: Tiếp tục hành trình tham quan, check-in chụp hình lưu niệm tại {destination}.",
                    "- Tối: Bữa tối ấm cúng, tiễn khách tại điểm hẹn, kết thúc tour 1 ngày. Hẹn gặp lại quý khách!",
                ]
            elif day == 1:
                heading = f"Ngày 1: KHỞI HÀNH - KHÁM PHÁ {destination.upper()}"
                activities = [
                    f"- Sáng: Đón khách tại điểm hẹn, khởi hành đi {destination}, trên đường dừng chân nghỉ ngơi.",
                    "- Trưa: Thưởng thức bữa trưa đặc sản địa phương, nhận phòng nghỉ dưỡng.",
                    f"- Chiều: Bắt đầu tham quan {highlights}, check-in và chụp hình lưu niệm.",
                    f"- Tối: Bữa tối tại nhà hàng, tự do khám phá ẩm thực đường phố về đêm, nghỉ đêm tại {destination}.",
                ]
            elif day == days:
                heading = f"Ngày {day}: TỔNG KẾT - TIỄN KHÁCH"
                activities = [
                    "- Sáng: Ăn sáng tại khách sạn, trả phòng và mua sắm đặc sản làm quà cho người thân.",
                    f"- Trưa: Dùng bữa trưa trọn vị, tổng kết hành trình {days} ngày tại {destination}.",
                    "- Chiều: Xe đưa tiễn khách tại điểm hẹn, kết thúc chuyến đi. Cảm ơn quý khách và hẹn gặp lại!",
                ]
            else:
                heading = f"Ngày {day}: TRẢI NGHIỆM SUỐT NGÀY TẠI {destination.upper()}"
                activities = [
                    "- Sáng: Ăn sáng buffet tại khách sạn, bắt đầu hành trình tham quan các điểm nổi bật.",
                    "- Trưa: Dùng bữa trưa tại nhà hàng địa phương, nghỉ ngơi thư giãn.",
                    f"- Chiều: Trải nghiệm {highlights} cùng hướng dẫn viên am hiểu.",
                    f"- Tối: Nghỉ đêm tại {destination}, tự do thư giãn hoặc khám phá dịch vụ nghỉ dưỡng.",
                ]
            day_blocks.append(heading + "\n" + "\n".join(activities))

        return description, "\n\n".join(day_blocks)

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

        local_summary = AIContentService._build_local_summary(feedbacks)
        if not GeminiService.is_configured():
            return local_summary

        for attempt in range(_MAX_AI_ATTEMPTS):
            result = GeminiService.generate_content(
                prompt, temperature=0.3, fallback_answer=local_summary
            )
            if result != local_summary:
                return result
            if attempt < _MAX_AI_ATTEMPTS - 1:
                time.sleep(_RETRY_DELAY_SECONDS * (attempt + 1))
        return local_summary

    @staticmethod
    def _build_local_summary(feedbacks: list) -> str:
        """Rating-based summary used when the AI summarizer is unavailable."""
        ratings = [int(f.get("rating", 5) or 5) for f in feedbacks]
        avg = sum(ratings) / len(ratings)
        positives = [f.get("comment", "").strip() for f in feedbacks if int(f.get("rating", 5) or 5) >= 4]
        concerns = [f.get("comment", "").strip() for f in feedbacks if int(f.get("rating", 5) or 5) <= 3]

        lines = [
            f"(Tổng hợp tự động từ {len(feedbacks)} phản hồi — điểm trung bình {avg:.1f}/5 sao)",
            "1. ĐIỂM KHEN NGỢI:",
        ]
        lines += [f"- {c}" for c in positives if c] or [
            "- Khách hàng hài lòng với chất lượng dịch vụ chung của tour."
        ]
        lines.append("2. ĐIỂM CẦN CẢI THIỆN:")
        lines += [f"- {c}" for c in concerns if c] or [
            "- Chưa có phàn nàn đáng kể; tiếp tục duy trì chất lượng hiện tại."
        ]
        lines.append("3. ĐỀ XUẤT HÀNH ĐỘNG:")
        lines.append(
            "- Tổng hợp thường xuyên, chấm điểm nhà cung cấp và đào tạo nhân sự "
            "theo các phản hồi còn lại."
        )
        return "\n".join(lines)

