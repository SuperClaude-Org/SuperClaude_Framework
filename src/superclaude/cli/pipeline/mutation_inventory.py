"""Mutation inventory -- enumerates all write paths per detected state variable.

For each detected state variable, scans ALL deliverable descriptions (not just
the introducing deliverable) for mutation indicators: update, increment, reset,
set-to, advance-by, clear.

Ambiguous mutations are flagged rather than silently dropped (R-004 mitigation).

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .invariants import MutationSite
from .models import Deliverable
from .state_detector import DetectionResult


# Mutation indicator patterns: verb + variable_name reference
_MUTATION_INDICATORS = [
    (re.compile(r"\bupdate\s+(\w+)", re.IGNORECASE), "update"),
    (re.compile(r"\bincrement\s+(\w+)", re.IGNORECASE), "increment"),
    (re.compile(r"\breset\s+(\w+)", re.IGNORECASE), "reset"),
    (re.compile(r"\bset\s+(\w+)\s+to\b", re.IGNORECASE), "set_to"),
    (re.compile(r"\badvance\s+(\w+)\s+by\b", re.IGNORECASE), "advance_by"),
    (re.compile(r"\bclear\s+(\w+)", re.IGNORECASE), "clear"),
    (re.compile(r"\bmodify\s+(\w+)", re.IGNORECASE), "modify"),
    (re.compile(r"\bassign\s+(\w+)", re.IGNORECASE), "assign"),
    (re.compile(r"\b(\w+)\s*(?:\+=|-=|\*=|/=|=)", re.IGNORECASE), "assignment_op"),
]

# Ambiguous mutation patterns (flagged for review)
_AMBIGUOUS_PATTERNS = [
    re.compile(r"\bchange\s+(\w+)", re.IGNORECASE),
    re.compile(r"\badjust\s+(\w+)", re.IGNORECASE),
    re.compile(r"\btweak\s+(\w+)", re.IGNORECASE),
]


@dataclass
class MutationInventoryResult:
    """Result of mutation inventory for a single variable."""
    variable_name: str
    mutation_sites: list[MutationSite]
    ambiguous_sites: list[MutationSite]

    @property
    def total_sites(self) -> int:
        return len(self.mutation_sites) + len(self.ambiguous_sites)


def generate_mutation_inventory(
    detections: list[DetectionResult],
    all_deliverables: list[Deliverable],
) -> list[MutationInventoryResult]:
    """For each detected state variable, enumerate all mutation sites.

    Scans ALL deliverable descriptions (cross-referencing the full roadmap),
    not just the introducing deliverable.

    Returns one MutationInventoryResult per detected variable.
    """
    results: list[MutationInventoryResult] = []

    for detection in detections:
        var_name = detection.variable_name
        mutation_sites: list[MutationSite] = []
        ambiguous_sites: list[MutationSite] = []
        seen_deliverables: set[str] = set()

        # Always include the birth site
        mutation_sites.append(MutationSite(
            deliverable_id=detection.deliverable_id,
            expression=f"introduced as {detection.introduction_type.value}",
            context="birth site",
        ))
        seen_deliverables.add(detection.deliverable_id)

        # Scan all deliverables for mutations
        for d in all_deliverables:
            if not d.description or not d.description.strip():
                continue

            desc_lower = d.description.lower()

            # Check for variable name reference in description
            if not _references_variable(desc_lower, var_name):
                continue

            # Check definite mutation indicators
            for pattern, indicator_name in _MUTATION_INDICATORS:
                for match in pattern.finditer(d.description):
                    target = match.group(1).lower()
                    if _is_variable_match(target, var_name):
                        key = (d.id, indicator_name)
                        if d.id not in seen_deliverables:
                            mutation_sites.append(MutationSite(
                                deliverable_id=d.id,
                                expression=f"{indicator_name} {var_name}",
                                context=d.description[:100],
                            ))
                            seen_deliverables.add(d.id)

            # Check ambiguous patterns
            for pattern in _AMBIGUOUS_PATTERNS:
                for match in pattern.finditer(d.description):
                    target = match.group(1).lower()
                    if _is_variable_match(target, var_name):
                        if d.id not in seen_deliverables:
                            ambiguous_sites.append(MutationSite(
                                deliverable_id=d.id,
                                expression=f"ambiguous mutation of {var_name}",
                                context=d.description[:100],
                            ))
                            seen_deliverables.add(d.id)

        results.append(MutationInventoryResult(
            variable_name=var_name,
            mutation_sites=mutation_sites,
            ambiguous_sites=ambiguous_sites,
        ))

    return results


def _references_variable(desc_lower: str, var_name: str) -> bool:
    """Check if a description references a variable name."""
    var_lower = var_name.lower().lstrip("_")
    # Direct name match or partial match after stripping underscores
    return var_lower in desc_lower or var_name.lower() in desc_lower


def _is_variable_match(target: str, var_name: str) -> bool:
    """Check if a regex-captured target matches the variable name."""
    var_lower = var_name.lower().lstrip("_")
    target_lower = target.lower().lstrip("_")
    return target_lower == var_lower or target_lower == var_name.lower()
