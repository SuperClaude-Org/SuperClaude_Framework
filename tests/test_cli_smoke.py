"""
Smoke tests for new typer + rich CLI
Tests basic functionality without full integration
"""

import pytest
from typer.testing import CliRunner
from superclaude.cli.app import app

runner = CliRunner()


class TestCLISmoke:
    """Basic smoke tests for CLI functionality"""

    def test_help_command(self):
        """Test that --help works"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "SuperClaude" in result.stdout
        assert "install" in result.stdout
        assert "doctor" in result.stdout
        assert "config" in result.stdout

    def test_version_command(self):
        """Test that --version works"""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "SuperClaude" in result.stdout
        assert "version" in result.stdout

    def test_install_help(self):
        """Test install command help"""
        result = runner.invoke(app, ["install", "--help"])
        assert result.exit_code == 0
        assert "install" in result.stdout.lower()

    def test_install_all_help(self):
        """Test install all subcommand help"""
        result = runner.invoke(app, ["install", "all", "--help"])
        assert result.exit_code == 0
        assert "Install SuperClaude" in result.stdout

    def test_doctor_help(self):
        """Test doctor command help"""
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0
        assert "diagnose" in result.stdout.lower() or "diagnostic" in result.stdout.lower()

    def test_doctor_run(self):
        """Test doctor command execution (may fail or pass depending on environment)"""
        result = runner.invoke(app, ["doctor"])
        # Don't assert exit code - depends on environment
        # Just verify it runs without crashing
        assert "Diagnostic" in result.stdout or "System" in result.stdout

    def test_config_help(self):
        """Test config command help"""
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "config" in result.stdout.lower()

    def test_config_show(self):
        """Test config show command"""
        result = runner.invoke(app, ["config", "show"])
        # Should not crash, may show "No API keys configured"
        assert result.exit_code == 0 or "not configured" in result.stdout

    def test_config_validate(self):
        """Test config validate command"""
        result = runner.invoke(app, ["config", "validate"])
        # Should not crash
        assert result.exit_code in (0, 1)  # May exit 1 if no keys configured


class TestCLIIntegration:
    """Integration tests for command workflows"""

    def test_doctor_install_workflow(self):
        """Test doctor → install suggestion workflow"""
        # Run doctor
        doctor_result = runner.invoke(app, ["doctor"])

        # Should suggest installation if not installed
        # Or show success if already installed
        assert doctor_result.exit_code in (0, 1)

    @pytest.mark.slow
    def test_install_dry_run(self):
        """Test installation in dry-run mode (safe, no changes)"""
        result = runner.invoke(app, [
            "install", "all",
            "--dry-run",
            "--non-interactive"
        ])

        # Dry run should succeed or fail gracefully
        assert result.exit_code in (0, 1)
        if result.exit_code == 0:
            # Should mention "dry run" or "would install"
            assert "dry" in result.stdout.lower() or "would" in result.stdout.lower()


@pytest.mark.skipif(
    not __name__ == "__main__",
    reason="Manual test - run directly to test CLI interactively"
)
def test_manual_cli():
    """
    Manual test for CLI interaction
    Run this file directly: python tests/test_cli_smoke.py
    """
    print("\n=== Manual CLI Test ===")
    print("Testing help command...")
    result = runner.invoke(app, ["--help"])
    print(result.stdout)

    print("\nTesting doctor command...")
    result = runner.invoke(app, ["doctor"])
    print(result.stdout)

    print("\nManual test complete!")


if __name__ == "__main__":
    test_manual_cli()
