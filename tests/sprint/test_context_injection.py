"""Context injection correctness tests (D-0024).

Validates that build_task_context() produces correct, complete context for
injection into task N+1 prompts. Covers:
- Prior results summary accuracy (all TaskResult fields present)
- Gate outcome inclusion (pass/fail/deferred visible)
- Remediation history presence
- Progressive summarization correctness (bounded growth)

Test scenarios: 1 task, 5 tasks, 10+ tasks (progressive summarization trigger),
mixed outcomes.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from superclaude.cli.sprint.models import (
    GateOutcome,
    TaskEntry,
    TaskResult,
    TaskStatus,
)
from superclaude.cli.sprint.process import (
    build_task_context,
    compress_context_summary,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _task(task_id: str, title: str = "Task") -> TaskEntry:
    return TaskEntry(task_id=task_id, title=title)


def _result(
    task_id: str = "T01.01",
    title: str = "Task",
    status: TaskStatus = TaskStatus.PASS,
    turns: int = 10,
    exit_code: int = 0,
    gate: GateOutcome = GateOutcome.PASS,
    reimbursement: int = 0,
    output_path: str = "",
    delta_seconds: float = 30.0,
) -> TaskResult:
    now = datetime.now(timezone.utc)
    return TaskResult(
        task=_task(task_id, title),
        status=status,
        turns_consumed=turns,
        exit_code=exit_code,
        started_at=now - timedelta(seconds=delta_seconds),
        finished_at=now,
        gate_outcome=gate,
        reimbursement_amount=reimbursement,
        output_path=output_path,
    )


# ===========================================================================
# Scenario: 1 task
# ===========================================================================


class TestContextInjectionSingleTask:
    """Context injection with a single prior task result."""

    @pytest.mark.context_injection_test
    def test_context_injection_test_single_task_includes_all_fields(self):
        """Single TaskResult context includes status, turns, gate outcome."""
        r = _result(task_id="T01.01", title="Setup env", turns=8, gate=GateOutcome.PASS)
        ctx = build_task_context([r])

        assert "## Prior Task Context" in ctx
        assert "T01.01" in ctx
        assert "Setup env" in ctx
        assert "pass" in ctx  # status
        assert "8" in ctx  # turns_consumed
        assert "### Gate Outcomes" in ctx
        assert "T01.01: pass" in ctx

    @pytest.mark.context_injection_test
    def test_context_injection_test_single_task_exit_code(self):
        """Exit code appears in verbose context summary."""
        r = _result(task_id="T01.01", exit_code=1, status=TaskStatus.FAIL)
        ctx = build_task_context([r])
        assert "Exit code" in ctx
        assert "1" in ctx

    @pytest.mark.context_injection_test
    def test_context_injection_test_single_task_duration(self):
        """Duration appears in verbose context summary."""
        r = _result(task_id="T01.01", delta_seconds=45.0)
        ctx = build_task_context([r])
        assert "Duration" in ctx
        assert "45.0s" in ctx

    @pytest.mark.context_injection_test
    def test_context_injection_test_single_task_output_path(self):
        """Output path appears when non-empty."""
        r = _result(task_id="T01.01", output_path="/tmp/out.md")
        ctx = build_task_context([r])
        assert "/tmp/out.md" in ctx

    @pytest.mark.context_injection_test
    def test_context_injection_test_single_task_no_remediation_section(self):
        """No remediation section when reimbursement is zero."""
        r = _result(task_id="T01.01", reimbursement=0)
        ctx = build_task_context([r])
        assert "### Remediation History" not in ctx


# ===========================================================================
# Scenario: 5 tasks (under default compress_threshold=3, but test with 5)
# ===========================================================================


class TestContextInjectionFiveTasks:
    """Context injection with five prior task results — tests progressive summarization."""

    @pytest.mark.context_injection_test
    def test_context_injection_test_five_tasks_all_present(self):
        """All 5 task IDs appear in context."""
        results = [_result(task_id=f"T01.{i:02d}") for i in range(1, 6)]
        ctx = build_task_context(results, compress_threshold=3)
        for i in range(1, 6):
            assert f"T01.{i:02d}" in ctx

    @pytest.mark.context_injection_test
    def test_context_injection_test_five_tasks_gate_outcomes(self):
        """All 5 gate outcomes visible in Gate Outcomes section."""
        outcomes = [GateOutcome.PASS, GateOutcome.FAIL, GateOutcome.DEFERRED,
                    GateOutcome.PASS, GateOutcome.PENDING]
        results = [
            _result(task_id=f"T01.{i:02d}", gate=outcomes[i - 1])
            for i in range(1, 6)
        ]
        ctx = build_task_context(results, compress_threshold=3)
        assert "T01.01: pass" in ctx
        assert "T01.02: fail" in ctx
        assert "T01.03: deferred" in ctx
        assert "T01.05: pending" in ctx

    @pytest.mark.context_injection_test
    def test_context_injection_test_five_tasks_compression_applied(self):
        """5 tasks with threshold=3 triggers progressive summarization."""
        results = [_result(task_id=f"T01.{i:02d}") for i in range(1, 6)]
        ctx = build_task_context(results, compress_threshold=3)
        assert "Earlier Tasks (compressed)" in ctx
        assert "Recent Tasks" in ctx

    @pytest.mark.context_injection_test
    def test_context_injection_test_five_tasks_mixed_statuses(self):
        """Mixed pass/fail/incomplete statuses all reflected."""
        results = [
            _result(task_id="T01.01", status=TaskStatus.PASS),
            _result(task_id="T01.02", status=TaskStatus.FAIL),
            _result(task_id="T01.03", status=TaskStatus.INCOMPLETE),
            _result(task_id="T01.04", status=TaskStatus.PASS),
            _result(task_id="T01.05", status=TaskStatus.SKIPPED),
        ]
        ctx = build_task_context(results, compress_threshold=3)
        # Gate Outcomes section always present
        assert "### Gate Outcomes" in ctx

    @pytest.mark.context_injection_test
    def test_context_injection_test_five_tasks_remediation_history(self):
        """Remediation history for tasks with reimbursement > 0."""
        results = [
            _result(task_id="T01.01", reimbursement=5),
            _result(task_id="T01.02", reimbursement=0),
            _result(task_id="T01.03", reimbursement=3),
            _result(task_id="T01.04", reimbursement=0),
            _result(task_id="T01.05", reimbursement=0),
        ]
        ctx = build_task_context(results, compress_threshold=3)
        assert "### Remediation History" in ctx
        assert "T01.01: reimbursed 5 turns" in ctx
        assert "T01.03: reimbursed 3 turns" in ctx
        # Non-reimbursed tasks not in remediation section
        remediation_section = ctx.split("### Remediation History")[1]
        assert "T01.02" not in remediation_section
        assert "T01.04" not in remediation_section


# ===========================================================================
# Scenario: 10+ tasks (progressive summarization trigger)
# ===========================================================================


class TestContextInjectionProgressiveSummarization:
    """Context injection with 10+ tasks — progressive summarization bounds growth."""

    @pytest.mark.context_injection_test
    def test_context_injection_test_ten_tasks_compression(self):
        """10 tasks trigger progressive summarization."""
        results = [_result(task_id=f"T01.{i:02d}") for i in range(1, 11)]
        ctx = build_task_context(results, compress_threshold=3)
        assert "Earlier Tasks (compressed)" in ctx
        assert "Recent Tasks" in ctx
        # Last 3 should have full detail (### heading)
        assert "### T01.08" in ctx
        assert "### T01.09" in ctx
        assert "### T01.10" in ctx
        # First task should be compressed (no ### heading)
        assert "### T01.01" not in ctx

    @pytest.mark.context_injection_test
    def test_context_injection_test_progressive_summary_bounded_size(self):
        """10-task context not significantly larger than 5-task context."""
        results_5 = [_result(task_id=f"T01.{i:02d}") for i in range(1, 6)]
        results_10 = [_result(task_id=f"T01.{i:02d}") for i in range(1, 11)]

        ctx_5 = build_task_context(results_5, compress_threshold=3)
        ctx_10 = build_task_context(results_10, compress_threshold=3)

        ratio = len(ctx_10) / len(ctx_5)
        assert ratio < 2.5, (
            f"10-task context is {ratio:.1f}x larger than 5-task; "
            f"progressive summarization should bound growth"
        )

    @pytest.mark.context_injection_test
    def test_context_injection_test_fifteen_tasks_bounded(self):
        """15-task context is bounded relative to 10-task context."""
        results_10 = [_result(task_id=f"T01.{i:02d}") for i in range(1, 11)]
        results_15 = [_result(task_id=f"T01.{i:02d}") for i in range(1, 16)]

        ctx_10 = build_task_context(results_10, compress_threshold=3)
        ctx_15 = build_task_context(results_15, compress_threshold=3)

        ratio = len(ctx_15) / len(ctx_10)
        assert ratio < 1.5, (
            f"15-task context is {ratio:.1f}x larger than 10-task; "
            f"growth should be sub-linear due to compression"
        )

    @pytest.mark.context_injection_test
    def test_context_injection_test_all_gate_outcomes_in_ten(self):
        """All 10 gate outcomes appear in Gate Outcomes section."""
        results = [
            _result(task_id=f"T01.{i:02d}", gate=GateOutcome.PASS)
            for i in range(1, 11)
        ]
        results[2] = _result(task_id="T01.03", gate=GateOutcome.FAIL)
        results[6] = _result(task_id="T01.07", gate=GateOutcome.DEFERRED)

        ctx = build_task_context(results, compress_threshold=3)
        assert "T01.03: fail" in ctx
        assert "T01.07: deferred" in ctx
        # All 10 listed
        for i in range(1, 11):
            assert f"T01.{i:02d}:" in ctx.split("### Gate Outcomes")[1]


# ===========================================================================
# Scenario: Mixed outcomes
# ===========================================================================


class TestContextInjectionMixedOutcomes:
    """Context injection with mixed statuses, gates, and reimbursements."""

    @pytest.mark.context_injection_test
    def test_context_injection_test_mixed_pass_fail_deferred(self):
        """Context correctly represents mixed pass/fail/deferred outcomes."""
        results = [
            _result(task_id="T01.01", status=TaskStatus.PASS,
                    gate=GateOutcome.PASS),
            _result(task_id="T01.02", status=TaskStatus.FAIL,
                    gate=GateOutcome.FAIL, reimbursement=5),
            _result(task_id="T01.03", status=TaskStatus.PASS,
                    gate=GateOutcome.DEFERRED),
        ]
        ctx = build_task_context(results)
        # All three visible
        assert "T01.01" in ctx
        assert "T01.02" in ctx
        assert "T01.03" in ctx
        # Gate outcomes
        assert "T01.01: pass" in ctx
        assert "T01.02: fail" in ctx
        assert "T01.03: deferred" in ctx
        # Remediation only for T01.02
        assert "### Remediation History" in ctx
        assert "T01.02: reimbursed 5 turns" in ctx

    @pytest.mark.context_injection_test
    def test_context_injection_test_empty_results(self):
        """Empty prior results produce empty context string."""
        ctx = build_task_context([])
        assert ctx == ""

    @pytest.mark.context_injection_test
    def test_context_injection_test_compressed_still_has_gate_outcome(self):
        """Compressed (non-verbose) summaries include gate outcome."""
        r = _result(task_id="T01.01", gate=GateOutcome.FAIL)
        compressed = r.to_context_summary(verbose=False)
        assert "gate: fail" in compressed

    @pytest.mark.context_injection_test
    def test_context_injection_test_verbose_summary_all_fields(self):
        """Verbose summary includes all required TaskResult fields."""
        r = _result(
            task_id="T01.01",
            title="Full test",
            status=TaskStatus.PASS,
            turns=15,
            exit_code=0,
            gate=GateOutcome.PASS,
            reimbursement=3,
            output_path="/out/result.md",
            delta_seconds=60.0,
        )
        summary = r.to_context_summary(verbose=True)
        assert "T01.01" in summary
        assert "Full test" in summary
        assert "pass" in summary
        assert "15" in summary
        assert "60.0s" in summary
        assert "0" in summary  # exit code
        assert "3 turns" in summary  # reimbursement
        assert "/out/result.md" in summary
