"""
Database connection and execution manager for TourAI.
Supports both SQLite (default for local development & automated tests)
and MySQL (configured via DATABASE_URL or MYSQL_* environment variables).
"""

import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Literal, overload

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("SQLITE_DB_PATH", str(BASE_DIR / "database" / "tour_ai.db"))
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

def get_connection():
    """Returns a database connection with dict-like row access."""
    # SQLite connection
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db():
    """Context manager for safe database transactions."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize tables and indexes using schema.sql and apply backward-compatible migrations."""
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_db() as conn:
        conn.executescript(schema_sql)
        cursor = conn.cursor()
        
        # Backward-compatible migrations for existing SQLite database
        try:
            cursor.execute("PRAGMA table_info(payments);")
            columns = [row[1] for row in cursor.fetchall()]
            if "payment_type" not in columns:
                cursor.execute("ALTER TABLE payments ADD COLUMN payment_type VARCHAR(30) NOT NULL DEFAULT 'FULL';")
            if "verified_by" not in columns:
                cursor.execute("ALTER TABLE payments ADD COLUMN verified_by INTEGER REFERENCES users(id);")
            if "verified_at" not in columns:
                cursor.execute("ALTER TABLE payments ADD COLUMN verified_at DATETIME;")
            if "notes" not in columns:
                cursor.execute("ALTER TABLE payments ADD COLUMN notes TEXT;")
        except Exception:
            pass

@overload
def execute_query(
    query: str,
    params: Any = (),
    *,
    commit: Literal[True],
    fetch_one: bool = False,
    fetch_all: bool = False,
) -> int: ...


@overload
def execute_query(
    query: str,
    params: Any = (),
    *,
    fetch_one: Literal[True],
    fetch_all: bool = False,
    commit: Literal[False] = False,
) -> dict[str, Any] | None: ...


@overload
def execute_query(
    query: str,
    params: Any = (),
    *,
    fetch_all: Literal[True],
    fetch_one: bool = False,
    commit: Literal[False] = False,
) -> list[dict[str, Any]]: ...


@overload
def execute_query(
    query: str,
    params: Any = (),
    *,
    fetch_one: Literal[False] = False,
    fetch_all: Literal[False] = False,
    commit: Literal[False] = False,
) -> sqlite3.Cursor: ...


@overload
def execute_query(
    query: str,
    params: Any = (),
    *,
    fetch_one: bool = False,
    fetch_all: bool = False,
    commit: bool = False,
) -> int | dict[str, Any] | None | list[dict[str, Any]] | sqlite3.Cursor: ...


def execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=False):
    """
    Executes a parameterized SQL query safely.
    Prevents SQL injection vulnerabilities.

    Overloads let static type checkers (Pylance/Pyright) infer the return type:
      - commit=True        -> int (lastrowid)
      - fetch_one=True     -> dict | None
      - fetch_all=True     -> list[dict]
      - no flag            -> sqlite3.Cursor
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            last_id = cursor.lastrowid
            return last_id
        if fetch_one:
            row = cursor.fetchone()
            return dict(row) if row else None
        if fetch_all:
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        return cursor

