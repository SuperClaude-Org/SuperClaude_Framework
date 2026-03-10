"""Tests for roadmap parallel generate group behavior."""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.executor import execute_pipeline
from superclaude.cli.pipeline.models import (
    GateCriteria,
    Step,
    StepResult,
    StepStatus,
)
from superclaude.cli.roadmap.executor import _build_steps
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig


def _now():
    return datetime.now(timezone.utc)


def _make_config(tmp_path: Path) -> RoadmapConfig:
    spec = tmp_path / "spec.md"
    spec.write_text("# Spec\nContent here.\n")
    output = tmp_path / "output"
    output.mkdir(exist_ok=True)
    return RoadmapConfig(
        spec_file=spec,
        output_dir=output,
        agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
    )


class TestParallelGenerateGroup:
    def test_generate_steps_are_parallel(self, tmp_path):
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        gen_group = steps[1]
        assert isinstance(gen_group, list)
        assert len(gen_group) == 2
        assert gen_group[0].id.startswith("generate-")
        assert gen_group[1].id.startswith("generate-")

    def test_generate_steps_use_different_models(self, tmp_path):
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        gen_group = steps[1]
        assert gen_group[0].model == "opus"
        assert gen_group[1].model == "haiku"

    def test_parallel_generate_runs_on_separate_threads(self, tmp_path):
        config = _make_config(tmp_path)
        gate = GateCriteria(
            required_frontmatter_fields=[],
            min_lines=1,
            enforcement_tier="LIGHT",
        )
        thread_ids = []

        def runner(step, cfg, cancel_check):
            thread_ids.append(threading.current_thread().ident)
            step.output_file.parent.mkdir(parents=True, exist_ok=True)
            step.output_file.write_text("content\n")
            return StepResult(
                step=step, status=StepStatus.PASS, attempt=1,
                gate_failure_reason=None, started_at=_now(), finished_at=_now(),
            )

        par_steps = [
            Step(id="gen-a", prompt="p", output_file=tmp_path / "a.md", gate=gate, timeout_seconds=60),
            Step(id="gen-b", prompt="p", output_file=tmp_path / "b.md", gate=gate, timeout_seconds=60),
        ]

        results = execute_pipeline(steps=[par_steps], config=config, run_step=runner)
        assert len(results) == 2
        assert all(r.status == StepStatus.PASS for r in results)
        assert len(set(thread_ids)) == 2  # Different threads

    def test_parallel_failure_cancels_sibling(self, tmp_path):
        config = _make_config(tmp_path)
        gate = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=5,
            enforcement_tier="STANDARD",
        )

        import time

        def runner(step, cfg, cancel_check):
            if step.id == "gen-fail":
                # Don't write output -> gate fails
                return StepResult(
                    step=step, status=StepStatus.PASS, attempt=1,
                    gate_failure_reason=None, started_at=_now(), finished_at=_now(),
                )
            else:
                time.sleep(0.2)
                if cancel_check():
                    return StepResult(
                        step=step, status=StepStatus.CANCELLED, attempt=1,
                        gate_failure_reason="Cancelled", started_at=_now(), finished_at=_now(),
                    )
                step.output_file.write_text("---\ntitle: T\n---\ncontent\nlines\nmore\n")
                return StepResult(
                    step=step, status=StepStatus.PASS, attempt=1,
                    gate_failure_reason=None, started_at=_now(), finished_at=_now(),
                )

        par_steps = [
            Step(id="gen-fail", prompt="p", output_file=tmp_path / "fail.md", gate=gate, timeout_seconds=60, retry_limit=0),
            Step(id="gen-slow", prompt="p", output_file=tmp_path / "slow.md", gate=gate, timeout_seconds=60),
        ]

        results = execute_pipeline(steps=[par_steps], config=config, run_step=runner)
        statuses = {r.step.id: r.status for r in results}
        assert statuses["gen-fail"] == StepStatus.FAIL

    def test_sequential_step_after_parallel_group(self, tmp_path):
        config = _make_config(tmp_path)
        gate = GateCriteria(
            required_frontmatter_fields=[],
            min_lines=1,
            enforcement_tier="LIGHT",
        )
        execution_order = []

        def runner(step, cfg, cancel_check):
            execution_order.append(step.id)
            step.output_file.parent.mkdir(parents=True, exist_ok=True)
            step.output_file.write_text("content\n")
            return StepResult(
                step=step, status=StepStatus.PASS, attempt=1,
                gate_failure_reason=None, started_at=_now(), finished_at=_now(),
            )

        par_group = [
            Step(id="gen-a", prompt="p", output_file=tmp_path / "a.md", gate=gate, timeout_seconds=60),
            Step(id="gen-b", prompt="p", output_file=tmp_path / "b.md", gate=gate, timeout_seconds=60),
        ]
        seq_step = Step(id="diff", prompt="p", output_file=tmp_path / "d.md", gate=gate, timeout_seconds=60)

        results = execute_pipeline(steps=[par_group, seq_step], config=config, run_step=runner)
        assert len(results) == 3
        assert execution_order.index("diff") > execution_order.index("gen-a")
        assert execution_order.index("diff") > execution_order.index("gen-b")
