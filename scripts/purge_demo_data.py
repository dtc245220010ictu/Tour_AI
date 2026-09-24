"""
Purge demo/seed business data from the TourAI database, keeping:
- The 5 role accounts (admin/staff/accountant/guide/customer)
- Destinations (master data)
- Real chat logs created during actual usage

Deletes (seed-marked rows only, in FK-safe order):
payments -> feedbacks -> guide_assignments -> tour_expenses
-> bookings -> tour_schedules -> tour_guides -> tours

Usage:
    python scripts/purge_demo_data.py            # only rows marked as seed
    python scripts/purge_demo_data.py --all      # wipe business tables entirely
    python scripts/purge_demo_data.py --db path/to/db.sqlite

NOTE: The default mode identifies seed rows by the known seed markers
(booking codes BK-2026100x and the seed batch timestamp). Re-seeding via
`python database/seeder.py` will insert demo data again.
"""

import argparse
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = BASE_DIR / "database" / "tour_ai.db"

# Markers identifying rows created by database/seeder.py
SEED_BOOKING_CODES = ("BK-20261001", "BK-20261002", "BK-20261003", "BK-20261004")
SEED_TIMESTAMP = "2026-09-15 14:06:38"  # created_at batch written by the seeder


def _ids(cur, sql, params=()):
    return [r[0] for r in cur.execute(sql, params).fetchall()]


def purge_seed(cur):
    """Delete only rows identifiable as seeder output. Returns summary dict."""
    tour_ids = _ids(cur, "SELECT id FROM tours WHERE created_at = ?", (SEED_TIMESTAMP,))
    schedule_ids = _ids(
        cur, "SELECT id FROM tour_schedules WHERE created_at = ?", (SEED_TIMESTAMP,)
    )
    guide_ids = _ids(
        cur, "SELECT id FROM tour_guides WHERE created_at = ?", (SEED_TIMESTAMP,)
    )
    booking_ids = _ids(
        cur,
        "SELECT id FROM bookings WHERE booking_code IN ({})".format(
            ",".join("?" * len(SEED_BOOKING_CODES))
        ),
        SEED_BOOKING_CODES,
    )

    summary = {}

    ph = ",".join("?" * len(booking_ids)) if booking_ids else None
    if ph:
        summary["payments"] = cur.rowcount if cur.execute(
            f"DELETE FROM payments WHERE booking_id IN ({ph})", booking_ids
        ) else 0
    else:
        summary["payments"] = 0

    # feedbacks: seed batch, or referencing seed tours/bookings
    cur.execute(
        """DELETE FROM feedbacks
           WHERE created_at = ?
              OR tour_id IN (SELECT id FROM tours WHERE created_at = ?)
              OR booking_id IN (SELECT id FROM bookings WHERE booking_code IN ({0}))""".format(
            ",".join("?" * len(SEED_BOOKING_CODES))
        ),
        (SEED_TIMESTAMP, SEED_TIMESTAMP, *SEED_BOOKING_CODES),
    )
    summary["feedbacks"] = cur.rowcount

    if schedule_ids:
        ph_s = ",".join("?" * len(schedule_ids))
        cur.execute(
            f"DELETE FROM guide_assignments WHERE schedule_id IN ({ph_s}) OR created_at = ?",
            (*schedule_ids, SEED_TIMESTAMP),
        )
        summary["guide_assignments"] = cur.rowcount
        cur.execute(
            f"DELETE FROM tour_expenses WHERE schedule_id IN ({ph_s})", schedule_ids
        )
        summary["tour_expenses"] = cur.rowcount
    else:
        summary["guide_assignments"] = 0
        summary["tour_expenses"] = 0

    if booking_ids:
        cur.execute(
            f"DELETE FROM bookings WHERE id IN ({ph})", booking_ids
        )
        summary["bookings"] = cur.rowcount
    else:
        summary["bookings"] = 0

    cur.execute("DELETE FROM tour_schedules WHERE created_at = ?", (SEED_TIMESTAMP,))
    summary["tour_schedules"] = cur.rowcount

    if guide_ids:
        cur.execute(
            "DELETE FROM tour_guides WHERE id IN ({})".format(
                ",".join("?" * len(guide_ids))
            ),
            guide_ids,
        )
        summary["tour_guides"] = cur.rowcount
    else:
        summary["tour_guides"] = 0

    cur.execute("DELETE FROM tours WHERE created_at = ?", (SEED_TIMESTAMP,))
    summary["tours"] = cur.rowcount

    return summary


def purge_all(cur):
    """Wipe all business tables entirely (users, destinations, chat_logs kept)."""
    summary = {}
    for table in (
        "payments",
        "feedbacks",
        "guide_assignments",
        "tour_expenses",
        "bookings",
        "tour_schedules",
        "tour_guides",
        "tours",
    ):
        cur.execute(f"DELETE FROM {table}")
        summary[table] = cur.rowcount
    return summary


def main():
    parser = argparse.ArgumentParser(description="Purge demo/seed business data.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to SQLite database")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Delete ALL rows in business tables (not just seed-marked rows)",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"ERROR: database not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    try:
        summary = purge_all(cur) if args.all else purge_seed(cur)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    mode = "FULL WIPE (--all)" if args.all else "seed-marked rows"
    print(f"Purged {mode} from {db_path}:")
    for table, count in summary.items():
        print(f"  {table}: {count} rows deleted")
    print("Kept: users (5 role accounts), destinations, chat_logs (real usage).")


if __name__ == "__main__":
    main()