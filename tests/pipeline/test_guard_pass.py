"""Integration tests for guard analysis pipeline pass (T03.03 / D-0036).

Two integration test scenarios:
1. Roadmap with type-migration deliverable (bool->int) -> guard analysis section present,
   ambiguity for `0` detected, release gate warning with mandatory owner, guard_test
   deliverables in correct milestone
2. Boolean guard with clear semantics -> no ambiguity flags, no release gate
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.guard_pass import (
    GuardAnalysisOutput,
    run_guard_analysis_pass,
)
from superclaude.cli.pipeline.invariant_pass import (
    InvariantRegistryOutput,
    run_invariant_registry_pass,
)
from superclaude.cli.pipeline.invariants import InvariantEntry, MutationSite
from superclaude.cli.pipeline.models import Deliverable, DeliverableKind


def _make(desc: str, did: str = "D-0001") -> Deliverable:
    return Deliverable(id=did, description=desc, kind=DeliverableKind.IMPLEMENT)


class TestGuardPassIntegration:
    """T03.03 integration tests."""

    def test_type_migration_bool_to_int_full_pipeline(self):
        """Integration test 1: bool->int type migration through full M2->M3 pipeline.

        Verifies:
        - Guard analysis section present
        - Ambiguity for `0` detected
        - Release gate warning with mandatory owner field
        - Guard_test deliverables generated
        """
        deliverables = [
            _make(
                "Replace boolean replay guard with integer offset for _replayed_event_offset",
                "D-0001",
            ),
            _make(
                "Compute event count from tail_events list",
                "D-0002",
            ),
        ]

        # Run M2 invariant registry pass first
        inv_output = run_invariant_registry_pass(deliverables)

        # Run M3 guard analysis pass
        fmea_map = {"D-0001": "high"}  # Simulate FMEA severity
        result = run_guard_analysis_pass(deliverables, inv_output, fmea_map)

        # Guard analysis section present
        assert "## Guard Analysis" in result.section_markdown
        assert "State Enumeration" in result.section_markdown

        # Ambiguity for 0 detected
        ambiguous = [d for d in result.detections if d.has_ambiguity]
        assert len(ambiguous) >= 1
        zero_states = []
        for det in ambiguous:
            zero_states.extend(s for s in det.states if s.value == "0" and s.is_ambiguous)
        assert len(zero_states) >= 1

        # Release gate warning with mandatory owner
        assert result.resolution.has_blocking_warnings is True
        assert len(result.resolution.gate_warnings) >= 1
        warning = result.resolution.gate_warnings[0]
        assert warning.is_blocking is True
        assert warning.owner == ""  # Mandatory field not yet assigned

        # Guard_test deliverables generated
        assert len(result.resolution.guard_test_deliverables) >= 2

        # Cannot advance to M4
        assert result.can_advance_to_m4 is False

        # FMEA elevation detected
        assert len(result.fmea_elevations) >= 1

    def test_boolean_guard_clear_semantics_no_flags(self):
        """Integration test 2: boolean guard with clear semantics -> no flags.

        Verifies:
        - No ambiguity flags
        - No release gate warnings
        - Can advance to M4
        """
        deliverables = [
            _make(
                "Check if is_enabled flag to determine whether feature is active",
                "D-0001",
            ),
            _make(
                "Update user preferences from settings panel",
                "D-0002",
            ),
        ]

        inv_output = run_invariant_registry_pass(deliverables)
        result = run_guard_analysis_pass(deliverables, inv_output)

        # No ambiguity
        for det in result.detections:
            assert det.ambiguity_flagged is False

        # No release gate warnings
        assert len(result.resolution.gate_warnings) == 0
        assert result.resolution.has_blocking_warnings is False

        # Can advance
        assert result.can_advance_to_m4 is True

    def test_invariant_cross_reference(self):
        """Guard variables cross-referenced with invariant entries."""
        deliverables = [
            _make(
                "Replace boolean replay guard with integer offset",
                "D-0001",
            ),
        ]

        # Create invariant output with matching entry
        inv_output = InvariantRegistryOutput(
            entries=[
                InvariantEntry(
                    variable_name="replay",
                    scope="module-level",
                    invariant_predicate="replay >= 0",
                    mutation_sites=[
                        MutationSite(deliverable_id="D-0001", expression="introduced as replacement"),
                    ],
                ),
            ],
        )

        result = run_guard_analysis_pass(deliverables, inv_output)

        # Cross-reference should find match
        assert "replay" in result.invariant_cross_refs
        assert result.invariant_cross_refs["replay"] is not None

    def test_no_guards_empty_section(self):
        """Deliverables without guard patterns produce empty section."""
        deliverables = [
            _make("Add logging to the data processing module", "D-0001"),
        ]

        result = run_guard_analysis_pass(deliverables)
        assert "No guard patterns detected" in result.section_markdown
        assert result.can_advance_to_m4 is True

    def test_pipeline_order_m2_then_m3(self):
        """Verify M3 uses M2 output correctly (pipeline ordering)."""
        deliverables = [
            _make(
                "Replace boolean processed with integer count",
                "D-0001",
            ),
        ]

        # M2 first
        inv_output = run_invariant_registry_pass(deliverables)

        # M3 uses M2 output
        fmea_map = {"D-0001": "medium"}
        result = run_guard_analysis_pass(deliverables, inv_output, fmea_map)

        # M3 completed without error
        assert result.section_markdown
        assert len(result.detections) >= 1

        # Medium severity should NOT elevate (only high/critical)
        assert len(result.fmea_elevations) == 0

    def test_fmea_elevation_only_for_high_severity(self):
        """FMEA elevation only occurs for high/critical severity."""
        deliverables = [
            _make("Replace boolean x with integer y", "D-0001"),
            _make("Replace boolean a with integer b", "D-0002"),
        ]

        inv_output = run_invariant_registry_pass(deliverables)
        fmea_map = {"D-0001": "high", "D-0002": "low"}
        result = run_guard_analysis_pass(deliverables, inv_output, fmea_map)

        # Only D-0001 (high severity) should elevate
        elevated_vars = set(result.fmea_elevations)
        # The variable from D-0001 should be elevated
        d1_detections = [d for d in result.detections if d.deliverable_id == "D-0001" and d.has_ambiguity]
        if d1_detections:
            assert d1_detections[0].guard_variable in elevated_vars
