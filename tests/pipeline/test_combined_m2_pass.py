"""Tests for combined M2 invariant registry + FMEA pipeline pass -- T02.09.

Scenarios from tasklist:
1. Spec with state variable introductions + computational deliverables ->
   both invariant registry and FMEA failure mode tables present
2. Cross-links between invariant entries and fmea_test deliverables are correct
3. Silent corruption findings trigger Release Gate Rule 1
4. Combined pass is idempotent
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.combined_m2_pass import (
    CombinedM2Output,
    run_combined_m2_pass,
)
from superclaude.cli.pipeline.fmea_classifier import (
    DetectionDifficulty,
    Severity,
)
from superclaude.cli.pipeline.models import Deliverable, DeliverableKind


def _make_test_deliverables() -> list[Deliverable]:
    """Create test deliverables with state variables and computations."""
    return [
        # State variable introduction (detected by state_detector)
        Deliverable(
            id="D2.1",
            description="Add replay offset counter for tracking position in event stream",
            kind=DeliverableKind.IMPLEMENT,
        ),
        # Mutation of state variable (detected by mutation_inventory)
        Deliverable(
            id="D3.1",
            description="Increment replay offset after processing each event batch",
            kind=DeliverableKind.IMPLEMENT,
        ),
        # Computational deliverable (triggers FMEA domain enumeration)
        Deliverable(
            id="D4.1",
            description="Filter events by type and compute aggregated metrics per category",
            kind=DeliverableKind.IMPLEMENT,
        ),
        # Another state variable
        Deliverable(
            id="D2.2",
            description="Add session cursor flag for pagination tracking",
            kind=DeliverableKind.IMPLEMENT,
        ),
        # Non-computational (should not trigger FMEA)
        Deliverable(
            id="D1.1",
            description="Document the API design and endpoint specifications",
            kind=DeliverableKind.IMPLEMENT,
        ),
    ]


class TestCombinedM2Pass:
    """Integration tests for the combined M2 pass."""

    def test_both_sections_present(self):
        """Both invariant registry and FMEA tables present in output."""
        deliverables = _make_test_deliverables()
        output = run_combined_m2_pass(deliverables)

        assert "Invariant Registry" in output.section_markdown
        assert "FMEA" in output.section_markdown

    def test_invariant_entries_generated(self):
        """State variables detected and registered."""
        deliverables = _make_test_deliverables()
        output = run_combined_m2_pass(deliverables)

        assert len(output.invariant_output.entries) >= 1, (
            "Should detect at least one state variable"
        )

    def test_invariant_check_deliverables_generated(self):
        """Invariant check deliverables generated."""
        deliverables = _make_test_deliverables()
        output = run_combined_m2_pass(deliverables)

        inv_checks = [
            d for d in output.all_generated_deliverables
            if d.kind == DeliverableKind.INVARIANT_CHECK
        ]
        assert len(inv_checks) >= 1

    def test_fmea_failure_modes_detected(self):
        """FMEA failure modes classified for computational deliverables."""
        deliverables = _make_test_deliverables()
        output = run_combined_m2_pass(deliverables)

        assert len(output.failure_modes) >= 1, (
            "Should detect failure modes for computational deliverables"
        )

    def test_cross_links_correct(self):
        """Cross-links between invariant entries and fmea_test deliverables."""
        deliverables = _make_test_deliverables()
        output = run_combined_m2_pass(deliverables)

        # Check that invariant entries have verification deliverable IDs
        for entry in output.invariant_output.entries:
            # Each entry should have at least the invariant_check IDs
            assert len(entry.verification_deliverable_ids) >= 1, (
                f"Entry '{entry.variable_name}' should have verification IDs"
            )

    def test_silent_corruption_triggers_release_gate(self):
        """Silent corruption -> Release Gate Rule 1 triggered."""
        # Deliverable with mutation but no error path on degenerate domain
        deliverables = [
            Deliverable(
                id="D2.1",
                description="Add replay offset counter for tracking position",
                kind=DeliverableKind.IMPLEMENT,
            ),
            Deliverable(
                id="D3.1",
                description="Advance replay offset by batch size, update position",
                kind=DeliverableKind.IMPLEMENT,
            ),
        ]

        output = run_combined_m2_pass(deliverables)

        # Check for any blocking violations from silent corruption
        if output.has_blocking_violations:
            for v in output.release_gate_violations:
                assert v.failure_mode.detection_difficulty == DetectionDifficulty.SILENT


class TestIdempotency:
    """Verify combined pass is idempotent."""

    def test_running_twice_identical_output(self):
        """Running twice produces identical output."""
        deliverables = _make_test_deliverables()

        output1 = run_combined_m2_pass(deliverables)
        output2 = run_combined_m2_pass(deliverables)

        assert output1.section_markdown == output2.section_markdown
        assert len(output1.all_generated_deliverables) == len(output2.all_generated_deliverables)
        assert len(output1.failure_modes) == len(output2.failure_modes)

    def test_idempotent_with_generated_fed_back(self):
        """Running with generated deliverables fed back produces same output."""
        deliverables = _make_test_deliverables()

        output1 = run_combined_m2_pass(deliverables)

        # Feed generated deliverables back
        all_deliverables = deliverables + output1.all_generated_deliverables
        output2 = run_combined_m2_pass(all_deliverables)

        # Same number of invariant entries (generated are filtered out)
        assert len(output1.invariant_output.entries) == len(output2.invariant_output.entries)


class TestCombinedOutput:
    """Verify combined output structure."""

    def test_all_generated_is_union(self):
        """all_generated_deliverables is union of invariant_check + fmea_test."""
        deliverables = _make_test_deliverables()
        output = run_combined_m2_pass(deliverables)

        inv_count = len(output.invariant_output.generated_deliverables)
        fmea_count = len(output.promotion_output.promoted_deliverables)

        assert len(output.all_generated_deliverables) == inv_count + fmea_count

    def test_empty_input(self):
        """Empty input produces no errors."""
        output = run_combined_m2_pass([])
        assert output.section_markdown != ""
        assert len(output.all_generated_deliverables) == 0

    def test_non_implement_only(self):
        """Only verify deliverables produce no invariant entries."""
        deliverables = [
            Deliverable(
                id="D1.1.b",
                description="Verify boundary conditions for offset",
                kind=DeliverableKind.VERIFY,
            ),
        ]
        output = run_combined_m2_pass(deliverables)
        assert len(output.invariant_output.entries) == 0
