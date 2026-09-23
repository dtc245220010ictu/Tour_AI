---
name: product-retrieval
description: Retrieve relevant products or tour packages from relational database using structured intent and parameterized SQL queries to guarantee zero SQL injection and zero hallucination.
---
# Product Retrieval Skill

## Objective
Execute precise, safe, parameterized database queries against MySQL/SQLite to fetch only existing tour products that have available seats matching the user's intent.

## Inputs
- Structured intent JSON from `question_analyzer`.

## Process
1. Build parameterized SQL query base.
2. Apply active status filters.
3. Apply capacity constraints (`available_seats > 0`).
4. Apply category/destination, budget, and duration filters.
5. Limit number of results.

## Rules
- NEVER use SQL string concatenation.
- ALWAYS use parameterized queries (`?`).
- Never fabricate or guess products.

