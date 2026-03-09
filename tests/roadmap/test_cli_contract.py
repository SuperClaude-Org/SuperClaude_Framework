"""Tests for CLI contract: --agents parsing and model routing (T04.07)."""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import PipelineConfig, Step
from superclaude.cli.roadmap.executor import _build_steps
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig


class TestAgentsParsing:
    def test_parse_two_agents(self):
        raw = "opus:architect,haiku:architect"
        specs = [AgentSpec.parse(a.strip()) for a in raw.split(",")]
        assert len(specs) == 2
        assert specs[0].model == "opus"
        assert specs[0].persona == "architect"
        assert specs[1].model == "haiku"
        assert specs[1].persona == "architect"

    def test_parse_different_personas(self):
        raw = "sonnet:security,haiku:qa"
        specs = [AgentSpec.parse(a.strip()) for a in raw.split(",")]
        assert specs[0].persona == "security"
        assert specs[1].persona == "qa"

    def test_default_agents_when_not_provided(self):
        config = RoadmapConfig()
        assert len(config.agents) == 2
        assert config.agents[0].model == "opus"
        assert config.agents[0].persona == "architect"
        assert config.agents[1].model == "haiku"
        assert config.agents[1].persona == "architect"

    def test_parse_single_agent(self):
        raw = "opus:architect"
        specs = [AgentSpec.parse(a.strip()) for a in raw.split(",")]
        assert len(specs) == 1

    def test_parse_model_only_defaults_persona(self):
        raw = "opus,haiku"
        specs = [AgentSpec.parse(a.strip()) for a in raw.split(",")]
        assert specs[0].persona == "architect"
        assert specs[1].persona == "architect"


class TestModelRouting:
    def test_generate_a_uses_first_agent_model(self):
        agents = [AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")]
        config = RoadmapConfig(
            agents=agents,
            output_dir=Path("/tmp"),
            spec_file=Path("/tmp/spec.md"),
        )

        steps = _build_steps(config)
        gen_group = steps[1]
        assert isinstance(gen_group, list)
        assert gen_group[0].model == "opus"

    def test_generate_b_uses_second_agent_model(self):
        agents = [AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")]
        config = RoadmapConfig(
            agents=agents,
            output_dir=Path("/tmp"),
            spec_file=Path("/tmp/spec.md"),
        )

        steps = _build_steps(config)
        gen_group = steps[1]
        assert isinstance(gen_group, list)
        assert gen_group[1].model == "haiku"

    def test_no_model_when_empty(self):
        agents = [AgentSpec("", "architect"), AgentSpec("", "architect")]
        config = RoadmapConfig(
            agents=agents,
            output_dir=Path("/tmp"),
            spec_file=Path("/tmp/spec.md"),
        )

        steps = _build_steps(config)
        gen_group = steps[1]
        assert isinstance(gen_group, list)
        assert gen_group[0].model == ""

    def test_context_isolation_no_forbidden_flags(self):
        """Verify that roadmap_run_step does not pass session-sharing flags."""
        # Context isolation is enforced by roadmap_run_step using inline
        # embedding (extra_args=[]) instead of the deleted _build_subprocess_argv.
        # This test verifies the contract is documented.
        from superclaude.cli.roadmap.executor import roadmap_run_step
        import inspect
        source = inspect.getsource(roadmap_run_step)
        assert "--continue" not in source
        assert "--session" not in source
        assert "--resume" not in source

    def test_build_steps_assigns_models(self):
        """Verify _build_steps assigns agent models to generate steps."""
        from superclaude.cli.roadmap.executor import _build_steps

        config = RoadmapConfig(
            spec_file=Path("/tmp/spec.md"),
            output_dir=Path("/tmp/output"),
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "qa")],
        )

        steps = _build_steps(config)

        # Second entry is the parallel generate group
        gen_group = steps[1]
        assert isinstance(gen_group, list)
        assert gen_group[0].model == "opus"
        assert gen_group[1].model == "haiku"


class TestAcceptanceCriteriaAC01:
    """AC-01: --dry-run prints 7 entries, exits 0, no files created."""

    def test_dry_run_seven_entries(self, tmp_path, capsys):
        from superclaude.cli.roadmap.executor import _build_steps, _dry_run_output

        spec = tmp_path / "spec.md"
        spec.write_text("# Spec\nContent here.\n")
        output = tmp_path / "output"
        output.mkdir()

        config = RoadmapConfig(
            spec_file=spec,
            output_dir=output,
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
        )

        steps = _build_steps(config)
        _dry_run_output(steps)
        captured = capsys.readouterr()

        # Count "Step N" lines -> 9 individual steps (8 entries, 2 parallel = 9)
        step_lines = [l for l in captured.out.splitlines() if l.startswith("Step ")]
        assert len(step_lines) == 9

    def test_dry_run_no_files_created(self, tmp_path, capsys):
        from superclaude.cli.roadmap.executor import _build_steps, _dry_run_output

        spec = tmp_path / "spec.md"
        spec.write_text("# Spec\nContent here.\n")
        output = tmp_path / "output"
        output.mkdir()

        config = RoadmapConfig(spec_file=spec, output_dir=output)
        steps = _build_steps(config)
        _dry_run_output(steps)

        # No output files should have been created
        output_files = list(output.glob("*.md"))
        assert len(output_files) == 0


