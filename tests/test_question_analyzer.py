"""
Unit tests for Question Analyzer service.
Verifies parsing of Vietnamese travel queries, budget normalization, destination extraction,
and detection of customer-feedback-summary requests.
"""

import pytest

from services.question_analyzer import QuestionAnalyzer

def test_analyze_ha_long_under_4_million():
    query = "Có tour Hạ Long nào dưới 4 triệu không?"
    intent = QuestionAnalyzer.analyze_question(query)

    assert "Hạ Long" in intent["destinations"]
    assert intent["max_price"] == 4_000_000
    assert intent["min_price"] is None

def test_analyze_da_nang_3_days_under_5_tr():
    query = "Tôi muốn đi Đà Nẵng 3 ngày dưới 5tr"
    intent = QuestionAnalyzer.analyze_question(query)

    assert "Đà Nẵng" in intent["destinations"]
    assert intent["duration_days"] == 3
    assert intent["max_price"] == 5_000_000

def test_analyze_beach_preference():
    query = "Tư vấn cho tôi tour đi biển tầm 3 đến 5 triệu"
    intent = QuestionAnalyzer.analyze_question(query)

    assert "biển" in intent["keywords"]
    assert intent["min_price"] == 3_000_000
    assert intent["max_price"] == 5_000_000
    # Should automatically suggest coastal destinations
    assert any(d in intent["destinations"] for d in ["Hạ Long", "Đà Nẵng", "Phú Quốc"])

def test_analyze_cheapest_sorting():
    query = "Tour nào có giá rẻ nhất hiện tại?"
    intent = QuestionAnalyzer.analyze_question(query)

    assert intent["sort_by"] == "price_asc"

def test_analyze_empty_or_whitespace():
    intent = QuestionAnalyzer.analyze_question("   ")
    assert intent["destinations"] == []
    assert intent["max_price"] is None


def test_analyze_khoang_5_trieu_no_false_da_lat_mapping():
    """REGRESSION: accent-stripped "khoảng" -> "khoang" contains "hoa".

    Whole-word matching must prevent keyword "hoa" from firing here, otherwise the
    query is wrongly mapped to Đà Lạt (no tours in DB) and the chatbot reports
    that no tour exists for a perfectly valid 5-million budget question.
    """
    intent = QuestionAnalyzer.analyze_question("Có tour nào khoảng 5 triệu không?")

    assert intent["max_price"] == 5_000_000
    assert intent["destinations"] == []
    assert "hoa" not in intent["keywords"]


def test_analyze_bare_budget_phrases():
    """Budget without an explicit prefix ("dưới/tối đa") must still be extracted."""
    for query in [
        "tour 5 triệu",
        "Tư vấn cho tôi tour giá 5 triệu",
        "Tôi có 5 triệu muốn đi du lịch",
        "tour 5tr",
    ]:
        intent = QuestionAnalyzer.analyze_question(query)
        assert intent["max_price"] == 5_000_000, f"failed for: {query}"


def test_analyze_duration_range_3_to_4_days():
    """Quick-chip scenario: budget + day range must produce an inclusive range."""
    intent = QuestionAnalyzer.analyze_question(
        "Tôi có khoảng 5 triệu, muốn đi biển 3-4 ngày thì có tour nào?"
    )

    assert intent["duration_days"] == [3, 4]
    assert intent["max_price"] == 5_000_000
    assert "biển" in intent["keywords"]
    assert "hoa" not in intent["keywords"]


def test_analyze_duration_single_day_stays_integer():
    intent = QuestionAnalyzer.analyze_question("Tôi muốn đi Đà Nẵng 3 ngày dưới 5tr")
    assert intent["duration_days"] == 3


@pytest.mark.parametrize("question", [
    "Tóm tắt phản hồi khách hàng",
    "Phân tích đánh giá của khách hàng giúp tôi",
    "Tổng hợp nhận xét khách hàng sau các chuyến đi",
    "Thống kê review feedback của du khách",
])
def test_feedback_summary_question_detected(question):
    """The chat assistant must recognize feedback-summary requests."""
    assert QuestionAnalyzer.is_feedback_summary_question(question) is True


@pytest.mark.parametrize("question", [
    "Có tour Hạ Long nào dưới 4 triệu không?",
    "Tư vấn giúp tôi tour Đà Nẵng 3 ngày",
    "Tóm tắt giúp tôi tour Sa Pa 2 ngày",
    "Tour nào khách hàng đánh giá cao nhất?",
])
def test_normal_tour_question_not_treated_as_feedback_summary(question):
    """Regular tour-consultation questions must NOT trigger the feedback branch."""
    assert QuestionAnalyzer.is_feedback_summary_question(question) is False

