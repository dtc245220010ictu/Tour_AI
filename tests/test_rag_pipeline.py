"""
Integration and End-to-End tests for RAG AI Pipeline and Chat API.
Verifies POST /api/chat endpoint, request validation, zero-hallucination constraints,
and rich tour cards response.
"""

from services.rag_service import RAGService

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

