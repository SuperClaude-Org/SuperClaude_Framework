"""Integration tests for CLI validate paths (Phase 4 T04.06).

Covers:
- roadmap validate subcommand registration and help output
- roadmap run --no-validate flag registration and help output
- validate subcommand constructs ValidateConfig correctly
- auto-invocation after successful pipeline completion
- --no-validate skips validation
- exit code always 0 even with blocking issues
- validation state persistence in .roadmap-state.json
- --resume skips re-validation when already completed
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import click.testing
import pytest

from superclaude.cli.roadmap.commands import roadmap_group
from superclaude.cli.roadmap.executor import (
    _auto_invoke_validate,
    _save_validation_status,
    execute_roadmap,
    read_state,
    write_state,
)
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig, ValidateConfig


@pytest.fixture
def cli_runner():
    return click.testing.CliRunner()


@pytest.fixture
def pipeline_output_dir(tmp_path):
    """Create a directory with the 3 required pipeline outputs."""
    d = tmp_path / "output"
    d.mkdir()
    (d / "roadmap.md").write_text(
        "---\ntitle: roadmap\n---\n" + "\n".join(f"line {i}" for i in range(30))
    )
    (d / "test-strategy.md").write_text(
        "---\ntitle: test-strategy\n---\n" + "\n".join(f"line {i}" for i in range(30))
    )
    (d / "extraction.md").write_text(
        "---\ntitle: extraction\n---\n" + "\n".join(f"line {i}" for i in range(30))
    )
    return d


class TestValidateSubcommandHelp:
    """Verify roadmap validate subcommand registration."""

    def test_validate_help_exits_0(self, cli_runner):
        result = cli_runner.invoke(roadmap_group, ["validate", "--help"])
        assert result.exit_code == 0

    def test_validate_help_shows_agents_option(self, cli_runner):
        result = cli_runner.invoke(roadmap_group, ["validate", "--help"])
        assert "--agents" in result.output

    def test_validate_help_shows_model_option(self, cli_runner):
        result = cli_runner.invoke(roadmap_group, ["validate", "--help"])
        assert "--model" in result.output

    def test_validate_help_shows_max_turns_option(self, cli_runner):
        result = cli_runner.invoke(roadmap_group, ["validate", "--help"])
        assert "--max-turns" in result.output

    def test_validate_help_shows_debug_option(self, cli_runner):
        result = cli_runner.invoke(roadmap_group, ["validate", "--help"])
        assert "--debug" in result.output

    def test_validate_help_shows_output_dir_argument(self, cli_runner):
        result = cli_runner.invoke(roadmap_group, ["validate", "--help"])
        assert "OUTPUT_DIR" in result.output


class TestRunNoValidateFlag:
    """Verify --no-validate flag on roadmap run."""

    def test_run_help_shows_no_validate(self, cli_runner):
        result = cli_runner.invoke(roadmap_group, ["run", "--help"])
        assert result.exit_code == 0
        assert "--no-validate" in result.output


class TestValidateConfigConstruction:
    """Verify validate subcommand constructs ValidateConfig correctly."""

    def test_standalone_default_single_agent(self, cli_runner, pipeline_output_dir):
        """Default agent count for standalone validate is 1 (single-agent for cost efficiency)."""
        captured_config = {}

        def mock_execute(config):
            captured_config["agents"] = config.agents
            return {"blocking_count": 0, "warning_count": 0, "info_count": 0}

        with patch(
            "superclaude.cli.roadmap.validate_executor.execute_validate",
            side_effect=mock_execute,
        ):
            result = cli_runner.invoke(
                roadmap_group, ["validate", str(pipeline_output_dir)]
            )

        assert result.exit_code == 0
        assert len(captured_config["agents"]) == 1
        assert captured_config["agents"][0].model == "opus"

    def test_custom_agents_parsed(self, cli_runner, pipeline_output_dir):
        captured_config = {}

        def mock_execute(config):
            captured_config["agents"] = config.agents
            return {"blocking_count": 0, "warning_count": 0, "info_count": 0}

        with patch(
            "superclaude.cli.roadmap.validate_executor.execute_validate",
            side_effect=mock_execute,
        ):
            result = cli_runner.invoke(
                roadmap_group,
                ["validate", str(pipeline_output_dir), "--agents", "sonnet:security,haiku:qa"],
            )

        assert result.exit_code == 0
        assert len(captured_config["agents"]) == 2
        assert captured_config["agents"][0].persona == "security"
        assert captured_config["agents"][1].persona == "qa"


class TestExitCodeBehavior:
    """Verify exit code is always 0 per NFR-006."""

    def test_exit_0_with_no_issues(self, cli_runner, pipeline_output_dir):
        with patch(
            "superclaude.cli.roadmap.validate_executor.execute_validate",
            return_value={"blocking_count": 0, "warning_count": 0, "info_count": 0},
        ):
            result = cli_runner.invoke(
                roadmap_group, ["validate", str(pipeline_output_dir)]
            )
        assert result.exit_code == 0

    def test_exit_0_with_blocking_issues(self, cli_runner, pipeline_output_dir):
        with patch(
            "superclaude.cli.roadmap.validate_executor.execute_validate",
            return_value={"blocking_count": 3, "warning_count": 2, "info_count": 1},
        ):
            result = cli_runner.invoke(
                roadmap_group, ["validate", str(pipeline_output_dir)]
            )
        assert result.exit_code == 0
        assert "WARNING" in result.output
        assert "3 blocking" in result.output

    def test_blocking_issues_shown_as_warning(self, cli_runner, pipeline_output_dir):
        with patch(
            "superclaude.cli.roadmap.validate_executor.execute_validate",
            return_value={"blocking_count": 5, "warning_count": 0, "info_count": 0},
        ):
            result = cli_runner.invoke(
                roadmap_group, ["validate", str(pipeline_output_dir)]
            )
        assert "5 blocking issue(s) found" in result.output


class TestAutoInvocation:
    """Verify auto-invocation after successful pipeline completion."""

    def test_auto_invoke_after_success(self, tmp_path):
        """execute_roadmap calls _auto_invoke_validate after all steps pass."""
        spec = tmp_path / "spec.md"
        spec.write_text("# Spec\nContent.\n")
        output = tmp_path / "output"
        output.mkdir()

        config = RoadmapConfig(
            spec_file=spec,
            output_dir=output,
            work_dir=output,
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
        )

        with (
            patch("superclaude.cli.roadmap.executor.execute_pipeline", return_value=[]),
            patch("superclaude.cli.roadmap.executor._auto_invoke_validate") as mock_validate,
        ):
            execute_roadmap(config)

        mock_validate.assert_called_once_with(config)

    def test_no_validate_skips_auto_invoke(self, tmp_path, capsys):
        """--no-validate skips validation and records 'skipped' in state."""
        spec = tmp_path / "spec.md"
        spec.write_text("# Spec\nContent.\n")
        output = tmp_path / "output"
        output.mkdir()

        config = RoadmapConfig(
            spec_file=spec,
            output_dir=output,
            work_dir=output,
        )

        with (
            patch("superclaude.cli.roadmap.executor.execute_pipeline", return_value=[]),
            patch("superclaude.cli.roadmap.executor._auto_invoke_validate") as mock_validate,
        ):
            execute_roadmap(config, no_validate=True)

        mock_validate.assert_not_called()
        captured = capsys.readouterr()
        assert "--no-validate" in captured.out

        # Verify state file has "skipped"
        state = read_state(output / ".roadmap-state.json")
        assert state is not None
        assert state["validation"]["status"] == "skipped"


class TestValidationStatePersistence:
    """Verify validation status recording in .roadmap-state.json."""

    def test_save_pass_status(self, tmp_path):
        config = RoadmapConfig(
            spec_file=tmp_path / "spec.md",
            output_dir=tmp_path,
            work_dir=tmp_path,
        )
        (tmp_path / "spec.md").write_text("# Spec")
        # Pre-populate a state file
        write_state({"schema_version": 1}, tmp_path / ".roadmap-state.json")

        _save_validation_status(config, "pass")

        state = read_state(tmp_path / ".roadmap-state.json")
        assert state["validation"]["status"] == "pass"
        assert "timestamp" in state["validation"]
        # Existing keys preserved
        assert state["schema_version"] == 1

    def test_save_fail_status(self, tmp_path):
        config = RoadmapConfig(
            spec_file=tmp_path / "spec.md",
            output_dir=tmp_path,
            work_dir=tmp_path,
        )
        (tmp_path / "spec.md").write_text("# Spec")
        write_state({"schema_version": 1}, tmp_path / ".roadmap-state.json")

        _save_validation_status(config, "fail")

        state = read_state(tmp_path / ".roadmap-state.json")
        assert state["validation"]["status"] == "fail"

    def test_save_skipped_status(self, tmp_path):
        config = RoadmapConfig(
            spec_file=tmp_path / "spec.md",
            output_dir=tmp_path,
            work_dir=tmp_path,
        )
        (tmp_path / "spec.md").write_text("# Spec")

        _save_validation_status(config, "skipped")

        state = read_state(tmp_path / ".roadmap-state.json")
        assert state["validation"]["status"] == "skipped"

    def test_backward_compatible_no_existing_keys_modified(self, tmp_path):
        config = RoadmapConfig(
            spec_file=tmp_path / "spec.md",
            output_dir=tmp_path,
            work_dir=tmp_path,
        )
        (tmp_path / "spec.md").write_text("# Spec")
        write_state(
            {"schema_version": 1, "steps": {"extract": {"status": "PASS"}}},
            tmp_path / ".roadmap-state.json",
        )

        _save_validation_status(config, "pass")

        state = read_state(tmp_path / ".roadmap-state.json")
        assert state["schema_version"] == 1
        assert state["steps"]["extract"]["status"] == "PASS"
        assert state["validation"]["status"] == "pass"


class TestResumeSkipsValidation:
    """Verify --resume skips re-validation when already completed."""

    def test_resume_skips_when_already_passed(self, tmp_path, capsys):
        spec = tmp_path / "spec.md"
        spec.write_text("# Spec\nContent.\n")
        output = tmp_path / "output"
        output.mkdir()

        # Pre-populate state with completed validation
        write_state(
            {
                "schema_version": 1,
                "spec_hash": "",
                "validation": {"status": "pass", "timestamp": "2026-01-01T00:00:00+00:00"},
            },
            output / ".roadmap-state.json",
        )

        config = RoadmapConfig(
            spec_file=spec,
            output_dir=output,
            work_dir=output,
        )

        with (
            patch("superclaude.cli.roadmap.executor.execute_pipeline", return_value=[]),
            patch("superclaude.cli.roadmap.executor._auto_invoke_validate") as mock_validate,
            patch("superclaude.cli.roadmap.executor._apply_resume", return_value=[]),
        ):
            execute_roadmap(config, resume=True)

        mock_validate.assert_not_called()
        captured = capsys.readouterr()
        assert "already completed" in captured.out

    def test_resume_invokes_when_not_yet_validated(self, tmp_path):
        spec = tmp_path / "spec.md"
        spec.write_text("# Spec\nContent.\n")
        output = tmp_path / "output"
        output.mkdir()

        # State without validation key
        write_state(
            {"schema_version": 1, "spec_hash": ""},
            output / ".roadmap-state.json",
        )

        config = RoadmapConfig(
            spec_file=spec,
            output_dir=output,
            work_dir=output,
        )

        with (
            patch("superclaude.cli.roadmap.executor.execute_pipeline", return_value=[]),
            patch("superclaude.cli.roadmap.executor._auto_invoke_validate") as mock_validate,
            patch("superclaude.cli.roadmap.executor._apply_resume", return_value=[]),
        ):
            execute_roadmap(config, resume=True)

        mock_validate.assert_called_once()
