# Spring Boot & Java-Based Migrations

Spring Boot provides native auto-configuration for Flyway. When the dependency is detected, Spring Boot automatically triggers Flyway migrations before the JPA `EntityManagerFactory` initializes.

---

## Spring Boot Auto-Configuration

Add the Flyway dependencies to your project (Maven or Gradle):

```kotlin
// build.gradle.kts
implementation("org.flywaydb:flyway-core")
implementation("org.flywaydb:flyway-database-postgresql")
```

### Essential `application.yml` Properties

```yaml
spring:
  flyway:
    enabled: true
    locations:
      - classpath:db/migration
    baseline-on-migrate: true
    baseline-version: "0"
    validate-on-migrate: true
    out-of-order: false
```

- **`baseline-on-migrate`:** If `true`, Flyway automatically calls `baseline` if running against an existing non-empty database without a schema history table.
- **`out-of-order`:** Allows older migrations to be applied if they were merged after a newer version was already executed. Recommended only in specific multi-branch environments.

---

## Programmatic Java Migrations

While plain SQL is the preferred medium for 95% of migrations, certain operations require programmatic execution:
- Encrypting or hashing existing sensitive data using external key vaults.
- Complex data transformations requiring third-party Java libraries.
- Migrating binary payloads stored in database LOB columns.

### Implementing `BaseJavaMigration`

To create a Java migration, extend `BaseJavaMigration` and place it in the configured migration package (e.g., `db.migration`):

```java
package db.migration;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

public class V2_0__HashApiTokens extends BaseJavaMigration {

    @Override
    public void migrate(Context context) throws Exception {
        var connection = context.getConnection();
        
        try (var selectStmt = connection.prepareStatement(
                "SELECT id, plain_token FROM api_keys WHERE token_hash IS NULL");
             var updateStmt = connection.prepareStatement(
                "UPDATE api_keys SET token_hash = ? WHERE id = ?");
             var rs = selectStmt.executeQuery()) {
             
            while (rs.next()) {
                long id = rs.getLong("id");
                String raw = rs.getString("plain_token");
                String hashed = computeSha256(raw);
                
                updateStmt.setString(1, hashed);
                updateStmt.setLong(2, id);
                updateStmt.addBatch();
            }
            updateStmt.executeBatch();
        }
    }

    private String computeSha256(String input) {
        // Compute cryptographic hash
        return Integer.toHexString(input.hashCode());
    }
}
```

---

## Flyway Lifecycle Callbacks

Callbacks allow you to execute custom logic at specific lifecycle points:
- **Events:** `beforeMigrate`, `afterMigrate`, `beforeEachMigrate`, `afterEachMigrate`.
- **SQL Callbacks:** Simply place a script named `beforeMigrate.sql` or `afterMigrate.sql` in `db/migration`.
- **Java Callbacks:** Implement `org.flywaydb.core.api.callback.Callback` to execute Java routines, such as notifying audit queues or clearing cache stores after a migration runs.
