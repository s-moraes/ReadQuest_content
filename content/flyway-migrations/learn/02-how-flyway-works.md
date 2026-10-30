# How Flyway Works Under the Hood

When Flyway points to a database, it ensures that the physical schema matches the exact migration state declared in the codebase. It achieves this without relying on complex external agents or proprietary daemons.

---

## The Migration Lifecycle

Whenever Flyway runs (via CLI, build plugin, or application startup), it follows a deterministic 5-step sequence:

1. **Metadata Table Inspection:** Flyway queries the database for its tracking table, by default named `flyway_schema_history`. If it does not exist, Flyway creates it.
2. **Filesystem / Classpath Scanning:** Flyway scans designated migration folders (e.g., `db/migration`) for migration scripts.
3. **Validation:** Flyway calculates the checksum of local scripts and compares them against previously recorded entries in `flyway_schema_history`. If an applied script was modified, validation fails immediately.
4. **Execution:** Flyway applies any pending migrations in ascending version order, each within an isolated transaction (when supported by the database).
5. **History Recording:** Flyway logs the migration result, execution duration, and CRC32 checksum into the history table.

---

## Anatomy of `flyway_schema_history`

The `flyway_schema_history` table is the single source of truth for your database evolution:

```sql
SELECT installed_rank, version, description,
       type, checksum, success
FROM flyway_schema_history
ORDER BY installed_rank;
```

| Column | Purpose |
| :--- | :--- |
| `installed_rank` | Global sequence order of execution |
| `version` | Semantic version string (e.g., `1.0.1`) |
| `description` | Human-readable description from filename |
| `type` | `SQL`, `JDBC`, etc. |
| `script` | Relative filename of the migration |
| `checksum` | CRC32 hash of the script body |
| `installed_by` | Database user who executed the script |
| `installed_on` | Timestamp of execution |
| `execution_time` | Milliseconds taken to execute |
| `success` | Boolean flag (`true` / `false`) |

---

## Distributed Concurrency and Locking

In modern cloud environments, multiple microservice replicas or containers boot simultaneously. To prevent race conditions where multiple nodes attempt to execute the same DDL script at once, Flyway enforces table-level locking:

- **Lock Acquisition:** Before running migrations, Flyway locks `flyway_schema_history` using database-specific locking mechanisms (e.g., `SELECT ... FOR UPDATE` or explicit advisory locks in PostgreSQL).
- **Sequential Execution:** The node holding the lock executes pending scripts.
- **Fail-Safe Release:** Once migrations finish (or fail), Flyway releases the lock, allowing waiting nodes to wake up, re-validate, and discover all scripts are already applied.
