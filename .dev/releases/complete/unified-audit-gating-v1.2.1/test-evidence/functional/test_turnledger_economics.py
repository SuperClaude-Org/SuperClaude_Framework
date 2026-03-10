"""Functional test: TurnLedger economic invariants.

Exercises the TurnLedger dataclass from src/superclaude/cli/sprint/models.py
to verify budget decay under repeated debit+credit cycles and the pre-launch
guard behaviour when budget is exhausted.

Run with:
    uv run pytest test_turnledger_economics.py -v
"""

from __future__ import annotations

import math

import pytest

from superclaude.cli.sprint.models import TurnLedger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def simulate_cycle(ledger: TurnLedger, spend: int) -> int:
    """Simulate one debit+credit cycle and return the new available budget.

    The caller (sprint runner) is responsible for computing the reimbursement
    amount.  credit() stores the raw value -- it does NOT multiply by
    reimbursement_rate internally.  We replicate the intended caller
    convention: reimburse = floor(spend * reimbursement_rate).
    """
    ledger.debit(spend)
    reimburse = math.floor(spend * ledger.reimbursement_rate)
    ledger.credit(reimburse)
    return ledger.available()


# ---------------------------------------------------------------------------
# Core economic invariant: budget decays under repeated cycles
# ---------------------------------------------------------------------------

class TestBudgetDecay:
    """After N debit+credit cycles at rate < 1.0, budget must decay."""

    @pytest.mark.parametrize("rate", [0.5, 0.9])
    def test_monotonic_decay_over_cycles(self, rate: float) -> None:
        """available() must be strictly non-increasing across cycles.

        Each cycle debits a fixed amount and credits floor(amount * rate).
        Because rate < 1.0, the net loss per cycle is positive, so available()
        must decrease (or at worst stay equal when floor rounds to zero).
        """
        budget = 100
        spend_per_cycle = 10
        ledger = TurnLedger(
            initial_budget=budget,
            reimbursement_rate=rate,
        )

        previous = ledger.available()
        assert previous == budget, "Initial available must equal initial_budget"

        cycles = 0
        while ledger.available() >= spend_per_cycle:
            new_available = simulate_cycle(ledger, spend_per_cycle)
            assert new_available <= previous, (
                f"Budget increased from {previous} to {new_available} "
                f"at cycle {cycles + 1} -- monotonicity violated"
            )
            previous = new_available
            cycles += 1

        # At rate=0.5 each cycle loses 5 net turns, so ~20 cycles to exhaust.
        # At rate=0.9 each cycle loses 1 net turn, so ~90 cycles.
        assert cycles > 0, "Must complete at least one cycle"
        assert ledger.available() < spend_per_cycle, (
            "Budget must eventually drop below the per-cycle spend"
        )

    def test_budget_reaches_zero_with_default_rate(self) -> None:
        """With default rate (0.5), budget must reach zero eventually."""
        ledger = TurnLedger(initial_budget=50)
        assert ledger.reimbursement_rate == 0.5, "Default rate must be 0.5"

        cycles = 0
        max_cycles = 200  # safety bound
        while ledger.available() > 0 and cycles < max_cycles:
            spend = min(1, ledger.available())
            simulate_cycle(ledger, spend)
            cycles += 1

        assert ledger.available() <= 0, (
            f"Budget must reach zero; got {ledger.available()} after {cycles} cycles"
        )

    def test_net_loss_per_cycle(self) -> None:
        """Each cycle loses exactly (spend - floor(spend * rate)) turns."""
        ledger = TurnLedger(initial_budget=100, reimbursement_rate=0.9)
        spend = 10
        expected_loss = spend - math.floor(spend * 0.9)  # 10 - 9 = 1

        before = ledger.available()
        simulate_cycle(ledger, spend)
        actual_loss = before - ledger.available()

        assert actual_loss == expected_loss, (
            f"Expected net loss {expected_loss}, got {actual_loss}"
        )


