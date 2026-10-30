# RAG Grounding & Pairwise Preference Scoring

The two most common production evaluation workloads are **RAG Groundedness (Hallucination Detection)** and **Side-by-Side Pairwise Preference**. Implementing these tasks within the JEV framework requires specific prompt structuring, atomic claim decomposition, and position-bias mitigation.

---

## 1. RAG Faithfulness via Natural Language Inference (NLI)

In Retrieval-Augmented Generation (RAG), a model synthesizes an answer from retrieved documents. A **faithfulness failure (hallucination)** occurs when the response introduces unsupported claims not present in the reference context.

```text
[ Retrieved Documents (Premise) ] + [ Generated Answer (Hypothesis) ]
                                  |
                                  v
                        [ JEV Decision Head ]
                                  |
            +---------------------+---------------------+
            |                     |                     |
     P(Entailment)         P(Contradiction)         P(Neutral)
       (Factual)           (Hallucination)        (Unverifiable)
```

### Atomic Claim Decomposition
Evaluating a 500-word essay in a single pass is prone to oversight. High-precision JEV pipelines apply **Atomic Claim Decomposition**:

```text
"The Hubble Telescope was launched in 1990 by NASA on the Discovery Shuttle."
                                  |
                +-----------------+-----------------+
                v                                   v
        [ Claim 1 ]                         [ Claim 2 ]
  "Hubble launched in 1990"           "Hubble launched on Discovery"
                |                                   |
           JEV: ENTAIL                         JEV: ENTAIL
                \                                   /
                 +-----------------+---------------+
                                   v
                      Overall Faithfulness = 100%
```

Each atomic sentence is verified independently in microsecond forward passes. If any single claim outputs $P(\text{Contradiction}) > 0.80$, the system flags a hallucination alert.

---

## 2. Pairwise Preference & The Bradley-Terry Model

When benchmarking model improvements or conducting automated A/B tests, systems present two candidate outputs ($Y_A$ and $Y_B$) to determine which is superior.

The statistical foundation of pairwise evaluation is the **Bradley-Terry Model**:

$$P(Y_A \succ Y_B) = \frac{e^{s_A}}{e^{s_A} + e^{s_B}} = \frac{1}{1 + e^{-(s_A - s_B)}}$$

Where $s_A$ and $s_B$ represent latent quality scores. JEV computes the probability distribution over three discrete decision tokens: `[MODEL_A, MODEL_B, TIE]`.

---

## 3. Neutralizing Position Bias

Generative LLMs exhibit severe **Position Bias**: models systematically favor whichever option is presented first ($Y_A$) regardless of quality.

```text
Query: "Explain Quantum Entanglement"
Pass 1: [ Option A: Good ] vs [ Option B: Bad ]  ===> Chooses Option A
Pass 2: [ Option B: Bad ]  vs [ Option A: Good ] ===> Chooses Option B! (BIAS!)
```

### Symmetric Logit Averaging (Bi-Directional Evaluation)
Because JEV executions cost virtually nothing and take milliseconds, the pipeline automatically evaluates both order permutations in parallel:

```text
Forward Pass 1: Prompt(A, B) ---> Extracts P_1(A), P_1(B)
Forward Pass 2: Prompt(B, A) ---> Extracts P_2(A), P_2(B)
```

The final debiased preference score is the symmetric average:

$$\bar{P}(A) = \frac{P_1(A \mid A, B) + P_2(A \mid B, A)}{2}$$

$$\bar{P}(B) = \frac{P_1(B \mid A, B) + P_2(B \mid B, A)}{2}$$

If the discrepancy $|\bar{P}_1(A) - \bar{P}_2(A)|$ exceeds a stability tolerance, the cascade detects position instability and **escalates to Tier 2**.

---

## 4. Benchmark Performance Comparison

On industry-standard evaluation benchmarks (RAGTruth, Arena-Hard, MT-Bench), JEV cascades achieve high correlation with human expert consensus:

| Evaluation Task | JEV Standalone Accuracy | Tier-2 Cascade Accuracy | Frontier Model (GPT-4o) |
| :--- | :--- | :--- | :--- |
| **Factuality (RAGTruth)** | $89.2\%$ | $96.8\%$ | $97.1\%$ |
| **Summarization Quality** | $84.5\%$ | $93.4\%$ | $93.9\%$ |
| **Arena-Hard Preference** | $81.0\%$ | $91.5\%$ | $92.0\%$ |
| **Complex Math Proofs** | $62.3\%$ (Weak) | $89.1\%$ (Escalated!) | $89.5\%$ |

> **Key Takeaway:** For standard factuality and preference tasks, JEV standalone matches frontier models within $1-3\%$. For complex reasoning tasks, the confidence gate safely catches low-performing samples and escalates them to Tier 2.
