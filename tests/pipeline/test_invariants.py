"""Tests for InvariantEntry data structure and constrained grammar predicates.

Covers T02.01 acceptance criteria:
- Constrained grammar acceptance/rejection
- Serialization round-trip
- Duplicate variable_name warning
- Empty mutation_sites valid
- Cross-milestone verification_deliverable_ids
"""

from __future__ import annotations

import json
import warnings

import pytest

from superclaude.cli.pipeline.invariants import (
    InvariantEntry,
    MutationSite,
    check_duplicate_variables,
    validate_predicate,
)


class TestValidatePredicate:
    """Constrained grammar validation."""

    def test_simple_comparison(self):
        ok, reason = validate_predicate("offset >= 0")
        assert ok, reason

    def test_equality(self):
        ok, reason = validate_predicate("counter == initial_value")
        assert ok, reason

    def test_is_not(self):
        ok, reason = validate_predicate("state is not None")
        assert ok, reason

    def test_in_operator(self):
        ok, reason = validate_predicate("status in VALID_STATES")
        assert ok, reason

    def test_not_in_operator(self):
        ok, reason = validate_predicate("key not in blacklist")
        assert ok, reason

    def test_compound_and(self):
        ok, reason = validate_predicate("offset >= 0 AND offset <= max_size")
        assert ok, reason

    def test_compound_or(self):
        ok, reason = validate_predicate("count == 0 OR count > threshold")
        assert ok, reason

    def test_complex_compound(self):
        ok, reason = validate_predicate(
            "_loaded_start_index >= 0 AND _loaded_start_index <= len(events)"
        )
        assert ok, reason

    def test_rejects_empty(self):
        ok, reason = validate_predicate("")
        assert not ok
        assert "empty" in reason.lower()

    def test_rejects_free_form_text(self):
        ok, reason = validate_predicate("the offset should always be positive")
        assert not ok
        assert "constrained grammar" in reason.lower()

    def test_rejects_no_operator(self):
        ok, reason = validate_predicate("offset positive")
        assert not ok

    def test_rejects_whitespace_only(self):
        ok, reason = validate_predicate("   ")
        assert not ok


class TestMutationSite:
    """MutationSite serialization."""

    def test_round_trip(self):
        ms = MutationSite(
            deliverable_id="D-0003",
            expression="increment offset by step_size",
            context="replay loop iteration",
        )
        d = ms.to_dict()
        restored = MutationSite.from_dict(d)
        assert restored.deliverable_id == ms.deliverable_id
        assert restored.expression == ms.expression
        assert restored.context == ms.context

    def test_empty_context_default(self):
        ms = MutationSite.from_dict({
            "deliverable_id": "D-0001",
            "expression": "reset counter",
        })
        assert ms.context == ""


class TestInvariantEntry:
    """InvariantEntry construction, validation, and serialization."""

    def test_valid_construction(self):
        entry = InvariantEntry(
            variable_name="_loaded_start_index",
            scope="EventReplayManager",
            invariant_predicate="_loaded_start_index >= 0",
        )
        assert entry.variable_name == "_loaded_start_index"

    def test_rejects_free_form_predicate(self):
        with pytest.raises(ValueError, match="Invalid invariant_predicate"):
            InvariantEntry(
                variable_name="offset",
                scope="Module",
                invariant_predicate="should always be positive",
            )

    def test_empty_mutation_sites_valid(self):
        entry = InvariantEntry(
            variable_name="counter",
            scope="Tracker",
            invariant_predicate="counter >= 0",
        )
        assert entry.mutation_sites == []

    def test_cross_milestone_verification_ids(self):
        entry = InvariantEntry(
            variable_name="offset",
            scope="Manager",
            invariant_predicate="offset >= 0",
            verification_deliverable_ids=["D-0005", "D-0012", "D-0025"],
        )
        assert len(entry.verification_deliverable_ids) == 3
        assert "D-0025" in entry.verification_deliverable_ids

    def test_serialization_round_trip(self):
        entry = InvariantEntry(
            variable_name="_offset",
            scope="ReplayManager",
            invariant_predicate="_offset >= 0 AND _offset <= max_events",
            mutation_sites=[
                MutationSite("D-0002", "set _offset to len(events)", "init"),
                MutationSite("D-0005", "increment _offset", "replay step"),
            ],
            verification_deliverable_ids=["D-0003.inv", "D-0006.inv"],
        )
        d = entry.to_dict()

        # Verify JSON serializable
        json_str = json.dumps(d)
        restored_dict = json.loads(json_str)

        restored = InvariantEntry.from_dict(restored_dict)
        assert restored.variable_name == entry.variable_name
        assert restored.scope == entry.scope
        assert restored.invariant_predicate == entry.invariant_predicate
        assert len(restored.mutation_sites) == 2
        assert restored.mutation_sites[0].deliverable_id == "D-0002"
        assert restored.mutation_sites[1].expression == "increment _offset"
        assert restored.verification_deliverable_ids == ["D-0003.inv", "D-0006.inv"]


class TestDuplicateVariableWarning:
    """Duplicate variable_name within same scope produces warning."""

    def test_duplicate_warns(self):
        entries = [
            InvariantEntry("offset", "Manager", "offset >= 0"),
            InvariantEntry("offset", "Manager", "offset <= 100"),
        ]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            msgs = check_duplicate_variables(entries)

        assert len(msgs) == 1
        assert "Duplicate" in msgs[0]
        assert len(w) == 1

    def test_different_scopes_no_warning(self):
        entries = [
            InvariantEntry("offset", "Manager", "offset >= 0"),
            InvariantEntry("offset", "Tracker", "offset >= 0"),
        ]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            msgs = check_duplicate_variables(entries)

        assert len(msgs) == 0
        assert len(w) == 0

    def test_no_duplicates_no_warning(self):
        entries = [
            InvariantEntry("offset", "Manager", "offset >= 0"),
            InvariantEntry("counter", "Manager", "counter >= 0"),
        ]
        msgs = check_duplicate_variables(entries)
        assert len(msgs) == 0
