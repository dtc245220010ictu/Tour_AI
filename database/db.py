"""MySQL connection and query helpers for TourAI.

All application SQL continues to use parameter binding. The compatibility
layer converts the existing ``?`` placeholders to MySQL Connector's ``%s``
placeholders before execution, so services never concatenate user input into
SQL and do not need to know about the connector implementation.
"""

from __future__ import annotations

import os
import re
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterator, Literal, overload

from dotenv import load_dotenv

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:  # pragma: no cover - gives a useful message before setup
    mysql = None
    MySQLError = Exception
else:
    mysql = mysql.connector


BASE_DIR = Path(__file__).resolve().parent.parent
# Database helpers are also used by standalone seeding, migration and
# maintenance scripts. Loading the project .env here keeps those commands
# consistent with the Flask entry point while preserving explicitly supplied
# process environment variables.
load_dotenv(BASE_DIR / ".env")
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_]+$")


def _require_mysql_connector() -> None:
    if mysql is None:
        raise RuntimeError(
            "Thiếu mysql-connector-python. Hãy cài dependencies bằng "
            "`pip install -r requirements.txt`."
        )


def _mysql_config(database: str | None = None) -> dict[str, Any]:
    """Build connector settings exclusively from environment variables."""
    _require_mysql_connector()
    db_name = database if database is not None else os.environ.get("MYSQL_DB", "").strip()
    user = os.environ.get("MYSQL_USER", "").strip()
    if not user or not db_name:
        raise RuntimeError(
            "Cần cấu hình MYSQL_USER và MYSQL_DB trong biến môi trường hoặc .env."
        )
    try:
        port = int(os.environ.get("MYSQL_PORT", "3306"))
    except ValueError as exc:
        raise RuntimeError("MYSQL_PORT phải là một số nguyên hợp lệ.") from exc

    return {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1").strip() or "127.0.0.1",
        "port": port,
        "user": user,
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": db_name,
        "charset": "utf8mb4",
        "use_unicode": True,
        "autocommit": False,
    }


def _convert_placeholders(query: str) -> str:
    """Convert qmark placeholders outside SQL string literals to MySQL ``%s``."""
    result: list[str] = []
    in_single = False
    in_double = False
    index = 0
    while index < len(query):
        char = query[index]
        next_char = query[index + 1] if index + 1 < len(query) else ""
        if char == "'" and not in_double:
            if in_single and next_char == "'":
                result.extend((char, next_char))
                index += 2
                continue
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double

        result.append("%s" if char == "?" and not in_single and not in_double else char)
        index += 1
    return "".join(result)


def _normalise_value(value: Any) -> Any:
    """Preserve the SQLite-era service contract for rows returned by MySQL."""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        # SQLite returned whole DECIMAL values inserted by this application as
        # integers. Preserve that public contract so callers can format
        # 3200000 as "3.200.000" rather than "3.200.000.0".
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    return value


class Row(dict[str, Any]):
    """Dictionary row that also supports SQLite-style numeric indexing."""

    def __getitem__(self, key: str | int) -> Any:
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


def _row(value: dict[str, Any] | None) -> Row | None:
    if value is None:
        return None
    return Row({key: _normalise_value(item) for key, item in value.items()})


class MySQLCursor:
    """Small cursor adapter used by existing services, seeders and tests."""

    def __init__(self, cursor: Any):
        self._cursor = cursor

    @property
    def lastrowid(self) -> int | None:
        return self._cursor.lastrowid

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    def execute(self, query: str, params: Any = ()) -> "MySQLCursor":
        self._cursor.execute(_convert_placeholders(query), params or ())
        return self

    def executemany(self, query: str, params: Any) -> "MySQLCursor":
        self._cursor.executemany(_convert_placeholders(query), params)
        return self

    def fetchone(self) -> Row | None:
        return _row(self._cursor.fetchone())

    def fetchall(self) -> list[Row]:
        return [_row(item) for item in self._cursor.fetchall() if item is not None]

    def close(self) -> None:
        self._cursor.close()


