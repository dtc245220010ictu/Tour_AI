"""
Pytest configuration and shared fixtures for TourAI test suite.
Uses an isolated SQLite test database to ensure tests are repeatable and independent.
"""

import os
import sys
from pathlib import Path
import pytest

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Use an isolated test database
TEST_DB_PATH = str(BASE_DIR / "database" / "test_tour_ai.db")
os.environ["SQLITE_DB_PATH"] = TEST_DB_PATH

from app import create_app
from database.db import init_db
from database.seeder import seed_all

# Keep tests hermetic: never call the external Gemini API during test runs.
# (load_dotenv() inside app.py may have loaded a real key from the project .env;
#  tests must exercise the deterministic grounded-fallback path instead.)
os.environ.pop("GEMINI_API_KEY", None)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initializes and seeds test database once for the session."""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

    init_db()
    seed_all()

    yield

    # Teardown
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key_123",
        "WTF_CSRF_ENABLED": False
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

