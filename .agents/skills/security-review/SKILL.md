---
name: security-review
description: Audit software applications for cybersecurity vulnerabilities including SQL Injection, Cross-Site Scripting (XSS), Secrets Exposure, Authentication & Authorization flaws, and LLM-specific vulnerabilities.
---
# Security Review Skill

## Objective
Conduct an exhaustive cybersecurity audit of the application source code, API contracts, database operations, and external AI integrations to ensure production-grade security posture.

## Audit Checklist
1. **SQL Injection (SQLi):** Ensure 100% of database interactions use parameterized queries or safe ORM calls. Forbid string interpolation in SQL.
2. **Cross-Site Scripting (XSS):** Verify that all dynamic user inputs rendered into HTML templates are escaped by default (Jinja2 auto-escaping) and client-side JS avoids unsafe `innerHTML` injection.
3. **Cross-Site Request Forgery (CSRF):** Verify session protection on state-modifying requests.
4. **Authentication & Password Storage:** Verify password hashing algorithm (bcrypt / pbkdf2 with high work factor). Check session expiration and brute-force mitigation.
5. **Authorization (RBAC):** Check role-based access control decorators (`@roles_required`) on administrative and staff endpoints.
6. **Secrets & Credentials Management:** Ensure API keys (Gemini API Key, Flask Secret Key, DB credentials) reside solely in environment variables and are excluded by `.gitignore`. Check that client-side JS never accesses secrets.
7. **Input Validation & Sanitization:** Check boundary and type checks on all request payloads (numeric ranges, string lengths, SQL injection payloads).
8. **Information Leakage:** Ensure production error handlers suppress debug stack traces and internal schema paths.
9. **LLM & RAG Security:** Verify prompt injection resistance, strict grounding rules, and that LLMs have zero direct database access.

## Rules
- Do NOT modify application code during review.
- Provide concrete evidence for each audit checkpoint.
- Classify vulnerabilities by severity (CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL).

## Outputs
Create:
- `docs/security-review.md`