# ---------------------------------------------------------------------------
# Pre-launch guard: HALT when budget is exhausted
# ---------------------------------------------------------------------------

class TestPreLaunchGuard:
    """can_launch() and can_remediate() must deny when budget is too low."""

    def test_can_launch_with_sufficient_budget(self) -> None:
        ledger = TurnLedger(initial_budget=20, minimum_allocation=5)
        assert ledger.can_launch() is True

    def test_cannot_launch_below_minimum_allocation(self) -> None:
        ledger = TurnLedger(initial_budget=20, minimum_allocation=5)
        # Consume until available < minimum_allocation
        ledger.debit(16)  # available = 4
        assert ledger.available() == 4
        assert ledger.can_launch() is False, (
            "can_launch() must return False when available < minimum_allocation"
        )

    def test_cannot_launch_at_zero(self) -> None:
        ledger = TurnLedger(initial_budget=10, minimum_allocation=5)
        ledger.debit(10)
        assert ledger.available() == 0
        assert ledger.can_launch() is False

    def test_can_launch_at_exact_threshold(self) -> None:
        """Boundary: available == minimum_allocation should permit launch."""
        ledger = TurnLedger(initial_budget=10, minimum_allocation=5)
        ledger.debit(5)  # available = 5, exactly at threshold
        assert ledger.available() == 5
        assert ledger.can_launch() is True

    def test_can_remediate_with_sufficient_budget(self) -> None:
        ledger = TurnLedger(
            initial_budget=10,
            minimum_remediation_budget=3,
        )
        assert ledger.can_remediate() is True

    def test_cannot_remediate_below_threshold(self) -> None:
        ledger = TurnLedger(
            initial_budget=10,
            minimum_remediation_budget=3,
        )
        ledger.debit(8)  # available = 2
        assert ledger.available() == 2
        assert ledger.can_remediate() is False

    def test_guard_halts_after_economic_decay(self) -> None:
        """Simulate repeated cycles until the guard triggers HALT.

        This is the integration scenario: keep running debit+credit cycles
        until can_launch() returns False, proving that economic decay
        eventually forces a halt.
        """
        ledger = TurnLedger(
            initial_budget=50,
            reimbursement_rate=0.5,
            minimum_allocation=5,
        )

        cycles = 0
        max_cycles = 200
        while ledger.can_launch() and cycles < max_cycles:
            simulate_cycle(ledger, 5)
            cycles += 1

        assert ledger.can_launch() is False, (
            "Guard must eventually deny launch after budget decay"
        )
        assert ledger.available() < ledger.minimum_allocation
        assert cycles < max_cycles, "Should not hit safety bound"


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

class TestInputValidation:
    """Negative amounts must raise ValueError."""

    def test_negative_debit_raises(self) -> None:
        ledger = TurnLedger(initial_budget=10)
        with pytest.raises(ValueError, match="non-negative"):
            ledger.debit(-1)

    def test_negative_credit_raises(self) -> None:
        ledger = TurnLedger(initial_budget=10)
        with pytest.raises(ValueError, match="non-negative"):
            ledger.credit(-1)


# ---------------------------------------------------------------------------
# Accounting identity
# ---------------------------------------------------------------------------

class TestAccountingIdentity:
    """available() must always equal initial_budget - consumed + reimbursed."""

    def test_identity_holds_after_mixed_operations(self) -> None:
        ledger = TurnLedger(initial_budget=100, reimbursement_rate=0.9)

        operations = [
            ("debit", 10),
            ("debit", 15),
            ("credit", 9),   # reimburse for first debit
            ("debit", 20),
            ("credit", 13),  # reimburse for second debit (floor(15*0.9)=13)
            ("credit", 18),  # reimburse for third debit (floor(20*0.9)=18)
        ]

        for op, amount in operations:
            getattr(ledger, op)(amount)
            assert ledger.available() == (
                ledger.initial_budget - ledger.consumed + ledger.reimbursed
            ), f"Accounting identity violated after {op}({amount})"
