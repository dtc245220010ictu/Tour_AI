"""
Unit & endpoint tests for AIContentService (staff AI content tools).
Guards the regression where the generator returned only the canned
customer-chat sentence instead of a real description + day-by-day itinerary
when the Gemini API was unavailable or answered in an unexpected format.
"""

from services.ai_content_service import AIContentService
from services.gemini_service import GeminiService

# The exact canned chat answer GeminiService._generate_fallback() returns.
CANNED_CHAT_ANSWER = (
    "Chào bạn! Dựa trên yêu cầu của bạn, TourAI đã tìm thấy các chuyến du lịch "
    "phù hợp nhất đang mở bán và còn chỗ trong hệ thống:\n\n"
    "Các tour trên đều có lịch trình chi tiết và được tổ chức trọn gói với dịch "
    "vụ chất lượng cao."
)

VALID_AI_ANSWER = """**[MÔ TẢ TOUR]**
Hành trình đưa du khách trở về miền di sản với những trải nghiệm khó quên, từ
đại nội cổ kính đến dòng sông Hương thơ mộng, ẩm thực cung đình và làng nghề
truyền thống được gìn giữ qua bao thế hệ.

## LỊCH TRÌNH CHI TIẾT
Ngày 1: Đón sân bay - Đại Nội Huế
- Sáng: Đón khách, nhận phòng khách sạn.
- Trưa: Ăn trưa món Huế.
- Chiều: Tham quan Đại Nội, Kinh thành.
- Tối: Ăn tối, dạo phố đi bộ.

Ngày 2: Chùa Thiên Mụ - Lăng Khải Định
- Sáng: Tham quan Chùa Thiên Mụ.
- Trưa: Ăn trưa.
- Chiều: Tham quan Lăng Khải Định.
- Tối: Nghe ca Huế trên sông Hương.

Ngày 3: Chợ Đông Ba - Tiễn khách
- Sáng: Mua đặc sản tại Chợ Đông Ba.
- Trưa: Ăn trưa, trả phòng.
- Chiều: Tiễn khách ra sân bay, kết thúc tour.
"""


def _generate(monkeypatch, ai_answer=None, configured=None):
    """Runs generate_tour_description with a stubbed Gemini layer."""
    if configured is None:
        # AI counts as configured whenever a stubbed answer is supplied.
        configured = ai_answer is not None
    monkeypatch.setattr(GeminiService, "is_configured", staticmethod(lambda: configured))
    if ai_answer is None:
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        return AIContentService.generate_tour_description(
            "Quy Nhơn - Kỳ Co - Eo Gió Biển Xanh", "Bình Định",
            "Kỳ Co, Eo Gió, bãi Xep, hải sản tươi sống", 3,
        )

    calls = {"count": 0, "texts": []}

    def fake_generate_content(prompt, temperature=0.4, fallback_answer=None, **kwargs):
        calls["count"] += 1
        calls["texts"].append(prompt)
        if callable(ai_answer):
            return ai_answer(calls["count"], fallback_answer)
        return ai_answer

    monkeypatch.setattr(GeminiService, "generate_content", staticmethod(fake_generate_content))
    monkeypatch.setattr("services.ai_content_service.time.sleep", lambda *_: None)
    result = AIContentService.generate_tour_description(
        "Quy Nhơn - Kỳ Co - Eo Gió Biển Xanh", "Bình Định",
        "Kỳ Co, Eo Gió, bãi Xep, hải sản tươi sống", 3,
    )
    result["_calls"] = calls
    return result


def test_offline_ai_itinerary_follows_requested_duration(monkeypatch):
    """Itinerary must cover exactly the requested number of days."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = AIContentService.generate_tour_description("Tour Đà Lạt 5 ngày", "Lâm Đồng", "", 5)

    assert "Ngày 5" in result["itinerary"]
    assert "Ngày 6" not in result["itinerary"]
    # Empty highlights still produce a readable sentence, not "None".
    assert "None" not in result["description"]


def test_parses_marked_ai_answer(monkeypatch):
    """A well-formed AI answer (markdown markers) is split into desc + itinerary."""
    result = _generate(monkeypatch, ai_answer=VALID_AI_ANSWER)

    assert result["source"] == "ai"
    assert result["description"].startswith("Hành trình đưa du khách")
    assert "[MÔ TẢ TOUR]" not in result["description"]
    assert "Ngày 1:" in result["itinerary"]
    assert "Ngày 3:" in result["itinerary"]
    # "lịch trình" inside the description must not trigger a false split.
    assert "LỊCH TRÌNH CHI TIẾT" not in result["itinerary"].split("Ngày 1")[0]


def test_rejects_irrelevant_ai_answer(monkeypatch):
    """An AI reply without a per-day plan (e.g. the canned sentence) is replaced."""
    result = _generate(monkeypatch, ai_answer=CANNED_CHAT_ANSWER)

    assert result["source"] == "template"
    assert "Ngày 1" in result["itinerary"] and "Ngày 3" in result["itinerary"]
    assert "TourAI đã tìm thấy các chuyến du lịch" not in result["description"]


def test_rejects_ai_itinerary_missing_requested_days(monkeypatch):
    """A truncated AI response cannot omit later days of the requested tour."""
    truncated_answer = """[MÔ TẢ TOUR]
