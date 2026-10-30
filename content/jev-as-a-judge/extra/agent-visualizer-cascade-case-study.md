# Deep Dive: Why JEV Confidence 0.55 Triggered Human Review

When inspecting production evaluations in the `agent-visualizer` UI, an operator noticed an intriguing result: an execution card displayed a **JEV Confidence** of $55\%$ (`0.55`), but the card was stamped with a prominent red badge: **"Needs Human Review"**.

This case study traces the underlying cascade logic step-by-step, explaining why this behavior is not a bug, but the intentional outcome of a safety-first 2-step decision chain.

---

## 1. The Operational Scenario

In the LLM-as-a-Judge view, an analyzed sample from experimental Task T5 (`T5_cross_session_ltm`) was submitted to the cascade:

- **JEV Tier 1:** Enabled (`jev.enabled=true`).
- **JEV Provider Adoption Threshold ($\tau_{\text{jev}}$):** Configured to `0.80` (or `1.00`).
- **Human Review Threshold ($\tau_{\text{human}}$):** Configured to `1.00` (`DEFAULT_HUMAN_REVIEW_THRESHOLD`).
- **Self-Consistency Repeats ($N$):** Configured to `3`.

```text
[ Sample: prompt + agent response ]
               |
               v
  Step 1: JevClient.score()
  JEV Response: { quality_rubric: 1, confidence: 0.55 }
```

---

## 2. Step-by-Step Execution Trace

### Step 1: JEV Fast Path Evaluation
`JudgeEvaluationService.evaluateCascade` issues a REST request to `POST /v1/systemone`. JEV evaluates the state in a single non-generative forward pass and returns:
- `quality_rubric`: `1`
- `confidence`: `0.55` ($55\%$)

### Step 2: The Adoption Threshold Gate
The service inspects the active provider's confidence threshold:

```java
if (jevScore.confidence() >= jevProvider.confidenceThreshold()) {
    results.add(fromJevScore(sample, judgeTask, jevScore));
    continue;
}
```

Because $0.55 < 0.80$, JEV is considered **unsure**. The engine refuses to accept JEV's grade as the final verdict.

### Step 3: Escalation to Tier 2 (LLM Self-Consistency)
Instead of aborting, the cascade falls back seamlessly to the generative judge, executing $3$ independent calls (`repeats = 3`).

Suppose the $3$ generative runs return:
- Run 1: `quality_rubric = 1`
- Run 2: `quality_rubric = 1`
- Run 3: `quality_rubric = 2`

`JudgeConsensus.fromRuns` identifies the mode as `1` with a frequency of $2/3$.
- `consensus.qualityRubric` $= 1$
- `confidence` $= \frac{2}{3} \approx 0.67$ ($67\%$, categorical label `med`)
- `tier` $= \text{Tier.JEV\_THEN\_LLM\_SELF\_CONSISTENCY}$
- `jevAttempt` preserves JEV's original score ($1$) and confidence ($0.55$) for telemetry.

### Step 4: The Human Review Evaluation
Finally, the UI checks whether the card warrants human inspection by calling `needsHumanReview`:

```java
public boolean needsHumanReview(double threshold) {
    return tier != Tier.JEV && confidence < threshold;
}
```

Let us evaluate the boolean conditions:
1. `tier != Tier.JEV`: **TRUE** (the tier is `JEV_THEN_LLM_SELF_CONSISTENCY`, since the LLM decided).
2. `confidence < threshold`: **TRUE** (the LLM's consensus confidence is $0.67$, which is strictly less than $\tau_{\text{human}} = 1.00$).

Both conditions hold $\implies \mathbf{needsHumanReview = true}$!

---

## 3. UI Presentation Breakdown

In `LlmJudgeView`, the resulting card displays the full forensic lineage:

| UI Component | Value / Text | Meaning |
| :--- | :--- | :--- |
| **Tier Badge** | `JEV → LLM` | JEV was consulted first, but escalated to generative self-consistency. |
| **JEV Confidence Badge** | `JEV Confidence: med (55%)` | Native confidence reported by JEV System 1. |
| **LLM Confidence Badge** | `LLM Confidence: med (67%)` | Inter-run agreement of the 3x generative LLM calls ($2/3$). |
| **Review Badge** | `Needs Human Review` | Escalated to Tier 3 because LLM agreement ($67\%$) fell below $\tau_{\text{human}} (100\%)$. |
| **Cascade Caption** | *"JEV scored quality_rubric=1, confidence=55% - below the configured threshold, so the result above was decided by 3x LLM self-consistency instead."* | Transparent textual explanation of why escalation occurred. |

---

## 4. Key Architectural Insights

1. **Why didn't JEV's 0.55 trigger human review directly?**  
   JEV's low confidence triggered **Tier 2 (LLM self-consistency)**, not human review. JEV is not authorized to escalate directly to humans—it must first give the higher-capacity reasoning model an opportunity to resolve the ambiguity.

2. **Why was human review triggered in the end?**  
   Human review was triggered because the **LLM itself was split** ($2/3$ agreement). When both the cheap classifier and the reasoning LLM exhibit uncertainty on the same execution, human expertise is indispensable.

3. **What if JEV had scored 0.85?**  
   Had JEV scored with $85\%$ confidence, it would have exceeded $\tau_{\text{jev}} = 0.80$. The tier would have been `Tier.JEV`. Because `tier == Tier.JEV`, `needsHumanReview()` would evaluate to `false`, and the sample would be accepted autonomously without any LLM cost or human intervention!
