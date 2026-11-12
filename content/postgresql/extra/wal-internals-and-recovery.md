# Under the Hood: Write-Ahead Log (WAL) & Crash Recovery

How can PostgreSQL promise that once your application receives a `COMMIT` acknowledgment, your data will never be lost—even if someone immediately pulls the physical power cord from the server rack?

The answer lies in **Write-Ahead Logging (WAL)**.

---

## The Durability Conundrum

In an ACID database, data pages live in memory inside the **Shared Buffer Pool**.

Writing an entire 8KB data page to disk on every single transaction `COMMIT` would be catastrophically slow:
- Disk pages are scattered randomly across the storage drive.
- Updating one row might require updating multiple index pages and table heap pages simultaneously (random I/O).
- Random disk writes choke storage controllers and degrade throughput to a crawl.

Instead of writing dirty data pages immediately to disk, PostgreSQL writes an **append-only binary record** of the exact delta change to the Write-Ahead Log.

---

## The Golden Rule of WAL

> **No data page modified in memory can be written to disk until the corresponding WAL record describing the change has been flushed to persistent storage.**

Because WAL records are written **sequentially** to disk, modern NVMe SSDs and disk controllers can append them in fractions of a millisecond with minimal latency.

```text
[ Client Tx ] ---> COMMIT
                         │
                         ▼
        1. Write delta to WAL Buffer (RAM)
                         │
                         ▼
        2. Flush WAL Buffer to disk (Sequential I/O via fsync)
                         │
                         ▼
        3. Acknowledge COMMIT to Client  <-- Data is now 100% durable!
                         │
        (Asynchronously in background)
                         ▼
        4. BgWriter flushes dirty 8KB Heap Pages to disk (Random I/O)
```

---

## Log Sequence Numbers (LSN)

Every single byte appended to the WAL stream is identified by a 64-bit integer called a **Log Sequence Number (LSN)**:
- Example: `0/16B3748`
- Every 8KB database page header contains the LSN of the most recent WAL record that modified that specific page (`pd_lsn`).

During normal operations, the **Checkpointer** periodically writes all dirty buffers in memory to disk and records a **Checkpoint Record** into the WAL log.

---

## Crash Recovery: What Happens After a Power Outage?

When the PostgreSQL server boots back up after an abnormal shutdown:

1. **Locate Last Checkpoint:** It reads the `pg_control` file to find the LSN of the last valid Checkpoint record.
2. **REDO Phase:** Starting from the checkpoint LSN, PostgreSQL reads through every subsequent WAL record sequentially and compares the record's LSN against the target page's `pd_lsn`:
   - If the page on disk has a lower LSN, PostgreSQL reapplies the delta change (**REDO**).
   - If the page already has that LSN or higher, it is skipped.
3. **Consistency Reached:** Once all WAL records up to the end of the log are replayed, all uncommitted in-flight transactions are marked as aborted, and PostgreSQL opens port 5432 for incoming connections.

This deterministic replay guarantees zero data loss for committed transactions.
