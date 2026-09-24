"""
Analytics and Reporting Service.
Calculates revenue, top selling tours, and schedule occupancy rates.
"""

from database.db import execute_query

class AnalyticsService:
    @staticmethod
    def get_dashboard_stats():
        revenue_row = execute_query(
            "SELECT COALESCE(SUM(total_amount), 0) AS total_revenue FROM bookings WHERE status IN ('CONFIRMED', 'COMPLETED');",
            fetch_one=True
        )
        total_revenue = revenue_row["total_revenue"] if revenue_row else 0

        bookings_row = execute_query(
            "SELECT COUNT(*) AS total_bookings FROM bookings;",
            fetch_one=True
        )
        total_bookings = bookings_row["total_bookings"] if bookings_row else 0

        customers_row = execute_query(
            "SELECT COUNT(*) AS total_customers FROM users WHERE role = 'CUSTOMER';",
            fetch_one=True
        )
        total_customers = customers_row["total_customers"] if customers_row else 0

        tours_row = execute_query(
            "SELECT COUNT(*) AS total_tours FROM tours WHERE is_active = 1;",
            fetch_one=True
        )
        total_tours = tours_row["total_tours"] if tours_row else 0

        return {
            "total_revenue": total_revenue,
            "total_bookings": total_bookings,
            "total_customers": total_customers,
            "total_tours": total_tours
        }

    @staticmethod
    def get_top_selling_tours(limit: int = 5):
        return execute_query(
            """SELECT t.id, t.title, t.base_price, d.name AS destination_name,
                      COUNT(b.id) AS booking_count,
                      COALESCE(SUM(b.total_amount), 0) AS tour_revenue
               FROM tours t
               JOIN destinations d ON t.destination_id = d.id
               LEFT JOIN tour_schedules s ON t.id = s.tour_id
               LEFT JOIN bookings b ON s.id = b.schedule_id AND b.status IN ('CONFIRMED', 'COMPLETED')
               WHERE t.is_active = 1
               GROUP BY t.id
               ORDER BY booking_count DESC, tour_revenue DESC
               LIMIT ?;""",
            (limit,),
            fetch_all=True
        )

    @staticmethod
    def get_occupancy_rates():
        schedules = execute_query(
            """SELECT s.id, s.departure_date, s.return_date, s.total_seats, s.available_seats, s.status,
                      s.adult_price, s.child_price,
                      t.title AS tour_title
               FROM tour_schedules s
               JOIN tours t ON s.tour_id = t.id
               ORDER BY s.departure_date ASC;""",
            fetch_all=True
        )
        for s in schedules:
            booked_seats = s["total_seats"] - s["available_seats"]
            rate = (booked_seats / s["total_seats"] * 100) if s["total_seats"] > 0 else 0
            s["booked_seats"] = booked_seats
            s["occupancy_rate"] = round(rate, 1)
        return schedules

