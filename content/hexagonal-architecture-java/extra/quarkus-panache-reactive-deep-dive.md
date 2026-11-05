# Non-Blocking Mutiny Pipelines in Hexagonal Adapters

Integrating reactive programming into an enterprise architecture presents a major architectural hazard: **reactive leakage**. If reactive types (such as Project Reactor's `Mono`/`Flux` or SmallRye Mutiny's `Uni`/`Multi`) leak into core domain models, the domain becomes coupled to a specific reactive streaming library.

This deep dive demonstrates how to confine **SmallRye Mutiny** to the Framework and Application boundaries while preserving pristine, synchronous domain entities.

---

## 1. The Reactive Leakage Trap

When developers first adopt reactive frameworks, they frequently write:

```java
// ANTI-PATTERN: Leaking reactive streams into domain entity
public class Router {
    // WRONG: Domain entities should never manipulate reactive streams!
    public Uni<Boolean> validateAndAddNetwork(Uni<Network> networkUni) {
        return networkUni.chain(net -> ...);
    }
}
```

This violates Hexagonal Architecture in three ways:
1. **Third-Party Dependency:** The domain now requires `io.smallrye.mutiny:mutiny`.
2. **Mental Overhead:** Testing a simple business rule now requires setting up reactive subscribers, test schedulers, and awaiting asynchronous signals.
3. **Loss of Portability:** Switching to virtual threads (Project Loom) or another framework requires rewriting core domain methods.

---

## 2. The Clean Hexagonal Reactive Boundary

In a proper hexagonal reactive design:
1. **Domain Hexagon:** Executes business invariants synchronously using standard POJOs.
2. **Output Adapter:** Bridges asynchronous database I/O using `Uni<T>`.
3. **Application Port:** Composes reactive stages, passing resolved domain entities into domain methods.

```text
Database (Async I/O)
   |
   v (Uni<RouterData>)
[ Output Adapter ]
   | Maps RouterData -> Router POJO
   v (Uni<Router>)
[ Input Port / Use Case ]
   | .onItem().invoke(router -> router.addNetwork(network))  <-- Pure Domain Call!
   v (Uni<Router>)
[ REST Adapter ]
   | Emits HTTP Response via Netty Event Loop
```

---

## 3. Implementation Example with Mutiny

```java
// Inside RouterReactiveInputPort (Application Hexagon)
public class RouterReactiveInputPort implements RouterReactiveUseCase {

    private final RouterReactiveOutputPort outputPort;

    public RouterReactiveInputPort(RouterReactiveOutputPort outputPort) {
        this.outputPort = outputPort;
    }

    @Override
    public Uni<Router> addNetworkToRouter(Id routerId, Network network) {
        return outputPort.retrieveRouter(routerId)
            // Execute synchronous business invariant inside the pure domain entity:
            .onItem().invoke(router -> router.addNetworkToRouter(network))
            // Persist the modified entity back to the reactive output adapter:
            .chain(outputPort::persistRouter);
    }
}
```

Notice how clean this is:
- The async flow control (`retrieve` $\rightarrow$ `modify` $\rightarrow$ `persist`) is managed by the pipeline.
- The business validation (`router.addNetworkToRouter(...)`) remains 100% pure, synchronous domain logic.
