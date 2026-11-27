# Mediator Pattern

The **Mediator** pattern reduces chaotic dependencies between objects by forcing them to communicate **only through a central mediator object** rather than holding direct references to each other.

---

## 1. The Problem It Solves

In a checkout form or air-traffic control tower, 6 components (country selector, ZIP input, tax calculator, coupon field, terms checkbox, submit button) might each call the other 5 directly. That creates a brittle $N \times (N-1)$ dependency web where changing one component breaks several others and makes unit testing impossible without instantiating the whole graph.

---

## 2. Structure

```text
  [CountrySelect] <---+
                      |
  [TermsCheckbox] <---+---> [CheckoutMediator]
                      |       (Coordinates rules & updates)
  [SubmitButton]  <---+
```

Each colleague knows **only** the `Mediator` interface—never its peer colleagues.

---

## 3. Deep-Dive Java Example

```java
public interface FormMediator {
    void notify(Component sender, String event);
}

public abstract class Component {
    protected final FormMediator mediator;

    protected Component(FormMediator mediator) {
        this.mediator = mediator;
    }
}

public final class Checkbox extends Component {
    private boolean checked;

    public Checkbox(FormMediator mediator) { super(mediator); }

    public void toggle() {
        this.checked = !this.checked;
        mediator.notify(this, "TOGGLED");
    }

    public boolean isChecked() { return checked; }
}

public final class SubmitButton extends Component {
    private boolean enabled;

    public SubmitButton(FormMediator mediator) { super(mediator); }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public boolean isEnabled() { return enabled; }
}
```

Now `CheckoutMediator` centralizes all cross-component rules in one testable class:

```java
public final class CheckoutMediator implements FormMediator {
    private Checkbox terms;
    private Checkbox ageVerified;
    private SubmitButton submit;

    public void wire(
        Checkbox terms,
        Checkbox ageVerified,
        SubmitButton submit
    ) {
        this.terms = terms;
        this.ageVerified = ageVerified;
        this.submit = submit;
    }

    @Override
    public void notify(Component sender, String event) {
        if ("TOGGLED".equals(event)) {
            boolean ready = terms.isChecked()
                && ageVerified.isChecked();
            submit.setEnabled(ready);
        }
    }
}
```

---

## 4. Real-World Java Examples

- **Spring `DispatcherServlet`:** Mediates between `HandlerMapping`, `HandlerAdapter`, `ViewResolver`, and exception handlers without them calling each other.
- **`java.util.concurrent.ExecutorService`:** Mediates between task submitters and worker thread pools.
- **CQRS Mediator Buses:** Controllers send `Command` or `Query` objects to a single mediator rather than injecting 10 domain services.

---

## 5. Mediator vs. Observer vs. Facade

| Pattern | Communication Flow | Coupling Goal |
| :--- | :--- | :--- |
| **Mediator** | Bidirectional, centralized among named peers | Remove $N \times N$ peer references |
| **Observer** | One-to-many broadcast to anonymous listeners | Decouple event producer from consumers |
| **Facade** | Unidirectional entry point into a subsystem | Simplify a complex API for external callers |

---

## 6. Avoiding the "God Mediator" & Trade-Offs

If a Mediator grows too large, split it by bounded context or screen section.

| Pros | Cons |
| :--- | :--- |
| Eliminates many-to-many colleague coupling | Mediator can become a complex "God Object" |
| Centralizes interaction rules in one place | Adds an extra hop for simple 2-class interactions |
| Colleagues become reusable in other contexts | |
