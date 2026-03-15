"""Tests for the CLI Portify executor.

Covers T03.04 (executor), T03.06 (_determine_status), T03.07 (retry),
T03.08 (TurnLedger / HALTED), T03.09 (signal handlers), T03.10 (return contract).
"""

from __future__ import annotations

import os
import signal
import time
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from superclaude.cli.cli_portify.executor import (
    DRY_RUN_PHASE_TYPES,
    PortifyExecutor,
    _build_resume_command,
    _calculate_suggested_resume_budget,
    _determine_status,
    _emit_return_contract,
)
from superclaude.cli.cli_portify.models import (
    PortifyOutcome,
    PortifyPhaseType,
    PortifyStatus,
    PortifyStep,
    TurnLedger,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_step(
    step_id: str,
    phase_type: PortifyPhaseType = PortifyPhaseType.PREREQUISITES,
    retry_limit: int = 1,
    output_file: Path | None = None,
) -> PortifyStep:
    return PortifyStep(
        step_id=step_id,
        phase_type=phase_type,
        retry_limit=retry_limit,
        output_file=output_file,
    )


def _runner_success(step: PortifyStep):
    """Always returns exit 0 with EXIT_RECOMMENDATION marker."""
    stdout = "EXIT_RECOMMENDATION: CONTINUE"
    if step.output_file:
        step.output_file.parent.mkdir(parents=True, exist_ok=True)
        step.output_file.write_text("---\nstatus: pass\n---\noutput")
    return 0, stdout, False


def _runner_failure(step: PortifyStep):
    return 1, "", False


def _runner_timeout(step: PortifyStep):
    return 124, "", True


def _runner_no_signal(step: PortifyStep):
    """Exit 0, no EXIT_RECOMMENDATION marker, artifact present."""
    if step.output_file:
        step.output_file.parent.mkdir(parents=True, exist_ok=True)
        step.output_file.write_text("content")
    return 0, "", False


# ---------------------------------------------------------------------------
# T03.04: test_executor — Sequential execution
# ---------------------------------------------------------------------------


class TestExecutorSequentialExecution:
    """T03.04 — Executor runs steps in sequential order."""

    def test_executor_runs_all_steps_sequentially(self, tmp_path):
        executed = []
        steps = [_make_step(sid) for sid in ["s1", "s2", "s3"]]

        def runner(step: PortifyStep):
            executed.append(step.step_id)
            return 0, "EXIT_RECOMMENDATION: CONTINUE", False

        ex = PortifyExecutor(steps, tmp_path, step_runner=runner)
        outcome = ex.run()
        assert outcome == PortifyOutcome.SUCCESS
        assert executed == ["s1", "s2", "s3"]

    def test_executor_stops_on_failure(self, tmp_path):
        executed = []
        steps = [_make_step(sid) for sid in ["s1", "s2", "s3"]]

        call_count = [0]

        def runner(step: PortifyStep):
            executed.append(step.step_id)
            call_count[0] += 1
            if step.step_id == "s2":
                return 1, "", False
            return 0, "EXIT_RECOMMENDATION: CONTINUE", False

        ex = PortifyExecutor(steps, tmp_path, step_runner=runner)
        outcome = ex.run()
        assert outcome == PortifyOutcome.FAILURE
        assert "s3" not in executed

    def test_executor_emits_return_contract(self, tmp_path):
        steps = [_make_step("s1")]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_success)
        ex.run()
        contract_path = tmp_path / "return-contract.yaml"
        assert contract_path.exists()

    def test_executor_dry_run_filters_phase_types(self, tmp_path):
        executed = []
        steps = [
            _make_step("s1", PortifyPhaseType.PREREQUISITES),
            _make_step("s2", PortifyPhaseType.SYNTHESIS),
            _make_step("s3", PortifyPhaseType.ANALYSIS),
            _make_step("s4", PortifyPhaseType.CONVERGENCE),
        ]

        def runner(step: PortifyStep):
            executed.append(step.step_id)
            return 0, "EXIT_RECOMMENDATION: CONTINUE", False

        ex = PortifyExecutor(steps, tmp_path, dry_run=True, step_runner=runner)
        ex.run()
        # Only PREREQUISITES and ANALYSIS are in DRY_RUN_PHASE_TYPES
        assert "s1" in executed  # PREREQUISITES
        assert "s2" not in executed  # SYNTHESIS — excluded
        assert "s3" in executed  # ANALYSIS
        assert "s4" not in executed  # CONVERGENCE — excluded

    def test_executor_resume_skips_prior_steps(self, tmp_path):
        executed = []
        steps = [_make_step(sid) for sid in ["s1", "s2", "s3"]]

        def runner(step: PortifyStep):
            executed.append(step.step_id)
            return 0, "EXIT_RECOMMENDATION: CONTINUE", False

        ex = PortifyExecutor(steps, tmp_path, resume_from="s2", step_runner=runner)
        ex.run()
        assert "s1" not in executed
        assert "s2" in executed
        assert "s3" in executed

    def test_executor_dry_run_contract_has_dry_run_outcome(self, tmp_path):
        steps = [_make_step("s1", PortifyPhaseType.PREREQUISITES)]
        ex = PortifyExecutor(steps, tmp_path, dry_run=True, step_runner=_runner_success)
        ex.run()
        contract = yaml.safe_load((tmp_path / "return-contract.yaml").read_text())
        assert contract["outcome"] == "DRY_RUN"


