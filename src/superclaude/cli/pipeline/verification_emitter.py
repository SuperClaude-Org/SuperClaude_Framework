"""Verification deliverable emitter -- generates invariant_check deliverables.

For each mutation site, emits a kind=invariant_check deliverable with:
- Variable name and invariant predicate
- Specific mutation being verified
- Edge cases (zero, empty, boundary)
- ID following D{milestone}.{seq}.inv pattern

R-005 mitigation: cap at 5 invariant_check deliverables per variable.

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .invariants import InvariantEntry, MutationSite
from .models import Deliverable, DeliverableKind
from .mutation_inventory import MutationInventoryResult


# Default edge cases for invariant checks
DEFAULT_EDGE_CASES = [
    "zero value",
    "empty collection",
    "boundary minimum",
    "negative value",
    "maximum boundary",
]

# Maximum invariant_check deliverables per variable (R-005)
DEFAULT_MAX_INVARIANT_CHECKS = 5


def emit_invariant_check_deliverables(
    inventory_results: list[MutationInventoryResult],
    invariant_entries: list[InvariantEntry],
    max_checks_per_variable: int = DEFAULT_MAX_INVARIANT_CHECKS,
) -> list[Deliverable]:
    """Generate invariant_check deliverables from mutation inventory.

    For each mutation site (up to max_checks_per_variable), emits a
    deliverable with kind=invariant_check containing:
    - The invariant predicate being verified
    - The specific mutation expression
    - Applicable edge cases

    Returns list of generated Deliverable objects.
    """
    generated: list[Deliverable] = []

    # Build lookup from variable_name -> InvariantEntry
    entry_lookup: dict[str, InvariantEntry] = {}
    for entry in invariant_entries:
        entry_lookup[entry.variable_name] = entry

    for inv_result in inventory_results:
        entry = entry_lookup.get(inv_result.variable_name)
        if entry is None:
            continue

        # Cap at max_checks_per_variable
        sites_to_check = inv_result.mutation_sites[:max_checks_per_variable]

        for idx, site in enumerate(sites_to_check):
            # Extract milestone from deliverable_id (e.g. "D2.3" -> "2")
            milestone = _extract_milestone(site.deliverable_id)
            seq = idx + 1

            deliverable_id = f"D{milestone}.{seq}.inv"

            # Build description with predicate, mutation reference, and edge cases
            edge_cases_str = ", ".join(DEFAULT_EDGE_CASES[:3])
            description = (
                f"Invariant check: verify '{entry.invariant_predicate}' "
                f"holds after {site.expression} in {site.deliverable_id}. "
                f"Edge cases: {edge_cases_str}. "
                f"State assertion: assert {entry.invariant_predicate}"
            )

            d = Deliverable(
                id=deliverable_id,
                description=description,
                kind=DeliverableKind.INVARIANT_CHECK,
                metadata={
                    "variable_name": entry.variable_name,
                    "scope": entry.scope,
                    "invariant_predicate": entry.invariant_predicate,
                    "mutation_deliverable_id": site.deliverable_id,
                    "mutation_expression": site.expression,
                    "edge_cases": DEFAULT_EDGE_CASES[:3],
                },
            )
            generated.append(d)

        # Update InvariantEntry with generated verification IDs
        entry.verification_deliverable_ids = [d.id for d in generated if
            d.metadata.get("variable_name") == entry.variable_name]

    return generated


def _extract_milestone(deliverable_id: str) -> str:
    """Extract milestone number from deliverable ID.

    Examples:
        "D2.3"   -> "2"
        "D-0015" -> "0015"
        "D4.2"   -> "4"
    """
    # Try D{number}.{seq} format first
    m = re.match(r"D(\d+)\.", deliverable_id)
    if m:
        return m.group(1)

    # Try D-{number} format
    m = re.match(r"D-(\d+)", deliverable_id)
    if m:
        return m.group(1)

    # Fallback: use the ID as-is
    return deliverable_id.lstrip("D-")
