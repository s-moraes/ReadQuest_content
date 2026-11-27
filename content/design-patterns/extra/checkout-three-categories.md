# Case Study: All Three Categories in One Checkout Flow

Real systems rarely use just one pattern. Below is how **Creational**, **Structural**, and **Behavioral** patterns collaborate in a single e-commerce checkout service.

---

## 1. Creational: Selecting the Gateway (`Factory Method`)

When an order arrives, the checkout service must not hardcode `new StripeClient()` or `new AdyenClient()`. A **Factory** encapsulates gateway instantiation based on region or currency:

```java
PaymentGateway rawGateway = gatewayFactory.forCurrency(
    order.currency()
);
```

---

## 2. Structural: Adapting & Hardening (`Adapter` + `Decorator`)

Each payment provider has a different SDK signature, and production calls need latency metrics and retries without polluting business code:

- **Adapter:** Wraps the third-party SDK so it conforms to your clean `PaymentGateway` interface.
- **Decorator:** Wraps the `PaymentGateway` with `MetricsGatewayDecorator` and `RetryGatewayDecorator`.

```java
PaymentGateway gateway = new RetryGatewayDecorator(
    new MetricsGatewayDecorator(
        new StripeGatewayAdapter(stripeSdk)
    )
);
```

---

## 3. Behavioral: Pricing & Events (`Strategy` + `Observer`)

Before charging, the service computes discounts using an interchangeable **Strategy**, and after payment succeeds, it notifies downstream listeners via **Observer**:

```java
BigDecimal total = discountStrategy.apply(order.subtotal());
PaymentReceipt receipt = gateway.charge(total);
eventBus.publish(new OrderPaidEvent(order.id(), receipt));
```

---

## Summary of Collaboration

| Step | Category | Pattern | Responsibility |
| :--- | :--- | :--- | :--- |
| 1 | **Creational** | Factory Method | Instantiate the right gateway |
| 2 | **Structural** | Adapter + Decorator | Normalize SDK & add cross-cutting layers |
| 3 | **Behavioral** | Strategy + Observer | Run pricing rules & broadcast events |
