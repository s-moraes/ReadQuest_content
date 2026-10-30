# Migration Types & Naming Conventions

Flyway organizes migration scripts based on strict file-naming conventions. Filenames instruct Flyway whether a script represents a one-time schema change, a repeatable database object, or a rollback.

---

## File Naming Anatomy

A standard Flyway migration filename consists of five distinct components:

```text
V2_1__create_customer_accounts_table.sql
^ ^  ^^ ^---------------------------^ ^^^
| |   |               |                |
| |   |               |                +-- File Suffix (.sql)
| |   |               +------------------- Description (words with _)
| |   +----------------------------------- Separator (strictly '__')
| +--------------------------------------- Version (numbers and dots/_)
+----------------------------------------- Prefix ('V', 'U', or 'R')
```

1. **Prefix:** `V` for Versioned, `U` for Undo, or `R` for Repeatable.
2. **Version:** Dots or underscores separate version parts (e.g., `1`, `1.2`, `2024.10.27.01`). Underscores in the version are converted to dots internally.
3. **Separator:** Exactly two underscores (`__`).
4. **Description:** Words separated by underscores, converted to spaces in reports.
5. **Suffix:** Configurable file extension, defaulting to `.sql`.

---

## 1. Versioned Migrations (`V`)

Versioned migrations are the foundation of Flyway:
- **Execution:** Run exactly once in ascending version order.
- **Immutability:** Once applied, the file's content must never change. Modifying an applied versioned script triggers a checksum validation error on next startup.
- **Use Cases:** Creating tables, altering columns, adding primary and foreign keys, schema drops.

```sql
-- V1_0__create_orders_table.sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 2. Repeatable Migrations (`R`)

Repeatable migrations do not have a version number:
- **Prefix:** Starts with `R__` (e.g., `R__customer_summary_view.sql`).
- **Execution Order:** Always executed after all pending versioned migrations have completed.
- **Re-Execution:** Flyway re-runs a repeatable migration whenever its checksum changes (i.e., when you edit the file).
- **Use Cases:** Recreating views, stored procedures, functions, and materialized view refresh triggers.

```sql
-- R__customer_summary_view.sql
CREATE OR REPLACE VIEW customer_summary_view AS
SELECT c.id, c.name, COUNT(o.id) AS total_orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name;
```

---

## 3. Undo Migrations (`U`)

Available in Flyway Teams/Enterprise editions:
- **Prefix:** `U` followed by the matching version (e.g., `U1_0__create_orders_table.sql`).
- **Purpose:** Reverses the effects of the corresponding versioned migration.
- **Note:** In production continuous delivery pipelines, forwards-only migrations (expanding and contracting) are generally favored over undo migrations to avoid catastrophic data loss.
