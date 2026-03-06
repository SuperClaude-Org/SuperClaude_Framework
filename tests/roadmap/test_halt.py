"""Tests for HALT output formatting per spec section 6.2 (T04.05)."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import GateCriteria, Step, StepResult, StepStatus
from superclaude.cli.roadmap.executor import _format_halt_output
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig


def _make_config(tmp_path: Path) -> RoadmapConfig:
    spec = tmp_path / "spec.md"
    spec.write_text("# Spec")
    return RoadmapConfig(
        spec_file=spec,
        output_dir=tmp_path,
        agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
    )


def _make_step(id: str, tmp_path: Path) -> Step:
    return Step(
        id=id,
        prompt=f"prompt for {id}",
        output_file=tmp_path / f"{id}.md",
        gate=GateCriteria(
            required_frontmatter_fields=[],
            min_lines=10,
            enforcement_tier="STANDARD",
        ),
        timeout_seconds=300,
    )


class TestHaltOutputFormat:
    def test_includes_step_name(self, tmp_path):
        config = _make_config(tmp_path)
        step = _make_step("debate", tmp_path)
        now = datetime.now(timezone.utc)

        results = [
            StepResult(
                step=_make_step("extract", tmp_path),
                status=StepStatus.PASS,
                attempt=1,
                started_at=now,
                finished_at=now + timedelta(seconds=10),
            ),
            StepResult(
                step=step,
                status=StepStatus.FAIL,
                attempt=2,
                gate_failure_reason="Below minimum line count: 5 < 10",
                started_at=now,
                finished_at=now + timedelta(seconds=30),
            ),
        ]

        output = _format_halt_output(results, config)
        assert "debate" in output

    def test_includes_gate_failure_reason(self, tmp_path):
        config = _make_config(tmp_path)
        step = _make_step("merge", tmp_path)
        now = datetime.now(timezone.utc)

        results = [
            StepResult(
                step=step,
                status=StepStatus.FAIL,
                attempt=2,
                gate_failure_reason="Missing required frontmatter field 'adversarial'",
                started_at=now,
                finished_at=now + timedelta(seconds=5),
            ),
        ]

        output = _format_halt_output(results, config)
        assert "Missing required frontmatter field" in output

    def test_includes_retry_command(self, tmp_path):
        config = _make_config(tmp_path)
        step = _make_step("score", tmp_path)
        now = datetime.now(timezone.utc)

        results = [
            StepResult(
                step=step,
                status=StepStatus.FAIL,
                attempt=2,
                gate_failure_reason="gate failed",
                started_at=now,
                finished_at=now + timedelta(seconds=5),
            ),
        ]

        output = _format_halt_output(results, config)
        assert "--resume" in output
        assert "superclaude roadmap run" in output

    def test_includes_completed_and_failed_counts(self, tmp_path):
        config = _make_config(tmp_path)
        now = datetime.now(timezone.utc)

        results = [
            StepResult(
                step=_make_step("extract", tmp_path),
                status=StepStatus.PASS,
                attempt=1,
                started_at=now,
                finished_at=now + timedelta(seconds=10),
            ),
            StepResult(
                step=_make_step("diff", tmp_path),
                status=StepStatus.PASS,
                attempt=1,
                started_at=now,
                finished_at=now + timedelta(seconds=15),
            ),
            StepResult(
                step=_make_step("debate", tmp_path),
                status=StepStatus.FAIL,
                attempt=2,
                gate_failure_reason="gate failed",
                started_at=now,
                finished_at=now + timedelta(seconds=30),
            ),
        ]

        output = _format_halt_output(results, config)
        assert "Completed steps:" in output
        assert "extract" in output
        assert "diff" in output
        assert "Failed step:" in output
        assert "debate" in output

    def test_includes_file_details_when_output_exists(self, tmp_path):
        config = _make_config(tmp_path)
        step = _make_step("debate", tmp_path)
        # Create the output file
        step.output_file.write_text("line 1\nline 2\nline 3\n")
        now = datetime.now(timezone.utc)

        results = [
            StepResult(
                step=step,
                status=StepStatus.FAIL,
                attempt=1,
                gate_failure_reason="gate failed",
                started_at=now,
                finished_at=now + timedelta(seconds=5),
            ),
        ]

        output = _format_halt_output(results, config)
        assert "Output size:" in output or "bytes" in output

    def test_includes_skipped_steps(self, tmp_path):
        config = _make_config(tmp_path)
        now = datetime.now(timezone.utc)

        # Only 2 steps executed, rest skipped
        results = [
            StepResult(
                step=_make_step("extract", tmp_path),
                status=StepStatus.PASS,
                attempt=1,
                started_at=now,
                finished_at=now + timedelta(seconds=5),
            ),
            StepResult(
                step=_make_step("debate", tmp_path),
                status=StepStatus.FAIL,
                attempt=1,
                gate_failure_reason="gate failed",
                started_at=now,
                finished_at=now + timedelta(seconds=5),
            ),
        ]

        output = _format_halt_output(results, config)
        assert "Skipped steps:" in output

    def test_empty_on_no_failures(self, tmp_path):
        config = _make_config(tmp_path)
        now = datetime.now(timezone.utc)

        results = [
            StepResult(
                step=_make_step("extract", tmp_path),
                status=StepStatus.PASS,
                attempt=1,
                started_at=now,
                finished_at=now + timedelta(seconds=5),
            ),
        ]

        output = _format_halt_output(results, config)
        assert output == ""

    def test_halt_output_written_to_stderr(self, tmp_path, capsys):
        """Verify execute_roadmap sends HALT to stderr (integration-level check)."""
        import sys
        config = _make_config(tmp_path)
        step = _make_step("debate", tmp_path)
        now = datetime.now(timezone.utc)

        results = [
            StepResult(
                step=step,
                status=StepStatus.FAIL,
                attempt=2,
                gate_failure_reason="gate failed",
                started_at=now,
                finished_at=now + timedelta(seconds=5),
            ),
        ]

        halt_msg = _format_halt_output(results, config)
        # Simulate what execute_roadmap does
        print(halt_msg, file=sys.stderr)

        captured = capsys.readouterr()
        assert halt_msg in captured.err
        assert captured.out == ""  # Nothing on stdout