# ---------------------------------------------------------------------------
# T03.06: test_determine_status — Status classification
# ---------------------------------------------------------------------------


class TestDetermineStatus:
    """T03.06 — _determine_status() classifies all exit code paths correctly."""

    def test_determine_status_timeout_exit_124(self):
        status = _determine_status(124, timed_out=True, stdout="")
        assert status == PortifyStatus.TIMEOUT

    def test_determine_status_timeout_flag(self):
        status = _determine_status(0, timed_out=True, stdout="")
        assert status == PortifyStatus.TIMEOUT

    def test_determine_status_error_nonzero(self):
        status = _determine_status(1, timed_out=False, stdout="")
        assert status == PortifyStatus.ERROR

    def test_determine_status_error_exit_2(self):
        status = _determine_status(2, timed_out=False, stdout="")
        assert status == PortifyStatus.ERROR

    def test_determine_status_pass_with_marker_and_artifact(self, tmp_path):
        artifact = tmp_path / "out.md"
        artifact.write_text("content")
        status = _determine_status(
            0, timed_out=False,
            stdout="EXIT_RECOMMENDATION: CONTINUE",
            artifact_path=artifact,
        )
        assert status == PortifyStatus.PASS

    def test_determine_status_pass_no_signal_no_marker(self, tmp_path):
        artifact = tmp_path / "out.md"
        artifact.write_text("content")
        status = _determine_status(
            0, timed_out=False, stdout="", artifact_path=artifact,
        )
        assert status == PortifyStatus.PASS_NO_SIGNAL

    def test_determine_status_pass_no_report_no_artifact(self, tmp_path):
        status = _determine_status(
            0, timed_out=False, stdout="",
            artifact_path=tmp_path / "nonexistent.md",
        )
        assert status == PortifyStatus.PASS_NO_REPORT

    def test_determine_status_pass_no_report_no_artifact_path(self):
        status = _determine_status(0, timed_out=False, stdout="", artifact_path=None)
        assert status == PortifyStatus.PASS_NO_REPORT

    def test_determine_status_pass_no_signal_triggers_retry(self, tmp_path):
        """PASS_NO_SIGNAL triggers retry (not PASS_NO_REPORT)."""
        artifact = tmp_path / "out.md"
        artifact.write_text("content")
        status = _determine_status(0, timed_out=False, stdout="", artifact_path=artifact)
        assert status == PortifyStatus.PASS_NO_SIGNAL
        # Verify it's distinct from PASS_NO_REPORT
        assert status != PortifyStatus.PASS_NO_REPORT


# ---------------------------------------------------------------------------
# T03.07: test_retry — Retry mechanism
# ---------------------------------------------------------------------------


