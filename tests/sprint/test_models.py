"""Unit tests for sprint data models.

Covers all 7 types (PhaseStatus, SprintOutcome, Phase, SprintConfig,
PhaseResult, SprintResult, MonitorState) and their property methods.
"""

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from superclaude.cli.sprint.models import (
    MonitorState,
    Phase,
    PhaseResult,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
    SprintResult,
)

# ---------------------------------------------------------------------------
# PhaseStatus enum
# ---------------------------------------------------------------------------


class TestPhaseStatus:
    """Tests for PhaseStatus enum properties."""

    def test_all_members_present(self):
        expected = {
            "PENDING",
            "RUNNING",
            "PASS",
            "PASS_NO_SIGNAL",
            "PASS_NO_REPORT",
            "HALT",
            "TIMEOUT",
            "ERROR",
            "SKIPPED",
        }
        assert {m.name for m in PhaseStatus} == expected

    @pytest.mark.parametrize(
        "status,expected",
        [
            (PhaseStatus.PENDING, False),
            (PhaseStatus.RUNNING, False),
            (PhaseStatus.PASS, True),
            (PhaseStatus.PASS_NO_SIGNAL, True),
            (PhaseStatus.PASS_NO_REPORT, True),
            (PhaseStatus.HALT, True),
            (PhaseStatus.TIMEOUT, True),
            (PhaseStatus.ERROR, True),
            (PhaseStatus.SKIPPED, True),
        ],
    )
    def test_is_terminal(self, status, expected):
        assert status.is_terminal is expected

    @pytest.mark.parametrize(
        "status,expected",
        [
            (PhaseStatus.PENDING, False),
            (PhaseStatus.RUNNING, False),
            (PhaseStatus.PASS, True),
            (PhaseStatus.PASS_NO_SIGNAL, True),
            (PhaseStatus.PASS_NO_REPORT, True),
            (PhaseStatus.HALT, False),
            (PhaseStatus.TIMEOUT, False),
            (PhaseStatus.ERROR, False),
            (PhaseStatus.SKIPPED, False),
        ],
    )
    def test_is_success(self, status, expected):
        assert status.is_success is expected

    @pytest.mark.parametrize(
        "status,expected",
        [
            (PhaseStatus.PENDING, False),
            (PhaseStatus.RUNNING, False),
            (PhaseStatus.PASS, False),
            (PhaseStatus.PASS_NO_SIGNAL, False),
            (PhaseStatus.PASS_NO_REPORT, False),
            (PhaseStatus.HALT, True),
            (PhaseStatus.TIMEOUT, True),
            (PhaseStatus.ERROR, True),
            (PhaseStatus.SKIPPED, False),
        ],
    )
    def test_is_failure(self, status, expected):
        assert status.is_failure is expected

    def test_values(self):
        assert PhaseStatus.PENDING.value == "pending"
        assert PhaseStatus.PASS.value == "pass"
        assert PhaseStatus.HALT.value == "halt"


# ---------------------------------------------------------------------------
# SprintOutcome enum
# ---------------------------------------------------------------------------


class TestSprintOutcome:
    """Tests for SprintOutcome enum."""

    def test_all_members_present(self):
        expected = {"SUCCESS", "HALTED", "INTERRUPTED", "ERROR"}
        assert {m.name for m in SprintOutcome} == expected

    def test_values(self):
        assert SprintOutcome.SUCCESS.value == "success"
        assert SprintOutcome.HALTED.value == "halted"
        assert SprintOutcome.INTERRUPTED.value == "interrupted"
        assert SprintOutcome.ERROR.value == "error"


# ---------------------------------------------------------------------------
# Phase dataclass
# ---------------------------------------------------------------------------


class TestPhase:
    """Tests for Phase dataclass."""

    def test_basic_creation(self):
        p = Phase(number=1, file=Path("/tmp/phase-1.md"))
        assert p.number == 1
        assert p.file == Path("/tmp/phase-1.md")
        assert p.name == ""

    def test_with_name(self):
        p = Phase(number=2, file=Path("/tmp/p2.md"), name="Backend Core")
        assert p.name == "Backend Core"

    def test_basename(self):
        p = Phase(number=1, file=Path("/some/dir/phase-1-tasklist.md"))
        assert p.basename == "phase-1-tasklist.md"

    def test_display_name_with_name(self):
        p = Phase(number=1, file=Path("/tmp/p1.md"), name="Foundation")
        assert p.display_name == "Foundation"

    def test_display_name_without_name(self):
        p = Phase(number=3, file=Path("/tmp/p3.md"))
        assert p.display_name == "Phase 3"


