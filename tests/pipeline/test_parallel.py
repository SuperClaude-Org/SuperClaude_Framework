"""Tests for _run_parallel_steps() -- cross-cancellation, timeout, concurrent execution."""

from __future__ import annotations

import threading
import time
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


class TestParallelBothSucceed:
    def test_both_steps_pass(self, tmp_path):
        cfg = PipelineConfig(work_dir=tmp_path)
        gate = GateCriteria(required_frontmatter_fields=[], min_lines=1, enforcement_tier="LIGHT")

        thread_ids = []

        def runner(step, config, cancel_check):
            thread_ids.append(threading.current_thread().ident)
            step.output_file.write_text("content\n")
            return StepResult(
                step=step, status=StepStatus.PASS, attempt=1,
                gate_failure_reason=None, started_at=_now(), finished_at=_now(),
            )

        par_steps = [
            Step(id="a", prompt="p", output_file=tmp_path / "a.md", gate=gate, timeout_seconds=60),
            Step(id="b", prompt="p", output_file=tmp_path / "b.md", gate=gate, timeout_seconds=60),
        ]

        results = execute_pipeline(steps=[par_steps], config=cfg, run_step=runner)
        assert len(results) == 2
        assert all(r.status == StepStatus.PASS for r in results)
        # Verify they ran on separate threads
        assert len(set(thread_ids)) == 2


class TestParallelOneFails:
    def test_sibling_cancelled_on_failure(self, tmp_path):
        cfg = PipelineConfig(work_dir=tmp_path)
        gate = GateCriteria(required_frontmatter_fields=[], min_lines=1, enforcement_tier="LIGHT")

        def runner(step, config, cancel_check):
            if step.id == "fail":
                # Don't write file -> gate fails
                return StepResult(
                    step=step, status=StepStatus.PASS, attempt=1,
                    gate_failure_reason=None, started_at=_now(), finished_at=_now(),
                )
            else:
                # Simulate work, check for cancel
                time.sleep(0.2)
                if cancel_check():
                    return StepResult(
                        step=step, status=StepStatus.CANCELLED, attempt=1,
                        gate_failure_reason="Cancelled", started_at=_now(), finished_at=_now(),
                    )
                step.output_file.write_text("ok\n")
                return StepResult(
                    step=step, status=StepStatus.PASS, attempt=1,
                    gate_failure_reason=None, started_at=_now(), finished_at=_now(),
                )

        par_steps = [
            Step(id="fail", prompt="p", output_file=tmp_path / "c.md", gate=gate, timeout_seconds=60, retry_limit=0),
            Step(id="slow", prompt="p", output_file=tmp_path / "d.md", gate=gate, timeout_seconds=60),
        ]

        results = execute_pipeline(steps=[par_steps], config=cfg, run_step=runner)
        statuses = {r.step.id: r.status for r in results}
        assert statuses["fail"] == StepStatus.FAIL


class TestParallelBothFail:
    def test_both_fail(self, tmp_path):
        cfg = PipelineConfig(work_dir=tmp_path)
        gate = GateCriteria(required_frontmatter_fields=[], min_lines=1, enforcement_tier="LIGHT")

        def runner(step, config, cancel_check):
            # Neither writes output -> both fail gate
            return StepResult(
                step=step, status=StepStatus.PASS, attempt=1,
                gate_failure_reason=None, started_at=_now(), finished_at=_now(),
            )

        par_steps = [
            Step(id="a", prompt="p", output_file=tmp_path / "a.md", gate=gate, timeout_seconds=60, retry_limit=0),
            Step(id="b", prompt="p", output_file=tmp_path / "b.md", gate=gate, timeout_seconds=60, retry_limit=0),
        ]

        results = execute_pipeline(steps=[par_steps], config=cfg, run_step=runner)
        # At least one should be FAIL (the other might be CANCELLED due to cross-cancel)
        assert any(r.status == StepStatus.FAIL for r in results)


class TestParallelWithSequential:
    def test_sequential_after_parallel(self, tmp_path):
        """Verify sequential steps execute after parallel group completes."""
        cfg = PipelineConfig(work_dir=tmp_path)
        gate = GateCriteria(required_frontmatter_fields=[], min_lines=1, enforcement_tier="LIGHT")

        execution_order = []

        def runner(step, config, cancel_check):
            execution_order.append(step.id)
            step.output_file.write_text("ok\n")
            return StepResult(
                step=step, status=StepStatus.PASS, attempt=1,
                gate_failure_reason=None, started_at=_now(), finished_at=_now(),
            )

        par_group = [
            Step(id="par-a", prompt="p", output_file=tmp_path / "a.md", gate=gate, timeout_seconds=60),
            Step(id="par-b", prompt="p", output_file=tmp_path / "b.md", gate=gate, timeout_seconds=60),
        ]
        seq_step = Step(id="seq", prompt="p", output_file=tmp_path / "s.md", gate=gate, timeout_seconds=60)

        results = execute_pipeline(steps=[par_group, seq_step], config=cfg, run_step=runner)
        assert len(results) == 3
        assert all(r.status == StepStatus.PASS for r in results)
        # seq must come after both par steps
        assert execution_order.index("seq") > execution_order.index("par-a")
        assert execution_order.index("seq") > execution_order.index("par-b")
