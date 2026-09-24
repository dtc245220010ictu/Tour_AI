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

        return execute_query(
            """INSERT INTO feedbacks (user_id, tour_id, booking_id, rating, comment)
            VALUES (?, ?, ?, ?, ?);""",
            (user_id, tour_id, booking_id, rating, comment.strip()),
            commit=True
        )

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

