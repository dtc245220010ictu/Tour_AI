"""
Unit tests for Authentication and User Management.
Verifies registration, password hashing, and login credentials.
"""

import pytest
from services.auth_service import AuthService

def test_register_and_login_success():
    email = "newuser@tourai.vn"
    user = AuthService.register_user(
        email=email,
        password="securepassword123",
        full_name="Người Dùng Mới",
        phone="0988776655"
    )

    assert user is not None
    assert user["email"] == email
    assert user["role"] == "CUSTOMER"

    # Login with correct credentials
    logged_in_user = AuthService.login_user(email, "securepassword123")
    assert logged_in_user is not None
    assert logged_in_user["id"] == user["id"]

def test_login_invalid_password():
    user = AuthService.login_user("admin@tourai.vn", "wrong_password_xyz")
    assert user is None

def test_register_duplicate_email_fails():
    with pytest.raises(ValueError) as exc:
        AuthService.register_user(
            email="admin@tourai.vn", # Already in seed data
            password="somepassword",
            full_name="Admin Giả Mạo",
            phone="0911222333"
        )
    assert "đã được sử dụng" in str(exc.value)

def test_login_page_has_quick_login_for_all_roles(client):
    """Trang đăng nhập hiển thị khu vực đăng nhập nhanh cho đủ 5 vai trò demo."""
    resp = client.get("/login")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")

    assert "Đăng nhập nhanh" in html
    assert "quick-login-btn" in html
    for email in [
        "admin@tourai.vn",
        "staff@tourai.vn",
        "accountant@tourai.vn",
        "guide@tourai.vn",
        "customer@tourai.vn",
    ]:
        assert email in html

def test_quick_login_accountant_flow(client):
    """
    Mô phỏng thao tác của nút đăng nhập nhanh: submit form /login với tài khoản kế toán.
    Đảm bảo đăng nhập thành công và truy cập được phân hệ kế toán.
    """
    resp = client.post(
        "/login",
        data={"email": "accountant@tourai.vn", "password": "accountant123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302

    with client.session_transaction() as sess:
        assert sess["role"] == "ACCOUNTANT"

    resp = client.get("/accounting/dashboard")
    assert resp.status_code == 200

def test_quick_login_hidden_when_disabled(monkeypatch):
    """Khi ENABLE_DEMO_QUICK_LOGIN=0, khu vực đăng nhập nhanh không được hiển thị."""
    monkeypatch.setenv("ENABLE_DEMO_QUICK_LOGIN", "0")

    from app import create_app
    local_app = create_app()
    local_app.config.update({"TESTING": True, "SECRET_KEY": "test_secret_key_123"})
    local_client = local_app.test_client()

    resp = local_client.get("/login")
    assert resp.status_code == 200
    assert "Đăng nhập nhanh" not in resp.data.decode("utf-8")


