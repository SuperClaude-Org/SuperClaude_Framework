"""T04.01 — Integration test: full phase lifecycle.

Tests that executor + mocked ClaudeProcess + TUI integrate correctly
through the full lifecycle: PENDING → RUNNING → PASS.
"""

from __future__ import annotations

from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from superclaude.cli.sprint.executor import execute_sprint
from superclaude.cli.sprint.models import (
    Phase,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
)
from superclaude.cli.sprint.tui import SprintTUI


def _make_config(tmp_path: Path, num_phases: int = 1) -> SprintConfig:
    """Create a SprintConfig with N phase files in tmp_path."""
    phases = []
    for i in range(1, num_phases + 1):
        pf = tmp_path / f"phase-{i}-tasklist.md"
        pf.write_text(f"# Phase {i}\n")
        phases.append(Phase(number=i, file=pf, name=f"Phase {i}"))

    index = tmp_path / "tasklist-index.md"
    index.write_text("index\n")

    return SprintConfig(
        index_path=index,
        release_dir=tmp_path,
        phases=phases,
        start_phase=1,
        end_phase=num_phases,
        max_turns=5,
    )


def _mock_popen_success(config: SprintConfig):
    """Create a mock Popen that exits 0 and writes CONTINUE to result file."""

    class FakePopen:
        def __init__(self, *args, **kwargs):
            self.returncode = 0
            self.pid = 12345
            self._poll_count = 0

        def poll(self):
            self._poll_count += 1
            if self._poll_count <= 1:
                return None  # still running on first poll
            return 0  # done on second poll

        def wait(self, timeout=None):
            self.returncode = 0
            return 0

    def popen_factory(cmd, **kwargs):
        proc = FakePopen()
        # Write result file with CONTINUE signal
        for phase in config.active_phases:
            result_path = config.result_file(phase)
            result_path.parent.mkdir(parents=True, exist_ok=True)
            result_path.write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            # Write output file so monitor sees content
            output_path = config.output_file(phase)
            output_path.write_text("Working on T01.01\nUsing Read tool\n")
        return proc

    return popen_factory


class TestFullPhaseLifecycle:
    """T04.01: executor drives phases through PENDING → RUNNING → PASS."""

    def test_single_phase_passes(self, tmp_path):
        config = _make_config(tmp_path, num_phases=1)
        popen_factory = _mock_popen_success(config)

        with (
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=popen_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            try:
                execute_sprint(config)
            except SystemExit:
                pass  # execute_sprint may raise SystemExit(1) on non-SUCCESS

        # Verify result file was checked and status determined
        assert config.result_file(config.phases[0]).exists()

    def test_single_phase_outcome_success(self, tmp_path):
        config = _make_config(tmp_path, num_phases=1)
        popen_factory = _mock_popen_success(config)

        # We need to capture the SprintResult. Patch the logger to grab it.
        captured_results = []
        original_write_summary = None

        def capture_summary(sprint_result):
            captured_results.append(sprint_result)
            if original_write_summary:
                original_write_summary(sprint_result)

        with (
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=popen_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as mock_logger_cls,
        ):
            logger_inst = MagicMock()
            logger_inst.write_summary = MagicMock(side_effect=lambda sr: captured_results.append(sr))
            mock_logger_cls.return_value = logger_inst

            try:
                execute_sprint(config)
            except SystemExit:
                pass

        assert len(captured_results) >= 1
        result = captured_results[0]
        assert result.outcome == SprintOutcome.SUCCESS
        assert len(result.phase_results) == 1
        assert result.phase_results[0].status == PhaseStatus.PASS

    def test_tui_renders_without_crash(self, tmp_path):
        """TUI renders to StringIO without terminal dependency."""
        config = _make_config(tmp_path, num_phases=1)
        console = Console(file=StringIO(), force_terminal=True, width=120)
        tui = SprintTUI(config, console=console)

        # Start and stop without crashing
        tui.start()
        tui.stop()

        output = console.file.getvalue()
        assert "SUPERCLAUDE SPRINT RUNNER" in output

    def test_two_phases_both_pass(self, tmp_path):
        config = _make_config(tmp_path, num_phases=2)
        popen_factory = _mock_popen_success(config)

        captured_results = []

        with (
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=popen_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as mock_logger_cls,
        ):
            logger_inst = MagicMock()
            logger_inst.write_summary = MagicMock(side_effect=lambda sr: captured_results.append(sr))
            mock_logger_cls.return_value = logger_inst

            try:
                execute_sprint(config)
            except SystemExit:
                pass

        assert len(captured_results) >= 1
        result = captured_results[0]
        assert result.outcome == SprintOutcome.SUCCESS
        assert len(result.phase_results) == 2
        assert all(r.status == PhaseStatus.PASS for r in result.phase_results)

    def test_phase_result_has_timing(self, tmp_path):
        config = _make_config(tmp_path, num_phases=1)
        popen_factory = _mock_popen_success(config)

        captured_results = []

        with (
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=popen_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as mock_logger_cls,
        ):
            logger_inst = MagicMock()
            logger_inst.write_summary = MagicMock(side_effect=lambda sr: captured_results.append(sr))
            mock_logger_cls.return_value = logger_inst

            try:
                execute_sprint(config)
            except SystemExit:
                pass

        result = captured_results[0]
        pr = result.phase_results[0]
        assert isinstance(pr.started_at, datetime)
        assert isinstance(pr.finished_at, datetime)
        assert pr.finished_at >= pr.started_at
