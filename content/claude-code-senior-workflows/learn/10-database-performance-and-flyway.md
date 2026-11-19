# Database Performance Tuning: N+1 Queries, EXPLAIN & Flyway

In Java backend systems, most production slowdowns come from the database layer: Hibernate N+1 queries, missing composite indexes, or Flyway migrations that acquire an `ACCESS EXCLUSIVE` lock on a hot table. Claude Code can diagnose and fix these issues rapidly when paired with **read-only PostgreSQL access** and **Testcontainers**.

---

## 1. Hunting Hibernate N+1 Queries

Instead of guessing from JPA entity annotations, enable Hibernate SQL statistics in a targeted test run and pipe the output to Claude Code:

```bash
./mvnw test -pl order-service -Dtest=OrderControllerIT \
  -Dspring.jpa.properties.hibernate.generate_statistics=true \
  | grep -E "Hibernate:|JDBC statements" \
  | claude -p "Identify N+1 queries and propose @EntityGraph or JOIN FETCH fixes."
```

**Guardrail:** Remind Claude in `CLAUDE.md` that `JOIN FETCH` on paginated queries (`Pageable`) causes Hibernate to paginate in memory (`HHH90003004`)—so paginated endpoints should use `@BatchSize` or two-step ID-fetch queries instead.

---

## 2. `EXPLAIN ANALYZE` with a Read-Only DB Role

When connected to a staging/local PostgreSQL instance via a `SELECT`-only role (`default_transaction_read_only = on`), Claude Code can:
1. Run `EXPLAIN (ANALYZE, BUFFERS)` on slow queries.
2. Spot `Seq Scan` bottlenecks, stale planner estimates, or non-sargable predicates (`WHERE LOWER(email) = ...`).
3. Propose a targeted partial or composite index (`CREATE INDEX CONCURRENTLY ...`).

---

## 3. Zero-Downtime Flyway Migrations

Add explicit Flyway safety rules to your Java `CLAUDE.md`:
- **Never** rewrite or edit an already-applied `V<N>__*.sql` migration (checksum mismatch).
- **Always** create a new `V<next>__*.sql` script.
- On large PostgreSQL tables, forbid `ADD COLUMN ... NOT NULL` without a `DEFAULT` or `CREATE INDEX` without `CONCURRENTLY` (with `lock_timeout` set).
- Verify every new migration by running `./mvnw verify -Dit.test=SchemaMigrationIT -q` against a real PostgreSQL Testcontainer.
