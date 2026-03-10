"""T09.03 — Property-based tests for TurnLedger, GateResultQueue, and DeferredRemediationLog.

Uses hypothesis to validate system invariants across randomized inputs:
1. Budget monotonicity: TurnLedger.consumed never decreases
2. Gate result ordering: GateResultQueue results arrive in submission order per step_id
3. Remediation idempotency: double mark_remediated produces identical state

Acceptance criteria (D-0040):
- Budget monotonicity property holds across >=100 randomized operation sequences
- Gate result ordering property holds across >=100 randomized concurrent submission scenarios
- Remediation idempotency property holds: double mark_remediated produces identical state
- `uv run pytest tests/ -k property_based` exits 0
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from superclaude.cli.pipeline.trailing_gate import (
    DeferredRemediationLog,
    GateResultQueue,
    RemediationStatus,
    TrailingGateResult,
)
from superclaude.cli.sprint.models import TurnLedger


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------


# Non-negative integers for budget operations
budget_amount = st.integers(min_value=0, max_value=1000)
positive_budget = st.integers(min_value=1, max_value=10000)


# Debit/credit operation sequences
@st.composite
def budget_operation_sequence(draw):
    """Generate a random sequence of (op_type, amount) tuples."""
    ops = draw(st.lists(
        st.tuples(
            st.sampled_from(["debit", "credit"]),
            budget_amount,
        ),
        min_size=1,
        max_size=200,
    ))
    return ops


# Gate results with varying step_ids
@st.composite
def gate_result_batch(draw):
    """Generate a batch of TrailingGateResult with sequential step_ids."""
    count = draw(st.integers(min_value=1, max_value=50))
    results = []
    for i in range(count):
        results.append(TrailingGateResult(
            step_id=f"step-{i}",
            passed=draw(st.booleans()),
            evaluation_ms=draw(st.floats(min_value=0.0, max_value=1000.0)),
            failure_reason="fail" if not results or draw(st.booleans()) else None,
        ))
    return results


# ===========================================================================
# Property 1: TurnLedger Budget Monotonicity
# ===========================================================================


class TestPropertyBudgetMonotonicity:
    """TurnLedger.consumed never decreases regardless of operation sequence."""

    @pytest.mark.property_based
    @given(initial=positive_budget, ops=budget_operation_sequence())
    @settings(max_examples=200, deadline=None)
    def test_consumed_never_decreases(self, initial, ops):
        """Property: for any sequence of debit/credit operations,
        TurnLedger.consumed is monotonically non-decreasing."""
        ledger = TurnLedger(initial_budget=initial)
        prev_consumed = 0

        for op_type, amount in ops:
            if op_type == "debit":
                ledger.debit(amount)
            else:
                ledger.credit(amount)

            # INVARIANT: consumed never decreases
            assert ledger.consumed >= prev_consumed, (
                f"Monotonicity violated: consumed went from "
                f"{prev_consumed} to {ledger.consumed} after {op_type}({amount})"
            )
            prev_consumed = ledger.consumed

    @pytest.mark.property_based
    @given(initial=positive_budget, ops=budget_operation_sequence())
    @settings(max_examples=200, deadline=None)
    def test_accounting_identity_holds(self, initial, ops):
        """Property: available() == initial_budget - consumed + reimbursed
        after any sequence of operations."""
        ledger = TurnLedger(initial_budget=initial)

        for op_type, amount in ops:
            if op_type == "debit":
                ledger.debit(amount)
            else:
                ledger.credit(amount)

        # INVARIANT: accounting identity
        assert ledger.available() == ledger.initial_budget - ledger.consumed + ledger.reimbursed

    @pytest.mark.property_based
    @given(initial=positive_budget, debits=st.lists(budget_amount, min_size=1, max_size=100))
    @settings(max_examples=200, deadline=None)
    def test_consumed_equals_sum_of_debits(self, initial, debits):
        """Property: consumed == sum of all debit amounts."""
        ledger = TurnLedger(initial_budget=initial)

        for amount in debits:
            ledger.debit(amount)

        assert ledger.consumed == sum(debits)

    @pytest.mark.property_based
    @given(initial=positive_budget, credits=st.lists(budget_amount, min_size=1, max_size=100))
    @settings(max_examples=200, deadline=None)
    def test_reimbursed_equals_sum_of_credits(self, initial, credits):
        """Property: reimbursed == sum of all credit amounts."""
        ledger = TurnLedger(initial_budget=initial)

        for amount in credits:
            ledger.credit(amount)

        assert ledger.reimbursed == sum(credits)

    @pytest.mark.property_based
    @given(amount=st.integers(min_value=-1000, max_value=-1))
    @settings(max_examples=50, deadline=None)
    def test_negative_debit_raises(self, amount):
        """Property: negative debit amounts always raise ValueError."""
        ledger = TurnLedger(initial_budget=100)
        with pytest.raises(ValueError):
            ledger.debit(amount)

    @pytest.mark.property_based
    @given(amount=st.integers(min_value=-1000, max_value=-1))
    @settings(max_examples=50, deadline=None)
    def test_negative_credit_raises(self, amount):
        """Property: negative credit amounts always raise ValueError."""
        ledger = TurnLedger(initial_budget=100)
        with pytest.raises(ValueError):
            ledger.credit(amount)


# ===========================================================================
# Property 2: GateResultQueue Ordering
# ===========================================================================


class TestPropertyGateResultOrdering:
    """GateResultQueue results arrive in submission order per step_id."""

    @pytest.mark.property_based
    @given(batch=gate_result_batch())
    @settings(max_examples=200, deadline=None)
    def test_drain_returns_all_submitted(self, batch):
        """Property: drain() returns exactly the results that were put()."""
        queue = GateResultQueue()

        for result in batch:
            queue.put(result)

        drained = queue.drain()
        assert len(drained) == len(batch)

        # All step_ids present
        submitted_ids = [r.step_id for r in batch]
        drained_ids = [r.step_id for r in drained]
        assert submitted_ids == drained_ids

    @pytest.mark.property_based
    @given(batch=gate_result_batch())
    @settings(max_examples=200, deadline=None)
    def test_fifo_ordering_preserved(self, batch):
        """Property: results are drained in FIFO order (submission order)."""
        queue = GateResultQueue()

        for result in batch:
            queue.put(result)

        drained = queue.drain()

        # FIFO: order preserved
        for i, (submitted, received) in enumerate(zip(batch, drained)):
            assert submitted.step_id == received.step_id, (
                f"Order violated at position {i}: expected {submitted.step_id}, "
                f"got {received.step_id}"
            )
            assert submitted.passed == received.passed

    @pytest.mark.property_based
    @settings(max_examples=100, deadline=None)
    @given(count=st.integers(min_value=2, max_value=20))
    def test_concurrent_put_no_loss(self, count):
        """Property: concurrent put() from multiple threads loses no results."""
        queue = GateResultQueue()
        barrier = threading.Barrier(count)

        def _producer(idx):
            barrier.wait()
            queue.put(TrailingGateResult(
                step_id=f"step-{idx}",
                passed=True,
                evaluation_ms=1.0,
            ))

        threads = [threading.Thread(target=_producer, args=(i,)) for i in range(count)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        drained = queue.drain()
        assert len(drained) == count

    @pytest.mark.property_based
    @settings(max_examples=100, deadline=None)
    @given(count=st.integers(min_value=1, max_value=30))
    def test_drain_then_empty(self, count):
        """Property: after drain(), queue is empty (second drain returns [])."""
        queue = GateResultQueue()

        for i in range(count):
            queue.put(TrailingGateResult(
                step_id=f"step-{i}", passed=True, evaluation_ms=1.0,
            ))

        first = queue.drain()
        assert len(first) == count

        second = queue.drain()
        assert len(second) == 0


# ===========================================================================
# Property 3: Remediation Idempotency
# ===========================================================================


class TestPropertyRemediationIdempotency:
    """DeferredRemediationLog.mark_remediated is idempotent."""

    @pytest.mark.property_based
    @given(step_ids=st.lists(
        st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=("L", "N"),
        )),
        min_size=1,
        max_size=30,
        unique=True,
    ))
    @settings(max_examples=200, deadline=None)
    def test_double_mark_remediated_idempotent(self, step_ids):
        """Property: marking the same entry remediated twice produces
        identical state (second call is a no-op returning False)."""
        log = DeferredRemediationLog()

        # Populate with failed gate results
        for sid in step_ids:
            log.append(TrailingGateResult(
                step_id=sid, passed=False,
                evaluation_ms=1.0, failure_reason="test failure",
            ))

        # Pick a random entry to remediate
        target = step_ids[0]

        # First mark: should succeed
        result_1 = log.mark_remediated(target)
        assert result_1 is True

        # Capture state after first mark
        pending_after_first = [e.step_id for e in log.pending_remediations()]

        # Second mark: same step_id — should return False (already remediated)
        result_2 = log.mark_remediated(target)
        assert result_2 is False

        # State unchanged: pending list is identical
        pending_after_second = [e.step_id for e in log.pending_remediations()]
        assert pending_after_first == pending_after_second

    @pytest.mark.property_based
    @given(step_ids=st.lists(
        st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=("L", "N"),
        )),
        min_size=2,
        max_size=20,
        unique=True,
    ))
    @settings(max_examples=200, deadline=None)
    def test_remediate_preserves_other_entries(self, step_ids):
        """Property: remediating one entry does not affect other entries."""
        log = DeferredRemediationLog()

        for sid in step_ids:
            log.append(TrailingGateResult(
                step_id=sid, passed=False,
                evaluation_ms=1.0, failure_reason="test failure",
            ))

        # Remediate first entry
        log.mark_remediated(step_ids[0])

        # All other entries remain pending
        pending = {e.step_id for e in log.pending_remediations()}
        expected_pending = set(step_ids[1:])
        assert pending == expected_pending

    @pytest.mark.property_based
    @given(step_ids=st.lists(
        st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=("L", "N"),
        )),
        min_size=1,
        max_size=20,
        unique=True,
    ))
    @settings(max_examples=200, deadline=None)
    def test_serialize_deserialize_roundtrip(self, step_ids):
        """Property: serialize → deserialize produces identical state."""
        log = DeferredRemediationLog()

        for sid in step_ids:
            log.append(TrailingGateResult(
                step_id=sid, passed=False,
                evaluation_ms=1.0, failure_reason=f"fail-{sid}",
            ))

        # Remediate some
        for sid in step_ids[:len(step_ids) // 2]:
            log.mark_remediated(sid)

        # Round-trip
        json_str = log.serialize()
        restored = DeferredRemediationLog.deserialize(json_str)

        # Same entry count
        assert restored.entry_count == log.entry_count

        # Same pending set
        original_pending = {e.step_id for e in log.pending_remediations()}
        restored_pending = {e.step_id for e in restored.pending_remediations()}
        assert original_pending == restored_pending

    @pytest.mark.property_based
    @settings(max_examples=100, deadline=None)
    @given(nonexistent_id=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=("L", "N"),
    )))
    def test_mark_nonexistent_returns_false(self, nonexistent_id):
        """Property: marking a non-existent step_id returns False."""
        log = DeferredRemediationLog()
        log.append(TrailingGateResult(
            step_id="existing", passed=False,
            evaluation_ms=1.0, failure_reason="fail",
        ))

        assume(nonexistent_id != "existing")
        assert log.mark_remediated(nonexistent_id) is False
