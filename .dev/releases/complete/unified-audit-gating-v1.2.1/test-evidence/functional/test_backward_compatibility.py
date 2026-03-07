"""Backward compatibility test for unified-audit-gating v1.2.1.

Invariant under test:
    grace_period=0 produces IDENTICAL behavior to pre-trailing-gate releases.

This means:
    1. GateMode defaults to BLOCKING on the Step dataclass.
    2. PipelineConfig.grace_period defaults to 0.
    3. SprintConfig inherits grace_period=0.
    4. The executor never instantiates TrailingGateRunner when grace_period=0.
    5. No daemon threads are spawned by the executor for gate evaluation.
    6. The executor forces GateMode.BLOCKING even if a step is marked TRAILING.
    7. Gate checks run synchronously (blocking path) at grace_period=0.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.pipeline.models import (
    GateCriteria,
    GateMode,
    PipelineConfig,
    Step,
    StepResult,
    StepStatus,
)
from superclaude.cli.pipeline.executor import execute_pipeline
from superclaude.cli.pipeline.trailing_gate import TrailingGateRunner
from superclaude.cli.sprint.models import SprintConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_step(
    step_id: str,
    gate_mode: GateMode = GateMode.BLOCKING,
    with_gate: bool = True,
) -> Step:
    """Build a minimal Step for testing."""
    gate = GateCriteria(
        required_frontmatter_fields=["title"],
        min_lines=1,
    ) if with_gate else None
    return Step(
        id=step_id,
        prompt=f"Test prompt for {step_id}",
        output_file=Path(f"/tmp/test-{step_id}.md"),
        gate=gate,
        timeout_seconds=30,
        gate_mode=gate_mode,
    )


def _passing_runner(step: Step, config: PipelineConfig, cancel_check) -> StepResult:
    """StepRunner that always returns PASS."""
    now = datetime.now(timezone.utc)
    return StepResult(
        step=step,
        status=StepStatus.PASS,
        attempt=1,
        started_at=now,
        finished_at=now,
    )


# ---------------------------------------------------------------------------
# 1. GateMode defaults to BLOCKING on the Step dataclass
# ---------------------------------------------------------------------------

class TestGateModeDefault:
    """Verify that Step.gate_mode defaults to BLOCKING -- the pre-trailing-gate
    behavior. Any change to this default would silently break all existing
    pipeline definitions that omit gate_mode."""

    def test_step_gate_mode_defaults_to_blocking(self):
        step = Step(
            id="s1",
            prompt="prompt",
            output_file=Path("/tmp/out.md"),
            gate=None,
            timeout_seconds=30,
        )
        assert step.gate_mode == GateMode.BLOCKING, (
            f"Step.gate_mode should default to BLOCKING, got {step.gate_mode}"
        )

    def test_gate_mode_blocking_is_string_blocking(self):
        """Enum value must be the literal string 'BLOCKING'."""
        assert GateMode.BLOCKING.value == "BLOCKING"


# ---------------------------------------------------------------------------
# 2. PipelineConfig and SprintConfig default grace_period=0
# ---------------------------------------------------------------------------

class TestGracePeriodDefaults:
    """Verify both config classes default grace_period to 0."""

    def test_pipeline_config_grace_period_defaults_to_zero(self):
        cfg = PipelineConfig()
        assert cfg.grace_period == 0, (
            f"PipelineConfig.grace_period should default to 0, got {cfg.grace_period}"
        )

    def test_sprint_config_inherits_grace_period_zero(self):
        cfg = SprintConfig()
        assert cfg.grace_period == 0, (
            f"SprintConfig.grace_period should default to 0, got {cfg.grace_period}"
        )

    def test_sprint_config_explicit_zero_matches_default(self):
        cfg = SprintConfig(grace_period=0)
        assert cfg.grace_period == 0


# ---------------------------------------------------------------------------
# 3. No daemon threads spawned at grace_period=0
# ---------------------------------------------------------------------------

class TestNoDaemonThreadsAtGracePeriodZero:
    """The executor must not spawn any daemon threads when grace_period=0.
    Trailing gate evaluation uses daemon threads; their presence at
    grace_period=0 would break the synchronous-only guarantee."""

    def test_no_new_daemon_threads_during_execution(self):
        """Run a pipeline with grace_period=0 and assert no new daemon
        threads appear beyond those present before execution."""
        config = PipelineConfig(grace_period=0)
        steps = [_make_step("s1", with_gate=False)]

        threads_before = {t.ident for t in threading.enumerate() if t.daemon}

        with patch(
            "superclaude.cli.pipeline.executor.gate_passed",
            return_value=(True, None),
        ):
            execute_pipeline(
                steps=steps,
                config=config,
                run_step=_passing_runner,
            )

        threads_after = {t.ident for t in threading.enumerate() if t.daemon}
        new_daemons = threads_after - threads_before
        assert len(new_daemons) == 0, (
            f"Expected 0 new daemon threads at grace_period=0, "
            f"found {len(new_daemons)} new daemon thread(s)"
        )


# ---------------------------------------------------------------------------
# 4. TrailingGateRunner is NOT instantiated at grace_period=0
# ---------------------------------------------------------------------------

class TestNoTrailingGateRunnerAtGracePeriodZero:
    """When grace_period=0 and no external trailing_runner is provided,
    the executor must never construct a TrailingGateRunner."""

    def test_trailing_gate_runner_not_constructed(self):
        config = PipelineConfig(grace_period=0)
        steps = [_make_step("s1", with_gate=False)]

        with patch(
            "superclaude.cli.pipeline.executor.TrailingGateRunner",
            wraps=TrailingGateRunner,
        ) as mock_cls, patch(
            "superclaude.cli.pipeline.executor.gate_passed",
            return_value=(True, None),
        ):
            execute_pipeline(
                steps=steps,
                config=config,
                run_step=_passing_runner,
            )
            mock_cls.assert_not_called(), (
                "TrailingGateRunner should not be instantiated when grace_period=0"
            )

    def test_trailing_gate_runner_constructed_when_grace_period_positive(self):
        """Sanity check: grace_period>0 DOES create a TrailingGateRunner."""
        config = PipelineConfig(grace_period=10)
        steps = [_make_step("s1", with_gate=False)]

        with patch(
            "superclaude.cli.pipeline.executor.TrailingGateRunner",
            wraps=TrailingGateRunner,
        ) as mock_cls, patch(
            "superclaude.cli.pipeline.executor.gate_passed",
            return_value=(True, None),
        ):
            execute_pipeline(
                steps=steps,
                config=config,
                run_step=_passing_runner,
            )
            mock_cls.assert_called_once(), (
                "TrailingGateRunner should be instantiated when grace_period > 0"
            )


# ---------------------------------------------------------------------------
# 5. Executor takes the BLOCKING path when grace_period=0
# ---------------------------------------------------------------------------

class TestExecutorBlockingPathAtGracePeriodZero:
    """Verify the executor evaluates gates synchronously (calls gate_passed
    directly) and does NOT submit to a TrailingGateRunner."""

    def test_gate_passed_called_synchronously(self):
        """gate_passed must be called in-line for a step with a gate
        when grace_period=0, regardless of the step's gate_mode setting."""
        config = PipelineConfig(grace_period=0)
        step = _make_step("s1", gate_mode=GateMode.TRAILING, with_gate=True)

        # Write a minimal file so gate_passed has something to read
        step.output_file.parent.mkdir(parents=True, exist_ok=True)
        step.output_file.write_text("---\ntitle: test\n---\nline1\n")

        with patch(
            "superclaude.cli.pipeline.executor.gate_passed",
            return_value=(True, None),
        ) as mock_gate:
            results = execute_pipeline(
                steps=[step],
                config=config,
                run_step=_passing_runner,
            )
            mock_gate.assert_called_once(), (
                "gate_passed should be called synchronously at grace_period=0"
            )

        assert results[0].status == StepStatus.PASS

    def test_trailing_mode_step_forced_blocking_at_grace_period_zero(self):
        """A step explicitly set to GateMode.TRAILING must be forced to
        BLOCKING when grace_period=0. This is the core backward-compat
        guarantee: grace_period=0 makes TRAILING impossible."""
        config = PipelineConfig(grace_period=0)
        step = _make_step("s1", gate_mode=GateMode.TRAILING, with_gate=True)
        step.output_file.parent.mkdir(parents=True, exist_ok=True)
        step.output_file.write_text("---\ntitle: test\n---\nline1\n")

        submit_calls = []

        with patch(
            "superclaude.cli.pipeline.executor.gate_passed",
            return_value=(True, None),
        ), patch.object(
            TrailingGateRunner, "submit",
            side_effect=lambda s, **kw: submit_calls.append(s),
        ):
            execute_pipeline(
                steps=[step],
                config=config,
                run_step=_passing_runner,
            )

        assert len(submit_calls) == 0, (
            f"TrailingGateRunner.submit should never be called at grace_period=0, "
            f"but was called {len(submit_calls)} time(s)"
        )

    def test_gate_failure_halts_pipeline_at_grace_period_zero(self):
        """At grace_period=0 a gate failure must HALT the pipeline
        (after retries), not defer it. This is blocking behavior."""
        config = PipelineConfig(grace_period=0)
        step = _make_step("s1", gate_mode=GateMode.BLOCKING, with_gate=True)
        step.retry_limit = 0  # no retries -- fail immediately
        step.output_file.parent.mkdir(parents=True, exist_ok=True)
        step.output_file.write_text("---\ntitle: test\n---\nline1\n")

        with patch(
            "superclaude.cli.pipeline.executor.gate_passed",
            return_value=(False, "Intentional test failure"),
        ):
            results = execute_pipeline(
                steps=[step],
                config=config,
                run_step=_passing_runner,
            )

        assert results[0].status == StepStatus.FAIL
        assert results[0].gate_failure_reason == "Intentional test failure"


