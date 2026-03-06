"""Conflict detector -- identifies writer/reader semantic divergence in implicit contracts.

Conflict categories:
1. Direct contradiction: writer and reader state opposite things
2. Scope mismatch: filtered subset vs full set
3. Type mismatch: boolean vs integer, etc.
4. Completeness mismatch: partial vs complete

Cross-references M2 invariant predicates and failure mode tables.
Extensible synonym dictionary (R-014 mitigation).

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from .contract_extractor import UNSPECIFIED, ImplicitContract
from .invariants import InvariantEntry


class ConflictKind(Enum):
    """Classification of conflict type."""
    DIRECT_CONTRADICTION = "direct_contradiction"
    SCOPE_MISMATCH = "scope_mismatch"
    TYPE_MISMATCH = "type_mismatch"
    COMPLETENESS_MISMATCH = "completeness_mismatch"
    UNSPECIFIED_WRITER = "unspecified_writer"


@dataclass
class ConflictDetection:
    """A detected conflict between writer semantics and reader assumptions.

    Attributes:
        contract: The ImplicitContract containing the conflict.
        kind: Classification of the conflict.
        description: Human-readable description of the divergence.
        suggested_resolution: Recommended action to resolve.
        severity: "high" | "medium" | "low" based on conflict kind.
    """
    contract: ImplicitContract
    kind: ConflictKind
    description: str
    suggested_resolution: str
    severity: str = "medium"


# ---------------------------------------------------------------------------
# Extensible synonym dictionary (R-014 mitigation)
# ---------------------------------------------------------------------------

SYNONYM_GROUPS: list[set[str]] = [
    {"total", "count", "number", "quantity", "sum", "amount"},
    {"all", "every", "complete", "full", "entire", "whole"},
    {"filtered", "subset", "partial", "selected", "matching", "qualifying"},
    {"processed", "handled", "completed", "finished", "consumed", "delivered"},
    {"offset", "position", "index", "cursor", "pointer", "location"},
    {"flag", "boolean", "bool", "toggle", "switch", "indicator"},
    {"integer", "int", "number", "numeric", "count"},
    {"string", "str", "text", "name", "label"},
    {"active", "enabled", "on", "true", "running"},
    {"inactive", "disabled", "off", "false", "stopped"},
]

# Build lookup: word -> union of all groups containing that word
_SYNONYM_LOOKUP: dict[str, set[str]] = {}
for group in SYNONYM_GROUPS:
    for word in group:
        if word in _SYNONYM_LOOKUP:
            _SYNONYM_LOOKUP[word] = _SYNONYM_LOOKUP[word] | group
        else:
            _SYNONYM_LOOKUP[word] = set(group)


def are_synonyms(word1: str, word2: str) -> bool:
    """Check if two words are synonyms according to the dictionary."""
    w1 = word1.lower().strip()
    w2 = word2.lower().strip()
    if w1 == w2:
        return True
    group = _SYNONYM_LOOKUP.get(w1, set())
    return w2 in group


# ---------------------------------------------------------------------------
# Scope indicators
# ---------------------------------------------------------------------------

_SCOPE_ALL = {"all", "every", "complete", "full", "entire", "total", "whole"}
_SCOPE_FILTERED = {"filtered", "subset", "partial", "selected", "matching", "some", "qualifying"}

# Type indicators
_TYPE_BOOLEAN = {"boolean", "bool", "flag", "true", "false", "toggle"}
_TYPE_INTEGER = {"integer", "int", "number", "count", "numeric", "counter"}
_TYPE_STRING = {"string", "str", "text", "name"}
_TYPE_GROUPS = [_TYPE_BOOLEAN, _TYPE_INTEGER, _TYPE_STRING]

# Contradiction indicators
_POSITIVE_INDICATORS = {"delivered", "processed", "completed", "sent", "written", "all", "total"}
_NEGATIVE_INDICATORS = {"undelivered", "unprocessed", "pending", "remaining", "failed", "none"}


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase words."""
    return set(re.findall(r"\b\w+\b", text.lower()))


