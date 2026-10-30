# Flyway Commands & CLI Tooling

Flyway provides a consistent set of lifecycle commands regardless of whether you invoke it through the Standalone CLI, Maven plugin, Gradle plugin, Docker container, or native Java API.

---

## The 7 Core Flyway Commands

| Command | Purpose | Production Safe? |
| :--- | :--- | :--- |
| **`migrate`** | Applies all pending migrations | Yes |
| **`info`** | Prints migration status, versions, and state | Yes |
| **`validate`** | Validates applied scripts against local files | Yes |
| **`baseline`** | Baselines an existing non-empty database | Yes (initial setup) |
| **`repair`** | Aligns checksums and removes failed rows | Use with caution |
| **`undo`** | Undoes the last versioned migration | Risky (requires Teams) |
| **`clean`** | Drops all schema objects in database | **NEVER in Production** |

---

## Command Deep Dive

### 1. `migrate`
Scans configured locations, checks `flyway_schema_history`, and applies pending scripts sequentially:

```bash
flyway -url=jdbc:postgresql://localhost:5432/app_db \
       -user=app_user -password=secret migrate
```

### 2. `info`
Generates a formatted summary displaying each script's category, version, description, type, installed date, state (`Success`, `Pending`, `Future`, `Out of Order`), and execution duration.

### 3. `validate`
Verifies that:
- Checksums of local scripts match records in `flyway_schema_history`.
- Applied migrations have not been deleted from the classpath.
- No unexpected changes were introduced out of order.

### 4. `baseline`
Initializes `flyway_schema_history` with an initial baseline record (e.g., version `1`), marking all migrations up to that version as already applied. Critical for legacy databases transitioning to Flyway.

### 5. `repair`
- Removes failed migration entries from `flyway_schema_history` (for databases without transactional DDL).
- Re-aligns checksums of applied scripts with local files after deliberate manual fixes.

---

## Build Tool Integration (Gradle & Maven)

### Gradle (`build.gradle.kts`)
```kotlin
plugins {
    id("org.flywaydb.flyway") version "10.10.0"
}

flyway {
    url = "jdbc:postgresql://localhost:5432/app_db"
    user = System.getenv("DB_USER")
    password = System.getenv("DB_PASSWORD")
    locations = arrayOf("filesystem:src/main/resources/db/migration")
}
```

Run migrations via Gradle:
```bash
./gradlew flywayMigrate
./gradlew flywayInfo
```

### Maven (`pom.xml`)
```xml
<plugin>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-maven-plugin</artifactId>
    <version>10.10.0</version>
    <configuration>
        <url>jdbc:postgresql://localhost:5432/app_db</url>
        <user>${env.DB_USER}</user>
        <password>${env.DB_PASSWORD}</password>
    </configuration>
</plugin>
```
