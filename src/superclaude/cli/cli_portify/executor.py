"""Sequential pipeline executor for CLI Portify.

Implements:
- Sequential step execution loop (T03.04)
- --dry-run phase type filtering to PREREQUISITES/ANALYSIS/USER_REVIEW/SPECIFICATION (T03.04)
- --resume <step-id> skip logic with prior results preserved (T03.04)
- Signal handling integration points (T03.04 / T03.09)
- Timeout classification: exit 124 → TIMEOUT (T03.06)
- _determine_status() classification (T03.06)
- Retry mechanism with retry_limit=1 (T03.07)
- TurnLedger budget exhaustion → HALTED (T03.08)
- Return contract emission on all outcome paths (T03.10)
"""

from __future__ import annotations

import signal
import time
from pathlib import Path
from typing import Callable, Optional

import yaml

from superclaude.cli.cli_portify.models import (
    PortifyOutcome,
    PortifyPhaseType,
    PortifyStatus,
    PortifyStep,
    PortifyStepResult,
    TurnLedger,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Phase types allowed during --dry-run (SC-012)
DRY_RUN_PHASE_TYPES: frozenset[PortifyPhaseType] = frozenset({
    PortifyPhaseType.PREREQUISITES,
    PortifyPhaseType.ANALYSIS,
    PortifyPhaseType.USER_REVIEW,
    PortifyPhaseType.SPECIFICATION,
})

# Exit code constants
EXIT_CODE_TIMEOUT: int = 124
EXIT_RECOMMENDATION_MARKER: str = "EXIT_RECOMMENDATION:"


# ---------------------------------------------------------------------------
# _determine_status()
# ---------------------------------------------------------------------------


def _determine_status(
    exit_code: int,
    timed_out: bool,
    stdout: str = "",
    artifact_path: Optional[Path] = None,
) -> PortifyStatus:
    """Classify a step outcome from exit code, EXIT_RECOMMENDATION, and artifact.

    Classification rules (priority order):
      1. exit 124 (or timed_out=True)  → TIMEOUT
      2. exit non-zero                 → ERROR
      3. exit 0 + marker + artifact    → PASS
      4. exit 0 + no marker + artifact → PASS_NO_SIGNAL  (triggers retry)
      5. exit 0 + artifact, no result  → PASS_NO_REPORT  (no retry)
      6. exit 0 + no artifact          → PASS_NO_REPORT
    """
    if timed_out or exit_code == EXIT_CODE_TIMEOUT:
        return PortifyStatus.TIMEOUT

    if exit_code != 0:
        return PortifyStatus.ERROR

    # exit 0 paths
    has_marker = EXIT_RECOMMENDATION_MARKER in stdout
    artifact_exists = artifact_path is not None and Path(artifact_path).exists()

    if has_marker and artifact_exists:
        return PortifyStatus.PASS

    if not has_marker and artifact_exists:
        return PortifyStatus.PASS_NO_SIGNAL  # triggers retry

    # No artifact (or no result file) → no retry
    return PortifyStatus.PASS_NO_REPORT


# ---------------------------------------------------------------------------
# Return contract helpers (T03.10)
# ---------------------------------------------------------------------------


def _build_resume_command(step_id: str, cli_name: str = "portify") -> str:
    """Build the exact CLI command string for resuming from a step."""
    return f"superclaude cli-portify run --resume {step_id}"


def _calculate_suggested_resume_budget(steps: list[PortifyStep]) -> int:
    """Calculate suggested_resume_budget = remaining_steps_count * 25.

    remaining = steps with PENDING or INCOMPLETE status.
    """
    remaining = sum(
        1 for s in steps
        if s.status in (PortifyStatus.PENDING, PortifyStatus.INCOMPLETE)
    )
    return remaining * 25


def _emit_return_contract(
    workdir: Path,
    outcome: PortifyOutcome,
    steps: list[PortifyStep],
    completed_steps: list[str],
    resume_from_step_id: str = "",
) -> Path:
    """Emit return-contract.yaml to the workdir on ALL outcome paths (SC-011).

    Returns the path to the emitted file.
    """
    remaining_steps = [s.step_id for s in steps if s.status in (PortifyStatus.PENDING, PortifyStatus.INCOMPLETE)]
    resume_command = _build_resume_command(resume_from_step_id) if resume_from_step_id else ""
    suggested_budget = _calculate_suggested_resume_budget(steps)

    contract = {
        "outcome": outcome.value,
        "completed_steps": completed_steps,
        "remaining_steps": remaining_steps,
        "resume_command": resume_command,
        "suggested_resume_budget": suggested_budget,
    }

    workdir.mkdir(parents=True, exist_ok=True)
    contract_path = workdir / "return-contract.yaml"
    with open(contract_path, "w") as fh:
        yaml.safe_dump(contract, fh, default_flow_style=False)
    return contract_path


# ---------------------------------------------------------------------------
# PortifyExecutor
# ---------------------------------------------------------------------------


class PortifyExecutor:
    """Sequential pipeline executor for CLI Portify.

    Usage:
        executor = PortifyExecutor(steps, workdir, dry_run=False)
        outcome = executor.run()
    """

    def __init__(
        self,
        steps: list[PortifyStep],
        workdir: Path,
        *,
        dry_run: bool = False,
        resume_from: str = "",
        turn_budget: int = 200,
        step_runner: Optional[Callable[[PortifyStep], tuple[int, str, bool]]] = None,
    ) -> None:
        """
        Args:
            steps: Ordered list of steps in registered order.
            workdir: Working directory for artifacts and return contract.
            dry_run: If True, filter execution to DRY_RUN_PHASE_TYPES only.
            resume_from: Step ID to resume from (skip all prior steps).
            turn_budget: Total Claude-invocation budget (TurnLedger).
            step_runner: Optional callable (step) -> (exit_code, stdout, timed_out).
                         Used for testing; real runs use subprocess.
        """
        self.steps = steps
        self.workdir = workdir
        self.dry_run = dry_run
        self.resume_from = resume_from
        self._ledger = TurnLedger(total_budget=turn_budget)
        self._step_runner = step_runner
        self._interrupted: bool = False
        self._completed_steps: list[str] = []
        self._step_results: dict[str, PortifyStepResult] = {}

        # Signal handler integration points (T03.04 / T03.09)
        self._prev_sigint: Optional[Callable] = None
        self._prev_sigterm: Optional[Callable] = None

    # ------------------------------------------------------------------
    # Signal handling (T03.09)
    # ------------------------------------------------------------------

    def _install_signal_handlers(self) -> None:
        """Register SIGINT / SIGTERM handlers for graceful shutdown."""
        def _handle(signum: int, frame) -> None:
            self._interrupted = True

        try:
            self._prev_sigint = signal.signal(signal.SIGINT, _handle)
            self._prev_sigterm = signal.signal(signal.SIGTERM, _handle)
        except (OSError, ValueError):
            # Non-main thread or OS doesn't support — skip gracefully
            pass

    def _restore_signal_handlers(self) -> None:
        """Restore prior signal handlers after execution."""
        try:
            if self._prev_sigint is not None:
                signal.signal(signal.SIGINT, self._prev_sigint)
            if self._prev_sigterm is not None:
                signal.signal(signal.SIGTERM, self._prev_sigterm)
        except (OSError, ValueError):
            pass

    # ------------------------------------------------------------------
    # Step filtering
    # ------------------------------------------------------------------

    def _should_execute(self, step: PortifyStep) -> bool:
        """Return True if this step should be executed given current mode."""
        if self.dry_run:
            return step.phase_type in DRY_RUN_PHASE_TYPES
        return True

    def _should_skip_for_resume(self, step: PortifyStep, resume_started: bool) -> bool:
        """Return True if this step should be skipped because --resume hasn't reached it."""
        return not resume_started

    # ------------------------------------------------------------------
    # Step execution
    # ------------------------------------------------------------------

    def _execute_step(self, step: PortifyStep) -> PortifyStatus:
        """Execute a single step with retry logic (retry_limit=1 for PASS_NO_SIGNAL)."""
        if self._step_runner is not None:
            exit_code, stdout, timed_out = self._step_runner(step)
        else:
            # Default: no-op (real subprocess invocation belongs in process.py)
            exit_code, stdout, timed_out = 0, "", False

        artifact_path = step.output_file
        status = _determine_status(exit_code, timed_out, stdout, artifact_path)
        self._ledger.consume(1)

        # Retry once on PASS_NO_SIGNAL (retry_limit=1 per NFR-002)
        if status == PortifyStatus.PASS_NO_SIGNAL and step.retry_limit >= 1:
            if self._ledger.can_launch():
                if self._step_runner is not None:
                    exit_code, stdout, timed_out = self._step_runner(step)
                else:
                    exit_code, stdout, timed_out = 0, "", False
                self._ledger.consume(1)
                status = _determine_status(exit_code, timed_out, stdout, artifact_path)

        return status

    # ------------------------------------------------------------------
    # Main execution loop
    # ------------------------------------------------------------------

    def run(self) -> PortifyOutcome:
        """Execute all steps sequentially. Returns pipeline outcome."""
        self._install_signal_handlers()
        outcome = PortifyOutcome.SUCCESS
        resume_started = (self.resume_from == "")  # True if no resume target

        try:
            for step in self.steps:
                # Check for interrupt before each step
                if self._interrupted:
                    outcome = PortifyOutcome.INTERRUPTED
                    break

                # Resume skip logic
                if not resume_started:
                    if step.step_id == self.resume_from:
                        resume_started = True
                    else:
                        step.status = PortifyStatus.SKIPPED
                        continue

                # Dry-run filtering
                if not self._should_execute(step):
                    step.status = PortifyStatus.SKIPPED
                    continue

                # Budget check before launch (FR-040)
                if not self._ledger.can_launch():
                    outcome = PortifyOutcome.HALTED
                    break

                step.status = PortifyStatus.RUNNING
                status = self._execute_step(step)
                step.status = status

                if status in (PortifyStatus.PASS, PortifyStatus.PASS_NO_SIGNAL, PortifyStatus.PASS_NO_REPORT):
                    self._completed_steps.append(step.step_id)
                elif status == PortifyStatus.TIMEOUT:
                    outcome = PortifyOutcome.TIMEOUT
                    break
                elif status == PortifyStatus.ERROR:
                    outcome = PortifyOutcome.FAILURE
                    break

                # Check interrupt after step completes
                if self._interrupted:
                    outcome = PortifyOutcome.INTERRUPTED
                    break

        finally:
            self._restore_signal_handlers()
            # Determine resume step (first non-completed step)
            resume_step = ""
            for s in self.steps:
                if s.status in (PortifyStatus.PENDING, PortifyStatus.INCOMPLETE):
                    resume_step = s.step_id
                    break
            _emit_return_contract(
                workdir=self.workdir,
                outcome=outcome if not self.dry_run else PortifyOutcome.DRY_RUN,
                steps=self.steps,
                completed_steps=self._completed_steps,
                resume_from_step_id=resume_step,
            )

        return outcome
