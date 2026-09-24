"""
Tour Guide Profile & Assignment Management Service (FR-017, FR-018 / CN6).
- Admin manages guide profiles and assignments (with schedule-overlap prevention).
- Guides view the assignment board read-only.
"""

from database.db import execute_query


class GuideService:
    @staticmethod
    def get_all_guides(include_inactive: bool = False):
        query = "SELECT * FROM tour_guides"
        if not include_inactive:
            query += " WHERE is_active = 1"
        query += " ORDER BY full_name ASC;"
        return execute_query(query, fetch_all=True)

    @staticmethod
    def get_guide_by_id(guide_id: int):
        return execute_query(
            "SELECT * FROM tour_guides WHERE id = ?;", (guide_id,), fetch_one=True
        )

    @staticmethod
    def create_guide(full_name: str, phone: str, email: str,
                     languages: str, experience_years: int, bio: str = ""):
        if not full_name or not phone or not email:
            raise ValueError("Họ tên, số điện thoại và email là bắt buộc.")
        duplicate = execute_query(
            "SELECT id FROM tour_guides WHERE phone = ? OR email = ?;",
            (phone.strip(), email.strip()), fetch_one=True
        )
        if duplicate:
            raise ValueError("Số điện thoại hoặc email đã tồn tại trong hồ sơ HDV.")
        return execute_query(
            """INSERT INTO tour_guides (full_name, phone, email, languages, experience_years, bio)
               VALUES (?, ?, ?, ?, ?, ?);""",
            (full_name.strip(), phone.strip(), email.strip(),
             (languages or "Tiếng Việt").strip(), int(experience_years), (bio or "").strip()),
            commit=True
        )

    @staticmethod
    def delete_guide(guide_id: int):
        """Soft-delete. Không cho xóa HDV đã có phân công (hủy phân công trước)."""
        assigned = execute_query(
            "SELECT id FROM guide_assignments WHERE guide_id = ? LIMIT 1;",
            (guide_id,), fetch_one=True
        )
        if assigned:
            raise ValueError("Hướng dẫn viên đã có phân công tour. Hãy hủy phân công trước khi xóa.")
        execute_query(
            "UPDATE tour_guides SET is_active = 0 WHERE id = ?;", (guide_id,), commit=True
        )

    @staticmethod
    def get_assignments(guide_id: int | None = None):
        """Bảng phân công (join HDV, lịch, tour, điểm đến)."""
        query = """
            SELECT ga.id, ga.role_in_tour, ga.notes, ga.created_at,
                   g.full_name AS guide_name, g.phone AS guide_phone,
                   g.languages AS guide_languages, g.experience_years,
                   s.departure_date, s.return_date, s.status AS schedule_status,
                   t.title AS tour_title, t.slug AS tour_slug,
                   d.name AS destination_name
            FROM guide_assignments ga
            JOIN tour_guides g ON ga.guide_id = g.id
            JOIN tour_schedules s ON ga.schedule_id = s.id
            JOIN tours t ON s.tour_id = t.id
            JOIN destinations d ON t.destination_id = d.id
        """
        params = ()
        if guide_id:
            query += " WHERE ga.guide_id = ?"
            params = (guide_id,)
        query += " ORDER BY s.departure_date ASC;"
        return execute_query(query, params, fetch_all=True)

    @staticmethod
    def get_all_schedules():
        return execute_query(
            """SELECT s.id, s.departure_date, s.return_date, s.status, t.title AS tour_title
               FROM tour_schedules s
               JOIN tours t ON s.tour_id = t.id
               ORDER BY s.departure_date ASC;""",
            fetch_all=True
        )

    @staticmethod
    def assign_guide(schedule_id: int, guide_id: int,
                     role_in_tour: str = "LEAD_GUIDE", notes: str = ""):
        """Phân công HDV - FR-018: từ chối phân công trùng lịch (overlap khoảng ngày)."""
        schedule = execute_query(
            "SELECT * FROM tour_schedules WHERE id = ?;", (schedule_id,), fetch_one=True
        )
        if not schedule:
            raise ValueError("Không tìm thấy lịch khởi hành.")
        guide = execute_query(
            "SELECT * FROM tour_guides WHERE id = ? AND is_active = 1;",
            (guide_id,), fetch_one=True
        )
        if not guide:
            raise ValueError("Không tìm thấy hướng dẫn viên.")

        duplicate = execute_query(
            "SELECT id FROM guide_assignments WHERE schedule_id = ? AND guide_id = ?;",
            (schedule_id, guide_id), fetch_one=True
        )
        if duplicate:
            raise ValueError("Hướng dẫn viên này đã được phân công cho đợt khởi hành này.")

        conflict = execute_query(
            """SELECT t.title, s.departure_date
               FROM guide_assignments ga
               JOIN tour_schedules s ON ga.schedule_id = s.id
               JOIN tours t ON s.tour_id = t.id
               WHERE ga.guide_id = ? AND ga.schedule_id != ?
                 AND s.departure_date <= ? AND s.return_date >= ?
               LIMIT 1;""",
            (guide_id, schedule_id, schedule["return_date"], schedule["departure_date"]),
            fetch_one=True
        )
        if conflict:
            raise ValueError(
                f"Trùng lịch! HDV \"{guide['full_name']}\" đã dẫn tour "
                f"\"{conflict['title']}\" khởi hành {conflict['departure_date']}."
            )

        valid_roles = ("LEAD_GUIDE", "ASSISTANT")
        if role_in_tour not in valid_roles:
            role_in_tour = "LEAD_GUIDE"
        return execute_query(
            "INSERT INTO guide_assignments (schedule_id, guide_id, role_in_tour, notes) VALUES (?, ?, ?, ?);",
            (schedule_id, guide_id, role_in_tour, (notes or "").strip()),
            commit=True
        )

    @staticmethod
    def remove_assignment(assignment_id: int):
        execute_query(
            "DELETE FROM guide_assignments WHERE id = ?;", (assignment_id,), commit=True
        )

    @staticmethod
    def get_guides_for_tour(tour_id: int):
        """HDV đã phân công cho các đợt khởi hành của tour (trang chi tiết tour - KH xem)."""
        return execute_query(
            """SELECT DISTINCT g.full_name, g.languages, g.experience_years, g.bio, ga.role_in_tour
               FROM guide_assignments ga
               JOIN tour_guides g ON ga.guide_id = g.id
               JOIN tour_schedules s ON ga.schedule_id = s.id
               WHERE s.tour_id = ? AND g.is_active = 1
               ORDER BY g.full_name ASC;""",
            (tour_id,), fetch_all=True
        )

