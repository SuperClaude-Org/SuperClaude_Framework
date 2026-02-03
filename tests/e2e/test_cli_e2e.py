"""
E2E tests for SuperClaude CLI commands.

These tests execute actual CLI commands via subprocess to verify
the complete user experience works correctly.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

# Get the venv bin directory where superclaude is installed
VENV_BIN = Path(sys.executable).parent
SUPERCLAUDE_CMD = VENV_BIN / "superclaude"
PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_cli(*args, timeout=30, cwd=None):
    """Run superclaude CLI command using venv binary."""
    if SUPERCLAUDE_CMD.exists():
        cmd = [str(SUPERCLAUDE_CMD), *args]
    else:
        # Fallback: use python -m superclaude
        cmd = [sys.executable, "-m", "superclaude", *args]

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


def run_pytest(*args, timeout=60):
    """Run pytest using venv python."""
    return subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=PROJECT_ROOT,
    )


class TestCLIVersion:
    """Test version command."""

    def test_version_flag(self):
        """Test --version shows version info."""
        result = run_cli("--version")
        assert result.returncode == 0
        assert "superclaude" in result.stdout.lower() or "4." in result.stdout

    def test_help_shows_version_option(self):
        """Test help mentions version option."""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "--version" in result.stdout


class TestCLIDoctor:
    """Test doctor command for health checks."""

    def test_doctor_runs(self):
        """Test doctor command executes without error."""
        result = run_cli("doctor", timeout=60)
        # Doctor should run (may have warnings but shouldn't crash)
        assert result.returncode in [0, 1]  # 0=healthy, 1=warnings
        # Should produce some output
        assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_doctor_checks_components(self):
        """Test doctor checks expected components."""
        result = run_cli("doctor", timeout=60)
        output = result.stdout + result.stderr
        # Should mention key components
        assert any(
            keyword in output.lower()
            for keyword in [
                "superclaude",
                "version",
                "check",
                "health",
                "status",
                "ok",
                "installed",
            ]
        )


class TestCLIInstall:
    """Test install command for slash commands."""

    def test_install_list(self):
        """Test install --list shows available commands."""
        result = run_cli("install", "--list")
        assert result.returncode == 0
        output = result.stdout + result.stderr
        # Should list some commands
        assert any(
            cmd in output.lower()
            for cmd in ["pm", "research", "implement", "test", "analyze"]
        )

    def test_install_to_temp_directory(self):
        """Test install command installs to specified directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            commands_dir = Path(tmpdir) / "commands"
            result = run_cli("install", "--target", str(commands_dir), timeout=60)
            assert result.returncode == 0
            # Should have created some .md files
            if commands_dir.exists():
                md_files = list(commands_dir.glob("*.md"))
                assert len(md_files) > 0, "No command files installed"

    def test_install_help(self):
        """Test install --help shows usage."""
        result = run_cli("install", "--help")
        assert result.returncode == 0
        assert "install" in result.stdout.lower()


class TestCLIMCP:
    """Test MCP server management commands."""

    def test_mcp_list(self):
        """Test mcp --list shows available servers."""
        result = run_cli("mcp", "--list")
        assert result.returncode == 0
        output = result.stdout + result.stderr
        # Should list some MCP servers
        assert any(
            server in output.lower()
            for server in [
                "tavily",
                "context7",
                "sequential",
                "serena",
                "gateway",
                "airis",
            ]
        )

    def test_mcp_help(self):
        """Test mcp --help shows usage."""
        result = run_cli("mcp", "--help")
        assert result.returncode == 0
        assert "mcp" in result.stdout.lower()


class TestCLIHelp:
    """Test help command and flags."""

    def test_help_flag(self):
        """Test --help shows usage."""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "superclaude" in result.stdout.lower()

    def test_help_shows_commands(self):
        """Test help shows available commands."""
        result = run_cli("--help")
        output = result.stdout.lower()
        # Should mention main commands
        assert any(cmd in output for cmd in ["install", "doctor", "mcp"])


class TestPytestPluginE2E:
    """Test pytest plugin loads correctly."""

    def test_plugin_registered(self):
        """Test superclaude plugin is registered with pytest."""
        result = run_pytest("--co", "-q", "tests/unit/test_confidence.py")
        # Should collect tests without error
        assert result.returncode == 0 or "collected" in result.stdout.lower()

    def test_plugin_fixtures_available(self):
        """Test plugin fixtures are available."""
        result = run_pytest("--fixtures", "-q")
        output = result.stdout + result.stderr
        # Should list our fixtures
        assert any(
            fixture in output
            for fixture in ["confidence_checker", "token_budget", "pm_context"]
        )

    def test_run_single_unit_test(self):
        """Test running a single unit test works."""
        result = run_pytest(
            "tests/unit/test_confidence.py::TestConfidenceChecker::test_high_confidence_scenario",
            "-v",
        )
        assert result.returncode == 0
        assert "passed" in result.stdout.lower()


class TestConfidenceCheckerE2E:
    """E2E tests for confidence checker functionality."""

    def test_confidence_check_workflow(self):
        """Test complete confidence check workflow."""
        result = run_pytest(
            "tests/unit/test_confidence.py::TestCodebaseSearchImplementation",
            "-v",
            timeout=120,
        )
        assert result.returncode == 0
        assert "passed" in result.stdout.lower()

    def test_architecture_compliance_workflow(self):
        """Test architecture compliance checking."""
        result = run_pytest(
            "tests/unit/test_confidence.py::TestTechStackDetection",
            "-v",
            timeout=120,
        )
        assert result.returncode == 0
        assert "passed" in result.stdout.lower()


class TestFullTestSuite:
    """Test running the full test suite."""

    def test_all_unit_tests_pass(self):
        """Test all unit tests pass."""
        result = run_pytest("tests/unit/", "-q", timeout=300)
        assert result.returncode == 0
        assert "passed" in result.stdout.lower()
        # Should not have failures
        assert (
            "failed" not in result.stdout.lower() or "0 failed" in result.stdout.lower()
        )

    def test_all_integration_tests_pass(self):
        """Test all integration tests pass."""
        result = run_pytest("tests/integration/", "-q", timeout=300)
        assert result.returncode == 0
        assert "passed" in result.stdout.lower()
