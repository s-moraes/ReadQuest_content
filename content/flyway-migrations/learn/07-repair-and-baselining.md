# Repairing, Baselining & Troubleshooting

Even in well-structured projects, database migrations occasionally fail due to syntax mistakes, merge conflicts, or unexpected production data anomalies. Knowing how to diagnose and recover from Flyway errors is an essential operational skill.

---

## Troubleshooting Common Errors

### 1. Checksum Mismatch (`ValidateFailedException`)
Occurs when the checksum of a local migration file does not match the checksum recorded in `flyway_schema_history`:

```text
Migration checksum mismatch for migration version 1.2
-> Applied to database : -182749102
-> Resolved locally    : 491827401
```

- **Cause:** A developer modified an already-applied versioned migration script (even changing whitespace or comments altered the hash).
- **Rule:** Never modify an applied versioned migration file. Always create a new versioned migration to apply changes.
- **Remedy:** If the change was purely cosmetic (comments/formatting), run `flyway repair` to update the checksum in `flyway_schema_history`.

---

## 2. Failed Migrations and Partial DDL

When a migration fails midway:
- **Transactional DDL (PostgreSQL, SQLite):** The transaction automatically rolls back. No partial tables remain, but the history table records `success = false`.
- **Non-Transactional DDL (MySQL, Oracle):** DDL statements execute an implicit commit. If statement 3 of 5 fails, statements 1 and 2 remain applied in the database!

### Recovery Steps:
1. Manually clean up any half-applied tables or columns in the database.
2. Run `flyway repair` to delete the failed row (`success = false`) from `flyway_schema_history`.
3. Fix the underlying SQL bug in the migration script.
4. Re-run `flyway migrate`.

---

## Baselining a Legacy Database

If an established database exists in production before introducing Flyway, running `V1__create_all_tables.sql` will fail because the tables already exist (`Relation already exists`).

```bash
flyway -baselineVersion=1.0 \
       -baselineDescription="Legacy Baseline" \
       baseline
```

1. Flyway writes an initial row to `flyway_schema_history` with version `1.0` and marks it as successful.
2. Any migration script with version $\le 1.0$ is completely ignored.
3. Subsequent scripts (e.g., `V1_1__add_user_settings.sql`) execute normally.

### Automated Baselining in Spring Boot

```yaml
spring:
  flyway:
    baseline-on-migrate: true
    baseline-version: "1.0"
    baseline-description: "Initial Baseline"
```

When `baseline-on-migrate` is `true`, Flyway checks if the target database contains tables. If tables exist without a `flyway_schema_history` table, it automatically triggers a baseline before running migrations.
