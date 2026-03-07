"""Trailing gate infrastructure -- async gate evaluation with deferred remediation.

Provides three components for non-blocking gate evaluation:
- TrailingGateRunner: daemon-thread gate evaluator with submit/drain/wait/cancel
- GateResultQueue: thread-safe result collection from concurrent gate evaluations
- DeferredRemediationLog: persistent log of gate failures requiring remediation

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from queue import Empty, Queue
from typing import Callable, Protocol, runtime_checkable

from .gates import gate_passed
from .models import GateCriteria, GateMode, Step, StepResult

_log = logging.getLogger("superclaude.pipeline.trailing_gate")


# ---------------------------------------------------------------------------
# T05.02 -- GateResultQueue
# ---------------------------------------------------------------------------


@dataclass
class TrailingGateResult:
    """Result of a trailing gate evaluation."""

    step_id: str
    passed: bool
    evaluation_ms: float
    failure_reason: str | None = None


class GateResultQueue:
    """Thread-safe queue for collecting gate evaluation results.

    Wraps stdlib ``queue.Queue`` with typed put/drain/pending_count methods.
    Safe for concurrent access from multiple daemon threads.
    """

    def __init__(self) -> None:
        self._queue: Queue[TrailingGateResult] = Queue()
        self._pending = 0
        self._lock = threading.Lock()

    def put(self, result: TrailingGateResult) -> None:
        """Enqueue a gate result. Thread-safe."""
        self._queue.put(result)
        with self._lock:
            self._pending += 1

    def drain(self) -> list[TrailingGateResult]:
        """Collect all available results without blocking.

        Returns a list of all results currently in the queue.
        """
        results: list[TrailingGateResult] = []
        while True:
            try:
                result = self._queue.get_nowait()
                results.append(result)
            except Empty:
                break
        with self._lock:
            self._pending = max(0, self._pending - len(results))
        return results

    def pending_count(self) -> int:
        """Return count of unprocessed results."""
        return self._queue.qsize()


# ---------------------------------------------------------------------------
# T05.01 -- TrailingGateRunner
# ---------------------------------------------------------------------------


class TrailingGateRunner:
    """Daemon-thread gate evaluator for trailing gate mode.

    Spawns daemon threads to evaluate gate criteria on step output files
    after the step subprocess completes. Results are collected via the
    internal GateResultQueue.

    Thread safety: submit() and drain() may be called concurrently from
    any thread. cancel() propagates to all active daemon threads.
    """

    def __init__(self, result_queue: GateResultQueue | None = None) -> None:
        self._queue = result_queue or GateResultQueue()
        self._threads: list[threading.Thread] = []
        self._cancelled = threading.Event()
        self._pending_count = 0
        self._lock = threading.Lock()

    @property
    def result_queue(self) -> GateResultQueue:
        return self._queue

    def submit(
        self,
        step: Step,
        gate_check: Callable[[Path, GateCriteria], tuple[bool, str | None]] = gate_passed,
    ) -> None:
        """Spawn a daemon thread to evaluate gate criteria on step output.

        The thread terminates after evaluation completes or cancellation.
        """
        if step.gate is None:
            # No gate to evaluate; submit a pass result immediately
            self._queue.put(
                TrailingGateResult(
                    step_id=step.id,
                    passed=True,
                    evaluation_ms=0.0,
                    failure_reason=None,
                )
            )
            return

        with self._lock:
            self._pending_count += 1

        def _evaluate() -> None:
            try:
                if self._cancelled.is_set():
                    return
                start = time.monotonic()
                passed, reason = gate_check(step.output_file, step.gate)
                elapsed_ms = (time.monotonic() - start) * 1000
                result = TrailingGateResult(
                    step_id=step.id,
                    passed=passed,
                    evaluation_ms=elapsed_ms,
                    failure_reason=reason,
                )
                self._queue.put(result)
                _log.debug(
                    "Trailing gate for '%s': %s (%.1fms)",
                    step.id,
                    "PASS" if passed else "FAIL",
                    elapsed_ms,
                )
            except Exception:
                _log.exception("Trailing gate evaluation error for step '%s'", step.id)
                self._queue.put(
                    TrailingGateResult(
                        step_id=step.id,
                        passed=False,
                        evaluation_ms=0.0,
                        failure_reason="Gate evaluation raised an exception",
                    )
                )
            finally:
                with self._lock:
                    self._pending_count -= 1

        t = threading.Thread(target=_evaluate, daemon=True)
        self._threads.append(t)
        t.start()

    def drain(self) -> list[TrailingGateResult]:
        """Collect all completed gate results."""
        return self._queue.drain()

    def wait_for_pending(self, timeout: float = 30.0) -> list[TrailingGateResult]:
        """Block until all pending gate evaluations complete or timeout.

        Returns all accumulated results. Never hangs indefinitely.
        """
        deadline = time.monotonic() + timeout
        # Join all active threads with bounded timeout
        for t in list(self._threads):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                _log.warning("wait_for_pending timed out with %d threads still active", self._pending_count)
                break
            t.join(timeout=remaining)

        # Drain whatever results are available
        return self.drain()

    def cancel(self) -> None:
        """Signal cancellation to all pending daemon threads.

        Threads check the cancellation event and terminate gracefully.
        """
        self._cancelled.set()
        # Give threads a brief window to notice cancellation
        for t in list(self._threads):
            t.join(timeout=1.0)
        self._threads.clear()

    @property
    def pending_count(self) -> int:
        """Number of gate evaluations still in progress."""
        with self._lock:
            return self._pending_count


# ---------------------------------------------------------------------------
# T05.03 -- DeferredRemediationLog
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# T07.01 -- TrailingGatePolicy Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class TrailingGatePolicy(Protocol):
    """Consumer-owned hooks for remediation step construction and file tracking.

    The sprint runner implements this protocol to build remediation steps
    and detect file changes, decoupling gate infrastructure from sprint-specific
    logic.

    Methods:
        build_remediation_step: Construct a focused remediation Step from a gate failure.
        files_changed: Return the set of file paths modified by a step execution.
    """

    def build_remediation_step(self, gate_result: TrailingGateResult) -> Step:
        """Build a remediation Step targeting the specific gate failure.

        Args:
            gate_result: The failed gate evaluation result.

        Returns:
            A Step configured to remediate the specific failure.
        """
        ...

    def files_changed(self, step_result: StepResult) -> set[Path]:
        """Return file paths modified during step execution.

        Args:
            step_result: The result of executing a step.

        Returns:
            Set of Path objects for files changed by the step.
        """
        ...


# ---------------------------------------------------------------------------
# T07.02 -- Remediation Prompt Construction
# ---------------------------------------------------------------------------


def build_remediation_prompt(
    gate_result: TrailingGateResult,
    original_step: Step,
    file_paths: set[Path] | None = None,
) -> str:
    """Build a focused remediation prompt from gate failure data.

    Assembles a subprocess prompt containing:
    - Gate failure reason (specific to the failure)
    - Original acceptance criteria (from the step's gate)
    - File paths involved in the failure
    - Remediation-specific instructions

    The prompt is scoped to the specific failure, not a re-execution
    of the full task.

    Args:
        gate_result: The failed gate evaluation result.
        original_step: The original Step that failed the gate.
        file_paths: Optional set of file paths involved in the failure.

    Returns:
        A deterministic remediation prompt string.
    """
    sections: list[str] = []

    # Header
    sections.append(
        f"# Remediation for step '{gate_result.step_id}'\n"
    )

    # Failure reason
    reason = gate_result.failure_reason or "Unknown gate failure"
    sections.append(
        f"## Gate Failure\n{reason}\n"
    )

    # Original acceptance criteria
    if original_step.gate is not None:
        gate = original_step.gate
        criteria_lines = [
            f"- Required frontmatter fields: {', '.join(gate.required_frontmatter_fields)}",
            f"- Minimum lines: {gate.min_lines}",
            f"- Enforcement tier: {gate.enforcement_tier}",
        ]
        if gate.semantic_checks:
            for check in gate.semantic_checks:
                criteria_lines.append(f"- Semantic check: {check.name}")
        sections.append(
            "## Acceptance Criteria\n" + "\n".join(criteria_lines) + "\n"
        )

    # File paths
    if file_paths:
        path_lines = [f"- {p}" for p in sorted(file_paths)]
        sections.append(
            "## Files Involved\n" + "\n".join(path_lines) + "\n"
        )

    # Instructions
    sections.append(
        "## Instructions\n"
        "Fix ONLY the specific gate failure described above.\n"
        "Do not re-execute the full task. Focus on making the output "
        "satisfy the acceptance criteria.\n"
        f"Output file: {original_step.output_file}\n"
    )

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# T07.03 -- Remediation Retry with TurnLedger Integration
# ---------------------------------------------------------------------------


class RemediationRetryStatus(Enum):
    """Outcome of a remediation retry sequence."""

    PASS_FIRST_ATTEMPT = "pass_first_attempt"
    PASS_SECOND_ATTEMPT = "pass_second_attempt"
    PERSISTENT_FAILURE = "persistent_failure"
    BUDGET_EXHAUSTED = "budget_exhausted"


@dataclass
class RemediationRetryResult:
    """Result of a remediation retry sequence."""

    status: RemediationRetryStatus
    attempts_made: int
    turns_consumed: int
    final_gate_result: TrailingGateResult | None = None


def attempt_remediation(
    remediation_step: Step,
    turns_per_attempt: int,
    can_remediate: Callable[[], bool],
    debit: Callable[[int], None],
    run_step: Callable[[Step], StepResult],
    check_gate: Callable[[StepResult], TrailingGateResult],
) -> RemediationRetryResult:
    """Execute remediation with retry-once semantics and budget integration.

    State machine:
    - Pre-check: can_remediate() → False → BUDGET_EXHAUSTED
    - ATTEMPT_1: debit → run → gate → pass → PASS_FIRST_ATTEMPT
    - ATTEMPT_1 fail: can_remediate() check → False → PERSISTENT_FAILURE (1 attempt debited)
    - ATTEMPT_2: debit → run → gate → pass → PASS_SECOND_ATTEMPT
    - ATTEMPT_2 fail: PERSISTENT_FAILURE (both attempts debited)

    Both attempts' turns are consumed on persistent failure (no reimbursement).

    Args:
        remediation_step: The Step to execute for remediation.
        turns_per_attempt: Turns to debit per attempt.
        can_remediate: Callable returning True if budget allows remediation.
        debit: Callable to consume turns from budget.
        run_step: Callable to execute the remediation step.
        check_gate: Callable to evaluate gate on step result.

    Returns:
        RemediationRetryResult with status and accounting.
    """
    total_turns = 0

    # Pre-check: enough budget for first attempt?
    if not can_remediate():
        return RemediationRetryResult(
            status=RemediationRetryStatus.BUDGET_EXHAUSTED,
            attempts_made=0,
            turns_consumed=0,
        )

    # --- Attempt 1 ---
    debit(turns_per_attempt)
    total_turns += turns_per_attempt
    result_1 = run_step(remediation_step)
    gate_1 = check_gate(result_1)

    if gate_1.passed:
        return RemediationRetryResult(
            status=RemediationRetryStatus.PASS_FIRST_ATTEMPT,
            attempts_made=1,
            turns_consumed=total_turns,
            final_gate_result=gate_1,
        )

    _log.info(
        "Remediation attempt 1 for '%s' failed: %s",
        remediation_step.id, gate_1.failure_reason,
    )

    # Pre-check before attempt 2
    if not can_remediate():
        return RemediationRetryResult(
            status=RemediationRetryStatus.PERSISTENT_FAILURE,
            attempts_made=1,
            turns_consumed=total_turns,
            final_gate_result=gate_1,
        )

    # --- Attempt 2 ---
    debit(turns_per_attempt)
    total_turns += turns_per_attempt
    result_2 = run_step(remediation_step)
    gate_2 = check_gate(result_2)

    if gate_2.passed:
        return RemediationRetryResult(
            status=RemediationRetryStatus.PASS_SECOND_ATTEMPT,
            attempts_made=2,
            turns_consumed=total_turns,
            final_gate_result=gate_2,
        )

    _log.info(
        "Remediation attempt 2 for '%s' failed (persistent): %s",
        remediation_step.id, gate_2.failure_reason,
    )

    # Persistent failure: both attempts' turns lost
    return RemediationRetryResult(
        status=RemediationRetryStatus.PERSISTENT_FAILURE,
        attempts_made=2,
        turns_consumed=total_turns,
        final_gate_result=gate_2,
    )


class RemediationStatus(Enum):
    """Status of a deferred remediation entry."""

    PENDING = "pending"
    REMEDIATED = "remediated"
    WAIVED = "waived"


@dataclass
class RemediationEntry:
    """A single deferred remediation record."""

    step_id: str
    gate_result: dict  # serialized TrailingGateResult
    failure_reason: str
    remediation_status: str = RemediationStatus.PENDING.value

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "gate_result": self.gate_result,
            "failure_reason": self.failure_reason,
            "remediation_status": self.remediation_status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> RemediationEntry:
        return cls(
            step_id=data["step_id"],
            gate_result=data["gate_result"],
            failure_reason=data["failure_reason"],
            remediation_status=data.get("remediation_status", RemediationStatus.PENDING.value),
        )


class DeferredRemediationLog:
    """Persistent log of gate failures requiring remediation.

    Single-writer thread safety: main thread writes, daemon threads may read.
    Supports disk persistence for --resume recovery.
    """

    def __init__(self, persist_path: Path | None = None) -> None:
        self._entries: list[RemediationEntry] = []
        self._persist_path = persist_path
        self._lock = threading.Lock()

    def append(self, gate_result: TrailingGateResult) -> None:
        """Add a remediation entry from a failed gate result."""
        entry = RemediationEntry(
            step_id=gate_result.step_id,
            gate_result={
                "step_id": gate_result.step_id,
                "passed": gate_result.passed,
                "evaluation_ms": gate_result.evaluation_ms,
                "failure_reason": gate_result.failure_reason,
            },
            failure_reason=gate_result.failure_reason or "Unknown failure",
        )
        with self._lock:
            self._entries.append(entry)
        if self._persist_path:
            self._write_to_disk()

    def pending_remediations(self) -> list[RemediationEntry]:
        """Return all unresolved remediation entries."""
        with self._lock:
            return [
                e for e in self._entries
                if e.remediation_status == RemediationStatus.PENDING.value
            ]

    def mark_remediated(self, step_id: str) -> bool:
        """Mark a remediation entry as resolved. Returns True if found."""
        with self._lock:
            for entry in self._entries:
                if entry.step_id == step_id and entry.remediation_status == RemediationStatus.PENDING.value:
                    entry.remediation_status = RemediationStatus.REMEDIATED.value
                    break
            else:
                return False
        if self._persist_path:
            self._write_to_disk()
        return True

    def serialize(self) -> str:
        """Serialize to JSON string for disk persistence."""
        with self._lock:
            data = [e.to_dict() for e in self._entries]
        return json.dumps(data, indent=2)

    @classmethod
    def deserialize(cls, json_str: str, persist_path: Path | None = None) -> DeferredRemediationLog:
        """Recover state from JSON string for --resume support."""
        data = json.loads(json_str)
        log = cls(persist_path=persist_path)
        log._entries = [RemediationEntry.from_dict(d) for d in data]
        return log

    def _write_to_disk(self) -> None:
        """Persist current state to disk."""
        if self._persist_path is None:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        self._persist_path.write_text(self.serialize(), encoding="utf-8")

    @classmethod
    def load_from_disk(cls, path: Path) -> DeferredRemediationLog:
        """Load from disk if file exists, otherwise return empty log."""
        if path.exists():
            content = path.read_text(encoding="utf-8")
            return cls.deserialize(content, persist_path=path)
        return cls(persist_path=path)

    @property
    def entry_count(self) -> int:
        with self._lock:
            return len(self._entries)


# ---------------------------------------------------------------------------
# T05.04 -- Scope-Based Gate Strategy
# ---------------------------------------------------------------------------


class GateScope(Enum):
    """Scope levels for gate strategy resolution."""

    RELEASE = "release"
    MILESTONE = "milestone"
    TASK = "task"


def resolve_gate_mode(
    scope: GateScope,
    config_gate_mode: GateMode = GateMode.BLOCKING,
    grace_period: int = 0,
) -> GateMode:
    """Resolve the effective gate mode based on scope and configuration.

    Rules:
    - Release scope: ALWAYS BLOCKING (immutable, not configurable)
    - Milestone scope: configurable, defaults to BLOCKING
    - Task scope: TRAILING when grace_period > 0, else BLOCKING

    Args:
        scope: The gate scope level.
        config_gate_mode: The configured gate mode (used for milestone scope).
        grace_period: Grace period in seconds (used for task scope).

    Returns:
        The effective GateMode for this scope.
    """
    if scope == GateScope.RELEASE:
        # Release gates are ALWAYS blocking -- enforced invariant
        return GateMode.BLOCKING

    if scope == GateScope.MILESTONE:
        # Milestone gates default to BLOCKING but are configurable
        return config_gate_mode

    if scope == GateScope.TASK:
        # Task gates trail when grace_period > 0
        if grace_period > 0:
            return GateMode.TRAILING
        return GateMode.BLOCKING

    # Fallback: BLOCKING
    return GateMode.BLOCKING
