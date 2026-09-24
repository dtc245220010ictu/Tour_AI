"""
Image upload service for admin forms (tours & destinations).
Validates uploaded images and stores them in static/uploads/ with a
unique filename, returning the public URL to save in the database.
"""

import uuid
from pathlib import Path

from werkzeug.datastructures import FileStorage

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class ImageUploadService:
    """Lưu file ảnh tải lên (chọn file hoặc dán Ctrl+V) vào static/uploads/."""

    @staticmethod
    def save(file: FileStorage) -> str:
        """Validate và lưu ảnh. Trả về URL công cộng (vd: /static/uploads/abc.png)."""
        if file is None or not file.filename:
            raise ValueError("Không có file ảnh được chọn.")

        ext = (
            file.filename.rsplit(".", 1)[-1].lower()
            if "." in file.filename
            else ""
        )
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                "Định dạng ảnh không hợp lệ. Chỉ chấp nhận: "
                + ", ".join(sorted(ALLOWED_EXTENSIONS))
                + "."
            )
        if file.mimetype and not file.mimetype.startswith("image/"):
            raise ValueError("File tải lên không phải là hình ảnh.")

        data = file.read()
        if not data:
            raise ValueError("File ảnh rỗng.")
        if len(data) > MAX_FILE_SIZE:
            raise ValueError("Ảnh vượt quá 5MB. Vui lòng chọn ảnh nhỏ hơn.")

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.{ext}"
        (UPLOAD_DIR / filename).write_bytes(data)
        return f"/static/uploads/{filename}"