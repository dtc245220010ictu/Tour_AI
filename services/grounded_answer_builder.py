"""
Grounded Answer Builder for TourAI Chat.
Composes natural, Gemini-style Vietnamese chat answers STRICTLY from the
structured rows already retrieved from the database and the parsed intent.

Guarantees (Zero Hallucination):
- Never invents a tour name, price, departure date or seat count: every fact
  printed comes from the passed `tours` / `alternatives` row dictionaries.
- Never fabricates numeric values: prices/dates are formatted exactly from
  stored numbers; criteria text is only built from non-null intent fields.
- Pure function: does NOT touch the database or any external API.

The output uses markdown-lite compatible with the chat UI formatter
(static/js/chat.js): **bold**, "- " bullets and newline line breaks.
"""

from services.context_builder import format_currency

HOTLINE = "1900-6868"


class GroundedAnswerBuilder:
    """Builds helpful, data-grounded chat answers (fallback for offline Gemini)."""

    @staticmethod
    def _describe_criteria(intent: dict) -> str:
        """Builds a human-readable criteria phrase from NON-NULL intent fields only."""
        parts = []

        destinations = intent.get("destinations") or []
        if destinations:
            if len(destinations) <= 4:
                parts.append("điểm đến " + ", ".join(destinations))
            else:
                shown = ", ".join(destinations[:3])
                remaining = len(destinations) - 3
                parts.append(f"điểm đến {shown} và {remaining} điểm đến khác")

        min_price = intent.get("min_price")
        max_price = intent.get("max_price")
        if min_price and max_price:
            parts.append(f"giá từ {format_currency(min_price)} đến {format_currency(max_price)}")
        elif max_price:
            parts.append(f"ngân sách tối đa {format_currency(max_price)}")
        elif min_price:
            parts.append(f"giá từ {format_currency(min_price)}")

        duration = intent.get("duration_days")
        if isinstance(duration, (list, tuple)) and len(duration) >= 2:
            bounds = sorted(int(d) for d in duration)
            parts.append(f"thời lượng {bounds[0]}-{bounds[-1]} ngày")
        elif duration:
            parts.append(f"thời lượng {int(duration)} ngày")

        keywords = intent.get("keywords") or []
        if keywords:
            parts.append("sở thích " + ", ".join(keywords))

        if not parts:
            return ""
        return ", ".join(parts)

    @staticmethod
    def _format_tour(index: int, tour: dict) -> str:
        """Formats one retrieved tour row into two readable lines."""
        title = tour.get("title") or "Tour du lịch"
        price = format_currency(tour.get("base_price", 0))
        days = tour.get("duration_days", "?")
        nights = tour.get("duration_nights", 0)
        destination = tour.get("destination_name") or ""
        region = tour.get("destination_region")
        place = f"{destination} ({region})" if destination and region else destination
        departure = tour.get("next_departure") or "đang cập nhật"
        seats = tour.get("total_available_seats") or 0

        lines = [f"- **{index}. {title}** — {price}/khách ({days} ngày {nights} đêm)"]
        detail = f"📍 {place}" if place else "📍 Việt Nam"
        detail += f" • 📅 Khởi hành: {departure} • Còn {seats} chỗ"
        lines.append(f"  {detail}")
        return "\n".join(lines)

    @staticmethod
    def _render_tours(tours: list) -> str:
        return "\n".join(
            GroundedAnswerBuilder._format_tour(idx, tour)
            for idx, tour in enumerate(tours, 1)
        )

    @staticmethod
    def _cheapest_note(tours: list, intent: dict) -> str:
        """Data-derived price insight: cheapest row + the requested budget."""
        if not tours:
            return ""
        cheapest = min(tours, key=lambda t: t.get("base_price") or 0)
        title = cheapest.get("title") or "Tour"
        price = format_currency(cheapest.get("base_price", 0))
        max_price = intent.get("max_price")
        if max_price:
            return (
                f"\n💡 Theo ngân sách {format_currency(max_price)} của bạn, "
                f"**{title}** có giá thấp nhất trong danh sách: {price}."
            )
        return f"\n💡 Gợi ý hấp dẫn nhất trong danh sách: **{title}** chỉ {price}/khách."

    @staticmethod
    def build(question: str, intent: dict | None = None,
              tours: list | None = None, alternatives: list | None = None) -> str:
        """
        Composes the final chat answer:
        - matching tours found    -> introduce them with concrete details.
        - no match, alternatives  -> honestly report, then introduce alternatives.
        - nothing at all          -> polite refusal + hotline (no invented data).
        """
        intent = intent or {}
        tours = tours or []
        alternatives = alternatives or []
        criteria = GroundedAnswerBuilder._describe_criteria(intent)
        criteria = criteria or f'yêu cầu "{question.strip()}"'

        # Case 1: exact matches found -> showcase them like a Gemini consultant.
        if tours:
            lines = [
                f"Chào bạn! Với **{criteria}**, hệ thống tìm thấy "
                f"**{len(tours)} tour đang mở bán và còn chỗ** phù hợp với bạn:",
                "",
                GroundedAnswerBuilder._render_tours(tours),
                GroundedAnswerBuilder._cheapest_note(tours, intent),
                "",
                f"💡 Bạn bấm **Xem chi tiết & Đặt** trên thẻ tour bên dưới để xem lịch trình "
                f"đầy đủ và chọn ngày khởi hành nhé. Nếu cần hỗ trợ, hãy liên hệ hotline "
                f"**{HOTLINE}** — chúc bạn có một chuyến đi thật tuyệt vời! 🌟",
            ]
            return "\n".join(lines)

        # Case 2: no exact match but alternatives exist -> report + introduce them.
        if alternatives:
            lines = [
                f"Chào bạn! Rất tiếc, hiện tại hệ thống **chưa có tour nào đáp ứng đúng** "
                f"{criteria}.",
                "",
                f"Để bạn không bỏ lỡ chuyến đi, dưới đây là **{len(alternatives)} tour khác** "
                f"đang mở bán và còn chỗ để bạn tham khảo:",
                "",
                GroundedAnswerBuilder._render_tours(alternatives),
                "",
                f"💡 Bạn có thể điều chỉnh tiêu chí (ngân sách, số ngày hoặc điểm đến) để "
                f"mở rộng lựa chọn, hoặc liên hệ hotline **{HOTLINE}** để được tư vấn riêng nhé!",
            ]
            return "\n".join(lines)

        # Case 3: database truly has nothing to offer -> honest refusal, no invention.
        return (
            f"Chào bạn! Rất tiếc, hiện tại hệ thống **chưa có tour nào khớp** với "
            f"{criteria} và cũng chưa có tour thay thế phù hợp để giới thiệu. 😥\n\n"
            f"Bạn thử đổi tiêu chí (điểm đến, ngân sách, số ngày) hoặc liên hệ hotline "
            f"**{HOTLINE}** để nhân viên tư vấn trực tiếp nhé! Ngoài ra bạn có thể xem "
            f"toàn bộ danh mục tour trên website. 🙏"
        )


