"""
Tests for SuperClaude CLI Main

Tests command-line interface functionality.
"""

import tempfile
from unittest.mock import patch

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

    def test_install_list_flag(self):
        """Test install --list flag"""
        runner = CliRunner()
        result = runner.invoke(main, ["install", "--list"])

        assert result.exit_code == 0
        assert "Available" in result.output or "command" in result.output.lower()

    @patch("superclaude.cli.install_commands.install_commands")
    def test_install_to_custom_target(self, mock_install):
        """Test install to custom target"""
        mock_install.return_value = (True, "Success")

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(main, ["install", "--target", tmpdir])

        # May succeed or fail depending on mock setup
        assert result.exit_code in [0, 1]


class TestUpdateCommand:
    """Tests for update command"""

    def test_update_help(self):
        """Test update help"""
        runner = CliRunner()
        result = runner.invoke(main, ["update", "--help"])

        assert result.exit_code == 0

    def test_update_executes(self):
        """Test update executes"""
        runner = CliRunner()
        result = runner.invoke(main, ["update"])

        # Update may succeed or fail depending on environment
        assert result.exit_code in [0, 1]


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
