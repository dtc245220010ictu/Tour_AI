"""
Unit tests for Booking and Capacity Management.
Verifies atomic seat deduction, overbooking prevention, and cancellation seat recovery.
"""

import pytest
from services.booking_service import BookingService, OverbookingError
from services.tour_service import TourService

def test_booking_successful_and_seats_deducted():
    # Schedule 1 (Hạ Long) initially has available_seats = 15
    schedule_before = TourService.get_schedule_by_id(1)
    assert schedule_before is not None
    initial_seats = schedule_before["available_seats"]

    # Book for 2 adults and 1 child (3 seats total)
    booking = BookingService.create_booking(
        user_id=5, # Customer user
        schedule_id=1,
        customer_name="Nguyễn Văn Test",
        customer_email="test@example.com",
        customer_phone="0911222333",
        num_adults=2,
        num_children=1,
        notes="Ghi chú kiểm thử"
    )

    assert booking is not None
    assert booking["booking_code"].startswith("BK-")
    assert booking["status"] == "PENDING"
    assert booking["num_adults"] == 2
    assert booking["num_children"] == 1

    # Verify seats were accurately deducted in database
    schedule_after = TourService.get_schedule_by_id(1)
    assert schedule_after is not None
    assert schedule_after["available_seats"] == initial_seats - 3

def test_overbooking_prevention_rejected():
    """
    CRITICAL BUSINESS CONSTRAINT TEST:
    Attempting to book more seats than available MUST raise OverbookingError!
    """
    schedule = TourService.get_schedule_by_id(1)
    assert schedule is not None
    available = schedule["available_seats"]

    # Attempt to book available + 5 seats
    with pytest.raises(OverbookingError) as exc_info:
        BookingService.create_booking(
            user_id=5,
            schedule_id=1,
            customer_name="Khách Hàng Quá Tải",
            customer_email="overbook@example.com",
            customer_phone="0999888777",
            num_adults=available + 5,
            num_children=0
        )

    assert "chỗ trống" in str(exc_info.value)

def test_cancellation_restores_seats():
    """
    Verifies that cancelling a booking releases the reserved seats back into the schedule.
    """
    schedule_before = TourService.get_schedule_by_id(1)
    assert schedule_before is not None
    seats_before = schedule_before["available_seats"]

    # 1. Book 2 seats
    booking = BookingService.create_booking(
        user_id=5,
        schedule_id=1,
        customer_name="Khách Test Hủy",
        customer_email="cancel@example.com",
        customer_phone="0911333444",
        num_adults=2,
        num_children=0
    )
    assert booking is not None
    mid_cancel = TourService.get_schedule_by_id(1)
    assert mid_cancel is not None
    assert mid_cancel["available_seats"] == seats_before - 2

    # 2. Cancel booking
    success = BookingService.cancel_booking(booking["id"], user_id=5)
    assert success is True

    # 3. Verify booking status and seat restoration
    updated_booking = BookingService.get_booking_by_id(booking["id"])
    assert updated_booking is not None
    assert updated_booking["status"] == "CANCELLED"

    schedule_after_cancel = TourService.get_schedule_by_id(1)
    assert schedule_after_cancel is not None
    assert schedule_after_cancel["available_seats"] == seats_before


def test_customer_self_cancels_confirmed_booking(client):
    """
    AC-005 / US-010: Khách hàng tự hủy đơn CONFIRMED của chính mình
    mà không cần thông qua nhân viên tư vấn.
    """
    seats_before = TourService.get_schedule_by_id(1)
    assert seats_before is not None

    booking = BookingService.create_booking(
        user_id=5,
        schedule_id=1,
        customer_name="Khách Tự Hủy",
        customer_email="selfcancel@example.com",
        customer_phone="0914444555",
        num_adults=2,
        num_children=0,
    )
    assert booking is not None

    # Nhân viên/kinh toán đã duyệt đơn -> CONFIRMED
    BookingService.update_booking_status(booking["id"], "CONFIRMED")

    with client.session_transaction() as sess:
        sess["user_id"] = 5
        sess["user_name"] = "Khách Hàng"
        sess["role"] = "CUSTOMER"

    resp = client.post(f"/booking/{booking['id']}/cancel")
    assert resp.status_code == 302
    assert "my-bookings" in resp.headers["Location"]

    updated = BookingService.get_booking_by_id(booking["id"])
    assert updated is not None
    assert updated["status"] == "CANCELLED"

    # Số chỗ được hoàn trả về như ban đầu
    schedule_after = TourService.get_schedule_by_id(1)
    assert schedule_after is not None
    assert schedule_after["available_seats"] == seats_before["available_seats"]


def test_customer_cancel_guardrails(client):
    """Khách chỉ hủy được đơn của mình và không hủy được đơn đã hoàn thành."""
    seats_before = TourService.get_schedule_by_id(1)
    assert seats_before is not None

    with client.session_transaction() as sess:
        sess["user_id"] = 5
        sess["user_name"] = "Khách Hàng"
        sess["role"] = "CUSTOMER"

    # (a) Không hủy được đơn của người khác -> bị chặn, đơn giữ nguyên PENDING
    other_booking = BookingService.create_booking(
        user_id=4,
        schedule_id=1,
        customer_name="Đơn Của Người Khác",
        customer_email="other_owner_cancel@example.com",
        customer_phone="0916666777",
        num_adults=1,
        num_children=0,
    )
    assert other_booking is not None
    resp = client.post(f"/booking/{other_booking['id']}/cancel")
    assert resp.status_code == 302
    assert "my-bookings" not in resp.headers["Location"]
    still = BookingService.get_booking_by_id(other_booking["id"])
    assert still is not None
    assert still["status"] == "PENDING"

    # (b) Không hủy được đơn đã COMPLETED
    done_booking = BookingService.create_booking(
        user_id=5,
        schedule_id=1,
        customer_name="Khách Đã Đi Tour",
        customer_email="completed_tour@example.com",
        customer_phone="0918888999",
        num_adults=1,
        num_children=0,
    )
    assert done_booking is not None
    BookingService.update_booking_status(done_booking["id"], "COMPLETED")
    resp = client.post(f"/booking/{done_booking['id']}/cancel")
    assert resp.status_code == 302
    still = BookingService.get_booking_by_id(done_booking["id"])
    assert still is not None
    assert still["status"] == "COMPLETED"

    # Dọn dẹp: hoàn trả chỗ để không ảnh hưởng test khác (net = 0 chỗ)
    BookingService.cancel_booking(other_booking["id"])
    BookingService.update_booking_status(done_booking["id"], "PENDING")
    BookingService.cancel_booking(done_booking["id"])

    seats_final = TourService.get_schedule_by_id(1)
    assert seats_final is not None
    assert seats_final["available_seats"] == seats_before["available_seats"]

