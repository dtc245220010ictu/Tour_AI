"""
RBAC (Role-Based Access Control) Tests for TourAI.
Verifies the permission matrix: ADMIN, STAFF, ACCOUNTANT, GUIDE, CUSTOMER
against management, accounting, feedback, and AI endpoints.
"""

import re
import pytest

from database.db import get_db
from services.tour_service import TourService


def _page_text(resp):
    return re.sub(r"\s+", " ", resp.data.decode("utf-8"))


def _login_as(client, user_id, name, role):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = name
        sess["role"] = role


def test_staff_cannot_access_statistics_dashboard(client):
    """CN8 (Thống kê): STAFF = Không có quyền -> /admin/dashboard từ chối (302)."""
    _login_as(client, 2, "Tư Vấn Viên", "STAFF")
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 302
    assert "/login" not in resp.headers["Location"]


def test_accountant_cannot_manage_bookings(client):
    """CN4 (Đặt chỗ): ACCOUNTANT = Không có quyền -> /admin/bookings từ chối."""
    _login_as(client, 3, "Kế Toán", "ACCOUNTANT")
    assert client.get("/admin/bookings").status_code == 302
    resp = client.post("/admin/bookings/1/status", data={"status": "CONFIRMED"})
    assert resp.status_code == 302


def test_staff_cannot_access_feedback_management(client):
    """CN7 (Phản hồi): STAFF = Không có quyền -> /admin/feedbacks từ chối."""
    _login_as(client, 2, "Tư Vấn Viên", "STAFF")
    assert client.get("/admin/feedbacks").status_code == 302
    resp = client.post("/api/ai/summarize-feedbacks")
    assert resp.status_code == 302


def test_staff_can_manage_tours_and_schedules(client):
    """CN2/CN3: STAFF được quản lý tour và lịch khởi hành."""
    _login_as(client, 2, "Tư Vấn Viên", "STAFF")
    assert client.get("/admin/tours").status_code == 200
    assert client.get("/admin/schedules").status_code == 200


def test_staff_cannot_delete_tour(client):
    """CN2: STAFF không có quyền Xóa tour -> endpoint delete = ADMIN-only."""
    _login_as(client, 2, "Tư Vấn Viên", "STAFF")
    resp = client.post("/admin/tours/1/delete")
    assert resp.status_code == 302  # roles_required redirects (permission denied)


def test_tour_manage_list_exposes_edit_action(client):
    """CN2: Trang Quản lý sản phẩm tour hiển thị nút Sửa cho ADMIN/STAFF; nút Xóa chỉ ADMIN."""
    _login_as(client, 2, "Tư Vấn Viên", "STAFF")
    text = _page_text(client.get("/admin/tours"))
    assert "/admin/tours/1/edit" in text
    assert "/admin/tours/1/delete" not in text

    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    text = _page_text(client.get("/admin/tours"))
    assert "/admin/tours/1/edit" in text
    assert "/admin/tours/1/delete" in text


