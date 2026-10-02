"""
Tính năng: Khách hủy tour báo hoàn toàn -> Kế toán / Admin duyệt hoàn tiền.

Quy tắc nghiệp vụ:
- Khách hủy tour ĐÃ THANH TOÁN -> hệ thống tự tạo phiếu "báo hoàn toàn"
  (request_amount = đúng số tiền khách đã trả) ở trạng thái PENDING.
- Chỉ ADMIN / ACCOUNTANT được duyệt hoặc từ chối.
- Duyệt -> sinh phiếu chi REFUND và chống hoàn vượt số tiền đã trả.
- Từ chối -> bắt buộc có lý do để thông báo cho khách.
"""

import re
import pytest

from database.db import execute_query, get_db
from services.booking_service import BookingService
from services.payment_service import PaymentService
from services.refund_service import RefundService
from services.tour_service import TourService


def _page_text(resp):
    return re.sub(r"\s+", " ", resp.data.decode("utf-8"))


def _login_as(client, user_id, name, role):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = name
        sess["role"] = role


@pytest.fixture
def paid_booking():
    """Booking đã thanh toán của khách id=5 (chưa hủy)."""
    tour_id = TourService.create_tour(
        destination_id=1, title="Tour Test Phieu Hoan Tien",
        description="Tour dùng để kiểm tra phiếu báo hoàn toàn khi khách hủy.",
        duration_days=3, duration_nights=2, base_price=4_000_000,
        transportation="Xe test", itinerary_text="Ngay 1", image_url="",
    )
    schedule_id = TourService.create_schedule(
        tour_id=tour_id, departure_date="2027-12-20", return_date="2027-12-22",
        adult_price=4_000_000, child_price=2_800_000, total_seats=10)
    booking = BookingService.create_booking(
        user_id=5, schedule_id=schedule_id, customer_name="Khach Hoan Tien",
        customer_email="hoan.tien@tourai.vn", customer_phone="0955555555", num_adults=2)
    PaymentService.record_payment(booking["id"], 8_000_000, "BANK_TRANSFER", "TXN-HOAN-TEST")
    yield {"booking_id": booking["id"], "tour_id": tour_id, "schedule_id": schedule_id}
    with get_db() as conn:
        conn.execute("DELETE FROM refund_requests WHERE booking_id = ?;", (booking["id"],))
        conn.execute("DELETE FROM payments WHERE booking_id = ?;", (booking["id"],))
        conn.execute("DELETE FROM bookings WHERE id = ?;", (booking["id"],))
        conn.execute("DELETE FROM tour_schedules WHERE tour_id = ?;", (tour_id,))
        conn.execute("DELETE FROM tours WHERE id = ?;", (tour_id,))



# ==============================================================
# 1. KHACH HUY TOUR -> TU DONG TAO PHIEU BAO HOAN TOAN
# ==============================================================
def test_cancel_creates_pending_refund_request(paid_booking):
    """Hủy tour đã thanh toán -> phiếu PENDING bằng đúng số tiền đã trả."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5,
                                  reason="Bận việc gia đình")

    req = RefundService.get_request_by_booking(paid_booking["booking_id"])
    assert req is not None
    assert req["status"] == "PENDING"
    assert float(req["paid_amount"]) == 8_000_000
    # BÁO HOÀN TOÀN: đúng bằng số tiền khách đã thanh toán
    assert float(req["request_amount"]) == 8_000_000
    assert "gia đình" in req["reason"]


def test_cancel_stores_reason_in_booking_notes(paid_booking):
    """Lý do hủy được ghi lại trên đơn."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5,
                                  reason="Thời tiết xấu bất ngờ")
    row = execute_query("SELECT status, notes FROM bookings WHERE id = ?;",
                        (paid_booking["booking_id"],), fetch_one=True)
    assert row["status"] == "CANCELLED"
    assert "Thời tiết xấu" in row["notes"]


def test_cancel_without_payment_creates_no_request(paid_booking):
    """Khách chưa thanh toán -> không tạo phiếu hoàn (không có gì để hoàn)."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5)
    execute_query("DELETE FROM payments WHERE booking_id = ?;", (paid_booking["booking_id"],),
                  commit=True)
    req = RefundService.create_request(paid_booking["booking_id"], reason="test")
    assert req is None


def test_one_request_per_booking(paid_booking):
    """Mỗi đơn chỉ có đúng 1 phiếu hoàn tiền."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do A")
    again = RefundService.create_request(paid_booking["booking_id"], reason="Lý do B")
    assert again is None
    count = execute_query("SELECT COUNT(*) AS c FROM refund_requests WHERE booking_id = ?;",
                          (paid_booking["booking_id"],), fetch_one=True)
    assert count["c"] == 1


