---
name: database-design
description: Design normalized relational database schemas from approved requirements and architectural models, including tables, relationships, constraints, indexes, and SQL schemas.
---
# Database Design Skill

## Objective
Transform approved software requirements and architectural specifications into an optimal, normalized relational database design (MySQL/SQLite) complete with constraints, indexes, and full SQL schema scripts.

## Inputs
Read:
- `docs/requirements.md`
- `docs/architecture.md`
- `docs/uml-diagrams.md`

## Process
1. **Identify Entities:** Extract all core domain entities from requirements and ERD.
2. **Define Attributes & Types:** Select appropriate data types (VARCHAR, INT, DECIMAL, DATETIME, TEXT, BOOLEAN) ensuring storage efficiency and precision.
3. **Establish Relationships & Cardinality:** Define 1-1, 1-N, and N-M relationships with explicit Foreign Keys.
4. **Normalization:** Apply 1NF, 2NF, and 3NF normalization principles to eliminate data redundancy and update anomalies.
5. **Keys & Constraints:**
   - Define Primary Keys (AUTO_INCREMENT/INTEGER PRIMARY KEY).
   - Define Foreign Keys with referential integrity (`ON DELETE CASCADE` or `RESTRICT`).
   - Define NOT NULL, UNIQUE, and CHECK constraints.
6. **Indexing Strategy:**
   - Index search columns (e.g. tour title, destination, price, departure_date).
   - Index foreign keys and frequently filtered columns.
7. **RAG & Chatbot Retrieval Optimization:** Ensure indexes support efficient multi-criteria search queries from the RAG retriever (destination, price range, duration, available seats).
8. **Generate SQL Schema Script:** Produce clean, production-ready DDL scripts compatible with MySQL and SQLite.

## Rules
- Do not write application source code.
- Do not invent undocumented fields.
- Strictly adhere to naming conventions (snake_case for tables and columns).
- Ensure foreign keys and indexes are explicitly defined.

## Outputs
Create:
- `docs/database-design.md`
- `database/schema.sql`

## Verification
- Verify that every functional requirement's data persistence is covered.
- Verify normalization up to 3NF.
- Verify that capacity constraints (`available_seats`, `total_seats`) are supported by constraints and atomic operations.

