---
name: architecture-design
description: Design software architecture from approved requirements while preserving traceability and documenting architectural decisions.
---
# Architecture Design Skill

## Objective
Transform approved software requirements into a coherent, modular, and extensible software architecture suitable for implementation.

## Inputs
Read:
- `docs/requirements.md`
- `docs/user-stories.md`
- `docs/acceptance-criteria.md`
- `docs/uml-diagrams.md`
Only use approved requirements.

## Process
1. Identify architectural style (Layered Architecture, MVC, Modular Monolith with RAG AI subsystem).
2. Identify major components and layers (Presentation, Routing, Application/Service Layer, Data Access/ORM, Database, External AI Services).
3. Define responsibility of each component.
4. Define dependencies between components (Dependency Inversion, Loose Coupling).
5. Define communication protocols and interfaces between components.
6. Define data flow across layers for critical workflows.
7. Identify external systems (Google Gemini AI API, payment gateway simulators).
8. Identify security boundaries, authentication/authorization checkpoints, and secrets isolation.
9. Document architectural decisions using ADR (Architectural Decision Records) format.
10. Check requirements-to-architecture traceability.

## Rules
- Do not implement source code.
- Do not modify approved requirements.
- Do not introduce unnecessary technologies or over-engineering.
- Every major architectural decision must have an explicit rationale.

## Outputs
Create:
- `docs/architecture.md`
- `docs/architecture-decisions.md`

## Verification
Verify that every major functional requirement is supported by at least one architectural component.

