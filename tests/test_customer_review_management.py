"""
Tính năng: Khách hàng xem / sửa / xóa đánh giá của chính mình.

Quy tắc nghiệp vụ:
- Chỉ khách gửi đánh giá mới được xem/sửa/xóa đánh giá đó.
- Sau khi xóa, khách có thể đánh giá lại đơn đã hoàn thành.
- Validate vẫn giữ nguyên: sao 1-5, nội dung không rỗng.
"""

import re
import pytest

from database.db import execute_query, get_db
from services.booking_service import BookingService
from services.feedback_service import FeedbackService
from services.tour_service import TourService


def _page_text(resp):
    return re.sub(r"\s+", " ", resp.data.decode("utf-8"))


def _login_as(client, user_id, name, role):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = name
        sess["role"] = role


@pytest.fixture
def own_booking():
    """Booking COMPLETED của khách id=5 (chưa đánh giá) + tour tương ứng."""
    tour_id = TourService.create_tour(
        destination_id=1, title="Tour Test Quan Ly Danh Gia",
        description="Tour dùng để kiểm tra khach xem/sua/xoa danh gia cua minh.",
        duration_days=2, duration_nights=1, base_price=2_000_000,
        transportation="Xe test", itinerary_text="Ngay 1", image_url="",
    )
    schedule_id = TourService.create_schedule(
        tour_id=tour_id, departure_date="2026-01-05", return_date="2026-01-06",
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    booking = BookingService.create_booking(
        user_id=5, schedule_id=schedule_id, customer_name="Khach Chu So Huu",
        customer_email="chu@tourai.vn", customer_phone="0933333333", num_adults=1)
    BookingService.update_booking_status(booking["id"], "COMPLETED")
    yield {"booking_id": booking["id"], "tour_id": tour_id, "schedule_id": schedule_id}
    with get_db() as conn:
        conn.execute("DELETE FROM feedbacks WHERE booking_id = ?;", (booking["id"],))
        conn.execute("DELETE FROM payments WHERE booking_id = ?;", (booking["id"],))
        conn.execute("DELETE FROM bookings WHERE id = ?;", (booking["id"],))
        conn.execute("DELETE FROM tour_schedules WHERE tour_id = ?;", (tour_id,))
        conn.execute("DELETE FROM tours WHERE id = ?;", (tour_id,))


def _create_review(user_id, booking_id, tour_id, rating=5, comment="Chuyến đi rất tuyệt vời"):
    return FeedbackService.create_feedback(
        user_id=user_id, tour_id=tour_id, rating=rating, comment=comment,
        booking_id=booking_id)



# ==============================================================
# 1. KHACH XEM DUOC DANH GIA CUA CHINH MINH
# ==============================================================
def test_get_user_feedbacks_returns_only_own_reviews(own_booking):
    """Danh sách chỉ chứa đánh giá của đúng khách đang xem."""
    before = {f["id"] for f in FeedbackService.get_user_feedbacks(5)}
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"])

    mine = FeedbackService.get_user_feedbacks(5)
    ids = {f["id"] for f in mine}
    # Đánh giá mới xuất hiện, các đánh giá cũ vẫn còn
    assert fid in ids
    assert before <= ids
    new_row = next(f for f in mine if f["id"] == fid)
    assert new_row["tour_title"] == "Tour Test Quan Ly Danh Gia"
    assert new_row["booking_code"]

    # Khách khác KHÔNG thấy đánh giá này
    assert fid not in {f["id"] for f in FeedbackService.get_user_feedbacks(6)}


def test_my_bookings_shows_review_section(client, own_booking):
    """Trang 'Tour của tôi' hiển thị khu vực quản lý đánh giá."""
    _create_review(5, own_booking["booking_id"], own_booking["tour_id"])
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")

    text = _page_text(client.get("/my-bookings"))
    assert "Đánh Giá Của Tôi" in text
    assert "Tour Test Quan Ly Danh Gia" in text
    assert "Sửa" in text and "Xóa" in text


def test_my_bookings_empty_state_when_no_review(client, own_booking):
    """Khách chưa từng đánh giá thì thấy thông báo rỗng thay vì lỗi."""
    # Tạo khách mới chưa có đánh giá nào
    from werkzeug.security import generate_password_hash
    from database.db import execute_query as _q

    _q("INSERT INTO users (email, password_hash, full_name, phone, role) "
       "VALUES (?, ?, ?, ?, 'CUSTOMER');",
       ("chua.danhgia@tourai.vn", generate_password_hash("x"), "Khách Mới", "0900009999"),
       commit=True)
    uid = _q("SELECT id FROM users WHERE email = ?;", ("chua.danhgia@tourai.vn",),
             fetch_one=True)["id"]
    try:
        _login_as(client, uid, "Khách Mới", "CUSTOMER")
        assert "Bạn chưa có đánh giá nào" in _page_text(client.get("/my-bookings"))
    finally:
        with get_db() as conn:
            conn.execute("DELETE FROM users WHERE id = ?;", (uid,))


# ==============================================================
# 2. SUA DANH GIA
# ==============================================================
def test_update_feedback_changes_rating_and_comment(own_booking):
    """Sửa được cả số sao lẫn nội dung."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"], 5, "Nhận xét cũ")
    FeedbackService.update_feedback(fid, 5, 3, "Nhận xét đã sửa")

    row = FeedbackService.get_feedback_by_id(fid)
    assert row["rating"] == 3
    assert row["comment"] == "Nhận xét đã sửa"


def test_update_feedback_validates_rating_and_comment(own_booking):
    """Vẫn validate sao 1-5 và nội dung không rỗng."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"])
    with pytest.raises(ValueError, match="từ 1 đến 5"):
        FeedbackService.update_feedback(fid, 5, 9, "Hop le")
    with pytest.raises(ValueError, match="nội dung"):
        FeedbackService.update_feedback(fid, 5, 4, "   ")


