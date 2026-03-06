"""Deliverable analysis -- behavioral detection and decomposition.

Provides:
- is_behavioral(): heuristic classifying deliverable descriptions
- decompose_deliverables(): splits behavioral deliverables into Implement/Verify pairs
"""

from __future__ import annotations

import re

from .models import Deliverable, DeliverableKind

# Computational verbs that signal behavioral deliverables
_COMPUTATIONAL_VERBS = frozenset({
    "compute", "extract", "filter", "count", "calculate", "determine",
    "select", "track", "increment", "update", "replace", "introduce",
    "implement", "retry", "parse", "validate", "transform", "convert",
    "aggregate", "merge", "split", "normalize", "encode", "decode",
    "generate", "emit", "dispatch", "invoke", "execute", "process",
    "build", "construct", "create", "initialize", "register",
})

# State mutation patterns (regex)
_STATE_MUTATION_PATTERNS = [
    r"self\._\w+",          # self._field access
    r"\bcounter\b",         # counter variable
    r"\boffset\b",          # offset variable
    r"\bcursor\b",          # cursor variable
    r"\bmutate\b",          # explicit mutation
    r"\bstate\b",           # state reference
]

# Conditional logic patterns
_CONDITIONAL_PATTERNS = frozenset({
    "guard", "sentinel", "flag", "early return", "bounded",
    "retry", "fallback", "threshold", "limit", "cap",
})

# Documentation verbs that suppress behavioral classification
_DOC_VERBS = frozenset({
    "document", "describe", "explain", "list", "outline",
    "summarize", "catalog", "enumerate", "write", "draft",
    "update readme", "add readme",
})


def is_behavioral(description: str) -> bool:
    """Classify a deliverable description as behavioral or non-behavioral.

    Detection categories:
    1. Computational verbs (compute, extract, filter, etc.)
    2. State mutation patterns (self._*, counter/offset/cursor)
    3. Conditional logic patterns (guard, sentinel, flag, early return)

    Negative signal suppression: doc-specific verbs (document, describe,
    explain, list) suppress false positives on documentation deliverables.

    Returns False for empty descriptions.
    """
    if not description or not description.strip():
        return False

    lower = description.lower()

    # Negative signal suppression: if doc verbs dominate, not behavioral
    doc_signals = sum(1 for v in _DOC_VERBS if v in lower)
    if doc_signals > 0:
        # Check if any strong behavioral signal overrides
        has_strong_behavioral = False
        words = set(re.findall(r'\b\w+\b', lower))
        behavioral_verb_hits = words & _COMPUTATIONAL_VERBS
        # Doc verbs win unless there are more behavioral signals
        if len(behavioral_verb_hits) <= doc_signals:
            return False
        has_strong_behavioral = True

    # Check computational verbs
    words = set(re.findall(r'\b\w+\b', lower))
    if words & _COMPUTATIONAL_VERBS:
        return True

    # Check state mutation patterns
    for pattern in _STATE_MUTATION_PATTERNS:
        if re.search(pattern, lower):
            return True

    # Check conditional logic patterns
    for pattern in _CONDITIONAL_PATTERNS:
        if pattern in lower:
            return True

    return False


def decompose_deliverables(
    deliverables: list[Deliverable],
) -> list[Deliverable]:
    """Expand behavioral deliverables into Implement/Verify pairs.

    For each behavioral deliverable D.x:
    - Emits D.x.a (kind=implement) with original description
    - Emits D.x.b (kind=verify) with verification description referencing D.x.a

    Non-behavioral deliverables pass through unchanged.
    Already-decomposed deliverables (IDs ending in .a or .b) are not re-decomposed.
    Empty input returns empty output.
    """
    if not deliverables:
        return []

    result: list[Deliverable] = []

    for d in deliverables:
        # Idempotency guard: skip already-decomposed deliverables
        if d.id.endswith(".a") or d.id.endswith(".b"):
            result.append(d)
            continue

        if is_behavioral(d.description):
            # Split into Implement + Verify pair
            impl = Deliverable(
                id=f"{d.id}.a",
                description=d.description,
                kind=DeliverableKind.IMPLEMENT,
                metadata=dict(d.metadata),
            )
            verify = Deliverable(
                id=f"{d.id}.b",
                description=(
                    f"Verify {d.id}.a: validate internal correctness of "
                    f"'{d.description}' — input domain boundaries, operand identity, "
                    f"post-condition assertions on internal state"
                ),
                kind=DeliverableKind.VERIFY,
                metadata=dict(d.metadata),
            )
            result.append(impl)
            result.append(verify)
        else:
            # Non-behavioral: pass through unchanged
            result.append(d)

    return result
