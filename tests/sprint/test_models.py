"""Unit tests for sprint data models.

Covers all types (PhaseStatus, SprintOutcome, Phase, SprintConfig,
PhaseResult, SprintResult, MonitorState, TaskResult, TaskStatus,
GateOutcome, TurnLedger) and their property methods.
"""

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from superclaude.cli.sprint.models import (
    GateOutcome,
    MonitorState,
    Phase,
    PhaseResult,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
    SprintResult,
    TaskEntry,
    TaskResult,
    TaskStatus,
    TurnLedger,
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
            "PASS_RECOVERED",
            "INCOMPLETE",
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
            (PhaseStatus.INCOMPLETE, True),
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
            (PhaseStatus.INCOMPLETE, False),
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
            (PhaseStatus.INCOMPLETE, True),
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
        assert cfg.max_turns == 100
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


# ---------------------------------------------------------------------------
# TurnLedger dataclass
# ---------------------------------------------------------------------------


class TestTurnLedger:
    """Tests for TurnLedger budget arithmetic."""

    def test_initial_available(self):
        ledger = TurnLedger(initial_budget=50)
        assert ledger.available() == 50

    def test_debit_reduces_available(self):
        ledger = TurnLedger(initial_budget=50)
        ledger.debit(10)
        assert ledger.consumed == 10
        assert ledger.available() == 40

    def test_debit_monotonicity(self):
        """consumed can only increase via debit."""
        ledger = TurnLedger(initial_budget=50)
        ledger.debit(10)
        ledger.debit(5)
        assert ledger.consumed == 15
        assert ledger.available() == 35

    def test_debit_negative_raises(self):
        ledger = TurnLedger(initial_budget=50)
        with pytest.raises(ValueError, match="non-negative"):
            ledger.debit(-1)

    def test_credit_increases_available(self):
        ledger = TurnLedger(initial_budget=50)
        ledger.debit(20)
        ledger.credit(5)
        assert ledger.reimbursed == 5
        assert ledger.available() == 35  # 50 - 20 + 5

    def test_credit_negative_raises(self):
        ledger = TurnLedger(initial_budget=50)
        with pytest.raises(ValueError, match="non-negative"):
            ledger.credit(-1)

    def test_available_formula(self):
        """available() = initial_budget - consumed + reimbursed."""
        ledger = TurnLedger(initial_budget=100)
        ledger.debit(30)
        ledger.credit(10)
        assert ledger.available() == 100 - 30 + 10

    def test_can_launch_true(self):
        ledger = TurnLedger(initial_budget=50, minimum_allocation=5)
        assert ledger.can_launch() is True

    def test_can_launch_false_insufficient(self):
        ledger = TurnLedger(initial_budget=50, minimum_allocation=5)
        ledger.debit(46)
        assert ledger.available() == 4
        assert ledger.can_launch() is False

    def test_can_launch_exact_boundary(self):
        ledger = TurnLedger(initial_budget=50, minimum_allocation=5)
        ledger.debit(45)
        assert ledger.available() == 5
        assert ledger.can_launch() is True

    def test_can_remediate_true(self):
        ledger = TurnLedger(initial_budget=50, minimum_remediation_budget=3)
        assert ledger.can_remediate() is True

    def test_can_remediate_false(self):
        ledger = TurnLedger(initial_budget=50, minimum_remediation_budget=3)
        ledger.debit(48)
        assert ledger.available() == 2
        assert ledger.can_remediate() is False

    def test_can_remediate_exact_boundary(self):
        ledger = TurnLedger(initial_budget=50, minimum_remediation_budget=3)
        ledger.debit(47)
        assert ledger.available() == 3
        assert ledger.can_remediate() is True

    def test_defaults(self):
        ledger = TurnLedger(initial_budget=50)
        assert ledger.consumed == 0
        assert ledger.reimbursed == 0
        assert ledger.reimbursement_rate == 0.8
        assert ledger.minimum_allocation == 5
        assert ledger.minimum_remediation_budget == 3

    def test_zero_budget_available(self):
        """initial_budget=0 → available starts at 0."""
        ledger = TurnLedger(initial_budget=0)
        assert ledger.available() == 0

    def test_zero_budget_can_launch_false(self):
        """With zero budget, can_launch() returns False."""
        ledger = TurnLedger(initial_budget=0, minimum_allocation=5)
        assert ledger.can_launch() is False

    def test_zero_budget_can_remediate_false(self):
        """With zero budget, can_remediate() returns False."""
        ledger = TurnLedger(initial_budget=0, minimum_remediation_budget=3)
        assert ledger.can_remediate() is False

    def test_over_budget_debit_makes_available_negative(self):
        """Debiting more than available results in negative available."""
        ledger = TurnLedger(initial_budget=10)
        ledger.debit(15)
        assert ledger.available() == -5
        assert ledger.can_launch() is False
        assert ledger.can_remediate() is False

    def test_debit_zero_is_noop(self):
        """debit(0) is valid and does not change state."""
        ledger = TurnLedger(initial_budget=50)
        ledger.debit(0)
        assert ledger.consumed == 0
        assert ledger.available() == 50

    def test_credit_zero_is_noop(self):
        """credit(0) is valid and does not change state."""
        ledger = TurnLedger(initial_budget=50)
        ledger.credit(0)
        assert ledger.reimbursed == 0
        assert ledger.available() == 50

    def test_credit_exceeds_consumed_increases_available(self):
        """Crediting more than consumed is allowed (increases available beyond initial)."""
        ledger = TurnLedger(initial_budget=50)
        ledger.debit(10)
        ledger.credit(20)
        assert ledger.available() == 60  # 50 - 10 + 20

    def test_budget_monotonicity_consumed_never_decreases(self):
        """consumed only increases — there is no method to decrease it."""
        ledger = TurnLedger(initial_budget=50)
        ledger.debit(10)
        ledger.debit(5)
        ledger.credit(20)  # credit doesn't decrease consumed
        assert ledger.consumed == 15  # still 10 + 5

    def test_budget_monotonicity_across_many_operations(self):
        """consumed never decreases across 15+ mixed operations."""
        ledger = TurnLedger(initial_budget=200)
        prev_consumed = 0
        ops = [
            ("debit", 10), ("debit", 5), ("credit", 3),
            ("debit", 20), ("credit", 10), ("debit", 1),
            ("credit", 0), ("debit", 15), ("debit", 0),
            ("credit", 5), ("debit", 8), ("credit", 2),
            ("debit", 12), ("debit", 3), ("credit", 7),
        ]
        for op, amount in ops:
            if op == "debit":
                ledger.debit(amount)
            else:
                ledger.credit(amount)
            assert ledger.consumed >= prev_consumed, (
                f"consumed decreased from {prev_consumed} to {ledger.consumed} "
                f"after {op}({amount})"
            )
            prev_consumed = ledger.consumed

        # Verify final arithmetic
        total_debits = sum(a for o, a in ops if o == "debit")
        total_credits = sum(a for o, a in ops if o == "credit")
        assert ledger.consumed == total_debits
        assert ledger.reimbursed == total_credits
        assert ledger.available() == 200 - total_debits + total_credits

    def test_exact_threshold_budget_can_launch(self):
        """Budget exactly at minimum_allocation allows launch."""
        ledger = TurnLedger(initial_budget=5, minimum_allocation=5)
        assert ledger.can_launch() is True

    def test_exact_threshold_budget_can_remediate(self):
        """Budget exactly at minimum_remediation_budget allows remediation."""
        ledger = TurnLedger(initial_budget=3, minimum_remediation_budget=3)
        assert ledger.can_remediate() is True

    def test_budget_decay_rate_08(self):
        """Verify budget decay math at rate=0.8: net cost per passing task = 4 turns (spec §4.1)."""
        import math

        ledger = TurnLedger(initial_budget=200, reimbursement_rate=0.8)
        # Simulate one task: 8 turns consumed, then credit floor(8 * 0.8) = 6
        ledger.debit(8)
        reimbursed = math.floor(8 * ledger.reimbursement_rate)
        assert reimbursed == 6
        ledger.credit(reimbursed)
        # Also add 2 overhead turns
        ledger.debit(2)
        # Net cost = 8 + 2 - 6 = 4
        assert ledger.consumed == 10  # 8 + 2
        assert ledger.reimbursed == 6
        assert ledger.available() == 200 - 10 + 6  # = 196

    def test_max_sustainable_tasks_at_08(self):
        """Verify sustainability boundary: budget=200, rate=0.8, net_cost=4/task → ~50 tasks (spec §4.2)."""
        import math

        ledger = TurnLedger(initial_budget=200, reimbursement_rate=0.8, minimum_allocation=8)
        task_count = 0
        while ledger.can_launch():
            ledger.debit(8)
            reimbursed = math.floor(8 * ledger.reimbursement_rate)
            ledger.credit(reimbursed)
            ledger.debit(2)  # overhead
            task_count += 1
            if task_count > 100:  # safety bound
                break
        # 200 / 4 net cost = 50 total capacity, but can_launch requires minimum_allocation=8
        # After 49 tasks: available = 200 - 49*10 + 49*6 = 4 < 8, so loop exits at 49
        assert task_count == 49
        assert ledger.available() == 4

    def test_46_task_sprint_sustainability(self):
        """NFR-003: a 46-task sprint at rate=0.8, budget=200 completes with 16-turn margin."""
        import math

        ledger = TurnLedger(initial_budget=200, reimbursement_rate=0.8)
        for _ in range(46):
            ledger.debit(8)
            reimbursed = math.floor(8 * ledger.reimbursement_rate)
            ledger.credit(reimbursed)
            ledger.debit(2)  # overhead
        assert ledger.available() > 0
        # Expected: 200 - 46*(8+2) + 46*6 = 200 - 460 + 276 = 16
        assert ledger.available() == 16

    def test_budget_exhaustion_property(self):
        """NFR-008: for rate < 1.0, budget monotonically decays and reaches 0 in finite steps."""
        import math
        import random

        rng = random.Random(42)  # deterministic seed per R-005
        for _ in range(20):  # 20 trials
            budget = rng.randint(50, 500)
            rate = round(rng.uniform(0.1, 0.99), 2)
            turns_per_task = rng.randint(1, 50)
            ledger = TurnLedger(initial_budget=budget, reimbursement_rate=rate, minimum_allocation=turns_per_task)

            prev_available = ledger.available()
            steps = 0
            while ledger.can_launch() and steps < 10000:
                ledger.debit(turns_per_task)
                reimbursed = math.floor(turns_per_task * rate)
                ledger.credit(reimbursed)
                # Verify monotonic decay: each cycle net cost > 0
                assert ledger.available() < prev_available, (
                    f"Budget did not decrease: {prev_available} -> {ledger.available()} "
                    f"(rate={rate}, turns={turns_per_task})"
                )
                prev_available = ledger.available()
                steps += 1
            # Budget must have been exhausted in finite steps
            assert not ledger.can_launch(), f"Budget never exhausted after {steps} steps"

    def test_rate_boundary_validation(self):
        """SC-001: verify TurnLedger behavior at rate boundary values."""
        import math

        # rate=0.0 → zero reimbursement, valid
        ledger_zero = TurnLedger(initial_budget=100, reimbursement_rate=0.0)
        ledger_zero.debit(10)
        reimbursed = math.floor(10 * ledger_zero.reimbursement_rate)
        ledger_zero.credit(reimbursed)
        assert reimbursed == 0
        assert ledger_zero.available() == 90  # no reimbursement

        # rate=0.99 → high reimbursement, valid
        ledger_high = TurnLedger(initial_budget=100, reimbursement_rate=0.99)
        ledger_high.debit(10)
        reimbursed = math.floor(10 * ledger_high.reimbursement_rate)
        ledger_high.credit(reimbursed)
        assert reimbursed == 9
        assert ledger_high.available() == 99

        # rate=1.0 → no decay, net cost = 0 per task (infinite budget)
        # SC-001 says this should be rejected, but TurnLedger currently has no validation.
        # This test documents the current behavior: rate=1.0 is accepted but causes zero net cost.
        ledger_one = TurnLedger(initial_budget=100, reimbursement_rate=1.0)
        ledger_one.debit(10)
        reimbursed = math.floor(10 * ledger_one.reimbursement_rate)
        ledger_one.credit(reimbursed)
        assert reimbursed == 10
        assert ledger_one.available() == 100  # no decay — budget never depletes

        # rate=-0.1 → negative reimbursement (penalizes)
        # SC-001 says this should be rejected, but TurnLedger currently has no validation.
        # This test documents the current behavior: negative rate produces negative credits.
        ledger_neg = TurnLedger(initial_budget=100, reimbursement_rate=-0.1)
        ledger_neg.debit(10)
        reimbursed = math.floor(10 * ledger_neg.reimbursement_rate)
        # floor(10 * -0.1) = floor(-1.0) = -1
        assert reimbursed == -1
        # credit(-1) should raise ValueError per existing validation
        with pytest.raises(ValueError, match="non-negative"):
            ledger_neg.credit(reimbursed)


# ---------------------------------------------------------------------------
# GateOutcome enum
# ---------------------------------------------------------------------------


class TestGateOutcome:
    """Tests for GateOutcome enum."""

    def test_all_members_present(self):
        expected = {"PASS", "FAIL", "DEFERRED", "PENDING"}
        assert {m.name for m in GateOutcome} == expected

    def test_values(self):
        assert GateOutcome.PASS.value == "pass"
        assert GateOutcome.FAIL.value == "fail"
        assert GateOutcome.DEFERRED.value == "deferred"
        assert GateOutcome.PENDING.value == "pending"

    def test_is_success_pass(self):
        assert GateOutcome.PASS.is_success is True

    def test_is_success_fail(self):
        assert GateOutcome.FAIL.is_success is False

    def test_is_success_deferred(self):
        assert GateOutcome.DEFERRED.is_success is False

    def test_is_success_pending(self):
        assert GateOutcome.PENDING.is_success is False


# ---------------------------------------------------------------------------
# TaskResult dataclass — enhanced fields and serialization
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


class TestTaskResult:
    """Tests for TaskResult dataclass fields and serialization."""

    def test_fields_present(self):
        """TaskResult has all required fields including gate_outcome and reimbursement_amount."""
        tr = _make_task_result()
        assert tr.task.task_id == "T01.01"
        assert tr.status == TaskStatus.PASS
        assert tr.turns_consumed == 10
        assert tr.gate_outcome == GateOutcome.PASS
        assert tr.reimbursement_amount == 0
        assert tr.output_path == ""

    def test_gate_outcome_default(self):
        tr = TaskResult(task=_make_task_entry())
        assert tr.gate_outcome == GateOutcome.PENDING

    def test_reimbursement_amount_default(self):
        tr = TaskResult(task=_make_task_entry())
        assert tr.reimbursement_amount == 0

    def test_output_path_field(self):
        tr = _make_task_result(output_path="/tmp/output.txt")
        assert tr.output_path == "/tmp/output.txt"

    def test_duration_seconds(self):
        now = datetime.now(timezone.utc)
        tr = _make_task_result(
            started_at=now - timedelta(seconds=45),
            finished_at=now,
        )
        assert abs(tr.duration_seconds - 45.0) < 0.01

    def test_to_context_summary_verbose(self):
        tr = _make_task_result(
            task=_make_task_entry(task_id="T02.03", title="Implement feature"),
            status=TaskStatus.PASS,
            gate_outcome=GateOutcome.PASS,
            turns_consumed=15,
        )
        summary = tr.to_context_summary(verbose=True)
        assert "### T02.03 — Implement feature" in summary
        assert "**Status**: pass" in summary
        assert "**Gate**: pass" in summary
        assert "**Turns consumed**: 15" in summary

    def test_to_context_summary_verbose_with_reimbursement(self):
        tr = _make_task_result(reimbursement_amount=5)
        summary = tr.to_context_summary(verbose=True)
        assert "**Reimbursement**: 5 turns" in summary

    def test_to_context_summary_verbose_without_reimbursement(self):
        tr = _make_task_result(reimbursement_amount=0)
        summary = tr.to_context_summary(verbose=True)
        assert "Reimbursement" not in summary

    def test_to_context_summary_verbose_with_output_path(self):
        tr = _make_task_result(output_path="/results/out.txt")
        summary = tr.to_context_summary(verbose=True)
        assert "**Output**: /results/out.txt" in summary

    def test_to_context_summary_compressed(self):
        tr = _make_task_result(
            task=_make_task_entry(task_id="T01.02"),
            status=TaskStatus.FAIL,
            gate_outcome=GateOutcome.FAIL,
        )
        summary = tr.to_context_summary(verbose=False)
        assert "T01.02" in summary
        assert "fail" in summary
        assert "gate: fail" in summary
        # Compressed should be a single line
        assert "\n" not in summary

    def test_to_context_summary_deterministic(self):
        """Serialization produces identical output for identical inputs."""
        now = datetime.now(timezone.utc)
        kwargs = dict(
            task=_make_task_entry(task_id="T01.01", title="Test"),
            status=TaskStatus.PASS,
            turns_consumed=10,
            started_at=now - timedelta(seconds=30),
            finished_at=now,
            gate_outcome=GateOutcome.PASS,
        )
        tr1 = TaskResult(**kwargs)
        tr2 = TaskResult(**kwargs)
        assert tr1.to_context_summary(verbose=True) == tr2.to_context_summary(verbose=True)
        assert tr1.to_context_summary(verbose=False) == tr2.to_context_summary(verbose=False)
