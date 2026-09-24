"""
Booking and Capacity Management Service.
Guarantees zero-overbooking using atomic database transactions.
"""

import time
import random
from database.db import get_db, execute_query

class OverbookingError(Exception):
    """Raised when the requested number of seats exceeds available capacity."""
    pass

class BookingService:
    @staticmethod
    def generate_booking_code() -> str:
        timestamp = time.strftime("%Y%m%d")
        rand = random.randint(1000, 9999)
        return f"BK-{timestamp}-{rand}"

    @staticmethod
    def create_booking(user_id: int, schedule_id: int, customer_name: str,
                       customer_email: str, customer_phone: str,
                       num_adults: int, num_children: int = 0, notes: str = ""):
        total_passengers = int(num_adults) + int(num_children)
        if total_passengers <= 0:
            raise ValueError("Số lượng khách phải lớn hơn 0.")

        with get_db() as conn:
            cursor = conn.cursor()

            # 1. Fetch schedule and check capacity
            cursor.execute("SELECT * FROM tour_schedules WHERE id = ?;", (schedule_id,))
            schedule = cursor.fetchone()
            if not schedule:
                raise ValueError("Không tìm thấy lịch khởi hành đã chọn.")

            if schedule["status"] != "OPEN":
                raise OverbookingError("Lịch khởi hành này hiện không mở nhận đặt chỗ.")

            if schedule["available_seats"] < total_passengers:
                raise OverbookingError(
                    f"Rất tiếc! Chuyến đi chỉ còn lại {schedule['available_seats']} chỗ trống, "
                    f"không đủ cho {total_passengers} khách."
                )

            # 2. Atomic seat deduction (Concurrency-safe)
            cursor.execute(
                """UPDATE tour_schedules 
                   SET available_seats = available_seats - ? 
                   WHERE id = ? AND available_seats >= ?;""",
                (total_passengers, schedule_id, total_passengers)
            )
            if cursor.rowcount == 0:
                raise OverbookingError("Số chỗ trống vừa được đặt bởi người khác. Vui lòng thử lại!")

            # 3. Calculate total amount
            total_amount = (num_adults * schedule["adult_price"]) + (num_children * schedule["child_price"])

            # 4. Create booking
            booking_code = BookingService.generate_booking_code()
            cursor.execute(
                """INSERT INTO bookings 
                (booking_code, user_id, schedule_id, customer_name, customer_email, customer_phone,
                 num_adults, num_children, total_amount, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?);""",
                (booking_code, user_id, schedule_id, customer_name.strip(), customer_email.strip(),
                 customer_phone.strip(), num_adults, num_children, total_amount, notes.strip())
            )
            booking_id = cursor.lastrowid
            if booking_id is None:
                raise ValueError("Không tạo được đơn đặt chỗ. Vui lòng thử lại.")

            # 5. Check if schedule is now full
            cursor.execute(
                "UPDATE tour_schedules SET status = 'FULL' WHERE id = ? AND available_seats = 0;",
                (schedule_id,)
            )

        return BookingService.get_booking_by_id(booking_id)

    @staticmethod
    def get_booking_by_id(booking_id: int):
        return execute_query(
            """SELECT b.*, s.departure_date, s.return_date, s.tour_id,
                      t.title AS tour_title, t.image_url AS tour_image,
                      d.name AS destination_name
               FROM bookings b
               JOIN tour_schedules s ON b.schedule_id = s.id
               JOIN tours t ON s.tour_id = t.id
               JOIN destinations d ON t.destination_id = d.id
               WHERE b.id = ?;""",
            (booking_id,),
            fetch_one=True
        )

    @staticmethod
    def get_booking_by_code(booking_code: str):
        return execute_query(
            """SELECT b.*, s.departure_date, s.return_date, s.tour_id,
                      t.title AS tour_title, t.image_url AS tour_image,
                      d.name AS destination_name
               FROM bookings b
               JOIN tour_schedules s ON b.schedule_id = s.id
               JOIN tours t ON s.tour_id = t.id
               JOIN destinations d ON t.destination_id = d.id
               WHERE b.booking_code = ?;""",
            (booking_code.strip(),),
            fetch_one=True
        )

    @staticmethod
    def get_user_bookings(user_id: int):
        return execute_query(
            """SELECT b.*, s.departure_date, s.return_date,
                      t.title AS tour_title, t.image_url AS tour_image,
                      d.name AS destination_name
               FROM bookings b
               JOIN tour_schedules s ON b.schedule_id = s.id
               JOIN tours t ON s.tour_id = t.id
               JOIN destinations d ON t.destination_id = d.id
               WHERE b.user_id = ?
               ORDER BY b.created_at DESC;""",
            (user_id,),
            fetch_all=True
        )

    @staticmethod
    def get_all_bookings(status: str | None = None):
        query = """
            SELECT b.*, s.departure_date, s.return_date,
                   t.title AS tour_title, d.name AS destination_name
            FROM bookings b
            JOIN tour_schedules s ON b.schedule_id = s.id
            JOIN tours t ON s.tour_id = t.id
            JOIN destinations d ON t.destination_id = d.id
        """
        params = []
        if status:
            query += " WHERE b.status = ?"
            params.append(status)
        query += " ORDER BY b.created_at DESC;"
        return execute_query(query, params, fetch_all=True)

    @staticmethod
    def cancel_booking(booking_id: int, user_id: int | None = None):
        """Cancels a booking and automatically restores seats."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("SELECT * FROM bookings WHERE id = ? AND user_id = ?;", (booking_id, user_id))
            else:
                cursor.execute("SELECT * FROM bookings WHERE id = ?;", (booking_id,))
                
            booking = cursor.fetchone()
            if not booking:
                raise ValueError("Không tìm thấy đơn đặt chỗ hoặc bạn không có quyền hủy.")

            if booking["status"] == "CANCELLED":
                return True

            if booking["status"] == "COMPLETED":
                raise ValueError("Tour đã hoàn thành. Không thể hủy đơn.")

            total_passengers = booking["num_adults"] + booking["num_children"]

            # 1. Update booking status
            cursor.execute("UPDATE bookings SET status = 'CANCELLED' WHERE id = ?;", (booking_id,))

            # 2. Restore seats
            cursor.execute(
                """UPDATE tour_schedules 
                   SET available_seats = available_seats + ?, status = 'OPEN' 
                   WHERE id = ?;""",
                (total_passengers, booking["schedule_id"])
            )

        return True

    @staticmethod
    def update_booking_status(booking_id: int, new_status: str):
        valid_statuses = ["PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"]
        if new_status not in valid_statuses:
            raise ValueError(f"Trạng thái không hợp lệ. Cho phép: {valid_statuses}")
            
        if new_status == "CANCELLED":
            return BookingService.cancel_booking(booking_id)
            
        execute_query("UPDATE bookings SET status = ? WHERE id = ?;", (new_status, booking_id), commit=True)
        return True

