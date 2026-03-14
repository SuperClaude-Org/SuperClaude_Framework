"""Tests for cli-portify CLI interface (v2.24.1).

Covers:
- TARGET positional argument replaces WORKFLOW_PATH
- --commands-dir, --skills-dir, --agents-dir options
- --include-agent option with empty-string filtering
- --save-manifest option
- Legacy skill-directory invocations continue to work
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from superclaude.cli.cli_portify.cli import cli_portify_group
from superclaude.cli.cli_portify.config import load_portify_config


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def skill_dir(tmp_path: Path) -> Path:
    """Create a minimal skill directory for CLI testing."""
    sd = tmp_path / "sc-test-protocol"
    sd.mkdir()
    (sd / "SKILL.md").write_text("# Test Skill\n")
    return sd


class TestTargetArgument:
    """CLI accepts TARGET as positional argument."""

    def test_help_shows_target(self, runner):
        result = runner.invoke(cli_portify_group, ["run", "--help"])
        assert result.exit_code == 0
        assert "TARGET" in result.output

    def test_help_does_not_show_workflow_path(self, runner):
        result = runner.invoke(cli_portify_group, ["run", "--help"])
        assert "WORKFLOW_PATH" not in result.output

    def test_skill_dir_invocation_works(self, runner, skill_dir, tmp_path):
        result = runner.invoke(cli_portify_group, [
            "run", str(skill_dir),
            "--output", str(tmp_path / "output"),
            "--dry-run",
        ])
        assert result.exit_code == 0
        assert "dry-run" in result.output


class TestNewCliOptions:
    """New CLI options appear in --help and accept values."""

    def test_commands_dir_in_help(self, runner):
        result = runner.invoke(cli_portify_group, ["run", "--help"])
        assert "--commands-dir" in result.output

    def test_skills_dir_in_help(self, runner):
        result = runner.invoke(cli_portify_group, ["run", "--help"])
        assert "--skills-dir" in result.output

    def test_agents_dir_in_help(self, runner):
        result = runner.invoke(cli_portify_group, ["run", "--help"])
        assert "--agents-dir" in result.output

    def test_include_agent_in_help(self, runner):
        result = runner.invoke(cli_portify_group, ["run", "--help"])
        assert "--include-agent" in result.output

    def test_save_manifest_in_help(self, runner):
        result = runner.invoke(cli_portify_group, ["run", "--help"])
        assert "--save-manifest" in result.output

    def test_commands_dir_accepted(self, runner, skill_dir, tmp_path):
        cmds = tmp_path / "commands"
        cmds.mkdir()
        result = runner.invoke(cli_portify_group, [
            "run", str(skill_dir),
            "--output", str(tmp_path / "output"),
            "--commands-dir", str(cmds),
            "--dry-run",
        ])
        assert result.exit_code == 0

    def test_skills_dir_accepted(self, runner, skill_dir, tmp_path):
        skills = tmp_path / "skills"
        skills.mkdir()
        result = runner.invoke(cli_portify_group, [
            "run", str(skill_dir),
            "--output", str(tmp_path / "output"),
            "--skills-dir", str(skills),
            "--dry-run",
        ])
        assert result.exit_code == 0

    def test_agents_dir_accepted(self, runner, skill_dir, tmp_path):
        agents = tmp_path / "agents"
        agents.mkdir()
        result = runner.invoke(cli_portify_group, [
            "run", str(skill_dir),
            "--output", str(tmp_path / "output"),
            "--agents-dir", str(agents),
            "--dry-run",
        ])
        assert result.exit_code == 0


class TestIncludeAgentFiltering:
    """--include-agent filters empty strings and accepts multiple values."""

    def test_multiple_include_agent(self, runner, skill_dir, tmp_path):
        result = runner.invoke(cli_portify_group, [
            "run", str(skill_dir),
            "--output", str(tmp_path / "output"),
            "--include-agent", "audit-scanner",
            "--include-agent", "quality-engineer",
            "--dry-run",
        ])
        assert result.exit_code == 0

    def test_empty_string_filtered(self, runner, skill_dir, tmp_path):
        """Empty --include-agent values are filtered out."""
        result = runner.invoke(cli_portify_group, [
            "run", str(skill_dir),
            "--output", str(tmp_path / "output"),
            "--include-agent", "",
            "--dry-run",
        ])
        assert result.exit_code == 0


class TestLegacyBackwardCompat:
    """Existing skill-directory invocations work identically."""

    def test_legacy_dir_invocation(self, runner, skill_dir, tmp_path):
        result = runner.invoke(cli_portify_group, [
            "run", str(skill_dir),
            "--output", str(tmp_path / "output"),
            "--dry-run",
        ])
        assert result.exit_code == 0
        assert "dry-run" in result.output
        assert "sc-test-protocol" in result.output or "test" in result.output.lower()

    def test_legacy_with_cli_name(self, runner, skill_dir, tmp_path):
        result = runner.invoke(cli_portify_group, [
            "run", str(skill_dir),
            "--output", str(tmp_path / "output"),
            "--cli-name", "custom-name",
            "--dry-run",
        ])
        assert result.exit_code == 0
        assert "custom-name" in result.output


# --- T03.05: Stream B Integration Tests ---


class TestValidationResultShape:
    """Validation result contains all v2.24.1 fields."""

    def test_result_has_all_new_fields(self, tmp_path):
        """ValidateConfigResult from run_validate_config has all new fields."""
        from superclaude.cli.cli_portify.steps.validate_config import (
            ValidateConfigResult,
            run_validate_config,
        )
        from superclaude.cli.cli_portify.models import (
            AgentEntry,
            ComponentTree,
        )

        sd = tmp_path / "sc-test-protocol"
        sd.mkdir()
        (sd / "SKILL.md").write_text("# Test\n")

        config = load_portify_config(
            workflow_path=sd,
            output_dir=tmp_path / "output",
        )
        config.component_tree = ComponentTree(
            agents=[AgentEntry(name="test-agent", found=True)],
        )
        result, step_result = run_validate_config(config)
        assert hasattr(result, "command_path")
        assert hasattr(result, "skill_dir")
        assert hasattr(result, "target_type")
        assert hasattr(result, "agent_count")
        assert hasattr(result, "warnings")
        assert isinstance(result.warnings, list)

    def test_result_serializes_to_json(self, tmp_path):
        """ValidateConfigResult.to_dict() is JSON-serializable."""
        import json
        from superclaude.cli.cli_portify.steps.validate_config import (
            run_validate_config,
        )

        sd = tmp_path / "sc-test-protocol"
        sd.mkdir()
        (sd / "SKILL.md").write_text("# Test\n")

        config = load_portify_config(
            workflow_path=sd,
            output_dir=tmp_path / "output",
        )
        result, _ = run_validate_config(config)
        d = result.to_dict()
        serialized = json.dumps(d)
        assert isinstance(serialized, str)
        assert "command_path" in serialized


class TestManifestOutput:
    """--save-manifest option produces readable Markdown file."""

    def test_manifest_markdown_generation(self, tmp_path):
        """ComponentTree.to_manifest_markdown() produces valid Markdown."""
        from superclaude.cli.cli_portify.models import (
            CommandEntry,
            ComponentTree,
            SkillEntry,
            AgentEntry,
        )

        tree = ComponentTree(
            command=CommandEntry(name="test-cmd", line_count=10),
            skill=SkillEntry(name="sc-test-protocol", line_count=50),
            agents=[AgentEntry(name="audit-scanner", found=True, line_count=20)],
        )
        md = tree.to_manifest_markdown()
        assert md.startswith("---\n")
        assert "source_command: test-cmd" in md
        assert "## Command (Tier 0)" in md
        assert "## Skill (Tier 1)" in md
        assert "## Agents (Tier 2)" in md

    def test_manifest_writable_to_file(self, tmp_path):
        """Manifest can be written to disk as a valid file."""
        from superclaude.cli.cli_portify.models import (
            CommandEntry,
            ComponentTree,
            SkillEntry,
        )

        tree = ComponentTree(
            command=CommandEntry(name="test", line_count=5),
            skill=SkillEntry(name="sc-test", line_count=15),
        )
        md = tree.to_manifest_markdown()
        manifest_path = tmp_path / "manifest.md"
        manifest_path.write_text(md, encoding="utf-8")
        assert manifest_path.exists()
        content = manifest_path.read_text()
        assert "---" in content
        assert "source_command: test" in content


class TestProcessIntegration:
    """Process invocation integration tests."""

    def test_additional_dirs_none_preserves_v224(self, tmp_path):
        """SC-11: additional_dirs=None produces same command as v2.24."""
        from superclaude.cli.cli_portify.process import PortifyProcess

        work = tmp_path / "work"
        wf = tmp_path / "workflow"

        proc_legacy = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=work,
            workflow_path=wf,
        )
        proc_new = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=work,
            workflow_path=wf,
            additional_dirs=None,
        )
        assert proc_legacy.build_command() == proc_new.build_command()

    def test_additional_dirs_list_adds_flags(self, tmp_path):
        """additional_dirs=[list] produces additional --add-dir flags."""
        from superclaude.cli.cli_portify.process import PortifyProcess

        work = tmp_path / "work"
        wf = tmp_path / "workflow"
        extra = tmp_path / "extra"
        extra.mkdir()

        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=work,
            workflow_path=wf,
            additional_dirs=[extra],
        )
        cmd = proc.build_command()
        add_dir_count = cmd.count("--add-dir")
        assert add_dir_count == 3  # work + wf + extra


class TestToFlatInventoryEquivalence:
    """SC-9: to_flat_inventory() equivalence test."""

    def test_flat_inventory_preserves_data(self):
        """ComponentTree.to_flat_inventory() preserves all component data."""
        from superclaude.cli.cli_portify.models import (
            CommandEntry,
            ComponentTree,
            SkillEntry,
            AgentEntry,
        )

        tree = ComponentTree(
            command=CommandEntry(name="cmd", path=Path("/cmd.md"), line_count=10),
            skill=SkillEntry(name="skill", path=Path("/skill"), line_count=50),
            agents=[
                AgentEntry(name="agent-a", path=Path("/a.md"), line_count=5),
            ],
        )
        inv = tree.to_flat_inventory()
        assert inv.component_count == tree.component_count
        # Verify Path -> str conversion
        for comp in inv.components:
            assert isinstance(comp.path, str)


class TestMissingAgentsIntegration:
    """SC-8: Missing agents warn, don't fail (integration test)."""

    def test_missing_agent_warns_not_fails_in_pipeline(self, tmp_path):
        from superclaude.cli.cli_portify.steps.validate_config import run_validate_config
        from superclaude.cli.cli_portify.models import (
            AgentEntry,
            ComponentTree,
        )

        sd = tmp_path / "sc-test-protocol"
        sd.mkdir()
        (sd / "SKILL.md").write_text("# Test\n")

        config = load_portify_config(
            workflow_path=sd,
            output_dir=tmp_path / "output",
        )
        config.component_tree = ComponentTree(
            agents=[
                AgentEntry(name="found-agent", found=True),
                AgentEntry(name="missing-agent", found=False),
            ]
        )
        result, step_result = run_validate_config(config)
        # Must pass validation (not fail)
        assert result.valid is True
        # But must have warnings
        assert len(result.warnings) == 1
        assert "missing-agent" in result.warnings[0]
