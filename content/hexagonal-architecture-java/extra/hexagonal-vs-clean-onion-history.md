# The Evolution of Decoupled Architectures

Over the past two decades, software engineering has witnessed an evolution of architectural patterns striving toward the same core goal: **freeing business logic from technological volatility**. Understanding the lineage from Hexagonal Architecture to Onion Architecture and Clean Architecture provides valuable perspective on modern software design.

---

## 1. 2005: Hexagonal Architecture (Alistair Cockburn)

Alistair Cockburn conceived Hexagonal Architecture (originally named **Ports and Adapters**) in 2005 to solve a common dilemma in object-oriented systems: business logic becoming entangled with user interfaces and database queries.

```text
Cockburn's Original Insight:
"Allow an application to equally be driven by users, programs, 
automated test, or batch scripts, and to be developed and tested in 
isolation from its eventual run-time devices and databases."
```

Why the hexagon shape? Cockburn selected the hexagon simply to provide enough geometric faces to visually represent multiple primary and secondary ports—not because the number six has mathematical significance.

---

## 2. 2008: Onion Architecture (Jeffrey Palermo)

In 2008, Jeffrey Palermo introduced **Onion Architecture**, building explicitly upon Cockburn's ports and adapters concept while emphasizing **Domain-Driven Design (DDD)** layers:

```text
                     [ ONION ARCHITECTURE ]
                 +----------------------------+
                 |       Infrastructure       |
                 |  +----------------------+  |
                 |  |   Application Core   |  |
                 |  |  +----------------+  |  |
                 |  |  | Domain Services|  |  |
                 |  |  |  +----------+  |  |  |
                 |  |  |  |  Domain  |  |  |  |
                 |  |  |  |  Model   |  |  |  |
                 |  |  |  +----------+  |  |  |
                 |  |  +----------------+  |  |
                 |  +----------------------+  |
                 +----------------------------+
```

Onion Architecture formalized concentric circular dependency rules:
- Dependencies point exclusively inward.
- The Domain Model sits at the absolute core.
- External infrastructure sits on the outer perimeter.

---

## 3. 2012: Clean Architecture (Robert C. Martin)

In 2012, Robert C. Martin ("Uncle Bob") synthesized Hexagonal Architecture, Onion Architecture, and Screaming Architecture into **Clean Architecture**:

- **Entities:** Enterprise business rules.
- **Use Cases:** Application-specific business rules.
- **Interface Adapters:** Controllers, Gateways, Presenters.
- **Frameworks & Drivers:** Web, Database, Devices, External Interfaces.

Clean Architecture popularized the term **The Dependency Rule**: source code dependencies must point only inward, toward higher-level policies.

---

## 4. Architectural Comparison Matrix

| Aspect | Hexagonal (Ports & Adapters) | Onion Architecture | Clean Architecture |
| :--- | :--- | :--- | :--- |
| **Origin Year** | 2005 (Alistair Cockburn) | 2008 (Jeffrey Palermo) | 2012 (Robert C. Martin) |
| **Primary Visual** | Hexagon with ports on faces | Concentric onion rings | Concentric circular layers |
| **Core Abstraction** | Ports (Input / Output) & Adapters | Domain Services & Interfaces | Use Cases & Interface Adapters |
| **Domain Coupling** | Highly flexible, pure domain core | Strictly coupled with DDD building blocks | Enterprise vs. Application business rules |
| **Delivery Model** | Symmetric handling of drivers & driven systems | Emphasizes UI on outside, DB on outside | Emphasizes Presenters, Controllers, Interactors |

Ultimately, whether you call it Hexagonal, Onion, or Clean Architecture, the fundamental principle is identical: **protect the domain core at all costs, invert external dependencies, and treat frameworks as interchangeable plugins.**
