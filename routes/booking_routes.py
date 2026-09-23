"""
Booking, Checkout, and Order History Routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required
from services.tour_service import TourService
from services.booking_service import BookingService, OverbookingError
from services.payment_service import PaymentService

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/booking/new/<int:schedule_id>", methods=["GET", "POST"])
@login_required
def new_booking(schedule_id):
    schedule = TourService.get_schedule_by_id(schedule_id)
    if not schedule:
        flash("Không tìm thấy lịch khởi hành đã chọn.", "danger")
        return redirect(url_for("tour.catalog"))

    if schedule["status"] != "OPEN" or schedule["available_seats"] <= 0:
        flash("Lịch khởi hành này hiện đã hết chỗ. Vui lòng chọn ngày khác.", "warning")
        return redirect(url_for("tour.detail", slug=schedule["tour_slug"]))

    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        customer_email = request.form.get("customer_email", "").strip()
        customer_phone = request.form.get("customer_phone", "").strip()
        num_adults = request.form.get("num_adults", 1, type=int)
        num_children = request.form.get("num_children", 0, type=int)
        notes = request.form.get("notes", "").strip()

        try:
            booking = BookingService.create_booking(
                user_id=session["user_id"],
                schedule_id=schedule_id,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                num_adults=num_adults,
                num_children=num_children,
                notes=notes
            )
            flash("Đặt chỗ tour thành công! Vui lòng hoàn tất thanh toán để giữ chỗ.", "success")
            return redirect(url_for("booking.booking_success", booking_code=booking["booking_code"]))
        except OverbookingError as e:
            flash(str(e), "danger")
        except ValueError as e:
            flash(str(e), "warning")

    return render_template("booking.html", schedule=schedule)

@booking_bp.route("/booking/success/<booking_code>")
@login_required
def booking_success(booking_code):
    booking = BookingService.get_booking_by_code(booking_code)
    if not booking:
        flash("Không tìm thấy đơn đặt tour.", "danger")
        return redirect(url_for("tour.index"))

    payments = PaymentService.get_payments_by_booking(booking["id"])
    return render_template("booking_success.html", booking=booking, payments=payments)

@booking_bp.route("/booking/<int:booking_id>/pay", methods=["POST"])
@login_required
def pay_booking(booking_id):
    booking = BookingService.get_booking_by_id(booking_id)
    if not booking or (booking["user_id"] != session["user_id"] and session.get("role") not in ["ADMIN", "ACCOUNTANT"]):
        flash("Không tìm thấy đơn đặt tour hoặc bạn không có quyền.", "danger")
        return redirect(url_for("tour.index"))

    payment_method = request.form.get("payment_method", "BANK_TRANSFER")
    try:
        PaymentService.record_payment(
            booking_id=booking_id,
            amount=booking["total_amount"],
            payment_method=payment_method,
            transaction_id=f"TXN-{booking['booking_code']}"
        )
        flash("Xác nhận thanh toán thành công! Chúc quý khách có chuyến đi vui vẻ.", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("booking.booking_success", booking_code=booking["booking_code"]))

@booking_bp.route("/my-bookings")
@login_required
def my_bookings():
    bookings = BookingService.get_user_bookings(session["user_id"])
    return render_template("my_bookings.html", bookings=bookings)

@booking_bp.route("/booking/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    try:
        BookingService.cancel_booking(booking_id, user_id=session["user_id"])
        flash("Đã hủy đơn đặt tour thành công. Số chỗ trống đã được hoàn trả về hệ thống.", "info")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("booking.my_bookings"))

