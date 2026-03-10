"""Tests for sprint process management — command construction, env, signals, context injection."""

import builtins
import signal
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from superclaude.cli.sprint.models import (
    GateOutcome,
    Phase,
    SprintConfig,
    TaskEntry,
    TaskResult,
    TaskStatus,
)
from superclaude.cli.sprint.process import (
    ClaudeProcess,
    SignalHandler,
    build_task_context,
    compress_context_summary,
    get_git_diff_context,
)


def _make_config(**kwargs):
    defaults = dict(
        index_path=Path("/tmp/tasklist-index.md"),
        release_dir=Path("/tmp/release"),
        phases=[Phase(number=1, file=Path("/tmp/phase-1-tasklist.md"))],
        max_turns=50,
    )
    defaults.update(kwargs)
    return SprintConfig(**defaults)


class TestClaudeProcess:
    """Test command construction and environment building."""

    def test_build_command_required_flags(self):
        config = _make_config()
        phase = config.phases[0]
        proc = ClaudeProcess(config, phase)

        cmd = proc.build_command()
        assert "claude" in cmd
        assert "--print" in cmd
        assert "--no-session-persistence" in cmd
        assert "--output-format" in cmd
        assert "stream-json" in cmd
        assert "--max-turns" in cmd
        assert "50" in cmd

    def test_build_command_permission_flag(self):
        config = _make_config(permission_flag="--dangerously-skip-permissions")
        proc = ClaudeProcess(config, config.phases[0])
        cmd = proc.build_command()
        assert "--dangerously-skip-permissions" in cmd

    def test_build_command_with_model(self):
        config = _make_config(model="claude-sonnet")
        proc = ClaudeProcess(config, config.phases[0])
        cmd = proc.build_command()
        assert "--model" in cmd
        assert "claude-sonnet" in cmd

    def test_build_command_without_model(self):
        config = _make_config(model="")
        proc = ClaudeProcess(config, config.phases[0])
        cmd = proc.build_command()
        assert "--model" not in cmd

    def test_build_env_claudecode_removed(self):
        config = _make_config()
        proc = ClaudeProcess(config, config.phases[0])
        env = proc.build_env()
        assert "CLAUDECODE" not in env

    def test_build_prompt_contains_task_unified(self):
        config = _make_config()
        proc = ClaudeProcess(config, config.phases[0])
        prompt = proc.build_prompt()
        assert "/sc:task-unified" in prompt

    def test_build_prompt_contains_compliance_strict(self):
        config = _make_config()
        proc = ClaudeProcess(config, config.phases[0])
        prompt = proc.build_prompt()
        assert "--compliance strict" in prompt

    def test_timeout_calculation(self):
        config = _make_config(max_turns=50)
        proc = ClaudeProcess(config, config.phases[0])
        # 50 * 120 + 300 = 6300
        assert proc.timeout_seconds == 6300

    def test_timeout_calculation_custom(self):
        config = _make_config(max_turns=100)
        proc = ClaudeProcess(config, config.phases[0])
        assert proc.timeout_seconds == 12300


class TestClaudeProcessPlatformFallback:
    def test_start_without_setpgrp_fallback(self, tmp_path):
        config = _make_config(
            release_dir=tmp_path,
            phases=[Phase(number=1, file=tmp_path / "phase-1-tasklist.md")],
        )
        config.phases[0].file.write_text("# Phase 1\n")
        proc = ClaudeProcess(config, config.phases[0])

        fake_process = MagicMock()
        with (
            patch("superclaude.cli.pipeline.process.hasattr", side_effect=lambda obj, name: False if obj.__name__ == "os" and name == "setpgrp" else builtins.hasattr(obj, name)),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", return_value=fake_process) as mock_popen,
        ):
            proc.start()

        kwargs = mock_popen.call_args.kwargs
        assert "preexec_fn" not in kwargs

    def test_terminate_non_unix_fallback_calls_process_methods(self, tmp_path):
        config = _make_config(
            release_dir=tmp_path,
            phases=[Phase(number=1, file=tmp_path / "phase-1-tasklist.md")],
        )
        config.phases[0].file.write_text("# Phase 1\n")
        proc = ClaudeProcess(config, config.phases[0])

        fake_process = MagicMock()
        fake_process.pid = 43210
        fake_process.poll.return_value = None
        proc._process = fake_process

        with patch(
            "superclaude.cli.pipeline.process.hasattr",
            side_effect=lambda obj, name: False
            if obj.__name__ == "os" and name in {"getpgid", "killpg"}
            else builtins.hasattr(obj, name),
        ):
            proc.terminate()

        fake_process.terminate.assert_called_once()
        fake_process.wait.assert_called()


