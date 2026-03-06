"""Tests for token budget accounting, enforcement, degradation, and override.

Covers T04.06 (D-0032), T04.07 (D-0033), T04.08 (D-0034).
"""

import pytest

from superclaude.cli.audit.budget import (
    CAPABILITY_NAMES,
    DEFAULT_DEGRADATION_ORDER,
    BudgetAccountant,
    BudgetConfig,
    DegradationHandler,
    DegradationLevel,
    EnforcementAction,
)


# ── T04.06: Budget Accounting ────────────────────────────────────────


class TestBudgetConfig:
    """Verify budget configuration validation."""

    def test_valid_config(self):
        cfg = BudgetConfig(total_budget=10000)
        assert cfg.validate() == []

    def test_invalid_zero_budget(self):
        cfg = BudgetConfig(total_budget=0)
        assert len(cfg.validate()) > 0

    def test_invalid_threshold_order(self):
        cfg = BudgetConfig(total_budget=10000, warn_threshold=0.95, degrade_threshold=0.80)
        assert len(cfg.validate()) > 0


class TestBudgetAccountant:
    """Verify per-phase token tracking and enforcement."""

    def test_per_phase_tracking(self):
        """Token consumption is tracked per phase."""
        acc = BudgetAccountant(BudgetConfig(total_budget=10000))
        acc.register_phase("surface", limit=5000)
        acc.record("surface", 1000)
        acc.record("surface", 500)
        status = acc.status()
        assert status.phases["surface"].tokens_used == 1500

    def test_utilization_computed(self):
        """Utilization is correctly computed."""
        acc = BudgetAccountant(BudgetConfig(total_budget=10000))
        acc.record("phase1", 7500)
        assert abs(acc.utilization - 0.75) < 0.001

    def test_remaining_computed(self):
        """Remaining tokens are correctly computed."""
        acc = BudgetAccountant(BudgetConfig(total_budget=10000))
        acc.record("phase1", 3000)
        assert acc.remaining == 7000

    def test_warn_at_75_percent(self):
        """Warning triggered at 75% utilization."""
        acc = BudgetAccountant(BudgetConfig(total_budget=10000))
        action = acc.record("phase1", 7500)
        assert action == EnforcementAction.WARN

    def test_degrade_at_90_percent(self):
        """Degradation triggered at 90% utilization."""
        acc = BudgetAccountant(BudgetConfig(total_budget=10000))
        acc.record("phase1", 5000)
        action = acc.record("phase1", 4000)
        assert action == EnforcementAction.DEGRADE

    def test_halt_at_100_percent(self):
        """Halt triggered at 100% utilization."""
        acc = BudgetAccountant(BudgetConfig(total_budget=10000))
        action = acc.record("phase1", 10000)
        assert action == EnforcementAction.HALT

    def test_none_below_75(self):
        """No enforcement below 75%."""
        acc = BudgetAccountant(BudgetConfig(total_budget=10000))
        action = acc.record("phase1", 5000)
        assert action == EnforcementAction.NONE

    def test_status_serialization(self):
        """Budget status serializes to dict for progress.json."""
        acc = BudgetAccountant(BudgetConfig(total_budget=10000))
        acc.record("phase1", 3000)
        d = acc.status().to_dict()
        assert "total_budget" in d
        assert "total_consumed" in d
        assert "utilization" in d
        assert d["phases"]["phase1"]["tokens_used"] == 3000

    def test_auto_register_phase(self):
        """Phases are auto-registered on first record."""
        acc = BudgetAccountant(BudgetConfig(total_budget=10000))
        acc.record("unregistered", 100)
        assert "unregistered" in acc.status().phases

    def test_budget_accuracy_within_5_percent(self):
        """Budget accounting is exact (within implementation)."""
        acc = BudgetAccountant(BudgetConfig(total_budget=10000))
        for i in range(100):
            acc.record("phase1", 100)
        assert acc.status().total_consumed == 10000


# ── T04.07: Degradation Sequence ─────────────────────────────────────


