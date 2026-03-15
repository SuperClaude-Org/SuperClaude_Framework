"""Tests for pipeline/process.py -- ClaudeProcess output_format and command building."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.cli.pipeline.process import ClaudeProcess


class TestClaudeProcessCommand:
    def test_default_output_format_stream_json(self, tmp_path):
        p = ClaudeProcess(
            prompt="test",
            output_file=tmp_path / "out.txt",
            error_file=tmp_path / "err.txt",
        )
        assert p.output_format == "stream-json"
        cmd = p.build_command()
        idx = cmd.index("--output-format")
        assert cmd[idx + 1] == "stream-json"

    def test_text_output_format(self, tmp_path):
        p = ClaudeProcess(
            prompt="test",
            output_file=tmp_path / "out.txt",
            error_file=tmp_path / "err.txt",
            output_format="text",
        )
        cmd = p.build_command()
        idx = cmd.index("--output-format")
        assert cmd[idx + 1] == "text"

    def test_required_flags(self, tmp_path):
        p = ClaudeProcess(
            prompt="hello",
            output_file=tmp_path / "out.txt",
            error_file=tmp_path / "err.txt",
        )
        cmd = p.build_command()
        assert "claude" in cmd
        assert "--print" in cmd
        assert "--verbose" in cmd
        assert "--no-session-persistence" in cmd
        assert "--tools" in cmd
        assert "default" in cmd
        assert "--dangerously-skip-permissions" in cmd
        assert "-p" in cmd
        assert "hello" in cmd

    def test_with_model(self, tmp_path):
        p = ClaudeProcess(
            prompt="test",
            output_file=tmp_path / "out.txt",
            error_file=tmp_path / "err.txt",
            model="opus",
        )
        cmd = p.build_command()
        assert "--model" in cmd
        idx = cmd.index("--model")
        assert cmd[idx + 1] == "opus"

    def test_without_model(self, tmp_path):
        p = ClaudeProcess(
            prompt="test",
            output_file=tmp_path / "out.txt",
            error_file=tmp_path / "err.txt",
        )
        cmd = p.build_command()
        assert "--model" not in cmd

    def test_extra_args(self, tmp_path):
        p = ClaudeProcess(
            prompt="test",
            output_file=tmp_path / "out.txt",
            error_file=tmp_path / "err.txt",
            extra_args=["--file", "/tmp/spec.md"],
        )
        cmd = p.build_command()
        assert "--file" in cmd
        assert "/tmp/spec.md" in cmd

    def test_max_turns_in_command(self, tmp_path):
        p = ClaudeProcess(
            prompt="test",
            output_file=tmp_path / "out.txt",
            error_file=tmp_path / "err.txt",
            max_turns=100,
        )
        cmd = p.build_command()
        idx = cmd.index("--max-turns")
        assert cmd[idx + 1] == "100"

    def test_tools_default_in_command(self, tmp_path):
        p = ClaudeProcess(
            prompt="test",
            output_file=tmp_path / "out.txt",
            error_file=tmp_path / "err.txt",
        )
        cmd = p.build_command()
        assert "--tools" in cmd
        assert cmd[cmd.index("--tools") + 1] == "default"


class TestClaudeProcessEnv:
    def test_removes_claudecode_env(self, tmp_path):
        p = ClaudeProcess(
            prompt="test",
            output_file=tmp_path / "out.txt",
            error_file=tmp_path / "err.txt",
        )
        with patch.dict("os.environ", {"CLAUDECODE": "1", "CLAUDE_CODE_ENTRYPOINT": "cli"}):
            env = p.build_env()
            assert "CLAUDECODE" not in env
            assert "CLAUDE_CODE_ENTRYPOINT" not in env


class TestClaudeProcessStreamJsonCompat:
    """Verify stream-json output produces identical subprocess args to sprint."""

    def test_stream_json_matches_sprint_flags(self, tmp_path):
        p = ClaudeProcess(
            prompt="/sc:task-unified test prompt",
            output_file=tmp_path / "out.txt",
            error_file=tmp_path / "err.txt",
            max_turns=50,
            output_format="stream-json",
            permission_flag="--dangerously-skip-permissions",
        )
        cmd = p.build_command()

        # These flags must all be present for sprint compatibility
        assert cmd[0] == "claude"
        assert "--print" in cmd
        assert "--verbose" in cmd
        assert "--dangerously-skip-permissions" in cmd
        assert "--no-session-persistence" in cmd
        assert "--tools" in cmd
        assert "default" in cmd
        assert "--output-format" in cmd
        idx = cmd.index("--output-format")
        assert cmd[idx + 1] == "stream-json"
        assert "--max-turns" in cmd
        idx2 = cmd.index("--max-turns")
        assert cmd[idx2 + 1] == "50"