def test_staff_can_open_and_submit_tour_edit_form(client):
    """CN2: STAFF mở được form Sửa tour từ danh sách và lưu thay đổi thành công."""
    tour_id = TourService.create_tour(
        destination_id=1,
        title="Tour Kiem Tra Form Sua",
        description="Tour dùng để kiểm tra chức năng sửa từ trang quản lý sản phẩm tour.",
        duration_days=2,
        duration_nights=1,
        base_price=1_000_000,
        transportation="Xe test",
        itinerary_text="Ngày 1: Test",
        image_url="",
    )
    try:
        _login_as(client, 2, "Tư Vấn Viên", "STAFF")

        resp = client.get(f"/admin/tours/{tour_id}/edit")
        assert resp.status_code == 200
        assert "Sửa Thông Tin Tour" in _page_text(resp)

        resp = client.post(
            f"/admin/tours/{tour_id}/edit",
            data={
                "destination_id": "1",
                "title": "Tour Da Cap Nhat Tu Quan Ly",
                "description": "Mô tả tour đã được cập nhật thành công từ trang quản lý sản phẩm.",
                "duration_days": "3",
                "duration_nights": "2",
                "base_price": "1200000",
                "transportation": "Xe du lịch",
                "itinerary_text": "Ngày 1: Cập nhật",
                "is_active": "1",
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert "Đã cập nhật tour thành công!" in _page_text(resp)

        updated = TourService.get_tour_by_id(tour_id)
        assert updated is not None
        assert updated["title"] == "Tour Da Cap Nhat Tu Quan Ly"
        assert updated["duration_days"] == 3
        assert float(updated["base_price"]) == 1_200_000
    finally:
        with get_db() as conn:
            conn.execute("DELETE FROM guide_assignments WHERE schedule_id IN (SELECT id FROM tour_schedules WHERE tour_id = ?);", (tour_id,))
            conn.execute("DELETE FROM tour_expenses WHERE schedule_id IN (SELECT id FROM tour_schedules WHERE tour_id = ?);", (tour_id,))
            conn.execute("DELETE FROM bookings WHERE schedule_id IN (SELECT id FROM tour_schedules WHERE tour_id = ?);", (tour_id,))
            conn.execute("DELETE FROM tour_schedules WHERE tour_id = ?;", (tour_id,))
            conn.execute("DELETE FROM tours WHERE id = ?;", (tour_id,))


def test_accountant_can_view_statistics(client):
    """CN8: ACCOUNTANT được Xem thống kê -> /admin/dashboard 200, ẩn bảng đặt chỗ."""
    _login_as(client, 3, "Kế Toán", "ACCOUNTANT")
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200
    assert "Đơn Đặt Chỗ Gần Đây" not in _page_text(resp)


def test_admin_full_access(client):
    """ADMIN toàn quyền trên các chức năng quản lý."""
    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    assert client.get("/admin/dashboard").status_code == 200
    assert client.get("/admin/tours").status_code == 200
    assert client.get("/admin/bookings").status_code == 200
    assert client.get("/admin/feedbacks").status_code == 200
    assert client.get("/accounting/dashboard").status_code == 200


def test_customer_cannot_access_admin_or_accounting(client):
    """CUSTOMER: không truy cập quản trị/kế toán."""
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")
    assert client.get("/admin/dashboard").status_code == 302
    assert client.get("/admin/tours").status_code == 302
    assert client.get("/accounting/dashboard").status_code == 302


def test_guide_is_read_only(client):
    """GUIDE: chỉ được xem -> không vào quản trị/kế toán, không gửi phản hồi."""
    _login_as(client, 4, "Hướng Dẫn Viên", "GUIDE")
    assert client.get("/admin/tours").status_code == 302
    assert client.get("/admin/schedules").status_code == 302
    assert client.get("/accounting/dashboard").status_code == 302
    # Bị từ chối khi POST gửi phản hồi (roles_required redirect về trang chủ)
    resp = client.post("/feedback/new", data={"tour_id": 1, "rating": 5, "comment": "ok"})
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")


def test_customer_can_submit_feedback(client):
    """CN7: CUSTOMER được Thêm đánh giá/phản hồi."""
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")
    resp = client.post(
        "/feedback/new",
        data={"tour_id": 1, "rating": 5, "comment": "Chuyến đi tuyệt vời!"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Cảm ơn bạn đã gửi đánh giá" in _page_text(resp)


def test_customer_cannot_view_others_booking(client):
    """CN4: CUSTOMER chỉ xem được đơn của chính mình."""
    from database.db import execute_query
    from services.booking_service import BookingService

    # Tạo một đơn của người dùng khác (user_id=4) để kiểm tra cách ly dữ liệu
    other = execute_query(
        "SELECT booking_code FROM bookings WHERE user_id != 5 LIMIT 1;",
        fetch_one=True,
    )
    if not other:
        booking = BookingService.create_booking(
            user_id=4,
            schedule_id=1,
            customer_name="Khách Của Hướng Dẫn Viên",
            customer_email="other_owner@test.com",
            customer_phone="0900000004",
            num_adults=1,
            num_children=0,
        )
        assert booking is not None
        other = {"booking_code": booking["booking_code"]}

    assert other is not None
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")
    resp = client.get(f"/booking/success/{other['booking_code']}")
    assert resp.status_code == 302
    assert "my-bookings" in resp.headers["Location"]


def test_all_roles_can_use_ai_chatbot(client):
    """Trợ lý AI: tất cả 5 vai trò đều Có quyền sử dụng (trang + API)."""
    for role, uid, name in [
        ("ADMIN", 1, "A"),
        ("STAFF", 2, "S"),
        ("ACCOUNTANT", 3, "K"),
        ("GUIDE", 4, "H"),
        ("CUSTOMER", 5, "C"),
    ]:
        _login_as(client, uid, name, role)
        resp = client.get("/chat")
        assert resp.status_code == 200, f"Vai trò {role} không dùng được Trợ lý AI"
        resp = client.post("/api/chat", json={"question": "Có tour nào đi biển không?"})
        assert resp.status_code == 200, f"API chat lỗi với vai trò {role}"


def test_anonymous_redirected_on_management_pages(client):
    """Khách chưa đăng nhập: bị chuyển hướng đăng nhập."""
    for url in ["/admin/dashboard", "/admin/tours", "/accounting/dashboard", "/my-bookings"]:
        resp = client.get(url)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


# ==============================================================
# CN6: Quản lý hướng dẫn viên & phân công tour
# ==============================================================
def test_admin_can_manage_guides(client):
    """ADMIN toàn quyền CN6: xem danh sách HDV + bảng phân công."""
    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    resp = client.get("/admin/guides")
    assert resp.status_code == 200
    html = _page_text(resp)
    assert "Quản Lý Hướng Dẫn Viên" in html
    assert "Lê Văn Hải" in html  # seed data


def test_staff_accountant_cannot_access_guide_management(client):
    """CN6: STAFF và ACCOUNTANT = Không có quyền quản lý HDV."""
    _login_as(client, 2, "Tư Vấn Viên", "STAFF")
    assert client.get("/admin/guides").status_code == 302

    _login_as(client, 3, "Kế Toán", "ACCOUNTANT")
    assert client.get("/admin/guides").status_code == 302
    resp = client.post("/admin/guides/assign", data={"schedule_id": 1, "guide_id": 1})
    assert resp.status_code == 302


def test_guide_can_view_assignment_board_readonly(client):
    """CN6: GUIDE xem bảng phân công của mình & đồng nghiệp (read-only, 200)."""
    _login_as(client, 4, "Hướng Dẫn Viên", "GUIDE")
    resp = client.get("/guide/schedule")
    assert resp.status_code == 200
    html = _page_text(resp)
    assert "Bảng Phân Công Nhiệm Vụ" in html
    assert "Lê Văn Hải" in html  # thấy phân công của đồng nghiệp (seed)
    # Read-only: không có form thao tác nào trên trang
    assert "Hủy phân công" not in html
    assert "admin.delete_guide" not in resp.data.decode("utf-8")


def test_customer_can_view_guides_on_tour_detail(client):
    """CN6: CUSTOMER xem HDV ở trang chi tiết tour."""
    resp = client.get("/tours/ha-long-du-thuyen-5-sao")
    if resp.status_code == 404:
        # fallback: lấy slug từ danh sách tour
        from database.db import execute_query
        tour = execute_query("SELECT slug FROM tours LIMIT 1;", fetch_one=True)
        assert tour is not None
        resp = client.get(f"/tours/{tour['slug']}")
    assert resp.status_code == 200
    assert "Hướng Dẫn Viên Đồng Hành" in _page_text(resp)


def test_customer_cannot_access_guide_admin(client):
    """CN6: CUSTOMER không vào được quản lý HDV."""
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")
    assert client.get("/admin/guides").status_code == 302
    assert client.get("/guide/schedule").status_code == 302


def test_assign_guide_rejects_schedule_conflict():
    """FR-018: Phân công trùng lịch phải bị từ chối."""
    from services.guide_service import GuideService
    from database.db import execute_query

    # HDV 1 (Lê Văn Hải) đã dẫn schedule 1: 2026-10-15 -> 2026-10-16
    # schedule 7 (Sa Pa): 2026-10-16 -> 2026-10-18 => overlap tại 10-16
    overlap = execute_query(
        "SELECT id FROM tour_schedules WHERE departure_date = '2026-10-16' AND return_date = '2026-10-18';",
        fetch_one=True,
    )
    if not overlap:
        pytest.skip("Không tìm thấy lịch trùng trong seed")

    with pytest.raises(ValueError) as exc:
        GuideService.assign_guide(schedule_id=overlap["id"], guide_id=1)
    assert "Trùng lịch" in str(exc.value)


def test_assign_guide_success_and_duplicate_rejected():
    """FR-018: Phân công hợp lệ thành công, phân công trùng bị từ chối."""
    from services.guide_service import GuideService
    from database.db import execute_query

    # Tìm lịch còn trống với HDV 2 (Nguyễn Thị Mai)
    free = execute_query(
        """SELECT s.id FROM tour_schedules s
           WHERE s.id NOT IN (SELECT schedule_id FROM guide_assignments WHERE guide_id = 2)
             AND s.id NOT IN (
               SELECT ga.schedule_id FROM guide_assignments ga
               JOIN tour_schedules s2 ON ga.schedule_id = s2.id
               JOIN tour_schedules mine ON mine.id = s.id
               WHERE ga.guide_id = 2 AND s2.departure_date <= mine.return_date AND s2.return_date >= mine.departure_date
             )
           LIMIT 1;""",
        fetch_one=True,
    )
    if not free:
        pytest.skip("Không có lịch trống cho HDV 2")

    aid = GuideService.assign_guide(schedule_id=free["id"], guide_id=2, notes="Test phân công")
    assert aid

    # Phân công trùng chính xác schedule+guide -> ValueError
    with pytest.raises(ValueError) as exc:
        GuideService.assign_guide(schedule_id=free["id"], guide_id=2)
    assert "đã được phân công" in str(exc.value)

    # Dọn dẹp
    GuideService.remove_assignment(aid)
