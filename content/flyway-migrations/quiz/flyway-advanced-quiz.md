## Q1
When introducing Flyway to an existing production database with tables already present, which command establishes a starting version without applying prior scripts?

### Option A
`flyway clean`

### Option B [CORRECT]
`flyway baseline`

### Option C
`flyway reset`

### Option D
`flyway snapshot`

### Explanation
`flyway baseline` initializes `flyway_schema_history` with an initial version baseline (e.g., version `1.0`), informing Flyway that existing database objects up to that version are already accounted for.

===

## Q2
Under the Expand and Contract pattern, how should a column rename be executed to ensure zero downtime during rolling deployments?

### Option A
Execute `ALTER TABLE RENAME COLUMN` directly in an early morning maintenance window.

### Option B
Drop the old column and create the new column in a single transactional script.

### Option C [CORRECT]
Add the new column, dual-write to both, migrate historical data, switch reads, and drop the old column in a subsequent release.

### Option D
Create an entirely new duplicate database and sync data asynchronously using CDC.

### Explanation
Direct column renames immediately break queries executed by currently running instances of the older application version ($N$). Splitting the change across releases (Expand -> Transition -> Contract) maintains continuous backward compatibility.

===

## Q3
Why can running Flyway across Windows and Linux environments cause unexpected checksum validation failures?

### Option A
Linux file systems require lowercase filenames for all migrations.

### Option B [CORRECT]
Differing line endings (Windows CRLF vs Unix LF) change the raw byte stream, producing different CRC32 checksums.

### Option C
Flyway encrypts checksums using OS-specific machine hardware keys.

### Option D
Flyway only supports Windows when using PowerShell scripts.

### Explanation
Flyway computes a CRC32 checksum on raw file bytes. If Git checks out files with `CRLF` on Windows and `LF` on Linux without a `.gitattributes` rule (`*.sql text eol=lf`), the resulting checksums will diverge and fail validation.

===

## Q4
In a standard Spring Boot application, when does Flyway execute database migrations by default?

### Option A
After the web server has started listening for incoming HTTP requests.

### Option B
Only when triggered manually through a Spring Boot Actuator endpoint.

### Option C [CORRECT]
Early during startup, before the JPA `EntityManagerFactory` and ORM mapping beans initialize.

### Option D
Asynchronously in a background worker thread after application startup completes.

### Explanation
Spring Boot's auto-configuration ensures Flyway runs before JPA/Hibernate beans initialize. This guarantees that table structures and columns exist before Hibernate performs validation or schema checks.

===

## Q5
In a database that lacks transactional DDL, what occurs if statement 3 in a 5-statement migration script throws an error?

### Option A
The database automatically rolls back statements 1 and 2.

### Option B [CORRECT]
Statements 1 and 2 remain permanently applied, and the migration is recorded as failed in the schema history.

### Option C
Flyway drops the entire database to prevent schema corruption.

### Option D
Flyway comments out statement 3 and proceeds to run statements 4 and 5.

### Explanation
In non-transactional DDL engines (such as MySQL prior to 8.0), DDL statements trigger implicit commits. If an error occurs halfway through a script, previous statements remain committed in the database, necessitating manual remediation and `flyway repair`.
