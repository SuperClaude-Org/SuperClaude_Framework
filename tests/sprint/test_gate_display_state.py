"""Tests for GateDisplayState enum and transition validation."""

import pytest

from superclaude.cli.sprint.models import (
    GATE_DISPLAY_TRANSITIONS,
    GateDisplayState,
    is_valid_gate_transition,
)


class TestGateDisplayStateEnum:
    """T08.01: GateDisplayState has exactly 7 values with display properties."""

    def test_exactly_7_values(self):
        assert len(GateDisplayState) == 7

    def test_expected_members(self):
        expected = {"NONE", "CHECKING", "PASS", "FAIL_DEFERRED", "REMEDIATING", "REMEDIATED", "HALT"}
        actual = {m.name for m in GateDisplayState}
        assert actual == expected

    def test_each_state_has_color(self):
        for state in GateDisplayState:
            assert isinstance(state.color, str), f"{state} missing color"
            assert len(state.color) > 0

    def test_each_state_has_icon(self):
        for state in GateDisplayState:
            assert isinstance(state.icon, str), f"{state} missing icon"
            assert len(state.icon) > 0

    def test_each_state_has_label(self):
        for state in GateDisplayState:
            assert isinstance(state.label, str), f"{state} missing label"
            assert len(state.label) > 0

    def test_colors_are_distinct(self):
        colors = [s.color for s in GateDisplayState]
        assert len(set(colors)) == len(colors), "Colors must be distinct per state"

    def test_icons_are_distinct(self):
        icons = [s.icon for s in GateDisplayState]
        assert len(set(icons)) == len(icons), "Icons must be distinct per state"


class TestGateDisplayTransitions:
    """State transitions follow the gate lifecycle."""

    def test_none_to_checking(self):
        assert is_valid_gate_transition(GateDisplayState.NONE, GateDisplayState.CHECKING)

    def test_checking_to_pass(self):
        assert is_valid_gate_transition(GateDisplayState.CHECKING, GateDisplayState.PASS)

    def test_checking_to_fail_deferred(self):
        assert is_valid_gate_transition(GateDisplayState.CHECKING, GateDisplayState.FAIL_DEFERRED)

    def test_fail_deferred_to_remediating(self):
        assert is_valid_gate_transition(GateDisplayState.FAIL_DEFERRED, GateDisplayState.REMEDIATING)

    def test_remediating_to_remediated(self):
        assert is_valid_gate_transition(GateDisplayState.REMEDIATING, GateDisplayState.REMEDIATED)

    def test_remediating_to_halt(self):
        assert is_valid_gate_transition(GateDisplayState.REMEDIATING, GateDisplayState.HALT)

    def test_invalid_transition_none_to_pass(self):
        assert not is_valid_gate_transition(GateDisplayState.NONE, GateDisplayState.PASS)

    def test_invalid_transition_pass_to_checking(self):
        assert not is_valid_gate_transition(GateDisplayState.PASS, GateDisplayState.CHECKING)

    def test_invalid_transition_halt_to_anything(self):
        for state in GateDisplayState:
            assert not is_valid_gate_transition(GateDisplayState.HALT, state)

    def test_transition_set_has_expected_count(self):
        # 6 valid transitions per the lifecycle diagram
        assert len(GATE_DISPLAY_TRANSITIONS) == 6

    def test_full_happy_path(self):
        """NONE → CHECKING → PASS is valid."""
        assert is_valid_gate_transition(GateDisplayState.NONE, GateDisplayState.CHECKING)
        assert is_valid_gate_transition(GateDisplayState.CHECKING, GateDisplayState.PASS)

    def test_full_remediation_path(self):
        """NONE → CHECKING → FAIL_DEFERRED → REMEDIATING → REMEDIATED is valid."""
        path = [
            GateDisplayState.NONE,
            GateDisplayState.CHECKING,
            GateDisplayState.FAIL_DEFERRED,
            GateDisplayState.REMEDIATING,
            GateDisplayState.REMEDIATED,
        ]
        for i in range(len(path) - 1):
            assert is_valid_gate_transition(path[i], path[i + 1]), f"Invalid: {path[i]} → {path[i+1]}"

    def test_full_halt_path(self):
        """NONE → CHECKING → FAIL_DEFERRED → REMEDIATING → HALT is valid."""
        path = [
            GateDisplayState.NONE,
            GateDisplayState.CHECKING,
            GateDisplayState.FAIL_DEFERRED,
            GateDisplayState.REMEDIATING,
            GateDisplayState.HALT,
        ]
        for i in range(len(path) - 1):
            assert is_valid_gate_transition(path[i], path[i + 1]), f"Invalid: {path[i]} → {path[i+1]}"
