"""Tests for tasklist CLI contract -- help text, exit codes, module structure.

Covers T04.03 acceptance criteria:
- superclaude tasklist validate --help renders with all option descriptions
- CLI exits 1 on HIGH-severity deviations
- Output written to {output_dir}/tasklist-fidelity.md
- Module structure verified
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from superclaude.cli.main import main
from superclaude.cli.tasklist.commands import tasklist_group, validate
from superclaude.cli.tasklist.executor import (
    _build_steps,
    _collect_tasklist_files,
    _has_high_severity,
)
from superclaude.cli.tasklist.gates import TASKLIST_FIDELITY_GATE
from superclaude.cli.tasklist.models import TasklistValidateConfig


class TestTasklistCLIHelp:
    """superclaude tasklist validate --help renders correctly."""

    def test_tasklist_group_help(self):
        runner = CliRunner()
        result = runner.invoke(tasklist_group, ["--help"])
        assert result.exit_code == 0
        assert "validate" in result.output

    def test_validate_help_renders(self):
        runner = CliRunner()
        result = runner.invoke(tasklist_group, ["validate", "--help"])
        assert result.exit_code == 0

    def test_validate_help_has_roadmap_file_option(self):
        runner = CliRunner()
        result = runner.invoke(tasklist_group, ["validate", "--help"])
        assert "--roadmap-file" in result.output

    def test_validate_help_has_tasklist_dir_option(self):
        runner = CliRunner()
        result = runner.invoke(tasklist_group, ["validate", "--help"])
        assert "--tasklist-dir" in result.output

    def test_validate_help_has_model_option(self):
        runner = CliRunner()
        result = runner.invoke(tasklist_group, ["validate", "--help"])
        assert "--model" in result.output

    def test_validate_help_has_max_turns_option(self):
        runner = CliRunner()
        result = runner.invoke(tasklist_group, ["validate", "--help"])
        assert "--max-turns" in result.output

    def test_validate_help_has_debug_option(self):
        runner = CliRunner()
        result = runner.invoke(tasklist_group, ["validate", "--help"])
        assert "--debug" in result.output

    def test_validate_registered_on_main(self):
        """Validate command is registered on the main CLI group."""
        runner = CliRunner()
        result = runner.invoke(main, ["tasklist", "--help"])
        assert result.exit_code == 0
        assert "validate" in result.output


class TestTasklistModuleStructure:
    """T04.03: Module structure verification."""

    def test_init_exists(self):
        from superclaude.cli import tasklist
        assert hasattr(tasklist, "__all__")

    def test_commands_module_exists(self):
        from superclaude.cli.tasklist import commands
        assert hasattr(commands, "tasklist_group")
        assert hasattr(commands, "validate")

    def test_executor_module_exists(self):
        from superclaude.cli.tasklist import executor
        assert hasattr(executor, "execute_tasklist_validate")

    def test_gates_module_exists(self):
        from superclaude.cli.tasklist import gates
        assert hasattr(gates, "TASKLIST_FIDELITY_GATE")

    def test_prompts_module_exists(self):
        from superclaude.cli.tasklist import prompts
        assert hasattr(prompts, "build_tasklist_fidelity_prompt")

    def test_models_module_exists(self):
        from superclaude.cli.tasklist import models
        assert hasattr(models, "TasklistValidateConfig")


class TestTasklistValidateExitCode:
    """T04.03: CLI exits 1 on HIGH-severity deviations."""

    def test_has_high_severity_true_for_high_count(self, tmp_path):
        report = tmp_path / "tasklist-fidelity.md"
        report.write_text(
            "---\n"
            "high_severity_count: 2\n"
            "medium_severity_count: 0\n"
            "low_severity_count: 0\n"
            "total_deviations: 2\n"
            "validation_complete: true\n"
            "tasklist_ready: false\n"
            "---\n"
            "## Deviation Report\n"
            "- DEV-001: HIGH\n"
            "- DEV-002: HIGH\n"
        )
        assert _has_high_severity(report) is True

    def test_has_high_severity_false_for_zero(self, tmp_path):
        report = tmp_path / "tasklist-fidelity.md"
        report.write_text(
            "---\n"
            "high_severity_count: 0\n"
            "medium_severity_count: 1\n"
            "low_severity_count: 2\n"
            "total_deviations: 3\n"
            "validation_complete: true\n"
            "tasklist_ready: true\n"
            "---\n"
            "## Deviation Report\n"
            "- DEV-001: MEDIUM\n"
        )
        assert _has_high_severity(report) is False

    def test_has_high_severity_true_for_missing_report(self, tmp_path):
        report = tmp_path / "nonexistent.md"
        assert _has_high_severity(report) is True

    def test_has_high_severity_true_for_no_frontmatter(self, tmp_path):
        report = tmp_path / "tasklist-fidelity.md"
        report.write_text("No frontmatter here.\n")
        assert _has_high_severity(report) is True


class TestCollectTasklistFiles:
    """Executor helper tests."""

    def test_collects_markdown_files(self, tmp_path):
        (tmp_path / "phase-1-tasklist.md").write_text("# Phase 1\n")
        (tmp_path / "phase-2-tasklist.md").write_text("# Phase 2\n")
        (tmp_path / "notes.txt").write_text("Not markdown\n")
        files = _collect_tasklist_files(tmp_path)
        assert len(files) == 2
        assert all(f.suffix == ".md" for f in files)

    def test_raises_for_missing_dir(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Tasklist directory not found"):
            _collect_tasklist_files(tmp_path / "nonexistent")

    def test_raises_for_empty_dir(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        with pytest.raises(FileNotFoundError, match="No markdown files found"):
            _collect_tasklist_files(empty)

    def test_files_sorted(self, tmp_path):
        (tmp_path / "b.md").write_text("b\n")
        (tmp_path / "a.md").write_text("a\n")
        (tmp_path / "c.md").write_text("c\n")
        files = _collect_tasklist_files(tmp_path)
        assert [f.name for f in files] == ["a.md", "b.md", "c.md"]


class TestBuildSteps:
    """Executor _build_steps tests."""

    def test_build_steps_creates_one_step(self, tmp_path):
        roadmap = tmp_path / "roadmap.md"
        roadmap.write_text("# Roadmap\n")
        tasklist_dir = tmp_path / "tasklists"
        tasklist_dir.mkdir()
        (tasklist_dir / "phase-1.md").write_text("# Phase 1\n")

        config = TasklistValidateConfig(
            output_dir=tmp_path,
            roadmap_file=roadmap,
            tasklist_dir=tasklist_dir,
        )
        steps = _build_steps(config)
        assert len(steps) == 1
        assert steps[0].id == "tasklist-fidelity"

    def test_build_steps_output_path(self, tmp_path):
        roadmap = tmp_path / "roadmap.md"
        roadmap.write_text("# Roadmap\n")
        tasklist_dir = tmp_path / "tasklists"
        tasklist_dir.mkdir()
        (tasklist_dir / "phase-1.md").write_text("# Phase 1\n")

        config = TasklistValidateConfig(
            output_dir=tmp_path,
            roadmap_file=roadmap,
            tasklist_dir=tasklist_dir,
        )
        steps = _build_steps(config)
        assert steps[0].output_file == tmp_path / "tasklist-fidelity.md"

    def test_build_steps_includes_roadmap_in_inputs(self, tmp_path):
        roadmap = tmp_path / "roadmap.md"
        roadmap.write_text("# Roadmap\n")
        tasklist_dir = tmp_path / "tasklists"
        tasklist_dir.mkdir()
        (tasklist_dir / "phase-1.md").write_text("# Phase 1\n")

        config = TasklistValidateConfig(
            output_dir=tmp_path,
            roadmap_file=roadmap,
            tasklist_dir=tasklist_dir,
        )
        steps = _build_steps(config)
        assert roadmap in steps[0].inputs

    def test_build_steps_includes_tasklist_files_in_inputs(self, tmp_path):
        roadmap = tmp_path / "roadmap.md"
        roadmap.write_text("# Roadmap\n")
        tasklist_dir = tmp_path / "tasklists"
        tasklist_dir.mkdir()
        (tasklist_dir / "phase-1.md").write_text("# Phase 1\n")
        (tasklist_dir / "phase-2.md").write_text("# Phase 2\n")

        config = TasklistValidateConfig(
            output_dir=tmp_path,
            roadmap_file=roadmap,
            tasklist_dir=tasklist_dir,
        )
        steps = _build_steps(config)
        # roadmap + 2 tasklist files = 3 inputs
        assert len(steps[0].inputs) == 3

    def test_build_steps_gate_is_tasklist_fidelity(self, tmp_path):
        roadmap = tmp_path / "roadmap.md"
        roadmap.write_text("# Roadmap\n")
        tasklist_dir = tmp_path / "tasklists"
        tasklist_dir.mkdir()
        (tasklist_dir / "phase-1.md").write_text("# Phase 1\n")

        config = TasklistValidateConfig(
            output_dir=tmp_path,
            roadmap_file=roadmap,
            tasklist_dir=tasklist_dir,
        )
        steps = _build_steps(config)
        assert steps[0].gate is TASKLIST_FIDELITY_GATE

    def test_build_steps_timeout_600s(self, tmp_path):
        roadmap = tmp_path / "roadmap.md"
        roadmap.write_text("# Roadmap\n")
        tasklist_dir = tmp_path / "tasklists"
        tasklist_dir.mkdir()
        (tasklist_dir / "phase-1.md").write_text("# Phase 1\n")

        config = TasklistValidateConfig(
            output_dir=tmp_path,
            roadmap_file=roadmap,
            tasklist_dir=tasklist_dir,
        )
        steps = _build_steps(config)
        assert steps[0].timeout_seconds == 600
