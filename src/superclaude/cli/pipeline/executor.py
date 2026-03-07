"""Pipeline executor -- generic step sequencer with retry, gates, and parallel dispatch.

Composition-via-callable design: consumers (sprint, roadmap) inject their own
StepRunner and callbacks. The executor handles step ordering, retry logic,
parallel dispatch, and state management.

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from typing import Callable, Protocol

from .gates import gate_passed
from .models import GateMode, PipelineConfig, Step, StepResult, StepStatus
from .trailing_gate import TrailingGateRunner

_log = logging.getLogger("superclaude.pipeline.executor")


class StepRunner(Protocol):
    """Callable that executes a single step's subprocess and returns a result.

    The runner is responsible for:
    - Launching the claude -p subprocess
    - Waiting for completion (with timeout enforcement)
    - Returning a StepResult with appropriate status

    The runner is NOT responsible for:
    - Retry logic (handled by execute_pipeline)
    - Gate checking (handled by execute_pipeline)
    - Step ordering (handled by execute_pipeline)
    """

    def __call__(
        self,
        step: Step,
        config: PipelineConfig,
        cancel_check: Callable[[], bool],
    ) -> StepResult: ...


def execute_pipeline(
    steps: list[Step | list[Step]],
    config: PipelineConfig,
    run_step: StepRunner,
    on_step_start: Callable[[Step], None] = lambda s: None,
    on_step_complete: Callable[[Step, StepResult], None] = lambda s, r: None,
    on_state_update: Callable[[dict], None] = lambda state: None,
    cancel_check: Callable[[], bool] = lambda: False,
    trailing_runner: TrailingGateRunner | None = None,
) -> list[StepResult]:
    """Generic pipeline executor.

    Processes steps in order. Each element in ``steps`` is either:
    - A single Step (executed sequentially)
    - A list[Step] (all steps in the list executed in parallel)

    For each step:
    1. Call on_step_start(step)
    2. Call run_step(step, config, cancel_check)
    3. If step has gate criteria: run gate_passed()
       - BLOCKING mode: evaluate synchronously, halt on failure
       - TRAILING mode (grace_period > 0): submit to TrailingGateRunner,
         continue execution; sync point at end collects results
    4. If gate fails and attempts < retry_limit: retry (go to 2)
    5. If gate fails and attempts exhausted: HALT
    6. Call on_step_complete(step, result)
    7. Call on_state_update(updated_state_dict)

    For parallel step groups:
    - All steps in the group run concurrently via _run_parallel_steps()
    - If any step in the group fails, remaining steps are cancelled
    - All results from the group must be PASS before proceeding

    Returns list of all StepResults (one per step, flattened).
    """
    all_results: list[StepResult] = []
    # Create trailing runner if grace_period > 0 and none provided
    _trailing = trailing_runner
    if _trailing is None and config.grace_period > 0:
        _trailing = TrailingGateRunner()

    for entry in steps:
        if cancel_check():
            break

        if isinstance(entry, list):
            # Parallel step group
            for s in entry:
                on_step_start(s)

            group_results = _run_parallel_steps(entry, config, run_step, cancel_check)
            all_results.extend(group_results)

            for r in group_results:
                on_step_complete(r.step, r)

            on_state_update(_build_state(all_results))

            # If any step in the group failed, halt
            if any(r.status != StepStatus.PASS for r in group_results):
                break
        else:
            # Sequential step -- branch on gate_mode
            result = _execute_single_step(
                entry, config, run_step, cancel_check,
                on_step_start, on_step_complete,
                trailing_runner=_trailing,
            )
            all_results.append(result)
            on_state_update(_build_state(all_results))

            if result.status != StepStatus.PASS:
                break

    # Sync point: collect all trailing gate results at end of pipeline
    if _trailing is not None:
        trailing_results = _trailing.wait_for_pending(
            timeout=max(30.0, float(config.grace_period))
        )
        for tr in trailing_results:
            if not tr.passed:
                _log.warning(
                    "Trailing gate failed for step '%s': %s",
                    tr.step_id,
                    tr.failure_reason,
                )

    return all_results


def _execute_single_step(
    step: Step,
    config: PipelineConfig,
    run_step: StepRunner,
    cancel_check: Callable[[], bool],
    on_step_start: Callable[[Step], None] = lambda s: None,
    on_step_complete: Callable[[Step, StepResult], None] = lambda s, r: None,
    trailing_runner: TrailingGateRunner | None = None,
) -> StepResult:
    """Execute a single step with retry logic and gate checking.

    Gate mode branching:
    - BLOCKING (default): gate evaluates synchronously before proceeding
    - TRAILING (grace_period > 0): gate submitted to TrailingGateRunner,
      step returns PASS immediately and execution continues
    - grace_period == 0 forces BLOCKING regardless of gate_mode
    """
    on_step_start(step)
    max_attempts = step.retry_limit + 1  # retry_limit=1 means 2 attempts total

    # Determine effective gate mode
    effective_mode = step.gate_mode
    if config.grace_period == 0:
        effective_mode = GateMode.BLOCKING

    for attempt in range(1, max_attempts + 1):
        if cancel_check():
            now = datetime.now(timezone.utc)
            result = StepResult(
                step=step,
                status=StepStatus.CANCELLED,
                attempt=attempt,
                gate_failure_reason="Cancelled by external signal",
                started_at=now,
                finished_at=now,
            )
            on_step_complete(step, result)
            return result

        result = run_step(step, config, cancel_check)
        result = StepResult(
            step=result.step,
            status=result.status,
            attempt=attempt,
            gate_failure_reason=result.gate_failure_reason,
            started_at=result.started_at,
            finished_at=result.finished_at,
        )

        # If step has no gate, trust the StepRunner's status
        if step.gate is None:
            on_step_complete(step, result)
            return result

        # If runner already reported failure/timeout, skip gate check
        if result.status in (StepStatus.TIMEOUT, StepStatus.CANCELLED):
            on_step_complete(step, result)
            return result

        # TRAILING mode: submit to runner, return PASS immediately
        if effective_mode == GateMode.TRAILING and trailing_runner is not None:
            trailing_runner.submit(step)
            result = StepResult(
                step=step,
                status=StepStatus.PASS,
                attempt=attempt,
                gate_failure_reason=None,
                started_at=result.started_at,
                finished_at=result.finished_at,
            )
            on_step_complete(step, result)
            return result

        # BLOCKING mode: run gate check synchronously
        passed, reason = gate_passed(step.output_file, step.gate)
        if passed:
            result = StepResult(
                step=step,
                status=StepStatus.PASS,
                attempt=attempt,
                gate_failure_reason=None,
                started_at=result.started_at,
                finished_at=result.finished_at,
            )
            on_step_complete(step, result)
            return result

        # Gate failed
        _log.info("Gate failed for step '%s' (attempt %d/%d): %s", step.id, attempt, max_attempts, reason)

        if attempt < max_attempts:
            continue  # retry

        # Exhausted retries
        result = StepResult(
            step=step,
            status=StepStatus.FAIL,
            attempt=attempt,
            gate_failure_reason=reason,
            started_at=result.started_at,
            finished_at=result.finished_at,
        )
        on_step_complete(step, result)
        return result

    # Should not reach here, but safety fallback
    now = datetime.now(timezone.utc)
    return StepResult(
        step=step,
        status=StepStatus.FAIL,
        attempt=max_attempts,
        gate_failure_reason="Unexpected: exhausted retry loop",
        started_at=now,
        finished_at=now,
    )


def _run_parallel_steps(
    steps: list[Step],
    config: PipelineConfig,
    run_step: StepRunner,
    cancel_check: Callable[[], bool],
) -> list[StepResult]:
    """Run steps concurrently. Returns when all complete or one fails.

    Cross-cancellation: if any step fails after retry, a shared Event
    is set, causing remaining steps to terminate their subprocesses.
    """
    cancel_event = threading.Event()
    results: list[StepResult | None] = [None] * len(steps)

    def _worker(idx: int, step: Step) -> None:
        def combined_cancel() -> bool:
            return cancel_check() or cancel_event.is_set()

        result = _execute_single_step(step, config, run_step, combined_cancel)
        results[idx] = result
        if result.status != StepStatus.PASS:
            cancel_event.set()

    threads = [
        threading.Thread(target=_worker, args=(i, s), daemon=True)
        for i, s in enumerate(steps)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Replace None entries (shouldn't happen, but defensive)
    final: list[StepResult] = []
    for i, r in enumerate(results):
        if r is not None:
            final.append(r)
        else:
            now = datetime.now(timezone.utc)
            final.append(StepResult(
                step=steps[i],
                status=StepStatus.CANCELLED,
                attempt=0,
                gate_failure_reason="Thread did not produce a result",
                started_at=now,
                finished_at=now,
            ))

    return final


def _build_state(results: list[StepResult]) -> dict:
    """Build a state dict from accumulated results."""
    return {
        "steps": {
            r.step.id: {
                "status": r.status.value,
                "attempt": r.attempt,
                "gate_failure_reason": r.gate_failure_reason,
            }
            for r in results
        },
        "total": len(results),
        "passed": sum(1 for r in results if r.status == StepStatus.PASS),
        "failed": sum(1 for r in results if r.status.is_failure),
    }
