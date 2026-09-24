"""
Image upload tests for the admin forms (file upload + paste endpoint).
Covers: successful upload, invalid file rejection, RBAC, and creating a tour
with an uploaded image file.
"""

import io
from pathlib import Path

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads"


def _login_as(client, user_id, name, role):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = name
        sess["role"] = role


def _cleanup(url):
    """Xóa file ảnh đã upload trong lúc test (nếu có)."""
    if url and url.startswith("/static/uploads/"):
        path = UPLOAD_DIR / url.rsplit("/", 1)[-1]
        if path.exists():
            path.unlink()


def test_upload_image_success(client):
    """ADMIN upload ảnh hợp lệ -> 200, trả URL /static/uploads/ và file tồn tại."""
    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    resp = client.post(
        "/admin/upload-image",
        data={"file": (io.BytesIO(b"fake-image-bytes"), "anh-moi.png")},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["url"].startswith("/static/uploads/")
    assert data["url"].endswith(".png")
    try:
        assert (UPLOAD_DIR / data["url"].rsplit("/", 1)[-1]).exists()
    finally:
        _cleanup(data["url"])


def test_upload_rejects_invalid_extension(client):
    """File không phải ảnh (sai đuôi) -> 400 với thông báo lỗi."""
    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    resp = client.post(
        "/admin/upload-image",
        data={"file": (io.BytesIO(b"MZ executable"), "script.exe")},
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["ok"] is False
    assert "hợp lệ" in data["error"]


def test_upload_requires_login(client):
    """Chưa đăng nhập -> redirect về /login (không upload được)."""
    resp = client.post(
        "/admin/upload-image",
        data={"file": (io.BytesIO(b"x"), "a.png")},
    )
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_upload_forbidden_for_customer(client):
    """CUSTOMER không có quyền upload ảnh -> redirect (302), không phải /login."""
    _login_as(client, 5, "Khách Hàng", "CUSTOMER")
    resp = client.post(
        "/admin/upload-image",
        data={"file": (io.BytesIO(b"x"), "a.png")},
    )
    assert resp.status_code == 302
    assert "/login" not in resp.headers["Location"]


def test_create_tour_with_file_upload(client):
    """Form Thêm Tour với file ảnh -> tour được tạo, image_url trỏ tới /static/uploads/."""
    _login_as(client, 1, "Quản Trị Viên", "ADMIN")
    resp = client.post(
        "/admin/tours",
        data={
            "destination_id": "1",
            "title": "Tour Test Upload Anh",
            "description": "Mô tả cho test upload ảnh",
            "duration_days": "2",
            "duration_nights": "1",
            "base_price": "1500000",
            "transportation": "Xe test",
            "itinerary_text": "Ngày 1: Test upload",
            "image_url": "",
            "image_file": (io.BytesIO(b"png-bytes-for-tour"), "tour-anh.png"),
        },
    )
    assert resp.status_code == 302  # redirect sau khi tạo thành công

    from database.db import get_db

    with get_db() as conn:
        row = conn.execute(
            "SELECT id, image_url FROM tours WHERE title = ?;",
            ("Tour Test Upload Anh",),
        ).fetchone()
        assert row is not None
        tour_id, image_url = row["id"], row["image_url"]
        assert image_url.startswith("/static/uploads/")
        # Dọn dẹp dữ liệu test
        conn.execute("DELETE FROM tours WHERE id = ?;", (tour_id,))
    _cleanup(image_url)