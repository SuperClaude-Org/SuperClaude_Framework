"""Tasklist gate criteria -- data definitions for tasklist validation.

Defines TASKLIST_FIDELITY_GATE as a module-level constant. Gate criteria
are pure data -- no logic, no imports from pipeline/gates.py enforcement
code (NFR-005).

Reuses semantic check functions from roadmap/gates.py:
- _high_severity_count_zero
- _tasklist_ready_consistent

This follows the same unidirectional dependency pattern as
roadmap/validate_gates.py.
"""

from __future__ import annotations

from ..pipeline.models import GateCriteria, SemanticCheck
from ..roadmap.gates import _high_severity_count_zero, _tasklist_ready_consistent

TASKLIST_FIDELITY_GATE = GateCriteria(
    required_frontmatter_fields=[
        "high_severity_count",
        "medium_severity_count",
        "low_severity_count",
        "total_deviations",
        "validation_complete",
        "tasklist_ready",
    ],
    min_lines=20,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="high_severity_count_zero",
            check_fn=_high_severity_count_zero,
            failure_message="high_severity_count must be 0 for tasklist-fidelity gate to pass",
        ),
        SemanticCheck(
            name="tasklist_ready_consistent",
            check_fn=_tasklist_ready_consistent,
            failure_message="tasklist_ready is inconsistent with severity counts or validation_complete",
        ),
    ],
)
