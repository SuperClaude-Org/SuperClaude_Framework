"""Tests for standalone convergence engine.

Covers:
- Convergence path: zero criticals -> CONVERGED
- Escalation path: max iterations reached -> ESCALATED
- Budget exhaustion path: budget guard triggers -> ESCALATED
- User rejection escalation
- State machine invariants
- Overall score computation
"""

from __future__ import annotations

import pytest

from superclaude.cli.cli_portify.convergence import (
    ConvergenceEngine,
    ConvergenceResult,
    ConvergenceState,
    EscalationReason,
    IterationResult,
    SimpleBudgetGuard,
)


class TestConvergencePath:

    def test_zero_criticals_converges(self):
        """Zero unaddressed CRITICALs should produce CONVERGED state."""
        engine = ConvergenceEngine(max_iterations=3)

        result = IterationResult(
            iteration=1,
            unaddressed_criticals=0,
            quality_scores={"clarity": 8.0, "completeness": 7.5, "testability": 9.0, "consistency": 8.5},
        )
        state = engine.submit(result)

        assert state == ConvergenceState.CONVERGED
        assert engine.is_done
        final = engine.result()
        assert final.is_converged
        assert final.iterations_completed == 1
        assert final.escalation_reason is None

    def test_convergence_on_second_iteration(self):
        """Convergence on second iteration after one with criticals."""
        engine = ConvergenceEngine(max_iterations=3)

        # First iteration: 2 criticals
        engine.submit(IterationResult(iteration=1, unaddressed_criticals=2))
        assert not engine.is_done

        # Second iteration: 0 criticals
        state = engine.submit(IterationResult(iteration=2, unaddressed_criticals=0))
        assert state == ConvergenceState.CONVERGED
        assert engine.result().iterations_completed == 2


class TestEscalationPath:

    def test_max_iterations_escalates(self):
        """Reaching max iterations with remaining criticals -> ESCALATED."""
        engine = ConvergenceEngine(max_iterations=2)

        engine.submit(IterationResult(iteration=1, unaddressed_criticals=3))
        state = engine.submit(IterationResult(iteration=2, unaddressed_criticals=1))

        assert state == ConvergenceState.ESCALATED
        assert engine.is_done
        final = engine.result()
        assert final.is_escalated
        assert final.escalation_reason == EscalationReason.MAX_ITERATIONS

    def test_default_max_iterations_is_3(self):
        engine = ConvergenceEngine()
        engine.submit(IterationResult(iteration=1, unaddressed_criticals=5))
        assert not engine.is_done
        engine.submit(IterationResult(iteration=2, unaddressed_criticals=3))
        assert not engine.is_done
        engine.submit(IterationResult(iteration=3, unaddressed_criticals=1))
        assert engine.is_done
        assert engine.state == ConvergenceState.ESCALATED


class TestBudgetExhaustionPath:

    def test_budget_exhaustion_escalates(self):
        """Budget guard should trigger ESCALATED when budget is exhausted."""
        guard = SimpleBudgetGuard(total_budget=1.5, per_iteration_cost=1.0)
        engine = ConvergenceEngine(max_iterations=5, budget_guard=guard)

        # First iteration uses 1.0 budget
        engine.submit(IterationResult(iteration=1, unaddressed_criticals=2))
        guard.record_spend(1.0)

        # Check budget before second iteration — only 0.5 left, not enough
        assert not engine.check_budget(1.0)
        engine.escalate_budget()

        assert engine.is_done
        assert engine.state == ConvergenceState.ESCALATED
        final = engine.result()
        assert final.escalation_reason == EscalationReason.BUDGET_EXHAUSTED

    def test_no_budget_guard_always_passes(self):
        """Without a budget guard, check_budget always returns True."""
        engine = ConvergenceEngine(max_iterations=3)
        assert engine.check_budget(100.0)

    def test_budget_guard_sufficient(self):
        guard = SimpleBudgetGuard(total_budget=10.0, per_iteration_cost=1.0)
        engine = ConvergenceEngine(max_iterations=3, budget_guard=guard)
        assert engine.check_budget(1.0)


class TestUserRejection:

    def test_user_rejection_escalates(self):
        engine = ConvergenceEngine(max_iterations=3)
        engine.submit(IterationResult(iteration=1, unaddressed_criticals=0))
        # Even though converged, user can escalate
        # (in practice this wouldn't happen, but testing the mechanism)
        # Actually, after convergence, submit would raise.
        # Let's test user escalation before convergence.
        engine2 = ConvergenceEngine(max_iterations=3)
        engine2.escalate_user()
        assert engine2.is_done
        assert engine2.result().escalation_reason == EscalationReason.USER_REJECTED


class TestStateMachineInvariants:

    def test_cannot_submit_after_terminal(self):
        engine = ConvergenceEngine(max_iterations=3)
        engine.submit(IterationResult(iteration=1, unaddressed_criticals=0))
        assert engine.is_done

        with pytest.raises(RuntimeError, match="terminal state"):
            engine.submit(IterationResult(iteration=2, unaddressed_criticals=0))

    def test_current_iteration_tracks(self):
        engine = ConvergenceEngine(max_iterations=5)
        assert engine.current_iteration == 0
        engine.submit(IterationResult(iteration=1, unaddressed_criticals=5))
        assert engine.current_iteration == 1
        engine.submit(IterationResult(iteration=2, unaddressed_criticals=0))
        assert engine.current_iteration == 2

    def test_initial_state_is_running(self):
        engine = ConvergenceEngine()
        assert engine.state == ConvergenceState.RUNNING
        assert not engine.is_done


class TestIterationResultScoring:

    def test_overall_score_is_mean(self):
        result = IterationResult(
            quality_scores={
                "clarity": 8.0,
                "completeness": 7.0,
                "testability": 9.0,
                "consistency": 6.0,
            }
        )
        # (8 + 7 + 9 + 6) / 4 = 7.5
        assert result.overall_score == pytest.approx(7.5, abs=0.01)

    def test_overall_score_empty(self):
        result = IterationResult()
        assert result.overall_score == 0.0

    def test_partial_scores(self):
        result = IterationResult(
            quality_scores={"clarity": 8.0, "completeness": 6.0}
        )
        # (8 + 6 + 0 + 0) / 4 = 3.5
        assert result.overall_score == pytest.approx(3.5, abs=0.01)


class TestSimpleBudgetGuard:

    def test_has_budget(self):
        g = SimpleBudgetGuard(total_budget=10.0, spent=3.0)
        assert g.has_budget(5.0)
        assert not g.has_budget(8.0)

    def test_remaining_budget(self):
        g = SimpleBudgetGuard(total_budget=10.0, spent=4.0)
        assert g.remaining_budget() == 6.0

    def test_record_spend(self):
        g = SimpleBudgetGuard(total_budget=10.0)
        g.record_spend(3.0)
        g.record_spend(2.0)
        assert g.spent == 5.0
        assert g.remaining_budget() == 5.0


class TestConvergenceResult:

    def test_converged_result(self):
        r = ConvergenceResult(
            state=ConvergenceState.CONVERGED,
            iterations_completed=2,
        )
        assert r.is_converged
        assert not r.is_escalated

    def test_escalated_result(self):
        r = ConvergenceResult(
            state=ConvergenceState.ESCALATED,
            escalation_reason=EscalationReason.MAX_ITERATIONS,
        )
        assert not r.is_converged
        assert r.is_escalated
