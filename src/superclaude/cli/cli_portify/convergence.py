"""Standalone convergence engine for cli-portify panel-review iterations.

Manages predicate checking, budget guards, and escalation as a
standalone component independent of Claude subprocess management.

State machine: RUNNING -> CONVERGED | ESCALATED

- Convergence predicate: zero unaddressed CRITICALs -> CONVERGED
- Max iterations: max_convergence (default 3)
- Budget guard: TurnLedger pre-launch check before each iteration
- Terminal states: CONVERGED (success), ESCALATED (partial, user escalation)

Per D-0030: Standalone, unit-testable convergence engine.
Per D-0046: TurnLedger pre-launch budget guard.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

_log = logging.getLogger("superclaude.cli_portify.convergence")


# --- Convergence States ---


class ConvergenceState(Enum):
    """Terminal and non-terminal convergence states."""

    RUNNING = "running"
    CONVERGED = "converged"
    ESCALATED = "escalated"

    @property
    def is_terminal(self) -> bool:
        return self in (ConvergenceState.CONVERGED, ConvergenceState.ESCALATED)


class EscalationReason(Enum):
    """Why the convergence engine escalated."""

    MAX_ITERATIONS = "max_iterations"
    BUDGET_EXHAUSTED = "budget_exhausted"
    USER_REJECTED = "user_rejected"


# --- Iteration Result Protocol ---


@dataclass
class IterationResult:
    """Result from a single panel-review iteration.

    Attributes:
        iteration: 1-based iteration number.
        unaddressed_criticals: Count of unaddressed CRITICAL findings.
        quality_scores: Dict of dimension scores (clarity, completeness, etc.).
        content: Raw output content from the iteration.
    """

    iteration: int = 0
    unaddressed_criticals: int = 0
    quality_scores: dict[str, float] = field(default_factory=dict)
    content: str = ""

    @property
    def overall_score(self) -> float:
        """Compute overall quality score as mean of 4 dimensions."""
        dimensions = ["clarity", "completeness", "testability", "consistency"]
        scores = [self.quality_scores.get(d, 0.0) for d in dimensions]
        if not any(scores):
            return 0.0
        return sum(scores) / len(dimensions)


# --- Budget Guard Protocol ---


class BudgetGuard(Protocol):
    """Protocol for pre-launch budget checking."""

    def has_budget(self, estimated_cost: float) -> bool:
        """Check if sufficient budget remains for the next iteration."""
        ...

    def remaining_budget(self) -> float:
        """Return the remaining budget."""
        ...


@dataclass
class SimpleBudgetGuard:
    """Simple budget guard with fixed total and per-iteration cost estimate.

    Attributes:
        total_budget: Total budget available.
        spent: Amount already spent.
        per_iteration_cost: Estimated cost per iteration.
    """

    total_budget: float = 100.0
    spent: float = 0.0
    per_iteration_cost: float = 10.0

    def has_budget(self, estimated_cost: float | None = None) -> bool:
        cost = estimated_cost if estimated_cost is not None else self.per_iteration_cost
        return (self.total_budget - self.spent) >= cost

    def remaining_budget(self) -> float:
        return self.total_budget - self.spent

    def record_spend(self, amount: float) -> None:
        self.spent += amount


# --- Convergence Engine ---


@dataclass
class ConvergenceResult:
    """Final result from the convergence engine.

    Attributes:
        state: Terminal convergence state.
        iterations_completed: Number of iterations executed.
        last_result: The final iteration result.
        escalation_reason: Why escalation occurred (if ESCALATED).
        quality_scores: Quality scores from the last iteration.
    """

    state: ConvergenceState = ConvergenceState.RUNNING
    iterations_completed: int = 0
    last_result: IterationResult | None = None
    escalation_reason: EscalationReason | None = None
    quality_scores: dict[str, float] = field(default_factory=dict)

    @property
    def overall_score(self) -> float:
        if self.last_result:
            return self.last_result.overall_score
        return 0.0

    @property
    def is_converged(self) -> bool:
        return self.state == ConvergenceState.CONVERGED

    @property
    def is_escalated(self) -> bool:
        return self.state == ConvergenceState.ESCALATED


class ConvergenceEngine:
    """Standalone convergence engine for panel-review iterations.

    Manages the iteration loop, convergence predicate checking,
    budget guards, and escalation. Independent of Claude subprocess
    management -- callers provide iteration results.

    Usage:
        engine = ConvergenceEngine(max_iterations=3)
        while not engine.is_done:
            # Run an iteration externally
            iter_result = run_panel_iteration(...)
            engine.submit(iter_result)
        result = engine.result()
    """

    def __init__(
        self,
        max_iterations: int = 3,
        budget_guard: BudgetGuard | None = None,
    ):
        self._max_iterations = max_iterations
        self._budget_guard = budget_guard
        self._iterations: list[IterationResult] = []
        self._state = ConvergenceState.RUNNING
        self._escalation_reason: EscalationReason | None = None

    @property
    def is_done(self) -> bool:
        return self._state.is_terminal

    @property
    def current_iteration(self) -> int:
        return len(self._iterations)

    @property
    def state(self) -> ConvergenceState:
        return self._state

    def check_budget(self, estimated_cost: float | None = None) -> bool:
        """Pre-launch budget guard: check before starting next iteration.

        Args:
            estimated_cost: Optional specific cost estimate.

        Returns:
            True if budget is available, False if exhausted.
        """
        if self._budget_guard is None:
            return True
        cost = estimated_cost if estimated_cost is not None else 0.0
        return self._budget_guard.has_budget(cost)

    def submit(self, iteration_result: IterationResult) -> ConvergenceState:
        """Submit an iteration result and advance the state machine.

        The convergence predicate checks:
        1. Zero unaddressed CRITICALs -> CONVERGED
        2. Max iterations reached -> ESCALATED
        3. Otherwise -> RUNNING (continue iterating)

        Args:
            iteration_result: Result from the latest iteration.

        Returns:
            The new convergence state.

        Raises:
            RuntimeError: If engine is already in a terminal state.
        """
        if self._state.is_terminal:
            raise RuntimeError(
                f"Cannot submit: convergence engine is in terminal state {self._state.value}"
            )

        self._iterations.append(iteration_result)
        iteration_num = len(self._iterations)

        _log.info(
            "convergence iteration=%d criticals=%d scores=%s",
            iteration_num,
            iteration_result.unaddressed_criticals,
            iteration_result.quality_scores,
        )

        # Convergence predicate: zero unaddressed CRITICALs
        if iteration_result.unaddressed_criticals == 0:
            self._state = ConvergenceState.CONVERGED
            _log.info("convergence CONVERGED after %d iterations", iteration_num)
            return self._state

        # Max iterations check
        if iteration_num >= self._max_iterations:
            self._state = ConvergenceState.ESCALATED
            self._escalation_reason = EscalationReason.MAX_ITERATIONS
            _log.warning(
                "convergence ESCALATED: max iterations (%d) reached with %d criticals remaining",
                self._max_iterations,
                iteration_result.unaddressed_criticals,
            )
            return self._state

        # Still running
        _log.info(
            "convergence RUNNING: iteration %d/%d, %d criticals remaining",
            iteration_num,
            self._max_iterations,
            iteration_result.unaddressed_criticals,
        )
        return self._state

    def escalate_budget(self) -> None:
        """Escalate due to budget exhaustion."""
        self._state = ConvergenceState.ESCALATED
        self._escalation_reason = EscalationReason.BUDGET_EXHAUSTED
        _log.warning("convergence ESCALATED: budget exhausted")

    def escalate_user(self) -> None:
        """Escalate due to user rejection."""
        self._state = ConvergenceState.ESCALATED
        self._escalation_reason = EscalationReason.USER_REJECTED
        _log.warning("convergence ESCALATED: user rejected")

    def result(self) -> ConvergenceResult:
        """Build the final convergence result.

        Can be called at any time, but the state may be non-terminal
        if called before convergence or escalation.
        """
        last = self._iterations[-1] if self._iterations else None
        return ConvergenceResult(
            state=self._state,
            iterations_completed=len(self._iterations),
            last_result=last,
            escalation_reason=self._escalation_reason,
            quality_scores=last.quality_scores if last else {},
        )
