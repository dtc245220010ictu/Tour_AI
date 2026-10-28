"""One-time, explicit migration of TourAI data from SQLite to MySQL.

The target is never cleared by default. Use ``--replace`` only after backing
up the MySQL target database; it removes all TourAI rows before importing the
SQLite source while retaining the MySQL schema.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

from database.db import create_database_if_missing, get_db, init_db


TABLES_IN_INSERT_ORDER = (
    "users",
    "destinations",
    "tours",
    "tour_schedules",
    "bookings",
    "payments",
    "refund_requests",
    "tour_guides",
    "guide_assignments",
    "feedbacks",
    "chat_logs",
    "tour_expenses",
)

TABLES_IN_DELETE_ORDER = tuple(reversed(TABLES_IN_INSERT_ORDER))


def _target_has_data() -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        for table in TABLES_IN_INSERT_ORDER:
            cursor.execute(f"SELECT COUNT(*) AS total FROM `{table}`")
            if cursor.fetchone()["total"]:
                return True
    return False


def _clear_target() -> None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in TABLES_IN_DELETE_ORDER:
            cursor.execute(f"DELETE FROM `{table}`")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def _read_source_rows(source: sqlite3.Connection, table: str) -> tuple[list[str], list[tuple]]:
    columns = [row[1] for row in source.execute(f"PRAGMA table_info({table})")]
    if not columns:
        return [], []
    quoted_columns = ", ".join(f'"{column}"' for column in columns)
    rows = [tuple(row[column] for column in columns) for row in source.execute(
        f"SELECT {quoted_columns} FROM {table}"
    )]
    return columns, rows


def migrate(source_path: Path, replace: bool) -> dict[str, int]:
    if not source_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy SQLite source database: {source_path}")

    create_database_if_missing()
    init_db()
    if _target_has_data():
        if not replace:
            raise RuntimeError(
                "MySQL target đã có dữ liệu. Sao lưu trước rồi chạy lại với --replace "
                "nếu bạn xác nhận muốn thay thế toàn bộ dữ liệu TourAI."
            )
        _clear_target()

    source = sqlite3.connect(source_path)
    source.row_factory = sqlite3.Row
    totals: dict[str, int] = {}
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            for table in TABLES_IN_INSERT_ORDER:
                columns, rows = _read_source_rows(source, table)
                if not rows:
                    totals[table] = 0
                    continue
                names = ", ".join(f"`{column}`" for column in columns)
                placeholders = ", ".join("?" for _ in columns)
                cursor.executemany(
                    f"INSERT INTO `{table}` ({names}) VALUES ({placeholders})",
                    rows,
                )
                totals[table] = len(rows)
    finally:
        source.close()
    return totals


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate TourAI SQLite data to MySQL.")
    parser.add_argument(
        "--source",
        type=Path,
        default=BASE_DIR / "database" / "tour_ai.db",
        help="Path to the source SQLite database (default: database/tour_ai.db).",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete all TourAI rows in the MySQL target before importing.",
    )
    args = parser.parse_args()

    totals = migrate(args.source.resolve(), args.replace)
    print("SQLite → MySQL migration completed:")
    for table in TABLES_IN_INSERT_ORDER:
        print(f"  {table}: {totals.get(table, 0)} rows")


if __name__ == "__main__":
    main()
