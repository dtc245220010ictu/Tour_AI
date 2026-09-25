"""
Unit tests for GroundedAnswerBuilder.
Verifies chat answers are rich and natural (Gemini-style) yet strictly
grounded in retrieved database rows - zero hallucination.
"""

from services.grounded_answer_builder import GroundedAnswerBuilder

TOUR = {
    "id": 1,
    "title": "Hạ Long - Du Thuyền 5 Sao Sang Trọng",
    "slug": "ha-long-du-thuyen-5-sao",
    "base_price": 3_200_000,
    "duration_days": 2,
    "duration_nights": 1,
    "destination_name": "Hạ Long",
    "destination_region": "Miền Bắc",
    "transportation": "Xe Limousine & Du thuyền 5 sao",
    "next_departure": "2026-10-15",
    "total_available_seats": 15,
}


def test_build_with_matches_quotes_real_tour_data():
    intent = {
        "destinations": ["Hạ Long"],
        "min_price": None,
        "max_price": 4_000_000,
        "duration_days": None,
        "keywords": [],
        "sort_by": None,
    }
    answer = GroundedAnswerBuilder.build(
        "Có tour Hạ Long nào dưới 4 triệu không?", intent, [TOUR], []
    )

    assert "Chào bạn" in answer
    assert TOUR["title"] in answer
    assert "3.200.000" in answer          # real formatted price
    assert "2026-10-15" in answer         # real departure date
    assert "Còn 15 chỗ" in answer         # real seat count
    assert "2 ngày 1 đêm" in answer       # real duration


def test_build_does_not_invent_unrelated_tours_or_prices():
    intent = {
        "destinations": ["Hạ Long"],
        "min_price": None,
        "max_price": None,
        "duration_days": None,
        "keywords": [],
        "sort_by": None,
    }
    answer = GroundedAnswerBuilder.build("Tour Hạ Long", intent, [TOUR], [])

    assert "Sa Pa" not in answer
    assert "Đà Lạt" not in answer
    assert "4.500.000" not in answer       # price that is not in the data


def test_build_no_match_reports_then_introduces_alternatives():
    intent = {
        "destinations": ["Hà Nội"],
        "min_price": None,
        "max_price": None,
        "duration_days": None,
        "keywords": [],
        "sort_by": None,
    }
    answer = GroundedAnswerBuilder.build("Có tour Hà Nội không?", intent, [], [TOUR])

    assert "chưa có tour nào đáp ứng đúng" in answer   # (1) reports honestly
    assert TOUR["title"] in answer                      # (2) introduces other tours
    assert "1900-6868" in answer


def test_build_nothing_available_polite_refusal_with_hotline():
    answer = GroundedAnswerBuilder.build(
        "Có tour Đà Lạt nào không?", {"destinations": ["Đà Lạt"]}, [], []
    )

    assert "chưa có tour nào" in answer
    assert "1900-6868" in answer
    # Nothing to introduce -> must not fabricate any tour
    assert "- **1." not in answer
