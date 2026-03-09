"""Roadmap gate criteria -- data definitions for each pipeline step's gate.

This module defines GateCriteria instances as module-level constants.
Gate criteria are pure data -- no logic, no imports from pipeline/gates.py
enforcement code (NFR-005).

Semantic check functions are defined here as pure functions accepting
file content and returning bool. They are registered on the STRICT-tier
GateCriteria instances.
"""

from __future__ import annotations

from ..pipeline.models import GateCriteria, SemanticCheck


# --- Semantic check functions (pure: content -> bool) ---

def _no_heading_gaps(content: str) -> bool:
    """Verify heading levels increment by at most 1 (no H2 -> H4 skip)."""
    prev_level = 0
    for line in content.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            level = 0
            for ch in stripped:
                if ch == "#":
                    level += 1
                else:
                    break
            if prev_level > 0 and level > prev_level + 1:
                return False
            prev_level = level
    return True


def _cross_refs_resolve(content: str) -> bool:
    """Verify all 'See section' / cross-reference patterns have matching headings.

    Checks that internal references like 'See section X.Y' or 'See X.Y'
    have corresponding headings. Unresolved references emit warnings but
    do not block the pipeline (warning-only mode per OQ-001 for v2.20).
    """
    import re
    import warnings

    # Extract heading anchors (simplified: heading text, lowercased)
    headings: set[str] = set()
    for line in content.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            heading_text = stripped.lstrip("#").strip().lower()
            headings.add(heading_text)

    # Find cross-references like "See section X" or "(see X.Y)"
    refs = re.findall(r'[Ss]ee\s+(?:[Ss]ection\s+)?["\']?(\d+(?:\.\d+)*)', content)
    # If there are no cross-references, that's fine
    if not refs:
        return True

    # Check each reference against headings
    unresolved: list[str] = []
    for ref in refs:
        found = any(ref in h for h in headings)
        if not found:
            # Also check if the section number appears as a heading prefix
            found = any(h.startswith(ref) for h in headings)
        if not found:
            unresolved.append(ref)

    if unresolved:
        for ref in unresolved:
            warnings.warn(
                f"Unresolved cross-reference: 'See section {ref}' has no matching heading",
                stacklevel=2,
            )
        # Warning-only mode (OQ-001): return True to avoid blocking pipeline
        return True

    return True


def _no_duplicate_headings(content: str) -> bool:
    """No duplicate H2 or H3 heading text."""
    seen: dict[int, set[str]] = {2: set(), 3: set()}
    for line in content.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            text = stripped[3:].strip().lower()
            if text in seen[2]:
                return False
            seen[2].add(text)
        elif stripped.startswith("### "):
            text = stripped[4:].strip().lower()
            if text in seen[3]:
                return False
            seen[3].add(text)
    return True


def _frontmatter_values_non_empty(content: str) -> bool:
    """All YAML frontmatter fields have non-empty values."""
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return False

    rest = stripped[3:].lstrip("\n")
    end_idx = rest.find("\n---")
    if end_idx == -1:
        return False

    frontmatter_text = rest[:end_idx]
    for line in frontmatter_text.splitlines():
        line = line.strip()
        if ":" in line:
            _key, value = line.split(":", 1)
            if not value.strip():
                return False
    return True


def _has_actionable_content(content: str) -> bool:
    """At least one section contains numbered or bulleted items."""
    import re
    # Look for markdown list items: "- ", "* ", "1. ", "2. ", etc.
    return bool(re.search(r'^\s*(?:[-*]|\d+\.)\s+\S', content, re.MULTILINE))


def _parse_frontmatter(content: str) -> dict[str, str] | None:
    """Extract YAML frontmatter key-value pairs from content.

    Returns a dict of key→value strings, or None if no frontmatter found.
    """
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return None

    rest = stripped[3:].lstrip("\n")
    end_idx = rest.find("\n---")
    if end_idx == -1:
        return None

    result: dict[str, str] = {}
    for line in rest[:end_idx].splitlines():
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def _high_severity_count_zero(content: str) -> bool:
    """Validate that high_severity_count equals zero in fidelity report frontmatter.

    Returns True only if the frontmatter contains high_severity_count with
    integer value 0. Returns False if:
    - Frontmatter is missing
    - high_severity_count field is missing
    - high_severity_count > 0

    Raises TypeError if high_severity_count value is not parseable as an integer.
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    value = fm.get("high_severity_count")
    if value is None:
        return False

    try:
        count = int(value)
    except (ValueError, TypeError):
        raise TypeError(
            f"high_severity_count must be an integer, got: {value!r}"
        )

    return count == 0


def _tasklist_ready_consistent(content: str) -> bool:
    """Validate tasklist_ready is consistent with severity counts.

    Consistency rule: tasklist_ready=true requires high_severity_count=0
    AND validation_complete=true. If tasklist_ready=true but either
    condition fails, this returns False (inconsistency detected).

    Returns False if:
    - Frontmatter is missing
    - tasklist_ready field is missing
    - Inconsistency: tasklist_ready=true but high_severity_count > 0
    - Inconsistency: tasklist_ready=true but validation_complete != true
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    tasklist_ready_str = fm.get("tasklist_ready")
    if tasklist_ready_str is None:
        return False

    tasklist_ready = tasklist_ready_str.lower() == "true"

    if not tasklist_ready:
        # If tasklist_ready is false, that's always consistent
        return True

    # tasklist_ready is true -- verify consistency
    high_str = fm.get("high_severity_count")
    if high_str is None:
        return False
    try:
        high_count = int(high_str)
    except (ValueError, TypeError):
        return False

    if high_count > 0:
        return False

    validation_str = fm.get("validation_complete")
    if validation_str is None:
        return False
    if validation_str.lower() != "true":
        return False

    return True


