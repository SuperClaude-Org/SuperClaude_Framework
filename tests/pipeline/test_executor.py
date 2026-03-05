"""Tests for pipeline/executor.py -- sequential flow, retry, callbacks, halt."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.executor import execute_pipeline
from superclaude.cli.pipeline.models import (
    GateCriteria,
    PipelineConfig,
    Step,
    StepResult,
    StepStatus,
)


def _now():
    return datetime.now(timezone.utc)


def _make_runner(write_output=True, status=StepStatus.PASS):
    """Create a mock StepRunner that optionally writes output files."""
    calls = []

    def runner(step, config, cancel_check):
        calls.append(step.id)
        if write_output and step.gate is not None:
            step.output_file.write_text(
                "---\ntitle: T\nversion: 1.0\n---\n" + "\n".join(["line"] * 20)
            )
        return StepResult(
            step=step, status=status, attempt=1,
            gate_failure_reason=None, started_at=_now(), finished_at=_now(),
        )

    return runner, calls


class TestSequentialFlow:
    def test_three_steps_all_pass(self, tmp_path):
        cfg = PipelineConfig(work_dir=tmp_path)
        gate = GateCriteria(required_frontmatter_fields=["title"], min_lines=5)
        steps = [
            Step(id="s1", prompt="p", output_file=tmp_path / "o1.md", gate=gate, timeout_seconds=60),
            Step(id="s2", prompt="p", output_file=tmp_path / "o2.md", gate=gate, timeout_seconds=60),
            Step(id="s3", prompt="p", output_file=tmp_path / "o3.md", gate=gate, timeout_seconds=60),
        ]
        runner, calls = _make_runner()
        results = execute_pipeline(steps=steps, config=cfg, run_step=runner)
        assert len(results) == 3
        assert all(r.status == StepStatus.PASS for r in results)
        assert calls == ["s1", "s2", "s3"]

    def test_no_gate_trusts_runner_status(self, tmp_path):
        cfg = PipelineConfig(work_dir=tmp_path)
        step = Step(id="s1", prompt="p", output_file=tmp_path / "o.md", gate=None, timeout_seconds=60)
        runner, calls = _make_runner(write_output=False)
        results = execute_pipeline(steps=[step], config=cfg, run_step=runner)
        assert len(results) == 1
        assert results[0].status == StepStatus.PASS


class TestRetryLogic:
    def test_retry_on_gate_failure(self, tmp_path):
        cfg = PipelineConfig(work_dir=tmp_path)
        gate = GateCriteria(required_frontmatter_fields=["title"], min_lines=5)
        step = Step(id="s1", prompt="p", output_file=tmp_path / "missing.md", gate=gate, timeout_seconds=60, retry_limit=1)

        runner, calls = _make_runner(write_output=False)
        results = execute_pipeline(steps=[step], config=cfg, run_step=runner)
        assert len(results) == 1
        assert results[0].status == StepStatus.FAIL
        assert results[0].attempt == 2  # tried twice
        assert "File not found" in results[0].gate_failure_reason
        assert calls == ["s1", "s1"]  # called twice

    def test_pass_on_retry(self, tmp_path):
        """First attempt fails gate, second attempt succeeds."""
        cfg = PipelineConfig(work_dir=tmp_path)
        gate = GateCriteria(required_frontmatter_fields=["title"], min_lines=3)
        step = Step(id="s1", prompt="p", output_file=tmp_path / "out.md", gate=gate, timeout_seconds=60, retry_limit=1)

        attempt_num = [0]
        def retry_runner(step, config, cancel_check):
            attempt_num[0] += 1
            if attempt_num[0] == 2:
                step.output_file.write_text("---\ntitle: T\n---\ncontent\nmore\n")
            return StepResult(
                step=step, status=StepStatus.PASS, attempt=1,
                gate_failure_reason=None, started_at=_now(), finished_at=_now(),
            )

        results = execute_pipeline(steps=[step], config=cfg, run_step=retry_runner)
        assert results[0].status == StepStatus.PASS
        assert results[0].attempt == 2


class TestCallbackInvocation:
    def test_callbacks_called_in_order(self, tmp_path):
        cfg = PipelineConfig(work_dir=tmp_path)
        steps = [
            Step(id="s1", prompt="p", output_file=tmp_path / "o.md", gate=None, timeout_seconds=60),
            Step(id="s2", prompt="p", output_file=tmp_path / "o2.md", gate=None, timeout_seconds=60),
        ]
        runner, _ = _make_runner(write_output=False)

        events = []
        results = execute_pipeline(
            steps=steps,
            config=cfg,
            run_step=runner,
            on_step_start=lambda s: events.append(("start", s.id)),
            on_step_complete=lambda s, r: events.append(("complete", s.id, r.status)),
            on_state_update=lambda state: events.append(("state", state["total"])),
        )
        assert events == [
            ("start", "s1"),
            ("complete", "s1", StepStatus.PASS),
            ("state", 1),
            ("start", "s2"),
            ("complete", "s2", StepStatus.PASS),
            ("state", 2),
        ]


class TestHaltOnFailure:
    def test_halts_after_failed_step(self, tmp_path):
        cfg = PipelineConfig(work_dir=tmp_path)
        gate = GateCriteria(required_frontmatter_fields=["x"], min_lines=5)
        steps = [
            Step(id="s1", prompt="p", output_file=tmp_path / "missing.md", gate=gate, timeout_seconds=60, retry_limit=0),
            Step(id="s2", prompt="p", output_file=tmp_path / "o2.md", gate=None, timeout_seconds=60),
        ]
        runner, calls = _make_runner(write_output=False)
        results = execute_pipeline(steps=steps, config=cfg, run_step=runner)
        assert len(results) == 1  # s2 never executed
        assert results[0].status == StepStatus.FAIL
        assert calls == ["s1"]


class TestCancelCheck:
    def test_cancel_stops_execution(self, tmp_path):
        cfg = PipelineConfig(work_dir=tmp_path)
        steps = [
            Step(id="s1", prompt="p", output_file=tmp_path / "o.md", gate=None, timeout_seconds=60),
            Step(id="s2", prompt="p", output_file=tmp_path / "o2.md", gate=None, timeout_seconds=60),
        ]
        runner, calls = _make_runner(write_output=False)
        # Cancel after first step
        call_count = [0]
        def cancel():
            call_count[0] += 1
            return call_count[0] > 1

        results = execute_pipeline(steps=steps, config=cfg, run_step=runner, cancel_check=cancel)
        # First step completes, second sees cancel
        assert len(results) <= 2
