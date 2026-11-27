# Abstract Factory Pattern

The **Abstract Factory** pattern provides an interface for creating **families of related or dependent objects** without specifying their concrete classes.

---

## 1. The Problem It Solves

Suppose your application renders UI components (`Button`, `Checkbox`, `Dialog`) across multiple themes or platforms (`Light`, `Dark`, `HighContrast`). If your screen code mixes `new LightButton()` with `new DarkCheckbox()`, the UI becomes visually inconsistent. You need a guarantee that all created components belong to the **same compatible family**.

---

## 2. Structure

```text
          [WidgetFactory <<interface>>]
          + createButton() : Button
          + createCheckbox() : Checkbox
                    ^
         +----------+----------+
         |                     |
  [LightFactory]         [DarkFactory]
  -> LightButton         -> DarkButton
  -> LightCheckbox       -> DarkCheckbox
```

Unlike **Factory Method** (which creates *one* product via inheritance), **Abstract Factory** uses **object composition** to produce an entire *suite* of matching products.

---

## 3. Code Example

```java
public interface Button { void render(); }
public interface Checkbox { void toggle(); }

public interface ThemeFactory {
    Button createButton();
    Checkbox createCheckbox();
}

public class DarkThemeFactory implements ThemeFactory {
    public Button createButton() { return new DarkButton(); }
    public Checkbox createCheckbox() { return new DarkCheckbox(); }
}

public class CheckoutScreen {
    private final Button submitBtn;
    private final Checkbox termsBox;

    public CheckoutScreen(ThemeFactory factory) {
        this.submitBtn = factory.createButton();
        this.termsBox = factory.createCheckbox();
    }
}
```

Swapping `LightThemeFactory` for `DarkThemeFactory` changes the entire UI family in one place without touching `CheckoutScreen`.

---

## 4. Factory Method vs. Abstract Factory

| Dimension | Factory Method | Abstract Factory |
| :--- | :--- | :--- |
| **Granularity** | Creates **one** product | Creates a **family** of related products |
| **Mechanism** | Typically inheritance (subclass override) | Composition (injected factory object) |
| **Best When** | One product varies across contexts | Multiple products must match together |

---

## 5. Trade-Offs

| Pros | Cons |
| :--- | :--- |
| Guarantees product family compatibility | Adding a new product type requires updating the factory interface and every implementation |
| Isolates concrete classes from clients | Increases interface and class count |
| Easy to swap entire product families | |
