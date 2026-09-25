---
name: tour-retrieval
description: Retrieve relevant tours and schedules from relational database using structured intent and parameterized SQL queries to guarantee zero SQL injection and zero hallucination.
---
# Tour / Product Retrieval Skill

## Objective
Execute precise, safe, parameterized database queries against MySQL/SQLite to fetch only existing tours that have available seats matching the user's intent.

## Inputs
- Structured intent JSON from `question_analyzer`.

## Process
1. Build parameterized SQL query base (`tours` joined with `destinations` and `tour_schedules`).
2. Apply filter for active tours (`tours.is_active = 1`).
3. Apply filter for open schedules with available seats (`schedules.available_seats > 0`).
4. Apply destination and regional filters.
5. Apply budget constraints (`base_price <= max_price`, `base_price >= min_price`).
6. Apply duration filter (`duration_days = ?` for a single day count; `duration_days BETWEEN ? AND ?` when the intent provides an inclusive range such as `[3, 4]`).
7. Apply sorting (by price, rating, or upcoming departure date).
8. Limit number of results (typically 3 to 5 results).

## Rules
- NEVER use string formatting/concatenation to construct SQL queries.
- ALWAYS use parameterized queries with placeholders (`?` or `%s`).
- Do not return inactive or deleted tours.
- Do not return tours with zero available seats (`available_seats = 0`).
- If no matching tours are found, return an empty list (`[]`). Never fabricate data.
- Alternative retrieval (`retrieve_alternative_tours`) runs after an empty strict search so the chatbot can honestly report "no exact match" AND introduce other real tours: it prefers tours from the requested destinations (lowest price first); if those destinations have no tours at all, it falls back to any available tour. It must return `[]` only when the database truly has no available tours.

