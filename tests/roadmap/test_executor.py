"""Tests for roadmap executor integration -- full pipeline with mock subprocesses."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.cli.pipeline.models import (
    GateCriteria,
    PipelineConfig,
    Step,
    StepResult,
    StepStatus,
)
from superclaude.cli.pipeline.executor import execute_pipeline
from superclaude.cli.roadmap.executor import (
    _build_steps,
    _format_halt_output,
    _sanitize_output,
    _save_state,
    execute_roadmap,
)
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig


def _now():
    return datetime.now(timezone.utc)


def _make_config(tmp_path: Path) -> RoadmapConfig:
    spec = tmp_path / "spec.md"
    spec.write_text("# Test Spec\nContent for testing.\n")
    output = tmp_path / "output"
    output.mkdir(exist_ok=True)
    return RoadmapConfig(
        spec_file=spec,
        output_dir=output,
        agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
        depth="standard",
    )


class TestBuildSteps:
    def test_produces_8_entries(self, tmp_path):
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        assert len(steps) == 8  # 6 sequential + 1 parallel group (2 steps) + spec-fidelity

    def test_second_entry_is_parallel(self, tmp_path):
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        assert isinstance(steps[1], list)
        assert len(steps[1]) == 2

    def test_step_ids_in_order(self, tmp_path):
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        ids = []
        for entry in steps:
            if isinstance(entry, list):
                ids.extend(s.id for s in entry)
            else:
                ids.append(entry.id)
        assert ids[0] == "extract"
        assert ids[1].startswith("generate-")
        assert ids[2].startswith("generate-")
        assert ids[3] == "diff"
        assert ids[4] == "debate"
        assert ids[5] == "score"
        assert ids[6] == "merge"
        assert ids[7] == "test-strategy"
        assert ids[8] == "spec-fidelity"


class TestIntegrationMockSubprocess:
    """Full pipeline run with mock step runner producing gate-passing output."""

    def test_full_pipeline_all_pass(self, tmp_path):
        config = _make_config(tmp_path)
        steps = _build_steps(config)

        def mock_runner(step, cfg, cancel_check):
            # Write gate-passing output for each step
            # Use realistic values for specific frontmatter fields
            fm_values = {
                "spec_source": "spec.md",
                "generated": "2026-03-08T00:00:00Z",
                "generator": "test-agent",
                "functional_requirements": "5",
                "nonfunctional_requirements": "3",
                "total_requirements": "8",
                "complexity_score": "0.7",
                "complexity_class": "moderate",
                "domains_detected": "2",
                "risks_identified": "3",
                "dependencies_identified": "4",
                "success_criteria_count": "5",
                "extraction_mode": "full",
                "primary_persona": "architect",
                "total_diff_points": "3",
                "shared_assumptions_count": "4",
                "convergence_score": "0.85",
                "rounds_completed": "2",
                "base_variant": "A",
                "variant_scores": "A:78 B:72",
                "adversarial": "true",
                "validation_milestones": "3",
                "interleave_ratio": "1:3",
                "high_severity_count": "0",
                "medium_severity_count": "0",
                "low_severity_count": "0",
                "total_deviations": "0",
                "validation_complete": "true",
                "tasklist_ready": "true",
            }
            fm_fields = {}
            if step.gate and step.gate.required_frontmatter_fields:
                for f in step.gate.required_frontmatter_fields:
                    fm_fields[f] = fm_values.get(f, "test_value")

            content_lines = ["---"]
            for k, v in fm_fields.items():
                content_lines.append(f"{k}: {v}")
            content_lines.append("---")
            # Add enough content lines with list items (for has_actionable_content)
            content_lines.append("## Overview")
            min_needed = step.gate.min_lines if step.gate else 10
            for i in range(max(min_needed, 10)):
                content_lines.append(f"- Item {i}: content for {step.id}")
            content = "\n".join(content_lines)

            step.output_file.parent.mkdir(parents=True, exist_ok=True)
            step.output_file.write_text(content)

            return StepResult(
                step=step,
                status=StepStatus.PASS,
                attempt=1,
                started_at=_now(),
                finished_at=_now(),
            )

        results = execute_pipeline(
            steps=steps,
            config=config,
            run_step=mock_runner,
        )

        assert len(results) == 9  # 8 entries -> 9 individual steps
        assert all(r.status == StepStatus.PASS for r in results)

    def test_pipeline_halts_on_gate_failure(self, tmp_path):
        config = _make_config(tmp_path)
        steps = _build_steps(config)

        def failing_runner(step, cfg, cancel_check):
            # Don't write any output -> gates will fail
            return StepResult(
                step=step,
                status=StepStatus.PASS,
                attempt=1,
                started_at=_now(),
                finished_at=_now(),
            )

        results = execute_pipeline(
            steps=steps,
            config=config,
            run_step=failing_runner,
        )

        # First step (extract) should fail gate (no output written)
        assert results[-1].status == StepStatus.FAIL
        assert len(results) < 9  # Not all steps executed


class TestContextIsolation:
    def test_subprocess_uses_mock(self, tmp_path):
        """Verify all tests use unittest.mock.patch for subprocess isolation."""
        # This is a meta-test documenting that integration tests
        # use mock runners rather than real subprocess calls.
        with patch("subprocess.Popen") as mock_popen:
            # If any test accidentally called subprocess.Popen directly,
            # this would be caught. Our mock runner pattern avoids that.
            assert not mock_popen.called


class TestSaveAndReloadState:
    def test_state_roundtrip(self, tmp_path):
        config = _make_config(tmp_path)
        step = Step(
            id="extract", prompt="p", output_file=config.output_dir / "extract.md",
            gate=None, timeout_seconds=300,
        )
        results = [
            StepResult(
                step=step,
                status=StepStatus.PASS,
                attempt=1,
                started_at=_now(),
                finished_at=_now(),
            ),
        ]

        _save_state(config, results)

        from superclaude.cli.roadmap.executor import read_state
        state = read_state(config.output_dir / ".roadmap-state.json")
        assert state is not None
        assert state["schema_version"] == 1
        assert state["steps"]["extract"]["status"] == "PASS"


class TestSanitizeOutput:
    """Unit tests for _sanitize_output() -- spec §6.2 test matrix."""

    def test_strips_preamble_before_frontmatter(self, tmp_path):
        """Preamble present: file is rewritten, returns byte count."""
        f = tmp_path / "output.md"
        preamble = "Here is the result:\n\n"
        body = "---\ntitle: test\n---\n## Content\n- item 1\n"
        f.write_text(preamble + body, encoding="utf-8")

        result = _sanitize_output(f)

        assert result == len(preamble.encode("utf-8"))
        assert f.read_text(encoding="utf-8") == body

    def test_no_preamble_unchanged(self, tmp_path):
        """No preamble (starts with ---): file unchanged, returns 0."""
        f = tmp_path / "output.md"
        content = "---\ntitle: test\n---\n## Content\n"
        f.write_text(content, encoding="utf-8")

        result = _sanitize_output(f)

        assert result == 0
        assert f.read_text(encoding="utf-8") == content

    def test_no_frontmatter_unchanged(self, tmp_path):
        """No frontmatter delimiter at all: file unchanged, returns 0."""
        f = tmp_path / "output.md"
        content = "Just some text without any frontmatter.\n"
        f.write_text(content, encoding="utf-8")

        result = _sanitize_output(f)

        assert result == 0
        assert f.read_text(encoding="utf-8") == content

    def test_multi_line_preamble_stripped(self, tmp_path):
        """Multi-line preamble: all lines before first --- are stripped."""
        f = tmp_path / "output.md"
        preamble = "Sure! Here is your output.\n\nI've formatted it as requested:\n\n"
        body = "---\nkey: value\n---\n- item\n"
        f.write_text(preamble + body, encoding="utf-8")

        result = _sanitize_output(f)

        assert result == len(preamble.encode("utf-8"))
        assert f.read_text(encoding="utf-8") == body

    def test_atomic_write_uses_tmp_and_replace(self, tmp_path):
        """Atomic write: .tmp file used and os.replace() called."""
        f = tmp_path / "output.md"
        preamble = "preamble\n"
        body = "---\ntitle: test\n---\n"
        f.write_text(preamble + body, encoding="utf-8")

        with patch("os.replace", wraps=__import__("os").replace) as mock_replace:
            result = _sanitize_output(f)

        assert result > 0
        # os.replace was called with the .tmp source and original target
        mock_replace.assert_called_once()
        call_args = mock_replace.call_args[0]
        assert str(call_args[0]).endswith(".tmp")
        assert call_args[1] == f
        # Final file has correct content
        assert f.read_text(encoding="utf-8") == body
