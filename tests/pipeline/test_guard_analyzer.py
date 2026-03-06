"""Tests for guard and sentinel analyzer (T03.01 / D-0032).

Five-scenario test suite:
1. "Replace boolean replay guard with integer offset" -> ambiguity for value `0`
2. Boolean with clear semantics -> no flag
3. Enum with exhaustive match -> no flag
4. Integer without documented zero/negative semantics -> flagged
5. Bool->int always triggers transition analysis
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.guard_analyzer import (
    GuardDetection,
    GuardKind,
    TypeTransitionKind,
    detect_guards,
)
from superclaude.cli.pipeline.models import Deliverable, DeliverableKind


def _make_deliverable(desc: str, did: str = "D-0001") -> Deliverable:
    return Deliverable(id=did, description=desc, kind=DeliverableKind.IMPLEMENT)


class TestGuardAnalyzer:
    """T03.01 acceptance criteria test suite."""

    def test_bool_to_int_replay_guard_ambiguity(self):
        """Scenario 1: 'Replace boolean replay guard with integer offset'
        -> ambiguity for value 0, with both semantic meanings documented."""
        d = _make_deliverable(
            "Replace boolean replay guard with integer offset for _replayed_event_offset"
        )
        results = detect_guards([d])
        assert len(results) >= 1

        # Find the type change detection
        type_detections = [r for r in results if r.type_transition == TypeTransitionKind.BOOL_TO_INT]
        assert len(type_detections) >= 1

        det = type_detections[0]
        assert det.guard_kind == GuardKind.TYPE_CHANGE
        assert det.type_transition == TypeTransitionKind.BOOL_TO_INT
        assert det.ambiguity_flagged is True

        # Value 0 must have multiple semantic meanings
        zero_states = [s for s in det.states if s.value == "0"]
        assert len(zero_states) == 1
        assert len(zero_states[0].semantic_meanings) >= 2
        # Both meanings documented
        meanings_text = [m.meaning for m in zero_states[0].semantic_meanings]
        assert any("replay" in m or "no events" in m or "start offset" in m for m in meanings_text)

    def test_boolean_clear_semantics_no_flag(self):
        """Scenario 2: Boolean guard with clear true/false semantics -> no ambiguity flag."""
        d = _make_deliverable(
            "Check if is_enabled flag to determine whether feature is active"
        )
        results = detect_guards([d])
        assert len(results) >= 1

        flag_detections = [r for r in results if r.guard_kind == GuardKind.FLAG_CHECK]
        assert len(flag_detections) >= 1

        det = flag_detections[0]
        assert det.ambiguity_flagged is False
        # Each state has exactly one meaning
        for state in det.states:
            assert len(state.semantic_meanings) == 1

    def test_enum_exhaustive_match_no_flag(self):
        """Scenario 3: Enum with exhaustive match -> no flag."""
        d = _make_deliverable(
            "Replace boolean enabled with 3-state enum (ACTIVE, PAUSED, DISABLED)"
        )
        results = detect_guards([d])
        type_detections = [r for r in results if r.type_transition == TypeTransitionKind.BOOL_TO_ENUM]
        assert len(type_detections) >= 1

        det = type_detections[0]
        # Bool->enum with 3 distinct states, each has single meaning
        assert det.ambiguity_flagged is False
        assert len(det.states) >= 3
        for state in det.states:
            assert len(state.semantic_meanings) == 1

    def test_integer_no_documented_semantics_flagged(self):
        """Scenario 4: Integer without documented zero/negative semantics -> flagged."""
        d = _make_deliverable(
            "Replace boolean processed with integer count for tracking"
        )
        results = detect_guards([d])
        type_detections = [r for r in results if r.type_transition == TypeTransitionKind.BOOL_TO_INT]
        assert len(type_detections) >= 1

        det = type_detections[0]
        assert det.ambiguity_flagged is True
        # Value 0 has multiple meanings (original false + zero count)
        zero_states = [s for s in det.states if s.value == "0"]
        assert len(zero_states) == 1
        assert zero_states[0].is_ambiguous is True

    def test_bool_to_int_always_triggers_transition_analysis(self):
        """Scenario 5: Bool->int always triggers transition analysis regardless of ambiguity."""
        d = _make_deliverable(
            "Replace boolean replay guard with integer offset for tracking events"
        )
        results = detect_guards([d])
        type_detections = [r for r in results if r.type_transition == TypeTransitionKind.BOOL_TO_INT]
        assert len(type_detections) >= 1

        det = type_detections[0]
        assert det.requires_transition_analysis is True

    def test_suppression_annotation(self):
        """@no-ambiguity-check suppresses ambiguity flag with rationale."""
        d = _make_deliverable(
            "Replace boolean guard with integer offset @no-ambiguity-check(zero semantics documented in ADR-42)"
        )
        results = detect_guards([d])
        type_detections = [r for r in results if r.type_transition == TypeTransitionKind.BOOL_TO_INT]
        assert len(type_detections) >= 1

        det = type_detections[0]
        assert det.suppressed is True
        assert det.suppression_rationale == "zero semantics documented in ADR-42"
        assert det.ambiguity_flagged is False  # Suppressed

    def test_empty_deliverables(self):
        """Empty input returns empty output."""
        assert detect_guards([]) == []

    def test_non_guard_deliverable(self):
        """Description without guard patterns returns no detections."""
        d = _make_deliverable("Add logging to the data processing module")
        results = detect_guards([d])
        assert len(results) == 0

    def test_multiple_guards_in_single_deliverable(self):
        """Multiple guard patterns in one deliverable all detected."""
        d = _make_deliverable(
            "Check if is_ready flag and use threshold max_retries as sentinel for early return"
        )
        results = detect_guards([d])
        assert len(results) >= 2
        var_names = {r.guard_variable for r in results}
        assert "is_ready" in var_names or "max_retries" in var_names
