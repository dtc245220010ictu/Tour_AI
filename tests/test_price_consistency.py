"""
Data-consistency tests: tour name and ticket prices must stay linked across pages.
Guards against mismatch between tours.base_price, tour_schedules prices,
bookings.total_amount and the tour title JOINed everywhere.
"""

from database.db import execute_query, get_db
import pytest
from services.booking_service import BookingService
from services.tour_service import TourService
from services.analytics_service import AnalyticsService


def test_schedule_title_matches_tours_table():
    """Tên tour trên form đặt chỗ phải JOIN từ bảng tours (không lưu riêng -> không lệch)."""
    schedule = TourService.get_schedule_by_id(1)
    tour = execute_query(
        "SELECT title FROM tours WHERE id = ?;", (schedule["tour_id"],), fetch_one=True
    )
    assert tour is not None
    assert schedule["tour_title"] == tour["title"]


def test_seeded_booking_total_matches_schedule_prices():
    """Tổng tiền đơn BK-20261001 phải bằng NL×giá NL + TE×giá TE của đúng lịch khởi hành."""
    booking = execute_query(
        "SELECT * FROM bookings WHERE booking_code = 'BK-20261001';", fetch_one=True
    )
    assert booking is not None
    schedule = execute_query(
        "SELECT adult_price, child_price FROM tour_schedules WHERE id = ?;",
        (booking["schedule_id"],),
        fetch_one=True,
    )
    expected = (
        booking["num_adults"] * schedule["adult_price"]
        + booking["num_children"] * schedule["child_price"]
    )
    assert abs(float(booking["total_amount"]) - float(expected)) < 1


def test_sync_schedule_prices_updates_all_departures():
    """sync_schedule_prices cập nhật giá NL = giá tour, giá TE = 70% cho mọi đợt của tour."""
    tour_id = TourService.create_tour(
        destination_id=1,
        title="Tour Dong Bo Gia Test",
        description="Tour dùng cho test đồng bộ giá",
        duration_days=2,
        duration_nights=1,
        base_price=1_000_000,
        transportation="Xe test",
        itinerary_text="Ngày 1: Test",
        image_url="",
    )
    try:
        TourService.create_schedule(tour_id, "2027-01-10", "2027-01-11", 900_000, 630_000, 10)
        TourService.create_schedule(tour_id, "2027-02-10", "2027-02-11", 950_000, 665_000, 10)

        synced = TourService.sync_schedule_prices(tour_id, 2_000_000)
        assert synced == 2

        rows = execute_query(
            "SELECT adult_price, child_price FROM tour_schedules WHERE tour_id = ?;",
            (tour_id,),
            fetch_all=True,
        )
        assert len(rows) == 2
        for s in rows:
            assert float(s["adult_price"]) == 2_000_000
            assert float(s["child_price"]) == 1_400_000  # 70%
    finally:
        with get_db() as conn:
            conn.execute("DELETE FROM guide_assignments WHERE schedule_id IN (SELECT id FROM tour_schedules WHERE tour_id = ?);", (tour_id,))
            conn.execute("DELETE FROM tour_expenses WHERE schedule_id IN (SELECT id FROM tour_schedules WHERE tour_id = ?);", (tour_id,))
            conn.execute("DELETE FROM bookings WHERE schedule_id IN (SELECT id FROM tour_schedules WHERE tour_id = ?);", (tour_id,))
            conn.execute("DELETE FROM tour_schedules WHERE tour_id = ?;", (tour_id,))
            conn.execute("DELETE FROM tours WHERE id = ?;", (tour_id,))


def test_occupancy_rates_include_price_and_title():
    """Bảng đợt khởi hành admin có đủ giá NL/TE và tên tour JOIN đúng từ bảng tours."""
    rows = AnalyticsService.get_occupancy_rates()
    assert rows
    for s in rows:
        assert "adult_price" in s and "child_price" in s
        assert s["tour_title"]

    first = rows[0]
    expected_title = execute_query(
        """SELECT t.title FROM tour_schedules s
           JOIN tours t ON s.tour_id = t.id WHERE s.id = ?;""",
        (first["id"],),
        fetch_one=True,
    )
    assert first["tour_title"] == expected_title["title"]


def test_update_schedule_derives_available_seats_from_active_bookings(client):
    """Editing a schedule cannot overwrite availability reserved by bookings."""
    tour_id = TourService.create_tour(
        destination_id=1,
        title="Tour Kiem Tra Dong Bo Cho",
        description="Tour dùng để kiểm tra số chỗ còn lại luôn được tính từ booking.",
        duration_days=2,
        duration_nights=1,
        base_price=1_500_000,
        transportation="Xe test",
        itinerary_text="Ngày 1: Test",
        image_url="",
    )
    try:
        schedule_id = TourService.create_schedule(
            tour_id, "2027-03-10", "2027-03-11", 1_500_000, 1_050_000, 8
        )
        booking = BookingService.create_booking(
            user_id=5,
            schedule_id=schedule_id,
            customer_name="Khách Đồng Bộ Chỗ",
            customer_email="seat-sync@test.com",
            customer_phone="0912345678",
            num_adults=2,
            num_children=1,
        )
        assert booking is not None
        confirmed_booking = BookingService.create_booking(
            user_id=5,
            schedule_id=schedule_id,
            customer_name="Khách Xác Nhận Chỗ",
            customer_email="confirmed-seat-sync@test.com",
            customer_phone="0987654321",
            num_adults=2,
            num_children=0,
        )
        assert confirmed_booking is not None
        BookingService.update_booking_status(confirmed_booking["id"], "CONFIRMED")

        # The endpoint must ignore a forged client-side available_seats value.
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Quản Trị Viên"
            sess["role"] = "ADMIN"
        response = client.post(
            f"/admin/schedules/{schedule_id}/edit",
            data={
                "departure_date": "2027-03-10",
                "return_date": "2027-03-11",
                "adult_price": "1600000",
                "child_price": "1120000",
                "total_seats": "10",
                "available_seats": "9999",  # ignored: no longer part of the server contract
                "status": "OPEN",
            },
        )
        assert response.status_code == 302
        updated = TourService.get_schedule_by_id(schedule_id)
        assert updated is not None
        assert updated["total_seats"] == 10
        assert updated["available_seats"] == 5  # 10 - (3 PENDING + 2 CONFIRMED)
        assert updated["status"] == "OPEN"

        with pytest.raises(ValueError, match="5 chỗ đã được giữ"):
            TourService.update_schedule(
                schedule_id=schedule_id,
                departure_date="2027-03-10",
                return_date="2027-03-11",
                adult_price=1_600_000,
                child_price=1_120_000,
                total_seats=4,
                status="OPEN",
            )
        unchanged = TourService.get_schedule_by_id(schedule_id)
        assert unchanged is not None
        assert unchanged["total_seats"] == 10
        assert unchanged["available_seats"] == 5
    finally:
        with get_db() as conn:
            conn.execute("DELETE FROM bookings WHERE schedule_id IN (SELECT id FROM tour_schedules WHERE tour_id = ?);", (tour_id,))
            conn.execute("DELETE FROM tour_schedules WHERE tour_id = ?;", (tour_id,))
            conn.execute("DELETE FROM tours WHERE id = ?;", (tour_id,))