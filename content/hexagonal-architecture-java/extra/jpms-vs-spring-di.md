# JPMS Strong Encapsulation vs. Reflection-Based DI

Many Java enterprise architectures attempt to maintain clean separation solely through dependency injection frameworks like Spring Boot or Google Guice. However, physical module boundaries using the **Java Platform Module System (JPMS)** provide guarantees that runtime DI frameworks cannot match.

---

## 1. The Illusion of Package Encapsulation

In classic Java (prior to Java 9), all classes on the classpath share a flat visibility space:
- Marking a class `public` makes it accessible to **every other class on the entire classpath**.
- Marking a class `package-private` (no modifier) restricts access to the exact same package—but any developer can create a class in `package com.example.domain` from another JAR and immediately access those package-private internals.

```text
Classpath (Flat Visibility):
+-------------------------------------------------------------+
| JAR A (Framework): can instantiate or access ANY public     |
| class in JAR B (Domain), even classes intended to be hidden!|
+-------------------------------------------------------------+
```

---

## 2. Strong Encapsulation in JPMS

JPMS introduces a two-tier encapsulation model:
1. **Explicit Exports:** A module only exposes packages that it explicitly names in `exports <package>;`.
2. **Compile-Time Rejection:** If a module tries to import a class from an unexported package, `javac` rejects the compilation.
3. **Runtime Reflection Guard:** Even if reflection (`Class.forName(...)`, `setAccessible(true)`) is attempted, the JVM throws an `InaccessibleObjectException` unless the module explicitly `opens` the package to the caller.

```java
// module-info.java
module dev.davivieira.topologyinventory.domain {
    // Only exports entity and value object APIs
    exports dev.davivieira.topologyinventory.domain.entity;
    exports dev.davivieira.topologyinventory.domain.vo;

    // Internal helper classes and validators remain completely invisible
    // to both framework and application modules!
}
```

---

## 3. Comparison Matrix: JPMS vs Traditional Framework DI

| Dimension | Conventional Spring Boot / Java | Modular Hexagonal with JPMS |
| :--- | :--- | :--- |
| **Boundary Enforcement** | Convention & code reviews (easily broken). | **Compiler & JVM bytecode verification**. |
| **Cyclic Dependencies** | Permitted (often creates tangled circular graphs). | **Strictly forbidden**; build fails if cycles exist. |
| **Startup Overhead** | High reflection scanning during classpath indexing. | Zero reflection scanning; resolved at module boot. |
| **Framework Lock-In** | Domain code littered with `@Component`, `@Autowired`. | Domain code is 100% pure Java POJO (`java.base`). |
| **Tooling & Build** | Simple flat Maven pom. | Multi-module Maven setup with `module-info.java`. |

By combining JPMS modularity at compile time with Quarkus build-time CDI for production wiring, software architects achieve the ultimate balance: mathematical boundary guarantees with cloud-native runtime speed.
