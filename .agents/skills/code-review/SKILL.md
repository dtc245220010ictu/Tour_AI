---
name: code-review
description: Review software implementation against architectural patterns, requirements compliance, code quality, maintainability, performance, error handling, and test thoroughness.
---
# Code Review Skill

## Objective
Systematically evaluate the entire codebase to detect defects, requirement gaps, architectural drift, performance bottlenecks, and code smell without modifying source code.

## Evaluation Criteria
1. **Correctness:** Does the code perform the exact intended function?
2. **Requirements Compliance:** Are all functional requirements and acceptance criteria fulfilled? Are there invented features?
3. **Architecture Compliance:** Are layering boundaries respected? Does the route talk to service? Does service talk to data access? Is LLM isolated from database?
4. **Maintainability & Clean Code:** Naming conventions, function sizing, modularity, type hints, docstrings.
5. **Duplication:** DRY (Don't Repeat Yourself) principle adherence.
6. **Error Handling:** Graceful exception management without leaking internal stack traces.
7. **Database Access:** Safe parameterized queries, transaction atomicity, connection cleanup.
8. **Test Quality:** Independent, repeatable, comprehensive automated tests.

## Issue Classification
Classify all identified items into 4 severity levels:
- **CRITICAL:** Causes data corruption, security vulnerability, or complete system crash.
- **HIGH:** Broken core requirement, overbooking leak, or uncontrolled hallucination.
- **MEDIUM:** Suboptimal performance, missing index, or inconsistent error response.
- **LOW:** Code style inconsistency, minor formatting, or documentation typo.

## Rules
- Do NOT modify application code during review.
- Provide concrete evidence (file paths and line numbers) for each observation.
- Recommend actionable remedies for every identified issue.

## Outputs
Create or update:
- `docs/code-review.md`
