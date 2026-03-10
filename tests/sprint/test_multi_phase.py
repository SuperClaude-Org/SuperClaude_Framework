"""Characterization tests for multi-phase sequencing and halt propagation.

Pins current behavior of phase iteration ordering and halt propagation
across >1 phase before any refactoring in Phase 2.
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


def _make_config(tmp_path: Path, num_phases: int = 3) -> SprintConfig:
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


class TestThreePhaseHappyPath:
    """Verify phases execute in strict sequential order: 1 -> 2 -> 3."""

    def test_three_phase_happy_path(self, tmp_path):
        config = _make_config(tmp_path, num_phases=3)
        phase_execution_order = []

        class _PassPopen:
            def __init__(self):
                self.returncode = 0
                self.pid = 5000
                self._poll = 0

            def poll(self):
                self._poll += 1
                return None if self._poll <= 1 else 0

            def wait(self, timeout=None):
                self.returncode = 0
                return 0

        def _factory(*args, **kwargs):
            # Determine which phase we're on from directory contents
            for phase in config.phases:
                result_file = config.result_file(phase)
                if not result_file.exists():
                    phase_execution_order.append(phase.number)
                    config.results_dir.mkdir(parents=True, exist_ok=True)
                    result_file.write_text("EXIT_RECOMMENDATION: CONTINUE\n")
                    config.output_file(phase).write_text(f"output phase {phase.number}\n")
                    break
            return _PassPopen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger
            execute_sprint(config)

        result = captured[0]
        # All 3 phases should have executed and passed
        assert result.outcome == SprintOutcome.SUCCESS
        assert len(result.phase_results) == 3
        # Phases executed in order
        assert phase_execution_order == [1, 2, 3]
        # All phases passed
        for pr in result.phase_results:
            assert pr.status == PhaseStatus.PASS


class TestHaltAtPhaseThree:
    """Verify halt at phase 3 propagates correctly: phases 1-2 pass, phase 3 halts."""

    def test_halt_at_phase_three(self, tmp_path):
        config = _make_config(tmp_path, num_phases=3)
        phase_counter = [0]

        class _Popen:
            def __init__(self):
                self.returncode = 0
                self.pid = 6000
                self._poll = 0

            def poll(self):
                self._poll += 1
                return None if self._poll <= 1 else 0

            def wait(self, timeout=None):
                self.returncode = 0
                return 0

        def _factory(*args, **kwargs):
            phase_counter[0] += 1
            current_phase = config.phases[phase_counter[0] - 1]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.output_file(current_phase).write_text(f"output phase {current_phase.number}\n")

            if phase_counter[0] <= 2:
                config.result_file(current_phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            else:
                config.result_file(current_phase).write_text("EXIT_RECOMMENDATION: HALT\n")
            return _Popen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger
            with pytest.raises(SystemExit) as exc:
                execute_sprint(config)
            assert exc.value.code == 1

        result = captured[0]
        # Sprint should be halted
        assert result.outcome == SprintOutcome.HALTED
        assert result.halt_phase == 3
        # All 3 phases should have results (phase 3 ran but halted)
        assert len(result.phase_results) == 3
        # First two passed, third halted
        assert result.phase_results[0].status == PhaseStatus.PASS
        assert result.phase_results[1].status == PhaseStatus.PASS
        assert result.phase_results[2].status == PhaseStatus.HALT
