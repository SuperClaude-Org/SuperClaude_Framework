"""T07.02 — E2E test: failure at phase 2 with resume.

Tests that phase 2 failure produces HALTED outcome, phases 3+ are not
executed, and the execution log contains the correct resume command.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.cli.sprint.executor import execute_sprint
from superclaude.cli.sprint.models import (
    Phase,
    SprintConfig,
)


def _make_config(tmp_path: Path) -> SprintConfig:
    phases = []
    for i in range(1, 4):
        pf = tmp_path / f"phase-{i}-tasklist.md"
        pf.write_text(f"# Phase {i}\n")
        phases.append(Phase(number=i, file=pf, name=f"Phase {i}"))

    index = tmp_path / "tasklist-index.md"
    index.write_text("- phase-1-tasklist.md\n- phase-2-tasklist.md\n- phase-3-tasklist.md\n")

    return SprintConfig(
        index_path=index,
        release_dir=tmp_path,
        phases=phases,
        start_phase=1,
        end_phase=3,
        max_turns=5,
    )


class _FakePopenExit0:
    def __init__(self):
        self.returncode = 0
        self.pid = 30000
        self._poll_count = 0

    def poll(self):
        self._poll_count += 1
        return None if self._poll_count <= 1 else 0

    def wait(self, timeout=None):
        self.returncode = 0
        return 0


class _FakePopenExit1:
    def __init__(self):
        self.returncode = 1
        self.pid = 30001
        self._poll_count = 0

    def poll(self):
        self._poll_count += 1
        return None if self._poll_count <= 1 else 1

    def wait(self, timeout=None):
        self.returncode = 1
        return 1


def _popen_factory_fail_phase2(config: SprintConfig):
    call_count = [0]

    def factory(cmd, **kwargs):
        call_count[0] += 1
        phase = config.phases[call_count[0] - 1]
        config.results_dir.mkdir(parents=True, exist_ok=True)

        output_path = config.output_file(phase)
        output_path.write_text(f"Phase {call_count[0]} output\n")

        if call_count[0] == 2:
            # Phase 2 fails with non-zero exit
            return _FakePopenExit1()
        else:
            result_path = config.result_file(phase)
            result_path.write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            return _FakePopenExit0()

    return factory


class TestE2EHalt:
    """T07.02: Phase 2 failure → HALTED outcome, no phase 3 execution."""

    def test_outcome_halted(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_fail_phase2(config)

        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            with pytest.raises(SystemExit) as exc:
                execute_sprint(config)
            assert exc.value.code == 1

        # Read JSONL to verify
        jsonl_path = config.execution_log_jsonl
        events = [json.loads(line) for line in jsonl_path.read_text().strip().split("\n")]
        summary = [e for e in events if e["event"] == "sprint_complete"]
        assert len(summary) == 1
        assert summary[0]["outcome"] == "halted"

    def test_no_phase3_events(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_fail_phase2(config)

        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            try:
                execute_sprint(config)
            except SystemExit:
                pass

        jsonl_path = config.execution_log_jsonl
        events = [json.loads(line) for line in jsonl_path.read_text().strip().split("\n")]
        phase_events = [e for e in events if e["event"] == "phase_complete"]

        # Only phase 1 and 2 should have events, not phase 3
        assert len(phase_events) == 2
        assert phase_events[0]["phase"] == 1
        assert phase_events[0]["status"] == "pass"
        assert phase_events[1]["phase"] == 2
        assert phase_events[1]["status"] == "error"

    def test_resume_command_in_log(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_fail_phase2(config)

        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            try:
                execute_sprint(config)
            except SystemExit:
                pass

        md_content = config.execution_log_md.read_text()
        assert "**Halted at**: Phase 2" in md_content
        assert "--start 2" in md_content

    def test_markdown_shows_halt_outcome(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_fail_phase2(config)

        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            try:
                execute_sprint(config)
            except SystemExit:
                pass

        md_content = config.execution_log_md.read_text()
        assert "**Outcome**: halted" in md_content

    def test_phase1_passed_in_log(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_fail_phase2(config)

        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            try:
                execute_sprint(config)
            except SystemExit:
                pass

        jsonl_path = config.execution_log_jsonl
        events = [json.loads(line) for line in jsonl_path.read_text().strip().split("\n")]
        phase_events = [e for e in events if e["event"] == "phase_complete"]
        assert phase_events[0]["status"] == "pass"
