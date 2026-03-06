"""Known limitations and non-determinism sources for final report.

Implements T05.08 / D-0047 / AC6 (quality extension):
  Documents sources of non-determinism and their impact on result reliability.
  Section is inserted between validation results and appendix.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LimitationEntry:
    """A known limitation or non-determinism source."""

    source: str
    impact: str
    mitigation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "impact": self.impact,
            "mitigation": self.mitigation,
        }


# Catalog of known non-determinism sources
KNOWN_LIMITATIONS: list[LimitationEntry] = [
    LimitationEntry(
        source="LLM Classification Variance",
        impact=(
            "Borderline files may shift 1-2 action categories between runs. "
            "Primarily affects Tier-2/3 files with lower confidence."
        ),
        mitigation=(
            "Evidence-gated DELETE (grep count 0), confidence thresholds, "
            "anti-lazy guard (>90% uniformity), 10% spot-check validation."
        ),
    ),
    LimitationEntry(
        source="Git History Dependency",
        impact=(
            "Shallow clones or squashed history may produce inaccurate "
            "staleness, age, and churn profiling results."
        ),
        mitigation=(
            "Missing git dates treated as unknown, budget caveats document "
            "dependency on git history depth."
        ),
    ),
    LimitationEntry(
        source="Dynamic Import Detection Limits",
        impact=(
            "Files consumed exclusively via dynamic imports may be falsely "
            "classified as dead code (false positive DELETE)."
        ),
        mitigation=(
            "Dynamic import pattern scanner, KEEP:monitor protection for "
            "detected patterns, framework hook exclusion list."
        ),
    ),
    LimitationEntry(
        source="Tier-C Inference Confidence",
        impact=(
            "Co-occurrence heuristic edges may create false dependency "
            "relationships, affecting dead code detection accuracy."
        ),
        mitigation=(
            "Tier-C weighted at 40% vs Tier-A 100%, dead code detection "
            "primarily uses Tier-A/B, evidence type labeled in reports."
        ),
    ),
]


def build_limitations_section() -> dict[str, Any]:
    """Build the limitations section for the final report.

    Returns a dict suitable for inclusion in the report between
    validation_results and appendix.
    """
    return {
        "title": "Known Limitations and Non-Determinism Sources",
        "limitations": [lim.to_dict() for lim in KNOWN_LIMITATIONS],
        "limitation_count": len(KNOWN_LIMITATIONS),
        "overall_assessment": (
            "Mitigations reduce but do not eliminate non-determinism. "
            "Audit results are recommendations requiring human review, "
            "particularly for DELETE classifications with low confidence."
        ),
    }


def render_limitations_markdown() -> str:
    """Render the limitations section as markdown."""
    lines = [
        "## Known Limitations and Non-Determinism Sources",
        "",
        "| # | Source | Impact | Mitigation |",
        "|---|--------|--------|------------|",
    ]
    for i, lim in enumerate(KNOWN_LIMITATIONS, start=1):
        lines.append(f"| {i} | {lim.source} | {lim.impact} | {lim.mitigation} |")

    lines.extend([
        "",
        "**Overall Assessment**: Mitigations reduce but do not eliminate "
        "non-determinism. Audit results are recommendations requiring human "
        "review, particularly for DELETE classifications with low confidence.",
    ])

    return "\n".join(lines)
