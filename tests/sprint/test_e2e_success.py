"""T07.01 — E2E test: 3-phase sprint to completion.

Full end-to-end test: mock Claude subprocess executes a 3-phase sprint;
verifies execution log (JSONL events + Markdown table) and final outcome.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from superclaude.cli.sprint.executor import execute_sprint
from superclaude.cli.sprint.models import (
    Phase,
    SprintConfig,
)


def _make_config(tmp_path: Path) -> SprintConfig:
    phases = []
    for i in range(1, 4):
        pf = tmp_path / f"phase-{i}-tasklist.md"
        pf.write_text(f"# Phase {i}: Test Phase\n")
        phases.append(Phase(number=i, file=pf, name=f"Test Phase {i}"))

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


class _FakePopenSuccess:
    def __init__(self):
        self.returncode = 0
        self.pid = 20000
        self._poll_count = 0

    def poll(self):
        self._poll_count += 1
        if self._poll_count <= 1:
            return None
        return 0

    def wait(self, timeout=None):
        self.returncode = 0
        return 0


def _popen_factory_all_pass(config: SprintConfig):
    """Popen factory: all phases pass with CONTINUE signal."""
    call_count = [0]

    def factory(cmd, **kwargs):
        call_count[0] += 1
        phase = config.phases[call_count[0] - 1]

        config.results_dir.mkdir(parents=True, exist_ok=True)

        # Write result file with CONTINUE signal
        result_path = config.result_file(phase)
        result_path.write_text(
            "---\nstatus: PASS\n---\n\nEXIT_RECOMMENDATION: CONTINUE\n"
        )

        # Write output file with realistic content
        output_path = config.output_file(phase)
        output_path.write_text(
            f"Working on T0{call_count[0]}.01\n"
            f"Using Read tool to examine files\n"
            f"modified `src/module{call_count[0]}.py`\n"
            f"Phase {call_count[0]} complete\n"
        )

        return _FakePopenSuccess()

    return factory


class TestE2ESuccess:
    """T07.01: 3-phase sprint completes with SUCCESS outcome."""

    def test_all_phases_pass(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_all_pass(config)

        with (
            patch("superclaude.cli.sprint.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.sprint.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            # Should not raise SystemExit since all pass
            execute_sprint(config)

        # Verify JSONL log exists and is valid
        jsonl_path = config.execution_log_jsonl
        assert jsonl_path.exists()

    def test_jsonl_events_for_each_phase(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_all_pass(config)

        with (
            patch("superclaude.cli.sprint.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.sprint.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            execute_sprint(config)

        jsonl_path = config.execution_log_jsonl
        events = [json.loads(line) for line in jsonl_path.read_text().strip().split("\n")]

        # Should have: sprint_start + 3x(phase_start + phase_complete) + sprint_complete = 8
        # write_phase_start is called when each phase begins RUNNING,
        # producing an additional event beyond what the original test expected.
        assert len(events) == 8

        # First event is sprint_start
        assert events[0]["event"] == "sprint_start"

        # 3 phase_start events (emitted when each phase launches)
        phase_start_events = [e for e in events if e["event"] == "phase_start"]
        assert len(phase_start_events) == 3
        assert [e["phase"] for e in phase_start_events] == [1, 2, 3]

        # 3 phase_complete events
        phase_events = [e for e in events if e["event"] == "phase_complete"]
        assert len(phase_events) == 3
        assert [e["phase"] for e in phase_events] == [1, 2, 3]
        assert all(e["status"] == "pass" for e in phase_events)

        # Last event is sprint_complete
        assert events[-1]["event"] == "sprint_complete"
        assert events[-1]["outcome"] == "success"

    def test_jsonl_lines_are_valid_json(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_all_pass(config)

        with (
            patch("superclaude.cli.sprint.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.sprint.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            execute_sprint(config)

        jsonl_path = config.execution_log_jsonl
        for line in jsonl_path.read_text().strip().split("\n"):
            parsed = json.loads(line)  # Should not raise
            assert isinstance(parsed, dict)

    def test_markdown_log_has_phase_rows(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_all_pass(config)

        with (
            patch("superclaude.cli.sprint.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.sprint.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            execute_sprint(config)

        md_path = config.execution_log_md
        assert md_path.exists()
        content = md_path.read_text()

        # Should contain table header
        assert "| Phase | Status |" in content

        # Should contain 3 phase rows
        assert "Phase 1" in content
        assert "Phase 2" in content
        assert "Phase 3" in content

        # Should contain outcome
        assert "success" in content

    def test_markdown_log_has_outcome(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_all_pass(config)

        with (
            patch("superclaude.cli.sprint.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.sprint.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            execute_sprint(config)

        content = config.execution_log_md.read_text()
        assert "**Outcome**: success" in content

    def test_result_files_created(self, tmp_path):
        config = _make_config(tmp_path)
        factory = _popen_factory_all_pass(config)

        with (
            patch("superclaude.cli.sprint.process.subprocess.Popen", side_effect=factory),
            patch("superclaude.cli.sprint.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            execute_sprint(config)

        # Result files should exist for all 3 phases
        for phase in config.phases:
            assert config.result_file(phase).exists()
            assert config.output_file(phase).exists()
