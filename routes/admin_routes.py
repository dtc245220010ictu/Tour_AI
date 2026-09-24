"""
Admin, Operations, and Staff Management Routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from routes.auth_routes import roles_required
from services.analytics_service import AnalyticsService
from services.auth_service import AuthService
from services.image_upload_service import ImageUploadService
from services.tour_service import TourService
from services.booking_service import BookingService
from services.feedback_service import FeedbackService
from services.guide_service import GuideService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@roles_required("ADMIN", "ACCOUNTANT")
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

def _resolve_image_url():
    """Ưu tiên file ảnh upload (image_file); fallback sang ô URL (image_url)."""
    file = request.files.get("image_file")
    if file and file.filename:
        return ImageUploadService.save(file)
    return request.form.get("image_url", "").strip()


@admin_bp.route("/upload-image", methods=["POST"])
@roles_required("ADMIN", "STAFF")
def upload_image():
    """AJAX endpoint: nhận ảnh dán (Ctrl+V) hoặc chọn file từ form admin."""
    file = request.files.get("file") or request.files.get("image_file")
    if not file or not file.filename:
        return jsonify({"ok": False, "error": "Không có file ảnh được chọn."}), 400
    try:
        return jsonify({"ok": True, "url": ImageUploadService.save(file)})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


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

        try:
            image_url = _resolve_image_url()
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("admin.manage_tours"))

        if destination_id is None:
            flash("Vui lòng chọn điểm đến cho tour.", "danger")
            return redirect(url_for("admin.manage_tours"))

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
# CN2: STAFF không có quyền Xóa tour -> chỉ ADMIN được xóa.
@roles_required("ADMIN")
def delete_tour(tour_id):
    TourService.delete_tour(tour_id)
    flash("Đã xóa tour thành công.", "info")
    return redirect(url_for("admin.manage_tours"))


@admin_bp.route("/tours/<int:tour_id>/edit", methods=["GET", "POST"])
@roles_required("ADMIN", "STAFF")
def edit_tour(tour_id):
    tour = TourService.get_tour_by_id(tour_id)
    if not tour:
        flash("Không tìm thấy tour cần sửa.", "danger")
        return redirect(url_for("admin.manage_tours"))

    if request.method == "POST":
        destination_id = request.form.get("destination_id", type=int)
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        duration_days = request.form.get("duration_days", 1, type=int)
        duration_nights = request.form.get("duration_nights", 0, type=int)
        base_price = request.form.get("base_price", 0, type=float)
        transportation = request.form.get("transportation", "Xe du lịch").strip()
        itinerary_text = request.form.get("itinerary_text", "").strip()
        is_active = 1 if request.form.get("is_active") == "1" else 0

        if not title or not description or not destination_id:
            flash("Vui lòng điền đầy đủ các trường bắt buộc.", "danger")
        else:
            try:
                image_url = _resolve_image_url()
                TourService.update_tour(
                    tour_id=tour_id,
                    destination_id=destination_id,
                    title=title,
                    description=description,
                    duration_days=duration_days,
                    duration_nights=duration_nights,
                    base_price=base_price,
                    transportation=transportation,
                    itinerary_text=itinerary_text,
                    image_url=image_url,
                    is_active=is_active
                )
                synced = 0
                if request.form.get("sync_schedule_prices") == "1":
                    synced = TourService.sync_schedule_prices(tour_id, base_price)
                if synced:
                    flash(f"Đã cập nhật tour & đồng bộ giá cho {synced} lịch khởi hành!", "success")
                else:
                    flash("Đã cập nhật tour thành công!", "success")
                return redirect(url_for("admin.manage_tours"))
            except ValueError as e:
                flash(str(e), "danger")
            except Exception as e:
                flash(f"Lỗi khi cập nhật tour: {str(e)}", "danger")

    destinations = TourService.get_all_destinations()
    return render_template("admin/tour_edit.html", tour=tour, destinations=destinations)

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

        if tour_id is None:
            flash("Vui lòng chọn tour cho lịch khởi hành.", "danger")
            return redirect(url_for("admin.manage_schedules"))

        try:
            TourService.create_schedule(tour_id, departure_date, return_date, adult_price, child_price, total_seats)
            flash("Đã thêm lịch khởi hành mới thành công!", "success")
            return redirect(url_for("admin.manage_schedules"))
        except Exception as e:
            flash(f"Lỗi khi tạo lịch trình: {str(e)}", "danger")

    tours = TourService.get_tours(limit=100)
    occupancy_rates = AnalyticsService.get_occupancy_rates()
    return render_template("admin/schedules_manage.html", tours=tours, schedules=occupancy_rates)


@admin_bp.route("/schedules/<int:schedule_id>/edit", methods=["GET", "POST"])
@roles_required("ADMIN", "STAFF")
def edit_schedule(schedule_id):
    schedule = TourService.get_schedule_by_id(schedule_id)
    if not schedule:
        flash("Không tìm thấy lịch khởi hành.", "danger")
        return redirect(url_for("admin.manage_schedules"))

    if request.method == "POST":
        try:
            TourService.update_schedule(
                schedule_id=schedule_id,
                departure_date=request.form.get("departure_date", ""),
                return_date=request.form.get("return_date", ""),
                adult_price=request.form.get("adult_price", 0, type=float),
                child_price=request.form.get("child_price", 0, type=float),
                total_seats=request.form.get("total_seats", 20, type=int),
                available_seats=request.form.get("available_seats", 0, type=int),
                status=request.form.get("status", "OPEN")
            )
            flash("Đã cập nhật lịch khởi hành & số chỗ thành công!", "success")
            return redirect(url_for("admin.manage_schedules"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("admin/schedule_edit.html", schedule=schedule)


@admin_bp.route("/schedules/<int:schedule_id>/delete", methods=["POST"])
# CN3: STAFF không có quyền Xóa lịch khởi hành -> chỉ ADMIN được xóa.
@roles_required("ADMIN")
def delete_schedule(schedule_id):
    try:
        TourService.delete_schedule(schedule_id)
        flash("Đã xóa lịch khởi hành.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_schedules"))


# ==============================================================
# Quản lý điểm đến
# - ADMIN: Xem / Thêm / Sửa / Xóa
# - STAFF: Xem / Thêm / Sửa (Xóa: Không có quyền - theo CN2)
# ==============================================================
@admin_bp.route("/destinations", methods=["GET", "POST"])
@roles_required("ADMIN", "STAFF")
def manage_destinations():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        region = request.form.get("region", "").strip()
        description = request.form.get("description", "").strip()
        try:
            image_url = _resolve_image_url()
            if not name or not region:
                raise ValueError("Tên điểm đến và khu vực là bắt buộc.")
            TourService.create_destination(name, region, description, image_url)
            flash("Đã thêm điểm đến mới thành công!", "success")
            return redirect(url_for("admin.manage_destinations"))
        except Exception as e:
            flash(f"Lỗi khi thêm điểm đến: {str(e)}", "danger")

    destinations = TourService.get_all_destinations()
    return render_template("admin/destinations_manage.html", destinations=destinations)


@admin_bp.route("/destinations/<int:dest_id>/edit", methods=["GET", "POST"])
@roles_required("ADMIN", "STAFF")
def edit_destination(dest_id):
    destination = TourService.get_destination_by_id(dest_id)
    if not destination:
        flash("Không tìm thấy điểm đến.", "danger")
        return redirect(url_for("admin.manage_destinations"))

    if request.method == "POST":
        try:
            TourService.update_destination(
                dest_id=dest_id,
                name=request.form.get("name", ""),
                region=request.form.get("region", ""),
                description=request.form.get("description", ""),
                image_url=_resolve_image_url()
            )
            flash("Đã cập nhật điểm đến thành công!", "success")
            return redirect(url_for("admin.manage_destinations"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("admin/destination_edit.html", destination=destination)


@admin_bp.route("/destinations/<int:dest_id>/delete", methods=["POST"])
# CN2: STAFF không có quyền Xóa điểm đến -> chỉ ADMIN được xóa.
@roles_required("ADMIN")
def delete_destination(dest_id):
    try:
        TourService.delete_destination(dest_id)
        flash("Đã xóa điểm đến.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_destinations"))


# ==============================================================
# Quản lý khách hàng
# - ADMIN: Xem / Thêm / Sửa / Xóa
# - STAFF: Chỉ được Xem (không thêm/sửa/xóa)
# ==============================================================
@admin_bp.route("/customers")
@roles_required("ADMIN", "STAFF")
def manage_customers():
    customers = AuthService.get_all_customers()
    # Hỗ trợ chế độ sửa: /admin/customers?edit=<user_id>
    edit_id = request.args.get("edit", type=int)
    edit_customer = AuthService.get_customer_by_id(edit_id) if edit_id else None
    return render_template(
        "admin/customers_manage.html",
        customers=customers,
        edit_customer=edit_customer,
        can_manage=(session.get("role") == "ADMIN")
    )


@admin_bp.route("/customers/create", methods=["POST"])
@roles_required("ADMIN")
def create_customer():
    try:
        AuthService.register_user(
            email=request.form.get("email", ""),
            password=request.form.get("password", ""),
            full_name=request.form.get("full_name", ""),
            phone=request.form.get("phone", ""),
            role="CUSTOMER"
        )
        flash("Đã thêm khách hàng mới thành công!", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_customers"))


@admin_bp.route("/customers/<int:user_id>/update", methods=["POST"])
@roles_required("ADMIN")
def update_customer(user_id):
    try:
        AuthService.update_customer(
            user_id=user_id,
            full_name=request.form.get("full_name", ""),
            phone=request.form.get("phone", ""),
            email=request.form.get("email", ""),
            password=request.form.get("password", "")
        )
        flash("Đã cập nhật thông tin khách hàng thành công!", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_customers"))


@admin_bp.route("/customers/<int:user_id>/delete", methods=["POST"])
@roles_required("ADMIN")
def delete_customer(user_id):
    try:
        AuthService.delete_customer(user_id)
        flash("Đã xóa khách hàng.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_customers"))


@admin_bp.route("/bookings")
@roles_required("ADMIN", "STAFF")
def manage_bookings():
    status = request.args.get("status")
    bookings = BookingService.get_all_bookings(status=status)
    return render_template("admin/bookings_manage.html", bookings=bookings, current_status=status)

@admin_bp.route("/bookings/<int:booking_id>/status", methods=["POST"])
@roles_required("ADMIN", "STAFF")
def update_booking_status(booking_id):
    new_status = request.form.get("status", "")
    try:
        BookingService.update_booking_status(booking_id, new_status)
        flash("Đã cập nhật trạng thái đơn đặt tour.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_bookings"))

@admin_bp.route("/feedbacks")
@roles_required("ADMIN")
def manage_feedbacks():
    feedbacks = FeedbackService.get_all_feedbacks()
    return render_template("admin/feedbacks_manage.html", feedbacks=feedbacks)


# ==============================================================
# CN6: Quản lý hướng dẫn viên & phân công tour
# - ADMIN: toàn quyền (thêm/sửa/xóa HDV, phân công)
# - STAFF / ACCOUNTANT / GUIDE / CUSTOMER: Không có quyền
#   (KH xem HDV qua trang chi tiết tour; GUIDE xem bảng phân công qua /guide/schedule)
# ==============================================================
@admin_bp.route("/guides", methods=["GET", "POST"])
@roles_required("ADMIN")
def manage_guides():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        languages = request.form.get("languages", "").strip()
        experience_years = request.form.get("experience_years", 1, type=int)
        bio = request.form.get("bio", "").strip()
        try:
            GuideService.create_guide(full_name, phone, email, languages, experience_years, bio)
            flash("Đã thêm mới hồ sơ hướng dẫn viên!", "success")
            return redirect(url_for("admin.manage_guides"))
        except ValueError as e:
            flash(str(e), "danger")

    guides = GuideService.get_all_guides()
    schedules = GuideService.get_all_schedules()
    assignments = GuideService.get_assignments()
    return render_template(
        "admin/guides_manage.html",
        guides=guides, schedules=schedules, assignments=assignments,
        can_manage=(session.get("role") == "ADMIN")
    )


@admin_bp.route("/guides/<int:guide_id>/delete", methods=["POST"])
@roles_required("ADMIN")
def delete_guide(guide_id):
    try:
        GuideService.delete_guide(guide_id)
        flash("Đã xóa (ngừng hoạt động) hồ sơ hướng dẫn viên.", "info")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_guides"))


@admin_bp.route("/guides/assign", methods=["POST"])
@roles_required("ADMIN")
def assign_guide():
    schedule_id = request.form.get("schedule_id", type=int)
    guide_id = request.form.get("guide_id", type=int)
    role_in_tour = request.form.get("role_in_tour", "LEAD_GUIDE").strip()
    notes = request.form.get("notes", "").strip()

    if schedule_id is None or guide_id is None:
        flash("Vui lòng chọn đầy đủ lịch khởi hành và hướng dẫn viên.", "danger")
        return redirect(url_for("admin.manage_guides"))

    try:
        GuideService.assign_guide(schedule_id, guide_id, role_in_tour, notes)
        flash("Đã phân công hướng dẫn viên cho đợt khởi hành!", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("admin.manage_guides"))


@admin_bp.route("/guides/assignments/<int:assignment_id>/delete", methods=["POST"])
@roles_required("ADMIN")
def delete_guide_assignment(assignment_id):
    GuideService.remove_assignment(assignment_id)
    flash("Đã hủy phân công hướng dẫn viên.", "info")
    return redirect(url_for("admin.manage_guides"))

