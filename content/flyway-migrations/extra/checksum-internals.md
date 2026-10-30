# CRC32 Checksum Traps & Line Endings

One of the most perplexing errors development teams encounter with Flyway is a `ValidateFailedException` occurring in CI/CD environments even though "nobody changed the SQL script." The culprit almost invariably boils down to invisible line-ending characters.

---

## How Flyway Computes Checksums

Flyway calculates a 32-bit Cyclic Redundancy Check (`CRC32`) for every SQL migration script:

1. Flyway opens the migration file as a stream.
2. It strips leading and trailing whitespace and comments (depending on configuration).
3. The remaining byte stream is fed into `java.util.zip.CRC32`.
4. The resulting 32-bit signed integer is stored in `flyway_schema_history.checksum`.

Because CRC32 operates directly on raw bytes, a file saved with Windows line endings (`\r\n` / CRLF) generates an entirely different checksum than the exact same file saved with Unix line endings (`\n` / LF).

---

## The Cross-Platform Trap

Consider this real-world scenario:

```text
Developer (Windows, CRLF)        CI/CD Runner (Linux, LF)
Commit V1__init.sql (CRLF)       Clones repo with LF
Calculated Checksum: 12345678    Calculated Checksum: 87654321
                                  --> VALIDATION FAILS!
```

If a developer runs Flyway locally on Windows and applies `V1__init.sql`, the CRC32 computed from `CRLF` bytes is written to the shared database. When a Linux CI pipeline runs `flyway validate`, Git clones the repository using Unix `LF` line endings, causing an immediate checksum mismatch!

---

## The Permanent Fix: `.gitattributes`

To prevent cross-platform checksum drift, enforce LF line endings across all migration SQL files in the root `.gitattributes` file:

```text
# Enforce Unix line endings for all Flyway migration scripts
*.sql text eol=lf
```

After committing this rule, normalize the repository once:
```bash
git add --renormalize .
git commit -m "chore: normalize line endings to LF"
```

Additionally, ensure your editor does not insert a Byte Order Mark (`BOM`) when saving UTF-8 SQL files, as UTF-8 BOM bytes (`0xEF, 0xBB, 0xBF`) will also alter the computed CRC32 hash.
