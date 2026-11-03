# The 17-Model Benchmark & Operational Trade-offs

The seminal research paper *"JEV-as-a-Judge: Accept When Confident, Escalate When Unsure"* (Li, Miao, Krishnan, & Padman, Carnegie Mellon University, arXiv:2609.26550) provides the first comprehensive empirical evaluation comparing decision-only judging against generative LLM judges and specialized reward models. 

Across 17 distinct model configurations and thousands of adjudicated test items, the CMU study establishes where lightweight decision-only evaluation succeeds, where it fails, and the precise operational trade-offs of production deployments.

---

## 1. Experimental Protocol & The 17-Model Panel

To rigorously test whether a decision-only interface can replace or gate generative LLM judges, the researchers constructed a multi-family evaluation panel consisting of 13 hosted services and 4 local baselines:

```text
+-----------------------------------------------------------------------+
|                       THE 17-MODEL BENCHMARK PANEL                    |
+-----------------------------------+-----------------------------------+
| Hosted Judges (Low-Effort / API)  | Local & Specialized Reward Models |
+-----------------------------------+-----------------------------------+
| - TypeSafe JEV 1.13.0             | - PairRM (local, H100)            |
| - GPT-4.1 mini, GPT-4.1           | - Skywork-Reward-V2 (local, V100) |
| - GPT-5.2, GPT-5.4, GPT-5.6 Sol   | - Qwen3-32B (local, H100)         |
| - GPT-6 Astra (Frontier baseline) | - Qwen3.5-27B (local, H100)       |
| - GPT-OSS 120B (Groq)             |                                   |
| - Qwen3.6-27B & Qwen3.8-27B (Groq)|                                   |
| - Claude Sonnet 5 (Anthropic)     |                                   |
| - Gemini 3 Flash & Gemini 3.1 Pro |                                   |
+-----------------------------------+-----------------------------------+
```

### The Output Contract
Generative comparator models received the exact same instructions and structured context as JEV. They were prompted under a strict JSON schema contract requiring a decision label and verbalized probability estimates without rationale generation, isolating verdict accuracy and confidence calibration from discursive reasoning.

---

## 2. Core Benchmark Results (Base Tasks)

The benchmark evaluated models across four fundamental datasets totaling 1,312 primary test items:
1. **RewardBench (400 pairs):** Balanced sample spanning chat, difficult chat, safety, and reasoning.
2. **JudgeBench (350 pairs):** Objective correctness stressing mathematics, coding, and logical derivations.
3. **HaluEval (240 judgments):** Evidence-grounded question answering (comparing reference vs. hallucinated responses against source documents).
4. **Existing Multi-Turn Labels (150 replies):** Multi-turn answer consistency across adversarial probes.

```text
| Model Configuration | RewardBench (400) | JudgeBench (350) | HaluEval (240) | Multi-Turn (150) | Valid / Base Calls |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **JEV 1.13.0**        | **92.2%**         | **78.6%**        | **87.5%**      | **94.0%**        | **1312 / 1312 (100%)** |
| GPT-6 Astra          | 93.5%             | 93.1%            | 86.7%          | 96.7%            | 1312 / 1312 (100%) |
| GPT-5.6 Sol          | 93.2%             | 93.1%            | 89.2%          | 95.3%            | 1312 / 1312 (100%) |
| GPT-5.4              | 93.0%             | 90.9%            | 88.3%          | 92.7%            | 1310 / 1312 (99.8%) |
| Gemini 3.1 Pro       | 94.5%             | 87.4%            | 87.1%          | 94.7%            | 1312 / 1312 (100%) |
| Claude Sonnet 5      | 91.2%             | 88.9%            | 85.8%          | 94.7%            | 1308 / 1312 (99.7%) |
| Gemini 3 Flash       | 92.8%             | 76.0%            | 83.3%          | 95.3%            | 1312 / 1312 (100%) |
| Skywork-Reward-V2    | 94.0%             | 71.1%            | —              | —                | 750 / 750 (100%)   |
| PairRM (local)       | 68.0%             | 54.3%            | —              | —                | 750 / 750 (100%)   |
```

