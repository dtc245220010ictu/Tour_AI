"""
Tour and Destination Management Service.
Provides catalog searching, filtering, and schedule management.
"""

import re
import unicodedata
from database.db import execute_query

def generate_slug(text: str) -> str:
    """Generate a clean URL-friendly slug from Vietnamese text."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text.lower()).strip()
    return re.sub(r'[-\s]+', '-', text)

class TourService:
    @staticmethod
    def get_all_destinations():
        return execute_query(
            "SELECT * FROM destinations ORDER BY region ASC, name ASC;",
            fetch_all=True
        )

    @staticmethod
    def get_destination_by_id(dest_id: int):
        return execute_query(
            "SELECT * FROM destinations WHERE id = ?;",
            (dest_id,),
            fetch_one=True
        )

    @staticmethod
    def create_destination(name: str, region: str, description: str, image_url: str):
        return execute_query(
            "INSERT INTO destinations (name, region, description, image_url) VALUES (?, ?, ?, ?);",
            (name.strip(), region.strip(), description.strip(), image_url.strip()),
            commit=True
        )

    @staticmethod
    def get_tours(destination_id=None, min_price=None, max_price=None, duration=None, keyword=None, limit=50):
        query = """
            SELECT t.*, d.name AS destination_name, d.region AS destination_region,
                   MIN(s.departure_date) AS next_departure,
                   COALESCE(SUM(s.available_seats), 0) AS total_available_seats
            FROM tours t
            JOIN destinations d ON t.destination_id = d.id
            LEFT JOIN tour_schedules s ON t.id = s.tour_id AND s.departure_date >= CURRENT_DATE AND s.status = 'OPEN'
            WHERE t.is_active = 1
        """
        params = []

        if destination_id:
            query += " AND t.destination_id = ?"
            params.append(destination_id)

        if min_price is not None and float(min_price) > 0:
            query += " AND t.base_price >= ?"
            params.append(float(min_price))

        if max_price is not None and float(max_price) > 0:
            query += " AND t.base_price <= ?"
            params.append(float(max_price))

        if duration is not None and int(duration) > 0:
            query += " AND t.duration_days = ?"
            params.append(int(duration))

        if keyword:
            query += " AND (t.title LIKE ? OR t.description LIKE ? OR d.name LIKE ?)"
            kw = f"%{keyword.strip()}%"
            params.extend([kw, kw, kw])

        query += " GROUP BY t.id ORDER BY t.id DESC LIMIT ?;"
        params.append(limit)

        return execute_query(query, params, fetch_all=True)

    @staticmethod
    def get_tour_by_id(tour_id: int):
        tour = execute_query(
            """SELECT t.*, d.name AS destination_name, d.region AS destination_region 
               FROM tours t
               JOIN destinations d ON t.destination_id = d.id
               WHERE t.id = ?;""",
            (tour_id,),
            fetch_one=True
        )
        if tour:
            tour["schedules"] = TourService.get_tour_schedules(tour_id)
        return tour

    @staticmethod
    def get_tour_by_slug(slug: str):
        tour = execute_query(
            """SELECT t.*, d.name AS destination_name, d.region AS destination_region 
               FROM tours t
               JOIN destinations d ON t.destination_id = d.id
               WHERE t.slug = ?;""",
            (slug,),
            fetch_one=True
        )
        if tour:
            tour["schedules"] = TourService.get_tour_schedules(tour["id"])
        return tour

    @staticmethod
    def create_tour(destination_id: int, title: str, description: str, duration_days: int,
                    duration_nights: int, base_price: float, transportation: str,
                    itinerary_text: str, image_url: str):
        slug_base = generate_slug(title)
        slug = slug_base
        count = 1
        while execute_query("SELECT id FROM tours WHERE slug = ?;", (slug,), fetch_one=True):
            slug = f"{slug_base}-{count}"
            count += 1

        tour_id = execute_query(
            """INSERT INTO tours 
            (destination_id, title, slug, description, duration_days, duration_nights, 
             base_price, transportation, itinerary_text, image_url, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1);""",
            (destination_id, title.strip(), slug, description.strip(), duration_days,
             duration_nights, base_price, transportation.strip(), itinerary_text.strip(), image_url.strip()),
            commit=True
        )
        return tour_id

    @staticmethod
    def update_tour(tour_id: int, destination_id: int, title: str, description: str,
                    duration_days: int, duration_nights: int, base_price: float,
                    transportation: str, itinerary_text: str, image_url: str, is_active: int = 1):
        execute_query(
            """UPDATE tours SET 
               destination_id = ?, title = ?, description = ?, duration_days = ?,
               duration_nights = ?, base_price = ?, transportation = ?, 
               itinerary_text = ?, image_url = ?, is_active = ?
               WHERE id = ?;""",
            (destination_id, title.strip(), description.strip(), duration_days,
             duration_nights, base_price, transportation.strip(), itinerary_text.strip(),
             image_url.strip(), is_active, tour_id),
            commit=True
        )

    @staticmethod
    def delete_tour(tour_id: int):
        # Soft delete
        execute_query("UPDATE tours SET is_active = 0 WHERE id = ?;", (tour_id,), commit=True)

    @staticmethod
    def get_tour_schedules(tour_id: int, only_open: bool = False):
        query = "SELECT * FROM tour_schedules WHERE tour_id = ?"
        if only_open:
            query += " AND status = 'OPEN' AND available_seats > 0"
        query += " ORDER BY departure_date ASC;"
        return execute_query(query, (tour_id,), fetch_all=True)

    @staticmethod
    def get_schedule_by_id(schedule_id: int):
        return execute_query(
            """SELECT s.*, t.title AS tour_title, t.slug AS tour_slug, 
                      d.name AS destination_name
               FROM tour_schedules s
               JOIN tours t ON s.tour_id = t.id
               JOIN destinations d ON t.destination_id = d.id
               WHERE s.id = ?;""",
            (schedule_id,),
            fetch_one=True
        )

    @staticmethod
    def create_schedule(tour_id: int, departure_date: str, return_date: str,
                        adult_price: float, child_price: float, total_seats: int):
        return execute_query(
            """INSERT INTO tour_schedules 
            (tour_id, departure_date, return_date, adult_price, child_price, total_seats, available_seats, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN');""",
            (tour_id, departure_date, return_date, adult_price, child_price, total_seats, total_seats),
            commit=True
        )

