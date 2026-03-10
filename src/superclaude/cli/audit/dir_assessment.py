"""Directory assessment blocks for large directories.

Implements T04.05 / D-0031 / AC16: directories exceeding a file count threshold
receive aggregate assessment blocks instead of per-file analysis entries.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from .classification import V2Action, V2Tier
from .consolidation import ConsolidatedFinding

DEFAULT_THRESHOLD = 50


@dataclass
class DirectoryAssessment:
    """Aggregate assessment block for a large directory."""

    directory: str
    file_count: int
    tier_distribution: dict[str, int]
    action_distribution: dict[str, int]
    dominant_tier: str
    dominant_action: str
    avg_confidence: float
    risk_summary: str
    sample_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "directory": self.directory,
            "file_count": self.file_count,
            "tier_distribution": self.tier_distribution,
            "action_distribution": self.action_distribution,
            "dominant_tier": self.dominant_tier,
            "dominant_action": self.dominant_action,
            "avg_confidence": round(self.avg_confidence, 4),
            "risk_summary": self.risk_summary,
            "sample_files": self.sample_files,
        }


def _compute_risk_summary(
    tier_dist: dict[str, int],
    action_dist: dict[str, int],
    file_count: int,
) -> str:
    """Compute a human-readable risk summary for a directory."""
    delete_count = action_dist.get("DELETE", 0)
    investigate_count = action_dist.get("INVESTIGATE", 0)
    high_risk = delete_count + investigate_count

    if high_risk == 0:
        return "low-risk: no actionable findings"
    ratio = high_risk / file_count
    if ratio > 0.5:
        return f"high-risk: {high_risk}/{file_count} files need action"
    elif ratio > 0.2:
        return f"medium-risk: {high_risk}/{file_count} files need action"
    return f"low-risk: {high_risk}/{file_count} files need action"


def identify_large_directories(
    findings: list[ConsolidatedFinding],
    threshold: int = DEFAULT_THRESHOLD,
) -> dict[str, list[ConsolidatedFinding]]:
    """Group findings by directory, return only those exceeding threshold.

    Args:
        findings: All consolidated findings.
        threshold: Minimum file count to qualify as "large" directory.

    Returns:
        Mapping of directory_path -> list of findings for large directories.
    """
    import os

    by_dir: dict[str, list[ConsolidatedFinding]] = {}
    for f in findings:
        dir_path = os.path.dirname(f.file_path) or "."
        by_dir.setdefault(dir_path, []).append(f)

    return {d: files for d, files in by_dir.items() if len(files) >= threshold}


def build_assessment_block(
    directory: str,
    findings: list[ConsolidatedFinding],
    max_sample: int = 5,
) -> DirectoryAssessment:
    """Build an aggregate assessment block for a large directory.

    Args:
        directory: Directory path.
        findings: All findings in this directory.
        max_sample: Max sample files to include in the block.

    Returns:
        DirectoryAssessment with aggregate metrics.
    """
    tier_counter: Counter[str] = Counter()
    action_counter: Counter[str] = Counter()
    confidence_sum = 0.0

    for f in findings:
        tier_counter[f.tier.value] += 1
        action_counter[f.action.value] += 1
        confidence_sum += f.confidence

    file_count = len(findings)
    avg_confidence = confidence_sum / file_count if file_count > 0 else 0.0
    tier_dist = dict(tier_counter)
    action_dist = dict(action_counter)

    dominant_tier = tier_counter.most_common(1)[0][0] if tier_counter else "unknown"
    dominant_action = action_counter.most_common(1)[0][0] if action_counter else "unknown"

    risk_summary = _compute_risk_summary(tier_dist, action_dist, file_count)
    sample_files = [f.file_path for f in findings[:max_sample]]

    return DirectoryAssessment(
        directory=directory,
        file_count=file_count,
        tier_distribution=tier_dist,
        action_distribution=action_dist,
        dominant_tier=dominant_tier,
        dominant_action=dominant_action,
        avg_confidence=avg_confidence,
        risk_summary=risk_summary,
        sample_files=sample_files,
    )


def generate_assessment_blocks(
    findings: list[ConsolidatedFinding],
    threshold: int = DEFAULT_THRESHOLD,
) -> tuple[list[DirectoryAssessment], list[ConsolidatedFinding]]:
    """Generate assessment blocks for large directories, pass through small ones.

    Args:
        findings: All consolidated findings.
        threshold: File count threshold for aggregate assessment.

    Returns:
        Tuple of (assessment_blocks, remaining_findings).
        remaining_findings are those in directories below threshold.
    """
    import os

    large_dirs = identify_large_directories(findings, threshold)
    large_dir_set = set(large_dirs.keys())

    blocks = []
    for directory, dir_findings in sorted(large_dirs.items()):
        blocks.append(build_assessment_block(directory, dir_findings))

    remaining = [
        f for f in findings
        if (os.path.dirname(f.file_path) or ".") not in large_dir_set
    ]

    return blocks, remaining
