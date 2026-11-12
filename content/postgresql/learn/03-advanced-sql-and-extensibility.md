# Advanced SQL Features & Procedural Extensibility

PostgreSQL goes far beyond basic CRUD operations. It complies rigorously with ANSI SQL standards while offering expressive constructs that allow developers to push complex analytical, recursive, and business logic directly into the database engine.

---

## Common Table Expressions (CTEs) & Recursive Queries

Common Table Expressions (`WITH` queries) break down massive queries into readable, composable modular blocks. 

PostgreSQL also supports **Recursive CTEs**, which are essential for traversing graphs, organizational charts, category trees, and bill-of-materials structures:

```sql
-- Traversal of an organizational hierarchy tree
WITH RECURSIVE employee_hierarchy AS (
    -- 1. Base case: top-level executives (no manager)
    SELECT emp_id, name, manager_id, 1 AS depth
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- 2. Recursive step: employees reporting to previous level
    SELECT e.emp_id, e.name, e.manager_id, eh.depth + 1
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.emp_id
)
SELECT depth, name, emp_id, manager_id 
FROM employee_hierarchy 
ORDER BY depth, name;
```

Starting in PostgreSQL 12, developers can specify `MATERIALIZED` or `NOT MATERIALIZED` to guide whether PostgreSQL evaluates the CTE as an in-memory temporary table or inlines it directly into the main query plan.

---

## Analytical Window Functions

Window functions perform calculations across a set of table rows that are related to the current row, without collapsing them into a single row like regular `GROUP BY` aggregates.

```sql
SELECT 
    order_id,
    customer_id,
    order_date,
    total_amount,
    -- Running cumulative revenue per customer:
    SUM(total_amount) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date
    ) AS cumulative_spent,
    -- Rank customers within their geographic territory:
    DENSE_RANK() OVER (
        PARTITION BY territory_id 
        ORDER BY total_amount DESC
    ) AS territory_rank,
    -- Difference from previous order amount:
    total_amount - LAG(total_amount, 1, 0) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date
    ) AS amount_diff_from_last
FROM orders;
```

Common window functions include `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LEAD()`, `LAG()`, `FIRST_VALUE()`, and `NTILE()`.

---

## Extensible Types and Domains

Instead of relying solely on generic data types, PostgreSQL allows engineers to define domain-specific constraints and composite structures:

```sql
-- Define an ENUM with strict state values
CREATE TYPE order_status AS ENUM (
    'PENDING', 'PAID', 'SHIPPED', 'DELIVERED', 'REFUNDED'
);

-- Define a DOMAIN: a base type with an enforced CHECK constraint
CREATE DOMAIN us_postal_code AS VARCHAR(10)
CHECK (VALUE ~ '^\d{5}(-\d{4})?$');

-- Table using custom types
CREATE TABLE customer_shipments (
    shipment_id SERIAL PRIMARY KEY,
    status      order_status NOT NULL DEFAULT 'PENDING',
    zip_code    us_postal_code NOT NULL
);
```

---

## Table Inheritance

PostgreSQL implements object-oriented table inheritance, allowing derived tables to inherit all columns and constraints of a parent table:

```sql
CREATE TABLE media_content (
    content_id  BIGSERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Child table inheriting columns from media_content
CREATE TABLE video_clip (
    duration_seconds INT NOT NULL,
    video_codec      TEXT NOT NULL
) INHERITS (media_content);

-- Querying the parent automatically returns data from all inherited children:
SELECT * FROM media_content;

-- Querying ONLY the parent without children:
SELECT * FROM ONLY media_content;
```

---

## Procedural Languages & Stored Functions

PostgreSQL is not restricted to standard SQL. Its execution engine can run stored procedures and functions written in multiple languages:
- **PL/pgSQL:** Built-in procedural language supporting loops, variables, and exceptions.
- **PL/Python, PL/Perl, PL/v8 (JavaScript), PL/Rust:** Third-party extensions executing native scripts inside the transaction boundary.

```sql
-- Stored procedure with transactional control (COMMIT/ROLLBACK)
CREATE OR REPLACE PROCEDURE transfer_balance(
    sender_id   INT,
    receiver_id INT,
    amount      NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF amount <= 0 THEN
        RAISE EXCEPTION 'Transfer amount must be positive';
    END IF;

    UPDATE accounts 
    SET balance = balance - amount 
    WHERE id = sender_id AND balance >= amount;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Insufficient balance for sender %', sender_id;
    END IF;

    UPDATE accounts 
    SET balance = balance + amount 
    WHERE id = receiver_id;
END;
$$;
```

### Triggers
Triggers allow automated execution of PL/pgSQL functions before or after `INSERT`, `UPDATE`, `DELETE`, or `TRUNCATE` events, making them ideal for audit trails and cache invalidation.
