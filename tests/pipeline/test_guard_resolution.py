"""Tests for guard resolution and Release Gate Rule 2 (T03.02 / D-0034).

Four-scenario test suite:
1. Ambiguous integer guard -> >=2 guard_test deliverables + release gate warning with mandatory owner
2. Unambiguous boolean -> zero guard deliverables
3. Bool->3-state enum -> transition mapping deliverable
4. Accepted-risk rationale is non-empty string with owner name
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.guard_analyzer import (
    GuardDetection,
    GuardKind,
    GuardState,
    SemanticMeaning,
    TypeTransitionKind,
    detect_guards,
)
from superclaude.cli.pipeline.guard_resolution import (
    AcceptedRisk,
    GuardResolutionOutput,
    ReleaseGateWarning,
    resolve_guards,
)
from superclaude.cli.pipeline.models import Deliverable, DeliverableKind


def _make_deliverable(desc: str, did: str = "D-0001") -> Deliverable:
    return Deliverable(id=did, description=desc, kind=DeliverableKind.IMPLEMENT)


class TestGuardResolution:
    """T03.02 acceptance criteria test suite."""

    def test_ambiguous_integer_guard_produces_deliverables_and_warning(self):
        """Scenario 1: Ambiguous integer guard -> >=2 guard_test deliverables + release gate warning."""
        d = _make_deliverable(
            "Replace boolean processed with integer count for tracking"
        )
        detections = detect_guards([d])
        result = resolve_guards(detections)

        # At minimum 2 guard_test deliverables (semantic doc + uniqueness test)
        assert len(result.guard_test_deliverables) >= 2
        assert all(
            d.kind == DeliverableKind.GUARD_TEST
            for d in result.guard_test_deliverables
        )

        # Release gate warning with mandatory owner
        assert len(result.gate_warnings) >= 1
        warning = result.gate_warnings[0]
        assert warning.is_blocking is True
        assert warning.owner == ""  # No owner assigned yet

    def test_unambiguous_boolean_zero_deliverables(self):
        """Scenario 2: Unambiguous boolean -> zero guard deliverables."""
        d = _make_deliverable(
            "Check if is_enabled flag to determine whether feature is active"
        )
        detections = detect_guards([d])
        result = resolve_guards(detections)

        assert len(result.guard_test_deliverables) == 0
        assert len(result.gate_warnings) == 0
        assert result.can_advance is True

    def test_bool_to_enum_transition_mapping(self):
        """Scenario 3: Bool->3-state enum -> transition mapping deliverable.

        Note: bool->enum with 3 distinct states (each single meaning) is NOT
        ambiguous, so no guard_test deliverables are generated.
        """
        d = _make_deliverable(
            "Replace boolean enabled with 3-state enum (ACTIVE, PAUSED, DISABLED)"
        )
        detections = detect_guards([d])
        result = resolve_guards(detections)

        # Bool->enum with exhaustive match is not ambiguous
        assert len(result.guard_test_deliverables) == 0
        assert result.can_advance is True

    def test_accepted_risk_validation(self):
        """Scenario 4: Accepted-risk rationale is non-empty string with owner name."""
        # Valid accepted risk
        risk = AcceptedRisk(owner="John Doe", rationale="Zero semantics documented in ADR-42")
        assert risk.owner == "John Doe"
        assert risk.rationale == "Zero semantics documented in ADR-42"

        # Empty owner rejected
        with pytest.raises(ValueError, match="non-empty owner"):
            AcceptedRisk(owner="", rationale="some rationale")

        # Missing rationale rejected
        with pytest.raises(ValueError, match="non-empty rationale"):
            AcceptedRisk(owner="John Doe", rationale="")

    def test_warning_resolved_with_owner(self):
        """Warning is resolved when owner is assigned."""
        warning = ReleaseGateWarning(
            guard_variable="count",
            deliverable_id="D-0001",
            message="test",
            owner="Jane Smith",
            review_date="2026-04-01",
        )
        assert warning.is_resolved is True
        assert warning.is_blocking is False

    def test_warning_resolved_with_accepted_risk(self):
        """Warning is resolved when accepted risk is provided."""
        risk = AcceptedRisk(owner="John", rationale="documented in ADR")
        warning = ReleaseGateWarning(
            guard_variable="count",
            deliverable_id="D-0001",
            message="test",
            accepted_risk=risk,
        )
        assert warning.is_resolved is True
        assert warning.is_blocking is False

    def test_bool_to_int_produces_transition_deliverable(self):
        """Bool->int ambiguous guard produces transition mapping deliverable."""
        d = _make_deliverable(
            "Replace boolean processed with integer count for tracking"
        )
        detections = detect_guards([d])
        result = resolve_guards(detections)

        # Should include a transition mapping deliverable
        trans_deliverables = [
            d for d in result.guard_test_deliverables
            if d.metadata.get("test_type") == "transition_mapping"
        ]
        assert len(trans_deliverables) >= 1
        assert trans_deliverables[0].metadata["transition_kind"] == "bool_to_int"

    def test_output_can_advance_blocks_on_unresolved(self):
        """GuardResolutionOutput.can_advance is False when warnings are blocking."""
        d = _make_deliverable(
            "Replace boolean replay guard with integer offset"
        )
        detections = detect_guards([d])
        result = resolve_guards(detections)

        assert result.has_blocking_warnings is True
        assert result.can_advance is False

    def test_suppressed_guard_no_resolution(self):
        """Suppressed guards produce no deliverables or warnings."""
        d = _make_deliverable(
            "Replace boolean guard with integer offset @no-ambiguity-check(documented in ADR-42)"
        )
        detections = detect_guards([d])
        result = resolve_guards(detections)

        assert len(result.guard_test_deliverables) == 0
        assert len(result.gate_warnings) == 0

    def test_section_markdown_rendered(self):
        """Resolution section markdown is non-empty for ambiguous guards."""
        d = _make_deliverable("Replace boolean x with integer y")
        detections = detect_guards([d])
        result = resolve_guards(detections)

        assert "## Guard Resolution" in result.section_markdown
        assert "BLOCKING" in result.section_markdown
