"""
Context Builder for TourAI RAG Pipeline.
Compacts retrieved database records into structured, factual text for prompt grounding.
"""

def format_currency(val: float) -> str:
    """Định dạng tiền kiểu Việt Nam, giữ nguyên phần thập phân (không làm tròn)."""
    try:
        number = float(val)
        integer_part, _, decimal_part = f"{number:.2f}".partition(".")
        grouped = f"{int(integer_part):,}".replace(",", ".")
        decimal_part = decimal_part.rstrip("0")
        return grouped + ("," + decimal_part if decimal_part else "") + " VNĐ"
    except (ValueError, TypeError):
        return str(val)

class ContextBuilder:
    @staticmethod
    def build_context(tours: list, alternatives: list | None = None) -> str:
        """
        Builds a compact textual context grounded strictly in database records.
        """
        if not tours and not alternatives:
            return "[KHÔNG TÌM THẤY TOUR THỎA MÃN TIÊU CHÍ TRONG CƠ SỞ DỮ LIỆU]"

        lines = []

        if tours:
            lines.append("=== DANH SÁCH TOUR THỎA MÃN YÊU CẦU TRONG CƠ SỞ DỮ LIỆU ===")
            for idx, tour in enumerate(tours, 1):
                departure = tour.get("next_departure") or "Đang cập nhật"
                seats = tour.get("total_available_seats", 0)
                price_str = format_currency(tour.get("base_price", 0))
                duration_str = f"{tour.get('duration_days', 1)} ngày {tour.get('duration_nights', 0)} đêm"
                
                lines.append(f"{idx}. Tên tour: {tour.get('title')}")
                lines.append(f"   - Điểm đến: {tour.get('destination_name')} ({tour.get('destination_region')})")
                lines.append(f"   - Giá tiêu chuẩn: {price_str} / khách")
                lines.append(f"   - Thời lượng: {duration_str}")
                lines.append(f"   - Phương tiện: {tour.get('transportation', 'Xe du lịch')}")
                lines.append(f"   - Lịch khởi hành gần nhất: {departure} (Số chỗ còn lại: {seats} chỗ)")
                lines.append(f"   - Điểm nhấn: {tour.get('description')[:200]}...")
                lines.append("")

        if not tours and alternatives:
            lines.append("=== KHÔNG CÓ TOUR ĐÚNG TIÊU CHÍ, DƯỚI ĐÂY LÀ CÁC TOUR GẦN NHẤT CÓ TRONG HỆ THỐNG ===")
            for idx, tour in enumerate(alternatives, 1):
                price_str = format_currency(tour.get("base_price", 0))
                duration_str = f"{tour.get('duration_days', 1)} ngày {tour.get('duration_nights', 0)} đêm"
                departure = tour.get("next_departure") or "Đang cập nhật"
                seats = tour.get("total_available_seats", 0)
                
                lines.append(f"{idx}. Tên tour: {tour.get('title')}")
                lines.append(f"   - Điểm đến: {tour.get('destination_name')}")
                lines.append(f"   - Giá: {price_str} / khách")
                lines.append(f"   - Thời lượng: {duration_str}")
                lines.append(f"   - Khởi hành: {departure} (Còn {seats} chỗ)")
                lines.append("")

        return "\n".join(lines)

