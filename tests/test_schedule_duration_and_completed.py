"""
Tính năng: Tự điền ngày về theo thời lượng tour + Bộ lọc "Tour đã hoàn thành".

Quy tắc nghiệp vụ:
- Ngày về của đợt khởi hành phải khớp với thời lượng của tour
  (ngày về = ngày khởi hành + duration_days - 1).
- Đợt đã kết thúc (ngày về < hôm nay) được đánh dấu là tour đã hoàn thành
  và lọc được qua bộ lọc trạng thái.
"""

from datetime import date, timedelta

import pytest

from database.db import get_db
from services.analytics_service import AnalyticsService
from services.tour_service import TourService


def _iso(days_from_today: int) -> str:
    return (date.today() + timedelta(days=days_from_today)).isoformat()


def _page_text(resp):
    import re
    return re.sub(r"\s+", " ", resp.data.decode("utf-8"))


def _login_as(client, user_id, name, role):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = name
        sess["role"] = role


@pytest.fixture
def duration_tour():
    """Tour 4 ngày 3 đêm dùng để kiểm tra công thức ngày về."""
    tour_id = TourService.create_tour(
        destination_id=1, title="Tour Test Thoi Luong",
        description="Tour 4 ngay 3 dem de kiem tra tu dien ngay ve.",
        duration_days=4, duration_nights=3, base_price=2_000_000,
        transportation="Xe test", itinerary_text="Ngay 1", image_url="",
    )
    yield tour_id
    with get_db() as conn:
        conn.execute(
            "DELETE FROM feedbacks WHERE booking_id IN "
            "(SELECT id FROM bookings WHERE schedule_id IN "
            "(SELECT id FROM tour_schedules WHERE tour_id = ?));", (tour_id,))
        conn.execute("DELETE FROM bookings WHERE schedule_id IN "
                     "(SELECT id FROM tour_schedules WHERE tour_id = ?);", (tour_id,))
        conn.execute("DELETE FROM guide_assignments WHERE schedule_id IN "
                     "(SELECT id FROM tour_schedules WHERE tour_id = ?);", (tour_id,))
        conn.execute("DELETE FROM tour_expenses WHERE schedule_id IN "
                     "(SELECT id FROM tour_schedules WHERE tour_id = ?);", (tour_id,))
        conn.execute("DELETE FROM tour_schedules WHERE tour_id = ?;", (tour_id,))
        conn.execute("DELETE FROM tours WHERE id = ?;", (tour_id,))



def test_tour_duration_available_on_schedule_row(duration_tour):
    """Đợt khởi hành trả về thời lượng tour để giao diện tự tính ngày về."""
    sid = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    row = TourService.get_schedule_by_id(sid)
    assert row["duration_days"] == 4
    assert row["duration_nights"] == 3


def test_occupancy_rows_include_duration(duration_tour):
    """Bảng quản lý lịch có duration để hiển thị 'x ngày y đêm'."""
    TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)

    rows = AnalyticsService.get_occupancy_rates()
    target = next(r for r in rows if r["tour_title"] == "Tour Test Thoi Luong")
    assert target["duration_days"] == 4
    assert target["duration_nights"] == 3


def test_return_date_formula_matches_duration(duration_tour):
    """Công thức ngày về = ngày khởi hành + (duration_days - 1)."""
    dep = date(2026, 12, 10)
    expected = (dep + timedelta(days=3)).isoformat()
    assert expected == "2026-12-13"

    sid = TourService.create_schedule(
        tour_id=duration_tour, departure_date=dep.isoformat(), return_date=expected,
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    row = TourService.get_schedule_by_id(sid)
    assert row["return_date"] == expected


def test_past_schedule_marked_completed(duration_tour):
    """Đợt đã qua được đánh dấu is_completed."""
    sid = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(-20), return_date=_iso(-17),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)

    rows = AnalyticsService.get_occupancy_rates()
    target = next(r for r in rows if r["id"] == sid)
    assert target["is_completed"] is True


def test_future_schedule_not_completed(duration_tour):
    """Đợt sắp tới chưa hoàn thành."""
    sid = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)

    rows = AnalyticsService.get_occupancy_rates()
    target = next(r for r in rows if r["id"] == sid)
    assert target["is_completed"] is False


