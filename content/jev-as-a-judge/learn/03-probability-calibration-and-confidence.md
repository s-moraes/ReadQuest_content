# Probability Calibration & Confidence Estimation

For a decision-only evaluator to serve as an effective gatekeeper, its confidence metrics must reflect reality. A model that outputs a $99\%$ probability for a hallucinated claim is dangerous. **Probability Calibration** ensures that a predicted score of $0.80$ corresponds to an actual empirical accuracy of $80\%$.

---

## 1. The Calibration Dilemma in Modern LLMs

Deep neural networks are notoriously **overconfident**. As demonstrated by Guo et al. (2017), modern transformer architectures trained with cross-entropy loss produce peaky, uncalibrated softmax distributions:

```text
UNCALIBRATED EVALUATOR (Dangerous)
Model predicts "PASS" with 98% confidence.
Reality: Correct only 65% of the time!
===> Cannot be trusted for automated decision gating.

PERFECTLY CALIBRATED EVALUATOR (Ideal)
For all predictions with 80% confidence, the model is correct 80% of the time.
For all predictions with 50% confidence, the model is correct 50% of the time.
===> Low confidence reliably flags genuine uncertainty!
```

In the JEV paradigm, confidence is not merely a descriptive stat—it is the **routing mechanism** that determines whether a request is accepted cheaply or escalated to an expensive frontier model.

---

## 2. Quantifying Calibration Error

To evaluate how well an evaluator's probabilities match real-world outcomes, engineers rely on statistical metrics:

### 1. Reliability Diagrams
Predictions are partitioned into $M$ equal-width probability bins (e.g., $[0.7, 0.8)$, $[0.8, 0.9)$). For each bin $B_m$, the empirical accuracy $\text{acc}(B_m)$ is plotted against the average confidence $\text{conf}(B_m)$. A perfectly calibrated model forms a diagonal line $y = x$.

```text
Accuracy
  1.0 |           / (Perfect Calibration)
      |         / *
  0.8 |       / *   (Actual Model: Overconfident!)
      |     / *
  0.6 |   / *
      | / *
  0.0 +-----------------------
      0.0   0.4   0.8   1.0  Confidence
```

### 2. Expected Calibration Error (ECE)
The weighted average difference between accuracy and confidence across all bins:

$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

Where $N$ is the total sample count and $|B_m|$ is the number of predictions falling into bin $m$. An $\text{ECE} < 0.05$ indicates a highly calibrated model.

### 3. Brier Score
Measures the mean squared error between probability forecasts and binary ground-truth labels ($y_i \in \{0, 1\}$):

$$\text{BS} = \frac{1}{N} \sum_{i=1}^{N} (p_i - y_i)^2$$

A Brier score of $0.0$ represents absolute perfection; a random guesser achieves $0.25$.

---

## 3. Post-Hoc Calibration: Temperature Scaling

To recalibrate an overconfident model without fine-tuning billions of weights, JEV applies **Temperature Scaling**:

```text
Logits: [ z_Pass, z_Fail ] ---> Divide by Scalar T ---> Softmax ---> Calibrated Probs
```

$$\hat{p}_i = \frac{e^{z_i / T}}{\sum_{j=1}^{K} e^{z_j / T}}$$

- If $T > 1$, the temperature softens the distribution, reducing overconfidence.
- If $T < 1$, the temperature sharpens probabilities.
- Because dividing by a positive constant preserves the ordering of logits ($\arg\max z_i = \arg\max z_i / T$), **Temperature Scaling never changes the predicted class label; it only corrects the confidence magnitude!**

```python
# Temperature Scaling Optimization in PyTorch
import torch
import torch.nn as nn
import torch.optim as optim

class ModelWithTemperature(nn.Module):
    def __init__(self):
        super().__init__()
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)

    def forward(self, logits):
        return logits / self.temperature

    def calibrate(self, valid_logits, valid_labels):
        # Learn single temperature parameter on validation set via NLL loss
        nll_criterion = nn.CrossEntropyLoss()
        optimizer = optim.LBFGS([self.temperature], lr=0.01, max_iter=50)

        def eval_loss():
            optimizer.zero_grad()
            loss = nll_criterion(self.forward(valid_logits), valid_labels)
            loss.backward()
            return loss

        optimizer.step(eval_loss)
        return self.temperature.item()
```

---

## 4. Confidence Signals in Practice

In production JEV runtimes, uncertainty is extracted using three complementary signals:

1. **Maximum Softmax Probability (MSP):** $S_{\text{MSP}} = \max_k P(y=k \mid x)$. Direct, fast, but sensitive to extreme logits.
2. **Margin Score (Top-2 Gap):** $S_{\text{Margin}} = P(\text{Top}_1) - P(\text{Top}_2)$. If $P(\text{Yes}) = 0.52$ and $P(\text{No}) = 0.48$, the margin is $0.04$, indicating severe model hesitation.
3. **Shannon Softmax Entropy:**
   
   $$H(P) = -\sum_{k=1}^{K} P_k \log P_k$$
   
   High entropy indicates the probability mass is dispersed uniformly across options, signaling high uncertainty.
