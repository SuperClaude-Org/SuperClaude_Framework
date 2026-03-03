"""T07.03 — CLI contract validation for all subcommands.

Tests that all 5 subcommands (run, attach, status, logs, kill) exist,
respond to --help, and expose documented options.
"""

from __future__ import annotations

from click.testing import CliRunner

from superclaude.cli.sprint.commands import sprint_group


class TestCLIContract:
    """T07.03: All 5 subcommands match documented CLI contract."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_sprint_group_help(self):
        result = self.runner.invoke(sprint_group, ["--help"])
        assert result.exit_code == 0
        assert "sprint" in result.output.lower()
        # All subcommands should be listed
        assert "run" in result.output
        assert "attach" in result.output
        assert "status" in result.output
        assert "logs" in result.output
        assert "kill" in result.output

    def test_run_help(self):
        result = self.runner.invoke(sprint_group, ["run", "--help"])
        assert result.exit_code == 0
        # Required argument
        assert "INDEX_PATH" in result.output or "index_path" in result.output.lower()
        # Documented options
        assert "--start" in result.output
        assert "--end" in result.output
        assert "--max-turns" in result.output
        assert "--model" in result.output
        assert "--dry-run" in result.output
        assert "--no-tmux" in result.output
        assert "--permission-flag" in result.output

    def test_run_help_permission_choices(self):
        result = self.runner.invoke(sprint_group, ["run", "--help"])
        assert result.exit_code == 0
        assert "--dangerously-skip-permissions" in result.output
        assert "--allow-hierarchical-permissions" in result.output

    def test_attach_help(self):
        result = self.runner.invoke(sprint_group, ["attach", "--help"])
        assert result.exit_code == 0
        assert "tmux" in result.output.lower() or "session" in result.output.lower()

    def test_status_help(self):
        result = self.runner.invoke(sprint_group, ["status", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output.lower()

    def test_logs_help(self):
        result = self.runner.invoke(sprint_group, ["logs", "--help"])
        assert result.exit_code == 0
        assert "--lines" in result.output or "-n" in result.output
        assert "--follow" in result.output or "-f" in result.output

    def test_logs_help_defaults(self):
        result = self.runner.invoke(sprint_group, ["logs", "--help"])
        assert result.exit_code == 0
        assert "50" in result.output  # default lines

    def test_kill_help(self):
        result = self.runner.invoke(sprint_group, ["kill", "--help"])
        assert result.exit_code == 0
        assert "--force" in result.output

    def test_all_subcommands_exit_cleanly(self):
        """All 5 subcommands respond to --help with exit code 0."""
        for subcmd in ["run", "attach", "status", "logs", "kill"]:
            result = self.runner.invoke(sprint_group, [subcmd, "--help"])
            assert result.exit_code == 0, f"{subcmd} --help failed: {result.output}"

    def test_invalid_subcommand(self):
        result = self.runner.invoke(sprint_group, ["nonexistent"])
        assert result.exit_code != 0
