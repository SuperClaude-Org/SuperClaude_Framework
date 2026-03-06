"""10% stratified consistency validation pass.

Implements AC6: a 10% sample validation pass to verify classification consistency.
Selects a stratified sample (proportional representation of each tier) and
re-runs classification to measure consistency rate.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Callable

from .classification import ClassificationResult, V2Action, V2Tier


@dataclass
class ValidationResult:
    """Result of the consistency validation pass."""

    total_classified: int
    sample_size: int
    consistent_count: int
    inconsistent_count: int
    consistency_rate: float
    tier_sample_counts: dict[str, int] = field(default_factory=dict)
    inconsistencies: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_classified": self.total_classified,
            "sample_size": self.sample_size,
            "consistent_count": self.consistent_count,
            "inconsistent_count": self.inconsistent_count,
            "consistency_rate": round(self.consistency_rate, 4),
            "tier_sample_counts": self.tier_sample_counts,
            "inconsistencies": self.inconsistencies,
        }


def stratified_sample(
    results: list[ClassificationResult],
    sample_fraction: float = 0.10,
    seed: int | None = None,
) -> list[ClassificationResult]:
    """Select a stratified sample of classified files.

    Ensures proportional representation of each tier.
    Each tier with files gets at least 1 sample.

    Args:
        results: All classification results.
        sample_fraction: Fraction to sample (default 10%).
        seed: Random seed for reproducibility.

    Returns:
        List of sampled ClassificationResults.
    """
    if not results:
        return []

    rng = random.Random(seed)

    by_tier: dict[str, list[ClassificationResult]] = {}
    for r in results:
        key = r.tier.value
        by_tier.setdefault(key, []).append(r)

    total_sample_size = max(1, math.ceil(len(results) * sample_fraction))
    sampled: list[ClassificationResult] = []

    # Proportional allocation with minimum 1 per populated tier
    tier_allocations: dict[str, int] = {}
    for tier_key, tier_results in by_tier.items():
        proportion = len(tier_results) / len(results)
        alloc = max(1, round(total_sample_size * proportion))
        alloc = min(alloc, len(tier_results))
        tier_allocations[tier_key] = alloc

    for tier_key, alloc in tier_allocations.items():
        tier_results = by_tier[tier_key]
        chosen = rng.sample(tier_results, min(alloc, len(tier_results)))
        sampled.extend(chosen)

    return sampled


def validate_consistency(
    results: list[ClassificationResult],
    classify_fn: Callable[..., ClassificationResult],
    sample_fraction: float = 0.10,
    seed: int | None = 42,
) -> ValidationResult:
    """Run the consistency validation pass.

    Re-classifies a stratified sample and compares to original results.

    Args:
        results: All classification results from the audit run.
        classify_fn: The classification function to re-run.
        sample_fraction: Fraction to sample (default 10%).
        seed: Random seed for reproducibility.

    Returns:
        ValidationResult with consistency metrics.
    """
    sample = stratified_sample(results, sample_fraction, seed)

    consistent = 0
    inconsistent = 0
    inconsistencies = []
    tier_sample_counts: dict[str, int] = {}

    for original in sample:
        tier_key = original.tier.value
        tier_sample_counts[tier_key] = tier_sample_counts.get(tier_key, 0) + 1

        # Re-classify with same parameters
        has_refs = original.action not in (V2Action.DELETE, V2Action.ARCHIVE)
        re_result = classify_fn(
            original.file_path,
            has_references=has_refs,
        )

        if re_result.tier == original.tier and re_result.action == original.action:
            consistent += 1
        else:
            inconsistent += 1
            inconsistencies.append({
                "file_path": original.file_path,
                "original_tier": original.tier.value,
                "original_action": original.action.value,
                "re_tier": re_result.tier.value,
                "re_action": re_result.action.value,
            })

    total = consistent + inconsistent
    rate = consistent / total if total > 0 else 1.0

    return ValidationResult(
        total_classified=len(results),
        sample_size=len(sample),
        consistent_count=consistent,
        inconsistent_count=inconsistent,
        consistency_rate=rate,
        tier_sample_counts=tier_sample_counts,
        inconsistencies=inconsistencies,
    )
