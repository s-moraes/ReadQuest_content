## Q1
What is the core operational principle of the "Accept When Confident, Escalate When Unsure" framework?

### Option A
Always accept every response to eliminate API costs entirely.

### Option B [CORRECT]
Accept JEV's low-cost verdict when its confidence exceeds a threshold, and escalate low-confidence cases to a frontier reasoning model.

### Option C
Run two frontier models in parallel on every single transaction and take the average.

### Option D
Escalate all short responses and accept only long essays.

### Explanation
The selective cascade uses a confidence cutoff (tau). Routine, unambiguous queries are resolved instantly and cheaply by Tier 1 (JEV). Ambiguous, low-confidence queries (the uncertain tail) are escalated to Tier 2 (Frontier reasoning model with Chain-of-Thought).

===

## Q2
In a selective cascade where JEV costs $0.0005 per evaluation, the frontier judge costs $0.0400, and the escalation rate is 15%, what is the expected cost per evaluation?

### Option A
$0.0405

### Option B [CORRECT]
$0.0650 for every 10 requests (approx. $0.0065 per request)

### Option C
$0.0200

### Option D
$0.0005

### Explanation
Expected Cost = Cost(JEV) + alpha * Cost(Frontier) = $0.0005 + 0.15 * $0.0400 = $0.0005 + $0.0060 = $0.0065 per evaluation. This represents an 83.75% cost reduction compared to running the frontier model directly.

===

## Q3
How does a JEV pipeline eliminate Position Bias in pairwise preference evaluations?

### Option A
By always selecting Option A regardless of content.

### Option B
By prompting the model to ignore formatting.

### Option C [CORRECT]
By evaluating both orderings (A, B) and (B, A) in parallel forward passes and taking the symmetric average of the logits.

### Option D
By generating 1,000 tokens of reasoning before making a selection.

### Explanation
Position bias occurs when models disproportionately pick the first option presented. Because JEV forward passes take only milliseconds, systems run both permutations (A vs B, and B vs A) in parallel and average the resulting probabilities, guaranteeing mathematical symmetry.

===

## Q4
What is a Style-Adversarial sample in LLM evaluation?

### Option A
A prompt that includes invalid ASCII characters or broken UTF-8 encoding.

### Option B
A request that asks the model to generate poetry instead of prose.

### Option C [CORRECT]
An answer that is factually wrong or nonsensical, but written in authoritative, highly polished, and persuasive prose.

### Option D
A dataset formatted without proper column headers.

### Explanation
Style-adversarial inputs exploit a model's tendency to correlate high-quality grammar, formal vocabulary, and clean markdown with correctness. A decision model without safety thresholds might be fooled by the tone, but its calibrated entropy will rise, triggering an escalation.

===

## Q5
Why do complex multi-step mathematical derivations challenge a single decision-only forward pass?

### Option A
Because neural networks cannot multiply numbers.

### Option B [CORRECT]
Because a single forward pass has a fixed computational depth and lacks intermediate tokens to act as an external scratchpad memory.

### Option C
Because mathematical symbols cannot be tokenized.

### Option D
Because math prompts can only be evaluated by human teachers.

### Explanation
In a single forward pass, computation is strictly bounded by the fixed depth of the transformer layers. Chain-of-Thought generation provides dynamic computational depth, where each generated token allows the model to store intermediate state and reason incrementally.