# ---------------------------------------------------------------------------
# 6. Full integration: multi-step pipeline at grace_period=0
# ---------------------------------------------------------------------------

class TestFullPipelineBackwardCompat:
    """End-to-end: run a multi-step pipeline at grace_period=0 and verify
    all steps execute synchronously with blocking gates, no trailing
    infrastructure activated."""

    def test_multi_step_all_blocking(self):
        config = PipelineConfig(grace_period=0)
        steps = [
            _make_step("step-1", gate_mode=GateMode.BLOCKING, with_gate=True),
            _make_step("step-2", gate_mode=GateMode.TRAILING, with_gate=True),
            _make_step("step-3", gate_mode=GateMode.BLOCKING, with_gate=False),
        ]

        for s in steps:
            if s.gate is not None:
                s.output_file.parent.mkdir(parents=True, exist_ok=True)
                s.output_file.write_text("---\ntitle: test\n---\nline1\n")

        execution_order = []

        def tracking_runner(step, cfg, cancel_check):
            execution_order.append(step.id)
            return _passing_runner(step, cfg, cancel_check)

        with patch(
            "superclaude.cli.pipeline.executor.TrailingGateRunner",
            wraps=TrailingGateRunner,
        ) as mock_cls, patch(
            "superclaude.cli.pipeline.executor.gate_passed",
            return_value=(True, None),
        ):
            results = execute_pipeline(
                steps=steps,
                config=config,
                run_step=tracking_runner,
            )
            mock_cls.assert_not_called()

        assert len(results) == 3
        assert all(r.status == StepStatus.PASS for r in results)
        assert execution_order == ["step-1", "step-2", "step-3"], (
            f"Steps should execute sequentially; got {execution_order}"
        )
