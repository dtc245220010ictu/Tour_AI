"""
Refund Request Service - Phiếu báo hoàn tiền khi khách hủy tour.

Luồng nghiệp vụ:
1. Khách hủy tour đã thanh toán -> hệ thống tự tạo yêu cầu hoàn tiền ở
   trạng thái 'PENDING' với số tiền khách BÁO HOÀN TOÀN (bằng đúng số tiền
   khách đã thanh toán) kèm lý do hủy.
2. Kế toán / Admin duyệt ('APPROVED' -> sinh phiếu chi REFUND) hoặc từ chối
   ('REJECTED' kèm lý do).
3. Khách theo dõi được trạng thái trên trang "Tour của tôi".
"""

from datetime import datetime

from database.db import execute_query, get_db

# Chính sách hoàn tiền hủy tour: >=7 ngày: 90% | 3-6 ngày: 50% | <3 ngày: 0%
_POLICY = ((7, 90), (3, 50))


class RefundService:
    @staticmethod
    def get_paid_amount(booking_id: int) -> float:
        """Tổng tiền khách đã thanh toán thành công (không tính khoản hoàn)."""
        row = execute_query(
            """SELECT COALESCE(SUM(amount), 0) AS paid
               FROM payments
               WHERE booking_id = ? AND payment_status = 'SUCCESS'
                 AND payment_type != 'REFUND';""",
            (booking_id,), fetch_one=True
        )
        return float(row["paid"] or 0)

    @staticmethod
    def get_policy_percent(departure_date: str) -> int:
        """Tỷ lệ hoàn theo chính sách dựa trên số ngày còn lại trước khởi hành."""
        try:
            dep = datetime.strptime(departure_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return 90
        days_left = (dep - datetime.now().date()).days
        for threshold, percent in _POLICY:
            if days_left >= threshold:
                return percent
        return 0

    @staticmethod
    def create_request(booking_id: int, reason: str = "", request_amount: float | None = None):
        """Khách hủy tour -> tự tạo phiếu báo hoàn toàn (nếu đã thanh toán).

        Trả về yêu cầu vừa tạo, hoặc None nếu khách chưa thanh toán
        (không có gì để hoàn) hoặc đơn đã có yêu cầu rồi.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings WHERE id = ?;", (booking_id,))
            booking = cursor.fetchone()
            if not booking:
                raise ValueError("Không tìm thấy đơn đặt tour.")

            # Mỗi đơn chỉ có 1 yêu cầu hoàn tiền
            cursor.execute(
                "SELECT id FROM refund_requests WHERE booking_id = ?;", (booking_id,)
            )
            if cursor.fetchone():
                return None

            paid = float(cursor.execute(
                """SELECT COALESCE(SUM(amount), 0) AS paid FROM payments
                   WHERE booking_id = ? AND payment_status = 'SUCCESS'
                     AND payment_type != 'REFUND';""",
                (booking_id,),
            ).fetchone()["paid"] or 0)
            if paid <= 0:
                return None  # Chưa thanh toán -> không cần hoàn

            # BÁO HOÀN TOÀN: khách yêu cầu hoàn đúng số tiền đã trả
            amount = paid if request_amount is None else float(request_amount)
            if amount <= 0:
                raise ValueError("Số tiền yêu cầu hoàn phải lớn hơn 0.")
            if amount > paid:
                raise ValueError(
                    f"Số tiền yêu cầu hoàn ({amount:,.0f} đ) không thể vượt quá "
                    f"số tiền khách đã thanh toán ({paid:,.0f} đ)."
                )

            cursor.execute(
                """INSERT INTO refund_requests
                   (booking_id, paid_amount, request_amount, reason, status)
                   VALUES (?, ?, ?, ?, 'PENDING');""",
                (booking_id, paid, amount, (reason or "").strip()),
            )
            request_id = cursor.lastrowid

        return RefundService.get_request(request_id)

    @staticmethod
    def get_request(request_id: int):
        return execute_query(
            """SELECT r.*, b.booking_code, b.customer_name, b.customer_email,
                      b.customer_phone, b.user_id, t.title AS tour_title,
                      s.departure_date, u.full_name AS processed_by_name
               FROM refund_requests r
               JOIN bookings b ON r.booking_id = b.id
               JOIN tour_schedules s ON b.schedule_id = s.id
               JOIN tours t ON s.tour_id = t.id
               LEFT JOIN users u ON r.processed_by = u.id
               WHERE r.id = ?;""",
            (request_id,), fetch_one=True
        )

    @staticmethod
    def get_request_by_booking(booking_id: int):
        return execute_query(
            """SELECT r.*, u.full_name AS processed_by_name
               FROM refund_requests r
               LEFT JOIN users u ON r.processed_by = u.id
               WHERE r.booking_id = ?;""",
            (booking_id,), fetch_one=True
        )

    @staticmethod
    def get_requests(status: str | None = None):
        """Danh sách phiếu hoàn tiền cho Admin/Kế toán xử lý (PENDING lên đầu)."""
        query = """
            SELECT r.*, b.booking_code, b.customer_name, b.customer_email,
                   b.customer_phone, b.user_id, t.title AS tour_title,
                   s.departure_date, u.full_name AS processed_by_name,
                   COALESCE(rf.refunded_amount, 0) AS refunded_amount
            FROM refund_requests r
            JOIN bookings b ON r.booking_id = b.id
            JOIN tour_schedules s ON b.schedule_id = s.id
            JOIN tours t ON s.tour_id = t.id
            LEFT JOIN users u ON r.processed_by = u.id
            LEFT JOIN (
                SELECT booking_id, SUM(amount) AS refunded_amount FROM payments
                WHERE payment_status = 'SUCCESS' AND payment_type = 'REFUND'
                GROUP BY booking_id
            ) rf ON b.id = rf.booking_id
        """
        params = []
        if status:
            query += " WHERE r.status = ?"
            params.append(status)
        query += " ORDER BY CASE r.status WHEN 'PENDING' THEN 0 ELSE 1 END, r.requested_at DESC;"

        rows = execute_query(query, params, fetch_all=True)
        for row in rows:
            row["policy_percent"] = RefundService.get_policy_percent(row["departure_date"])
            row["policy_amount"] = row["paid_amount"] * row["policy_percent"] / 100
        return rows

    @staticmethod
    def get_customer_requests(user_id: int):
        """Các phiếu hoàn tiền của riêng khách hàng (để hiển thị trạng thái)."""
        return execute_query(
            """SELECT r.*, b.booking_code, t.title AS tour_title, s.departure_date
               FROM refund_requests r
               JOIN bookings b ON r.booking_id = b.id
               JOIN tour_schedules s ON b.schedule_id = s.id
               JOIN tours t ON s.tour_id = t.id
               WHERE b.user_id = ?
               ORDER BY r.requested_at DESC;""",
            (user_id,), fetch_all=True
        )

    @staticmethod
    def approve_request(request_id: int, approver_id: int,
                        decision_amount: float | None = None, notes: str = ""):
        """Kế toán/Admin DUYỆT hoàn tiền -> xuất quỹ (sinh phiếu chi REFUND).

        `decision_amount` mặc định = số tiền khách báo hoàn toàn.
        """
        # Import cục bộ để tránh vòng lặp import với AccountingService
        from services.accounting_service import AccountingService

        request = RefundService.get_request(request_id)
        if not request:
            raise ValueError("Không tìm thấy phiếu hoàn tiền cần duyệt.")
        if request["status"] != "PENDING":
            raise ValueError(
                f"Phiếu này đã được xử lý (trạng thái: {request['status']}), không thể duyệt lại."
            )

        amount = float(request["request_amount"] if decision_amount is None else decision_amount)
        if amount <= 0:
            raise ValueError("Số tiền hoàn trả phải lớn hơn 0.")

        # Xuất quỹ -> tạo phiếu chi REFUND (có kiểm tra chống hoàn vượt số đã trả)
        AccountingService.process_refund(
            booking_id=request["booking_id"],
            refund_amount=amount,
            accountant_user_id=approver_id,
            notes=notes or f"Duyệt hoàn tiền yêu cầu #{request_id}"
        )

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_query(
            """UPDATE refund_requests
               SET status = 'APPROVED', processed_by = ?, processed_at = ?,
                   decision_amount = ?, decision_notes = ?
               WHERE id = ?;""",
            (approver_id, now_str, amount, (notes or "").strip(), request_id),
            commit=True
        )
        return True

    @staticmethod
    def reject_request(request_id: int, approver_id: int, notes: str = ""):
        """Kế toán/Admin TỪ CHỐI hoàn tiền - bắt buộc có lý do."""
        request = RefundService.get_request(request_id)
        if not request:
            raise ValueError("Không tìm thấy phiếu hoàn tiền cần từ chối.")
        if request["status"] != "PENDING":
            raise ValueError(
                f"Phiếu này đã được xử lý (trạng thái: {request['status']}), không thể từ chối lại."
            )
        notes = (notes or "").strip()
        if not notes:
            raise ValueError("Vui lòng nhập lý do từ chối hoàn tiền để thông báo cho khách.")

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_query(
            """UPDATE refund_requests
               SET status = 'REJECTED', processed_by = ?, processed_at = ?, decision_notes = ?
               WHERE id = ?;""",
            (approver_id, now_str, notes, request_id),
            commit=True
        )
        return True
