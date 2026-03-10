"""Gate criteria and semantic checks for Cleanup Audit pipeline.

Each step's output must pass its gate before the pipeline continues.
Gates enforce structural and semantic quality programmatically,
removing this responsibility from inference.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

import re

from superclaude.cli.pipeline.models import GateCriteria, SemanticCheck


# --- Semantic Check Functions ---
# Pure functions: Callable[[str], bool]  (content: str) -> bool


def has_classification_table(content: str) -> bool:
    """Check that content contains a classification results table."""
    return bool(
        re.search(r"\|.*File.*\|.*Classification.*\|", content, re.IGNORECASE)
    )


def has_per_file_profiles(content: str) -> bool:
    """Check that content contains per-file profile sections."""
    return bool(re.search(r"##\s+.*\.(?:py|ts|js|md)", content))


def has_cross_cutting_findings(content: str) -> bool:
    """Check that content contains cross-cutting analysis findings."""
    return bool(
        re.search(r"(?:cross-cutting|duplication|sprawl)", content, re.IGNORECASE)
    )


def has_consolidation_opportunities(content: str) -> bool:
    """Check that content identifies consolidation opportunities."""
    return bool(
        re.search(r"(?:consolidat|merg|deduplic)", content, re.IGNORECASE)
    )


def has_deduplication_evidence(content: str) -> bool:
    """Check that the summary contains deduplication analysis evidence."""
    return bool(
        re.search(r"(?:deduplic|duplicate|overlap)", content, re.IGNORECASE)
    )


def has_exit_recommendation(content: str) -> bool:
    """Check that content contains an EXIT_RECOMMENDATION marker."""
    return "EXIT_RECOMMENDATION:" in content


def has_validation_verdicts(content: str) -> bool:
    """Check that validation output contains pass/fail verdicts."""
    return bool(
        re.search(r"(?:PASS|FAIL|verdict|validated)", content, re.IGNORECASE)
    )


# --- Gate Definitions ---

GATE_G001 = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=0,
    enforcement_tier="LIGHT",
    semantic_checks=None,
)

GATE_G002 = GateCriteria(
    required_frontmatter_fields=["title", "status", "pass"],
    min_lines=50,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck(
            name="has_classification_table",
            check_fn=has_classification_table,
            failure_message="Missing classification results table",
        ),
    ],
)

GATE_G003 = GateCriteria(
    required_frontmatter_fields=["title", "status", "pass"],
    min_lines=50,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck(
            name="has_per_file_profiles",
            check_fn=has_per_file_profiles,
            failure_message="Missing per-file profile sections",
        ),
    ],
)

GATE_G004 = GateCriteria(
    required_frontmatter_fields=["title", "status", "pass", "finding_count"],
    min_lines=100,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="has_cross_cutting_findings",
            check_fn=has_cross_cutting_findings,
            failure_message="Missing cross-cutting analysis findings",
        ),
        SemanticCheck(
            name="has_consolidation_opportunities",
            check_fn=has_consolidation_opportunities,
            failure_message="Missing consolidation opportunities",
        ),
    ],
)

GATE_G005 = GateCriteria(
    required_frontmatter_fields=[
        "title",
        "status",
        "total_findings",
        "severity_distribution",
    ],
    min_lines=100,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="has_deduplication_evidence",
            check_fn=has_deduplication_evidence,
            failure_message="Missing deduplication evidence in summary",
        ),
        SemanticCheck(
            name="has_exit_recommendation",
            check_fn=has_exit_recommendation,
            failure_message="Missing EXIT_RECOMMENDATION marker",
        ),
    ],
)

GATE_G006 = GateCriteria(
    required_frontmatter_fields=["title", "status"],
    min_lines=30,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck(
            name="has_validation_verdicts",
            check_fn=has_validation_verdicts,
            failure_message="Missing validation verdicts",
        ),
    ],
)

# Collected for iteration
ALL_GATES: dict[str, GateCriteria] = {
    "G-001": GATE_G001,
    "G-002": GATE_G002,
    "G-003": GATE_G003,
    "G-004": GATE_G004,
    "G-005": GATE_G005,
    "G-006": GATE_G006,
}
