"""
Tests for SuperClaude CLI Main

Tests command-line interface functionality.
"""

import tempfile
from pathlib import Path

from click.testing import CliRunner

from superclaude.cli.main import main


class TestCLIGroup:
    """Tests for main CLI group"""

    def test_main_help(self):
        """Test main help command"""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "SuperClaude" in result.output

    def test_main_version(self):
        """Test version option"""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "SuperClaude" in result.output


class TestVersionCommand:
    """Tests for version command"""

    def test_version_command(self):
        """Test version subcommand"""
        runner = CliRunner()
        result = runner.invoke(main, ["version"])

        assert result.exit_code == 0
        assert "version" in result.output.lower()


class TestInstallCommand:
    """Tests for install command"""

    def test_install_help(self):
        """Test install help"""
        runner = CliRunner()
        result = runner.invoke(main, ["install", "--help"])

        assert result.exit_code == 0
        assert "install" in result.output.lower()
        assert "--minimal" in result.output

    def test_install_list_flag(self):
        """Test install --list flag shows skills and agents"""
        runner = CliRunner()
        result = runner.invoke(main, ["install", "--list"])

        assert result.exit_code == 0
        assert "Skills" in result.output
        assert "Agents" in result.output
        assert "confidence-check" in result.output
        assert "explore-haiku" in result.output

    def test_install_to_custom_dirs(self):
        """Test install to custom skill/agent directories"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            agents_dir = Path(tmpdir) / "agents"

            result = runner.invoke(
                main,
                [
                    "install",
                    "--skills-dir",
                    str(skills_dir),
                    "--agents-dir",
                    str(agents_dir),
                ],
            )

            assert result.exit_code == 0
            assert (skills_dir / "confidence-check" / "SKILL.md").exists()
            assert (agents_dir / "explore-haiku.md").exists()

    def test_install_minimal(self):
        """Test --minimal installs only confidence-check, no agents"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            agents_dir = Path(tmpdir) / "agents"

            result = runner.invoke(
                main,
                [
                    "install",
                    "--minimal",
                    "--skills-dir",
                    str(skills_dir),
                    "--agents-dir",
                    str(agents_dir),
                ],
            )

            assert result.exit_code == 0
            assert (skills_dir / "confidence-check").exists()
            assert not (skills_dir / "spec-panel").exists()
            assert not agents_dir.exists()


class TestUpdateCommand:
    """Tests for update command"""

    def test_update_help(self):
        """Test update help"""
        runner = CliRunner()
        result = runner.invoke(main, ["update", "--help"])

        assert result.exit_code == 0

    def test_update_force_reinstalls(self):
        """Test update force-reinstalls skills and agents"""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            agents_dir = Path(tmpdir) / "agents"
            args = [
                "--skills-dir",
                str(skills_dir),
                "--agents-dir",
                str(agents_dir),
            ]

            result1 = runner.invoke(main, ["install", *args])
            assert result1.exit_code == 0

            # Modify an installed file, update should overwrite it
            skill_md = skills_dir / "confidence-check" / "SKILL.md"
            skill_md.write_text("modified")

            result2 = runner.invoke(main, ["update", *args])
            assert result2.exit_code == 0
            assert skill_md.read_text() != "modified"


class TestMCPCommand:
    """Tests for mcp command"""

    def test_mcp_help(self):
        """Test mcp help"""
        runner = CliRunner()
        result = runner.invoke(main, ["mcp", "--help"])

        assert result.exit_code == 0
        assert "mcp" in result.output.lower() or "server" in result.output.lower()

    def test_mcp_list(self):
        """Test mcp --list"""
        runner = CliRunner()
        result = runner.invoke(main, ["mcp", "--list"])

        assert result.exit_code == 0
        assert "Available" in result.output or "Server" in result.output


class TestDoctorCommand:
    """Tests for doctor command"""

    def test_doctor_help(self):
        """Test doctor help"""
        runner = CliRunner()
        result = runner.invoke(main, ["doctor", "--help"])

        assert result.exit_code == 0

    def test_doctor_executes(self):
        """Test doctor command executes"""
        runner = CliRunner()
        result = runner.invoke(main, ["doctor"])

        # Doctor returns 0 if all checks pass, 1 otherwise
        assert result.exit_code in [0, 1]
        assert "doctor" in result.output.lower() or "healthy" in result.output.lower()

    def test_doctor_verbose(self):
        """Test doctor with verbose flag"""
        runner = CliRunner()
        result = runner.invoke(main, ["doctor", "--verbose"])

        assert result.exit_code in [0, 1]


class TestInstallSkillCommand:
    """Tests for install-skill command"""

    def test_install_skill_help(self):
        """Test install-skill help"""
        runner = CliRunner()
        result = runner.invoke(main, ["install-skill", "--help"])

        assert result.exit_code == 0

    def test_install_skill_not_found(self):
        """Test install-skill with unknown skill"""
        runner = CliRunner()
        result = runner.invoke(main, ["install-skill", "unknown-skill-xyz-123"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_install_skill_with_force(self):
        """Test install-skill with force flag"""
        runner = CliRunner()
        # Force flag should work even if skill not found
        result = runner.invoke(main, ["install-skill", "unknown-xyz", "--force"])

        # Should fail because skill not found
        assert result.exit_code == 1


class TestCLIEdgeCases:
    """Edge case tests for CLI"""

    def test_unknown_command(self):
        """Test unknown command shows error"""
        runner = CliRunner()
        result = runner.invoke(main, ["unknown-command"])

        assert result.exit_code != 0

    def test_empty_invocation_shows_usage(self):
        """Test empty invocation shows usage info"""
        runner = CliRunner()
        result = runner.invoke(main, [])

        # Click shows usage and exits with code 2 when no command given
        # This is expected behavior for command groups
        assert result.exit_code in [0, 2]
        assert "Usage" in result.output or "superclaude" in result.output.lower()