class TestRetry:
    """T03.07 — Retry mechanism with retry_limit=1."""

    def test_retry_triggered_on_pass_no_signal(self, tmp_path):
        """PASS_NO_SIGNAL triggers exactly one retry."""
        artifact = tmp_path / "out.md"
        call_count = [0]
        step = _make_step("s1", output_file=artifact)

        def runner(s: PortifyStep):
            call_count[0] += 1
            artifact.write_text("content")
            return 0, "", False  # no marker → PASS_NO_SIGNAL

        ex = PortifyExecutor([step], tmp_path, step_runner=runner)
        ex.run()
        # 1 initial + 1 retry = 2 calls
        assert call_count[0] == 2

    def test_retry_not_triggered_on_pass_no_report(self, tmp_path):
        """PASS_NO_REPORT does not trigger retry (no artifact)."""
        call_count = [0]
        step = _make_step("s1", output_file=tmp_path / "nonexistent.md")

        def runner(s: PortifyStep):
            call_count[0] += 1
            return 0, "", False  # no marker, no artifact → PASS_NO_REPORT

        ex = PortifyExecutor([step], tmp_path, step_runner=runner)
        ex.run()
        assert call_count[0] == 1  # no retry

    def test_retry_max_one_attempt(self, tmp_path):
        """Retry fires at most once regardless of repeated PASS_NO_SIGNAL."""
        artifact = tmp_path / "out.md"
        call_count = [0]
        step = _make_step("s1", output_file=artifact)

        def runner(s: PortifyStep):
            call_count[0] += 1
            artifact.write_text("still no marker")
            return 0, "", False

        ex = PortifyExecutor([step], tmp_path, step_runner=runner)
        ex.run()
        # Max 2 calls (1 initial + 1 retry) — never more
        assert call_count[0] == 2

    def test_retry_consumes_budget(self, tmp_path):
        """Each retry invocation consumes one turn from the ledger."""
        artifact = tmp_path / "out.md"
        step = _make_step("s1", output_file=artifact)

        def runner(s: PortifyStep):
            artifact.write_text("content")
            return 0, "", False  # PASS_NO_SIGNAL → retry

        ex = PortifyExecutor([step], tmp_path, turn_budget=10, step_runner=runner)
        ex.run()
        # 2 turns consumed (initial + retry)
        assert ex._ledger.consumed == 2


# ---------------------------------------------------------------------------
# T03.08: test_turn_ledger — TurnLedger and HALTED
# ---------------------------------------------------------------------------


class TestTurnLedger:
    """T03.08 — TurnLedger tracks budget and produces HALTED on exhaustion."""

    def test_turn_ledger_tracks_consumed(self):
        ledger = TurnLedger(total_budget=5)
        ledger.consume(2)
        assert ledger.consumed == 2
        assert ledger.remaining == 3

    def test_turn_ledger_can_launch_true(self):
        ledger = TurnLedger(total_budget=5)
        assert ledger.can_launch() is True

    def test_turn_ledger_can_launch_false_when_exhausted(self):
        ledger = TurnLedger(total_budget=2)
        ledger.consume(2)
        assert ledger.can_launch() is False

    def test_turn_ledger_remaining_never_negative(self):
        ledger = TurnLedger(total_budget=1)
        ledger.consume(10)
        assert ledger.remaining == 0

    def test_turn_ledger_budget_exhaustion_produces_halted(self, tmp_path):
        """When budget=0, first step triggers HALTED before any execution."""
        steps = [_make_step(sid) for sid in ["s1", "s2"]]
        executed = []

        def runner(s: PortifyStep):
            executed.append(s.step_id)
            return 0, "EXIT_RECOMMENDATION: CONTINUE", False

        ex = PortifyExecutor(steps, tmp_path, turn_budget=0, step_runner=runner)
        outcome = ex.run()
        assert outcome == PortifyOutcome.HALTED
        assert executed == []

    def test_turn_ledger_halted_emits_return_contract(self, tmp_path):
        steps = [_make_step("s1")]
        ex = PortifyExecutor(steps, tmp_path, turn_budget=0, step_runner=_runner_success)
        ex.run()
        assert (tmp_path / "return-contract.yaml").exists()


# ---------------------------------------------------------------------------
# T03.09: test_signal_handler — Signal handling
# ---------------------------------------------------------------------------


