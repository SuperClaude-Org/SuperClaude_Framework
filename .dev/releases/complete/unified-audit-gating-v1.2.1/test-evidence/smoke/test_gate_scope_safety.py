"""Smoke tests for the critical safety invariant: Release-scope gates are ALWAYS BLOCKING.

unified-audit-gating-v1.2.1 introduces scope-based gate strategy via
``resolve_gate_mode`` in ``trailing_gate.py``:

  - Release scope  -> BLOCKING (always, hardcoded, non-configurable)
  - Milestone scope -> configurable (default: BLOCKING)
  - Task scope     -> TRAILING when grace_period > 0, else BLOCKING

These tests verify that no combination of arguments can cause a release-scope
gate to resolve as TRAILING. A release gate being allowed to trail would
bypass the pre-ship verification contract and is a safety-critical defect.

Tested API surface:
  - trailing_gate.GateScope (enum)
  - trailing_gate.resolve_gate_mode (function)
  - models.GateMode (enum)
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.models import GateMode
from superclaude.cli.pipeline.trailing_gate import GateScope, resolve_gate_mode


# ---------------------------------------------------------------------------
# 1. Release-scope gates are ALWAYS GateMode.BLOCKING
# ---------------------------------------------------------------------------


class TestReleaseScopeAlwaysBlocking:
    """Verify the hardcoded invariant: release gates cannot be TRAILING."""

    def test_release_default_is_blocking(self) -> None:
        """Release scope with all defaults must resolve to BLOCKING."""
        result = resolve_gate_mode(scope=GateScope.RELEASE)
        assert result is GateMode.BLOCKING, (
            f"Release-scope gate resolved to {result!r} with defaults; "
            "expected GateMode.BLOCKING"
        )

    def test_release_ignores_trailing_config(self) -> None:
        """Explicitly requesting TRAILING for a release gate must be overridden to BLOCKING."""
        result = resolve_gate_mode(
            scope=GateScope.RELEASE,
            config_gate_mode=GateMode.TRAILING,
        )
        assert result is GateMode.BLOCKING, (
            f"Release-scope gate resolved to {result!r} when config_gate_mode=TRAILING; "
            "the release scope must override any configured mode to BLOCKING"
        )

    def test_release_ignores_grace_period(self) -> None:
        """A non-zero grace_period must NOT make a release gate trailing."""
        result = resolve_gate_mode(
            scope=GateScope.RELEASE,
            grace_period=10,
        )
        assert result is GateMode.BLOCKING, (
            f"Release-scope gate resolved to {result!r} with grace_period=10; "
            "grace_period must be ignored for release scope"
        )

    def test_release_ignores_trailing_config_and_grace_period(self) -> None:
        """Both TRAILING config and grace_period together must still yield BLOCKING."""
        result = resolve_gate_mode(
            scope=GateScope.RELEASE,
            config_gate_mode=GateMode.TRAILING,
            grace_period=999,
        )
        assert result is GateMode.BLOCKING, (
            f"Release-scope gate resolved to {result!r} when both "
            "config_gate_mode=TRAILING and grace_period=999; "
            "release scope must be unconditionally BLOCKING"
        )

    @pytest.mark.parametrize("grace_period", [0, 1, 5, 60, 3600])
    def test_release_blocking_across_grace_periods(self, grace_period: int) -> None:
        """Release scope must be BLOCKING regardless of any grace_period value."""
        result = resolve_gate_mode(
            scope=GateScope.RELEASE,
            grace_period=grace_period,
        )
        assert result is GateMode.BLOCKING, (
            f"Release-scope gate resolved to {result!r} with grace_period={grace_period}"
        )

    @pytest.mark.parametrize("config_mode", list(GateMode))
    def test_release_blocking_across_all_gate_modes(self, config_mode: GateMode) -> None:
        """Release scope must be BLOCKING regardless of any config_gate_mode value."""
        result = resolve_gate_mode(
            scope=GateScope.RELEASE,
            config_gate_mode=config_mode,
        )
        assert result is GateMode.BLOCKING, (
            f"Release-scope gate resolved to {result!r} "
            f"with config_gate_mode={config_mode!r}"
        )


# ---------------------------------------------------------------------------
# 2. Task-scope gates default to TRAILING (when grace_period > 0)
# ---------------------------------------------------------------------------


class TestTaskScopeDefaults:
    """Verify task-scope gates trail when grace_period > 0."""

    def test_task_trailing_with_grace_period(self) -> None:
        """Task scope with grace_period > 0 must resolve to TRAILING."""
        result = resolve_gate_mode(
            scope=GateScope.TASK,
            grace_period=1,
        )
        assert result is GateMode.TRAILING, (
            f"Task-scope gate resolved to {result!r} with grace_period=1; "
            "expected GateMode.TRAILING"
        )

    def test_task_blocking_with_zero_grace_period(self) -> None:
        """Task scope with grace_period=0 must resolve to BLOCKING."""
        result = resolve_gate_mode(
            scope=GateScope.TASK,
            grace_period=0,
        )
        assert result is GateMode.BLOCKING, (
            f"Task-scope gate resolved to {result!r} with grace_period=0; "
            "expected GateMode.BLOCKING"
        )

    def test_task_trailing_with_large_grace_period(self) -> None:
        """Task scope with a large grace_period must still resolve to TRAILING."""
        result = resolve_gate_mode(
            scope=GateScope.TASK,
            grace_period=3600,
        )
        assert result is GateMode.TRAILING, (
            f"Task-scope gate resolved to {result!r} with grace_period=3600; "
            "expected GateMode.TRAILING"
        )

    def test_task_defaults_to_blocking_no_args(self) -> None:
        """Task scope with all defaults (grace_period=0) must be BLOCKING."""
        result = resolve_gate_mode(scope=GateScope.TASK)
        assert result is GateMode.BLOCKING, (
            f"Task-scope gate resolved to {result!r} with all defaults; "
            "expected GateMode.BLOCKING (grace_period defaults to 0)"
        )


# ---------------------------------------------------------------------------
# 3. Milestone-scope gates default to BLOCKING
# ---------------------------------------------------------------------------


class TestMilestoneScopeDefaults:
    """Verify milestone-scope gate defaults and configurability."""

    def test_milestone_default_is_blocking(self) -> None:
        """Milestone scope with defaults must resolve to BLOCKING."""
        result = resolve_gate_mode(scope=GateScope.MILESTONE)
        assert result is GateMode.BLOCKING, (
            f"Milestone-scope gate resolved to {result!r} with defaults; "
            "expected GateMode.BLOCKING"
        )

    def test_milestone_configurable_to_trailing(self) -> None:
        """Milestone scope must respect config_gate_mode=TRAILING when set."""
        result = resolve_gate_mode(
            scope=GateScope.MILESTONE,
            config_gate_mode=GateMode.TRAILING,
        )
        assert result is GateMode.TRAILING, (
            f"Milestone-scope gate resolved to {result!r} with "
            "config_gate_mode=TRAILING; milestone scope should be configurable"
        )

    def test_milestone_configurable_to_blocking(self) -> None:
        """Milestone scope must respect explicit config_gate_mode=BLOCKING."""
        result = resolve_gate_mode(
            scope=GateScope.MILESTONE,
            config_gate_mode=GateMode.BLOCKING,
        )
        assert result is GateMode.BLOCKING, (
            f"Milestone-scope gate resolved to {result!r} with "
            "config_gate_mode=BLOCKING"
        )

    def test_milestone_ignores_grace_period(self) -> None:
        """Milestone scope resolution must not be affected by grace_period."""
        result_gp0 = resolve_gate_mode(
            scope=GateScope.MILESTONE,
            config_gate_mode=GateMode.BLOCKING,
            grace_period=0,
        )
        result_gp10 = resolve_gate_mode(
            scope=GateScope.MILESTONE,
            config_gate_mode=GateMode.BLOCKING,
            grace_period=10,
        )
        assert result_gp0 == result_gp10 == GateMode.BLOCKING, (
            "Milestone scope should resolve based on config_gate_mode, "
            f"not grace_period. Got gp=0: {result_gp0!r}, gp=10: {result_gp10!r}"
        )


# ---------------------------------------------------------------------------
# 4. GateScope enum completeness
# ---------------------------------------------------------------------------


class TestGateScopeEnum:
    """Verify that the GateScope enum contains the expected members."""

    def test_scope_members(self) -> None:
        """GateScope must have exactly RELEASE, MILESTONE, TASK."""
        expected = {"RELEASE", "MILESTONE", "TASK"}
        actual = {member.name for member in GateScope}
        assert actual == expected, (
            f"GateScope members mismatch: expected {expected}, got {actual}"
        )

    def test_scope_values(self) -> None:
        """GateScope values must be lowercase strings matching the enum name."""
        for member in GateScope:
            assert member.value == member.name.lower(), (
                f"GateScope.{member.name} has value {member.value!r}, "
                f"expected {member.name.lower()!r}"
            )
