"""Characterization tests for DiagnosticCollector integration in sprint executor.

Pins current behavior: failure triggers DiagnosticCollector.collect(),
and exceptions in diagnostics do not abort the sprint.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.sprint.executor import execute_sprint
from superclaude.cli.sprint.models import (
    Phase,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
)


def _make_config(tmp_path: Path, num_phases: int = 1) -> SprintConfig:
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


class _HaltPopen:
    def __init__(self):
        self.returncode = 0
        self.pid = 3000
        self._poll = 0

    def poll(self):
        self._poll += 1
        return None if self._poll <= 1 else 0

    def wait(self, timeout=None):
        self.returncode = 0
        return 0


class TestFailureTriggersCollector:
    """Phase failure must trigger DiagnosticCollector.collect()."""

    def test_failure_triggers_collector(self, tmp_path):
        config = _make_config(tmp_path)

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: HALT\n")
            config.output_file(phase).write_text("output\n")
            return _HaltPopen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
            patch("superclaude.cli.sprint.executor.DiagnosticCollector") as collector_cls,
            patch("superclaude.cli.sprint.executor.FailureClassifier") as classifier_cls,
            patch("superclaude.cli.sprint.executor.ReportGenerator") as reporter_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger

            collector_mock = MagicMock()
            bundle_mock = MagicMock()
            collector_mock.collect.return_value = bundle_mock
            collector_cls.return_value = collector_mock

            classifier_mock = MagicMock()
            classifier_cls.return_value = classifier_mock

            reporter_mock = MagicMock()
            reporter_cls.return_value = reporter_mock

            with pytest.raises(SystemExit) as exc:
                execute_sprint(config)
            assert exc.value.code == 1

        result = captured[0]
        assert result.outcome == SprintOutcome.HALTED

        # DiagnosticCollector.collect() must have been called
        collector_mock.collect.assert_called_once()
        # FailureClassifier.classify() must have been called with the bundle
        classifier_mock.classify.assert_called_once_with(bundle_mock)
        # ReportGenerator.write() must have been called
        reporter_mock.write.assert_called_once()


class TestDiagnosticsExceptionNonFatal:
    """Exception in DiagnosticCollector.collect() must NOT prevent sprint from halting cleanly."""

    def test_diagnostics_exception_non_fatal(self, tmp_path):
        config = _make_config(tmp_path)

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: HALT\n")
            config.output_file(phase).write_text("output\n")
            return _HaltPopen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
            patch("superclaude.cli.sprint.executor.DiagnosticCollector") as collector_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger

            # Make DiagnosticCollector.collect() raise an exception
            collector_mock = MagicMock()
            collector_mock.collect.side_effect = RuntimeError("Diagnostics failed!")
            collector_cls.return_value = collector_mock

            with pytest.raises(SystemExit) as exc:
                execute_sprint(config)
            assert exc.value.code == 1

        result = captured[0]
        # Sprint should still halt cleanly even though diagnostics failed
        assert result.outcome == SprintOutcome.HALTED
        assert result.halt_phase == 1
        assert result.phase_results[0].status == PhaseStatus.HALT
