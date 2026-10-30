# Zero-Downtime Blue-Green Pipeline

In mission-critical enterprise systems, running migrations during application startup on production pods introduces significant risks: startup latency spikes, race conditions, and lack of rollback boundaries.

---

## The Migration Runner Pattern

Instead of letting web application instances execute migrations upon booting, decouple database schema migration into an isolated, short-lived CI/CD task:

```text
[ Git Tag: v2.4.0 ]
       |
       v
+-----------------------------+
| CI: Flyway Migrate Runner   |  <-- Single container / Kubernetes Job
| Runs backward-compatible DDL|
+-----------------------------+
       | (Success)
       v
+-----------------------------+
| CD: Blue/Green Deployment   |
| Boots Green Pods (v2.4.0)   |
| Health checks pass          |
| Router switches traffic     |
+-----------------------------+
```

---

## Kubernetes Job Example

In Kubernetes, Flyway runs as a dedicated `Job` or `PreSync` hook in ArgoCD before the application `Deployment` updates:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: flyway-migration-job
spec:
  template:
    spec:
      containers:
        - name: flyway
          image: flyway/flyway:10.10.0
          command: ["flyway", "migrate"]
          env:
            - name: FLYWAY_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: jdbc_url
            - name: FLYWAY_USER
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: username
            - name: FLYWAY_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: password
      restartPolicy: OnFailure
  backoffLimit: 2
```

---

## Architectural Rules for CI/CD Migrations

1. **Dedicated Database User:** The migration runner should authenticate with a dedicated DDL user account having schema alter privileges, while running application instances authenticate with a restricted DML-only user (`SELECT`, `INSERT`, `UPDATE`, `DELETE`).
2. **Lock Timeout Configuration:** Set a strict statement and lock timeout (e.g., `SET lock_timeout = '5s'`) to prevent migration scripts from queueing behind long-running analytical queries.
3. **Automated Schema Linting:** Integrate tools like `sqlfluff` or custom Flyway check scripts into pull request validations to catch forbidden statements (such as `DROP COLUMN` or unindexed foreign keys) before they reach production branches.
