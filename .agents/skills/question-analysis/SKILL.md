---
name: question-analysis
description: Analyze natural language user queries in Vietnamese and extract structured search intent parameters including destinations, budget limits, duration, and preferences.
---
# Question Analysis Skill

## Objective
Transform raw natural-language questions from users into a structured intent JSON object containing normalized search criteria suitable for database queries.

## Inputs
- Natural language query string (Vietnamese).

## Outputs
Structured intent JSON with the following fields:
- `destinations`: list of destination names mentioned (e.g. `["Hạ Long", "Đà Nẵng"]`).
- `min_price`: minimum price in VND or null.
- `max_price`: maximum price in VND or null.
- `duration_days`: list or int of days requested (e.g. `2`, `3`).
- `keywords`: key travel terms extracted (e.g. `["biển", "du thuyền", "nghỉ dưỡng"]`).
- `sort_by`: sorting preference (`"price_asc"`, `"price_desc"`, or `null`).

## Rules
- Do not invent destinations not mentioned or strongly implied.
- Do not guess price constraints if the user did not specify budget.
- Normalize Vietnamese monetary expressions to numeric VND:
  - "dưới 5 triệu" / "dưới 5tr" / "dưới 5 củ" -> `max_price: 5000000`
  - "khoảng 3-4 triệu" -> `min_price: 3000000, max_price: 4000000`
  - "khoảng 5 triệu" / "tour 5 triệu" / "tôi có 5 triệu" (budget with no explicit prefix) -> `max_price: 5000000`
  - "ít nhất 3 ngày" -> `duration_days: 3`
  - "3-4 ngày" / "từ 3 đến 4 ngày" -> `duration_days: [3, 4]` (inclusive range)
- Handle diacritics and non-diacritic inputs gracefully ("da lat" -> "Đà Lạt").
- Match destinations and keywords as whole words only: accent-stripped "khoảng" -> "khoang" must never trigger keyword "hoa", otherwise the query is wrongly mapped to Đà Lạt and valid budget questions return zero tours.

