"""
Image upload tests for the admin forms (file upload + paste endpoint).
Covers: successful upload, invalid file rejection, RBAC, and creating a tour
with an uploaded image file.
"""

import io
import re
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


def test_edit_form_image_field_accepts_relative_uploaded_url(client):
    """Ô ảnh trên form Sửa tour không dùng type=url: ảnh upload nội bộ (/static/uploads/...)
    là đường dẫn tương đối nên HTML5 type=url sẽ chặn submit và bắt người dùng nhập lại URL."""
    from database.db import get_db
    from services.tour_service import TourService

    tour_id = TourService.create_tour(
        destination_id=1,
        title="Tour Test Sua Anh Tuong Doi",
        description="Tour dùng để kiểm tra ô ảnh trên form sửa tour.",
        duration_days=2,
        duration_nights=1,
        base_price=1_000_000,
        transportation="Xe test",
        itinerary_text="Ngày 1: Test",
        image_url="/static/uploads/relative-image-test.png",
    )
    try:
        _login_as(client, 1, "Quản Trị Viên", "ADMIN")
        resp = client.get(f"/admin/tours/{tour_id}/edit")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8")
        match = re.search(r'<input[^>]*name="image_url"[^>]*>', html)
        assert match is not None
        tag = match.group(0)
        assert 'type="url"' not in tag
        assert "/static/uploads/relative-image-test.png" in tag

        # Bấm "Lưu thay đổi" với nguyên giá trị ảnh tương đối -> không bị mất ảnh
        resp = client.post(
            f"/admin/tours/{tour_id}/edit",
            data={
                "destination_id": "1",
                "title": "Tour Test Sua Anh Tuong Doi",
                "description": "Tour dùng để kiểm tra ô ảnh trên form sửa tour.",
                "duration_days": "2",
                "duration_nights": "1",
                "base_price": "1000000",
                "transportation": "Xe test",
                "itinerary_text": "Ngày 1: Test",
                "image_url": "/static/uploads/relative-image-test.png",
                "is_active": "1",
            },
        )
        assert resp.status_code == 302
        with get_db() as conn:
            saved = conn.execute(
                "SELECT image_url FROM tours WHERE id = ?;", (tour_id,)
            ).fetchone()
        assert saved["image_url"] == "/static/uploads/relative-image-test.png"
    finally:
        with get_db() as conn:
            conn.execute("DELETE FROM tour_schedules WHERE tour_id = ?;", (tour_id,))
            conn.execute("DELETE FROM tours WHERE id = ?;", (tour_id,))