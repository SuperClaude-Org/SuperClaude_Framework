"""Tests for FMEA deliverable promotion -- T02.08.

Scenarios from tasklist:
1. Silent corruption -> promoted fmea_test + release gate triggered
2. Cosmetic -> accepted risk in metadata
3. Promoted deliverable includes detection mechanism
4. Configurable threshold
5. Zero above-threshold -> no promotion and no accepted-risk entries
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.fmea_classifier import (
    DetectionDifficulty,
    FMEAFailureMode,
    Severity,
)
from superclaude.cli.pipeline.fmea_promotion import (
    FMEAPromotionOutput,
    ReleaseGateViolation,
    accept_violation,
    promote_failure_modes,
)
from superclaude.cli.pipeline.models import DeliverableKind


class TestFMEAPromotion:
    """Core promotion scenarios from tasklist."""

    def test_silent_corruption_promoted_and_gate_triggered(self):
        """Silent corruption -> promoted fmea_test + release gate triggered."""
        mode = FMEAFailureMode(
            deliverable_id="D2.3",
            domain_description="Zero numeric input",
            detection_difficulty=DetectionDifficulty.SILENT,
            severity=Severity.WRONG_STATE,
            signal_source="signal_1",
            description="State variable 'offset' mutated without error path",
        )

        output = promote_failure_modes([mode])

        assert len(output.promoted_deliverables) == 1
        d = output.promoted_deliverables[0]
        assert d.kind == DeliverableKind.FMEA_TEST
        assert "fmea" in d.id

        # Release gate triggered
        assert len(output.release_gate_violations) == 1
        assert output.has_blocking_violations is True

    def test_cosmetic_accepted_risk(self):
        """Cosmetic -> accepted risk in metadata."""
        mode = FMEAFailureMode(
            deliverable_id="D4.1",
            domain_description="Normal input",
            detection_difficulty=DetectionDifficulty.IMMEDIATE,
            severity=Severity.COSMETIC,
            signal_source="signal_2",
            description="Minor display issue on normal input",
        )

        output = promote_failure_modes([mode])

        assert len(output.promoted_deliverables) == 0
        assert len(output.accepted_risks) == 1
        risk = output.accepted_risks[0]
        assert risk["severity"] == "cosmetic"
        assert "rationale" in risk
        assert len(risk["rationale"]) > 0

    def test_promoted_deliverable_includes_detection_mechanism(self):
        """Promoted deliverable includes detection mechanism description."""
        mode = FMEAFailureMode(
            deliverable_id="D3.1",
            domain_description="Empty input",
            detection_difficulty=DetectionDifficulty.SILENT,
            severity=Severity.DATA_LOSS,
            signal_source="both",
            description="Dual signal: mutation without error path and wrong outcome detected",
        )

        output = promote_failure_modes([mode])
        d = output.promoted_deliverables[0]
        assert "Detection mechanism" in d.description or "Detection:" in d.description

    def test_configurable_threshold(self):
        """Threshold can be lowered to promote more modes."""
        mode = FMEAFailureMode(
            deliverable_id="D5.1",
            domain_description="Zero input",
            detection_difficulty=DetectionDifficulty.DELAYED,
            severity=Severity.DEGRADED,
            signal_source="signal_2",
            description="Returns degraded result on zero input",
        )

        # Default threshold (wrong_state) should not promote degraded
        output_default = promote_failure_modes([mode])
        assert len(output_default.promoted_deliverables) == 0

        # Lowered threshold should promote
        output_low = promote_failure_modes([mode], promotion_threshold=Severity.DEGRADED)
        assert len(output_low.promoted_deliverables) == 1

    def test_zero_above_threshold_no_entries(self):
        """Zero above-threshold -> no promotion and no accepted-risk entries."""
        output = promote_failure_modes([])

        assert len(output.promoted_deliverables) == 0
        assert len(output.accepted_risks) == 0
        assert len(output.release_gate_violations) == 0


class TestReleaseGateRule1:
    """Release Gate Rule 1 enforcement."""

    def test_blocking_until_accepted(self):
        """Violations block until explicitly accepted."""
        mode = FMEAFailureMode(
            deliverable_id="D2.3",
            domain_description="Zero input",
            detection_difficulty=DetectionDifficulty.SILENT,
            severity=Severity.WRONG_STATE,
            signal_source="signal_1",
            description="Silent corruption",
        )

        output = promote_failure_modes([mode])
        assert output.has_blocking_violations is True

    def test_acceptance_requires_named_owner(self):
        """Acceptance requires non-empty named owner."""
        violation = ReleaseGateViolation(
            failure_mode=FMEAFailureMode(
                deliverable_id="D2.3",
                domain_description="Zero",
                detection_difficulty=DetectionDifficulty.SILENT,
                severity=Severity.WRONG_STATE,
                signal_source="signal_1",
                description="Silent corruption",
            ),
        )

        with pytest.raises(ValueError, match="accepted_by must not be empty"):
            accept_violation(violation, "", "some rationale")

    def test_acceptance_requires_rationale(self):
        """Acceptance requires non-empty rationale."""
        violation = ReleaseGateViolation(
            failure_mode=FMEAFailureMode(
                deliverable_id="D2.3",
                domain_description="Zero",
                detection_difficulty=DetectionDifficulty.SILENT,
                severity=Severity.WRONG_STATE,
                signal_source="signal_1",
                description="Silent corruption",
            ),
        )

        with pytest.raises(ValueError, match="acceptance_rationale must not be empty"):
            accept_violation(violation, "team_lead", "")

    def test_accepted_violation_no_longer_blocking(self):
        """Accepted violation no longer blocks."""
        mode = FMEAFailureMode(
            deliverable_id="D2.3",
            domain_description="Zero",
            detection_difficulty=DetectionDifficulty.SILENT,
            severity=Severity.WRONG_STATE,
            signal_source="signal_1",
            description="Silent corruption",
        )
        output = promote_failure_modes([mode])
        assert output.has_blocking_violations is True

        accept_violation(
            output.release_gate_violations[0],
            "project_lead",
            "Risk accepted after manual review of boundary conditions",
        )
        assert output.has_blocking_violations is False


class TestMarkdownOutput:
    """Verify markdown section rendering."""

    def test_section_contains_headings(self):
        mode = FMEAFailureMode(
            deliverable_id="D2.3",
            domain_description="Zero",
            detection_difficulty=DetectionDifficulty.SILENT,
            severity=Severity.WRONG_STATE,
            signal_source="signal_1",
            description="Silent corruption",
        )
        output = promote_failure_modes([mode])
        assert "## FMEA Failure Mode Analysis" in output.section_markdown
        assert "Release Gate Rule 1" in output.section_markdown

    def test_empty_section(self):
        output = promote_failure_modes([])
        assert "No failure modes detected" in output.section_markdown
