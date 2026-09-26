"""
Integration and End-to-End tests for RAG AI Pipeline and Chat API.
Verifies POST /api/chat endpoint, request validation, zero-hallucination constraints,
and rich tour cards response.
"""

from services.rag_service import RAGService
import pytest

def test_rag_service_ha_long_query():
    query = "Có tour Hạ Long nào dưới 4 triệu không?"
    result = RAGService.answer_question(query)

    assert result is not None
    assert "answer" in result
    assert len(result["answer"]) > 20
    assert len(result["tours"]) >= 1
    assert result["tours"][0]["destination_name"] == "Hạ Long"

def test_api_chat_success(client):
    response = client.post(
        "/api/chat",
        json={"question": "Có tour nào đi biển dưới 5 triệu không?"}
    )
    assert response.status_code == 200
    data = response.get_json()

    assert "answer" in data
    assert "tours" in data
    assert isinstance(data["tours"], list)
    assert len(data["tours"]) > 0

def test_api_chat_empty_question_returns_400(client):
    response = client.post(
        "/api/chat",
        json={"question": "   "}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


@pytest.mark.parametrize("question", [
    "Tư vấn cho tôi đi du lịch",
    "Có tour gì hay không?",
])
def test_api_chat_vague_request_returns_only_real_available_tours(client, question):
    """Vague requests may receive general suggestions, but never fabricated/full tours."""
    response = client.post("/api/chat", json={"question": question})
    assert response.status_code == 200
    data = response.get_json()

    assert data["answer"]
    assert 1 <= len(data["tours"]) <= 4
    assert all(tour["total_available_seats"] > 0 for tour in data["tours"])


def test_api_chat_vague_budget_request_respects_max_price(client):
    """A short, underspecified budget question still constrains real suggestions."""
    response = client.post("/api/chat", json={"question": "Tầm 5 triệu thì đi đâu?"})
    assert response.status_code == 200
    data = response.get_json()

    assert len(data["tours"]) > 0
    assert all(tour["base_price"] <= 5_000_000 for tour in data["tours"])

def test_api_chat_zero_hallucination_impossible_price(client):
    """
    CRITICAL ZERO-HALLUCINATION TEST:
    Asking for a tour to Đà Lạt under 100,000 VND (which does not exist).
    The response must politely state that no such tour exists,
    instead of hallucinating a fake 100k tour!
    """
    response = client.post(
        "/api/chat",
        json={"question": "Có tour Đà Lạt nào dưới 100 nghìn không?"}
    )
    assert response.status_code == 200
    data = response.get_json()

    answer = data["answer"].lower()
    # Must communicate that no exact matching tour was found
    assert any(phrase in answer for phrase in ["chưa có", "không tìm thấy", "chưa tìm thấy", "không có", "chưa có tour"])

def test_api_chat_budget_5_trieu_returns_tours(client):
    """REGRESSION: asking for a ~5 million VND tour must return matching tours.

    Previously the accent-stripped keyword "hoa" fired inside "khoang" (khoảng),
    mapping the query to Đà Lạt and making the chatbot answer 'no tours found'.
    """
    response = client.post(
        "/api/chat",
        json={"question": "Có tour nào khoảng 5 triệu không?"}
    )
    assert response.status_code == 200
    data = response.get_json()

    assert len(data["tours"]) > 0
    for tour in data["tours"]:
        assert tour["base_price"] <= 5_000_000

def test_api_chat_beach_range_budget_returns_tours(client):
    """REGRESSION for the quick-chip prompt: budget + 3-4 day range must find tours."""
    response = client.post(
        "/api/chat",
        json={"question": "Tôi có khoảng 5 triệu, muốn đi biển 3-4 ngày thì có tour nào?"}
    )
    assert response.status_code == 200
    data = response.get_json()

    assert len(data["tours"]) > 0
    assert all(tour["duration_days"] in (3, 4) for tour in data["tours"])

def test_api_chat_no_match_reports_and_suggests_other_tours(client):
    """When no tour meets the requirement the chatbot must BOTH
    (1) honestly report that no matching tour exists, and
    (2) introduce other available tours instead of leaving the customer empty-handed.
    """
    # Nha Trang does not exist in the test database -> zero exact matches
    response = client.post(
        "/api/chat",
        json={"question": "Có tour Nha Trang nào không?"}
    )
    assert response.status_code == 200
    data = response.get_json()

    answer = data["answer"].lower()
    # (1) reports no matching tour
    assert any(phrase in answer for phrase in ["chưa có", "không tìm thấy", "chưa tìm thấy", "không có"])
    # (2) suggests other tours
    assert len(data["tours"]) > 0

def test_api_chat_impossible_price_still_suggests_tours(client):
    """Zero-hallucination + alternatives: impossible budget -> no fake tour,
    but the response still introduces real tours."""
    response = client.post(
        "/api/chat",
        json={"question": "Có tour Hạ Long nào dưới 100 nghìn không?"}
    )
    assert response.status_code == 200
    data = response.get_json()

    answer = data["answer"].lower()
    assert any(phrase in answer for phrase in ["chưa có", "không tìm thấy", "chưa tìm thấy", "không có"])
    # Real alternatives must be offered (not the impossible 100k tour)
    assert len(data["tours"]) > 0
    assert all(tour["destination_name"] == "Hạ Long" for tour in data["tours"])

def test_api_chat_answer_quotes_real_db_data_without_gemini(client, monkeypatch):
    """Chat must act like a smart consultant quoting REAL database details
    (tour title, price, departure) even when the Gemini API key is unavailable."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    response = client.post(
        "/api/chat",
        json={"question": "Có tour Hạ Long nào dưới 4 triệu không?"}
    )
    assert response.status_code == 200
    data = response.get_json()

    assert len(data["tours"]) >= 1
    tour = data["tours"][0]
    answer = data["answer"]
    assert tour["title"] in answer
    price_str = f"{tour['base_price']:,}".replace(",", ".")
    assert price_str in answer
    assert "Khởi hành" in answer

def test_api_chat_no_match_answer_introduces_alternative_tours(client, monkeypatch):
    """No exact match -> the grounded answer must report it AND name the alternatives."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    response = client.post(
        "/api/chat",
        json={"question": "Có tour Nha Trang nào không?"}
    )
    assert response.status_code == 200
    data = response.get_json()

    assert "chưa có tour nào" in data["answer"].lower()
    assert len(data["tours"]) > 0
    assert data["tours"][0]["title"] in data["answer"]


