# Empirical Cascades & Calibration Transfer Limits

The ultimate goal of the CMU study is proving that decision-only judges can serve as an automated, frozen first pass in a **Selective Prediction Cascade**. By utilizing confidence estimates, an engineering pipeline can route easy evaluations through JEV and escalate only ambiguous cases to expensive frontier LLMs.

However, the empirical findings also reveal severe pitfalls: naive probability calibration does not transfer across workloads, and order-dependent variance demands bilateral aggregation.

---

## 1. How Confidence Orders Evaluation Errors

A selective prediction cascade depends on whether a model's confidence accurately flags its own mistakes. In JEV, confidence is represented by the maximum label probability:

$$q = \max_k p_k$$

Across 990 base judgments in the CMU study, JEV's empirical accuracy rises monotonically with $q$:

```text
JEV Accuracy vs. Confidence Bin (q):
-----------------------------------------------------------
q < 0.60:       [======] 47.7% Accuracy  (Flip of a coin)
0.60 <= q < 0.70:[========] 61.2%
0.70 <= q < 0.80:[==========] 76.5%
0.80 <= q < 0.90:[============] 84.1%
0.90 <= q < 0.95:[==============) 89.8%
0.95 <= q < 0.99:[================] 93.9%
q = 1.00:       [====================] 99.1% Accuracy!
```

### The Error Detection Signal
Evaluating error detection via the Area Under the ROC Curve ($\text{AUROC}$ of $1 - q$ against incorrect decisions) shows strong ranking ability:
- **RewardBench:** $\text{AUROC} = 0.869$
- **HaluEval:** $\text{AUROC} = 0.863$
- **JudgeBench:** $\text{AUROC} = 0.745$

### Interchagability at High Confidence
When $q \ge 0.90$, JEV and GPT-6 Astra are virtually indistinguishable in performance (**95.8% vs. 96.5%**). However, on items where JEV is unsure ($q < 0.90$), GPT-6 holds a massive $15\text{ percentage point}$ advantage (**82.6% vs. 67.9%**). This confirms that JEV's confidence accurately isolates when stronger reasoning is required.

---

## 2. Frozen Single-Order Cascade Dynamics

By applying a fixed threshold $\tau = 0.90$, the cascade accepts JEV's verdict when $q \ge 0.90$ and calls GPT-6 when $q < 0.90$:

```text
[ Incoming Request ]
         |
         v
  [ JEV 1.13.0 ] ---> Cost: $0.042 / 1k | Latency: 150ms
         |
    Is q >= 0.90?
    /           \
  YES (66%)     NO (34%)
   |              |
[ ACCEPT ]     [ ESCALATE ] ---> [ GPT-6 Astra ]
Verdict: JEV                     Verdict: GPT-6
```

### Cascade Benchmark Results (Pooled Tasks):
- **Escalation Rate ($\alpha$):** Only $34\%$ of items are escalated.
- **Accuracy Retention:** The cascade achieves **$91.3\%$ accuracy**, retaining **$99.6\%$** of GPT-6's standalone performance ($91.7\%$) with a paired difference of only $-0.40\text{ pp}$.
- **Operating Cost:** Total evaluation expenses drop to **$47\%$ of GPT-6's fee** (~$\$6.30$ per $1,000$ judgments instead of $\$14.50+$).

### Error Complementarity on Preference Benchmarks
On RewardBench, the cascade actually **outperformed GPT-6 alone** (**$94.0\%$ vs. $93.5\%$**) while consuming only **$22\%$ of its fee**. Because JEV and GPT-6 make different types of errors, their combined oracle union achieves **$95.7\%$ accuracy**.

---

## 3. Bilateral (Two-Order) Aggregation & Positional Invariance

LLM judges frequently suffer from **position bias** (preferring the first candidate $A$ regardless of content). The CMU study tested order reversal on 750 preference pairs:
- Reversal changed $3.25\%$ of decisions on RewardBench and $11.14\%$ on JudgeBench.
- **Zero Positional Bias:** JEV selected position 1 exactly $48.9\%$ and $48.4\%$ of the time, demonstrating neutral position symmetry.

To eliminate order variance entirely in production, the paper formulates the **Bilateral Order Averaging** equation:

$$\bar{p}(A) = \frac{1}{2} \Big[ p_1(A, B) + \big(1 - p_1(B, A)\big) \Big]$$

Where:
- $p_1(A, B)$ is the probability assigned to Candidate A when presented first.
- $p_1(B, A)$ is the probability assigned to Candidate B when Candidate B is presented first.

Under this two-order policy with threshold $\tau = 0.90$, the cascade accepted **$53.7\%$ of pairs** and matched GPT-6 within $0.6\text{ pp}$ ($92.5\%$ vs $93.1\%$) at **$56.8\%$ of the fee**, fully neutralizing candidate ordering artifacts.

---

## 4. The Failure of Temperature Scaling Transfer

In machine learning, **Temperature Scaling** (Platt scaling, Guo et al., 2017) is the standard method for calibrating predicted logits:

$$\hat{p}_i = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}$$

Where $T > 0$ softens ($T > 1$) or sharpens ($T < 1$) probabilities without changing the argmax decision.

The CMU study attempted to calibrate JEV probabilities by fitting optimal temperature $T$ on a pilot dataset and transferring it to the held-out extension sets. **The transfer failed completely:**

```text
Fitted Optimal Temperatures Across Workloads:
-----------------------------------------------------------
RewardBench (Preference):   T = 0.65  (Demands sharpening)
JudgeBench (Reasoning):     T = 2.15  (Demands softening)
HaluEval (Factuality):      T = 4.45  (Demands heavy softening)
```

### Impact on Negative Log-Likelihood (NLL):
When a temperature calibrated on one workload was applied to another:
- On JudgeBench, NLL **degraded from $0.449$ to $0.475$**!
- On RewardBench, NLL **degraded from $0.205$ to $0.232$**!

```text
        [ WORKLOAD SENSITIVITY ]
   RewardBench (T=0.65)  <--->  HaluEval (T=4.45)
          \                         /
           \                       /
      [ Attempting Global Temperature Transfer ]
                         |
                         v
          CALIBRATION COLLAPSE (Worse NLL)
```

> **Crucial Engineering Rule:** There is no universal calibration temperature across LLM evaluation tasks. Confidence thresholds $\tau$ and calibration factors $T$ must be validated locally on representative workload-specific samples.