Hành trình biển xanh thư giãn mang đến cho du khách những khoảnh khắc đáng nhớ,
kết hợp tham quan thắng cảnh, thưởng thức ẩm thực địa phương và nghỉ dưỡng.

[LỊCH TRÌNH CHI TIẾT]
Ngày 1: Khởi hành và nhận phòng
- Sáng: Đón khách tại điểm hẹn, khởi hành đến điểm đến.
- Trưa: Dùng bữa trưa tại nhà hàng địa phương.
- Chiều: Tham quan thắng cảnh nổi bật và chụp ảnh lưu niệm.
- Tối: Dùng bữa tối, tự do khám phá và nghỉ đêm tại khách sạn.
"""

    result = _generate(monkeypatch, ai_answer=truncated_answer)

    assert result["source"] == "template"
    for day in ("Ngày 1", "Ngày 2", "Ngày 3"):
        assert day in result["itinerary"]


def test_retries_transient_api_failure(monkeypatch):
    """A transient failure (fallback returned) is retried before using the template."""

    def flaky(attempt, fallback_answer):
        # First call simulates a 503 (GeminiService hands back the fallback).
        return fallback_answer if attempt == 1 else VALID_AI_ANSWER

    result = _generate(monkeypatch, ai_answer=flaky)

    assert result["source"] == "ai"
    assert result["_calls"]["count"] == 2


def test_offline_ai_returns_full_day_by_day_itinerary(monkeypatch):
    """REGRESSION: no API key -> structured content, never the canned chat line."""
    result = _generate(monkeypatch)

    assert result["source"] == "template"
    assert len(result["description"]) > 100
    for day in ("Ngày 1", "Ngày 2", "Ngày 3"):
        assert day in result["itinerary"]
    for slot in ("Sáng", "Trưa", "Chiều", "Tối"):
        assert slot in result["itinerary"]
    # The old bug: one irrelevant canned sentence in BOTH fields.
    assert "TourAI đã tìm thấy các chuyến du lịch" not in result["description"]
    assert "TourAI đã tìm thấy các chuyến du lịch" not in result["itinerary"]
    assert result["description"] != result["itinerary"]


def test_api_generate_description_returns_structured_content(client):
    """POST /api/ai/generate-description must return desc + full itinerary."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Quản Trị Viên"
        sess["role"] = "ADMIN"

    resp = client.post("/api/ai/generate-description", json={
        "title": "Huế - Đại Nội - Chùa Thiên Mụ",
        "destination": "Thừa Thiên Huế",
        "highlights": "Đại Nội, chùa Thiên Mụ, lăng Khải Định, ca Huế",
        "duration_days": 3,
    })
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["description"]
    assert "Ngày 1" in data["itinerary"]
    assert "Ngày 3" in data["itinerary"]
    assert data["source"] in ("ai", "template")
    assert "TourAI đã tìm thấy các chuyến du lịch" not in data["description"]


def test_api_generate_description_survives_bad_duration(client):
    """Non-numeric duration_days must not crash with a 500."""
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["user_name"] = "Tư Vấn Viên"
        sess["role"] = "STAFF"

    resp = client.post("/api/ai/generate-description", json={
        "title": "Tour Vũng Tàu 2N1Đ",
        "destination": "Bà Rịa - Vũng Tàu",
        "duration_days": "abc",
    })
    assert resp.status_code == 200
    assert "Ngày 1" in resp.get_json()["itinerary"]


def test_summarize_feedbacks_never_returns_canned_chat_answer(monkeypatch):
    """The feedback summarizer must return a real summary even when offline."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    summary = AIContentService.summarize_feedbacks([
        {"rating": 5, "comment": "HDV rất nhiệt tình"},
        {"rating": 3, "comment": "Bữa trưa hơi ít món"},
    ])

    assert "TourAI đã tìm thấy các chuyến du lịch" not in summary
    assert "ĐIỂM KHEN NGỢI" in summary
    assert "ĐIỂM CẦN CẢI THIỆN" in summary
