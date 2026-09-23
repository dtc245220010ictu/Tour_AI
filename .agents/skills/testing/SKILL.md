---
name: testing
description: Plan, write, and execute automated test suites (unit, integration, and capacity checks) adhering to requirements and verifying zero-hallucination and overbooking prevention.
---
# Testing Skill

## Objective
Establish a rigorous quality assurance workflow that translates software requirements into concrete test scenarios, automated test cases, and execution reports.

## Workflow
Requirements
    ↓
Test Scenario
    ↓
Test Case
    ↓
Automated Test (pytest)
    ↓
Execution
    ↓
Result & Metrics
    ↓
Defect Reporting

## Inputs
Read:
- `docs/requirements.md`
- `docs/user-stories.md`
- `docs/acceptance-criteria.md`

## Process
1. **Develop Test Scenarios:** Map each Functional Requirement (FR-xxx) and Acceptance Criteria (AC-xxx) to test scenarios.
2. **Design Test Cases:** Detail preconditions, inputs, execution steps, expected outcomes, and boundary conditions.
3. **Implement Automated Tests in `tests/`:**
   - Unit tests for core services (Auth, Booking, Capacity Lock, Question Analysis, Retrieval, Context Builder).
   - Integration tests for Flask endpoints (`/tours`, `POST /booking/new/...`, `POST /api/chat`).
4. **Execute Test Suite:** Run tests via `pytest -v`.
5. **Analyze Failures:** Never modify tests merely to make them pass; verify if failure is a real defect in implementation.
6. **Produce Test Reports:** Generate structured test plan and execution report.

## Rules
- Do NOT alter tests just to pass; address root causes in application code if a defect is found.
- Ensure 100% test coverage for critical business logic:
  - Seat deduction and overbooking prevention.
  - Zero-hallucination when no tours match.
  - SQL injection immunity in tour retrieval.

## Outputs
Create:
- `docs/test-plan.md`
- `docs/test-report.md`
- Automated test scripts in `tests/`

