"""
Tour and Destination Management Service.
Provides catalog searching, filtering, and schedule management.
"""

import re
import unicodedata
from database.db import get_db, execute_query

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
    def update_destination(dest_id: int, name: str, region: str, description: str, image_url: str):
        """Cập nhật điểm đến (ADMIN / STAFF)."""
        destination = TourService.get_destination_by_id(dest_id)
        if not destination:
            raise ValueError("Không tìm thấy điểm đến.")

        name = (name or "").strip()
        region = (region or "").strip()
        if not name or not region:
            raise ValueError("Tên điểm đến và khu vực là bắt buộc.")

        duplicate = execute_query(
            "SELECT id FROM destinations WHERE name = ? AND id != ?;",
            (name, dest_id),
            fetch_one=True
        )
        if duplicate:
            raise ValueError("Tên điểm đến đã tồn tại. Vui lòng chọn tên khác.")

        execute_query(
            "UPDATE destinations SET name = ?, region = ?, description = ?, image_url = ? WHERE id = ?;",
            (name, region, (description or "").strip(), (image_url or "").strip(), dest_id),
            commit=True
        )
        return True

    @staticmethod
    def delete_destination(dest_id: int):
        """Xóa điểm đến (ADMIN only - STAFF không có quyền Xóa theo CN2). Chặn xóa điểm đến đang có tour liên kết."""
        destination = TourService.get_destination_by_id(dest_id)
        if not destination:
            raise ValueError("Không tìm thấy điểm đến.")

        linked = execute_query(
            "SELECT COUNT(*) AS c FROM tours WHERE destination_id = ?;",
            (dest_id,),
            fetch_one=True
        )
        if linked and linked["c"] > 0:
            raise ValueError(
                f"Điểm đến đang gắn với {linked['c']} tour. "
                "Hãy xóa hoặc chuyển các tour đó sang điểm đến khác trước khi xóa."
            )
        execute_query("DELETE FROM destinations WHERE id = ?;", (dest_id,), commit=True)
        return True

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
    def sync_schedule_prices(tour_id: int, base_price: float) -> int:
        """Đồng bộ giá vé của TẤT CẢ lịch khởi hành theo giá tour hiện tại.
        Giá trẻ em = 70% giá người lớn (quy ước toàn hệ thống).
        Trả về số lịch khởi hành đã cập nhật.
        """
        adult = float(base_price)
        child = round(adult * 0.7)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tour_schedules SET adult_price = ?, child_price = ? WHERE tour_id = ?;",
                (adult, child, tour_id),
            )
            return cursor.rowcount

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

    @staticmethod
    def update_schedule(schedule_id: int, departure_date: str, return_date: str,
                        adult_price: float, child_price: float, total_seats: int,
                        status: str = "OPEN"):
        """Cập nhật lịch khởi hành mà không cho phép ghi đè số ghế đã giữ.

        `available_seats` luôn được suy ra từ tổng số ghế trừ số hành khách của
        các booking chưa hủy (PENDING, CONFIRMED hoặc COMPLETED). Nhờ vậy form
        quản trị không thể vô tình nhập một số chỗ còn lại mâu thuẫn với dữ liệu
        booking thực tế.
        """
        departure_date = (departure_date or "").strip()
        return_date = (return_date or "").strip()
        if not departure_date or not return_date:
            raise ValueError("Ngày khởi hành và ngày về là bắt buộc.")
        if return_date < departure_date:
            raise ValueError("Ngày về phải lớn hơn hoặc bằng ngày khởi hành.")

        adult_price = float(adult_price)
        child_price = float(child_price)
        if adult_price <= 0 or child_price <= 0:
            raise ValueError("Giá vé phải lớn hơn 0.")

        total_seats = int(total_seats)
        if total_seats < 1:
            raise ValueError("Tổng số chỗ phải lớn hơn 0.")

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tour_schedules WHERE id = ?;", (schedule_id,))
            if not cursor.fetchone():
                raise ValueError("Không tìm thấy lịch khởi hành.")

            # Booking is created in PENDING while its seats are already reserved,
            # therefore every non-cancelled booking must be counted here.
            cursor.execute(
                """SELECT COALESCE(SUM(num_adults + num_children), 0) AS reserved_seats
                   FROM bookings
                   WHERE schedule_id = ? AND status IN ('PENDING', 'CONFIRMED', 'COMPLETED');""",
                (schedule_id,),
            )
            reserved_row = cursor.fetchone()
            reserved_seats = int(reserved_row["reserved_seats"] or 0)
            if total_seats < reserved_seats:
                raise ValueError(
                    f"Tổng số chỗ không thể nhỏ hơn {reserved_seats} chỗ đã được giữ bởi các đơn đặt tour."
                )
            available_seats = total_seats - reserved_seats

            if status not in ("OPEN", "FULL", "CLOSED", "CANCELLED"):
                status = "OPEN"
            # OPEN/FULL is always determined from the derived availability.
            # CLOSED and CANCELLED remain explicit operational decisions.
            if status == "OPEN" and available_seats == 0:
                status = "FULL"
            elif status == "FULL" and available_seats > 0:
                status = "OPEN"

            cursor.execute(
                """UPDATE tour_schedules SET
                   departure_date = ?, return_date = ?, adult_price = ?, child_price = ?,
                   total_seats = ?, available_seats = ?, status = ?
                   WHERE id = ?;""",
                (departure_date, return_date, adult_price, child_price,
                 total_seats, available_seats, status, schedule_id),
            )
        return True

    @staticmethod
    def delete_schedule(schedule_id: int):
        """Xóa lịch khởi hành (ADMIN only - STAFF không có quyền Xóa theo CN3). Chặn xóa đợt đã có đơn đặt chỗ."""
        schedule = execute_query(
            "SELECT id FROM tour_schedules WHERE id = ?;",
            (schedule_id,),
            fetch_one=True
        )
        if not schedule:
            raise ValueError("Không tìm thấy lịch khởi hành.")

        linked = execute_query(
            "SELECT COUNT(*) AS c FROM bookings WHERE schedule_id = ?;",
            (schedule_id,),
            fetch_one=True
        )
        if linked and linked["c"] > 0:
            raise ValueError("Đợt khởi hành này đã có đơn đặt chỗ. Không thể xóa.")

        execute_query("DELETE FROM tour_schedules WHERE id = ?;", (schedule_id,), commit=True)
        return True