def _detect_scope_mismatch(writer_tokens: set[str], reader_tokens: set[str]) -> bool:
    """Detect scope mismatch: one side says 'all/total', other says 'filtered/subset'."""
    writer_has_all = bool(writer_tokens & _SCOPE_ALL)
    writer_has_filtered = bool(writer_tokens & _SCOPE_FILTERED)
    reader_has_all = bool(reader_tokens & _SCOPE_ALL)
    reader_has_filtered = bool(reader_tokens & _SCOPE_FILTERED)

    return (writer_has_all and reader_has_filtered) or (writer_has_filtered and reader_has_all)


def _detect_type_mismatch(writer_tokens: set[str], reader_tokens: set[str]) -> bool:
    """Detect type mismatch: writer implies one type, reader implies another."""
    for i, group_a in enumerate(_TYPE_GROUPS):
        for group_b in _TYPE_GROUPS[i + 1:]:
            writer_in_a = bool(writer_tokens & group_a)
            reader_in_b = bool(reader_tokens & group_b)
            writer_in_b = bool(writer_tokens & group_b)
            reader_in_a = bool(reader_tokens & group_a)
            if (writer_in_a and reader_in_b) or (writer_in_b and reader_in_a):
                return True
    return False


def _detect_direct_contradiction(writer_tokens: set[str], reader_tokens: set[str]) -> bool:
    """Detect direct contradiction: writer says positive, reader says negative or vice versa."""
    writer_pos = bool(writer_tokens & _POSITIVE_INDICATORS)
    writer_neg = bool(writer_tokens & _NEGATIVE_INDICATORS)
    reader_pos = bool(reader_tokens & _POSITIVE_INDICATORS)
    reader_neg = bool(reader_tokens & _NEGATIVE_INDICATORS)

    return (writer_pos and reader_neg) or (writer_neg and reader_pos)


def _detect_completeness_mismatch(
    writer_tokens: set[str],
    reader_tokens: set[str],
    invariant_entry: InvariantEntry | None = None,
) -> bool:
    """Detect completeness mismatch using semantic and invariant cross-reference."""
    # Check for partial vs complete indicators
    completeness_full = {"complete", "all", "total", "full", "entire"}
    completeness_partial = {"partial", "some", "subset", "incremental", "batch"}

    writer_full = bool(writer_tokens & completeness_full)
    writer_partial = bool(writer_tokens & completeness_partial)
    reader_full = bool(reader_tokens & completeness_full)
    reader_partial = bool(reader_tokens & completeness_partial)

    if (writer_full and reader_partial) or (writer_partial and reader_full):
        return True

    # Cross-reference with invariant entry for enriched detection
    if invariant_entry:
        pred_tokens = _tokenize(invariant_entry.invariant_predicate)
        if pred_tokens & completeness_full and reader_partial:
            return True

    return False


# ---------------------------------------------------------------------------
# Main detector
# ---------------------------------------------------------------------------

