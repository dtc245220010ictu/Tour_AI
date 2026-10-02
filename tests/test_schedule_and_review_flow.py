"""
Tính năng: Tạm hoãn lịch khởi hành kèm lý do + Đánh giá sau khi hoàn thành chuyến đi.

Quy tắc nghiệp vụ kiểm tra:
- Lịch khởi hành được TẠM HOÃN (POSTPONED) thì bắt buộc phải có lý do.
- Đợt đã tạm hoãn không được nhận thêm đơn đặt chỗ.
- Bảng đánh giá CHỈ hiển thị khi khách đã hoàn thành (COMPLETED) chuyến đi;
  mỗi đơn chỉ được đánh giá đúng 1 lần.
"""

import re
import pytest

from database.db import execute_query, get_db
from services.booking_service import BookingService, OverbookingError
from services.feedback_service import FeedbackService
from services.tour_service import TourService


def _page_text(resp):
    return re.sub(r"\s+", " ", resp.data.decode("utf-8"))


def _login_as(client, user_id, name, role):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = name
        sess["role"] = role


def _cleanup(tour_id, schedule_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM feedbacks WHERE booking_id IN "
            "(SELECT id FROM bookings WHERE schedule_id = ?);", (schedule_id,))
        conn.execute("DELETE FROM bookings WHERE schedule_id = ?;", (schedule_id,))
        conn.execute("DELETE FROM guide_assignments WHERE schedule_id = ?;", (schedule_id,))
        conn.execute("DELETE FROM tour_expenses WHERE schedule_id = ?;", (schedule_id,))
        conn.execute("DELETE FROM tour_schedules WHERE tour_id = ?;", (tour_id,))
        conn.execute("DELETE FROM tours WHERE id = ?;", (tour_id,))


def _make_tour(title, description, dep, ret, adult):
    tour_id = TourService.create_tour(
        destination_id=1, title=title, description=description,
        duration_days=2, duration_nights=1, base_price=adult,
        transportation="Xe test", itinerary_text="Ngay 1: Test", image_url="",
    )
    schedule_id = TourService.create_schedule(
        tour_id=tour_id, departure_date=dep, return_date=ret,
        adult_price=adult, child_price=round(adult * 0.7), total_seats=10,
    )
    return tour_id, schedule_id


@pytest.fixture
def open_schedule():
    """Một tour + đợt khởi hành OPEN. Tự dọn dẹp về sau."""
    tour_id, schedule_id = _make_tour(
        "Tour Test Tam Hoan Dot",
        "Tour dùng để kiểm tra tính năng tạm hoãn lịch khởi hành kèm lý do.",
        "2026-12-01", "2026-12-03", 3_000_000)
    yield {"tour_id": tour_id, "schedule_id": schedule_id}
    _cleanup(tour_id, schedule_id)


@pytest.fixture
def completed_booking():
    """Một booking COMPLETED của khách id=5."""
    tour_id, schedule_id = _make_tour(
        "Tour Test Danh Gia Hoan Thanh",
        "Tour dùng để kiểm tra bảng đánh giá chỉ mở khi chuyến đi đã hoàn thành.",
        "2026-01-10", "2026-01-11", 2_500_000)
    booking = BookingService.create_booking(
        user_id=5, schedule_id=schedule_id, customer_name="Khach Danh Gia",
        customer_email="danhgia@tourai.vn", customer_phone="0911222333", num_adults=2)
    BookingService.update_booking_status(booking["id"], "COMPLETED")
    slug = execute_query("SELECT slug FROM tours WHERE id = ?;", (tour_id,),
                         fetch_one=True)["slug"]
    yield {"booking": BookingService.get_booking_by_id(booking["id"]), "slug": slug}
    _cleanup(tour_id, schedule_id)


# ==============================================================
# 1. TAM HOAN LICH KHOI HANH (POSTPONED) - BAT BUOC KEM LY DO
# ==============================================================
def test_postpone_schedule_requires_reason(open_schedule):
    """Không có lý do thì không được tạm hoãn."""
    with pytest.raises(ValueError, match="lý do"):
        TourService.postpone_schedule(open_schedule["schedule_id"], "   ")