def test_postponed_past_schedule_not_completed(duration_tour):
    """Đợt đã qua nhưng đang tạm hoãn thì chưa tính là tour đã hoàn thành."""
    sid = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(-20), return_date=_iso(-17),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    TourService.postpone_schedule(sid, "Tạm hoãn do thời tiết")

    rows = AnalyticsService.get_occupancy_rates()
    target = next(r for r in rows if r["id"] == sid)
    assert target["is_completed"] is False


def test_filter_completed_returns_only_past(duration_tour):
    """Bộ lọc 'completed' chỉ trả về đợt đã kết thúc."""
    past_id = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(-20), return_date=_iso(-17),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    future_id = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)

    ids = [r["id"] for r in AnalyticsService.get_occupancy_rates("completed")]
    assert past_id in ids
    assert future_id not in ids


def test_filter_upcoming_excludes_completed(duration_tour):
    """Bộ lọc 'upcoming' loại các đợt đã hoàn thành."""
    past_id = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(-20), return_date=_iso(-17),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    future_id = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)

    ids = [r["id"] for r in AnalyticsService.get_occupancy_rates("upcoming")]
    assert future_id in ids
    assert past_id not in ids


def test_filter_postponed(duration_tour):
    """Bộ lọc 'postponed' chỉ trả về đợt đang tạm hoãn."""
    sid = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    other = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(60), return_date=_iso(63),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    TourService.postpone_schedule(sid, "Lý do tạm hoãn")

    ids = [r["id"] for r in AnalyticsService.get_occupancy_rates("postponed")]
    assert ids == [sid]
    assert other not in ids


def test_filter_all_returns_everything(duration_tour):
    """Bộ lọc mặc định trả về toàn bộ đợt."""
    a = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(-20), return_date=_iso(-17),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    b = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    ids = [r["id"] for r in AnalyticsService.get_occupancy_rates("all")]
    assert a in ids and b in ids


def test_schedules_page_exposes_filter_tabs_and_duration_data(client, duration_tour):
    """Trang quản lý lịch có bộ lọc trạng thái + dữ liệu thời lượng để JS dùng."""
    TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)

    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    resp = client.get("/admin/schedules")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    # Bộ lọc trạng thái
    for label in ["Tất cả", "Sắp diễn ra", "Đã hoàn thành", "Đang tạm hoãn"]:
        assert label in html
    # Option tour mang thời lượng để tự tính ngày về
    assert 'data-duration-days="4"' in html
    assert 'data-duration-nights="3"' in html
    # Ô nhập ngày về có id để JS ghi vào
    assert 'id="return_date"' in html
    assert 'id="departure_date"' in html


def test_completed_filter_page_shows_badge(client, duration_tour):
    """Lọc 'Đã hoàn thành' chỉ hiện đợt đã qua kèm badge."""
    TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(-20), return_date=_iso(-17),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)

    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    html = client.get("/admin/schedules?filter=completed").get_data(as_text=True)
    assert "Tour Test Thoi Luong" in html
    assert "ĐÃ HOÀN THÀNH" in html


def test_upcoming_filter_page_hides_completed(client, duration_tour):
    """Lọc 'Sắp diễn ra' không hiện đợt đã hoàn thành."""
    TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(-20), return_date=_iso(-17),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)
    TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)

    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    rows = AnalyticsService.get_occupancy_rates("upcoming")
    titles = [r["tour_title"] for r in rows]
    assert "Tour Test Thoi Luong" in titles
    assert all(not r["is_completed"] for r in rows)


def test_schedule_edit_page_contains_auto_return_script(client, duration_tour):
    """Form sửa lịch có script tự điền ngày về theo thời lượng tour."""
    sid = TourService.create_schedule(
        tour_id=duration_tour, departure_date=_iso(30), return_date=_iso(33),
        adult_price=2_000_000, child_price=1_400_000, total_seats=10)

    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    resp = client.get(f"/admin/schedules/{sid}/edit")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "const totalDays = 4;" in html
    assert "const totalNights = 3;" in html
    assert 'id="return_date"' in html

