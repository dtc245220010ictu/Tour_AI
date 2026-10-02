"""
Public Tour Catalog and Detail Routes.
"""

from flask import Blueprint, render_template, request, abort, session
from services.tour_service import TourService
from services.feedback_service import FeedbackService
from services.guide_service import GuideService

tour_bp = Blueprint("tour", __name__)

@tour_bp.route("/")
def index():
    destinations = TourService.get_all_destinations()
    featured_tours = TourService.get_tours(limit=6)
    return render_template("index.html", destinations=destinations, featured_tours=featured_tours)

@tour_bp.route("/tours")
def catalog():
    dest_id = request.args.get("destination_id", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    duration = request.args.get("duration", type=int)
    keyword = request.args.get("keyword", type=str)

    destinations = TourService.get_all_destinations()
    tours = TourService.get_tours(
        destination_id=dest_id,
        min_price=min_price,
        max_price=max_price,
        duration=duration,
        keyword=keyword,
        limit=50
    )

    return render_template(
        "tours.html",
        destinations=destinations,
        tours=tours,
        selected_dest=dest_id,
        selected_min_price=min_price,
        selected_max_price=max_price,
        selected_duration=duration,
        keyword=keyword or ""
    )

@tour_bp.route("/tours/<slug>")
def detail(slug):
    tour = TourService.get_tour_by_slug(slug)
    if not tour:
        abort(404)

    schedules = TourService.get_tour_schedules(tour["id"], only_open=True)
    postponed_schedules = TourService.get_postponed_schedules(tour["id"])
    feedbacks = FeedbackService.get_feedbacks_by_tour(tour["id"])
    guides = GuideService.get_guides_for_tour(tour["id"])

    # Calculate average rating
    avg_rating = 0
    if feedbacks:
        avg_rating = round(sum([f["rating"] for f in feedbacks]) / len(feedbacks), 1)

    # Bảng đánh giá chỉ mở khi khách đã HOÀN THÀNH chuyến đi của tour này
    # và chưa từng đánh giá đơn đó (mỗi đơn chỉ nhận 1 đánh giá).
    review_booking = None
    if session.get("user_id") and session.get("role") == "CUSTOMER":
        review_booking = FeedbackService.get_reviewable_booking(session["user_id"], tour["id"])

    return render_template(
        "tour_detail.html",
        tour=tour,
        schedules=schedules,
        postponed_schedules=postponed_schedules,
        feedbacks=feedbacks,
        avg_rating=avg_rating,
        guides=guides,
        review_booking=review_booking
    )