def test_postpone_schedule_stores_status_and_reason(open_schedule):
    """Tạm hoãn hợp lệ: status = POSTPONED và lưu lý do + mốc thời gian."""
    TourService.postpone_schedule(open_schedule["schedule_id"], "Thời tiết xấu do bão số 3")

    row = TourService.get_schedule_by_id(open_schedule["schedule_id"])
    assert row["status"] == "POSTPONED"
    assert row["postpone_reason"] == "Thời tiết xấu do bão số 3"
    assert row["postponed_at"] is not None


def test_postponed_schedule_cannot_receive_new_booking(open_schedule):
    """Đợt đang tạm hoãn thì khách không thể đặt thêm chỗ."""
    TourService.postpone_schedule(open_schedule["schedule_id"], "Chờ thời tiết ổn định")

    with pytest.raises(OverbookingError):
        BookingService.create_booking(
            user_id=5, schedule_id=open_schedule["schedule_id"],
            customer_name="Khách Test", customer_email="khach.test@tourai.vn",
            customer_phone="0900000000", num_adults=1)


def test_postponed_schedule_hidden_from_public_booking_list(open_schedule):
    """Đợt tạm hoãn không hiện danh sách mở bán, nhưng vẫn tra cứu được lý do."""
    tour_id = open_schedule["tour_id"]
    TourService.postpone_schedule(open_schedule["schedule_id"], "Đợt khởi hành dời lịch")

    open_schedules = TourService.get_tour_schedules(tour_id, only_open=True)
    assert open_schedule["schedule_id"] not in [s["id"] for s in open_schedules]

    postponed = TourService.get_postponed_schedules(tour_id)
    assert len(postponed) == 1
    assert postponed[0]["postpone_reason"] == "Đợt khởi hành dời lịch"


def test_resume_schedule_restores_open_status(open_schedule):
    """Khôi phục đợt đã tạm hoãn: trở lại OPEN và xóa lý do."""
    sid = open_schedule["schedule_id"]
    TourService.postpone_schedule(sid, "Lý do tạm thời")
    TourService.resume_schedule(sid)

    row = TourService.get_schedule_by_id(sid)
    assert row["status"] == "OPEN"
    assert row["postpone_reason"] is None


def test_resume_rejects_schedule_not_postponed(open_schedule):
    """Chỉ khôi phục được đợt đang tạm hoãn."""
    with pytest.raises(ValueError):
        TourService.resume_schedule(open_schedule["schedule_id"])


def test_update_schedule_postponed_requires_reason(open_schedule):
    """Sửa lịch sang POSTPONED cũng bắt buộc phải có lý do."""
    with pytest.raises(ValueError, match="lý do"):
        TourService.update_schedule(
            schedule_id=open_schedule["schedule_id"],
            departure_date="2026-12-01", return_date="2026-12-03",
            adult_price=3_000_000, child_price=2_100_000, total_seats=10,
            status="POSTPONED", postpone_reason="")


def test_update_schedule_clears_reason_when_leaving_postponed(open_schedule):
    """Chuyển sang trạng thái khác thì lý do tạm hoãn cũ được xóa."""
    sid = open_schedule["schedule_id"]
    TourService.postpone_schedule(sid, "Bão số 3")
    TourService.update_schedule(
        schedule_id=sid, departure_date="2026-12-01", return_date="2026-12-03",
        adult_price=3_000_000, child_price=2_100_000, total_seats=10,
        status="OPEN")

    row = TourService.get_schedule_by_id(sid)
    assert row["status"] == "OPEN"
    assert row["postpone_reason"] is None


def test_admin_postpone_route_rejects_blank_reason(client, open_schedule):
    """Route admin cũng chặn lý do rỗng (validate tầng service)."""
    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    resp = client.post(
        f"/admin/schedules/{open_schedule['schedule_id']}/postpone",
        data={"postpone_reason": "   "}, follow_redirects=True)
    assert resp.status_code == 200
    assert "lý do" in _page_text(resp).lower()
    assert TourService.get_schedule_by_id(open_schedule["schedule_id"])["status"] == "OPEN"