class TestSignalHandler:
    """Test signal handler registration and flag management."""

    def test_initial_state(self):
        handler = SignalHandler()
        assert handler.shutdown_requested is False

    def test_install_uninstall(self):
        handler = SignalHandler()
        original_sigint = signal.getsignal(signal.SIGINT)

        handler.install()
        # Signal handler should be changed
        assert signal.getsignal(signal.SIGINT) != original_sigint

        handler.uninstall()
        # Should be restored
        current = signal.getsignal(signal.SIGINT)
        assert current == original_sigint

    def test_handle_sets_flag(self):
        handler = SignalHandler()
        handler.install()

        try:
            # Directly call the handler
            handler._handle(signal.SIGINT, None)
            assert handler.shutdown_requested is True
        finally:
            handler.uninstall()

    def test_idempotent_handle(self):
        handler = SignalHandler()
        handler.install()

        try:
            handler._handle(signal.SIGINT, None)
            handler._handle(signal.SIGTERM, None)
            assert handler.shutdown_requested is True
        finally:
            handler.uninstall()


# ---------------------------------------------------------------------------
# Helper factories for context injection tests
# ---------------------------------------------------------------------------


def _make_task_entry(**kwargs) -> TaskEntry:
    defaults = dict(task_id="T01.01", title="Test task")
    defaults.update(kwargs)
    return TaskEntry(**defaults)


def _make_task_result(**kwargs) -> TaskResult:
    now = datetime.now(timezone.utc)
    defaults = dict(
        task=_make_task_entry(),
        status=TaskStatus.PASS,
        turns_consumed=10,
        exit_code=0,
        started_at=now - timedelta(seconds=30),
        finished_at=now,
        gate_outcome=GateOutcome.PASS,
    )
    defaults.update(kwargs)
    return TaskResult(**defaults)


# ---------------------------------------------------------------------------
# Context Injection (T04.01)
# ---------------------------------------------------------------------------


class TestBuildTaskContext:
    """Tests for build_task_context()."""

    def test_context_injection_empty_results(self):
        """No prior results produces empty context."""
        ctx = build_task_context([])
        assert ctx == ""

    def test_context_injection_single_result(self):
        """Single prior result appears in context with full detail."""
        results = [_make_task_result(
            task=_make_task_entry(task_id="T01.01", title="Setup"),
            status=TaskStatus.PASS,
            gate_outcome=GateOutcome.PASS,
        )]
        ctx = build_task_context(results)
        assert "## Prior Task Context" in ctx
        assert "T01.01" in ctx
        assert "Setup" in ctx
        assert "### Gate Outcomes" in ctx
        assert "T01.01: pass" in ctx

    def test_context_injection_multiple_results(self):
        """Multiple prior results all appear in context."""
        results = [
            _make_task_result(task=_make_task_entry(task_id="T01.01", title="First")),
            _make_task_result(task=_make_task_entry(task_id="T01.02", title="Second")),
        ]
        ctx = build_task_context(results)
        assert "T01.01" in ctx
        assert "T01.02" in ctx
        assert "First" in ctx
        assert "Second" in ctx

    def test_context_injection_gate_outcomes_visible(self):
        """Gate outcomes (pass/fail/deferred) are visible in context."""
        results = [
            _make_task_result(
                task=_make_task_entry(task_id="T01.01"),
                gate_outcome=GateOutcome.PASS,
            ),
            _make_task_result(
                task=_make_task_entry(task_id="T01.02"),
                gate_outcome=GateOutcome.FAIL,
            ),
            _make_task_result(
                task=_make_task_entry(task_id="T01.03"),
                gate_outcome=GateOutcome.DEFERRED,
            ),
        ]
        ctx = build_task_context(results)
        assert "T01.01: pass" in ctx
        assert "T01.02: fail" in ctx
        assert "T01.03: deferred" in ctx

    def test_context_injection_remediation_history(self):
        """Remediation history appears for tasks with reimbursement."""
        results = [
            _make_task_result(
                task=_make_task_entry(task_id="T01.01"),
                reimbursement_amount=5,
            ),
            _make_task_result(
                task=_make_task_entry(task_id="T01.02"),
                reimbursement_amount=0,
            ),
        ]
        ctx = build_task_context(results)
        assert "### Remediation History" in ctx
        assert "T01.01: reimbursed 5 turns" in ctx
        assert "T01.02" not in ctx.split("### Remediation History")[1]

    def test_context_injection_no_remediation_section_when_none(self):
        """No remediation section when no tasks had reimbursement."""
        results = [_make_task_result(reimbursement_amount=0)]
        ctx = build_task_context(results)
        assert "### Remediation History" not in ctx

    def test_context_injection_includes_git_diff(self):
        """Git diff summary is included when start_commit is provided."""
        results = [_make_task_result()]
        with patch(
            "superclaude.cli.sprint.process._subprocess.run"
        ) as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=" file1.py | 10 ++++\n file2.py | 5 ++\n 2 files changed\n",
            )
            ctx = build_task_context(results, start_commit="abc123")
        assert "### Git Changes Since Sprint Start" in ctx
        assert "file1.py" in ctx

    def test_context_injection_progressive_compression(self):
        """Tasks beyond threshold are compressed in context."""
        results = [
            _make_task_result(
                task=_make_task_entry(task_id=f"T01.{i:02d}", title=f"Task {i}"),
                gate_outcome=GateOutcome.PASS,
            )
            for i in range(1, 7)  # 6 tasks, threshold=3
        ]
        ctx = build_task_context(results, compress_threshold=3)
        # Older tasks should be compressed
        assert "Earlier Tasks (compressed)" in ctx
        # Recent tasks should have full detail
        assert "Recent Tasks" in ctx


