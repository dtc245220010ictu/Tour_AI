"""
Tour Retriever for TourAI RAG Pipeline.
Translates structured intent into parameterized SQL queries to retrieve matching tours.
Zero SQL Injection. Zero Hallucination.
"""

from database.db import execute_query

class TourRetriever:
    @staticmethod
    def retrieve_tours(intent: dict, limit: int = 4) -> list:
        """
        Executes safe parameterized SQL query based on intent.
        Returns only tours that are active and have open schedules with available seats.
        """
        query = """
            SELECT t.id, t.title, t.slug, t.description, t.duration_days, t.duration_nights,
                   t.base_price, t.transportation, t.image_url,
                   d.name AS destination_name, d.region AS destination_region,
                   MIN(s.departure_date) AS next_departure,
                   SUM(s.available_seats) AS total_available_seats
            FROM tours t
            JOIN destinations d ON t.destination_id = d.id
            JOIN tour_schedules s ON t.id = s.tour_id
            WHERE t.is_active = 1
              AND s.status = 'OPEN'
              AND s.available_seats > 0
        """
        params = []

        # 1. Filter by destinations
        destinations = intent.get("destinations", [])
        if destinations:
            placeholders = ", ".join(["?"] * len(destinations))
            query += f" AND d.name IN ({placeholders})"
            params.extend(destinations)

        # 2. Filter by max budget
        max_price = intent.get("max_price")
        if max_price is not None and max_price > 0:
            query += " AND t.base_price <= ?"
            params.append(float(max_price))

        # 3. Filter by min budget
        min_price = intent.get("min_price")
        if min_price is not None and min_price > 0:
            query += " AND t.base_price >= ?"
            params.append(float(min_price))

        # 4. Filter by duration: integer -> exact match,
        #    range like [3, 4] -> inclusive BETWEEN filter
        duration_days = intent.get("duration_days")
        if isinstance(duration_days, (list, tuple)):
            bounds = sorted({int(d) for d in duration_days if d})
            if len(bounds) == 1:
                query += " AND t.duration_days = ?"
                params.append(bounds[0])
            elif len(bounds) > 1:
                query += " AND t.duration_days BETWEEN ? AND ?"
                params.extend([bounds[0], bounds[-1]])
        elif duration_days is not None and duration_days > 0:
            query += " AND t.duration_days = ?"
            params.append(int(duration_days))

        # 5. Grouping
        query += " GROUP BY t.id"

        # 6. Sorting
        sort_by = intent.get("sort_by")
        if sort_by == "price_asc":
            query += " ORDER BY t.base_price ASC"
        elif sort_by == "price_desc":
            query += " ORDER BY t.base_price DESC"
        else:
            query += " ORDER BY next_departure ASC, t.base_price ASC"

        # 7. Limit
        query += " LIMIT ?;"
        params.append(limit)

        results = execute_query(query, params, fetch_all=True)
        return results if results else []

    @staticmethod
    def retrieve_alternative_tours(intent: dict, limit: int = 3) -> list:
        """
        When strict criteria find no tours, retrieve the closest available tours
        (e.g. relaxing price or duration constraint) so the chatbot can politely
        report "no exact match" while still introducing other real tours.
        Preference order:
          1. Tours in the requested destinations (sorted by lowest price).
          2. If those destinations have no tours at all -> ANY available tour,
             so the customer is never left with a dead end.
        """
        def _fetch(destinations: list) -> list:
            query = """
                SELECT t.id, t.title, t.slug, t.description, t.duration_days, t.duration_nights,
                       t.base_price, t.transportation, t.image_url,
                       d.name AS destination_name, d.region AS destination_region,
                       MIN(s.departure_date) AS next_departure,
                       SUM(s.available_seats) AS total_available_seats
                FROM tours t
                JOIN destinations d ON t.destination_id = d.id
                JOIN tour_schedules s ON t.id = s.tour_id
                WHERE t.is_active = 1
                  AND s.status = 'OPEN'
                  AND s.available_seats > 0
            """
            params = []
            if destinations:
                placeholders = ", ".join(["?"] * len(destinations))
                query += f" AND d.name IN ({placeholders})"
                params.extend(destinations)

            query += " GROUP BY t.id ORDER BY t.base_price ASC LIMIT ?;"
            params.append(limit)
            return execute_query(query, params, fetch_all=True) or []

        destinations = intent.get("destinations", [])
        alternatives = _fetch(destinations)
        if not alternatives and destinations:
            # Requested destinations have no tours at all -> suggest any tour.
            alternatives = _fetch([])
        return alternatives

