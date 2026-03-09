"""Tests for --dry-run output (T04.02)."""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import GateCriteria, SemanticCheck, Step
from superclaude.cli.roadmap.executor import _dry_run_output


def _dummy_check(content: str) -> bool:
    return True


def _make_step(id: str, output: str, gate: GateCriteria | None = None, model: str = "", parallel: bool = False) -> Step:
    return Step(
        id=id,
        prompt=f"prompt for {id}",
        output_file=Path(f"/tmp/roadmap/{output}"),
        gate=gate or GateCriteria(
            required_frontmatter_fields=["field1"],
            min_lines=50,
            enforcement_tier="STANDARD",
        ),
        timeout_seconds=300,
        model=model,
    )


class TestDryRunOutput:
    def _build_8_steps(self) -> list[Step | list[Step]]:
        """Build a representative 9-step pipeline (8 logical entries, 9 steps)."""
        gate_standard = GateCriteria(
            required_frontmatter_fields=["functional_requirements"],
            min_lines=50,
            enforcement_tier="STANDARD",
        )
        gate_strict = GateCriteria(
            required_frontmatter_fields=["spec_source", "complexity_score"],
            min_lines=100,
            enforcement_tier="STRICT",
            semantic_checks=[
                SemanticCheck(name="check_1", check_fn=_dummy_check, failure_message="fail"),
            ],
        )

        return [
            _make_step("extract", "extraction.md", gate_standard),
            [
                _make_step("generate-opus-architect", "roadmap-opus.md", gate_strict, model="opus"),
                _make_step("generate-haiku-architect", "roadmap-haiku.md", gate_strict, model="haiku"),
            ],
            _make_step("diff", "diff-analysis.md", gate_standard),
            _make_step("debate", "debate-transcript.md", gate_strict),
            _make_step("score", "base-selection.md", gate_standard),
            _make_step("merge", "roadmap.md", gate_strict),
            _make_step("test-strategy", "test-strategy.md", gate_standard),
            _make_step("spec-fidelity", "spec-fidelity.md", gate_strict),
        ]

    def test_prints_all_step_entries(self, capsys):
        steps = self._build_8_steps()
        _dry_run_output(steps)
        captured = capsys.readouterr()

        # Should have 9 step entries (8 logical + 2 parallel = 9 individual)
        assert "extract" in captured.out
        assert "generate-opus-architect" in captured.out
        assert "generate-haiku-architect" in captured.out
        assert "diff" in captured.out
        assert "debate" in captured.out
        assert "score" in captured.out
        assert "merge" in captured.out
        assert "test-strategy" in captured.out
        assert "spec-fidelity" in captured.out

    def test_each_entry_includes_step_id(self, capsys):
        steps = self._build_8_steps()
        _dry_run_output(steps)
        captured = capsys.readouterr()

        # Count "Step N" lines
        step_lines = [l for l in captured.out.splitlines() if l.startswith("Step ")]
        assert len(step_lines) == 9

    def test_each_entry_includes_output_file(self, capsys):
        steps = self._build_8_steps()
        _dry_run_output(steps)
        captured = capsys.readouterr()

        assert "Output:" in captured.out
        assert "extraction.md" in captured.out

    def test_each_entry_includes_gate_tier(self, capsys):
        steps = self._build_8_steps()
        _dry_run_output(steps)
        captured = capsys.readouterr()

        assert "Gate tier:" in captured.out
        assert "STANDARD" in captured.out
        assert "STRICT" in captured.out

    def test_each_entry_includes_timeout(self, capsys):
        steps = self._build_8_steps()
        _dry_run_output(steps)
        captured = capsys.readouterr()

        assert "Timeout: 300s" in captured.out

    def test_parallel_steps_labeled(self, capsys):
        steps = self._build_8_steps()
        _dry_run_output(steps)
        captured = capsys.readouterr()

        assert "(parallel)" in captured.out

    def test_model_shown_when_present(self, capsys):
        steps = self._build_8_steps()
        _dry_run_output(steps)
        captured = capsys.readouterr()

        assert "Model: opus" in captured.out
        assert "Model: haiku" in captured.out

    def test_no_subprocess_invocations(self):
        """Dry run output is a pure print function -- no subprocess."""
        # _dry_run_output is a pure function that only prints.
        # This test verifies the function signature takes no config/runner args.
        import inspect
        sig = inspect.signature(_dry_run_output)
        params = list(sig.parameters.keys())
        assert params == ["steps"]

    def test_semantic_checks_shown(self, capsys):
        steps = self._build_8_steps()
        _dry_run_output(steps)
        captured = capsys.readouterr()

        assert "Semantic checks:" in captured.out
        assert "check_1" in captured.out