def test_request_amount_cannot_exceed_paid(paid_booking):
    """Không thể yêu cầu hoàn nhiều hơn số tiền đã trả."""
    with pytest.raises(ValueError, match="không thể vượt quá"):
        RefundService.create_request(paid_booking["booking_id"], reason="x",
                                     request_amount=99_000_000)


def test_customer_cancel_route_reports_refund(client, paid_booking):
    """Khách hủy qua giao diện được báo đã gửi yêu cầu hoàn toàn."""
    _login_as(client, 5, "Khách Hoàn Tiền", "CUSTOMER")
    resp = client.post(f"/booking/{paid_booking['booking_id']}/cancel",
                       data={"cancel_reason": "Đi công tác đột xuất"},
                       follow_redirects=True)
    assert resp.status_code == 200
    text = _page_text(resp)
    assert "Yêu cầu hoàn toàn" in text
    assert "8.000.000" in text
    assert "CHỜ DUYỆT HOÀN" in text  # badge trên bảng Tour của tôi


# ==============================================================
# 2. KE TOAN / ADMIN DUYET HOAN TIEN
# ==============================================================
def test_accountant_page_lists_pending_request(client, paid_booking):
    """Trang Hoàn Tiền hiển thị phiếu đang chờ duyệt kèm lý do khách."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Hủy vì lịch trình")
    _login_as(client, 3, "Kế Toán", "ACCOUNTANT")

    resp = client.get("/accounting/refunds")
    assert resp.status_code == 200
    text = _page_text(resp)
    assert "Phiếu Báo Hoàn Toàn" in text
    assert "Hủy vì lịch trình" in text
    assert "Duyệt hoàn tiền" in text
    assert "Từ chối" in text


def test_approve_request_creates_refund_payment(paid_booking):
    """Duyệt -> sinh phiếu chi REFUND đúng số tiền và ghi người xử lý."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    req = RefundService.get_request_by_booking(paid_booking["booking_id"])

    RefundService.approve_request(req["id"], approver_id=3, notes="CK STK 0123456789")

    updated = RefundService.get_request(req["id"])
    assert updated["status"] == "APPROVED"
    assert float(updated["decision_amount"]) == 8_000_000
    assert updated["processed_by"] == 3
    assert updated["processed_at"] is not None

    refund_row = execute_query(
        "SELECT COALESCE(SUM(amount), 0) AS a FROM payments "
        "WHERE booking_id = ? AND payment_type = 'REFUND' AND payment_status = 'SUCCESS';",
        (paid_booking["booking_id"],), fetch_one=True)
    assert refund_row["a"] == 8_000_000


def test_approve_with_partial_amount(paid_booking):
    """Kế toán có thể duyệt số tiền ít hơn khách yêu cầu (áp chính sách)."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    req = RefundService.get_request_by_booking(paid_booking["booking_id"])

    RefundService.approve_request(req["id"], approver_id=3, decision_amount=7_200_000)
    updated = RefundService.get_request(req["id"])
    assert updated["status"] == "APPROVED"
    assert float(updated["decision_amount"]) == 7_200_000  # 90% theo chính sách


def test_approve_twice_is_blocked(paid_booking):
    """Phiếu đã xử lý không được duyệt lại (chống hoàn tiền 2 lần)."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    req = RefundService.get_request_by_booking(paid_booking["booking_id"])
    RefundService.approve_request(req["id"], approver_id=3)

    with pytest.raises(ValueError, match="đã được xử lý"):
        RefundService.approve_request(req["id"], approver_id=3)

    refund_row = execute_query(
        "SELECT COALESCE(SUM(amount), 0) AS a FROM payments "
        "WHERE booking_id = ? AND payment_type = 'REFUND';",
        (paid_booking["booking_id"],), fetch_one=True)
    assert refund_row["a"] == 8_000_000  # không bị hoàn 2 lần


def test_admin_can_approve_refund(client, paid_booking):
    """ADMIN cũng được quyền duyệt hoàn tiền."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    req = RefundService.get_request_by_booking(paid_booking["booking_id"])

    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    resp = client.post(f"/accounting/refunds/{req['id']}/approve",
                       data={"decision_amount": req["request_amount"], "notes": "Duyệt"},
                       follow_redirects=True)
    assert "Đã duyệt hoàn tiền" in _page_text(resp)
    assert RefundService.get_request(req["id"])["status"] == "APPROVED"



# ==============================================================
# 3. TU CHOI HOAN TIEN (bat buoc co ly do)
# ==============================================================
def test_reject_request_requires_reason(paid_booking):
    """Từ chối mà không ghi lý do thì bị chặn."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    req = RefundService.get_request_by_booking(paid_booking["booking_id"])
    with pytest.raises(ValueError, match="lý do từ chối"):
        RefundService.reject_request(req["id"], approver_id=3, notes="   ")


