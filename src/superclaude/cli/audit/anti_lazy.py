"""Anti-lazy distribution and consistency guards.

Implements T04.12 / D-0038 / AC18: detects suspiciously uniform classification
distributions (e.g., all KEEP) and triggers re-analysis of flagged batches.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from .classification import V2Action
from .consolidation import ConsolidatedFinding

DEFAULT_UNIFORMITY_THRESHOLD = 0.90


@dataclass
class UniformityFlag:
    """Records a batch flagged for suspicious uniformity."""

    batch_id: str
    dominant_action: str
    dominant_count: int
    total_count: int
    uniformity_ratio: float
    file_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "dominant_action": self.dominant_action,
            "dominant_count": self.dominant_count,
            "total_count": self.total_count,
            "uniformity_ratio": round(self.uniformity_ratio, 4),
            "file_paths": self.file_paths,
        }


@dataclass
class AntiLazyReport:
    """Report from anti-lazy guard analysis."""

    total_batches_checked: int
    flagged_batches: list[UniformityFlag]
    batches_passed: int
    reanalysis_triggered: bool

    @property
    def flagged_count(self) -> int:
        return len(self.flagged_batches)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_batches_checked": self.total_batches_checked,
            "flagged_count": self.flagged_count,
            "batches_passed": self.batches_passed,
            "reanalysis_triggered": self.reanalysis_triggered,
            "flagged_batches": [f.to_dict() for f in self.flagged_batches],
        }


def check_batch_uniformity(
    batch_id: str,
    findings: list[ConsolidatedFinding],
    threshold: float = DEFAULT_UNIFORMITY_THRESHOLD,
) -> UniformityFlag | None:
    """Check if a batch has suspiciously uniform classification.

    Args:
        batch_id: Identifier for this batch.
        findings: Findings in this batch.
        threshold: Uniformity threshold (default 90%).

    Returns:
        UniformityFlag if flagged, None if distribution is acceptable.
    """
    if not findings:
        return None

    action_counts = Counter(f.action.value for f in findings)
    total = len(findings)
    dominant_action, dominant_count = action_counts.most_common(1)[0]
    uniformity = dominant_count / total

    if uniformity > threshold:
        return UniformityFlag(
            batch_id=batch_id,
            dominant_action=dominant_action,
            dominant_count=dominant_count,
            total_count=total,
            uniformity_ratio=uniformity,
            file_paths=[f.file_path for f in findings],
        )

    return None


def run_anti_lazy_guard(
    batches: dict[str, list[ConsolidatedFinding]],
    threshold: float = DEFAULT_UNIFORMITY_THRESHOLD,
) -> AntiLazyReport:
    """Run anti-lazy guard across all batches.

    Args:
        batches: Mapping of batch_id -> list of findings.
        threshold: Uniformity threshold (default 90%).

    Returns:
        AntiLazyReport with flagged batches.
    """
    flagged: list[UniformityFlag] = []
    passed = 0

    for batch_id, findings in sorted(batches.items()):
        flag = check_batch_uniformity(batch_id, findings, threshold)
        if flag:
            flagged.append(flag)
        else:
            passed += 1

    return AntiLazyReport(
        total_batches_checked=len(batches),
        flagged_batches=flagged,
        batches_passed=passed,
        reanalysis_triggered=len(flagged) > 0,
    )
