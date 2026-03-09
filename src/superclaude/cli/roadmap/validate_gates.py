"""Validation gate criteria -- data definitions for validate pipeline steps.

Defines GateCriteria instances for the validation subsystem:
REFLECT_GATE and ADVERSARIAL_MERGE_GATE.

Imports from roadmap/gates.py only (unidirectional dependency preserved).
"""

from __future__ import annotations

from ..pipeline.models import GateCriteria, SemanticCheck
from .gates import _frontmatter_values_non_empty


def _has_agreement_table(content: str) -> bool:
    """Check that content contains a markdown agreement table.

    An agreement table has a header row containing 'agree' or 'agreement'
    (case-insensitive) and at least one pipe-delimited data row.
    """
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "|" in line and ("agree" in line.lower() or "agreement" in line.lower()):
            # Check for a separator row after header
            if i + 1 < len(lines) and "|" in lines[i + 1] and "-" in lines[i + 1]:
                return True
    return False


REFLECT_GATE = GateCriteria(
    required_frontmatter_fields=[
        "blocking_issues_count",
        "warnings_count",
        "tasklist_ready",
    ],
    min_lines=20,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_values_non_empty",
            check_fn=_frontmatter_values_non_empty,
            failure_message="One or more required frontmatter fields have empty values",
        ),
    ],
)

ADVERSARIAL_MERGE_GATE = GateCriteria(
    required_frontmatter_fields=[
        "blocking_issues_count",
        "warnings_count",
        "tasklist_ready",
        "validation_mode",
        "validation_agents",
    ],
    min_lines=30,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_values_non_empty",
            check_fn=_frontmatter_values_non_empty,
            failure_message="One or more required frontmatter fields have empty values",
        ),
        SemanticCheck(
            name="agreement_table_present",
            check_fn=_has_agreement_table,
            failure_message="No agreement table found -- adversarial merge requires an agreement/disagreement table",
        ),
    ],
)
