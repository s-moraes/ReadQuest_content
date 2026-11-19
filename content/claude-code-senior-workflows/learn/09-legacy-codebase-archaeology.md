# Legacy Codebase Archaeology & Strangler Fig Migrations

Most senior engineers do not spend their week on greenfield microservices—they inherit 10-year-old Java EE / Spring monoliths with sparse documentation, 2,000-line service classes, and minimal test coverage. **Claude Code** excels at accelerating **codebase archaeology** and executing safe **Strangler Fig** extractions—provided you never let it refactor untested code blindly.

---

## Step 1: Read-Only Archaeology (Mapping the Monolith)

Before changing a single line, use a read-only pass (or an isolated `Explore` subagent) to map entry points, hidden side effects, and database coupling:

```text
Trace all callers of LegacyBillingProcessor.processInvoice()
and map:
1. Every database table read or mutated (including native SQL).
2. External HTTP/SOAP/JMS calls inside the transaction.
3. Static singletons or ThreadLocal state it depends on.
Do NOT edit any files yet.
```

This produces a dependency map in minutes instead of hours of manual `Ctrl+Click` tracing.

---

## Step 2: Characterization Tests First (The Safety Harness)

Never refactor legacy code without a behavioral lock. Ask Claude Code to write **characterization tests** (golden-master tests) that capture *what the legacy code actually does today*—quirks and all—before you touch the implementation:

1. Mock only external network/queue boundaries (or use Testcontainers for the DB).
2. Assert exact return values, exceptions, and side-effect calls across happy paths and edge cases.
3. Run `./mvnw test -Dtest=LegacyBillingProcessorCharacterizationTest -q` until green.

---

## Step 3: Incremental Strangler Fig Extraction

Once the characterization tests pass, extract new behavior behind a clean interface (seam) without breaking callers:

```text
Legacy Caller ---> BillingFacade (Seam / Feature Flag)
                      ├── old path -> LegacyBillingProcessor
                      └── new path -> CleanHexagonalBillingService
```

- Let Claude Code generate the new `CleanHexagonalBillingService` + unit tests in an isolated `--worktree`.
- Keep the characterization test suite running against *both* implementations to prove parity before flipping the feature flag.