# ---------------------------------------------------------------------------
# SprintConfig dataclass
# ---------------------------------------------------------------------------


def _make_phases(n: int = 3) -> list[Phase]:
    return [Phase(number=i + 1, file=Path(f"/tmp/phase-{i + 1}.md")) for i in range(n)]


def _make_config(**kwargs) -> SprintConfig:
    defaults = dict(
        index_path=Path("/tmp/tasklist-index.md"),
        release_dir=Path("/tmp/release"),
        phases=_make_phases(3),
    )
    defaults.update(kwargs)
    return SprintConfig(**defaults)


class TestSprintConfig:
    """Tests for SprintConfig dataclass."""

    def test_defaults(self):
        cfg = _make_config()
        assert cfg.start_phase == 1
        assert cfg.end_phase == 0
        assert cfg.max_turns == 50
        assert cfg.model == ""
        assert cfg.dry_run is False
        assert cfg.permission_flag == "--dangerously-skip-permissions"
        assert cfg.tmux_session_name == ""

    def test_results_dir(self):
        cfg = _make_config()
        assert cfg.results_dir == Path("/tmp/release/results")

    def test_execution_log_jsonl(self):
        cfg = _make_config()
        assert cfg.execution_log_jsonl == Path("/tmp/release/execution-log.jsonl")

    def test_execution_log_md(self):
        cfg = _make_config()
        assert cfg.execution_log_md == Path("/tmp/release/execution-log.md")

    def test_active_phases_all(self):
        cfg = _make_config()
        active = cfg.active_phases
        assert len(active) == 3
        assert [p.number for p in active] == [1, 2, 3]

    def test_active_phases_range(self):
        cfg = _make_config(start_phase=2, end_phase=3)
        active = cfg.active_phases
        assert len(active) == 2
        assert [p.number for p in active] == [2, 3]

    def test_active_phases_auto_end(self):
        cfg = _make_config(start_phase=2, end_phase=0)
        active = cfg.active_phases
        assert len(active) == 2
        assert [p.number for p in active] == [2, 3]

    def test_output_file(self):
        cfg = _make_config()
        phase = cfg.phases[0]
        assert cfg.output_file(phase) == Path("/tmp/release/results/phase-1-output.txt")

    def test_error_file(self):
        cfg = _make_config()
        phase = cfg.phases[1]
        assert cfg.error_file(phase) == Path("/tmp/release/results/phase-2-errors.txt")

    def test_result_file(self):
        cfg = _make_config()
        phase = cfg.phases[2]
        assert cfg.result_file(phase) == Path("/tmp/release/results/phase-3-result.md")


# ---------------------------------------------------------------------------
# PhaseResult dataclass
# ---------------------------------------------------------------------------


def _make_phase_result(**kwargs) -> PhaseResult:
    now = datetime.now(timezone.utc)
    defaults = dict(
        phase=Phase(number=1, file=Path("/tmp/p1.md")),
        status=PhaseStatus.PASS,
        exit_code=0,
        started_at=now - timedelta(seconds=90),
        finished_at=now,
    )
    defaults.update(kwargs)
    return PhaseResult(**defaults)


class TestPhaseResult:
    """Tests for PhaseResult dataclass."""

    def test_duration_seconds(self):
        now = datetime.now(timezone.utc)
        result = _make_phase_result(
            started_at=now - timedelta(seconds=120),
            finished_at=now,
        )
        assert abs(result.duration_seconds - 120.0) < 0.01

    def test_duration_display_seconds(self):
        now = datetime.now(timezone.utc)
        result = _make_phase_result(
            started_at=now - timedelta(seconds=45),
            finished_at=now,
        )
        assert result.duration_display == "45s"

    def test_duration_display_minutes(self):
        now = datetime.now(timezone.utc)
        result = _make_phase_result(
            started_at=now - timedelta(seconds=125),
            finished_at=now,
        )
        assert result.duration_display == "2m 5s"

    def test_defaults(self):
        result = _make_phase_result()
        assert result.output_bytes == 0
        assert result.error_bytes == 0
        assert result.last_task_id == ""
        assert result.files_changed == 0


# ---------------------------------------------------------------------------
# SprintResult dataclass
# ---------------------------------------------------------------------------


def _make_sprint_result(**kwargs) -> SprintResult:
    defaults = dict(config=_make_config())
    defaults.update(kwargs)
    return SprintResult(**defaults)


