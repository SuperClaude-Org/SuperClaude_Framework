"""State variable detection -- scans deliverable descriptions for variable introductions.

Provides:
- detect_state_variables(): scans descriptions for self._ assignments, counter/offset/cursor
  introductions, and type replacement patterns
- DetectionResult: tuple of (variable_name, deliverable_id, introduction_type)

Detection categories:
1. self._* assignments
2. "introduce variable", "add counter/offset/cursor/flag"
3. "replace X with Y" where Y is state-tracking type

Low-confidence detections are flagged for human review (R-004 mitigation).

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .models import Deliverable


class IntroductionType(Enum):
    """How a state variable was introduced."""
    SELF_ASSIGNMENT = "self_assignment"
    COUNTER = "counter"
    OFFSET = "offset"
    CURSOR = "cursor"
    FLAG = "flag"
    REPLACEMENT = "replacement"
    GENERIC = "generic"


@dataclass
class DetectionResult:
    """A detected state variable introduction.

    Attributes:
        variable_name: Extracted or inferred variable name.
        deliverable_id: ID of the deliverable containing the introduction.
        introduction_type: How the variable was introduced.
        confidence: Detection confidence (0.0-1.0). Below 0.7 = flagged for review.
    """
    variable_name: str
    deliverable_id: str
    introduction_type: IntroductionType
    confidence: float = 1.0

    @property
    def needs_review(self) -> bool:
        return self.confidence < 0.7


# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

# self._field patterns
_SELF_FIELD_RE = re.compile(r"self\.(_\w+)")

# Explicit introduction patterns
_INTRO_PATTERNS = [
    # "introduce <variable_name>" / "add <type> <variable_name>"
    (re.compile(r"\bintroduce\s+(?:a\s+|an\s+)?(?:new\s+)?(\w+)", re.IGNORECASE), IntroductionType.GENERIC, 0.85),
    (re.compile(r"\badd\s+(?:a\s+|an\s+)?(?:new\s+)?counter\b[\s:]*(\w*)", re.IGNORECASE), IntroductionType.COUNTER, 0.9),
    (re.compile(r"\badd\s+(?:a\s+|an\s+)?(?:new\s+)?offset\b[\s:]*(\w*)", re.IGNORECASE), IntroductionType.OFFSET, 0.9),
    (re.compile(r"\badd\s+(?:a\s+|an\s+)?(?:new\s+)?cursor\b[\s:]*(\w*)", re.IGNORECASE), IntroductionType.CURSOR, 0.9),
    (re.compile(r"\badd\s+(?:a\s+|an\s+)?(?:new\s+)?flag\b[\s:]*(\w*)", re.IGNORECASE), IntroductionType.FLAG, 0.9),
    # Reverse patterns: "add X counter/offset/cursor/flag" (type keyword after qualifier)
    (re.compile(r"\badd\s+((?:\w+\s+)+)counter\b", re.IGNORECASE), IntroductionType.COUNTER, 0.85),
    (re.compile(r"\badd\s+((?:\w+\s+)+)offset\b", re.IGNORECASE), IntroductionType.OFFSET, 0.85),
    (re.compile(r"\badd\s+((?:\w+\s+)+)cursor\b", re.IGNORECASE), IntroductionType.CURSOR, 0.85),
    (re.compile(r"\badd\s+((?:\w+\s+)+)flag\b", re.IGNORECASE), IntroductionType.FLAG, 0.85),
    # "introduce cursor for ..."
    (re.compile(r"\bintroduce\s+(?:a\s+|an\s+)?cursor\b\s+(?:for\s+)?(\w*)", re.IGNORECASE), IntroductionType.CURSOR, 0.9),
    (re.compile(r"\bintroduce\s+(?:a\s+|an\s+)?counter\b\s+(?:for\s+)?(\w*)", re.IGNORECASE), IntroductionType.COUNTER, 0.9),
    (re.compile(r"\bintroduce\s+(?:a\s+|an\s+)?offset\b\s+(?:for\s+)?(\w*)", re.IGNORECASE), IntroductionType.OFFSET, 0.9),
    (re.compile(r"\bintroduce\s+(?:a\s+|an\s+)?flag\b\s+(?:for\s+)?(\w*)", re.IGNORECASE), IntroductionType.FLAG, 0.9),
]

# Type replacement pattern: "replace X with Y"
_REPLACEMENT_RE = re.compile(
    r"\breplace\s+(\w+)\s+with\s+(\w[\w\s]*)",
    re.IGNORECASE,
)

# State-tracking type synonyms (extensible)
STATE_TYPE_SYNONYMS: set[str] = {
    "int", "integer", "offset", "counter", "cursor", "flag",
    "boolean", "bool", "enum", "state", "index", "tracker",
    "accumulator", "pointer", "sentinel", "marker",
}

# Documentation suppression patterns
_DOC_SUPPRESSION_RE = re.compile(
    r"\b(?:document|describe|explain|list|outline|summarize)\b",
    re.IGNORECASE,
)


def detect_state_variables(
    deliverables: list[Deliverable],
) -> list[DetectionResult]:
    """Scan deliverable descriptions for state variable introductions.

    Returns a list of DetectionResult tuples. Low-confidence detections
    (confidence < 0.7) are flagged for human review.

    Multiple variables from a single deliverable are all returned.
    Documentation-only deliverables are excluded.
    """
    results: list[DetectionResult] = []

    for d in deliverables:
        desc = d.description
        if not desc or not desc.strip():
            continue

        # Documentation suppression
        if _DOC_SUPPRESSION_RE.search(desc) and not _has_strong_state_signal(desc):
            continue

        found = _detect_from_description(desc, d.id)
        results.extend(found)

    return results


def _has_strong_state_signal(desc: str) -> bool:
    """Check if description has strong state variable signals despite doc verbs."""
    lower = desc.lower()
    if _SELF_FIELD_RE.search(lower):
        return True
    for keyword in ("counter", "offset", "cursor", "flag", "replace"):
        if keyword in lower:
            return True
    return False


def _detect_from_description(desc: str, deliverable_id: str) -> list[DetectionResult]:
    """Extract state variable detections from a single description."""
    results: list[DetectionResult] = []
    seen_vars: set[str] = set()

    # 1. self._field patterns (highest confidence)
    for match in _SELF_FIELD_RE.finditer(desc):
        var_name = match.group(1)
        if var_name not in seen_vars:
            seen_vars.add(var_name)
            results.append(DetectionResult(
                variable_name=var_name,
                deliverable_id=deliverable_id,
                introduction_type=IntroductionType.SELF_ASSIGNMENT,
                confidence=0.95,
            ))

    # 2. Explicit introduction patterns
    for pattern, intro_type, confidence in _INTRO_PATTERNS:
        for match in pattern.finditer(desc):
            var_name = match.group(1).strip() if match.group(1) else intro_type.value
            if not var_name:
                var_name = intro_type.value
            if var_name not in seen_vars:
                seen_vars.add(var_name)
                results.append(DetectionResult(
                    variable_name=var_name,
                    deliverable_id=deliverable_id,
                    introduction_type=intro_type,
                    confidence=confidence,
                ))

    # 3. Type replacement patterns
    for match in _REPLACEMENT_RE.finditer(desc):
        old_type = match.group(1).strip()
        new_type_phrase = match.group(2).strip()
        # Check if replacement target is a state-tracking type
        new_type_words = set(new_type_phrase.lower().split())
        if new_type_words & STATE_TYPE_SYNONYMS:
            var_name = old_type
            if var_name not in seen_vars:
                seen_vars.add(var_name)
                results.append(DetectionResult(
                    variable_name=var_name,
                    deliverable_id=deliverable_id,
                    introduction_type=IntroductionType.REPLACEMENT,
                    confidence=0.85,
                ))

    return results
