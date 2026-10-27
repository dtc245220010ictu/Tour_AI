"""
Guide Assignment Board Routes (CN6).
GUIDE: xem bảng phân công của chính mình và của đồng nghiệp (read-only).
ADMIN: toàn quyền xem theo ma trận phân quyền.
STAFF / ACCOUNTANT / CUSTOMER: Không có quyền trên trang này.
"""

from flask import Blueprint, render_template
from routes.auth_routes import roles_required
from services.guide_service import GuideService

guide_bp = Blueprint("guide", __name__, url_prefix="/guide")


@guide_bp.route("/schedule")
@roles_required("GUIDE", "ADMIN")
def schedule():
    assignments = GuideService.get_assignments()
    return render_template(
        "guide/schedule.html",
        assignments=assignments,
        current_guide=None  # Bảng hiển thị toàn bộ (mình + đồng nghiệp) theo CN6
    )


@guide_bp.route("/customers")
@roles_required("GUIDE", "ADMIN")
def assigned_customers():
    """Danh sách khách theo các đoàn có phân công HDV, chỉ đọc."""
    customers = GuideService.get_assigned_group_customers()
    return render_template("guide/customers.html", customers=customers)
