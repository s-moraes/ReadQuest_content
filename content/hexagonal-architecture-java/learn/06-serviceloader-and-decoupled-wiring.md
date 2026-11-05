# Decoupled Wiring with ServiceLoader & SPI

One of the greatest promises of Hexagonal Architecture is technology agnosticism: you should be able to run and test your core business logic completely disconnected from heavy frameworks. While dependency injection containers like Spring or Quarkus are standard in production, Java provides a native mechanism to wire hexagonal dependencies without any framework at all: the **Service Provider Interface (SPI)** powered by `java.util.ServiceLoader`.

---

## 1. The Challenge of Adapter Decoupling

In a hexagonal system:
1. Driving adapters (such as a CLI or REST controller) need an implementation of an **Input Port** / Use Case.
2. Input ports need an implementation of an **Output Port**.
3. But driving adapters should **not** hardcode a dependency on a specific database adapter (e.g. `new RouterMySQLAdapter()`).

If an input adapter explicitly instantiates `RouterMySQLAdapter`, it introduces a compile-time coupling between driving and driven adapters, breaking the hexagonal premise.

```text
POOR DESIGN (Coupled Adapters):
[ REST Adapter ] ----> instantiates: new RouterMySQLAdapter() [ MySQL DB ]
                       (Cannot swap to MongoDB or In-Memory for testing!)

HEXAGONAL DESIGN (SPI Decoupled):
[ REST Adapter ] ----> [ RouterManagementUseCase ] (Interface)
                                 ^
                                 | (discovered via ServiceLoader)
                       [ RouterManagementInputPort ]
                                 |
                                 v
                       [ RouterManagementOutputPort ] (Interface)
                                 ^
                                 | (discovered via ServiceLoader)
                       [ RouterMySQLAdapter ] OR [ InMemoryRouterAdapter ]
```

---

## 2. Java ServiceLoader Mechanism

Java's `ServiceLoader` enables runtime discovery of service provider implementations declared in `module-info.java` or `META-INF/services`.

### Declaring Service Consumers and Providers in JPMS:

In the **Application** module, we declare that it `uses` the output port interface:
```java
module dev.davivieira.topologyinventory.application {
    requires dev.davivieira.topologyinventory.domain;
    exports dev.davivieira.topologyinventory.application.usecase;
    exports dev.davivieira.topologyinventory.application.ports.output;

    uses dev.davivieira.topologyinventory.application.ports.output.RouterManagementOutputPort;
}
```

In the **Framework** module, we declare that it `provides` the implementation:
```java
module dev.davivieira.topologyinventory.framework {
    requires dev.davivieira.topologyinventory.domain;
    requires dev.davivieira.topologyinventory.application;

    provides dev.davivieira.topologyinventory.application.ports.output.RouterManagementOutputPort
        with dev.davivieira.topologyinventory.framework.adapters.output.database.RouterMySQLAdapter;
}
```

---

## 3. Dynamic Adapter Initialization

To bridge adapters dynamically, we can build a generic adapter factory that loads the appropriate provider at startup:

```java
package dev.davivieira.topologyinventory.framework.adapters.input.generic;

import dev.davivieira.topologyinventory.application.ports.input.RouterManagementInputPort;
import dev.davivieira.topologyinventory.application.ports.output.RouterManagementOutputPort;
import dev.davivieira.topologyinventory.application.usecase.RouterManagementUseCase;
import java.util.ServiceLoader;

public class RouterManagementGenericAdapter {

    private final RouterManagementUseCase routerManagementUseCase;

    public RouterManagementGenericAdapter() {
        // Discovers output port implementation dynamically on the module path
        RouterManagementOutputPort outputPort = ServiceLoader.load(RouterManagementOutputPort.class)
            .findFirst()
            .orElseThrow(() -> new IllegalStateException("No output port provider registered!"));

        this.routerManagementUseCase = new RouterManagementInputPort(outputPort);
    }

    public RouterManagementUseCase getUseCase() {
        return routerManagementUseCase;
    }
}
```

---

## 4. Why This Matters for Architecture

By utilizing SPI and `ServiceLoader`:
1. **Zero-Framework Execution:** You can test the entire hexagonal system, driving it from a CLI or unit test, without booting an application server or dependency injection container.
2. **Effortless Mocking & Swapping:** In a local or unit-test environment, replacing `RouterMySQLAdapter` with an in-memory `RouterMapAdapter` requires only swapping the provider module—zero changes to application or domain code.
3. **Pluggable Architecture:** Different distributions of the software can ship with alternative adapters (e.g. AWS DynamoDB adapter vs On-premise Oracle adapter) without recompiling the core.
