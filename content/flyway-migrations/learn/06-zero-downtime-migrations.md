# Zero-Downtime Schema Evolution

In continuous deployment environments, applications update without downtime. During rolling updates or blue-green deployments, the previous application version ($N$) and the new version ($N+1$) run concurrently against the exact same database.

---

## The Golden Rule of Backward Compatibility

> Every database schema change must be backward-compatible with the currently running version of the application.

Destructive changes executed prematurely will instantly break running instances:
- Renaming column `phone` to `phone_number` causes version $N$ to fail queries.
- Adding a `NOT NULL` column without a default value breaks `INSERT` statements from version $N$.
- Dropping a column still referenced in version $N$'s queries results in fatal SQL errors.

---

## The Expand and Contract Pattern

To execute breaking schema changes with zero downtime, split the transformation into three or four separate releases:

```text
Step 1: EXPAND            Step 2: TRANSITION        Step 3: CONTRACT
(Deploy V1 Migrations)    (Deploy App v2)           (Deploy V2 Migrations)
+--------------------+    +--------------------+    +--------------------+
|  users             |    |  users             |    |  users             |
|  - full_name       |    |  - full_name       |    |  - first_name      |
|  - first_name (new)|    |  - first_name      |    |  - last_name       |
|  - last_name  (new)|    |  - last_name       |    +--------------------+
+--------------------+    +--------------------+
```

### Phase 1: Expand (Release 1)
- Add the new columns as nullable or with safe defaults.
- Deploy migration `V2_0__add_first_and_last_name.sql`.
- Both old and new application instances function without issues.

### Phase 2: Dual-Writing & Backfill (Release 2)
- Update application code to read from the old column, but write to both old and new columns.
- Run a background data migration script to populate `first_name` and `last_name` from existing `full_name` records.

### Phase 3: Switch Reading (Release 3)
- Deploy application version that reads exclusively from `first_name` and `last_name`.
- Remove all references to `full_name` from application source code.

### Phase 4: Contract (Release 4)
- Run Flyway migration `V3_0__drop_full_name_column.sql`.
- The unused column is dropped safely because no running application instance references it.

---

## Safe DDL Practices in PostgreSQL

Certain DDL commands take exclusive table locks (`ACCESS EXCLUSIVE`) that block read and write traffic on high-throughput tables:

- **Creating Indexes:** Never use `CREATE INDEX` on large tables. Always execute `CREATE INDEX CONCURRENTLY` (Flyway allows disabling transaction wrapping with `@flyway:executeInTransaction false`).
- **Adding Constraints:** Add `CHECK` constraints with `NOT VALID`, then validate them in a subsequent statement to avoid locking the table during full-table verification.
