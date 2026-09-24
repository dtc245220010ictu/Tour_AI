"""
Data-consistency tests: tour name and ticket prices must stay linked across pages.
Guards against mismatch between tours.base_price, tour_schedules prices,
bookings.total_amount and the tour title JOINed everywhere.
"""

from database.db import execute_query, get_db
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