"""
Unit tests for Context Builder.
Verifies compact formatting and factual consistency.
"""

from services.context_builder import ContextBuilder

def test_build_context_with_tours():
    tours = [
        {
            "id": 1,
            "title": "Hạ Long 2N1Đ",
            "destination_name": "Hạ Long",
            "destination_region": "Miền Bắc",
            "base_price": 3200000,
            "duration_days": 2,
            "duration_nights": 1,
            "transportation": "Du thuyền",
            "next_departure": "2026-10-15",
            "total_available_seats": 15,
            "description": "Nghỉ đêm du thuyền cao cấp."
        }
    ]
    context = ContextBuilder.build_context(tours)

    assert "Hạ Long 2N1Đ" in context
    assert "3.200.000 VNĐ" in context
    assert "15 chỗ" in context

def test_build_context_empty():
    context = ContextBuilder.build_context([])
    assert "[KHÔNG TÌM THẤY TOUR THỎA MÃN TIÊU CHÍ TRONG CƠ SỞ DỮ LIỆU]" in context

