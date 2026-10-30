## Q1
In the `agent-visualizer` cascade architecture (`LAJ-09`), under what exact condition does a sample short-circuit at Tier 1, bypassing the generative LLM self-consistency loop entirely?

### Option A
When the LLM judge API is unreachable, causing JEV to be invoked as an emergency fallback evaluator.

### Option B [CORRECT]
When JEV is enabled globally and its native confidence meets or exceeds the active provider's confidence threshold (`jevScore.confidence() >= jevProvider.confidenceThreshold()`).

### Option C
When JEV assigns a `quality_rubric` score of 3, regardless of its reported confidence metric.

### Option D
When the user explicitly selects "Single-Shot JEV" from the desktop UI toolbar instead of the default batch runner.

### Explanation
In `JudgeEvaluationService.evaluateCascade`, Tier 1 checks `jevScore.confidence() >= jevProvider.confidenceThreshold()`. If this condition holds, the sample is wrapped directly as `Tier.JEV` and added to results, completely skipping the generative LLM call loop.

===

## Q2
In `JudgeConsensus.fromRuns()`, if two different `quality_rubric` values tie with the exact same maximum frequency, how does the engine deterministically resolve the tie?

### Option A
It re-evaluates the sample one additional time with a higher temperature to break the deadlock.

### Option B
It chooses the rubric score that appeared first in chronological execution order.

### Option C [CORRECT]
It selects the value closest to the median of all runs; if still tied, it conservatively selects the lower value.

### Option D
It discards the sample and sets `quality_rubric = 0` with `needsHumanReview = true`.

### Explanation
`JudgeConsensus.pickTieBreakValue` sorts all run rubric scores and calculates their median. It selects the tied mode with the minimum absolute distance to this median (`Math.abs(value - median)`). If distances are identical, it falls back to `thenComparingInt(v -> v)`, selecting the lower, more conservative rubric score.

===

## Q3
Why does `JudgeConfidenceResult.needsHumanReview(threshold)` explicitly check `tier != Tier.JEV` before comparing against the human review threshold?

### Option A
Because JEV does not output a numerical confidence value, making mathematical threshold comparisons impossible.

### Option B
Because JEV is hardcoded to never be used in production or experimental workflows.

### Option C
Because human raters are legally prohibited from inspecting decisions made by external proprietary classifiers.

### Option D [CORRECT]
Because a `Tier.JEV` decision already satisfied its own provider adoption threshold, and testing it against a second independent threshold would contradict that decision.

### Explanation
The cascade operates as a strict 2-step decision chain: JEV resolves alone or defers to the LLM, and the LLM resolves alone or defers to a human. A sample resolved by JEV has already cleared its provider's confidence threshold ($\tau_{\text{jev}}$). Flagging it again under an independently-configured human threshold ($\tau_{\text{human}}$) would violate the adoption guarantee.

===

## Q4
During the EXP-04 benchmark on Task T5 (`T5_cross_session_ltm`), what was identified as the primary confounding factor explaining why standalone JEV scored $\kappa \approx 0.26$ while LLM self-consistency scored $\kappa \approx 0.77$?

### Option A
JEV's REST API experienced frequent HTTP 504 timeouts, returning corrupt payload objects for all 16 cases.

### Option B [CORRECT]
JEV was sent a generic instruction without task-specific anchors, whereas the generative LLM received rich, task-grounded prompt templates.

### Option C
JEV was evaluated using an incompatible 1–10 scale rather than the canonical 0–3 quality rubric.

### Option D
The human ground truth raters disagreed with each other, producing an invalid baseline with $\kappa < 0.20$.

### Explanation
As documented in `LLM_AS_A_JUDGE.MD` and `CLAUDE.md`, the initial `JevClient` dispatched a generic instruction (`"avalie segundo o QUALITY_RUBRIC.md"`) through `JevQuestion`, omitting the specific hydration-goal memory anchors that `JudgePromptConfig` provided to the LLM. This zero-shot handicap caused JEV to never score above 1 across all 16 test cases.

===

## Q5
What is the functional difference between executing `JudgeCsvBatchCli` with and without the `--jev` flag?

### Option A
With `--jev`, it only validates CSV column headers without making network calls; without it, it calls the LLM.

### Option B
With `--jev`, it forces 100% of samples to be graded by human raters in an interactive CLI prompt.

### Option C [CORRECT]
With `--jev`, it activates the 3-Tier cascade (`evaluateCascade`), attempting JEV first and falling back to LLM self-consistency only for uncertain cases.

### Option D
With `--jev`, it disables all confidence calculations and uses single-shot generative evaluation.

### Explanation
`JudgeCsvBatchCli` defaults to LAJ-08 pure self-consistency (`evaluationService.evaluateWithConfidence`), running every case $N$ times through the generative LLM. Adding the `--jev` flag switches the batch runner to `evaluationService.evaluateCascade`, running JEV as Tier 1 first and outputting additional `tier` and `needs_human_review` columns.
