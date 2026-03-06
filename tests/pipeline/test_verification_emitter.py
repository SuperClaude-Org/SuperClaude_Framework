"""Tests for verification deliverable emitter.

Covers T02.04 acceptance criteria:
- 3 mutation sites -> 3 invariant_check deliverables
- Each references correct predicate
- Edge cases include zero/empty/boundary
- Deliverables inserted into correct milestone
- Release Gate Rule 3: each verify deliverable contains state assertion
- Cap at 5 per variable (R-005)
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.invariants import InvariantEntry, MutationSite
from superclaude.cli.pipeline.models import DeliverableKind
from superclaude.cli.pipeline.mutation_inventory import MutationInventoryResult
from superclaude.cli.pipeline.verification_emitter import (
    emit_invariant_check_deliverables,
)


def _inv(var: str, scope: str, pred: str, sites: list[MutationSite]) -> tuple[InvariantEntry, MutationInventoryResult]:
    entry = InvariantEntry(
        variable_name=var, scope=scope, invariant_predicate=pred,
        mutation_sites=sites,
    )
    result = MutationInventoryResult(
        variable_name=var, mutation_sites=sites, ambiguous_sites=[],
    )
    return entry, result


class TestVerificationEmitter:
    """Four-scenario test suite per tasklist spec."""

    def test_three_sites_three_deliverables(self):
        """3 mutation sites -> 3 invariant_check deliverables."""
        sites = [
            MutationSite("D2.3", "introduced as offset", "birth"),
            MutationSite("D3.1", "increment offset", "loop"),
            MutationSite("D4.2", "reset offset", "completion"),
        ]
        entry, inv_result = _inv("offset", "Manager", "offset >= 0", sites)

        deliverables = emit_invariant_check_deliverables([inv_result], [entry])
        assert len(deliverables) == 3
        assert all(d.kind == DeliverableKind.INVARIANT_CHECK for d in deliverables)

    def test_each_references_correct_predicate(self):
        """Each deliverable references the invariant predicate."""
        sites = [MutationSite("D1.1", "birth", "init")]
        entry, inv_result = _inv("counter", "Tracker", "counter >= 0", sites)

        deliverables = emit_invariant_check_deliverables([inv_result], [entry])
        assert len(deliverables) == 1
        assert "counter >= 0" in deliverables[0].description
        assert deliverables[0].metadata["invariant_predicate"] == "counter >= 0"

    def test_edge_cases_included(self):
        """Edge cases include zero/empty/boundary."""
        sites = [MutationSite("D1.0", "birth", "init")]
        entry, inv_result = _inv("x", "Mod", "x >= 0", sites)

        deliverables = emit_invariant_check_deliverables([inv_result], [entry])
        desc = deliverables[0].description
        assert "zero" in desc.lower()
        assert "empty" in desc.lower()
        assert "boundary" in desc.lower()

    def test_correct_milestone_placement(self):
        """Deliverables use correct milestone in ID."""
        sites = [
            MutationSite("D2.3", "birth", "init"),
            MutationSite("D4.1", "update x", "loop"),
        ]
        entry, inv_result = _inv("x", "Mod", "x >= 0", sites)

        deliverables = emit_invariant_check_deliverables([inv_result], [entry])
        ids = [d.id for d in deliverables]
        assert ids[0].startswith("D2.")  # milestone 2
        assert ids[1].startswith("D4.")  # milestone 4

    def test_state_assertion_present(self):
        """Release Gate Rule 3: each verify deliverable contains state assertion."""
        sites = [MutationSite("D1.0", "birth", "init")]
        entry, inv_result = _inv("y", "Mod", "y >= 0", sites)

        deliverables = emit_invariant_check_deliverables([inv_result], [entry])
        for d in deliverables:
            assert "assert" in d.description.lower()

    def test_cap_at_five(self):
        """R-005: cap at 5 invariant_check deliverables per variable."""
        sites = [MutationSite(f"D{i}.0", f"mutation {i}", f"ctx {i}") for i in range(8)]
        entry, inv_result = _inv("z", "Mod", "z >= 0", sites)

        deliverables = emit_invariant_check_deliverables([inv_result], [entry], max_checks_per_variable=5)
        assert len(deliverables) == 5

    def test_configurable_cap(self):
        """Cap is configurable via max_checks_per_variable."""
        sites = [MutationSite(f"D{i}.0", f"mutation {i}", f"ctx {i}") for i in range(10)]
        entry, inv_result = _inv("w", "Mod", "w >= 0", sites)

        deliverables = emit_invariant_check_deliverables([inv_result], [entry], max_checks_per_variable=3)
        assert len(deliverables) == 3


class TestEdgeCases:

    def test_empty_inventory(self):
        deliverables = emit_invariant_check_deliverables([], [])
        assert deliverables == []

    def test_no_matching_entry(self):
        """Inventory result without matching InvariantEntry produces no deliverables."""
        sites = [MutationSite("D1.0", "birth", "init")]
        inv_result = MutationInventoryResult("unknown_var", sites, [])
        deliverables = emit_invariant_check_deliverables([inv_result], [])
        assert deliverables == []
