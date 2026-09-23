---
name: documentation
description: Maintain comprehensive, synchronized project documentation including README, API specifications, deployment guides, user manuals, and architectural references adhering to implementation reality.
---
# Documentation Skill

## Objective
Produce clear, accurate, and actionable documentation that perfectly mirrors the actual implemented software, enabling developers, devops engineers, and end-users to understand, deploy, and operate the system effortlessly.

## Inputs
Read:
- Entire codebase (`app.py`, `routes/`, `services/`, `database/`, `tests/`)
- All approved design specifications in `docs/`

## Process
1. **README.md Creation/Update:**
   - Project overview, core features, architecture summary.
   - Prerequisites, installation, environment configuration, database setup.
   - Quickstart commands for running the app and executing automated tests.
   - Demo accounts and test queries.
2. **API Specification (`docs/api.md`):**
   - Endpoints list (`GET`, `POST`), URL parameters, request body schemas, response payloads, error status codes.
3. **Deployment Guide (`docs/deployment.md`):**
   - Production deployment guidelines using Gunicorn, Nginx, Docker, systemd, and MySQL configuration.
4. **User Guide (`docs/user-guide.md`):**
   - Step-by-step walkthrough for Customers (browsing, searching, chatbot consultation, booking, payments, reviews) and Staff/Admins (dashboard, tour CRUD, AI generator, feedback summarizer).

## Rules
- Strictly document implemented reality; never describe features that do not exist in code.
- Ensure all command lines and code snippets are copy-paste ready and tested.
- Maintain bilingual consistency or standard Vietnamese for user guides and technical documentation.

## Outputs
- `README.md`
- `docs/api.md`
- `docs/deployment.md`
- `docs/user-guide.md`

