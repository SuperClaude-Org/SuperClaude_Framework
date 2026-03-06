"""Tests for --resume with stale spec SHA-256 detection and skip-completed logic (T04.01)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from superclaude.cli.pipeline.models import GateCriteria, Step, StepStatus
from superclaude.cli.roadmap.executor import _apply_resume, read_state, write_state
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig


def _make_step(id: str, output_file: Path, gate: GateCriteria | None = None) -> Step:
    return Step(
        id=id,
        prompt=f"prompt for {id}",
        output_file=output_file,
        gate=gate,
        timeout_seconds=300,
    )


def _make_gate() -> GateCriteria:
    return GateCriteria(
        required_frontmatter_fields=[],
        min_lines=1,
        enforcement_tier="LIGHT",
    )


@pytest.fixture
def tmp_dir(tmp_path):
    """Create a temporary spec file and output directory."""
    spec = tmp_path / "spec.md"
    spec.write_text("# Spec\nSome content here\n")
    return tmp_path, spec


class TestResumeClean:
    """Resume where some steps pass gates, others don't."""

    def test_skips_completed_steps(self, tmp_dir, capsys):
        tmp_path, spec = tmp_dir
        output = tmp_path / "output"
        output.mkdir()

        gate = _make_gate()

        # Create output files for steps that should pass
        extract_out = output / "extraction.md"
        extract_out.write_text("some content\n")

        gen_a_out = output / "gen-a.md"
        gen_a_out.write_text("gen a content\n")

        gen_b_out = output / "gen-b.md"
        gen_b_out.write_text("gen b content\n")

        # diff output doesn't exist - should fail gate
        diff_out = output / "diff.md"

        steps = [
            _make_step("extract", extract_out, gate),
            [
                _make_step("generate-a", gen_a_out, gate),
                _make_step("generate-b", gen_b_out, gate),
            ],
            _make_step("diff", diff_out, gate),
            _make_step("debate", output / "debate.md", gate),
        ]

        config = RoadmapConfig(
            spec_file=spec,
            output_dir=output,
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
        )

        def gate_fn(output_file, criteria):
            return (output_file.exists(), None if output_file.exists() else "not found")

        result = _apply_resume(steps, config, gate_fn)

        # extract and generate group should be skipped, diff onward should remain
        step_ids = []
        for entry in result:
            if isinstance(entry, list):
                step_ids.extend(s.id for s in entry)
            else:
                step_ids.append(entry.id)

        assert "extract" not in step_ids
        assert "generate-a" not in step_ids
        assert "generate-b" not in step_ids
        assert "diff" in step_ids
        assert "debate" in step_ids

    def test_nothing_to_do_when_all_pass(self, tmp_dir, capsys):
        tmp_path, spec = tmp_dir
        output = tmp_path / "output"
        output.mkdir()

        gate = _make_gate()
        out = output / "out.md"
        out.write_text("content\n")

        steps = [_make_step("extract", out, gate)]
        config = RoadmapConfig(spec_file=spec, output_dir=output)

        def gate_fn(output_file, criteria):
            return (True, None)

        result = _apply_resume(steps, config, gate_fn)
        assert result == []
        captured = capsys.readouterr()
        assert "Nothing to do" in captured.out


class TestResumeStaleSpec:
    """Resume with stale spec SHA-256 detection."""

    def test_stale_spec_forces_extract_rerun(self, tmp_dir, capsys):
        tmp_path, spec = tmp_dir
        output = tmp_path / "output"
        output.mkdir()

        # Write a state file with a different spec hash
        state = {
            "schema_version": 1,
            "spec_hash": "deadbeef" * 8,  # wrong hash
        }
        write_state(state, output / ".roadmap-state.json")

        gate = _make_gate()
        extract_out = output / "extraction.md"
        extract_out.write_text("content\n")
        diff_out = output / "diff.md"
        diff_out.write_text("content\n")

        steps = [
            _make_step("extract", extract_out, gate),
            _make_step("diff", diff_out, gate),
        ]

        config = RoadmapConfig(spec_file=spec, output_dir=output)

        def gate_fn(output_file, criteria):
            return (True, None)

        result = _apply_resume(steps, config, gate_fn)

        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "spec-file has changed" in captured.err

        # Extract should be forced to re-run
        step_ids = [s.id for s in result if not isinstance(s, list)]
        assert "extract" in step_ids

    def test_matching_hash_allows_skip(self, tmp_dir, capsys):
        tmp_path, spec = tmp_dir
        output = tmp_path / "output"
        output.mkdir()

        # Write state with correct hash
        current_hash = hashlib.sha256(spec.read_bytes()).hexdigest()
        state = {"schema_version": 1, "spec_hash": current_hash}
        write_state(state, output / ".roadmap-state.json")

        gate = _make_gate()
        extract_out = output / "extraction.md"
        extract_out.write_text("content\n")

        steps = [_make_step("extract", extract_out, gate)]
        config = RoadmapConfig(spec_file=spec, output_dir=output)

        def gate_fn(output_file, criteria):
            return (True, None)

        result = _apply_resume(steps, config, gate_fn)
        assert result == []
        captured = capsys.readouterr()
        assert "WARNING" not in captured.err


class TestResumeMissingState:
    """Resume when no state file exists."""

    def test_full_run_with_no_state_file(self, tmp_dir, capsys):
        tmp_path, spec = tmp_dir
        output = tmp_path / "output"
        output.mkdir()

        gate = _make_gate()
        steps = [
            _make_step("extract", output / "e.md", gate),
            _make_step("diff", output / "d.md", gate),
        ]
        config = RoadmapConfig(spec_file=spec, output_dir=output)

        def gate_fn(output_file, criteria):
            return (False, "not found")

        result = _apply_resume(steps, config, gate_fn)
        # All steps should be included since none pass gates
        step_ids = [s.id for s in result if not isinstance(s, list)]
        assert "extract" in step_ids
        assert "diff" in step_ids
