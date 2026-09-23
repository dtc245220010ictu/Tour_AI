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

