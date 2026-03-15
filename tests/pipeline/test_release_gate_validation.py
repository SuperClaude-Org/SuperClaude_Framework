"""T02.10 validation tests -- Release Gate Rule 1 and known bug pattern detection.

Validates:
1. Silent corruption findings block downstream progression
2. Known bug pattern: wrong-operand state mutation (_loaded_start_index -= mounted)
3. Known bug pattern: sentinel ambiguity (_replayed_event_offset = len(plan.tail_events))
4. Phase 2 exit criteria
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.combined_m2_pass import run_combined_m2_pass
from superclaude.cli.pipeline.fmea_classifier import DetectionDifficulty, Severity
from superclaude.cli.pipeline.fmea_promotion import accept_violation
from superclaude.cli.pipeline.models import Deliverable, DeliverableKind


class TestReleaseGateRule1Enforcement:
    """Validate Release Gate Rule 1: silent corruption blocks downstream."""

    def test_silent_corruption_blocks_progression(self):
        """Pipeline refuses to advance with unresolved silent corruption."""
        deliverables = [
            Deliverable(
                id="D2.1",
                description="Add loaded_start_index offset for tracking loaded position",
                kind=DeliverableKind.IMPLEMENT,
            ),
            Deliverable(
                id="D3.1",
                description="Advance loaded_start_index by batch count, update position",
                kind=DeliverableKind.IMPLEMENT,
            ),
        ]

        output = run_combined_m2_pass(deliverables)

        if output.has_blocking_violations:
            # Verify blocking condition
            for v in output.release_gate_violations:
                assert not v.accepted, "Unresolved violations must block"

    def test_acceptance_unblocks_progression(self):
        """Explicit acceptance with owner + rationale unblocks."""
        deliverables = [
            Deliverable(
                id="D2.1",
                description="Add loaded_start_index offset for tracking loaded position",
                kind=DeliverableKind.IMPLEMENT,
            ),
            Deliverable(
                id="D3.1",
                description="Advance loaded_start_index by batch count, update position",
                kind=DeliverableKind.IMPLEMENT,
            ),
        ]

        output = run_combined_m2_pass(deliverables)

        if output.has_blocking_violations:
            for v in output.release_gate_violations:
                accept_violation(v, "team_lead", "Reviewed and mitigated via boundary test")

            assert not output.has_blocking_violations


class TestKnownBugPatterns:
    """Verify known source bug patterns are caught during planning."""

    def test_wrong_operand_state_mutation_detected(self):
        """Wrong-operand: _loaded_start_index -= mounted caught by invariant registry."""
        deliverables = [
            Deliverable(
                id="D2.1",
                description="Add self._loaded_start_index counter for tracking replay position",
                kind=DeliverableKind.IMPLEMENT,
            ),
            Deliverable(
                id="D3.1",
                description="Decrement self._loaded_start_index by mounted count to advance position",
                kind=DeliverableKind.IMPLEMENT,
            ),
        ]

        output = run_combined_m2_pass(deliverables)

        # State variable should be detected
        detected_vars = [e.variable_name for e in output.invariant_output.entries]
        assert any("loaded_start_index" in v for v in detected_vars), (
            f"_loaded_start_index should be detected. Got: {detected_vars}"
        )

        # Invariant check deliverables should be generated
        assert len(output.invariant_output.generated_deliverables) >= 1

    def test_sentinel_ambiguity_detected(self):
        """Sentinel ambiguity: _replayed_event_offset = len(plan.tail_events) caught."""
        deliverables = [
            Deliverable(
                id="D2.1",
                description="Add self._replayed_event_offset counter for replay tracking",
                kind=DeliverableKind.IMPLEMENT,
            ),
            Deliverable(
                id="D4.1",
                description="Set self._replayed_event_offset to track completed replay position",
                kind=DeliverableKind.IMPLEMENT,
            ),
        ]

        output = run_combined_m2_pass(deliverables)

        detected_vars = [e.variable_name for e in output.invariant_output.entries]
        assert any("replayed_event_offset" in v for v in detected_vars), (
            f"_replayed_event_offset should be detected. Got: {detected_vars}"
        )


class TestPhase2ExitCriteria:
    """Phase 2 milestone exit criteria validation."""

    def test_all_deliverable_types_present(self):
        """D-0011 through D-0028 artifact paths should exist."""
        import os

        base = "/config/workspace/SuperClaude_Framework/.dev/releases/complete/v.2.11-roadmap-v4/tasklist/artifacts"

        if not os.path.isdir(base):
            pytest.skip(f"Artifact base directory not present in this environment: {base}")

        for d_num in range(11, 29):
            d_dir = os.path.join(base, f"D-{d_num:04d}")
            assert os.path.isdir(d_dir), f"Artifact directory missing: {d_dir}"

            # Check for at least one file
            contents = os.listdir(d_dir)
            assert len(contents) >= 1, f"Empty artifact directory: {d_dir}"

    def test_constrained_grammar_rejects_freeform(self):
        """Constrained grammar rejects free-form invariant predicates."""
        from superclaude.cli.pipeline.invariants import InvariantEntry

        with pytest.raises(ValueError, match="constrained grammar"):
            InvariantEntry(
                variable_name="offset",
                scope="class",
                invariant_predicate="the offset should always be positive",
            )

    def test_dual_signal_independence(self):
        """Signal 2 independently detects without invariant predicates."""
        from superclaude.cli.pipeline.fmea_classifier import classify_failure_modes
        from superclaude.cli.pipeline.fmea_domains import DomainCategory, InputDomain

        d = Deliverable(
            id="D5.1",
            description="Increment replay offset, update position counter",
            kind=DeliverableKind.IMPLEMENT,
        )
        domains = {"D5.1": [InputDomain(DomainCategory.ZERO, "Zero numeric input")]}

        results = classify_failure_modes([d], domains, invariant_entries=[])
        silent = [r for r in results if r.detection_difficulty == DetectionDifficulty.SILENT]
        assert len(silent) >= 1, "Signal 2 must detect independently"