def detect_conflicts(
    contracts: list[ImplicitContract],
    invariant_entries: list[InvariantEntry] | None = None,
    fmea_severity_map: dict[str, str] | None = None,
) -> list[ConflictDetection]:
    """Detect conflicts in implicit contracts.

    Args:
        contracts: List of ImplicitContract from T04.02.
        invariant_entries: M2 invariant entries for cross-reference enrichment.
        fmea_severity_map: M2 FMEA severity map for completeness enrichment.

    Returns:
        List of ConflictDetection objects.
    """
    if invariant_entries is None:
        invariant_entries = []
    if fmea_severity_map is None:
        fmea_severity_map = {}

    # Build invariant lookup
    inv_lookup: dict[str, InvariantEntry] = {}
    for entry in invariant_entries:
        inv_lookup[entry.variable_name] = entry

    conflicts: list[ConflictDetection] = []

    for contract in contracts:
        # Rule: UNSPECIFIED writer always conflicts (cannot verify compatibility)
        if contract.writer_semantics == UNSPECIFIED:
            conflicts.append(ConflictDetection(
                contract=contract,
                kind=ConflictKind.UNSPECIFIED_WRITER,
                description=(
                    f"Writer semantics for '{contract.variable}' are UNSPECIFIED "
                    f"in {contract.writer_deliverable}. Cannot verify compatibility "
                    f"with reader {contract.reader_deliverable}."
                ),
                suggested_resolution=(
                    f"Add explicit semantic declaration for '{contract.variable}' "
                    f"in deliverable {contract.writer_deliverable}."
                ),
                severity="high",
            ))
            continue

        # Skip if reader is also unspecified (already flagged via needs_human_review)
        if contract.reader_assumption == UNSPECIFIED:
            conflicts.append(ConflictDetection(
                contract=contract,
                kind=ConflictKind.UNSPECIFIED_WRITER,
                description=(
                    f"Reader assumption for '{contract.variable}' is UNSPECIFIED "
                    f"in {contract.reader_deliverable}."
                ),
                suggested_resolution=(
                    f"Add explicit assumption for '{contract.variable}' "
                    f"in deliverable {contract.reader_deliverable}."
                ),
                severity="high",
            ))
            continue

        writer_tokens = _tokenize(contract.writer_semantics)
        reader_tokens = _tokenize(contract.reader_assumption)
        inv_entry = inv_lookup.get(contract.variable)

        # Check each conflict type (in order of severity)
        if _detect_direct_contradiction(writer_tokens, reader_tokens):
            conflicts.append(ConflictDetection(
                contract=contract,
                kind=ConflictKind.DIRECT_CONTRADICTION,
                description=(
                    f"Direct contradiction for '{contract.variable}': "
                    f"writer says '{contract.writer_semantics}', "
                    f"reader assumes '{contract.reader_assumption}'."
                ),
                suggested_resolution=(
                    f"Align writer and reader on the semantic meaning of "
                    f"'{contract.variable}' across milestones."
                ),
                severity="high",
            ))
        elif _detect_scope_mismatch(writer_tokens, reader_tokens):
            conflicts.append(ConflictDetection(
                contract=contract,
                kind=ConflictKind.SCOPE_MISMATCH,
                description=(
                    f"Scope mismatch for '{contract.variable}': "
                    f"writer says '{contract.writer_semantics}', "
                    f"reader assumes '{contract.reader_assumption}'."
                ),
                suggested_resolution=(
                    f"Clarify whether '{contract.variable}' represents a "
                    f"filtered subset or the complete set."
                ),
                severity="high",
            ))
        elif _detect_type_mismatch(writer_tokens, reader_tokens):
            conflicts.append(ConflictDetection(
                contract=contract,
                kind=ConflictKind.TYPE_MISMATCH,
                description=(
                    f"Type mismatch for '{contract.variable}': "
                    f"writer implies '{contract.writer_semantics}', "
                    f"reader assumes '{contract.reader_assumption}'."
                ),
                suggested_resolution=(
                    f"Standardize the type of '{contract.variable}' "
                    f"across writer and reader deliverables."
                ),
                severity="medium",
            ))
        elif _detect_completeness_mismatch(writer_tokens, reader_tokens, inv_entry):
            conflicts.append(ConflictDetection(
                contract=contract,
                kind=ConflictKind.COMPLETENESS_MISMATCH,
                description=(
                    f"Completeness mismatch for '{contract.variable}': "
                    f"writer says '{contract.writer_semantics}', "
                    f"reader assumes '{contract.reader_assumption}'."
                ),
                suggested_resolution=(
                    f"Verify whether '{contract.variable}' represents complete "
                    f"or partial data across milestones."
                ),
                severity="medium",
            ))
        # No conflict detected for identical or compatible semantics

    return conflicts
