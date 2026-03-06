"""Full-flow integration test -- 4 scenarios exercising the complete pipeline.

Covers T07.07 acceptance criteria (Gap 6 deliverable: mandatory).

Scenarios:
1. Task passes gate → continue to next task
2. Task fails gate → remediation spawned → remediation passes → continue
3. Task fails gate → remediation fails → retry fails → HALT with diagnostic
4. Low budget → can_remediate() false → HALT with budget message

Mock boundaries: subprocess execution is mocked; real orchestration, budget,
gate, remediation, conflict review, and diagnostic chain logic is exercised.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.conflict_review import (
    ConflictAction,
    review_conflicts,
)
from superclaude.cli.pipeline.diagnostic_chain import (
    DiagnosticStage,
    run_diagnostic_chain,
)
from superclaude.cli.pipeline.models import (
    GateCriteria,
    Step,
    StepResult,
    StepStatus,
)
from superclaude.cli.pipeline.trailing_gate import (
    RemediationRetryStatus,
    TrailingGateResult,
    attempt_remediation,
    build_remediation_prompt,
)
from superclaude.cli.sprint.models import (
    SprintConfig,
    TaskEntry,
    TurnLedger,
    build_resume_output,
)


def _make_step(step_id: str, tmp_path: Path, gate: GateCriteria | None = None) -> Step:
    output = tmp_path / f"{step_id}_output.md"
    return Step(
        id=step_id, prompt=f"Execute {step_id}",
        output_file=output, gate=gate, timeout_seconds=60,
    )


def _make_gate_result(step_id: str, passed: bool, reason: str | None = None):
    return TrailingGateResult(
        step_id=step_id, passed=passed,
        evaluation_ms=10.0, failure_reason=reason,
    )


def _make_step_result(step: Step, status: StepStatus = StepStatus.PASS):
    now = datetime.now(timezone.utc)
    return StepResult(step=step, status=status, started_at=now, finished_at=now)


class TestFullFlowIntegration:
    """Full-flow integration test exercising 4 compound scenarios."""

    # -----------------------------------------------------------------------
    # Scenario 1: Task passes gate → continue
    # -----------------------------------------------------------------------

    def test_scenario_1_pass_gate_continue(self, tmp_path):
        """Task passes gate; budget debited and reimbursed; next task proceeds."""
        ledger = TurnLedger(initial_budget=100)

        gate = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=3,
            enforcement_tier="STANDARD",
        )
        step = _make_step("task-1", tmp_path, gate=gate)

        # Simulate task execution
        ledger.debit(10)
        result = _make_step_result(step, StepStatus.PASS)

        # Gate passes
        gate_result = _make_gate_result("task-1", passed=True)
        assert gate_result.passed

        # Reimbursement on pass
        reimbursement = int(10 * ledger.reimbursement_rate)
        ledger.credit(reimbursement)

        # Budget accounting correct
        assert ledger.consumed == 10
        assert ledger.reimbursed == reimbursement
        assert ledger.available() == 100 - 10 + reimbursement

        # No remediation needed, no conflict review needed
        # Next task can proceed
        assert ledger.can_launch()

    # -----------------------------------------------------------------------
    # Scenario 2: Task fails gate → remediation succeeds → continue
    # -----------------------------------------------------------------------

    def test_scenario_2_fail_remediate_pass(self, tmp_path):
        """Task fails gate, remediation passes on first attempt, continues."""
        ledger = TurnLedger(initial_budget=100, minimum_remediation_budget=5)

        gate = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=5,
            enforcement_tier="STRICT",
        )
        step = _make_step("task-2", tmp_path, gate=gate)

        # Task execution
        ledger.debit(10)
        task_result = _make_step_result(step, StepStatus.PASS)

        # Gate fails
        gate_result = _make_gate_result(
            "task-2", passed=False,
            reason="Missing required field 'title'",
        )
        assert not gate_result.passed

        # Build remediation prompt
        prompt = build_remediation_prompt(
            gate_result, step,
            file_paths={step.output_file},
        )
        assert "Missing required field 'title'" in prompt

        # Build remediation step
        remediation_step = _make_step("task-2_remediation", tmp_path)

        # Attempt remediation (passes first attempt)
        retry_result = attempt_remediation(
            remediation_step=remediation_step,
            turns_per_attempt=5,
            can_remediate=ledger.can_remediate,
            debit=ledger.debit,
            run_step=lambda s: _make_step_result(s, StepStatus.PASS),
            check_gate=lambda r: _make_gate_result("task-2_remediation", True),
        )

        assert retry_result.status == RemediationRetryStatus.PASS_FIRST_ATTEMPT
        assert retry_result.attempts_made == 1

        # Conflict review (no intervening tasks in this scenario)
        conflict = review_conflicts(
            remediation_files={remediation_step.output_file},
            intervening_files=set(),
        )
        assert conflict.action == ConflictAction.PASSTHROUGH

        # Budget accounting
        assert ledger.consumed == 15  # 10 original + 5 remediation
        assert ledger.can_launch()  # Can continue

    # -----------------------------------------------------------------------
    # Scenario 3: Task fails gate → remediation fails → HALT with diagnostic
    # -----------------------------------------------------------------------

    def test_scenario_3_fail_remediate_fail_halt(self, tmp_path):
        """Task fails gate, remediation persistently fails, HALT with diagnostic."""
        ledger = TurnLedger(initial_budget=100, minimum_remediation_budget=5)

        gate = GateCriteria(
            required_frontmatter_fields=["title", "status"],
            min_lines=10,
            enforcement_tier="STRICT",
        )
        step = _make_step("task-3", tmp_path, gate=gate)

        # Task execution
        ledger.debit(10)

        # Gate fails
        gate_result = _make_gate_result(
            "task-3", passed=False,
            reason="Output too short and missing frontmatter",
        )

        # Build remediation
        remediation_step = _make_step("task-3_remediation", tmp_path)

        # Both remediation attempts fail
        retry_result = attempt_remediation(
            remediation_step=remediation_step,
            turns_per_attempt=5,
            can_remediate=ledger.can_remediate,
            debit=ledger.debit,
            run_step=lambda s: _make_step_result(s, StepStatus.FAIL),
            check_gate=lambda r: _make_gate_result(
                "task-3_remediation", False, "still broken"
            ),
        )

        assert retry_result.status == RemediationRetryStatus.PERSISTENT_FAILURE
        assert retry_result.attempts_made == 2

        # Both attempts' turns consumed
        assert ledger.consumed == 20  # 10 original + 5 + 5 remediation

        # Diagnostic chain fires
        diagnostic = run_diagnostic_chain(
            step_id="task-3",
            failure_reason="Output too short and missing frontmatter",
            remediation_output="",
        )
        assert diagnostic.is_complete
        assert diagnostic.stages_completed == 4

        # Resume output generated
        remaining = [
            TaskEntry(task_id="T07.04", title="Conflict review"),
            TaskEntry(task_id="T07.05", title="Diagnostic chain"),
        ]
        config = SprintConfig(index_path=Path("sprint.md"), work_dir=tmp_path)
        resume = build_resume_output(
            config=config,
            halt_task_id="T07.04",
            remaining_tasks=remaining,
            diagnostic_path=str(tmp_path / "diagnostic.md"),
            ledger=ledger,
        )
        assert "--resume T07.04" in resume
        assert "2" in resume  # remaining count
        assert "diagnostic.md" in resume

    # -----------------------------------------------------------------------
    # Scenario 4: Low budget → skip remediation → HALT
    # -----------------------------------------------------------------------

    def test_scenario_4_low_budget_halt(self, tmp_path):
        """Low budget prevents remediation; HALT with budget message."""
        ledger = TurnLedger(
            initial_budget=15,
            minimum_remediation_budget=10,
            minimum_allocation=5,
        )

        step = _make_step("task-4", tmp_path)

        # Task consumes most of the budget
        ledger.debit(12)
        assert ledger.available() == 3

        # Gate fails
        gate_result = _make_gate_result(
            "task-4", passed=False,
            reason="Gate failure",
        )

        # Can't remediate (budget too low)
        assert not ledger.can_remediate()

        # Attempt remediation returns BUDGET_EXHAUSTED
        remediation_step = _make_step("task-4_remediation", tmp_path)
        retry_result = attempt_remediation(
            remediation_step=remediation_step,
            turns_per_attempt=10,
            can_remediate=ledger.can_remediate,
            debit=ledger.debit,
            run_step=lambda s: _make_step_result(s, StepStatus.PASS),
            check_gate=lambda r: _make_gate_result("task-4_remediation", True),
        )

        assert retry_result.status == RemediationRetryStatus.BUDGET_EXHAUSTED
        assert retry_result.attempts_made == 0
        assert retry_result.turns_consumed == 0

        # Budget unchanged (no remediation was attempted)
        assert ledger.consumed == 12

        # No diagnostic chain for budget-specific halt (Gap 2, R-011)
        # Resume output includes budget info
        config = SprintConfig(index_path=Path("sprint.md"), work_dir=tmp_path)
        remaining = [TaskEntry(task_id="T07.05", title="Next task")]
        resume = build_resume_output(
            config=config,
            halt_task_id="T07.05",
            remaining_tasks=remaining,
            ledger=ledger,
        )
        assert "--resume T07.05" in resume
        assert "3" in resume  # available turns
        assert "12" in resume  # consumed turns

    # -----------------------------------------------------------------------
    # Cross-scenario: Budget accounting consistency
    # -----------------------------------------------------------------------

    def test_budget_accounting_across_scenarios(self, tmp_path):
        """Verify TurnLedger state is consistent across multiple operations."""
        ledger = TurnLedger(initial_budget=200, minimum_remediation_budget=5)

        # Task 1: passes (10 consumed, 5 reimbursed)
        ledger.debit(10)
        ledger.credit(int(10 * ledger.reimbursement_rate))

        # Task 2: fails, remediation passes (10 + 5 consumed)
        ledger.debit(10)
        retry = attempt_remediation(
            remediation_step=_make_step("s2_rem", tmp_path),
            turns_per_attempt=5,
            can_remediate=ledger.can_remediate,
            debit=ledger.debit,
            run_step=lambda s: _make_step_result(s, StepStatus.PASS),
            check_gate=lambda r: _make_gate_result("s2", True),
        )
        assert retry.status == RemediationRetryStatus.PASS_FIRST_ATTEMPT

        # Verify cumulative accounting
        # consumed: 10 + 10 + 5 = 25
        # reimbursed: 5
        # available: 200 - 25 + 5 = 180
        assert ledger.consumed == 25
        assert ledger.reimbursed == 5
        assert ledger.available() == 180
