# CI/CD Regression Testing & Offline Benchmarking

Modifying system prompts, updating retrieval chunks in RAG pipelines, or swapping LLM model weights frequently introduces unexpected regression bugs: fixing one customer edge case often degrades accuracy across ten others. Integrating **JEV evaluation gates into CI/CD pipelines** enables continuous automated testing without crippling developer velocity or API budgets.

---

## 1. The Challenge of Prompt Regression in CI/CD

Software engineers rely on unit tests to prevent regressions. However, testing non-deterministic generative models poses unique challenges:

```text
Prompt Engineer edits prompt: "Be more concise when explaining errors."
                                 |
                                 v
                     [ PULL REQUEST SUBMITTED ]
                                 |
         +-----------------------+-----------------------+
         |                                               |
  Edge Case 1 Fixed!                              Edge Case 42 BROKEN!
  (Error explanation is concise)                  (Omits critical stack traces!)
```

Without automated evaluation gates in CI/CD, regressions reach production undetected.

---

## 2. The Economic Barrier of Traditional LLM Judges in CI

Running a comprehensive test suite of 2,500 representative prompts on every Git commit:

$$\text{Cost per PR Build} = 2,500 \text{ prompts} \times \$0.04 = \$100.00$$

If a team of 10 engineers pushes 30 commits per day, CI/CD evaluation costs **$\$3,000\text{ per day}$** ($\$90,000/\text{month}$), with each test run taking 45 minutes.

### The JEV CI/CD Advantage
By running **JEV decision-only evaluations**:
- **Speed:** 2,500 tests complete in **under 45 seconds** via parallelized forward passes.
- **Cost:** 2,500 tests cost **$\$1.25** total!
- **Fast Feedback Loop:** Developers receive instant pass/fail feedback directly on their GitHub pull requests.

---

## 3. GitHub Actions Automated Gate Example

```yaml
# .github/workflows/llm-eval-gate.yml
name: LLM Regression Evaluation Gate

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'rag_config/**'

jobs:
  run-evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: pip install typesafe-jev pytest

      - name: Run JEV Regression Suite
        run: |
          python -m jev.cli run \
            --dataset tests/golden_benchmark.jsonl \
            --min-faithfulness 0.95 \
            --max-escalation-rate 0.20 \
            --output-report eval_report.json

      - name: Comment PR Report
        uses: actions/github-script@v7
        with:
          script: |
            const report = require('./eval_report.json');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `### 🤖 JEV Evaluation Report
              - **Status**: ${report.passed ? '✅ PASSED' : '❌ FAILED'}
              - **Faithfulness**: ${report.faithfulness}% (Threshold: 95%)
              - **Escalation Rate**: ${report.escalation_rate}% (Max: 20%)`
            });
```

---

## 4. The Active Learning Data Flywheel

The true power of the JEV framework lies in the synergy between production traffic and CI/CD benchmarks:

```text
[ Production Traffic ]
          |
    JEV Evaluates
          |
     Uncertain? (Confidence < 0.85)
          |
          v
[ Escalated Edge Cases ] ---> [ Human Expert Review ]
                                       |
                              Verified Ground Truth
                                       |
                                       v
                     [ CI/CD Golden Regression Dataset ]
                                       |
                     Prevents similar failures forever!
```

1. **Automated Discovery:** Production requests that trigger Tier-2 escalations are automatically flagged as edge cases.
2. **Human Labeling:** Data annotators review the uncertain samples and label the true ground-truth verdict.
3. **Continuous Expansion:** New edge cases are appended to the golden CI/CD test suite, creating an automated data flywheel that hardens system reliability over time.