def test_api_chat_feedback_summary_requires_admin(client, monkeypatch):
    """REGRESSION: a request to summarize customer feedback must NOT be answered
    with tour consultation text. Non-admin users receive a polite notice and no
    tour cards / no feedback content."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    response = client.post("/api/chat", json={"question": "Tóm tắt phản hồi khách hàng"})
    assert response.status_code == 200
    data = response.get_json()

    assert data["tours"] == []
    assert "ADMIN" in data["answer"]
    # Never leak the feedback report, never fall back to tour introductions
    assert "ĐIỂM KHEN NGỢI" not in data["answer"]
    assert "chưa có tour" not in data["answer"].lower()


def test_api_chat_feedback_summary_admin_returns_feedback_report(client, monkeypatch):
    """ADMIN asking for a feedback summary receives a real report built from the
    feedbacks stored in the database (deterministic offline fallback in tests)."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Quản Trị Viên"
        sess["role"] = "ADMIN"

    response = client.post("/api/chat", json={"question": "Tóm tắt phản hồi khách hàng"})
    assert response.status_code == 200
    data = response.get_json()

    assert data["tours"] == []
    answer = data["answer"]
    assert "ĐIỂM KHEN NGỢI" in answer
    assert "ĐIỂM CẦN CẢI THIỆN" in answer
    # Header must be grounded in the seeded test database (4 feedbacks, avg 4.8/5)
    assert "4 phản hồi" in answer
    assert "4.8/5" in answer

