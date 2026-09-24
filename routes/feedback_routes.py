"""
Feedback and Review Submission Routes.
"""

from flask import Blueprint, request, redirect, url_for, flash, session
from routes.auth_routes import roles_required
from services.feedback_service import FeedbackService
from services.tour_service import TourService

feedback_bp = Blueprint("feedback", __name__)

@feedback_bp.route("/feedback/new", methods=["POST"])
@roles_required("ADMIN", "CUSTOMER")
def submit_feedback():
    tour_id = request.form.get("tour_id", type=int)
    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()
    booking_id = request.form.get("booking_id", type=int)

    if tour_id is None or rating is None:
        flash("Vui lòng gửi đánh giá hợp lệ (chọn tour và số sao).", "danger")
        return redirect(url_for("tour.index"))

    tour = TourService.get_tour_by_id(tour_id)
    if not tour:
        flash("Không tìm thấy tour cần đánh giá.", "danger")
        return redirect(url_for("tour.index"))

    try:
        FeedbackService.create_feedback(
            user_id=session["user_id"],
            tour_id=tour_id,
            rating=rating,
            comment=comment,
            booking_id=booking_id
        )
        flash("Cảm ơn bạn đã gửi đánh giá phản hồi cho chuyến đi!", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("tour.detail", slug=tour["slug"]))