def test_staff_can_postpone_schedule(client, open_schedule):
    """STAFF được phép tạm hoãn đợt (CN3 - vận hành lịch khởi hành)."""
    _login_as(client, 2, "Tư Vấn Viên", "STAFF")
    resp = client.post(
        f"/admin/schedules/{open_schedule['schedule_id']}/postpone",
        data={"postpone_reason": "Đường bị ngập do mưa lớn"}, follow_redirects=True)
    assert resp.status_code == 200
    row = TourService.get_schedule_by_id(open_schedule["schedule_id"])
    assert row["status"] == "POSTPONED"
    assert row["postpone_reason"] == "Đường bị ngập do mưa lớn"


def test_admin_can_resume_schedule(client, open_schedule):
    """Route khôi phục mở lại đợt đã tạm hoãn."""
    sid = open_schedule["schedule_id"]
    TourService.postpone_schedule(sid, "Tạm hoãn tạm thời")

    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    resp = client.post(f"/admin/schedules/{sid}/resume", follow_redirects=True)
    assert resp.status_code == 200
    assert TourService.get_schedule_by_id(sid)["status"] == "OPEN"


def test_postpone_reason_visible_to_customers(client, open_schedule):
    """Khách hàng xem trang tour thấy lý do tạm hoãn."""
    slug = execute_query("SELECT slug FROM tours WHERE id = ?;",
                         (open_schedule["tour_id"],), fetch_one=True)["slug"]
    TourService.postpone_schedule(open_schedule["schedule_id"],
                                  "Bão số 3 đổi hướng khởi hành")

    _login_as(client, 5, "Khách Hàng", "CUSTOMER")
    resp = client.get(f"/tours/{slug}")
    assert resp.status_code == 200
    text = _page_text(resp)
    assert "Bão số 3 đổi hướng khởi hành" in text
    assert "tạm hoãn" in text.lower()


def test_schedules_manage_page_shows_postpone_reason(client, open_schedule):
    """Trang quản lý lịch hiển thị nút Tạm hoãn và lý do đã lưu."""
    TourService.postpone_schedule(open_schedule["schedule_id"], "Lý do hiển thị trên bảng")

    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    resp = client.get("/admin/schedules")
    assert resp.status_code == 200
    text = _page_text(resp)
    assert "Lý do hiển thị trên bảng" in text
    assert "TẠM HOÃN" in text



# ==============================================================
# 2. BANG DANH GIA CHI HIEN KHI CHUYEN DI HOAN THANH
# ==============================================================
def test_review_form_hidden_before_trip_completed(client, completed_booking):
    """CHƯA hoàn thành -> bảng đánh giá không hiện (chỉ có nhắc nhở)."""
    booking = completed_booking["booking"]
    BookingService.update_booking_status(booking["id"], "CONFIRMED")

    _login_as(client, 5, "Khách Hàng", "CUSTOMER")
    resp = client.get(f"/tours/{completed_booking['slug']}")

    assert resp.status_code == 200
    assert FeedbackService.get_reviewable_booking(5, booking["tour_id"]) is None
    text = _page_text(resp)
    # Form đánh giá (nút Gửi đánh giá + hidden booking_id) không xuất hiện
    assert "Gửi đánh giá" not in text
    assert 'name="booking_id"' not in resp.get_data(as_text=True)
    # Thay vào đó hiện nhắc nhở: chỉ mở sau khi hoàn thành chuyến đi
    assert "Bảng đánh giá sẽ mở sau khi bạn" in text
    assert "hoàn thành chuyến đi" in text


def test_review_form_shown_after_trip_completed(client, completed_booking):
    """Đã hoàn thành -> bảng đánh giá hiện, gắn đúng booking_id."""
    booking = completed_booking["booking"]
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")

    reviewable = FeedbackService.get_reviewable_booking(5, booking["tour_id"])
    assert reviewable is not None
    assert reviewable["id"] == booking["id"]

    resp = client.get(f"/tours/{completed_booking['slug']}")
    assert "Gửi đánh giá" in _page_text(resp)
    assert f'name="booking_id" value="{booking["id"]}"' in resp.get_data(as_text=True)


