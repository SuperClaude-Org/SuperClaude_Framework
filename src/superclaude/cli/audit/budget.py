"""Token budget accounting, enforcement, degradation, and override.

Implements:
  T04.06 / D-0032 / AC9: per-phase budget tracking with threshold enforcement
  T04.07 / D-0033 / AC9: deterministic degradation sequence
  T04.08 / D-0034 / AC9: degrade-priority override for protected capabilities

Budget schema: total_budget, per_phase_limits, current_consumption, remaining.
Enforcement thresholds: 75% = WARN, 90% = DEGRADE, 100% = HALT.

Degradation levels (activated in order):
  L1: Skip duplication matrix
  L2: Reduce validation sample to 5%
  L3: Skip Tier-C graph edges
  L4: Reduce profile to 4 core fields
  L5: Emit minimum viable report
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EnforcementAction(Enum):
    """Actions triggered at budget thresholds."""

    NONE = "none"
    WARN = "warn"
    DEGRADE = "degrade"
    HALT = "halt"


class DegradationLevel(Enum):
    """Ordered degradation levels."""

    L1_SKIP_DUPLICATION = "L1_skip_duplication_matrix"
    L2_REDUCE_VALIDATION = "L2_reduce_validation_sample"
    L3_SKIP_TIER_C = "L3_skip_tier_c_edges"
    L4_REDUCE_PROFILE = "L4_reduce_profile_fields"
    L5_MINIMUM_REPORT = "L5_minimum_viable_report"


# Default order for degradation
DEFAULT_DEGRADATION_ORDER: list[DegradationLevel] = [
    DegradationLevel.L1_SKIP_DUPLICATION,
    DegradationLevel.L2_REDUCE_VALIDATION,
    DegradationLevel.L3_SKIP_TIER_C,
    DegradationLevel.L4_REDUCE_PROFILE,
    DegradationLevel.L5_MINIMUM_REPORT,
]

# Capability names for override config
CAPABILITY_NAMES: dict[DegradationLevel, str] = {
    DegradationLevel.L1_SKIP_DUPLICATION: "duplication_matrix",
    DegradationLevel.L2_REDUCE_VALIDATION: "validation_sample",
    DegradationLevel.L3_SKIP_TIER_C: "tier_c_edges",
    DegradationLevel.L4_REDUCE_PROFILE: "full_profile",
    DegradationLevel.L5_MINIMUM_REPORT: "detailed_report",
}

# Reverse mapping
_NAME_TO_LEVEL: dict[str, DegradationLevel] = {
    v: k for k, v in CAPABILITY_NAMES.items()
}


@dataclass
class BudgetConfig:
    """Budget configuration with per-phase limits and thresholds."""

    total_budget: int
    per_phase_limits: dict[str, int] = field(default_factory=dict)
    warn_threshold: float = 0.75
    degrade_threshold: float = 0.90
    halt_threshold: float = 1.00

    def validate(self) -> list[str]:
        """Validate config. Returns list of error messages (empty = valid)."""
        errors = []
        if self.total_budget <= 0:
            errors.append("total_budget must be positive")
        if not (0 < self.warn_threshold < self.degrade_threshold < self.halt_threshold <= 1.0):
            errors.append("thresholds must be ordered: warn < degrade < halt <= 1.0")
        return errors


@dataclass
class PhaseConsumption:
    """Token consumption for a single phase."""

    phase: str
    tokens_used: int = 0
    limit: int = 0

    @property
    def utilization(self) -> float:
        return self.tokens_used / self.limit if self.limit > 0 else 0.0


@dataclass
class DegradationEvent:
    """Records activation of a degradation level."""

    level: DegradationLevel
    triggered_at_utilization: float
    capability_skipped: str


@dataclass
class BudgetStatus:
    """Current budget status snapshot."""

    total_budget: int
    total_consumed: int
    remaining: int
    utilization: float
    enforcement: EnforcementAction
    phases: dict[str, PhaseConsumption]
    active_degradation_levels: list[DegradationLevel]
    degradation_log: list[DegradationEvent]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_budget": self.total_budget,
            "total_consumed": self.total_consumed,
            "remaining": self.remaining,
            "utilization": round(self.utilization, 4),
            "enforcement": self.enforcement.value,
            "phases": {
                k: {
                    "tokens_used": v.tokens_used,
                    "limit": v.limit,
                    "utilization": round(v.utilization, 4),
                }
                for k, v in self.phases.items()
            },
            "active_degradation_levels": [l.value for l in self.active_degradation_levels],
            "degradation_log": [
                {
                    "level": e.level.value,
                    "triggered_at": round(e.triggered_at_utilization, 4),
                    "capability_skipped": e.capability_skipped,
                }
                for e in self.degradation_log
            ],
        }


class BudgetAccountant:
    """Tracks token consumption per phase and enforces budget limits.

    Integrates with degradation handler for progressive capability reduction.
    """

    def __init__(self, config: BudgetConfig) -> None:
        errors = config.validate()
        if errors:
            raise ValueError(f"Invalid budget config: {'; '.join(errors)}")

        self._config = config
        self._phases: dict[str, PhaseConsumption] = {}
        self._total_consumed = 0
        self._degradation_handler: DegradationHandler | None = None

    def set_degradation_handler(self, handler: DegradationHandler) -> None:
        self._degradation_handler = handler

    def register_phase(self, phase: str, limit: int | None = None) -> None:
        """Register a phase with optional per-phase limit."""
        phase_limit = limit or self._config.per_phase_limits.get(phase, 0)
        self._phases[phase] = PhaseConsumption(phase=phase, limit=phase_limit)

    def record(self, phase: str, tokens: int) -> EnforcementAction:
        """Record token consumption for a phase.

        Returns the enforcement action triggered (if any).
        """
        if phase not in self._phases:
            self.register_phase(phase)

        self._phases[phase].tokens_used += tokens
        self._total_consumed += tokens

        action = self._evaluate_enforcement()

        if action == EnforcementAction.DEGRADE and self._degradation_handler:
            self._degradation_handler.activate_next(self.utilization)

        return action

    @property
    def utilization(self) -> float:
        if self._config.total_budget <= 0:
            return 0.0
        return self._total_consumed / self._config.total_budget

    @property
    def remaining(self) -> int:
        return max(0, self._config.total_budget - self._total_consumed)

    def _evaluate_enforcement(self) -> EnforcementAction:
        util = self.utilization
        if util >= self._config.halt_threshold:
            return EnforcementAction.HALT
        elif util >= self._config.degrade_threshold:
            return EnforcementAction.DEGRADE
        elif util >= self._config.warn_threshold:
            return EnforcementAction.WARN
        return EnforcementAction.NONE

    def status(self) -> BudgetStatus:
        """Get current budget status snapshot."""
        handler = self._degradation_handler
        return BudgetStatus(
            total_budget=self._config.total_budget,
            total_consumed=self._total_consumed,
            remaining=self.remaining,
            utilization=self.utilization,
            enforcement=self._evaluate_enforcement(),
            phases=dict(self._phases),
            active_degradation_levels=(
                handler.active_levels if handler else []
            ),
            degradation_log=(
                handler.log if handler else []
            ),
        )


class DegradationHandler:
    """Manages progressive degradation sequence.

    Activates degradation levels in order as budget pressure increases.
    Supports override to protect specific capabilities from degradation.
    """

    def __init__(
        self,
        order: list[DegradationLevel] | None = None,
        protected: set[str] | None = None,
    ) -> None:
        """Initialize degradation handler.

        Args:
            order: Degradation order (default: L1-L5).
            protected: Set of capability names to protect from degradation.

        Raises:
            ValueError: If protected capability names are invalid.
        """
        base_order = order or list(DEFAULT_DEGRADATION_ORDER)
        protected_set = protected or set()

        # Validate protected capability names
        valid_names = set(CAPABILITY_NAMES.values())
        invalid = protected_set - valid_names
        if invalid:
            raise ValueError(
                f"Invalid capability names for protection: {invalid}. "
                f"Valid names: {valid_names}"
            )

        # Build effective order: skip protected items
        self._effective_order: list[DegradationLevel] = []
        self._protected_levels: set[DegradationLevel] = set()

        for level in base_order:
            cap_name = CAPABILITY_NAMES[level]
            if cap_name in protected_set:
                self._protected_levels.add(level)
            else:
                self._effective_order.append(level)

        self._active: list[DegradationLevel] = []
        self._log: list[DegradationEvent] = []
        self._next_index = 0

    @property
    def active_levels(self) -> list[DegradationLevel]:
        return list(self._active)

    @property
    def log(self) -> list[DegradationEvent]:
        return list(self._log)

    @property
    def protected_capabilities(self) -> set[str]:
        return {CAPABILITY_NAMES[l] for l in self._protected_levels}

    def is_active(self, level: DegradationLevel) -> bool:
        return level in self._active

    def is_protected(self, level: DegradationLevel) -> bool:
        return level in self._protected_levels

    def activate_next(self, utilization: float) -> DegradationLevel | None:
        """Activate the next degradation level in sequence.

        Args:
            utilization: Current budget utilization (0.0-1.0).

        Returns:
            The activated level, or None if all levels already active.
        """
        if self._next_index >= len(self._effective_order):
            return None

        level = self._effective_order[self._next_index]
        self._active.append(level)
        self._log.append(DegradationEvent(
            level=level,
            triggered_at_utilization=utilization,
            capability_skipped=CAPABILITY_NAMES[level],
        ))
        self._next_index += 1
        return level

    def activate_up_to(self, target_level: DegradationLevel) -> list[DegradationLevel]:
        """Activate all levels up to and including target (in effective order).

        Skips already-active and protected levels.
        """
        activated = []
        for level in self._effective_order:
            if level in self._active:
                if level == target_level:
                    break
                continue
            self._active.append(level)
            self._log.append(DegradationEvent(
                level=level,
                triggered_at_utilization=0.0,
                capability_skipped=CAPABILITY_NAMES[level],
            ))
            activated.append(level)
            if level == target_level:
                break
        self._next_index = max(
            self._next_index,
            len([l for l in self._effective_order if l in self._active]),
        )
        return activated

    def should_skip(self, capability: str) -> bool:
        """Check if a capability should be skipped due to degradation.

        Args:
            capability: Capability name (e.g., "duplication_matrix").

        Returns:
            True if the capability's degradation level is active.
        """
        level = _NAME_TO_LEVEL.get(capability)
        if level is None:
            return False
        return level in self._active

    def get_validation_sample_fraction(self) -> float:
        """Get the validation sample fraction (reduced under degradation)."""
        if self.is_active(DegradationLevel.L2_REDUCE_VALIDATION):
            return 0.05
        return 0.10

    def get_profile_fields(self) -> list[str]:
        """Get the profile fields to use (reduced under degradation)."""
        if self.is_active(DegradationLevel.L4_REDUCE_PROFILE):
            return ["imports", "exports", "size", "complexity"]
        return [
            "imports", "exports", "size", "complexity",
            "age", "churn", "coupling", "test_coverage",
        ]
