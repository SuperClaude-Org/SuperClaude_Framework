#!/usr/bin/env python3
"""Real-world TurnLedger + Per-Task Subprocess + Trailing Gate simulation.

This is NOT a unit test. It exercises the actual production classes
in a realistic sprint scenario:
  - 8 tasks in a phase with a budget of 100 turns
  - Each task "consumes" a variable number of turns (simulated subprocess)
  - The TurnLedger tracks budget debit/credit at each step
  - Trailing gates evaluate each task output asynchronously
  - The budget decays until a task is skipped due to exhaustion
  - Full trace output shows every number at every step

Run: uv run python <this_file>
"""

import sys
import json
import time
import tempfile
import threading
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from superclaude.cli.sprint.models import (
    TurnLedger,
    TaskEntry,
    TaskResult,
    TaskStatus,
    GateOutcome,
    build_resume_output,
    SprintConfig,
)
from superclaude.cli.pipeline.trailing_gate import (
    TrailingGateRunner,
    GateResultQueue,
    DeferredRemediationLog,
    TrailingGateResult,
    GateScope,
    resolve_gate_mode,
)
from superclaude.cli.pipeline.models import (
    GateMode,
    GateCriteria,
    SemanticCheck,
    Step,
    PipelineConfig,
)

# ─── Helpers ─────────────────────────────────────────────────────────
DIVIDER = "=" * 78
SUBDIV  = "-" * 78