def test_submit_feedback_blocked_for_unfinished_booking(client, completed_booking):
    """Server chặn đánh giá khi đơn chưa COMPLETED (bỏ qua kiểm tra giao diện)."""
    booking = completed_booking["booking"]
    BookingService.update_booking_status(booking["id"], "CONFIRMED")

    _login_as(client, 5, "Khách Hàng", "CUSTOMER")
    resp = client.post("/feedback/new", data={
        "tour_id": booking["tour_id"], "booking_id": booking["id"],
        "rating": 5, "comment": "Chuyến đi rất tuyệt vời"}, follow_redirects=True)
    assert resp.status_code == 200
    assert "Chỉ có thể đánh giá sau khi chuyến đi đã hoàn thành" in _page_text(resp)

    row = execute_query("SELECT COUNT(*) AS c FROM feedbacks WHERE booking_id = ?;",
                        (booking["id"],), fetch_one=True)
    assert row["c"] == 0



def test_submit_feedback_allowed_once_after_completion(client, completed_booking):
    """Sau khi hoàn thành thì đánh giá được, nhưng chỉ 1 lần cho mỗi đơn."""
    booking = completed_booking["booking"]
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")

    payload = {"tour_id": booking["tour_id"], "booking_id": booking["id"],
               "rating": 5, "comment": "Chuyến đi tuyệt vời, HDV thân thiện"}
    first = client.post("/feedback/new", data=payload, follow_redirects=True)
    assert "Cảm ơn bạn đã gửi đánh giá" in _page_text(first)

    second = client.post("/feedback/new", data=payload, follow_redirects=True)
    assert "Bạn đã đánh giá chuyến đi này rồi" in _page_text(second)

    row = execute_query("SELECT COUNT(*) AS c FROM feedbacks WHERE booking_id = ?;",
                        (booking["id"],), fetch_one=True)
    assert row["c"] == 1

    # Form đánh giá đóng lại sau khi đã gửi
    resp = client.get(f"/tours/{completed_booking['slug']}")
    assert "Gửi đánh giá" not in _page_text(resp)


def test_cannot_review_other_customers_booking(completed_booking):
    """Khách không thể đánh giá đơn của người khác."""
    booking = completed_booking["booking"]
    with pytest.raises(ValueError, match="chính mình"):
        FeedbackService.create_feedback(
            user_id=4, tour_id=booking["tour_id"], rating=5,
            comment="Cố đánh giá đơn của người khác", booking_id=booking["id"])


def test_my_bookings_shows_review_button_after_completion(client, completed_booking):
    """Trang 'Tour của tôi' hiện nút Đánh giá khi đơn đã hoàn thành."""
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")
    resp = client.get("/my-bookings")
    assert "ĐÃ HOÀN THÀNH" in _page_text(resp)
    assert "⭐ Đánh giá" in _page_text(resp)
    assert completed_booking["slug"] in resp.get_data(as_text=True)


def test_my_bookings_marks_reviewed_booking(client, completed_booking):
    """Sau khi đánh giá, nút Đánh giá đổi thành 'Đã đánh giá'."""
    booking = completed_booking["booking"]
    FeedbackService.create_feedback(user_id=5, tour_id=booking["tour_id"], rating=4,
                                    comment="Chuyến đi ổn", booking_id=booking["id"])

    _login_as(client, 5, "Khách Hàng", "CUSTOMER")
    text = _page_text(client.get("/my-bookings"))
    assert "Đã đánh giá" in text
    assert "⭐ Đánh giá" not in text


def test_unreviewed_completed_bookings_listing(completed_booking):
    """Danh sách chờ đánh giá chỉ gồm đơn COMPLETED chưa có phản hồi."""
    booking = completed_booking["booking"]
    pending = FeedbackService.get_unreviewed_completed_bookings(5)
    assert booking["id"] in [b["id"] for b in pending]

    FeedbackService.create_feedback(user_id=5, tour_id=booking["tour_id"], rating=5,
                                    comment="Tuyệt vời", booking_id=booking["id"])
    pending_after = FeedbackService.get_unreviewed_completed_bookings(5)
    assert booking["id"] not in [b["id"] for b in pending_after]

