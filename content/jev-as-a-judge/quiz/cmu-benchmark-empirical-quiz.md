## Q1
According to the empirical findings in the CMU study (Li et al., 2026), what is the primary economic and operational advantage of TypeSafe JEV 1.13.0 compared to frontier generative judges like GPT-6 Astra?

### Option A
JEV uses extensive chain-of-thought scratchpad tokens to outscore frontier models on formal mathematical derivations.

### Option B [CORRECT]
JEV charges exclusively for input tokens ($0.042/M tokens) with zero output token fees, operating at 0.36% of GPT-6's fee (~$0.042 vs. ~$14.50 per 1,000 judgments) with 150ms latency.

### Option C
JEV requires local GPU cluster deployment and incurs significant per-query inference infrastructure overhead.

### Option D
JEV generates natural-language justification paragraphs with 100% adherence to Markdown formatting rules.

### Explanation
TypeSafe JEV operates as a decision-only judge, billing $0.042 per million input tokens with zero output-token costs. It executes in approximately 150ms and operates at 0.36% of the cost of GPT-6 Astra on identical inputs.

===

## Q2
In the 9-workload JEV Operating Envelope formalized by Li et al., which workloads are recommended for immediate escalation rather than standalone JEV evaluation?

### Option A
Ordinary preference ranking (RewardBench) and evidence-grounded factuality (HaluEval QA).

### Option B
Document-grounded summaries with verified context and binary sentiment classification.

### Option C [CORRECT]
Difficult correctness requiring multi-step derivations (JudgeBench) and style-adversarial pairs where incorrect answers are elaborately written (RM-Bench Hard).

### Option D
Multi-turn conversational consistency checks and final-answer adjudication.

### Explanation
Table 2 of the CMU paper establishes that multi-step derivations (math and code on JudgeBench) and style-adversarial pairs (where wrong answers use verbose, authoritative phrasing on RM-Bench) expose JEV's lack of chain-of-thought verification, requiring escalation to frontier reasoning models.

===

## Q3
What occurred when JEV evaluated the RM-Bench style-adversarial benchmark, where incorrect answers were styled with elaborate formatting and authoritative tone?

### Option A
JEV's accuracy improved by 5 percentage points because the elaborate styling provided denser semantic tokens.

### Option B [CORRECT]
JEV's accuracy dropped by 9.2 percentage points (from 84.0% to 74.8%), while GPT-6 remained resilient (+1.3 pp), revealing JEV's susceptibility to verbosity bias.

### Option C
Both JEV and GPT-6 collapsed to chance accuracy (50%) due to prompt injection vulnerabilities.

### Option D
JEV rejected all candidate pairs as malformed JSON schema inputs.

### Explanation
RM-Bench demonstrated that decision-only classification without generative verification falls for elaborate wrong answers, causing JEV's accuracy to decline from 84.0% on matched pairs to 74.8% on hard adversarial pairs. Frontier reasoning models like GPT-6 resisted this bias (moving from 93.3% to 94.6%).

===

## Q4
To neutralize candidate presentation order variance in pairwise comparisons, what bilateral probability aggregation formula is derived in the CMU study?

### Option A
$$\bar{p}(A) = p_1(A, B) \times p_1(B, A)$$

### Option B
$$\bar{p}(A) = \max\big(p_1(A, B), p_1(B, A)\big)$$

### Option C [CORRECT]
$$\bar{p}(A) = \frac{1}{2} \Big[ p_1(A, B) + \big(1 - p_1(B, A)\big) \Big]$$

### Option D
$$\bar{p}(A) = \frac{p_1(A, B)}{p_1(A, B) + p_1(B, A)}$$

### Explanation
The paper defines bilateral order averaging as $\bar{p}(A) = \frac{1}{2} [p_1(A, B) + (1 - p_1(B, A))]$, where $p_1(A, B)$ is the probability of candidate A when shown first, and $p_1(B, A)$ is candidate B's probability when candidate B is shown first. This mathematically neutralizes order effects.

===

## Q5
What critical empirical insight regarding Temperature Scaling (Platt scaling) for probability calibration was demonstrated when transferring parameters across datasets?

### Option A
A single universal temperature parameter ($T = 1.0$) achieved zero calibration error across all NLP benchmarks.

### Option B
Temperature scaling parameters transfer perfectly between preference benchmarks and factuality datasets without retraining.

### Option C [CORRECT]
Fitted temperatures point in opposing directions across workloads ($T = 0.65$ on RewardBench vs. $T = 4.45$ on HaluEval), and transferring them degrades negative log-likelihood (NLL).

### Option D
Temperature scaling is mathematically invalid for probabilistic neural classifiers.

### Explanation
Guo et al. temperature scaling failed to transfer across workloads: RewardBench required sharpening ($T = 0.65$), while HaluEval required aggressive softening ($T = 4.45$). Applying a temperature fitted on one dataset to another worsened NLL (e.g., from 0.449 to 0.475 on JudgeBench), proving that calibration must be performed locally for each specific production workload.