def _convergence_score_valid(content: str) -> bool:
    """convergence_score frontmatter value parses as float in [0.0, 1.0]."""
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return False

    rest = stripped[3:].lstrip("\n")
    end_idx = rest.find("\n---")
    if end_idx == -1:
        return False

    frontmatter_text = rest[:end_idx]
    for line in frontmatter_text.splitlines():
        line = line.strip()
        if line.startswith("convergence_score:"):
            value = line.split(":", 1)[1].strip()
            try:
                score = float(value)
                return 0.0 <= score <= 1.0
            except ValueError:
                return False
    return False  # convergence_score field not found


# --- GateCriteria instances ---

EXTRACT_GATE = GateCriteria(
    required_frontmatter_fields=[
        "spec_source",
        "generated",
        "generator",
        "functional_requirements",
        "nonfunctional_requirements",
        "total_requirements",
        "complexity_score",
        "complexity_class",
        "domains_detected",
        "risks_identified",
        "dependencies_identified",
        "success_criteria_count",
        "extraction_mode",
    ],
    min_lines=50,
    enforcement_tier="STRICT",
)

GENERATE_A_GATE = GateCriteria(
    required_frontmatter_fields=["spec_source", "complexity_score", "primary_persona"],
    min_lines=100,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_values_non_empty",
            check_fn=_frontmatter_values_non_empty,
            failure_message="One or more required frontmatter fields have empty values",
        ),
        SemanticCheck(
            name="has_actionable_content",
            check_fn=_has_actionable_content,
            failure_message="No numbered or bulleted items found -- roadmap must contain actionable content",
        ),
    ],
)

GENERATE_B_GATE = GateCriteria(
    required_frontmatter_fields=["spec_source", "complexity_score", "primary_persona"],
    min_lines=100,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_values_non_empty",
            check_fn=_frontmatter_values_non_empty,
            failure_message="One or more required frontmatter fields have empty values",
        ),
        SemanticCheck(
            name="has_actionable_content",
            check_fn=_has_actionable_content,
            failure_message="No numbered or bulleted items found -- roadmap must contain actionable content",
        ),
    ],
)

DIFF_GATE = GateCriteria(
    required_frontmatter_fields=["total_diff_points", "shared_assumptions_count"],
    min_lines=30,
    enforcement_tier="STANDARD",
)

DEBATE_GATE = GateCriteria(
    required_frontmatter_fields=["convergence_score", "rounds_completed"],
    min_lines=50,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="convergence_score_valid",
            check_fn=_convergence_score_valid,
            failure_message="convergence_score must be a float in [0.0, 1.0]",
        ),
    ],
)

SCORE_GATE = GateCriteria(
    required_frontmatter_fields=["base_variant", "variant_scores"],
    min_lines=20,
    enforcement_tier="STANDARD",
)

MERGE_GATE = GateCriteria(
    required_frontmatter_fields=["spec_source", "complexity_score", "adversarial"],
    min_lines=150,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="no_heading_gaps",
            check_fn=_no_heading_gaps,
            failure_message="Heading level gap detected (e.g. H2 -> H4 without H3)",
        ),
        SemanticCheck(
            name="cross_refs_resolve",
            check_fn=_cross_refs_resolve,
            failure_message="Internal cross-reference does not resolve to an existing heading",
        ),
        SemanticCheck(
            name="no_duplicate_headings",
            check_fn=_no_duplicate_headings,
            failure_message="Duplicate H2 or H3 heading text detected",
        ),
    ],
)

TEST_STRATEGY_GATE = GateCriteria(
    required_frontmatter_fields=["validation_milestones", "interleave_ratio"],
    min_lines=40,
    enforcement_tier="STANDARD",
)

SPEC_FIDELITY_GATE = GateCriteria(
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
            failure_message="high_severity_count must be 0 for spec-fidelity gate to pass",
        ),
        SemanticCheck(
            name="tasklist_ready_consistent",
            check_fn=_tasklist_ready_consistent,
            failure_message="tasklist_ready is inconsistent with severity counts or validation_complete",
        ),
    ],
)

# All gates in pipeline order for reference
ALL_GATES = [
    ("extract", EXTRACT_GATE),
    ("generate-A", GENERATE_A_GATE),
    ("generate-B", GENERATE_B_GATE),
    ("diff", DIFF_GATE),
    ("debate", DEBATE_GATE),
    ("score", SCORE_GATE),
    ("merge", MERGE_GATE),
    ("test-strategy", TEST_STRATEGY_GATE),
    ("spec-fidelity", SPEC_FIDELITY_GATE),
]
