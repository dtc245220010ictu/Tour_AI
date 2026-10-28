"""Pytest configuration and shared fixtures for TourAI on MySQL.

Tests are intentionally isolated in an explicitly configured database ending
in ``_test``. The fixture drops and recreates only that database; it never
touches ``MYSQL_DB`` used by the application.
"""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

TEST_DB_NAME = os.environ.get("MYSQL_TEST_DB", "").strip()
if not TEST_DB_NAME:
    raise RuntimeError(
        "Thiếu MYSQL_TEST_DB. Đặt một database MySQL riêng kết thúc bằng '_test' "
        "trong .env trước khi chạy pytest."
    )

# Set this before importing app.py; load_dotenv() there does not overwrite an
# existing environment variable, so init_db() always targets the test database.
os.environ["MYSQL_DB"] = TEST_DB_NAME

from app import create_app
from database.db import init_db, recreate_test_database
from database.seeder import seed_all

# Keep tests hermetic: never call the external Gemini API during test runs.
os.environ.pop("GEMINI_API_KEY", None)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create a clean, explicitly named MySQL database and seed it once."""
    recreate_test_database(TEST_DB_NAME)
    init_db()
    seed_all()
    yield


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key_123",
        "WTF_CSRF_ENABLED": False,
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()
