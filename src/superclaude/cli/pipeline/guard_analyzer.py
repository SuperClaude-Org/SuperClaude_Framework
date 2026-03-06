"""Guard and sentinel analyzer -- detects conditional logic and type changes in deliverables.

Detects:
1. Guards: if/else, early return, sentinel values, flag checks
2. Type changes: bool->int, enum->string, bool->enum
3. State enumeration: all possible values and semantic meanings per guard variable
4. Ambiguity detection: flags when one value maps to multiple semantic meanings

Bool->int type changes always trigger transition analysis regardless of ambiguity.

R-009 mitigation: @no-ambiguity-check annotation suppresses detection with documented rationale.
R-010 mitigation: seed with known archetypes for guard patterns.

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from .models import Deliverable, DeliverableKind


class GuardKind(Enum):
    """Classification of guard/conditional pattern detected."""
    IF_ELSE = "if_else"
    EARLY_RETURN = "early_return"
    SENTINEL_VALUE = "sentinel_value"
    FLAG_CHECK = "flag_check"
    TYPE_CHANGE = "type_change"


class TypeTransitionKind(Enum):
    """Classification of type transition detected."""
    BOOL_TO_INT = "bool_to_int"
    BOOL_TO_ENUM = "bool_to_enum"
    ENUM_TO_STRING = "enum_to_string"
    INT_TO_ENUM = "int_to_enum"
    OTHER = "other"


@dataclass
class SemanticMeaning:
    """A single semantic meaning for a guard value."""
    value: str
    meaning: str


@dataclass
class GuardState:
    """Enumerated state of a guard variable."""
    value: str
    semantic_meanings: list[SemanticMeaning] = field(default_factory=list)

    @property
    def is_ambiguous(self) -> bool:
        """A value is ambiguous when it maps to multiple semantic meanings."""
        return len(self.semantic_meanings) > 1


@dataclass
class GuardDetection:
    """A detected guard/conditional pattern in a deliverable.

    Attributes:
        deliverable_id: Source deliverable.
        guard_variable: Name of the guard variable or sentinel.
        guard_kind: Classification of the guard pattern.
        states: Enumerated states with semantic meanings.
        type_transition: If a type change was detected, the transition kind.
        ambiguity_flagged: Whether ambiguity was detected.
        suppressed: True if @no-ambiguity-check annotation present.
        suppression_rationale: Rationale from the suppression annotation.
    """
    deliverable_id: str
    guard_variable: str
    guard_kind: GuardKind
    states: list[GuardState] = field(default_factory=list)
    type_transition: TypeTransitionKind | None = None
    ambiguity_flagged: bool = False
    suppressed: bool = False
    suppression_rationale: str = ""

    @property
    def requires_transition_analysis(self) -> bool:
        """Bool->int type changes always require transition analysis."""
        return self.type_transition == TypeTransitionKind.BOOL_TO_INT

    @property
    def has_ambiguity(self) -> bool:
        """True if any state value maps to multiple semantic meanings."""
        return any(s.is_ambiguous for s in self.states)


# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

# Guard patterns in deliverable descriptions
_GUARD_PATTERNS = [
    # "if <condition> ... else ..." or "check if"
    (re.compile(r"\bif\s+(\w+)\b.*\belse\b", re.IGNORECASE), GuardKind.IF_ELSE),
    (re.compile(r"\bcheck\s+(?:if|whether)\s+(\w+)", re.IGNORECASE), GuardKind.FLAG_CHECK),
    # "early return when <condition>"
    (re.compile(r"\bearly\s+return\b.*?\b(\w+)", re.IGNORECASE), GuardKind.EARLY_RETURN),
    # "sentinel value" or "<variable> as sentinel"
    (re.compile(r"\b(\w+)\s+(?:as\s+)?sentinel\b", re.IGNORECASE), GuardKind.SENTINEL_VALUE),
    (re.compile(r"\bsentinel\s+(?:value\s+)?(?:for\s+)?(\w+)", re.IGNORECASE), GuardKind.SENTINEL_VALUE),
    # "guard" keyword
    (re.compile(r"\b(\w+)\s+guard\b", re.IGNORECASE), GuardKind.FLAG_CHECK),
    (re.compile(r"\bguard\s+(?:on\s+|for\s+|using\s+)?(\w+)", re.IGNORECASE), GuardKind.FLAG_CHECK),
    # "flag" check
    (re.compile(r"\b(\w+)\s+flag\b", re.IGNORECASE), GuardKind.FLAG_CHECK),
    (re.compile(r"\bflag\s+(\w+)", re.IGNORECASE), GuardKind.FLAG_CHECK),
    # "bounded by" / "threshold" / "limit"
    (re.compile(r"\bbounded\s+by\s+(\w+)", re.IGNORECASE), GuardKind.SENTINEL_VALUE),
    (re.compile(r"\bthreshold\s+(\w+)", re.IGNORECASE), GuardKind.SENTINEL_VALUE),
]

# Type change patterns
_TYPE_CHANGE_PATTERNS = [
    # "replace boolean/bool X [qualifier...] with integer/int ..."
    # Captures multi-word name between bool and with (e.g. "replay guard")
    (re.compile(r"\breplace\s+(?:a\s+)?bool(?:ean)?\s+([\w\s]+?)\s+with\s+(?:an?\s+)?int(?:eger)?", re.IGNORECASE),
     TypeTransitionKind.BOOL_TO_INT),
    # "change X from bool to int"
    (re.compile(r"\b([\w]+)\s+from\s+bool(?:ean)?\s+to\s+int(?:eger)?", re.IGNORECASE),
     TypeTransitionKind.BOOL_TO_INT),
    # "bool->int" or "boolean->integer"
    (re.compile(r"\b(\w+)\b.*\bbool(?:ean)?\s*(?:->|→|to)\s*int(?:eger)?", re.IGNORECASE),
     TypeTransitionKind.BOOL_TO_INT),
    # "replace boolean/bool X [qualifier...] with [N-state] enum ..."
    (re.compile(r"\breplace\s+(?:a\s+)?bool(?:ean)?\s+([\w\s]+?)\s+with\s+(?:an?\s+)?(?:\d+-state\s+)?enum", re.IGNORECASE),
     TypeTransitionKind.BOOL_TO_ENUM),
    # "bool->enum" / "bool to 3-state enum"
    (re.compile(r"\b(\w+)\b.*\bbool(?:ean)?\s*(?:->|→|to)\s*(?:\d+-state\s+)?enum", re.IGNORECASE),
     TypeTransitionKind.BOOL_TO_ENUM),
    # "replace enum X with string"
    (re.compile(r"\breplace\s+(?:an?\s+)?enum\s+(\w+)\s+with\s+(?:a\s+)?string", re.IGNORECASE),
     TypeTransitionKind.ENUM_TO_STRING),
]

# Suppression annotation
_SUPPRESSION_RE = re.compile(
    r"@no-ambiguity-check\s*(?:\(\s*(.+?)\s*\))?",
    re.IGNORECASE,
)

# Known archetype patterns for seeding (R-010)
_KNOWN_ARCHETYPES: dict[str, list[GuardState]] = {
    "replay": [
        GuardState(
            value="0",
            semantic_meanings=[
                SemanticMeaning("0", "no events to replay"),
                SemanticMeaning("0", "start offset for replay"),
            ],
        ),
        GuardState(value="N>0", semantic_meanings=[
            SemanticMeaning("N>0", "offset into event list"),
        ]),
    ],
    "boolean": [
        GuardState(value="true", semantic_meanings=[
            SemanticMeaning("true", "condition active"),
        ]),
        GuardState(value="false", semantic_meanings=[
            SemanticMeaning("false", "condition inactive"),
        ]),
    ],
}


def detect_guards(
    deliverables: list[Deliverable],
) -> list[GuardDetection]:
    """Scan deliverable descriptions for guard patterns and type changes.

    Returns a list of GuardDetection objects. Each detection includes
    enumerated states, ambiguity flags, and type transition analysis.

    Idempotent: does not modify input deliverables.
    """
    results: list[GuardDetection] = []

    for d in deliverables:
        if not d.description or not d.description.strip():
            continue

        desc = d.description
        desc_lower = desc.lower()

        # Check suppression
        suppressed = False
        suppression_rationale = ""
        supp_match = _SUPPRESSION_RE.search(desc)
        if supp_match:
            suppressed = True
            suppression_rationale = supp_match.group(1) or "no rationale provided"

        # Detect type changes (highest priority)
        seen_transitions: set[TypeTransitionKind] = set()
        for pattern, transition_kind in _TYPE_CHANGE_PATTERNS:
            if transition_kind in seen_transitions:
                continue
            match = pattern.search(desc)
            if match:
                raw_name = match.group(1).strip()
                # Extract first word as variable name from multi-word captures
                var_name = raw_name.split()[0] if raw_name else raw_name
                seen_transitions.add(transition_kind)
                detection = _build_type_change_detection(
                    d.id, var_name, transition_kind, desc_lower,
                    suppressed, suppression_rationale,
                )
                results.append(detection)

        # Detect guard patterns
        seen_vars: set[str] = set()
        for pattern, guard_kind in _GUARD_PATTERNS:
            for match in pattern.finditer(desc):
                var_name = match.group(1)
                if var_name.lower() in {"a", "an", "the", "if", "when", "is", "not"}:
                    continue
                if var_name in seen_vars:
                    continue
                seen_vars.add(var_name)

                detection = _build_guard_detection(
                    d.id, var_name, guard_kind, desc_lower,
                    suppressed, suppression_rationale,
                )
                results.append(detection)

    return results


def _build_type_change_detection(
    deliverable_id: str,
    var_name: str,
    transition_kind: TypeTransitionKind,
    desc_lower: str,
    suppressed: bool,
    suppression_rationale: str,
) -> GuardDetection:
    """Build a GuardDetection for a type change."""
    states = _enumerate_type_change_states(var_name, transition_kind, desc_lower)
    ambiguity = any(s.is_ambiguous for s in states)

    return GuardDetection(
        deliverable_id=deliverable_id,
        guard_variable=var_name,
        guard_kind=GuardKind.TYPE_CHANGE,
        states=states,
        type_transition=transition_kind,
        ambiguity_flagged=ambiguity and not suppressed,
        suppressed=suppressed,
        suppression_rationale=suppression_rationale,
    )


def _build_guard_detection(
    deliverable_id: str,
    var_name: str,
    guard_kind: GuardKind,
    desc_lower: str,
    suppressed: bool,
    suppression_rationale: str,
) -> GuardDetection:
    """Build a GuardDetection for a guard pattern."""
    states = _enumerate_guard_states(var_name, guard_kind, desc_lower)
    ambiguity = any(s.is_ambiguous for s in states)

    return GuardDetection(
        deliverable_id=deliverable_id,
        guard_variable=var_name,
        guard_kind=guard_kind,
        states=states,
        type_transition=None,
        ambiguity_flagged=ambiguity and not suppressed,
        suppressed=suppressed,
        suppression_rationale=suppression_rationale,
    )


def _enumerate_type_change_states(
    var_name: str,
    transition_kind: TypeTransitionKind,
    desc_lower: str,
) -> list[GuardState]:
    """Enumerate states for type change transitions."""
    if transition_kind == TypeTransitionKind.BOOL_TO_INT:
        # Bool->int always has ambiguity for 0: means both "false" and "zero offset"
        # Check for archetype match (replay pattern)
        if _matches_archetype(desc_lower, "replay"):
            return list(_KNOWN_ARCHETYPES["replay"])
        return [
            GuardState(
                value="0",
                semantic_meanings=[
                    SemanticMeaning("0", "original false/no state"),
                    SemanticMeaning("0", "zero numeric value"),
                ],
            ),
            GuardState(value="N>0", semantic_meanings=[
                SemanticMeaning("N>0", "positive numeric value"),
            ]),
            GuardState(value="N<0", semantic_meanings=[
                SemanticMeaning("N<0", "negative numeric value (if applicable)"),
            ]),
        ]
    elif transition_kind == TypeTransitionKind.BOOL_TO_ENUM:
        return [
            GuardState(value="state_A", semantic_meanings=[
                SemanticMeaning("state_A", "first enum state (maps to old true)"),
            ]),
            GuardState(value="state_B", semantic_meanings=[
                SemanticMeaning("state_B", "second enum state (maps to old false)"),
            ]),
            GuardState(value="state_C", semantic_meanings=[
                SemanticMeaning("state_C", "new third state"),
            ]),
        ]
    elif transition_kind == TypeTransitionKind.ENUM_TO_STRING:
        return [
            GuardState(value="valid_string", semantic_meanings=[
                SemanticMeaning("valid_string", "matches expected enum name"),
            ]),
            GuardState(value="empty_string", semantic_meanings=[
                SemanticMeaning("empty_string", "empty/missing value"),
            ]),
            GuardState(value="unknown_string", semantic_meanings=[
                SemanticMeaning("unknown_string", "unrecognized value"),
            ]),
        ]
    return []


def _enumerate_guard_states(
    var_name: str,
    guard_kind: GuardKind,
    desc_lower: str,
) -> list[GuardState]:
    """Enumerate states for guard patterns based on kind."""
    if guard_kind == GuardKind.FLAG_CHECK:
        # Boolean flags: true/false
        if _matches_archetype(desc_lower, "boolean"):
            return list(_KNOWN_ARCHETYPES["boolean"])
        return [
            GuardState(value="true", semantic_meanings=[
                SemanticMeaning("true", f"{var_name} active"),
            ]),
            GuardState(value="false", semantic_meanings=[
                SemanticMeaning("false", f"{var_name} inactive"),
            ]),
        ]
    elif guard_kind == GuardKind.SENTINEL_VALUE:
        # Sentinel: has a special value + normal range
        return [
            GuardState(
                value="sentinel",
                semantic_meanings=[
                    SemanticMeaning("sentinel", "special/boundary marker"),
                ],
            ),
            GuardState(
                value="normal",
                semantic_meanings=[
                    SemanticMeaning("normal", "within expected range"),
                ],
            ),
        ]
    elif guard_kind in (GuardKind.IF_ELSE, GuardKind.EARLY_RETURN):
        return [
            GuardState(value="truthy", semantic_meanings=[
                SemanticMeaning("truthy", f"condition on {var_name} met"),
            ]),
            GuardState(value="falsy", semantic_meanings=[
                SemanticMeaning("falsy", f"condition on {var_name} not met"),
            ]),
        ]
    return []


def _matches_archetype(desc_lower: str, archetype_key: str) -> bool:
    """Check if description matches a known archetype."""
    archetype_keywords = {
        "replay": ["replay", "replayed", "event_offset", "tail_events"],
        "boolean": ["boolean", "bool", "true/false", "is_"],
    }
    keywords = archetype_keywords.get(archetype_key, [])
    return any(kw in desc_lower for kw in keywords)
