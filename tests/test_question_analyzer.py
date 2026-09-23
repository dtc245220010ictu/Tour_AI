"""
Unit tests for Question Analyzer service.
Verifies parsing of Vietnamese travel queries, budget normalization, and destination extraction.
"""

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

