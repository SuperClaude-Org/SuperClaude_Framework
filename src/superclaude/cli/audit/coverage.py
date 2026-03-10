"""Coverage tracking with per-risk-tier metrics and artifact output.

Implements AC2: coverage artifacts that report per-tier metrics.
Accumulates classification results and emits a structured coverage report
with tier-stratified file counts and percentages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .classification import ClassificationResult, V2Tier


@dataclass
class TierMetrics:
    """Metrics for a single tier."""

    tier: str
    file_count: int = 0
    file_paths: list[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        return 0.0  # Set by CoverageTracker after totals known

    def to_dict(self, total: int) -> dict[str, Any]:
        pct = (self.file_count / total * 100) if total > 0 else 0.0
        return {
            "tier": self.tier,
            "file_count": self.file_count,
            "percentage": round(pct, 2),
            "file_paths": self.file_paths,
        }


@dataclass
class CoverageArtifact:
    """Structured coverage report with tier breakdown."""

    total_files_scanned: int
    total_files_classified: int
    tier_breakdown: dict[str, dict[str, Any]]
    percentages_sum: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_files_scanned": self.total_files_scanned,
            "total_files_classified": self.total_files_classified,
            "tier_breakdown": self.tier_breakdown,
            "percentages_sum": self.percentages_sum,
        }


class CoverageTracker:
    """Accumulates classification results and emits coverage artifacts."""

    def __init__(self, total_files_scanned: int) -> None:
        self._total_scanned = total_files_scanned
        self._tier_data: dict[str, TierMetrics] = {
            V2Tier.TIER_1.value: TierMetrics(tier=V2Tier.TIER_1.value),
            V2Tier.TIER_2.value: TierMetrics(tier=V2Tier.TIER_2.value),
        }
        self._seen_files: set[str] = set()

    def add(self, result: ClassificationResult) -> None:
        """Add a classification result. Deduplicates by file_path."""
        if result.file_path in self._seen_files:
            return
        self._seen_files.add(result.file_path)

        tier_key = result.tier.value
        metrics = self._tier_data[tier_key]
        metrics.file_count += 1
        metrics.file_paths.append(result.file_path)

    def emit(self) -> CoverageArtifact:
        """Produce a coverage artifact with tier-stratified percentages."""
        total_classified = sum(m.file_count for m in self._tier_data.values())
        breakdown = {}
        pct_sum = 0.0

        for tier_key, metrics in self._tier_data.items():
            d = metrics.to_dict(total_classified)
            breakdown[tier_key] = d
            pct_sum += d["percentage"]

        return CoverageArtifact(
            total_files_scanned=self._total_scanned,
            total_files_classified=total_classified,
            tier_breakdown=breakdown,
            percentages_sum=round(pct_sum, 2),
        )