### Key Quantitative Findings:
- **Parity on Ordinary Preference:** On RewardBench, JEV scores **92.2%** vs. GPT-6's **93.5%**—a paired difference of only $-1.25\text{ pp}$ ($95\%$ cluster interval $[-3.8, 1.5]$).
- **Parity on Grounded Factuality:** On HaluEval, JEV achieves **87.5%** vs. GPT-6's **86.7%** ($+0.83\text{ pp}$).
- **The Reasoning Gap on JudgeBench:** On objective derivation verification (JudgeBench), JEV scores **78.6%** vs. GPT-6's **93.1%**, exposing a $-14.6\text{ pp}$ deficit when multi-step math or code execution is required.

---

## 3. Blinded Human Adjudication & Label Noise

Benchmark ground-truth labels often contain subtle annotation errors. To ensure the findings were not artifacts of faulty labels, the CMU researchers conducted **blinded human expert adjudication** across all base items where JEV and GPT-6 disagreed:

```text
[ Disagreement Item (JEV vs. GPT-6) ]
                  |
                  v
       [ Blinded Human Expert ]
       (No model names, no labels)
                  |
         +--------+--------+
         |                 |
  On RewardBench:    On HaluEval:
  - GPT-6 wins: 17   - 24 of 26 mutual "misses" were actually
  - JEV wins: 5        unsupported benchmark labels!
  - Indecisive: 7    - Under corrected labels:
                       JEV: 95.8% | GPT-6: 98.3%
```

On HaluEval, 24 of the 26 items where both JEV and GPT-6 were marked incorrect were found to have **factually incorrect benchmark labels** (the provided text did not support the ground truth). When evaluated against verified ground truth, JEV reached **95.8%** and GPT-6 reached **98.3%**, proving that decision-only judging reliably identifies factual grounding errors.

---

## 4. Economic Pricing & Latency Reality

The defining advantage of decision-only judging lies in the extreme asymmetry of operational cost and execution latency:

| Evaluator Engine | Pricing per Million Tokens | Cost per 1,000 Decisions | Wall-Clock Latency | Output Contract Violations |
| :--- | :---: | :---: | :---: | :---: |
| **TypeSafe JEV 1.13.0** | **$0.042 In / $0.00 Out** | **~$0.042** | **0.15s (150ms)** | **0 / 1,312 (0.0%)** |
| Gemini 3 Flash | $0.50 In / $3.00 Out | ~$0.85 | 1.10s | 0 / 1,312 (0.0%) |
| Claude Sonnet 5 | $2.00 In / $10.00 Out | ~$3.60 | 2.45s | 4 / 1,312 (0.3%) |
| GPT-5.6 Sol | $4.00 In / $20.00 Out | ~$6.80 | 3.10s | 0 / 1,312 (0.0%) |
| **GPT-6 Astra** | **$10.00 In / $50.00 Out** | **~$14.50** | **4.20s** | **0 / 1,312 (0.0%)** |
| Qwen3.6-27B (Groq) | $0.60 In / $3.00 Out | ~$0.90 | 0.85s | 57 / 1,312 (4.3%) |

```text
Operational Cost Comparison (1,000,000 Evaluations):
=====================================================
GPT-6 Astra:      $14,500.00  [========================================]
Claude Sonnet 5:   $3,600.00  [==========]
Gemini 3 Flash:      $850.00  [==]
TypeSafe JEV:         $42.00  [*] (0.36% of GPT-6 fee!)
```

### 1. 0.36% of the Comparator's Fee
JEV charges solely for input tokens with zero output token fees. Evaluating 1,000 items with JEV costs **$0.042**, compared to **$14.50+** with GPT-6 Astra—an economic reduction of over **99.6%**.

### 2. 150ms Instant Verification
Operating as a direct classifier, JEV renders judgments in approximately 150 milliseconds, making it compatible with real-time API gateways, whereas generative models require multi-second generation windows.

### 3. Contract Reliability (Zero Malformed Schemas)
While generative models under JSON mode occasionally emit truncated brackets, markdown ticks, or transport aborts (e.g., Qwen3.6 suffered 57 contract errors and 33 transport timeouts), JEV achieved **1312/1312 perfect responses** due to its typed endpoint architecture.