# ---------------------------------------------------------------------------
# Git Diff Context (T04.04)
# ---------------------------------------------------------------------------


class TestGetGitDiffContext:
    """Tests for get_git_diff_context()."""

    def test_git_diff_context_success(self):
        """Successful git diff returns structured markdown section."""
        with patch("superclaude.cli.sprint.process._subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=" src/models.py | 15 +++++++++\n 1 file changed\n",
            )
            result = get_git_diff_context("HEAD~3")
        assert "### Git Changes Since Sprint Start" in result
        assert "src/models.py" in result
        assert "```" in result

    def test_git_diff_context_empty_diff(self):
        """Empty diff returns empty string."""
        with patch("superclaude.cli.sprint.process._subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            result = get_git_diff_context("HEAD")
        assert result == ""

    def test_git_diff_context_non_zero_exit(self):
        """Non-zero exit code returns empty string."""
        with patch("superclaude.cli.sprint.process._subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=128, stdout="")
            result = get_git_diff_context("invalid-ref")
        assert result == ""

    def test_git_diff_context_git_not_found(self):
        """FileNotFoundError (git not installed) returns empty string."""
        with patch(
            "superclaude.cli.sprint.process._subprocess.run",
            side_effect=FileNotFoundError,
        ):
            result = get_git_diff_context("HEAD")
        assert result == ""

    def test_git_diff_context_timeout(self):
        """Timeout returns empty string."""
        import subprocess
        with patch(
            "superclaude.cli.sprint.process._subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="git", timeout=10),
        ):
            result = get_git_diff_context("HEAD")
        assert result == ""


# ---------------------------------------------------------------------------
# Progressive Summarization (T04.05)
# ---------------------------------------------------------------------------


class TestCompressContextSummary:
    """Tests for compress_context_summary()."""

    def test_progressive_summary_empty(self):
        """Empty results produce empty string."""
        assert compress_context_summary([]) == ""

    def test_progressive_summary_under_threshold(self):
        """Results within threshold are all full detail."""
        results = [
            _make_task_result(task=_make_task_entry(task_id=f"T01.{i:02d}"))
            for i in range(1, 4)  # 3 results, keep_recent=3
        ]
        summary = compress_context_summary(results, keep_recent=3)
        assert "Earlier Tasks (compressed)" not in summary
        assert "Recent Tasks" in summary

    def test_progressive_summary_over_threshold(self):
        """Results over threshold compress older tasks."""
        results = [
            _make_task_result(task=_make_task_entry(task_id=f"T01.{i:02d}"))
            for i in range(1, 8)  # 7 results, keep_recent=3
        ]
        summary = compress_context_summary(results, keep_recent=3)
        assert "Earlier Tasks (compressed)" in summary
        assert "Recent Tasks" in summary

    def test_progressive_summary_preserves_gate_outcomes(self):
        """Compressed summaries still include gate outcome."""
        results = [
            _make_task_result(
                task=_make_task_entry(task_id=f"T01.{i:02d}"),
                gate_outcome=GateOutcome.PASS,
            )
            for i in range(1, 8)
        ]
        summary = compress_context_summary(results, keep_recent=3)
        # Compressed older tasks should still show gate outcome
        assert "gate: pass" in summary

    def test_progressive_summary_recent_full_detail(self):
        """Most recent N tasks have full detail."""
        results = [
            _make_task_result(
                task=_make_task_entry(task_id=f"T01.{i:02d}", title=f"Task {i}"),
                turns_consumed=i * 5,
            )
            for i in range(1, 12)  # 11 tasks
        ]
        summary = compress_context_summary(results, keep_recent=3)
        # Last 3 tasks should have full detail (### heading format)
        assert "### T01.09" in summary
        assert "### T01.10" in summary
        assert "### T01.11" in summary
        # First task should be compressed (no ### heading)
        assert "### T01.01" not in summary

    def test_progressive_summary_bounded_size(self):
        """Context size does not grow linearly beyond threshold."""
        small_results = [
            _make_task_result(task=_make_task_entry(task_id=f"T01.{i:02d}"))
            for i in range(1, 5)  # 4 tasks
        ]
        large_results = [
            _make_task_result(task=_make_task_entry(task_id=f"T01.{i:02d}"))
            for i in range(1, 15)  # 14 tasks
        ]
        small_summary = compress_context_summary(small_results, keep_recent=3)
        large_summary = compress_context_summary(large_results, keep_recent=3)
        # Large should not be proportionally larger (14/4 = 3.5x)
        # With compression it should be much less than 3.5x
        ratio = len(large_summary) / len(small_summary)
        assert ratio < 3.0, f"Compression ratio {ratio:.1f} exceeds 3.0x"
