---
name: requirements-analysis
description: Analyze software requirements and transform natural-language requirements into structured functional requirements, non-functional requirements, user stories, acceptance criteria, and traceability information.
---
# Requirements Analysis Skill

## Objective
Analyze software requirements systematically and produce a structured specification suitable for subsequent architecture, database, implementation, and testing activities.

## Inputs
Read the following project artifacts when available:
- customer requirements (`docs/customer-requirement.md`)
- business requirements
- existing requirements documentation
- project constraints

## Process
### 1. Identify stakeholders
Identify all stakeholders relevant to the system (e.g. Tour Operator, Travel Consultant, Accountant, Tour Guide, Customer).

### 2. Identify actors
Identify actors interacting with the system directly or indirectly.

### 3. Identify functional requirements
Convert explicit business needs into functional requirements.
Use structured IDs:
- FR-001
- FR-002
- FR-003...

### 4. Identify non-functional requirements
Identify requirements related to:
- performance
- security
- reliability
- usability
- maintainability
- scalability
Use structured IDs:
- NFR-001
- NFR-002...

### 5. Identify business rules
List business rules explicitly stated by the requirements (e.g., booking slot limits, cancellation deadlines, deposit thresholds).
Do not invent business rules.

### 6. Identify assumptions
Separate assumptions from actual requirements.

### 7. Identify ambiguities
Identify requirements that are:
- ambiguous
- incomplete
- contradictory
- not testable

### 8. Create user stories
Use the standard format:
As a <role>,
I want <capability>,
so that <benefit>.

### 9. Create acceptance criteria
Each important user story must have testable acceptance criteria using Gherkin format:
Given <initial state>
When <action performed>
Then <expected result>.

### 10. Traceability
Every user story must be traceable to one or more functional requirements.

## Rules
- Do not write source code.
- Do not design the database.
- Do not design the architecture.
- Do not invent undocumented business rules.
- Clearly distinguish requirements from assumptions.
- Clearly identify missing information.

## Outputs
Create or update:
- `docs/requirements.md`
- `docs/user-stories.md`
- `docs/acceptance-criteria.md`
- `docs/requirements-issues.md`

## Verification
Before completing the task verify:
- All functional requirements have unique IDs;
- All non-functional requirements have unique IDs;
- User stories trace to requirements;
- Acceptance criteria are testable;
- Ambiguities and assumptions are explicitly documented.

