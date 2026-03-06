"""Invariant registry -- state variable tracking and constrained predicate validation.

Provides:
- MutationSite: location + expression for a single write to a state variable
- InvariantEntry: registry row binding variable name, scope, constrained predicate,
  mutation sites, and verification deliverable cross-references
- validate_predicate(): constrained grammar checker rejecting free-form text

Constrained grammar:
    predicate := clause (('AND'|'OR') clause)*
    clause    := variable_name comparison_op expression
    comparison_op := '==' | '!=' | '<' | '<=' | '>' | '>=' | 'is' | 'is not' | 'in' | 'not in'
    variable_name := identifier (may contain dots, brackets)
    expression := any token sequence that is NOT a comparison_op or logic_op

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import json
import re
import warnings
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Constrained grammar for invariant predicates
# ---------------------------------------------------------------------------

_COMPARISON_OPS = frozenset({
    "==", "!=", "<", "<=", ">", ">=", "is", "is not", "in", "not in",
})

# Regex matching: identifier comparison_op expression
# We tokenize by splitting on AND/OR logic operators first, then validate each clause.
_LOGIC_SPLIT_RE = re.compile(r"\s+(AND|OR)\s+", re.IGNORECASE)

# A clause must contain a comparison operator surrounded by non-empty LHS and RHS.
_CLAUSE_RE = re.compile(
    r"^(.+?)\s+(==|!=|<=|>=|<|>|is\s+not|is|not\s+in|in)\s+(.+)$",
    re.IGNORECASE,
)


def validate_predicate(predicate: str) -> tuple[bool, str | None]:
    """Validate a predicate string against the constrained grammar.

    Returns (True, None) if valid.
    Returns (False, reason) if invalid.
    """
    if not predicate or not predicate.strip():
        return False, "Predicate is empty"

    text = predicate.strip()

    # Split into clauses on AND/OR
    clauses = _LOGIC_SPLIT_RE.split(text)

    # After splitting on AND/OR, we get alternating: clause, operator, clause, ...
    # Filter out the logic operators to get just clauses
    clause_texts = [clauses[i] for i in range(0, len(clauses), 2)]
    logic_ops = [clauses[i] for i in range(1, len(clauses), 2)]

    if not clause_texts:
        return False, "No clauses found in predicate"

    for i, clause in enumerate(clause_texts):
        clause = clause.strip()
        if not clause:
            return False, f"Empty clause at position {i}"

        m = _CLAUSE_RE.match(clause)
        if not m:
            return False, (
                f"Clause does not match constrained grammar "
                f"'variable_name comparison_op expression': {clause!r}"
            )

        lhs, op, rhs = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        if not lhs:
            return False, f"Empty variable_name in clause: {clause!r}"
        if not rhs:
            return False, f"Empty expression in clause: {clause!r}"

    return True, None


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MutationSite:
    """A single write path for a state variable.

    Attributes:
        deliverable_id: ID of the deliverable containing this mutation.
        expression: The mutation expression text (e.g. "increment offset by step_size").
        context: Surrounding context or description of why the mutation happens.
    """

    deliverable_id: str
    expression: str
    context: str = ""

    def to_dict(self) -> dict:
        return {
            "deliverable_id": self.deliverable_id,
            "expression": self.expression,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MutationSite:
        return cls(
            deliverable_id=data["deliverable_id"],
            expression=data["expression"],
            context=data.get("context", ""),
        )


@dataclass
class InvariantEntry:
    """Registry row for a tracked state variable.

    Attributes:
        variable_name: Name of the state variable (e.g. "_loaded_start_index").
        scope: Scope where the variable lives (e.g. "EventReplayManager", "module-level").
        invariant_predicate: Constrained grammar predicate. Validated on construction.
        mutation_sites: List of MutationSite describing all known write paths.
        verification_deliverable_ids: Cross-milestone deliverable IDs that verify this invariant.
    """

    variable_name: str
    scope: str
    invariant_predicate: str
    mutation_sites: list[MutationSite] = field(default_factory=list)
    verification_deliverable_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the invariant predicate against constrained grammar."""
        ok, reason = validate_predicate(self.invariant_predicate)
        if not ok:
            raise ValueError(
                f"Invalid invariant_predicate for '{self.variable_name}': {reason}. "
                f"Expected format: 'variable_name comparison_op expression [AND|OR ...]'"
            )

    def to_dict(self) -> dict:
        return {
            "variable_name": self.variable_name,
            "scope": self.scope,
            "invariant_predicate": self.invariant_predicate,
            "mutation_sites": [ms.to_dict() for ms in self.mutation_sites],
            "verification_deliverable_ids": list(self.verification_deliverable_ids),
        }

    @classmethod
    def from_dict(cls, data: dict) -> InvariantEntry:
        return cls(
            variable_name=data["variable_name"],
            scope=data["scope"],
            invariant_predicate=data["invariant_predicate"],
            mutation_sites=[
                MutationSite.from_dict(ms) for ms in data.get("mutation_sites", [])
            ],
            verification_deliverable_ids=data.get("verification_deliverable_ids", []),
        )


def check_duplicate_variables(
    entries: list[InvariantEntry],
) -> list[str]:
    """Check for duplicate variable_name within the same scope.

    Returns list of warning messages. Duplicates produce warnings, not errors,
    to allow cross-milestone tracking.
    """
    seen: dict[tuple[str, str], int] = {}
    warning_messages: list[str] = []

    for entry in entries:
        key = (entry.variable_name, entry.scope)
        if key in seen:
            msg = (
                f"Duplicate variable_name '{entry.variable_name}' in scope "
                f"'{entry.scope}' (occurrence #{seen[key] + 1})"
            )
            warnings.warn(msg, stacklevel=2)
            warning_messages.append(msg)
            seen[key] += 1
        else:
            seen[key] = 1

    return warning_messages
