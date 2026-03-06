"""Tests for progress display callbacks (T04.03)."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import Step, StepResult, StepStatus
from superclaude.cli.roadmap.executor import _print_step_start, _print_step_complete


def _make_step(id: str) -> Step:
    return Step(
        id=id,
        prompt=f"prompt for {id}",
        output_file=Path(f"/tmp/{id}.md"),
        gate=None,
        timeout_seconds=300,
    )


class TestPrintStepStart:
    def test_prints_step_id(self, capsys):
        step = _make_step("extract")
        _print_step_start(step)
        captured = capsys.readouterr()
        assert "extract" in captured.out
        assert "[roadmap]" in captured.out

    def test_prints_for_parallel_steps(self, capsys):
        step_a = _make_step("generate-opus-architect")
        step_b = _make_step("generate-haiku-architect")
        _print_step_start(step_a)
        _print_step_start(step_b)
        captured = capsys.readouterr()
        assert "generate-opus-architect" in captured.out
        assert "generate-haiku-architect" in captured.out


class TestPrintStepComplete:
    def test_pass_status_shown(self, capsys):
        step = _make_step("extract")
        now = datetime.now(timezone.utc)
        result = StepResult(
            step=step,
            status=StepStatus.PASS,
            attempt=1,
            started_at=now,
            finished_at=now + timedelta(seconds=42),
        )
        _print_step_complete(step, result)
        captured = capsys.readouterr()
        assert "PASS" in captured.out
        assert "extract" in captured.out

    def test_fail_status_shown(self, capsys):
        step = _make_step("debate")
        now = datetime.now(timezone.utc)
        result = StepResult(
            step=step,
            status=StepStatus.FAIL,
            attempt=2,
            gate_failure_reason="Below minimum line count",
            started_at=now,
            finished_at=now + timedelta(seconds=10),
        )
        _print_step_complete(step, result)
        captured = capsys.readouterr()
        assert "FAIL" in captured.out
        assert "debate" in captured.out
        assert "Below minimum line count" in captured.out

    def test_attempt_count_shown(self, capsys):
        step = _make_step("merge")
        now = datetime.now(timezone.utc)
        result = StepResult(
            step=step,
            status=StepStatus.PASS,
            attempt=2,
            started_at=now,
            finished_at=now + timedelta(seconds=5),
        )
        _print_step_complete(step, result)
        captured = capsys.readouterr()
        assert "attempt 2" in captured.out

    def test_elapsed_time_shown(self, capsys):
        step = _make_step("extract")
        now = datetime.now(timezone.utc)
        result = StepResult(
            step=step,
            status=StepStatus.PASS,
            attempt=1,
            started_at=now,
            finished_at=now + timedelta(seconds=120),
        )
        _print_step_complete(step, result)
        captured = capsys.readouterr()
        assert "120s" in captured.out

    def test_timeout_status_shown(self, capsys):
        step = _make_step("score")
        now = datetime.now(timezone.utc)
        result = StepResult(
            step=step,
            status=StepStatus.TIMEOUT,
            attempt=1,
            gate_failure_reason="Step timed out after 300s",
            started_at=now,
            finished_at=now + timedelta(seconds=300),
        )
        _print_step_complete(step, result)
        captured = capsys.readouterr()
        assert "TIMEOUT" in captured.out
        assert "score" in captured.out


class TestProgressCallbackProtocol:
    """Verify callbacks are compatible with execute_pipeline signature."""

    def test_callbacks_compatible_with_pipeline(self):
        from superclaude.cli.pipeline.executor import execute_pipeline
        import inspect

        sig = inspect.signature(execute_pipeline)
        params = sig.parameters

        # on_step_start expects Callable[[Step], None]
        assert "on_step_start" in params
        # on_step_complete expects Callable[[Step, StepResult], None]
        assert "on_step_complete" in params

    def test_step_start_accepts_step(self):
        step = _make_step("test")
        # Should not raise
        _print_step_start(step)

    def test_step_complete_accepts_step_and_result(self):
        step = _make_step("test")
        now = datetime.now(timezone.utc)
        result = StepResult(
            step=step,
            status=StepStatus.PASS,
            attempt=1,
            started_at=now,
            finished_at=now,
        )
        # Should not raise
        _print_step_complete(step, result)