def test_cannot_update_other_customers_review(own_booking):
    """Khách khác không sửa được đánh giá không thuộc về mình."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"])
    with pytest.raises(ValueError, match="chính mình"):
        FeedbackService.update_feedback(fid, 6, 1, "Cố sửa đánh giá người khác")
    assert FeedbackService.get_feedback_by_id(fid)["rating"] == 5


def test_edit_page_renders_own_review(client, own_booking):
    """Form sửa hiển thị đúng nội dung đánh giá của khách."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"], 4, "Cảm nhận riêng")
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")

    resp = client.get(f"/feedback/{fid}/edit")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Cảm nhận riêng" in html
    assert 'name="rating"' in html
    assert 'name="comment"' in html


def test_edit_route_rejects_other_customer(client, own_booking):
    """Route chặn cả khi xem lẫn khi lưu đánh giá của người khác."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"])
    _login_as(client, 6, "Khách Khác", "CUSTOMER")

    resp = client.get(f"/feedback/{fid}/edit", follow_redirects=True)
    assert "chính mình" in _page_text(resp)

    resp = client.post(f"/feedback/{fid}/edit",
                       data={"rating": 1, "comment": "hack"}, follow_redirects=True)
    assert "chính mình" in _page_text(resp)
    assert FeedbackService.get_feedback_by_id(fid)["rating"] == 5


def test_edit_route_saves_changes(client, own_booking):
    """Gửi form sửa cập nhật đánh giá trong DB."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"], 5, "Cũ")
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")

    resp = client.post(f"/feedback/{fid}/edit",
                       data={"rating": 2, "comment": "Mới"}, follow_redirects=True)
    assert resp.status_code == 200
    assert "Đã cập nhật đánh giá" in _page_text(resp)
    row = FeedbackService.get_feedback_by_id(fid)
    assert row["rating"] == 2 and row["comment"] == "Mới"


# ==============================================================
# 3. XOA DANH GIA
# ==============================================================
def test_delete_feedback_removes_record(own_booking):
    """Xóa đánh giá thật sự biến mất khỏi DB."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"])
    FeedbackService.delete_feedback(fid, 5)
    assert FeedbackService.get_feedback_by_id(fid) is None


def test_cannot_delete_other_customers_review(own_booking):
    """Khách khác không xóa được đánh giá không thuộc về mình."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"])
    with pytest.raises(ValueError, match="chính mình"):
        FeedbackService.delete_feedback(fid, 6)
    assert FeedbackService.get_feedback_by_id(fid) is not None


def test_delete_route_rejects_other_customer(client, own_booking):
    """Route xóa chặn thao tác chéo."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"])
    _login_as(client, 6, "Khách Khác", "CUSTOMER")

    resp = client.post(f"/feedback/{fid}/delete", follow_redirects=True)
    assert "chính mình" in _page_text(resp)
    assert FeedbackService.get_feedback_by_id(fid) is not None


def test_delete_allows_reviewing_again(client, own_booking):
    """Sau khi xóa, khách đánh giá lại được đơn đã hoàn thành."""
    bid, tid = own_booking["booking_id"], own_booking["tour_id"]
    fid = _create_review(5, bid, tid)
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")

    client.post(f"/feedback/{fid}/delete", follow_redirects=True)
    assert FeedbackService.get_reviewable_booking(5, tid)["id"] == bid

    resp = client.post("/feedback/new",
                       data={"tour_id": tid, "booking_id": bid, "rating": 5,
                             "comment": "Đánh giá lại lần hai"}, follow_redirects=True)
    assert "Cảm ơn bạn đã gửi đánh giá" in _page_text(resp)


def test_staff_cannot_manage_customer_reviews(client, own_booking):
    """STAFF không được sửa/xóa đánh giá của khách."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"])
    _login_as(client, 2, "Tư Vấn Viên", "STAFF")

    resp = client.get(f"/feedback/{fid}/edit", follow_redirects=True)
    assert "không có quyền" in _page_text(resp).lower()
    resp = client.post(f"/feedback/{fid}/delete", follow_redirects=True)
    assert "không có quyền" in _page_text(resp).lower()
    assert FeedbackService.get_feedback_by_id(fid) is not None


def test_anonymous_cannot_manage_reviews(client, own_booking):
    """Khách chưa đăng nhập bị chuyển hướng về trang login."""
    fid = _create_review(5, own_booking["booking_id"], own_booking["tour_id"])
    with client.session_transaction() as sess:
        sess.clear()

    resp = client.get(f"/feedback/{fid}/edit", follow_redirects=True)
    assert "đăng nhập" in _page_text(resp).lower()
    assert FeedbackService.get_feedback_by_id(fid) is not None

