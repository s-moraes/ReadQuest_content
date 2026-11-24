# Backups & Point-in-Time Recovery (PITR) Internals

`pg_dump` is great for small logical exports, but large production databases rely on **physical base backups + WAL archiving** for **Point-in-Time Recovery (PITR)**.

---

## How PITR Works

Physical recovery combines two ingredients:
1. **Base Backup (`pg_basebackup` / `pgBackRest`):** A consistent binary snapshot of the data directory (`PGDATA`).
2. **Archived WAL Stream (`archive_command`):** Every 16 MB WAL segment shipped continuously to S3/object storage.

```text
Base Backup (02:00 UTC) + WAL Segments (02:00 -> 14:32)
   ---> Replay stops at '2026-11-24 14:32:05 UTC'
   ---> Database restored 1 second BEFORE accidental DELETE!
```

---

## Configuring Recovery Targets

When restoring a cluster with tools like `pgBackRest` or native `recovery_target_time` in `postgresql.conf`:

```ini
restore_command = 'pgbackrest --stanza=main archive-get %f "%p"'
recovery_target_time = '2026-11-24 14:32:05+00'
recovery_target_action = 'promote'
```

PostgreSQL replays WAL records sequentially from the base backup until the exact timestamp, then promotes the server to accept writes.

---

## Why Logical `pg_dump` Is Not Enough at Scale

| Aspect | `pg_dump` (Logical) | Physical + PITR (`pgBackRest`) |
| :--- | :--- | :--- |
| **Granularity** | Point-in-snapshot when dump started | **Any second** up to latest archived WAL |
| **Restore Speed** | Slow (rebuilds all indexes via SQL) | Fast (copies raw data files + WAL replay) |
| **Production Rule** | Good for small DBs & schema exports | **Mandatory** for zero-data-loss recovery |

> A backup you have never restored is not a backup. Automate regular **restore drills** into a staging environment to verify both `RPO` and `RTO`.
