"""Report depth modes: summary, standard, detailed.

Implements T04.10 / D-0036 / AC10: configurable report depth so operators
can choose between concise summaries and detailed per-file analysis.

Depth levels:
  summary:  tier counts + top 10 findings only
  standard: per-section findings with evidence (default)
  detailed: per-file profiles + full evidence chains
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .consolidation import ConsolidatedFinding, ConsolidationReport
from .dir_assessment import DirectoryAssessment


class ReportDepth(Enum):
    """Report output depth level."""

    SUMMARY = "summary"
    STANDARD = "standard"
    DETAILED = "detailed"


def parse_depth(value: str | None) -> ReportDepth:
    """Parse depth flag value. Default: STANDARD."""
    if value is None:
        return ReportDepth.STANDARD
    try:
        return ReportDepth(value.lower())
    except ValueError:
        raise ValueError(
            f"Invalid depth '{value}'. Must be one of: summary, standard, detailed"
        )


def render_summary(
    report: ConsolidationReport,
    assessment_blocks: list[DirectoryAssessment] | None = None,
) -> dict[str, Any]:
    """Render summary depth: tier counts + top 10 findings.

    Args:
        report: Consolidated audit report.
        assessment_blocks: Optional directory assessment blocks.

    Returns:
        Summary report dict.
    """
    tier_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    for f in report.findings:
        tier_counts[f.tier.value] += 1
        action_counts[f.action.value] += 1

    # Top 10 by confidence (descending), then alphabetical
    sorted_findings = sorted(
        report.findings,
        key=lambda f: (-f.confidence, f.file_path),
    )
    top_findings = [
        {
            "file_path": f.file_path,
            "tier": f.tier.value,
            "action": f.action.value,
            "confidence": f.confidence,
        }
        for f in sorted_findings[:10]
    ]

    result: dict[str, Any] = {
        "depth": "summary",
        "total_findings": report.total_consolidated,
        "tier_counts": dict(tier_counts),
        "action_counts": dict(action_counts),
        "top_findings": top_findings,
        "conflict_count": len(report.conflicts),
    }

    if assessment_blocks:
        result["directory_assessments"] = [b.to_dict() for b in assessment_blocks]

    return result


def render_standard(
    report: ConsolidationReport,
    assessment_blocks: list[DirectoryAssessment] | None = None,
) -> dict[str, Any]:
    """Render standard depth: per-section findings with evidence.

    Args:
        report: Consolidated audit report.
        assessment_blocks: Optional directory assessment blocks.

    Returns:
        Standard report dict.
    """
    # Group findings by action
    by_action: dict[str, list[dict[str, Any]]] = {}
    for f in report.findings:
        key = f.action.value
        entry = {
            "file_path": f.file_path,
            "tier": f.tier.value,
            "confidence": f.confidence,
            "evidence": f.evidence,
            "source_phases": f.source_phases,
        }
        if f.conflict:
            entry["conflict"] = f.conflict.to_dict()
        by_action.setdefault(key, []).append(entry)

    tier_counts: Counter[str] = Counter()
    for f in report.findings:
        tier_counts[f.tier.value] += 1

    result: dict[str, Any] = {
        "depth": "standard",
        "total_findings": report.total_consolidated,
        "tier_counts": dict(tier_counts),
        "sections": by_action,
        "conflict_count": len(report.conflicts),
    }

    if assessment_blocks:
        result["directory_assessments"] = [b.to_dict() for b in assessment_blocks]

    return result


def render_detailed(
    report: ConsolidationReport,
    assessment_blocks: list[DirectoryAssessment] | None = None,
) -> dict[str, Any]:
    """Render detailed depth: per-file profiles + full evidence chains.

    Args:
        report: Consolidated audit report.
        assessment_blocks: Optional directory assessment blocks.

    Returns:
        Detailed report dict.
    """
    file_entries = []
    for f in report.findings:
        entry = f.to_dict()
        file_entries.append(entry)

    tier_counts: Counter[str] = Counter()
    for f in report.findings:
        tier_counts[f.tier.value] += 1

    result: dict[str, Any] = {
        "depth": "detailed",
        "total_findings": report.total_consolidated,
        "tier_counts": dict(tier_counts),
        "files": file_entries,
        "conflicts": [c.to_dict() for c in report.conflicts],
    }

    if assessment_blocks:
        result["directory_assessments"] = [b.to_dict() for b in assessment_blocks]

    return result


def render_report(
    report: ConsolidationReport,
    depth: ReportDepth = ReportDepth.STANDARD,
    assessment_blocks: list[DirectoryAssessment] | None = None,
) -> dict[str, Any]:
    """Render report at the specified depth level.

    Args:
        report: Consolidated audit report.
        depth: Output depth level.
        assessment_blocks: Optional directory assessment blocks.

    Returns:
        Report dict at the requested depth.
    """
    renderers = {
        ReportDepth.SUMMARY: render_summary,
        ReportDepth.STANDARD: render_standard,
        ReportDepth.DETAILED: render_detailed,
    }
    return renderers[depth](report, assessment_blocks)