class TestDegradationHandler:
    """Verify ordered degradation sequence."""

    def test_default_order(self):
        """Degradation activates in L1-L5 order."""
        handler = DegradationHandler()
        activated = []
        for _ in range(5):
            level = handler.activate_next(0.9)
            assert level is not None
            activated.append(level)
        assert activated == list(DEFAULT_DEGRADATION_ORDER)

    def test_activation_logged(self):
        """Degradation log records activations."""
        handler = DegradationHandler()
        handler.activate_next(0.91)
        handler.activate_next(0.93)
        assert len(handler.log) == 2
        assert handler.log[0].level == DegradationLevel.L1_SKIP_DUPLICATION
        assert handler.log[1].level == DegradationLevel.L2_REDUCE_VALIDATION

    def test_is_active(self):
        """is_active reflects activated levels."""
        handler = DegradationHandler()
        handler.activate_next(0.9)
        assert handler.is_active(DegradationLevel.L1_SKIP_DUPLICATION)
        assert not handler.is_active(DegradationLevel.L2_REDUCE_VALIDATION)

    def test_should_skip(self):
        """should_skip reflects capability degradation state."""
        handler = DegradationHandler()
        handler.activate_next(0.9)
        assert handler.should_skip("duplication_matrix")
        assert not handler.should_skip("validation_sample")

    def test_validation_sample_reduced(self):
        """Validation sample fraction reduces from 10% to 5% at L2."""
        handler = DegradationHandler()
        assert handler.get_validation_sample_fraction() == 0.10
        handler.activate_next(0.9)  # L1
        handler.activate_next(0.92)  # L2
        assert handler.get_validation_sample_fraction() == 0.05

    def test_profile_fields_reduced(self):
        """Profile fields reduce from 8 to 4 at L4."""
        handler = DegradationHandler()
        assert len(handler.get_profile_fields()) == 8
        for _ in range(4):  # Activate L1-L4
            handler.activate_next(0.9)
        assert len(handler.get_profile_fields()) == 4

    def test_no_more_levels(self):
        """Returns None when all levels exhausted."""
        handler = DegradationHandler()
        for _ in range(5):
            handler.activate_next(0.9)
        assert handler.activate_next(0.99) is None

    def test_activate_up_to(self):
        """activate_up_to activates all levels up to target."""
        handler = DegradationHandler()
        activated = handler.activate_up_to(DegradationLevel.L3_SKIP_TIER_C)
        assert len(activated) == 3
        assert handler.is_active(DegradationLevel.L1_SKIP_DUPLICATION)
        assert handler.is_active(DegradationLevel.L3_SKIP_TIER_C)
        assert not handler.is_active(DegradationLevel.L4_REDUCE_PROFILE)


# ── T04.08: Degrade-Priority Override ─────────────────────────────────


class TestDegradePriorityOverride:
    """Verify protected capability override."""

    def test_protected_capability_preserved(self):
        """Protected capability is not degraded even under budget pressure."""
        handler = DegradationHandler(protected={"duplication_matrix"})
        # Activate all available levels
        for _ in range(5):
            handler.activate_next(0.95)
        # duplication_matrix should NOT be active
        assert not handler.is_active(DegradationLevel.L1_SKIP_DUPLICATION)
        assert not handler.should_skip("duplication_matrix")

    def test_non_protected_degrade_in_adjusted_order(self):
        """Non-protected capabilities degrade when protected items are skipped."""
        handler = DegradationHandler(protected={"duplication_matrix"})
        level = handler.activate_next(0.9)
        # First activation should be L2 (skipping L1 which is protected)
        assert level == DegradationLevel.L2_REDUCE_VALIDATION

    def test_invalid_capability_rejected(self):
        """Invalid capability names are rejected at startup."""
        with pytest.raises(ValueError, match="Invalid capability names"):
            DegradationHandler(protected={"nonexistent_capability"})

    def test_protected_set_accessor(self):
        """Protected capabilities are accessible."""
        handler = DegradationHandler(protected={"duplication_matrix", "tier_c_edges"})
        assert "duplication_matrix" in handler.protected_capabilities
        assert "tier_c_edges" in handler.protected_capabilities

    def test_is_protected(self):
        """is_protected reports correct status."""
        handler = DegradationHandler(protected={"duplication_matrix"})
        assert handler.is_protected(DegradationLevel.L1_SKIP_DUPLICATION)
        assert not handler.is_protected(DegradationLevel.L2_REDUCE_VALIDATION)

    def test_protect_then_degrade(self):
        """Protected duplication, validation reduced instead."""
        handler = DegradationHandler(protected={"duplication_matrix"})
        handler.activate_next(0.9)
        assert not handler.should_skip("duplication_matrix")
        assert handler.should_skip("validation_sample")


# ── Integration: Budget + Degradation ─────────────────────────────────


class TestBudgetDegradationIntegration:
    """Verify budget accountant triggers degradation handler."""

    def test_degrade_triggers_handler(self):
        """Budget degrade threshold triggers degradation handler."""
        config = BudgetConfig(total_budget=10000)
        acc = BudgetAccountant(config)
        handler = DegradationHandler()
        acc.set_degradation_handler(handler)

        acc.record("phase1", 9000)  # 90% -> DEGRADE
        assert len(handler.active_levels) == 1
        assert handler.is_active(DegradationLevel.L1_SKIP_DUPLICATION)

    def test_status_includes_degradation(self):
        """Budget status includes degradation info."""
        config = BudgetConfig(total_budget=10000)
        acc = BudgetAccountant(config)
        handler = DegradationHandler()
        acc.set_degradation_handler(handler)

        acc.record("phase1", 9500)
        status = acc.status()
        d = status.to_dict()
        assert len(d["active_degradation_levels"]) > 0
        assert len(d["degradation_log"]) > 0
