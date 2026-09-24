"""
Authentication Routes and Access Control Decorators.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập để tiếp tục.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Vui lòng đăng nhập để tiếp tục.", "warning")
                return redirect(url_for("auth.login", next=request.url))
            user_role = session.get("role", "CUSTOMER")
            if user_role not in roles:
                flash("Bạn không có quyền truy cập vào chức năng này.", "danger")
                return redirect(url_for("tour.index"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("tour.index"))
        
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()

        try:
            AuthService.register_user(email, password, full_name, phone, role="CUSTOMER")
            flash("Đăng ký tài khoản thành công! Hãy đăng nhập để bắt đầu.", "success")
            return redirect(url_for("auth.login"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("tour.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = AuthService.login_user(email, password)
        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["user_email"] = user["email"]
            session["role"] = user["role"]

            flash(f"Chào mừng bạn trở lại, {user['full_name']}!", "success")
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)
            if user["role"] in ["ADMIN", "ACCOUNTANT"]:
                return redirect(url_for("admin.dashboard"))
            if user["role"] == "STAFF":
                # STAFF has no access to the statistics dashboard (Chức năng 8)
                return redirect(url_for("admin.manage_tours"))
            if user["role"] == "GUIDE":
                # GUIDE: trang riêng - bảng phân công nhiệm vụ (CN6, chỉ xem)
                return redirect(url_for("guide.schedule"))
            return redirect(url_for("tour.index"))
        else:
            flash("Email hoặc mật khẩu không chính xác. Vui lòng thử lại.", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất an toàn.", "info")
    return redirect(url_for("tour.index"))

