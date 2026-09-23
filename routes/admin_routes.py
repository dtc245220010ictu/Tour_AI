"""
Admin, Operations, and Staff Management Routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth_routes import roles_required
from services.analytics_service import AnalyticsService
from services.tour_service import TourService
from services.booking_service import BookingService
from services.feedback_service import FeedbackService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@roles_required("ADMIN", "STAFF", "ACCOUNTANT")
def dashboard():
    stats = AnalyticsService.get_dashboard_stats()
    top_tours = AnalyticsService.get_top_selling_tours(limit=5)
    occupancy_rates = AnalyticsService.get_occupancy_rates()
    recent_bookings = BookingService.get_all_bookings()[:8]

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        top_tours=top_tours,
        occupancy_rates=occupancy_rates,
        recent_bookings=recent_bookings
    )

@admin_bp.route("/tours", methods=["GET", "POST"])
@roles_required("ADMIN", "STAFF")
def manage_tours():
    if request.method == "POST":
        destination_id = request.form.get("destination_id", type=int)
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        duration_days = request.form.get("duration_days", 1, type=int)
        duration_nights = request.form.get("duration_nights", 0, type=int)
        base_price = request.form.get("base_price", 0, type=float)
        transportation = request.form.get("transportation", "Xe du lịch").strip()
        itinerary_text = request.form.get("itinerary_text", "").strip()
        image_url = request.form.get("image_url", "").strip()

        try:
            TourService.create_tour(
                destination_id=destination_id,
                title=title,
                description=description,
                duration_days=duration_days,
                duration_nights=duration_nights,
                base_price=base_price,
                transportation=transportation,
                itinerary_text=itinerary_text,
                image_url=image_url
            )
            flash("Đã thêm tour mới thành công!", "success")
            return redirect(url_for("admin.manage_tours"))
        except Exception as e:
            flash(f"Lỗi khi thêm tour: {str(e)}", "danger")

    destinations = TourService.get_all_destinations()
    tours = TourService.get_tours(limit=100)
    return render_template("admin/tours_manage.html", destinations=destinations, tours=tours)

@admin_bp.route("/tours/<int:tour_id>/delete", methods=["POST"])
@roles_required("ADMIN")
def delete_tour(tour_id):
    TourService.delete_tour(tour_id)
    flash("Đã xóa tour thành công.", "info")
    return redirect(url_for("admin.manage_tours"))

@admin_bp.route("/schedules", methods=["GET", "POST"])
@roles_required("ADMIN", "STAFF")
def manage_schedules():
    if request.method == "POST":
        tour_id = request.form.get("tour_id", type=int)
        departure_date = request.form.get("departure_date", "")
        return_date = request.form.get("return_date", "")
        adult_price = request.form.get("adult_price", 0, type=float)
        child_price = request.form.get("child_price", 0, type=float)
        total_seats = request.form.get("total_seats", 20, type=int)

        try:
            TourService.create_schedule(tour_id, departure_date, return_date, adult_price, child_price, total_seats)
            flash("Đã thêm lịch khởi hành mới thành công!", "success")
            return redirect(url_for("admin.manage_schedules"))
        except Exception as e:
            flash(f"Lỗi khi tạo lịch trình: {str(e)}", "danger")

    tours = TourService.get_tours(limit=100)
    occupancy_rates = AnalyticsService.get_occupancy_rates()
    return render_template("admin/schedules_manage.html", tours=tours, schedules=occupancy_rates)

@admin_bp.route("/bookings")
@roles_required("ADMIN", "STAFF", "ACCOUNTANT")
def manage_bookings():
    status = request.args.get("status")
    bookings = BookingService.get_all_bookings(status=status)
    return render_template("admin/bookings_manage.html", bookings=bookings, current_status=status)

@admin_bp.route("/bookings/<int:booking_id>/status", methods=["POST"])
@roles_required("ADMIN", "STAFF", "ACCOUNTANT")
def update_booking_status(booking_id):
    new_status = request.form.get("status")
    try:
        BookingService.update_booking_status(booking_id, new_status)
        flash("Đã cập nhật trạng thái đơn đặt tour.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_bookings"))

@admin_bp.route("/feedbacks")
@roles_required("ADMIN", "STAFF")
def manage_feedbacks():
    feedbacks = FeedbackService.get_all_feedbacks()
    return render_template("admin/feedbacks_manage.html", feedbacks=feedbacks)

