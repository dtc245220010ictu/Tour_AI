"""
Payment and Settlement Service.
Handles deposit recording, checkout confirmations, and payment history.
"""

from database.db import execute_query, get_db

class PaymentService:
    @staticmethod
    def record_payment(booking_id: int, amount: float, payment_method: str = "BANK_TRANSFER", transaction_id: str = None):
        if amount <= 0:
            raise ValueError("Số tiền thanh toán phải lớn hơn 0.")

        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check booking
            cursor.execute("SELECT * FROM bookings WHERE id = ?;", (booking_id,))
            booking = cursor.fetchone()
            if not booking:
                raise ValueError("Không tìm thấy đơn đặt tour.")

            # Record payment
            cursor.execute(
                """INSERT INTO payments 
                (booking_id, amount, payment_method, transaction_id, payment_status)
                VALUES (?, ?, ?, ?, 'SUCCESS');""",
                (booking_id, amount, payment_method, transaction_id)
            )
            payment_id = cursor.lastrowid

            # Update booking status to CONFIRMED
            cursor.execute("UPDATE bookings SET status = 'CONFIRMED' WHERE id = ?;", (booking_id,))

        return payment_id

    @staticmethod
    def get_payments_by_booking(booking_id: int):
        return execute_query(
            "SELECT * FROM payments WHERE booking_id = ? ORDER BY payment_date DESC;",
            (booking_id,),
            fetch_all=True
        )

