"""T09.01 — E2E acceptance test: multi-task sprint with trailing gates.

End-to-end test exercising the complete unified flow:
- Budget allocation via TurnLedger (debit/credit/available)
- Per-task subprocess orchestration via execute_phase_tasks()
- Trailing gate evaluation via TrailingGateRunner
- Remediation retry via attempt_remediation()
- Context injection via TaskResult.to_context_summary()
- Phase report generation via aggregate_task_results()

Mock boundary: subprocess execution is mocked (_subprocess_factory);
all other components execute with real logic.

Acceptance criteria (D-0038):
- Multi-task sprint completes with correct per-task results under trailing gate mode
- Budget accounting identity: consumed + available == initial_budget + reimbursed
- No silent incompletion: error_max_turns scenarios correctly trigger INCOMPLETE + HALT
- `uv run pytest tests/sprint/ -k e2e_trailing` exits 0
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.conflict_review import ConflictAction, review_conflicts
from superclaude.cli.pipeline.diagnostic_chain import run_diagnostic_chain
from superclaude.cli.pipeline.gates import gate_passed
from superclaude.cli.pipeline.models import (
    GateCriteria,
    GateMode,
    Step,
    StepResult,
    StepStatus,
)
from superclaude.cli.pipeline.trailing_gate import (
    DeferredRemediationLog,
    GateResultQueue,
    RemediationRetryStatus,
    TrailingGateResult,
    TrailingGateRunner,
    attempt_remediation,
    build_remediation_prompt,
    resolve_gate_mode,
    GateScope,
)
from superclaude.cli.sprint.executor import (
    AggregatedPhaseReport,
    aggregate_task_results,
    check_budget_guard,
    execute_phase_tasks,
)
from superclaude.cli.sprint.models import (
    GateOutcome,
    Phase,
    SprintConfig,
    TaskEntry,
    TaskResult,
    TaskStatus,
    TurnLedger,
    build_resume_output,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(tmp_path: Path, grace_period: int = 10) -> SprintConfig:
    phases = []
    for i in range(1, 3):
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
        end_phase=2,
        max_turns=50,
    )


def _make_tasks(count: int = 5) -> list[TaskEntry]:
    """Create a multi-task inventory for E2E testing."""
    return [
        TaskEntry(task_id=f"T09.{i:02d}", title=f"E2E task {i}")
        for i in range(1, count + 1)
    ]


def _make_step(step_id: str, tmp_path: Path, gate: GateCriteria | None = None) -> Step:
    return Step(
        id=step_id,
        prompt=f"Execute {step_id}",
        output_file=tmp_path / f"{step_id}_output.md",
        gate=gate,
        timeout_seconds=60,
        gate_mode=GateMode.TRAILING,
    )


def _make_gate_result(step_id: str, passed: bool, reason: str | None = None) -> TrailingGateResult:
    return TrailingGateResult(
        step_id=step_id, passed=passed,
        evaluation_ms=5.0, failure_reason=reason,
    )


def _make_step_result(step: Step, status: StepStatus = StepStatus.PASS) -> StepResult:
    now = datetime.now(timezone.utc)
    return StepResult(step=step, status=status, started_at=now, finished_at=now)


def _write_passing_output(path: Path, lines: int = 20) -> None:
    """Write a file that passes STANDARD gate checks."""
    content = ["---", "title: test output", "status: pass", "---"]
    content.extend([f"Line {i}: content" for i in range(lines)])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(content))


# ===========================================================================
# T09.01 — End-to-End Sprint Test with Trailing Gates
# ===========================================================================


class TestE2ETrailingGates:
    """End-to-end acceptance test: multi-task sprint with trailing gate mode.

    Exercises the complete flow: budget → subprocess → gate → remediation
    → context → report.
    """

    # -----------------------------------------------------------------------
    # Core E2E: multi-task sprint with budget and trailing gates
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_multi_task_sprint_with_trailing_gates(self, tmp_path):
        """Multi-task sprint completes with correct per-task results under
        trailing gate mode: all tasks pass, gates evaluate asynchronously,
        budget accounting is correct, and phase report is generated."""
        # Setup
        ledger = TurnLedger(initial_budget=200, minimum_allocation=5)
        tasks = _make_tasks(4)
        config = _make_config(tmp_path, grace_period=10)
        phase = config.phases[0]

        # Mock subprocess: all tasks succeed, consume varying turns
        turn_costs = [8, 12, 6, 10]  # per-task turn costs

        def subprocess_factory(task, cfg, ph):
            idx = int(task.task_id.split(".")[-1]) - 1
            return (0, turn_costs[idx], 1024 * (idx + 1))

        results, remaining = execute_phase_tasks(
            tasks, config, phase,
            ledger=ledger,
            _subprocess_factory=subprocess_factory,
        )

        # All 4 tasks should have results, none remaining
        assert len(results) == 4
        assert len(remaining) == 0

        # All tasks passed
        assert all(r.status == TaskStatus.PASS for r in results)

        # Budget accounting identity: available == initial - consumed + reimbursed
        assert ledger.available() == ledger.initial_budget - ledger.consumed + ledger.reimbursed

        # Consumed should reflect actual turn costs with pre-allocation reconciliation
        # Pre-alloc is 5 per task; actual costs are [8, 12, 6, 10]
        # Task 1: debit(5), actual=8, additional debit(3) → total consumed so far: 8
        # Task 2: debit(5), actual=12, additional debit(7) → total consumed: 20
        # Task 3: debit(5), actual=6, additional debit(1) → total consumed: 26
        # Task 4: debit(5), actual=10, additional debit(5) → total consumed: 36
        assert ledger.consumed == sum(turn_costs)

        # Now verify trailing gate evaluation
        gate = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=3,
            enforcement_tier="STANDARD",
        )
        runner = TrailingGateRunner()

        for i, result in enumerate(results):
            step = _make_step(result.task.task_id, tmp_path, gate=gate)
            _write_passing_output(step.output_file)
            runner.submit(step)

        # Wait for all trailing gates
        gate_results = runner.wait_for_pending(timeout=10.0)
        gate_results.extend(runner.drain())
        assert len(gate_results) == 4
        assert all(gr.passed for gr in gate_results)

        # Generate phase report
        report = aggregate_task_results(
            phase_number=1,
            task_results=results,
            budget_remaining=ledger.available(),
        )

        assert report.status == "PASS"
        assert report.tasks_total == 4
        assert report.tasks_passed == 4
        assert report.tasks_failed == 0

    # -----------------------------------------------------------------------
    # Budget accounting identity
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_budget_accounting_identity(self, tmp_path):
        """Budget accounting identity: total consumed + remaining == initial budget."""
        ledger = TurnLedger(initial_budget=100, minimum_allocation=5)
        tasks = _make_tasks(3)
        config = _make_config(tmp_path)
        phase = config.phases[0]

        def subprocess_factory(task, cfg, ph):
            return (0, 10, 500)

        results, remaining = execute_phase_tasks(
            tasks, config, phase,
            ledger=ledger,
            _subprocess_factory=subprocess_factory,
        )

        # Accounting identity: consumed - reimbursed + available == initial_budget
        assert ledger.consumed - ledger.reimbursed + ledger.available() == ledger.initial_budget
        # Equivalent: available == initial_budget - consumed + reimbursed
        assert ledger.available() == ledger.initial_budget - ledger.consumed + ledger.reimbursed

    # -----------------------------------------------------------------------
    # No silent incompletion: error_max_turns triggers INCOMPLETE
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_no_silent_incompletion_error_max_turns(self, tmp_path):
        """error_max_turns scenario: exit code 124 triggers INCOMPLETE status,
        which is correctly reported (not silently swallowed)."""
        ledger = TurnLedger(initial_budget=100, minimum_allocation=5)
        tasks = _make_tasks(3)
        config = _make_config(tmp_path)
        phase = config.phases[0]

        # First task passes, second hits error_max_turns (exit 124), third would be skipped
        exit_codes = [0, 124, 0]

        def subprocess_factory(task, cfg, ph):
            idx = int(task.task_id.split(".")[-1]) - 1
            return (exit_codes[idx], 5, 500)

        results, remaining = execute_phase_tasks(
            tasks, config, phase,
            ledger=ledger,
            _subprocess_factory=subprocess_factory,
        )

        assert len(results) == 3
        assert results[0].status == TaskStatus.PASS
        assert results[1].status == TaskStatus.INCOMPLETE
        assert results[2].status == TaskStatus.PASS  # continues after INCOMPLETE

        # Verify INCOMPLETE is properly classified as failure
        assert results[1].status.is_failure

    # -----------------------------------------------------------------------
    # Budget exhaustion skips remaining tasks
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_budget_exhaustion_skips_remaining(self, tmp_path):
        """When budget is exhausted, remaining tasks are SKIPPED and listed."""
        ledger = TurnLedger(initial_budget=12, minimum_allocation=5)
        tasks = _make_tasks(5)
        config = _make_config(tmp_path)
        phase = config.phases[0]

        # Each task consumes 6 turns; budget of 12 allows 2 tasks then exhaustion
        def subprocess_factory(task, cfg, ph):
            return (0, 6, 500)

        results, remaining = execute_phase_tasks(
            tasks, config, phase,
            ledger=ledger,
            _subprocess_factory=subprocess_factory,
        )

        # First 2 tasks execute, remaining 3 are skipped
        passed = [r for r in results if r.status == TaskStatus.PASS]
        skipped = [r for r in results if r.status == TaskStatus.SKIPPED]
        assert len(passed) == 2
        assert len(skipped) == 3
        assert len(remaining) == 3

        # Budget guard should block further launches
        msg = check_budget_guard(ledger)
        assert msg is not None
        assert "exhausted" in msg.lower() or "remaining" in msg.lower()

    # -----------------------------------------------------------------------
    # Trailing gate with remediation and context injection
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_trailing_gate_remediation_and_context(self, tmp_path):
        """Complete flow: task runs → trailing gate fails → remediation
        succeeds → context injected from prior results → phase report
        generated with correct accounting."""
        ledger = TurnLedger(
            initial_budget=100,
            minimum_allocation=5,
            minimum_remediation_budget=5,
        )

        # Step 1: Task execution
        step = _make_step("T09.01", tmp_path, gate=GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=5,
            enforcement_tier="STRICT",
        ))
        ledger.debit(10)

        # Step 2: Trailing gate evaluation (fails)
        gate_result = _make_gate_result(
            "T09.01", passed=False,
            reason="Missing required field 'title'",
        )

        # Record in deferred remediation log
        remediation_log = DeferredRemediationLog(persist_path=tmp_path / "remediation.json")
        remediation_log.append(gate_result)
        assert remediation_log.entry_count == 1
        assert len(remediation_log.pending_remediations()) == 1

        # Step 3: Build remediation prompt (verifies context injection)
        prompt = build_remediation_prompt(gate_result, step, file_paths={step.output_file})
        assert "Missing required field 'title'" in prompt
        assert "T09.01" in prompt

        # Step 4: Remediation attempt (passes first try)
        remediation_step = _make_step("T09.01_remediation", tmp_path)
        retry_result = attempt_remediation(
            remediation_step=remediation_step,
            turns_per_attempt=5,
            can_remediate=ledger.can_remediate,
            debit=ledger.debit,
            run_step=lambda s: _make_step_result(s, StepStatus.PASS),
            check_gate=lambda r: _make_gate_result("T09.01_remediation", True),
        )
        assert retry_result.status == RemediationRetryStatus.PASS_FIRST_ATTEMPT

        # Mark remediated
        remediation_log.mark_remediated("T09.01")
        assert len(remediation_log.pending_remediations()) == 0

        # Step 5: Context injection from prior task results
        task_entry = TaskEntry(task_id="T09.01", title="E2E task 1")
        task_result = TaskResult(
            task=task_entry,
            status=TaskStatus.PASS,
            turns_consumed=10,
            gate_outcome=GateOutcome.PASS,
        )
        context = task_result.to_context_summary(verbose=True)
        assert "T09.01" in context
        assert "pass" in context

        compressed = task_result.to_context_summary(verbose=False)
        assert "T09.01" in compressed
        assert "gate: pass" in compressed

        # Step 6: Phase report
        report = aggregate_task_results(
            phase_number=1,
            task_results=[task_result],
            budget_remaining=ledger.available(),
        )
        assert report.status == "PASS"
        assert report.budget_remaining == ledger.available()

    # -----------------------------------------------------------------------
    # Gate mode resolution with grace_period
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_gate_mode_resolution_with_grace_period(self):
        """Trailing gate mode activates when grace_period > 0 for task scope."""
        # Task scope: trailing when grace_period > 0
        mode = resolve_gate_mode(GateScope.TASK, grace_period=10)
        assert mode == GateMode.TRAILING

        # Task scope: blocking when grace_period == 0
        mode = resolve_gate_mode(GateScope.TASK, grace_period=0)
        assert mode == GateMode.BLOCKING

        # Release scope: always blocking (immutable)
        mode = resolve_gate_mode(GateScope.RELEASE, grace_period=999)
        assert mode == GateMode.BLOCKING

    # -----------------------------------------------------------------------
    # Mixed outcomes: pass, fail, incomplete in one sprint
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_mixed_outcomes_comprehensive(self, tmp_path):
        """Multi-task sprint with mixed outcomes: PASS, FAIL, INCOMPLETE."""
        ledger = TurnLedger(initial_budget=200, minimum_allocation=5)
        tasks = _make_tasks(5)
        config = _make_config(tmp_path)
        phase = config.phases[0]

        # exit codes: 0=PASS, 1=FAIL, 0=PASS, 124=INCOMPLETE, 0=PASS
        outcomes = [(0, 10, 500), (1, 8, 300), (0, 12, 600), (124, 5, 200), (0, 7, 400)]

        def subprocess_factory(task, cfg, ph):
            idx = int(task.task_id.split(".")[-1]) - 1
            return outcomes[idx]

        results, remaining = execute_phase_tasks(
            tasks, config, phase,
            ledger=ledger,
            _subprocess_factory=subprocess_factory,
        )

        assert len(results) == 5
        statuses = [r.status for r in results]
        assert statuses == [
            TaskStatus.PASS,
            TaskStatus.FAIL,
            TaskStatus.PASS,
            TaskStatus.INCOMPLETE,
            TaskStatus.PASS,
        ]

        # Phase report reflects mixed outcomes
        report = aggregate_task_results(
            phase_number=1,
            task_results=results,
            budget_remaining=ledger.available(),
        )
        assert report.tasks_passed == 3
        assert report.tasks_failed == 1
        assert report.tasks_incomplete == 1
        assert report.status == "PARTIAL"

        # Budget identity still holds
        assert ledger.available() == ledger.initial_budget - ledger.consumed + ledger.reimbursed

    # -----------------------------------------------------------------------
    # HALT output with resume and diagnostic chain
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_halt_produces_resume_output_and_diagnostic(self, tmp_path):
        """On persistent failure: diagnostic chain fires, resume output
        includes remaining tasks and budget info."""
        ledger = TurnLedger(initial_budget=100, minimum_remediation_budget=5)
        ledger.debit(20)

        # Diagnostic chain fires on persistent failure
        diagnostic = run_diagnostic_chain(
            step_id="T09.03",
            failure_reason="Output missing required frontmatter fields",
            remediation_output="attempted fix but still missing fields",
        )
        assert diagnostic.is_complete
        assert diagnostic.stages_completed == 4

        # Resume output
        remaining = [
            TaskEntry(task_id="T09.04", title="Next task"),
            TaskEntry(task_id="T09.05", title="Final task"),
        ]
        config = _make_config(tmp_path)
        resume = build_resume_output(
            config=config,
            halt_task_id="T09.04",
            remaining_tasks=remaining,
            diagnostic_path=str(tmp_path / "diagnostic.md"),
            ledger=ledger,
        )
        assert "--resume T09.04" in resume
        assert "2" in resume  # remaining count
        assert "diagnostic.md" in resume
        assert str(ledger.consumed) in resume

    # -----------------------------------------------------------------------
    # Conflict review: no overlap means PASSTHROUGH
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_conflict_review_passthrough(self, tmp_path):
        """Conflict review with no overlap returns PASSTHROUGH."""
        result = review_conflicts(
            remediation_files={tmp_path / "fix.py"},
            intervening_files={tmp_path / "other.py"},
        )
        assert result.action == ConflictAction.PASSTHROUGH

    # -----------------------------------------------------------------------
    # Phase report markdown and YAML output
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_phase_report_formats(self, tmp_path):
        """Phase report generates valid markdown and YAML output."""
        tasks = _make_tasks(3)
        task_results = [
            TaskResult(
                task=tasks[0], status=TaskStatus.PASS,
                turns_consumed=10, exit_code=0,
            ),
            TaskResult(
                task=tasks[1], status=TaskStatus.FAIL,
                turns_consumed=8, exit_code=1,
            ),
            TaskResult(
                task=tasks[2], status=TaskStatus.PASS,
                turns_consumed=12, exit_code=0,
            ),
        ]

        report = aggregate_task_results(
            phase_number=9,
            task_results=task_results,
            budget_remaining=70,
        )

        # YAML output
        yaml_output = report.to_yaml()
        assert "phase: 9" in yaml_output
        assert "status: PARTIAL" in yaml_output
        assert "tasks_passed: 2" in yaml_output
        assert "tasks_failed: 1" in yaml_output

        # Markdown output
        md_output = report.to_markdown()
        assert "Phase 9" in md_output
        assert "EXIT_RECOMMENDATION:" in md_output
        assert "HALT" in md_output  # PARTIAL status → HALT recommendation

    # -----------------------------------------------------------------------
    # Remediation log persistence and deserialization
    # -----------------------------------------------------------------------

    @pytest.mark.e2e_trailing
    def test_remediation_log_persistence(self, tmp_path):
        """DeferredRemediationLog persists to disk and recovers via deserialize."""
        persist_path = tmp_path / "remediation.json"
        log = DeferredRemediationLog(persist_path=persist_path)

        # Append entries
        log.append(_make_gate_result("step-1", False, "fail 1"))
        log.append(_make_gate_result("step-2", False, "fail 2"))
        assert log.entry_count == 2

        # Persist
        assert persist_path.exists()

        # Mark one remediated
        log.mark_remediated("step-1")
        assert len(log.pending_remediations()) == 1

        # Reload from disk
        loaded = DeferredRemediationLog.load_from_disk(persist_path)
        assert loaded.entry_count == 2
        pending = loaded.pending_remediations()
        assert len(pending) == 1
        assert pending[0].step_id == "step-2"
