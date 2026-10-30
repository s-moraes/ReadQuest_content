# Decision-Only Evaluation Architecture

The core premise of **JEV (Judge / Evaluator / Validator)** is that for the vast majority of evaluation tasks, authoring natural language rationales is unnecessary and counterproductive. Instead, **Decision-Only Evaluation** treats LLMs as discriminators, extracting structured classifications directly from model log probabilities.

---

## 1. Deconstructing the Autoregressive Bottleneck

To understand why traditional LLM judges are slow, consider the mechanics of autoregressive decoding:

```text
AUTOREGRESSIVE GENERATION (Slow, Memory-Bound)
Token 1 ---> Token 2 ---> Token 3 ... ---> Token 800 ---> Token 801 (Verdict)
|------------------ 800 Sequential Forward Passes -------------------|
Each pass reloads KV-cache, bound by GPU memory bandwidth (Memory Wall).

DECISION-ONLY LOGIT EVALUATION (Fast, Compute-Bound)
[ Prompt Context + Response ] ---> Single Forward Pass ---> Extract Logits
|------------------------- 1 Forward Pass ---------------------------|
Directly calculates P(Pass) vs P(Fail) from the output vocabulary head!
```

In standard text generation, each generated token requires a separate forward pass through the transformer layers. Generating 800 tokens of step-by-step reasoning requires **800 sequential GPU invocations**.

In contrast, **Decision-Only Evaluation** processes the prompt in a single parallelized prompt-ingestion pass and inspects the output logits for the target decision tokens.

---

## 2. Logit Extraction & Probability Derivation

When evaluating whether an answer is grounded in retrieved context, the evaluator structures the prompt so the very next token represents the verdict:

```text
Context: "The Eiffel Tower is located in Paris, France."
Claim: "The Eiffel Tower is in Berlin."
Question: Is the claim factually grounded in the context?
Answer (Yes / No): [NEXT TOKEN]
```

Instead of running greedy decoding, the evaluator extracts the unnormalized logit values $z_{\text{Yes}}$ and $z_{\text{No}}$ directly from the model's vocabulary projection head:

$$P(\text{Yes}) = \frac{e^{z_{\text{Yes}}}}{e^{z_{\text{Yes}}} + e^{z_{\text{No}}}}, \quad P(\text{No}) = \frac{e^{z_{\text{No}}}}{e^{z_{\text{Yes}}} + e^{z_{\text{No}}}}$$

```python
# Extracting decision probabilities in Python
import torch
import torch.nn.functional as F

def evaluate_factuality(model, tokenizer, prompt: str) -> dict:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model(**inputs)
        # Logits of the very last position in the prompt
        next_token_logits = outputs.logits[0, -1, :]

    yes_id = tokenizer.encode("Yes", add_special_tokens=False)[-1]
    no_id = tokenizer.encode("No", add_special_tokens=False)[-1]

    # Calculate softmax across target decision tokens only
    target_logits = torch.tensor([next_token_logits[yes_id], 
                                  next_token_logits[no_id]])
    probs = F.softmax(target_logits, dim=0)

    p_yes = probs[0].item()
    p_no = probs[1].item()

    return {
        "verdict": "PASS" if p_yes > p_no else "FAIL",
        "confidence": max(p_yes, p_no),
        "p_pass": p_yes,
        "p_fail": p_no
    }
```

---

## 3. The Anatomy of TypeSafe JEV

TypeSafe JEV formalizes this approach by enforcing strict typing schemas over evaluation tasks:

```text
+-------------------------------------------------------------+
|                     TYPESAFE JEV SCHEMAS                    |
|                                                             |
|  1. Binary Decision:     { PASS, FAIL }                     |
|  2. Pairwise Preference: { MODEL_A, MODEL_B, TIE }          |
|  3. Ordinal Likert:      { SCORE_1, SCORE_2 ... SCORE_5 }   |
|  4. Multi-Label Categorical: { TOXIC, SPAM, FACTUAL }       |
+-------------------------------------------------------------+
```

### Architectural Benefits

1. **Sub-50ms Latency:** Because no tokens are decoded sequentially, execution latency drops from seconds to tens of milliseconds.
2. **Zero Schema Hallucinations:** Generative models often fail to produce valid JSON when temperature fluctuates. Decision-only extraction derives answers directly from vocabulary indices, making syntax errors mathematically impossible.
3. **Calibrated Confidence Scoring:** Traditional LLMs say *"I am 100% sure"* even when hallucinating. In JEV, the softmax distribution over decision tokens provides an authentic, granular probability metric.

---

## 4. Generative vs. Decision-Only Trade-Offs

| Evaluation Dimension | Generative Reasoning Judge | Decision-Only JEV Judge |
| :--- | :--- | :--- |
| **Execution Latency** | High ($3,000\text{ms} - 10,000\text{ms}$) | Ultra-low ($20\text{ms} - 80\text{ms}$) |
| **Evaluation Cost** | $\$0.02 - \$0.10$ per item | $<\$0.0005$ per item |
| **Output Format** | Unstructured prose + JSON | Strictly typed label + probability |
| **Audit Explanation**| Natural language reasoning chain | None out-of-the-box (decision-only) |
| **Failure Modes** | Hallucinated reasoning, verbosity | Struggles on multi-step complex logic |
| **Best Used For** | Offline gold-standard audits | Real-time production guardrails |
