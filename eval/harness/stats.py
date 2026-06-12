"""Aggregation: pass@k and bootstrap CIs, with a cost-adjusted verdict.

A component survives only if its B arm beats baseline A beyond overlapping CIs
AND does not regress quality-per-token. This is the gate the whole harness
exists to enforce; the verdict must come from these numbers, never from a prior
belief about what the native feature does.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .config import TrialResult


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator (Chen et al., 2021). n trials, c correct."""
    if k > n:
        raise ValueError("k cannot exceed n")
    if n - c < k:
        return 1.0
    # 1 - C(n-c, k) / C(n, k)
    prod = 1.0
    for i in range(n - c + 1, n + 1):
        prod *= (i - k) / i
    return 1.0 - prod


def _bootstrap_mean_ci(values: list[float], iters: int = 5000,
                       alpha: float = 0.05, seed: int = 0) -> tuple[float, float, float]:
    """Percentile bootstrap CI for the mean. Deterministic via fixed seed so
    re-runs reproduce (Math.random would not be reproducible)."""
    if not values:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(iters):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int((alpha / 2) * iters)]
    hi = means[int((1 - alpha / 2) * iters)]
    return sum(values) / n, lo, hi


@dataclass
class ArmSummary:
    arm: str
    n_trials: int
    pass_rate: float
    pass_ci: tuple[float, float]
    pass_at_1: float
    pass_at_k: float
    mean_output_tokens: float
    mean_cost_usd: float
    quality_per_1k_tokens: float  # pass_rate per 1k output tokens


def summarize_arm(results: list[TrialResult], k: int) -> ArmSummary:
    arm = results[0].arm
    passes = [1.0 if r.passed else 0.0 for r in results]
    n = len(results)
    c = int(sum(passes))
    rate, lo, hi = _bootstrap_mean_ci(passes)
    out_tokens = [float(r.output_tokens) for r in results]
    mean_out = sum(out_tokens) / n if n else 0.0
    mean_cost = sum(r.cost_usd for r in results) / n if n else 0.0
    qpt = (rate / (mean_out / 1000.0)) if mean_out else 0.0
    return ArmSummary(
        arm=arm, n_trials=n, pass_rate=rate, pass_ci=(lo, hi),
        pass_at_1=pass_at_k(n, c, 1),
        pass_at_k=pass_at_k(n, c, min(k, n)),
        mean_output_tokens=mean_out, mean_cost_usd=mean_cost,
        quality_per_1k_tokens=qpt,
    )


def verdict(baseline: ArmSummary, candidate: ArmSummary) -> str:
    """SURVIVE / CUT / INCONCLUSIVE from the numbers alone."""
    beats = candidate.pass_ci[0] > baseline.pass_ci[1]          # CIs disjoint, B higher
    worse = candidate.pass_ci[1] < baseline.pass_ci[0]
    cost_ok = candidate.quality_per_1k_tokens >= baseline.quality_per_1k_tokens
    if beats and cost_ok:
        return "SURVIVE"
    if beats and not cost_ok:
        return "SURVIVE? (wins but costs more per token — judge by budget)"
    if worse:
        return "CUT (native baseline wins)"
    return "INCONCLUSIVE (CIs overlap — need more trials/tasks)"
