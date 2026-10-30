# Introduction to Database Migrations

Software applications evolve continuously, and with them, the underlying database schemas must also adapt. Managing database schema changes across development, staging, and production environments reliably is one of the most critical challenges in software engineering.

---

## The Problem with Manual Database Changes

In early software projects, developers often applied schema modifications manually via SQL consoles or shared unversioned scripts:

- **Environment Drift:** Staging might have columns that production lacks.
- **Human Error:** Forgetting to run a script during deployment leads to runtime crashes (`Table 'users' doesn't have column 'phone'`).
- **Audit Deficit:** Nobody knows when a table was modified, by whom, or for which release.
- **No Rollback Strategy:** Manual rollbacks are error-prone and often destroy customer data.

---

## What is Evolutionary Database Design?

Coined by Martin Fowler and Pramod Sadalage, Evolutionary Database Design treats database schemas as version-controlled artifacts that evolve incrementally alongside application source code.

```text
+-----------------------+     +-----------------------+
|  Application Code     |     |  Database Schema      |
|  Git Commit: e4f2a1b  | <-> |  Migration: V3__add   |
|  Release: v1.4.0      |     |  Status: Applied (OK) |
+-----------------------+     +-----------------------+
```

Every database modification—adding a table, altering a column, creating an index—is captured as an immutable, timestamped or numbered script stored directly in the application's source repository.

---

## State-Based vs Migration-Based Approaches

Database tooling generally falls into two distinct philosophies:

| Feature | State-Based (Declarative) | Migration-Based (Imperative) |
| :--- | :--- | :--- |
| **Philosophy** | Define target schema state | Define delta scripts (V1, V2) |
| **Tools** | Liquibase Diff, SSDT, Prisma | Flyway, Liquibase, DbUp |
| **Data Migration** | Complex data transforms | Straightforward SQL DML |
| **Determinism** | Engine decides the path | Developer decides exact steps |
| **Control** | Lower control over DDL | Total control over exact SQL |

Flyway embraces the **migration-based** approach: you write plain SQL scripts describing transition steps, and Flyway guarantees they run deterministically in the correct order.

---

## Why Choose Flyway?

Flyway is an open-source database migration tool favored for its simplicity, speed, and focus on raw SQL:

1. **Plain SQL First:** No cumbersome XML or YAML abstractions required.
2. **Deterministic Execution:** Uses an internal metadata table to verify checksums and track applied scripts.
3. **Cross-Platform:** Available as a standalone CLI, Maven/Gradle plugin, and native Java API.
4. **Spring Boot Native:** Auto-configures out of the box upon application startup.
