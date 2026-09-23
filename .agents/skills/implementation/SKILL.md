---
name: implementation
description: Implement software features faithfully adhering to approved requirements, architectural guidelines, and database specifications with clean code, proper error handling, and robust tests.
---
# Implementation Skill

## Objective
Write maintainable, secure, and production-ready code in Python Flask that faithfully implements the approved specifications without introducing undocumented assumptions or altering architecture.

## Inputs
Read:
- `docs/requirements.md`
- `docs/architecture.md`
- `docs/database-design.md`
- `docs/acceptance-criteria.md`

## Process
1. **Read Specification:** Review relevant Functional Requirements and Acceptance Criteria before implementing.
2. **Understand Architecture:** Locate target component in the layered architecture (Route -> Service -> Database).
3. **Understand Database:** Inspect schema, data types, constraints, and relationships.
4. **Implement Core Logic:**
   - Write clean, modular Python functions/classes with type hints and docstrings.
   - Implement input validation and error handling.
   - Use parameterized SQL queries exclusively to prevent SQL injection.
   - Ensure atomic database transactions for critical operations (e.g. seat reservation).
5. **Run Linter / Syntax Check:** Verify syntax and code quality.
6. **Run Tests:** Execute automated unit and integration tests.
7. **Review Diff:** Inspect changed files to ensure no regressions or unintended edits.

## Rules
- Do not change requirements or architecture without approval.
- Do not hard-code API keys, secrets, or database credentials.
- If specification is insufficient or ambiguous, pause and request human guidance rather than guessing.
- Never let AI LLM services access database directly.

## Outputs
- Source code in `models/`, `services/`, `routes/`, `templates/`, `static/`, and `app.py`.
- Automated test suites in `tests/`.

## Verification
- Code passes linting/syntax checks.
- All unit and integration tests pass cleanly.
- Error handling returns user-friendly messages without leaking sensitive stack traces.

