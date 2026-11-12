# The Origins of Postgres: Stonebraker's Vision

PostgreSQL is one of the most successful open-source software projects in computer science history. Its roots stretch back to the mid-1970s and the visionary research of Turing Award laureate **Michael Stonebraker** at the University of California, Berkeley.

---

## From Ingres to Postgres (1973–1986)

In 1973, Stonebraker and Eugene Wong began development of **Ingres** (Interactive Graphics and Retrieval System) at UC Berkeley. Ingres was one of the earliest working implementations of Edgar F. Codd's revolutionary Relational Model, alongside IBM's System R.

While Ingres proved the viability of relational databases, by the mid-1980s Stonebraker observed significant limitations in pure relational systems:
- Real-world software needed to handle complex data types (coordinates, geometric shapes, CAD drawings, temporal spans).
- Relational tables lacked concepts of data inheritance and user-defined functions.
- Concurrency control in existing engines relied on heavy locking mechanisms that choked under write pressure.

In 1986, Stonebraker launched a successor project at UC Berkeley named **Postgres** (literally meaning *"Post-Ingres"*).

---

## Foundational Innovations of the Berkeley Postgres Project

Stonebraker's original 1986 paper, *The Design of Postgres*, laid out several revolutionary concepts that remain core to modern database theory:

```text
+--------------------------------------------------------------------------+
|                  Original Postgres Innovations (1986)                    |
|                                                                          |
|  1. Object-Relational Model: User-defined types, operators, and methods  |
|  2. Extensible Query Optimizer: Optimizer rules informed by user types   |
|  3. Time-Travel & Versioning: Storing historical versions of tuples      |
|  4. Active Rules Engine: Dynamic triggers executing procedural logic     |
+--------------------------------------------------------------------------+
```

Originally, Postgres used its own query language called **PostQUEL**. 

In 1994, two Berkeley graduate students, Andrew Yu and Jolly Chen, replaced PostQUEL with standard SQL. This fork was released to the public under the name **Postgres95**.

---

## 1996: The Birth of PostgreSQL

By 1996, the project had grown far beyond a university research prototype. A global community of open-source developers banded together, coordinating development internationally. 

Because the year 1995 was already in the past, the group renamed the project to **PostgreSQL** to emphasize its full compliance with the SQL standard, while retaining the historical shorthand **Postgres**.

```text
[1973] Ingres (UC Berkeley)
   │
   ▼
[1986] Postgres (Post-Ingres, Michael Stonebraker)
   │
   ▼
[1994] Postgres95 (Andrew Yu & Jolly Chen add SQL)
   │
   ▼
[1996] PostgreSQL 6.0 (Global Development Group formed)
   │
   ▼
[Present] PostgreSQL 16+ (Gold standard open-source enterprise database)
```

---

## The Turing Award Legacy

In 2014, the Association for Computing Machinery (ACM) awarded Michael Stonebraker the **A.M. Turing Award** (the "Nobel Prize of Computing") citing his foundational contributions to the concepts and practices underlying modern database systems.

Unlike many open-source projects that eventually fell under the control of single commercial entities, PostgreSQL remains strictly governed by the non-profit **PostgreSQL Global Development Group**, ensuring it will forever remain free, open, and community-driven.