class TestSignalHandler:
    """T03.09 — SIGINT/SIGTERM set INTERRUPTED outcome after step completes."""

    def test_signal_handler_interrupted_flag_set(self, tmp_path):
        steps = [_make_step(sid) for sid in ["s1", "s2"]]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_success)

        # Simulate interrupt mid-run by setting the flag directly
        original_runner = ex._step_runner

        call_count = [0]

        def runner_with_interrupt(step: PortifyStep):
            call_count[0] += 1
            if call_count[0] == 1:
                ex._interrupted = True  # simulate signal after first step
            return 0, "EXIT_RECOMMENDATION: CONTINUE", False

        ex._step_runner = runner_with_interrupt
        outcome = ex.run()
        assert outcome == PortifyOutcome.INTERRUPTED

    def test_signal_handler_interrupted_emits_contract(self, tmp_path):
        steps = [_make_step("s1")]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_success)
        ex._interrupted = True  # interrupt before any step
        ex.run()
        assert (tmp_path / "return-contract.yaml").exists()

    def test_signal_handler_sigint_registered(self, tmp_path):
        """_install_signal_handlers registers SIGINT handler."""
        steps = [_make_step("s1")]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_success)
        ex._install_signal_handlers()
        # Verify handler is installed (not SIG_DFL or SIG_IGN)
        handler = signal.getsignal(signal.SIGINT)
        assert callable(handler)
        ex._restore_signal_handlers()

    def test_signal_handler_sigterm_registered(self, tmp_path):
        """_install_signal_handlers registers SIGTERM handler."""
        steps = [_make_step("s1")]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_success)
        ex._install_signal_handlers()
        handler = signal.getsignal(signal.SIGTERM)
        assert callable(handler)
        ex._restore_signal_handlers()

    def test_signal_handler_handlers_restored_after_run(self, tmp_path):
        """Original signal handlers are restored after executor finishes."""
        original_sigint = signal.getsignal(signal.SIGINT)
        steps = [_make_step("s1")]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_success)
        ex.run()
        assert signal.getsignal(signal.SIGINT) == original_sigint


# ---------------------------------------------------------------------------
# T03.10: test_return_contract — Return contract emission
# ---------------------------------------------------------------------------


class TestReturnContract:
    """T03.10 — Return contract emitted on all outcome paths (SC-011)."""

    def test_return_contract_emitted_on_success(self, tmp_path):
        steps = [_make_step("s1")]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_success)
        ex.run()
        assert (tmp_path / "return-contract.yaml").exists()

    def test_return_contract_emitted_on_failure(self, tmp_path):
        steps = [_make_step("s1")]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_failure)
        ex.run()
        assert (tmp_path / "return-contract.yaml").exists()

    def test_return_contract_emitted_on_timeout(self, tmp_path):
        steps = [_make_step("s1")]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_timeout)
        ex.run()
        assert (tmp_path / "return-contract.yaml").exists()

    def test_return_contract_emitted_on_dry_run(self, tmp_path):
        steps = [_make_step("s1", PortifyPhaseType.PREREQUISITES)]
        ex = PortifyExecutor(steps, tmp_path, dry_run=True, step_runner=_runner_success)
        ex.run()
        assert (tmp_path / "return-contract.yaml").exists()

    def test_return_contract_emitted_on_halted(self, tmp_path):
        steps = [_make_step("s1")]
        ex = PortifyExecutor(steps, tmp_path, turn_budget=0, step_runner=_runner_success)
        ex.run()
        assert (tmp_path / "return-contract.yaml").exists()

    def test_return_contract_resume_command_format(self, tmp_path):
        steps = [_make_step("s1"), _make_step("s2")]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_failure)
        ex.run()
        contract = yaml.safe_load((tmp_path / "return-contract.yaml").read_text())
        # resume_command should contain step id
        rc = contract.get("resume_command", "")
        assert "superclaude cli-portify run --resume" in rc

    def test_return_contract_suggested_budget_dynamic(self, tmp_path):
        """suggested_resume_budget = remaining_pending_steps * 25."""
        steps = [_make_step(sid) for sid in ["s1", "s2", "s3"]]
        # s1 fails, s2 and s3 remain
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_failure)
        ex.run()
        contract = yaml.safe_load((tmp_path / "return-contract.yaml").read_text())
        # After s1 fails: s2 + s3 are PENDING → 2 * 25 = 50
        assert contract["suggested_resume_budget"] == 50

    def test_return_contract_success_completed_steps(self, tmp_path):
        steps = [_make_step(sid) for sid in ["s1", "s2"]]
        ex = PortifyExecutor(steps, tmp_path, step_runner=_runner_success)
        ex.run()
        contract = yaml.safe_load((tmp_path / "return-contract.yaml").read_text())
        assert "s1" in contract["completed_steps"]
        assert "s2" in contract["completed_steps"]

    def test_resume_command_helper(self):
        cmd = _build_resume_command("step-5")
        assert "step-5" in cmd
        assert "superclaude cli-portify run --resume" in cmd

    def test_suggested_budget_calculation(self, tmp_path):
        steps = [_make_step(sid) for sid in ["s1", "s2", "s3"]]
        # All PENDING → 3 * 25 = 75
        budget = _calculate_suggested_resume_budget(steps)
        assert budget == 75
