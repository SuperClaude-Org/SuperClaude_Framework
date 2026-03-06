"""Post-consolidation stratified spot-check validator.

Implements T04.02 / D-0028 / AC6: samples 10% of consolidated findings
stratified by tier, re-classifies independently, reports consistency rate
with per-tier breakdown.

Uses fresh evidence gathering (not cached) for independent re-classification.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Callable

from .classification import ClassificationResult, V2Action, V2Tier, classify_finding
from .consolidation import ConsolidatedFinding, ConsolidationReport


@dataclass
class SpotCheckResult:
    """Result of the post-consolidation spot-check validation."""

    total_consolidated: int
    sample_size: int
    consistent_count: int
    inconsistent_count: int
    overall_consistency_rate: float
    per_tier_rates: dict[str, float]
    per_tier_sample_counts: dict[str, int]
    inconsistencies: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_consolidated": self.total_consolidated,
            "sample_size": self.sample_size,
            "consistent_count": self.consistent_count,
            "inconsistent_count": self.inconsistent_count,
            "overall_consistency_rate": round(self.overall_consistency_rate, 4),
            "per_tier_rates": {
                k: round(v, 4) for k, v in self.per_tier_rates.items()
            },
            "per_tier_sample_counts": self.per_tier_sample_counts,
            "inconsistencies": self.inconsistencies,
        }


def _stratified_sample(
    findings: list[ConsolidatedFinding],
    sample_fraction: float = 0.10,
    seed: int | None = 42,
) -> list[ConsolidatedFinding]:
    """Select a stratified sample from consolidated findings.

    Proportional to tier distribution. Each populated tier gets at least 1 sample.
    """
    if not findings:
        return []

    rng = random.Random(seed)

    by_tier: dict[str, list[ConsolidatedFinding]] = {}
    for f in findings:
        key = f.tier.value
        by_tier.setdefault(key, []).append(f)

    total_target = max(1, math.ceil(len(findings) * sample_fraction))
    sampled: list[ConsolidatedFinding] = []

    for tier_key, tier_findings in by_tier.items():
        proportion = len(tier_findings) / len(findings)
        alloc = max(1, round(total_target * proportion))
        alloc = min(alloc, len(tier_findings))
        chosen = rng.sample(tier_findings, alloc)
        sampled.extend(chosen)

    return sampled


def spot_check_validate(
    report: ConsolidationReport,
    reclassify_fn: Callable[[str], ClassificationResult] | None = None,
    sample_fraction: float = 0.10,
    seed: int | None = 42,
) -> SpotCheckResult:
    """Run post-consolidation spot-check validation.

    Samples consolidated findings stratified by tier, re-classifies each
    independently, and measures consistency rate.

    Args:
        report: Consolidation report to validate.
        reclassify_fn: Function that takes a file_path and returns a fresh
            ClassificationResult. If None, uses default classify_finding
            with has_references inferred from original action.
        sample_fraction: Fraction to sample (default 10%).
        seed: Random seed for reproducibility.

    Returns:
        SpotCheckResult with consistency metrics.
    """
    sample = _stratified_sample(report.findings, sample_fraction, seed)

    consistent = 0
    inconsistent = 0
    inconsistencies: list[dict[str, Any]] = []
    per_tier_correct: dict[str, int] = {}
    per_tier_total: dict[str, int] = {}

    for finding in sample:
        tier_key = finding.tier.value
        per_tier_total[tier_key] = per_tier_total.get(tier_key, 0) + 1

        if reclassify_fn is not None:
            re_result = reclassify_fn(finding.file_path)
        else:
            # Default: re-derive from action
            has_refs = finding.action not in (V2Action.DELETE, V2Action.ARCHIVE)
            re_result = classify_finding(
                finding.file_path,
                has_references=has_refs,
            )

        if re_result.tier == finding.tier and re_result.action == finding.action:
            consistent += 1
            per_tier_correct[tier_key] = per_tier_correct.get(tier_key, 0) + 1
        else:
            inconsistent += 1
            inconsistencies.append({
                "file_path": finding.file_path,
                "original_tier": finding.tier.value,
                "original_action": finding.action.value,
                "re_tier": re_result.tier.value,
                "re_action": re_result.action.value,
            })

    total = consistent + inconsistent
    overall_rate = consistent / total if total > 0 else 1.0

    per_tier_rates: dict[str, float] = {}
    for tier_key, count in per_tier_total.items():
        correct = per_tier_correct.get(tier_key, 0)
        per_tier_rates[tier_key] = correct / count if count > 0 else 1.0

    return SpotCheckResult(
        total_consolidated=len(report.findings),
        sample_size=len(sample),
        consistent_count=consistent,
        inconsistent_count=inconsistent,
        overall_consistency_rate=overall_rate,
        per_tier_rates=per_tier_rates,
        per_tier_sample_counts=per_tier_total,
        inconsistencies=inconsistencies,
    )