class TestSprintResult:
    """Tests for SprintResult dataclass."""

    def test_default_outcome(self):
        sr = _make_sprint_result()
        assert sr.outcome == SprintOutcome.SUCCESS

    def test_phases_passed(self):
        sr = _make_sprint_result(
            phase_results=[
                _make_phase_result(status=PhaseStatus.PASS),
                _make_phase_result(status=PhaseStatus.PASS_NO_SIGNAL),
                _make_phase_result(status=PhaseStatus.ERROR),
            ]
        )
        assert sr.phases_passed == 2

    def test_phases_failed(self):
        sr = _make_sprint_result(
            phase_results=[
                _make_phase_result(status=PhaseStatus.PASS),
                _make_phase_result(status=PhaseStatus.HALT),
                _make_phase_result(status=PhaseStatus.TIMEOUT),
                _make_phase_result(status=PhaseStatus.ERROR),
            ]
        )
        assert sr.phases_failed == 3

    def test_duration_display_minutes(self):
        now = datetime.now(timezone.utc)
        sr = _make_sprint_result()
        sr.started_at = now - timedelta(seconds=185)
        sr.finished_at = now
        assert sr.duration_display == "3m 5s"

    def test_duration_display_hours(self):
        now = datetime.now(timezone.utc)
        sr = _make_sprint_result()
        sr.started_at = now - timedelta(seconds=3720)
        sr.finished_at = now
        assert sr.duration_display == "1h 2m"

    def test_resume_command_when_halted(self):
        sr = _make_sprint_result()
        sr.halt_phase = 2
        cmd = sr.resume_command()
        assert "superclaude sprint run" in cmd
        assert "--start 2" in cmd
        assert "--end 3" in cmd

    def test_resume_command_when_not_halted(self):
        sr = _make_sprint_result()
        assert sr.resume_command() == ""

    def test_resume_command_with_explicit_end(self):
        cfg = _make_config(end_phase=5, phases=_make_phases(6))
        sr = SprintResult(config=cfg, halt_phase=3)
        cmd = sr.resume_command()
        assert "--start 3" in cmd
        assert "--end 5" in cmd


# ---------------------------------------------------------------------------
# MonitorState dataclass
# ---------------------------------------------------------------------------


class TestMonitorState:
    """Tests for MonitorState dataclass."""

    def test_defaults(self):
        ms = MonitorState()
        assert ms.output_bytes == 0
        assert ms.last_task_id == ""
        assert ms.last_tool_used == ""
        assert ms.files_changed == 0
        assert ms.growth_rate_bps == 0.0
        assert ms.stall_seconds == 0.0

    def test_stall_status_active(self):
        now = time.monotonic()
        ms = MonitorState(events_received=10, last_event_time=now - 10.0)
        assert ms.stall_status == "active"

    def test_stall_status_thinking(self):
        now = time.monotonic()
        ms = MonitorState(events_received=10, last_event_time=now - 35.0)
        assert ms.stall_status == "thinking..."

    def test_stall_status_stalled(self):
        now = time.monotonic()
        ms = MonitorState(events_received=10, last_event_time=now - 125.0)
        assert ms.stall_status == "STALLED"

    def test_stall_status_boundary_30(self):
        now = time.monotonic()
        # Use 29s to avoid race between setting last_event_time and reading it
        ms = MonitorState(events_received=10, last_event_time=now - 29.0)
        assert ms.stall_status == "active"

    def test_stall_status_boundary_thinking(self):
        now = time.monotonic()
        ms = MonitorState(events_received=10, last_event_time=now - 60.0)
        assert ms.stall_status == "thinking..."

    def test_stall_status_boundary_stalled(self):
        now = time.monotonic()
        ms = MonitorState(events_received=10, last_event_time=now - 121.0)
        assert ms.stall_status == "STALLED"

    def test_stall_status_waiting_no_events(self):
        now = time.monotonic()
        ms = MonitorState(events_received=0, phase_started_at=now - 10.0)
        assert ms.stall_status == "waiting..."

    def test_stall_status_waiting_no_events_stalled(self):
        now = time.monotonic()
        ms = MonitorState(events_received=0, phase_started_at=now - 130.0)
        assert ms.stall_status == "STALLED"

    def test_output_size_display_bytes(self):
        ms = MonitorState(output_bytes=512)
        assert ms.output_size_display == "512 B"

    def test_output_size_display_kb(self):
        ms = MonitorState(output_bytes=2048)
        assert ms.output_size_display == "2.0 KB"

    def test_output_size_display_mb(self):
        ms = MonitorState(output_bytes=2 * 1024 * 1024)
        assert ms.output_size_display == "2.0 MB"

    def test_output_size_display_zero(self):
        ms = MonitorState(output_bytes=0)
        assert ms.output_size_display == "0 B"