def test_reject_request_marks_rejected(paid_booking):
    """Từ chối -> trạng thái REJECTED, không tạo phiếu chi REFUND."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    req = RefundService.get_request_by_booking(paid_booking["booking_id"])

    RefundService.reject_request(req["id"], approver_id=3,
                                 notes="Hủy trong vòng 3 ngày, không đủ điều kiện hoàn")

    updated = RefundService.get_request(req["id"])
    assert updated["status"] == "REJECTED"
    assert "không đủ điều kiện" in updated["decision_notes"]

    refund_row = execute_query(
        "SELECT COALESCE(SUM(amount), 0) AS a FROM payments "
        "WHERE booking_id = ? AND payment_type = 'REFUND';",
        (paid_booking["booking_id"],), fetch_one=True)
    assert refund_row["a"] == 0  # không được xuất quỹ


def test_reject_route_and_customer_view(client, paid_booking):
    """Từ chối qua giao diện -> khách thấy trạng thái kèm lý do."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    req = RefundService.get_request_by_booking(paid_booking["booking_id"])

    _login_as(client, 3, "Kế Toán", "ACCOUNTANT")
    resp = client.post(f"/accounting/refunds/{req['id']}/reject",
                       data={"notes": "Không đủ điều kiện hoàn theo chính sách"},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert RefundService.get_request(req["id"])["status"] == "REJECTED"

    _login_as(client, 5, "Khách", "CUSTOMER")
    text = _page_text(client.get("/my-bookings"))
    assert "TỪ CHỐI HOÀN" in text
    assert "Không đủ điều kiện" in text


# ==============================================================
# 4. PHAN QUYEN - chi ADMIN / ACCOUNTANT duyet duoc
# ==============================================================
def test_customer_cannot_approve_refund(client, paid_booking):
    """Khách hàng không tự duyệt được phiếu của chính mình."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    req = RefundService.get_request_by_booking(paid_booking["booking_id"])

    _login_as(client, 5, "Khách", "CUSTOMER")
    resp = client.post(f"/accounting/refunds/{req['id']}/approve",
                       data={"decision_amount": req["request_amount"]}, follow_redirects=True)
    assert "không có quyền" in _page_text(resp).lower()
    assert RefundService.get_request(req["id"])["status"] == "PENDING"


def test_staff_cannot_approve_refund(client, paid_booking):
    """STAFF không thuộc phân hệ tài chính nên không được duyệt hoàn tiền."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    req = RefundService.get_request_by_booking(paid_booking["booking_id"])

    _login_as(client, 2, "Tư Vấn Viên", "STAFF")
    resp = client.post(f"/accounting/refunds/{req['id']}/approve",
                       data={"decision_amount": req["request_amount"]}, follow_redirects=True)
    assert "không có quyền" in _page_text(resp).lower()
    assert RefundService.get_request(req["id"])["status"] == "PENDING"


def test_anonymous_cannot_approve_refund(client, paid_booking):
    """Chưa đăng nhập bị chuyển hướng về trang login."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    req = RefundService.get_request_by_booking(paid_booking["booking_id"])
    with client.session_transaction() as sess:
        sess.clear()

    resp = client.post(f"/accounting/refunds/{req['id']}/approve",
                       data={"decision_amount": req["request_amount"]}, follow_redirects=True)
    assert "đăng nhập" in _page_text(resp).lower()
    assert RefundService.get_request(req["id"])["status"] == "PENDING"


# ==============================================================
# 5. CHINH SACH GOI Y
# ==============================================================
def test_policy_percent_by_days_left():
    """Tỷ lệ gợi ý đúng theo chính sách: >=7 ngày 90%, 3-6 ngày 50%, <3 ngày 0%."""
    from datetime import date, timedelta
    assert RefundService.get_policy_percent((date.today() + timedelta(days=10)).isoformat()) == 90
    assert RefundService.get_policy_percent((date.today() + timedelta(days=5)).isoformat()) == 50
    assert RefundService.get_policy_percent((date.today() + timedelta(days=1)).isoformat()) == 0


def test_refund_list_exposes_policy_amount(paid_booking):
    """Danh sách phiếu kèm số tiền gợi ý theo chính sách để kế toán đối chiếu."""
    BookingService.cancel_booking(paid_booking["booking_id"], user_id=5, reason="Lý do")
    rows = RefundService.get_requests(status="PENDING")
    row = next(r for r in rows if r["booking_id"] == paid_booking["booking_id"])
    assert row["policy_percent"] in (0, 50, 90)
    assert row["policy_amount"] == row["paid_amount"] * row["policy_percent"] / 100