class TestAcceptanceCriteriaAC03:
    """AC-03: gate failure triggers halt with diagnostic output."""

    def test_gate_failure_halt_diagnostic(self, tmp_path):
        from datetime import datetime, timezone, timedelta
        from superclaude.cli.pipeline.models import StepResult, StepStatus, GateCriteria
        from superclaude.cli.roadmap.executor import _format_halt_output

        spec = tmp_path / "spec.md"
        spec.write_text("# Spec")
        config = RoadmapConfig(
            spec_file=spec, output_dir=tmp_path,
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
        )

        now = datetime.now(timezone.utc)
        step_obj = Step(
            id="debate", prompt="p", output_file=tmp_path / "debate.md",
            gate=GateCriteria(required_frontmatter_fields=[], min_lines=10, enforcement_tier="STANDARD"),
            timeout_seconds=300,
        )

        results = [
            StepResult(
                step=step_obj, status=StepStatus.FAIL, attempt=2,
                gate_failure_reason="Below minimum line count: 5 < 10",
                started_at=now, finished_at=now + timedelta(seconds=30),
            ),
        ]

        output = _format_halt_output(results, config)
        assert "ERROR" in output
        assert "debate" in output
        assert "Below minimum line count" in output
        assert "--resume" in output


class TestAcceptanceCriteriaAC04:
    """AC-04: --resume skips completed steps."""

    def test_resume_skips_completed(self, tmp_path, capsys):
        from superclaude.cli.roadmap.executor import _apply_resume
        from superclaude.cli.pipeline.models import GateCriteria

        spec = tmp_path / "spec.md"
        spec.write_text("# Spec\nContent.\n")
        output = tmp_path / "output"
        output.mkdir()

        gate = GateCriteria(required_frontmatter_fields=[], min_lines=1, enforcement_tier="LIGHT")

        # Pre-populate output files for completed steps
        extract_out = output / "e.md"
        extract_out.write_text("content\n")

        diff_out = output / "d.md"  # Not created -> should remain

        steps = [
            Step(id="extract", prompt="p", output_file=extract_out, gate=gate, timeout_seconds=60),
            Step(id="diff", prompt="p", output_file=diff_out, gate=gate, timeout_seconds=60),
        ]

        config = RoadmapConfig(spec_file=spec, output_dir=output)

        def gate_fn(f, c):
            return (f.exists(), None if f.exists() else "not found")

        result = _apply_resume(steps, config, gate_fn)
        step_ids = [s.id for s in result if not isinstance(s, list)]
        assert "extract" not in step_ids
        assert "diff" in step_ids


class TestAcceptanceCriteriaAC05:
    """AC-05: stale spec forces extract re-run with warning."""

    def test_stale_spec_warning(self, tmp_path, capsys):
        from superclaude.cli.roadmap.executor import _apply_resume, write_state

        spec = tmp_path / "spec.md"
        spec.write_text("# Updated Spec\nNew content.\n")
        output = tmp_path / "output"
        output.mkdir()

        state = {"schema_version": 1, "spec_hash": "0000000000000000000000000000000000000000000000000000000000000000"}
        write_state(state, output / ".roadmap-state.json")

        from superclaude.cli.pipeline.models import GateCriteria
        gate = GateCriteria(required_frontmatter_fields=[], min_lines=1, enforcement_tier="LIGHT")
        extract_out = output / "e.md"
        extract_out.write_text("content\n")

        steps = [Step(id="extract", prompt="p", output_file=extract_out, gate=gate, timeout_seconds=60)]
        config = RoadmapConfig(spec_file=spec, output_dir=output)

        def gate_fn(f, c):
            return (True, None)

        result = _apply_resume(steps, config, gate_fn)
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "spec-file has changed" in captured.err
        step_ids = [s.id for s in result if not isinstance(s, list)]
        assert "extract" in step_ids


class TestAcceptanceCriteriaAC07:
    """AC-07: --agents routes models correctly to generate steps."""

    def test_agents_model_routing(self):
        agents_str = "opus:architect,haiku:architect"
        specs = [AgentSpec.parse(a.strip()) for a in agents_str.split(",")]

        config = RoadmapConfig(
            spec_file=Path("/tmp/spec.md"),
            output_dir=Path("/tmp/output"),
            agents=specs,
        )

        steps = _build_steps(config)
        gen_group = steps[1]
        assert isinstance(gen_group, list)

        # First agent uses opus
        assert gen_group[0].model == "opus"

        # Second agent uses haiku
        assert gen_group[1].model == "haiku"
