"""
Feedback and Review Management Service.
Collects ratings and reviews for tours and provides feedback logs.
"""

from database.db import execute_query

class FeedbackService:
    @staticmethod
    def create_feedback(user_id: int, tour_id: int, rating: int, comment: str, booking_id: int | None = None):
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError("Đánh giá sao phải nằm trong khoảng từ 1 đến 5.")
        if not comment or not comment.strip():
            raise ValueError("Vui lòng nhập nội dung đánh giá.")

        # Chỉ được đánh giá khi gắn với một đơn đã hoàn thành của chính khách hàng.
        # (Đơn đã hoàn thành = chuyến đi thực sự diễn ra -> mới có trải nghiệm để đánh giá.)
        if booking_id is not None:
            booking = execute_query(
                """SELECT b.id, b.user_id, b.status, s.tour_id
                   FROM bookings b
                   JOIN tour_schedules s ON b.schedule_id = s.id
                   WHERE b.id = ?;""",
                (booking_id,),
                fetch_one=True
            )
            if not booking:
                raise ValueError("Không tìm thấy đơn đặt tour cần đánh giá.")
            if booking["user_id"] != user_id:
                raise ValueError("Bạn chỉ có thể đánh giá đơn đặt tour của chính mình.")
            if booking["status"] != "COMPLETED":
                raise ValueError("Chỉ có thể đánh giá sau khi chuyến đi đã hoàn thành.")
            if FeedbackService.has_reviewed_booking(booking_id):
                raise ValueError("Bạn đã đánh giá chuyến đi này rồi. Cảm ơn bạn!")
            tour_id = booking["tour_id"]

        return execute_query(
            """INSERT INTO feedbacks (user_id, tour_id, booking_id, rating, comment)
            VALUES (?, ?, ?, ?, ?);""",
            (user_id, tour_id, booking_id, rating, comment.strip()),
            commit=True
        )

    @staticmethod
    def has_reviewed_booking(booking_id: int) -> bool:
        """True nếu đơn đặt tour này đã được khách hàng đánh giá."""
        row = execute_query(
            "SELECT 1 AS reviewed FROM feedbacks WHERE booking_id = ? LIMIT 1;",
            (booking_id,),
            fetch_one=True
        )
        return bool(row)

    @staticmethod
    def get_unreviewed_completed_bookings(user_id: int):
        """Các đơn đã hoàn thành nhưng khách hàng chưa gửi đánh giá (chờ đánh giá)."""
        return execute_query(
            """SELECT b.id, b.booking_code, b.schedule_id, b.status,
                      s.departure_date, s.return_date,
                      t.id AS tour_id, t.title AS tour_title, t.slug AS tour_slug,
                      t.image_url AS tour_image,
                      d.name AS destination_name
               FROM bookings b
               JOIN tour_schedules s ON b.schedule_id = s.id
               JOIN tours t ON s.tour_id = t.id
               JOIN destinations d ON t.destination_id = d.id
               WHERE b.user_id = ?
                 AND b.status = 'COMPLETED'
                 AND NOT EXISTS (SELECT 1 FROM feedbacks f WHERE f.booking_id = b.id)
               ORDER BY s.return_date DESC, b.id DESC;""",
            (user_id,),
            fetch_all=True
        )

    @staticmethod
    def get_reviewable_booking(user_id: int, tour_id: int):
        """Đơn đã hoàn thành của khách cho một tour cụ thể mà chưa được đánh giá.

        Dùng để hiển thị bảng đánh giá trên trang chi tiết tour đúng lúc
        chuyến đi đã kết thúc. Trả về None nếu chưa từng đi hoặc đã đánh giá.
        """
        return execute_query(
            """SELECT b.id, b.booking_code, b.schedule_id,
                      s.departure_date, s.return_date
               FROM bookings b
               JOIN tour_schedules s ON b.schedule_id = s.id
               WHERE b.user_id = ?
                 AND s.tour_id = ?
                 AND b.status = 'COMPLETED'
                 AND NOT EXISTS (SELECT 1 FROM feedbacks f WHERE f.booking_id = b.id)
               ORDER BY s.return_date DESC, b.id DESC
               LIMIT 1;""",
            (user_id, tour_id),
            fetch_one=True
        )

    @staticmethod
    def get_reviewed_booking_ids(user_id: int) -> set:
        """Tập id các đơn mà khách hàng đã gửi đánh giá (để đánh dấu trong lịch sử)."""
        rows = execute_query(
            """SELECT DISTINCT booking_id FROM feedbacks
               WHERE user_id = ? AND booking_id IS NOT NULL;""",
            (user_id,),
            fetch_all=True
        )
        return {r["booking_id"] for r in rows}

    @staticmethod
    def get_user_feedbacks(user_id: int):
        """Danh sách đánh giả của riêng khách hàng (kèm thông tin tour/đơn).

        Dùng cho màn hình "Tour của tôi" để khách xem, sửa hoặc xóa
        các đánh giá mình đã gửi sau các chuyến đi đã hoàn thành.
        """
        return execute_query(
            """SELECT f.id, f.tour_id, f.booking_id, f.rating, f.comment, f.created_at,
                      t.title AS tour_title, t.slug AS tour_slug, t.image_url AS tour_image,
                      b.booking_code, b.status AS booking_status,
                      s.departure_date, s.return_date,
                      d.name AS destination_name
               FROM feedbacks f
               JOIN tours t ON f.tour_id = t.id
               LEFT JOIN bookings b ON f.booking_id = b.id
               LEFT JOIN tour_schedules s ON b.schedule_id = s.id
               LEFT JOIN destinations d ON t.destination_id = d.id
               WHERE f.user_id = ?
               ORDER BY f.created_at DESC, f.id DESC;""",
            (user_id,),
            fetch_all=True
        )

    @staticmethod
    def get_feedback_by_id(feedback_id: int):
        """Lấy một đánh giá kèm thông tin tour để hiển thị form sửa."""
        return execute_query(
            """SELECT f.*, t.slug AS tour_slug, t.title AS tour_title,
                      b.booking_code
               FROM feedbacks f
               JOIN tours t ON f.tour_id = t.id
               LEFT JOIN bookings b ON f.booking_id = b.id
               WHERE f.id = ?;""",
            (feedback_id,),
            fetch_one=True
        )

    @staticmethod
    def _assert_owner(feedback_id: int, user_id: int):
        """Lấy đánh giá và bảo đảm nó thuộc về đang đăng nhập (chống thao tác chéo)."""
        feedback = FeedbackService.get_feedback_by_id(feedback_id)
        if not feedback:
            raise ValueError("Không tìm thấy đánh giá cần thao tác.")
        if feedback["user_id"] != user_id:
            raise ValueError("Bạn chỉ có thể thao tác trên đánh giá của chính mình.")
        return feedback

    @staticmethod
    def update_feedback(feedback_id: int, user_id: int, rating: int, comment: str):
        """Sửa đánh giá đã gửi (chỉ chủ đánh giá được sửa)."""
        FeedbackService._assert_owner(feedback_id, user_id)

        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError("Đánh giá sao phải nằm trong khoảng từ 1 đến 5.")
        comment = (comment or "").strip()
        if not comment:
            raise ValueError("Vui lòng nhập nội dung đánh giá.")

        execute_query(
            "UPDATE feedbacks SET rating = ?, comment = ? WHERE id = ?;",
            (rating, comment, feedback_id),
            commit=True
        )
        return True

    @staticmethod
    def delete_feedback(feedback_id: int, user_id: int):
        """Xóa đánh giá đã gửi (chỉ chủ đánh giá được xóa).

        Sau khi xóa, khách có thể đánh giá lại đơn đó vì đơn vẫn COMPLETED.
        """
        FeedbackService._assert_owner(feedback_id, user_id)
        execute_query("DELETE FROM feedbacks WHERE id = ?;", (feedback_id,), commit=True)
        return True

    @staticmethod
    def get_feedbacks_by_tour(tour_id: int):
        return execute_query(
            """SELECT f.*, u.full_name AS user_name
            FROM feedbacks f
            JOIN users u ON f.user_id = u.id
            WHERE f.tour_id = ?
            ORDER BY f.created_at DESC;""",
            (tour_id,),
            fetch_all=True
        )

    @staticmethod
    def get_all_feedbacks(limit: int = 100):
        return execute_query(
            """SELECT f.*, u.full_name AS user_name, t.title AS tour_title
            FROM feedbacks f
            JOIN users u ON f.user_id = u.id
            JOIN tours t ON f.tour_id = t.id
            ORDER BY f.created_at DESC
            LIMIT ?;""",
            (limit,),
            fetch_all=True
        )

