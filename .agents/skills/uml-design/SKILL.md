---
name: uml-design
description: Standardized skill to produce comprehensive UML diagrams and architectural models including Use Case, Class, Sequence, Activity, and Entity-Relationship Diagrams (ERD) using Mermaid and markdown specifications.
---
# UML Design Skill

## Objective
Transform approved software requirements and domain models into precise, standardized UML diagrams and visual design artifacts that guide implementation, database schema design, and technical documentation.

## Inputs
Read the following project artifacts:
- `docs/requirements.md`
- `docs/user-stories.md`
- `docs/acceptance-criteria.md`

## Process
### 1. Identify System Actors & Use Cases
- Map actors (Customer, Admin, Staff/Consultant, Accountant, Tour Guide, AI Engine) to high-level use cases.
- Group use cases into functional subsystems (Authentication, Tour & Schedule Management, Booking & Capacity Control, Payment, Guide Assignment, Feedback, Analytics, AI Services).
- Define include and extend relationships where applicable.

### 2. Design Class Diagram
- Model core entities, domain models, service layer, and controller classes.
- Detail attributes (with types and visibility), methods, and cardinality relationships (1-1, 1-N, N-M, inheritance).

### 3. Design Sequence Diagrams
- Map critical interactions step-by-step:
  - Tour Booking & Overbooking Prevention (Client -> Route -> BookingService -> TourSchedule -> DB).
  - AI RAG Chatbot Flow (User -> ChatAPI -> QuestionAnalyzer -> TourRetriever -> ContextBuilder -> GeminiService -> Response).

### 4. Design Activity Diagrams
- Diagram business logic workflows, branch conditions, and exception states (e.g. Tour booking with seat availability check, payment confirmation, or seat release upon cancellation).

### 5. Design Entity-Relationship Diagram (ERD)
- Define all database tables, columns, data types, primary keys (PK), foreign keys (FK), and referential integrity constraints.

## Rules
- Use valid Mermaid syntax supported by markdown previewers and documentation generators.
- Maintain 100% consistency with functional requirements (FR-xxx) and acceptance criteria (AC-xxx).
- Avoid vague or disconnected components; every entity must serve an approved requirement.

## Outputs
Create or update:
- `docs/uml-diagrams.md`

## Verification
- Verify that every actor in requirements has corresponding use cases.
- Verify that sequence diagrams accurately reflect the layered architecture.
- Verify that ERD matches the database requirements and capacity constraint rules.

