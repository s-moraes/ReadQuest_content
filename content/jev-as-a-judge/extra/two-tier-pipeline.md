# Building a Two-Tier Escalation Pipeline in Python

A hands-on implementation guide for building an asynchronous, two-tier "Accept When Confident, Escalate When Unsure" evaluation pipeline using Python, TypeSafe JEV, and OpenAI.

---

## 1. Pipeline Architecture Overview

The pipeline implements an asynchronous gatekeeper:

```text
[ Incoming RAG Query + Context + Answer ]
                   |
                   v
         [ Async Task Runner ]
                   |
                   v
    +------------------------------+
    | Tier 1: Local JEV Evaluator  | ---> Extract logits in 35ms
    +------------------------------+
                   |
             Confidence >= 0.85?
                   |
            +------+------+
            |             |
         YES (85%)      NO (15%)
            v             v
       [ ACCEPT ]   [ ESCALATE ] ---> Tier 2: OpenAI GPT-4o / Claude 3.5
      Fast Path!                       (With Chain-of-Thought Rationale)
```

---

## 2. Production Python Implementation

```python
import asyncio
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class CascadeVerdict:
    verdict: str           # "PASS" or "FAIL"
    confidence: float      # Calibrated score [0.0 - 1.0]
    tier_used: str         # "TIER_1_JEV" or "TIER_2_FRONTIER"
    latency_ms: float
    cost_usd: float
    rationale: Optional[str] = None

class ProductionJevCascade:
    def __init__(self, tau: float = 0.85):
        self.tau = tau

    async def _evaluate_tier_1_jev(self, context: str, answer: str) -> Dict[str, Any]:
        """Simulates local fast forward-pass logit extraction."""
        start = time.perf_counter()
        await asyncio.sleep(0.035)  # 35ms local GPU forward pass

        # In production, query JEV model directly
        # Here we mock realistic logit probabilities:
        p_pass = 0.94
        p_fail = 0.06
        confidence = max(p_pass, p_fail)

        elapsed = (time.perf_counter() - start) * 1000
        return {
            "verdict": "PASS" if p_pass > p_fail else "FAIL",
            "confidence": confidence,
            "latency_ms": elapsed,
            "cost_usd": 0.0004
        }

    async def _evaluate_tier_2_frontier(self, context: str, answer: str) -> Dict[str, Any]:
        """Invokes frontier reasoning model when Tier 1 is uncertain."""
        start = time.perf_counter()
        await asyncio.sleep(2.500)  # 2.5s network call with CoT reasoning

        elapsed = (time.perf_counter() - start) * 1000
        return {
            "verdict": "PASS",
            "confidence": 0.99,
            "rationale": "Verified: Claim matches context paragraph 2.",
            "latency_ms": elapsed,
            "cost_usd": 0.0350
        }

    async def evaluate(self, context: str, answer: str) -> CascadeVerdict:
        t1 = await self._evaluate_tier_1_jev(context, answer)

        # Accept When Confident
        if t1["confidence"] >= self.tau:
            return CascadeVerdict(
                verdict=t1["verdict"],
                confidence=t1["confidence"],
                tier_used="TIER_1_JEV",
                latency_ms=t1["latency_ms"],
                cost_usd=t1["cost_usd"]
            )

        # Escalate When Unsure
        t2 = await self._evaluate_tier_2_frontier(context, answer)
        return CascadeVerdict(
            verdict=t2["verdict"],
            confidence=t2["confidence"],
            tier_used="TIER_2_FRONTIER",
            latency_ms=t1["latency_ms"] + t2["latency_ms"],
            cost_usd=t1["cost_usd"] + t2["cost_usd"],
            rationale=t2["rationale"]
        )

# Example Execution
async def main():
    pipeline = ProductionJevCascade(tau=0.85)
    result = await pipeline.evaluate(
        context="PostgreSQL supports multi-version concurrency control.",
        answer="PostgreSQL implements MVCC for read isolation."
    )
    print(f"Verdict: {result.verdict} | Tier: {result.tier_used} | Cost: ${result.cost_usd:.4f}")

if __name__ == "__main__":
    asyncio.run(main())
```
