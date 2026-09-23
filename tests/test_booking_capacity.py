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
    assert schedule_after["available_seats"] == initial_seats - 3

def test_overbooking_prevention_rejected():
    """
    CRITICAL BUSINESS CONSTRAINT TEST:
    Attempting to book more seats than available MUST raise OverbookingError!
    """
    schedule = TourService.get_schedule_by_id(1)
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
    assert TourService.get_schedule_by_id(1)["available_seats"] == seats_before - 2

    # 2. Cancel booking
    success = BookingService.cancel_booking(booking["id"], user_id=5)
    assert success is True

    # 3. Verify booking status and seat restoration
    updated_booking = BookingService.get_booking_by_id(booking["id"])
    assert updated_booking["status"] == "CANCELLED"

    schedule_after_cancel = TourService.get_schedule_by_id(1)
    assert schedule_after_cancel["available_seats"] == seats_before