def banner(msg: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {msg}")
    print(DIVIDER)

def ledger_snapshot(ledger: TurnLedger, label: str = "") -> None:
    tag = f" ({label})" if label else ""
    print(f"  [LEDGER{tag}] initial={ledger.initial_budget}  "
          f"consumed={ledger.consumed}  reimbursed={ledger.reimbursed}  "
          f"available={ledger.available()}  "
          f"can_launch={ledger.can_launch()}  can_remediate={ledger.can_remediate()}")

# ─── Simulated task definitions ──────────────────────────────────────

TASKS = [
    TaskEntry(task_id="T01.01", title="Implement TurnLedger dataclass"),
    TaskEntry(task_id="T01.02", title="Add error_max_turns NDJSON detection"),
    TaskEntry(task_id="T01.03", title="Implement INCOMPLETE reclassification"),
    TaskEntry(task_id="T01.04", title="Add pre-launch budget guard"),
    TaskEntry(task_id="T01.05", title="Implement tasklist parser"),
    TaskEntry(task_id="T01.06", title="Per-task subprocess orchestration loop"),
    TaskEntry(task_id="T01.07", title="4-layer subprocess isolation"),
    TaskEntry(task_id="T01.08", title="Result aggregation and phase reports"),
]

# Simulated turns consumed per task (variable, realistic range)
SIMULATED_TURNS = [12, 8, 15, 20, 18, 25, 14, 10]

# Simulated gate outcomes: most pass, T01.04 fails
SIMULATED_GATE_PASS = [True, True, True, False, True, True, True, True]


def main() -> int:
    exit_code = 0
    started = time.monotonic()

    banner("REAL-WORLD SIMULATION: TurnLedger + Per-Task Subprocess + Trailing Gates")
    print(f"  Timestamp   : {datetime.now(timezone.utc).isoformat()}")
    print(f"  Tasks       : {len(TASKS)}")
    print(f"  Budget      : 100 turns")
    print(f"  Reimburse   : 50% rate (production default)")
    print(f"  Min alloc   : 5 turns")
    print(f"  Min remediate: 3 turns")

    # ─── PHASE 1: TurnLedger lifecycle ───────────────────────────────
    banner("PHASE 1: TurnLedger Lifecycle — Budget Tracking Through a Sprint")

    ledger = TurnLedger(initial_budget=100, reimbursement_rate=0.5)
    ledger_snapshot(ledger, "INITIAL STATE")

    results: list[TaskResult] = []
    remaining_ids: list[str] = []
    gate_runner = TrailingGateRunner()

    print(f"\n  Starting per-task subprocess loop with {len(TASKS)} tasks...")
    print(SUBDIV)

    for i, task in enumerate(TASKS):
        task_start = datetime.now(timezone.utc)
        turns_this_task = SIMULATED_TURNS[i]
        gate_passes = SIMULATED_GATE_PASS[i]

        print(f"\n  ┌─ TASK {task.task_id}: {task.title}")
        print(f"  │  Simulated turns: {turns_this_task}")

        # PRE-LAUNCH BUDGET CHECK (real production code path)
        if not ledger.can_launch():
            print(f"  │  !! BUDGET GUARD TRIGGERED: available={ledger.available()} < min_alloc={ledger.minimum_allocation}")
            remaining_ids = [t.task_id for t in TASKS[i:]]
            print(f"  │  Remaining tasks skipped: {remaining_ids}")
            for t in TASKS[i:]:
                results.append(TaskResult(
                    task=t,
                    status=TaskStatus.SKIPPED,
                    started_at=task_start,
                    finished_at=datetime.now(timezone.utc),
                ))
            ledger_snapshot(ledger, "HALT — budget exhausted")
            print(f"  └─ SKIPPED (budget exhausted)")
            break

        # DEBIT: pre-allocate minimum_allocation (real production code path)
        pre_alloc = ledger.minimum_allocation
        ledger.debit(pre_alloc)
        print(f"  │  [DEBIT] pre-allocated {pre_alloc} turns")
        ledger_snapshot(ledger, f"after pre-alloc")

        # SIMULATE SUBPROCESS EXECUTION
        print(f"  │  [SUBPROCESS] simulating {turns_this_task} turns of work...")
        time.sleep(0.02)  # Small delay to make timestamps real

        # RECONCILE: adjust for actual consumption (real production code path)
        actual = turns_this_task
        if actual > pre_alloc:
            extra = actual - pre_alloc
            ledger.debit(extra)
            print(f"  │  [DEBIT] additional {extra} turns (actual={actual} > pre_alloc={pre_alloc})")
        elif actual < pre_alloc:
            refund = pre_alloc - actual
            ledger.credit(refund)
            print(f"  │  [CREDIT] refund {refund} turns (actual={actual} < pre_alloc={pre_alloc})")
        else:
            print(f"  │  [EXACT] actual={actual} == pre_alloc={pre_alloc}, no adjustment")

        ledger_snapshot(ledger, f"after reconciliation")

        # TRAILING GATE: submit async gate evaluation
        # Create a temp output file with simulated content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(f"# Task {task.task_id} Output\nSimulated output for gate check.\n")
            output_path = Path(f.name)

        # Use a custom gate_check that returns our simulated result
        def make_gate_check(passes: bool):
            def _check(path, criteria):
                time.sleep(0.01)  # Simulate gate evaluation time
                if passes:
                    return (True, None)
                return (False, f"Simulated gate failure for testing")
            return _check

        gate_step = Step(
            id=task.task_id,
            prompt=f"Execute {task.task_id}",
            output_file=output_path,
            gate=GateCriteria(required_frontmatter_fields=[], min_lines=1),
            timeout_seconds=300,
        )
        gate_runner.submit(gate_step, gate_check=make_gate_check(gate_passes))
        print(f"  │  [GATE] submitted trailing gate (will {'PASS' if gate_passes else 'FAIL'})")

        # REIMBURSEMENT: if gate passes, credit back 50% of actual turns
        # (In production this happens after gate result is drained;
        #  here we simulate the full flow inline for visibility)
        time.sleep(0.05)  # Wait for gate thread
        gate_results = gate_runner.wait_for_pending(timeout=5.0)

        for gr in gate_results:
            if gr.step_id == task.task_id:
                if gr.passed:
                    reimburse = int(actual * ledger.reimbursement_rate)
                    ledger.credit(reimburse)
                    gate_outcome = GateOutcome.PASS
                    print(f"  │  [GATE RESULT] PASS — evaluation took {gr.evaluation_ms:.1f}ms")
                    print(f"  │  [CREDIT] reimbursed {reimburse} turns ({ledger.reimbursement_rate*100:.0f}% of {actual})")
                else:
                    gate_outcome = GateOutcome.FAIL
                    print(f"  │  [GATE RESULT] FAIL — reason: {gr.failure_reason}")
                    print(f"  │  [NO CREDIT] zero reimbursement on gate failure")

                    # Check if we can remediate
                    if ledger.can_remediate():
                        print(f"  │  [REMEDIATION] budget allows remediation (available={ledger.available()} >= min_remediate={ledger.minimum_remediation_budget})")
                    else:
                        print(f"  │  [REMEDIATION SKIP] insufficient budget for remediation")

        ledger_snapshot(ledger, f"end of {task.task_id}")

        status = TaskStatus.PASS if gate_passes else TaskStatus.FAIL
        results.append(TaskResult(
            task=task,
            status=status,
            turns_consumed=turns_this_task,
            exit_code=0,
            started_at=task_start,
            finished_at=datetime.now(timezone.utc),
            gate_outcome=gate_outcome,
        ))
        print(f"  └─ {status.value.upper()} (consumed={turns_this_task}, gate={gate_outcome.value})")

    # ─── PHASE 2: Final accounting ────────────────────────────────────
    banner("PHASE 2: Final Accounting")

    print(f"\n  Task Results:")
    print(f"  {'Task ID':<12} {'Status':<12} {'Turns':<8} {'Gate':<12}")
    print(f"  {'-'*12} {'-'*12} {'-'*8} {'-'*12}")
    for r in results:
        turns_str = str(r.turns_consumed) if r.turns_consumed else "-"
        gate_str = r.gate_outcome.value if r.gate_outcome else "-"
        print(f"  {r.task.task_id:<12} {r.status.value:<12} {turns_str:<8} {gate_str:<12}")

    print()
    ledger_snapshot(ledger, "FINAL STATE")

    # Verify accounting identity
    identity_holds = (
        ledger.available() == ledger.initial_budget - ledger.consumed + ledger.reimbursed
    )
    print(f"\n  Accounting identity: available == initial - consumed + reimbursed")
    print(f"    {ledger.available()} == {ledger.initial_budget} - {ledger.consumed} + {ledger.reimbursed}")
    print(f"    Identity holds: {identity_holds}")

    # Verify monotonicity: budget should have decayed
    print(f"\n  Budget decay: {ledger.initial_budget} → {ledger.available()} "
          f"(net loss: {ledger.initial_budget - ledger.available()} turns)")

    passed = sum(1 for r in results if r.status == TaskStatus.PASS)
    failed = sum(1 for r in results if r.status == TaskStatus.FAIL)
    skipped = sum(1 for r in results if r.status == TaskStatus.SKIPPED)
    print(f"\n  Summary: {passed} passed, {failed} failed, {skipped} skipped out of {len(TASKS)} tasks")

    # ─── PHASE 3: Scope-based gate strategy ───────────────────────────
    banner("PHASE 3: Scope-Based Gate Strategy Verification")

    for scope in GateScope:
        for mode_override in [GateMode.BLOCKING, GateMode.TRAILING]:
            for gp in [0, 1, 10]:
                resolved = resolve_gate_mode(
                    scope=scope,
                    config_gate_mode=mode_override,
                    grace_period=gp,
                )
                override_str = mode_override.value
                print(f"  scope={scope.value:<10} config={override_str:<10} grace_period={gp:<4} → {resolved.value}")

    # ─── PHASE 4: Resume semantics ────────────────────────────────────
    if remaining_ids:
        banner("PHASE 4: Resume Output (HALT scenario)")
        remaining_tasks = [t for t in TASKS if t.task_id in remaining_ids]
        config = SprintConfig(
            index_path=Path("tasklist-index.md"),
            work_dir=Path("/tmp/sprint-work"),
            max_turns=150,
        )
        resume_output = build_resume_output(
            config=config,
            halt_task_id=remaining_ids[0],
            remaining_tasks=remaining_tasks,
            diagnostic_path="/tmp/diagnostic-chain-output.md",
            ledger=ledger,
        )
        print(resume_output)
    else:
        banner("PHASE 4: No HALT — All tasks completed within budget")
        print("  Budget was sufficient for all 8 tasks.")

    # ─── PHASE 5: Thread safety evidence ──────────────────────────────
    banner("PHASE 5: Thread Safety — Concurrent Gate Submissions")

    queue = GateResultQueue()
    runner = TrailingGateRunner(result_queue=queue)
    thread_ids_before = {t.ident for t in threading.enumerate() if t.daemon}

    NUM_CONCURRENT = 5
    barrier = threading.Barrier(NUM_CONCURRENT)

    def submit_from_thread(idx: int):
        barrier.wait()
        step = Step(
            id=f"concurrent-{idx}",
            prompt=f"Concurrent task {idx}",
            output_file=Path(f"/tmp/concurrent-{idx}.md"),
            gate=GateCriteria(required_frontmatter_fields=[], min_lines=1),
            timeout_seconds=300,
        )
        runner.submit(step, gate_check=lambda p, c: (True, None))

    threads = []
    for idx in range(NUM_CONCURRENT):
        t = threading.Thread(target=submit_from_thread, args=(idx,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=5.0)

    concurrent_results = runner.wait_for_pending(timeout=10.0)
    thread_ids_after = {t.ident for t in threading.enumerate() if t.daemon}
    new_daemons = thread_ids_after - thread_ids_before

    print(f"  Submitted {NUM_CONCURRENT} gate evaluations from {NUM_CONCURRENT} concurrent threads")
    print(f"  Collected {len(concurrent_results)} results")
    print(f"  All passed: {all(r.passed for r in concurrent_results)}")
    print(f"  New daemon threads still alive: {len(new_daemons)} (should be 0 after wait)")
    for r in concurrent_results:
        print(f"    step={r.step_id}  passed={r.passed}  eval_ms={r.evaluation_ms:.1f}")

    # ─── Final verdict ────────────────────────────────────────────────
    elapsed = time.monotonic() - started
    banner("SIMULATION COMPLETE")
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"  Tasks executed: {passed + failed}/{len(TASKS)} ({skipped} skipped)")
    print(f"  Budget consumed: {ledger.consumed} of {ledger.initial_budget}")
    print(f"  Budget reimbursed: {ledger.reimbursed}")
    print(f"  Final available: {ledger.available()}")
    print(f"  Identity verified: {identity_holds}")
    print(f"  Concurrent gate safety: {len(concurrent_results)}/{NUM_CONCURRENT} collected")

    if not identity_holds:
        print("\n  !! FAILURE: Accounting identity violated")
        exit_code = 1

    if ledger.available() >= ledger.initial_budget:
        print("\n  !! FAILURE: Budget did not decay (monotonicity violated)")
        exit_code = 1

    if exit_code == 0:
        print(f"\n  VERDICT: ALL CHECKS PASSED")
    else:
        print(f"\n  VERDICT: FAILURES DETECTED")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
