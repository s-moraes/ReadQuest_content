## Q1
What does a sudden spike in the cascade escalation rate (alpha) from 15% to 45% typically indicate in production?

### Option A
The cloud datacenter upgraded its cooling hardware.

### Option B [CORRECT]
Production data drift, new unobserved user query patterns, or an adversarial prompt injection attack.

### Option C
All LLM models have ceased functioning simultaneously.

### Option D
The Redis cache memory has been completely deleted.

### Explanation
The escalation rate (alpha) measures the fraction of inputs where JEV exhibits uncertainty. A sudden spike indicates that incoming production queries no longer match the distribution JEV was calibrated on, signaling data drift or targeted prompt injection attempts.

===

## Q2
Why is JEV preferred over generative LLMs for inline synchronous guardrails?

### Option A
Because JEV can run without electricity.

### Option B
Because generative models cannot output English.

### Option C [CORRECT]
Because JEV executes in 20–50ms without sequential token decoding, preventing noticeable latency delays for end users.

### Option D
Because JEV guarantees 100% accuracy on every task without exceptions.

### Explanation
Inline guardrails must evaluate responses before or while they are streamed to the user. A multi-second generative judge disrupts the interactive chat experience, whereas JEV's 20–50ms forward pass runs imperceptibly fast.

===

## Q3
What is the primary benefit of integrating JEV evaluation into CI/CD regression test suites?

### Option A
It allows developers to bypass code reviews entirely.

### Option B [CORRECT]
It enables automated testing of thousands of prompt variations in seconds for negligible cost before merging pull requests.

### Option C
It converts Python code directly into machine assembly.

### Option D
It replaces GitHub Actions with local unit tests.

### Explanation
Testing generative prompts with frontier models on every git commit takes 45+ minutes and costs thousands of dollars per month. JEV evaluates thousands of regression cases in under a minute for pennies, enabling rapid developer iteration.

===

## Q4
How does the Active Learning Flywheel operate in a JEV-as-a-Judge system?

### Option A
By deleting all production logs older than 7 days.

### Option B
By automatically retraining the model on every incoming user query without human review.

### Option C [CORRECT]
By isolating production cases that triggered Tier-2 escalations, having human experts label them, and adding them to the CI/CD golden test suite.

### Option D
By generating random synthetic test prompts every morning.

### Explanation
The active learning flywheel identifies hard edge cases automatically: any query that triggers an escalation represents an area where the model was uncertain. These edge cases are triaged, labeled by humans, and added to regression benchmarks to prevent future failures.

===

## Q5
In an asynchronous shadow evaluation topology, what happens if the JEV telemetry pipeline experiences a brief delay?

### Option A
The end user's active chat session freezes immediately.

### Option B [CORRECT]
The end user continues receiving responses with zero latency impact while evaluation events queue safely in the background.

### Option C
The database rolls back all completed transactions.

### Option D
The load balancer evicts all application servers.

### Explanation
In asynchronous shadow mode, evaluation is decoupled from the user-facing request-response thread. Telemetry is shipped via background workers (e.g., Kafka or Celery), ensuring that evaluation spikes or pipeline delays never degrade the user experience.
