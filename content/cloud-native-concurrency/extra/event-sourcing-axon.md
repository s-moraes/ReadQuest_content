# Event-Sourced Banking Service with Axon

Traditional relational banking applications store account balances as a mutable numeric column in a database table:

```sql
UPDATE accounts SET balance = balance - 100 WHERE id = 'acc-882';
```

In high-concurrency cloud environments with distributed microservices, this approach forces services to acquire exclusive pessimistic database locks, creating severe throughput bottlenecks and making historical audits extraordinarily difficult.

---

## Architectural Blueprint

By pairing **Command Query Responsibility Segregation (CQRS)** with **Event Sourcing** via the **Axon Framework**, the banking service eliminates row-level write contention by recording immutable state transitions into an append-only event store.

```text
[ Client ]
    |
    v (1. Issue Command: DebitAccountCommand)
[ Account Aggregate (Command Model) ]
    |
    +---> Validates balance invariants
    |
    v (2. Apply Event: AccountDebitedEvent)
[ Event Store (Append-Only) ]
    |
    +---> Broadcasts to Projections (Async)
    |
    v (3. Update Materialized View)
[ Account Summary View (Read Model / Elastic / Postgres) ]
```

---

## Step 1: The Command Aggregate

The Aggregate Root is the transactional boundary. In Axon, it enforces domain rules and emits events without knowing about read models or database schemas:

```java
@Aggregate
public class BankAccountAggregate {

    @AggregateIdentifier
    private String accountId;
    private BigDecimal currentBalance;

    protected BankAccountAggregate() {}

    @CommandHandler
    public BankAccountAggregate(CreateAccountCommand cmd) {
        if (cmd.getInitialBalance().compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Initial balance cannot be negative");
        }
        apply(new AccountCreatedEvent(cmd.getAccountId(), cmd.getInitialBalance()));
    }

    @CommandHandler
    public void handle(DebitAccountCommand cmd) {
        if (this.currentBalance.compareTo(cmd.getAmount()) < 0) {
            throw new InsufficientFundsException("Insufficient funds for debit");
        }
        apply(new AccountDebitedEvent(this.accountId, cmd.getAmount()));
    }

    @EventSourcingHandler
    public void on(AccountCreatedEvent event) {
        this.accountId = event.getAccountId();
        this.currentBalance = event.getInitialBalance();
    }

    @EventSourcingHandler
    public void on(AccountDebitedEvent event) {
        this.currentBalance = this.currentBalance.subtract(event.getAmount());
    }
}
```

---

## Step 2: The Materialized Query Projection

While the command model appends events to the event store, an asynchronous event projector updates denormalized read-optimized tables:

```java
@Component
public class AccountBalanceProjection {

    private final AccountBalanceRepository repository;

    public AccountBalanceProjection(AccountBalanceRepository repository) {
        this.repository = repository;
    }

    @EventHandler
    public void on(AccountDebitedEvent event) {
        repository.findById(event.getAccountId()).ifPresent(view -> {
            view.setBalance(view.getBalance().subtract(event.getAmount()));
            view.setLastUpdated(Instant.now());
            repository.save(view);
        });
    }

    @QueryHandler
    public AccountBalanceDto handle(FindAccountBalanceQuery query) {
        return repository.findById(query.getAccountId())
            .map(view -> new AccountBalanceDto(view.getId(), view.getBalance()))
            .orElseThrow(() -> new AccountNotFoundException(query.getAccountId()));
    }
}
```

---

## Why This Architecture Thrives Under Concurrency

1. **Zero Row-Level Deadlocks:** The event store only receives `INSERT` statements. Append-only writes execute with minimal database locking compared to constant `UPDATE` statements on the same row.
2. **Complete Auditability:** Every transaction since account opening is permanently preserved in the event log. Regulatory compliance and dispute resolution become trivial.
3. **Independent Scalability:** Write workloads scale independently of read query traffic. Read projections can be mirrored across read replicas or distributed caches.