class MySQLConnection:
    """Connection adapter that provides the SQLite methods used by the project."""

    def __init__(self, connection: Any):
        self._connection = connection

    def cursor(self) -> MySQLCursor:
        return MySQLCursor(self._connection.cursor(dictionary=True, buffered=True))

    def execute(self, query: str, params: Any = ()) -> MySQLCursor:
        cursor = self.cursor()
        cursor.execute(query, params)
        return cursor

    def executemany(self, query: str, params: Any) -> MySQLCursor:
        cursor = self.cursor()
        cursor.executemany(query, params)
        return cursor

    def commit(self) -> None:
        self._connection.commit()

    def rollback(self) -> None:
        self._connection.rollback()

    def close(self) -> None:
        self._connection.close()


def get_connection(database: str | None = None) -> MySQLConnection:
    """Open a MySQL connection using the configured application database."""
    try:
        return MySQLConnection(mysql.connect(**_mysql_config(database)))
    except MySQLError as exc:
        raise RuntimeError(
            "Không thể kết nối MySQL. Kiểm tra MYSQL_HOST, MYSQL_PORT, MYSQL_USER, "
            "MYSQL_PASSWORD và MYSQL_DB trong .env."
        ) from exc


@contextmanager
def get_db() -> Iterator[MySQLConnection]:
    """Yield one transactional MySQL connection and commit or roll back safely."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _run_schema(cursor: MySQLCursor, schema_sql: str) -> None:
    """Execute the simple, semicolon-delimited DDL script idempotently."""
    for statement in schema_sql.split(";"):
        statement = re.sub(r"--[^\r\n]*", "", statement).strip()
        if not statement:
            continue
        try:
            cursor.execute(statement)
        except MySQLError as exc:
            # MySQL has no portable CREATE INDEX IF NOT EXISTS. Existing
            # indexes are expected whenever init_db() is called after startup.
            if getattr(exc, "errno", None) == 1061:
                continue
            raise


def init_db() -> None:
    """Create the MySQL tables and indexes declared in ``database/schema.sql``."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_db() as conn:
        cursor = conn.cursor()
        _run_schema(cursor, schema_sql)
        cursor.close()


def create_database_if_missing(database_name: str | None = None) -> None:
    """Create the configured application database without touching its data."""
    database_name = database_name or os.environ.get("MYSQL_DB", "").strip()
    if not _IDENTIFIER.fullmatch(database_name):
        raise ValueError("MYSQL_DB phải là một tên database MySQL hợp lệ.")

    config = _mysql_config()
    config.pop("database")
    try:
        raw_connection = mysql.connect(**config)
    except MySQLError as exc:
        raise RuntimeError("Không thể kết nối MySQL để tạo application database.") from exc

    try:
        cursor = raw_connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.close()
        raw_connection.commit()
    finally:
        raw_connection.close()


def recreate_test_database(database_name: str) -> None:
    """Recreate an explicitly named MySQL test database.

    This destructive helper refuses every database name except an identifier
    ending in ``_test``. It is used only by the pytest fixture after the test
    database has been selected through ``MYSQL_TEST_DB``.
    """
    if not _IDENTIFIER.fullmatch(database_name) or not database_name.endswith("_test"):
        raise ValueError("MYSQL_TEST_DB phải là tên hợp lệ và kết thúc bằng '_test'.")

    config = _mysql_config()
    config.pop("database")
    try:
        raw_connection = mysql.connect(**config)
    except MySQLError as exc:
        raise RuntimeError("Không thể kết nối MySQL để khởi tạo test database.") from exc

    try:
        cursor = raw_connection.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS `{database_name}`")
        cursor.execute(
            f"CREATE DATABASE `{database_name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.close()
        raw_connection.commit()
    finally:
        raw_connection.close()


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


def execute_query(
    query: str,
    params: Any = (),
    fetch_one: bool = False,
    fetch_all: bool = False,
    commit: bool = False,
) -> int | dict[str, Any] | None | list[dict[str, Any]] | MySQLCursor:
    """Execute parameterized SQL and return normalized dict-like MySQL rows."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            return int(cursor.lastrowid or 0)
        if fetch_one:
            row = cursor.fetchone()
            return dict(row) if row else None
        if fetch_all:
            return [dict(row) for row in cursor.fetchall()]
        return cursor
