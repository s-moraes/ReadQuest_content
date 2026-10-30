## Q1
What table does Flyway use by default to track applied migrations and execution metadata?

### Option A
`database_changelog`

### Option B
`flyway_migration_state`

### Option C [CORRECT]
`flyway_schema_history`

### Option D
`schema_migrations_log`

### Explanation
Flyway records all executed migrations, script names, execution times, and CRC32 checksums in the `flyway_schema_history` table (which replaced the older `schema_version` table in Flyway 5).

===

## Q2
Which prefix designates a migration script that Flyway re-executes whenever its checksum changes?

### Option A
`V`

### Option B
`U`

### Option C
`B`

### Option D [CORRECT]
`R`

### Explanation
`R` denotes Repeatable migrations (e.g., `R__user_summary_view.sql`). Repeatable migrations run without a version number, execute after all pending versioned migrations have completed, and re-run whenever their checksum changes.

===

## Q3
In standard Flyway file naming conventions, what separator must be placed between the version number and description?

### Option A
A single underscore (`_`)

### Option B [CORRECT]
A double underscore (`__`)

### Option C
A single hyphen (`-`)

### Option D
A double hyphen (`--`)

### Explanation
Flyway strictly enforces a double underscore (`__`) between the version string and the descriptive title (such as `V1_2__create_orders_table.sql`). A single underscore inside the version part is parsed as a dot.

===

## Q4
What occurs when Flyway validates a codebase where an already-applied versioned migration script was modified?

### Option A
Flyway silently overrides the changes and continues running.

### Option B [CORRECT]
Flyway throws a checksum validation error and aborts execution.

### Option C
Flyway automatically rolls back the entire database to version 0.

### Option D
Flyway creates a duplicate entry in the history table.

### Explanation
Versioned migrations are immutable once executed. During validation, Flyway calculates the file's CRC32 checksum and compares it against the recorded checksum in `flyway_schema_history`. A mismatch triggers `ValidateFailedException` to prevent schema drift.

===

## Q5
Which command should be executed to remove failed migration records and re-align checksums in the history table?

### Option A
`flyway clean`

### Option B
`flyway baseline`

### Option C [CORRECT]
`flyway repair`

### Option D
`flyway info`

### Explanation
The `repair` command resets checksums of applied migrations to match modified local scripts and deletes failed migration entries (`success = false`) so they can be corrected and re-executed.
