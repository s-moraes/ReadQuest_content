# The Mathematics of Expected Calibration Error (ECE)

A deep dive into the mathematical formulation of Expected Calibration Error (ECE) and why probability calibration is the vital foundation of selective prediction systems.

---

## 1. Formal Definition of Calibration

Let $X$ denote an input feature space and $Y \in \{1, \dots, K\}$ denote a discrete ground-truth class label. A probabilistic classifier outputs a predicted class $\hat{Y}$ and an associated confidence estimate $\hat{P} \in [0, 1]$.

A model is said to be **perfectly calibrated** if:

$$\mathbb{P}\left(\hat{Y} = Y \mid \hat{P} = p\right) = p \quad \forall p \in [0, 1]$$

In plain English: among all predictions where the model claims $80\%$ confidence, exactly $80\%$ of them must be empirically correct.

---

## 2. Derivation of Expected Calibration Error (ECE)

Because continuous probability values cannot be evaluated from finite empirical samples, continuous confidence space $[0, 1]$ is partitioned into $M$ disjoint, equal-width intervals:

$$I_m = \left( \frac{m - 1}{M}, \frac{m}{M} \right], \quad m \in \{1, \dots, M\}$$

Let $B_m$ be the set of sample indices whose predicted confidence falls into interval $I_m$:

$$B_m = \left\{ i \in \{1, \dots, N\} : \hat{p}_i \in I_m \right\}$$

### 1. Empirical Accuracy per Bin
The fraction of correctly classified instances in bin $B_m$:

$$\text{acc}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} \mathbf{1}(\hat{y}_i = y_i)$$

### 2. Average Confidence per Bin
The average predicted probability score in bin $B_m$:

$$\text{conf}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} \hat{p}_i$$

### 3. The Final ECE Metric
The **Expected Calibration Error (ECE)** is the sample-weighted average difference between bin accuracy and bin confidence:

$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

---

## 3. Maximum Calibration Error (MCE)

In high-stakes compliance and safety domains, the average calibration error may obscure severe isolated miscalibrations in critical bins. **Maximum Calibration Error (MCE)** evaluates the worst-case discrepancy:

$$\text{MCE} = \max_{m \in \{1, \dots, M\}} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

---

## 4. Python ECE Calculation Implementation

```python
import numpy as np

def compute_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> float:
    """
    Computes Expected Calibration Error (ECE).
    probs: Array of predicted probabilities for the top class [0.0 - 1.0]
    labels: Binary ground truth array (1 for correct, 0 for incorrect)
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total_samples = len(probs)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        # Identify samples falling into current bin
        in_bin = (probs > bin_lower) & (probs <= bin_upper)
        bin_size = np.sum(in_bin)

        if bin_size > 0:
            bin_acc = np.mean(labels[in_bin])
            bin_conf = np.mean(probs[in_bin])
            ece += (bin_size / total_samples) * np.abs(bin_acc - bin_conf)

    return float(ece)
```
