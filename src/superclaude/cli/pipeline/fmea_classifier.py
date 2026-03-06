"""FMEA failure mode classifier -- dual signal detection for silent corruption.

Provides:
- FMEAFailureMode: classification output with detection_difficulty and severity
- classify_failure_modes(): dual-signal classifier for computational deliverables

Signal 1: Cross-reference against invariant predicates. Violation without error = silent corruption.
Signal 2: Independent no-error-path detection. Computation returns value without exception
           on degenerate input = potential silent corruption. Works even without invariant predicates.

Dual signal prevents circular dependency on M2 registry completeness.

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from .fmea_domains import InputDomain, enumerate_input_domains
from .invariants import InvariantEntry
from .models import Deliverable


class DetectionDifficulty(Enum):
    """How easily a failure is detected."""

    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    SILENT = "silent"


class Severity(Enum):
    """Impact severity of a failure mode."""

    DATA_LOSS = "data_loss"
    WRONG_STATE = "wrong_state"
    DEGRADED = "degraded"
    COSMETIC = "cosmetic"

    @property
    def rank(self) -> int:
        """Numeric rank for comparison (higher = more severe)."""
        return {
            Severity.COSMETIC: 1,
            Severity.DEGRADED: 2,
            Severity.WRONG_STATE: 3,
            Severity.DATA_LOSS: 4,
        }[self]

    def __ge__(self, other: Severity) -> bool:
        return self.rank >= other.rank

    def __gt__(self, other: Severity) -> bool:
        return self.rank > other.rank

    def __le__(self, other: Severity) -> bool:
        return self.rank <= other.rank

    def __lt__(self, other: Severity) -> bool:
        return self.rank < other.rank


@dataclass
class FMEAFailureMode:
    """A classified failure mode for a deliverable + domain combination.

    Attributes:
        deliverable_id: The deliverable being analyzed.
        domain_description: The input domain that triggers this failure.
        detection_difficulty: How easily the failure is detected.
        severity: Impact severity.
        signal_source: Which signal detected this ("signal_1", "signal_2", "both").
        description: Human-readable description of the failure mode.
        invariant_predicate: The invariant predicate violated (if Signal 1).
    """

    deliverable_id: str
    domain_description: str
    detection_difficulty: DetectionDifficulty
    severity: Severity
    signal_source: str
    description: str
    invariant_predicate: str = ""


# ---------------------------------------------------------------------------
# Detection heuristics
# ---------------------------------------------------------------------------

# Patterns indicating explicit error handling (raises, throws, errors)
_ERROR_PATH_RE = re.compile(
    r"\b(?:raise|raises?|throw|throws?|error|exception|fail|abort|reject|invalid|"
    r"TypeError|ValueError|KeyError|IndexError|RuntimeError)\b",
    re.IGNORECASE,
)

# Patterns indicating value return without validation
_SILENT_RETURN_RE = re.compile(
    r"\b(?:return|returns?|produce|produces?|yield|yields?|compute|computes?|"
    r"calculate|calculates?|output|outputs?)\b",
    re.IGNORECASE,
)

# Patterns indicating state mutation
_STATE_MUTATION_RE = re.compile(
    r"\b(?:advance|increment|decrement|update|set|reset|modify|assign|"
    r"append|extend|replace|offset|shift|move)\b",
    re.IGNORECASE,
)

# Patterns indicating wrong/incorrect outcome
_WRONG_OUTCOME_RE = re.compile(
    r"\b(?:wrong|incorrect|invalid|stale|outdated|corrupt|mismatch|"
    r"inconsistent|drift|desync|off-by|overflow|underflow)\b",
    re.IGNORECASE,
)

# Patterns indicating delayed detection
_DELAYED_DETECTION_RE = re.compile(
    r"\b(?:later|eventually|downstream|subsequently|next|after|future|"
    r"propagate|cascade|accumulate|gradually)\b",
    re.IGNORECASE,
)


def classify_failure_modes(
    deliverables: list[Deliverable],
    domain_map: dict[str, list[InputDomain]],
    invariant_entries: list[InvariantEntry] | None = None,
) -> list[FMEAFailureMode]:
    """Classify failure modes using dual-signal detection.

    Args:
        deliverables: All deliverables to analyze.
        domain_map: Map of deliverable_id -> input domains (from fmea_domains).
        invariant_entries: Optional invariant entries for Signal 1 cross-reference.

    Returns:
        List of classified FMEAFailureMode objects.
    """
    if invariant_entries is None:
        invariant_entries = []

    # Build invariant lookup
    invariant_lookup: dict[str, InvariantEntry] = {
        e.variable_name: e for e in invariant_entries
    }

    results: list[FMEAFailureMode] = []

    for d in deliverables:
        domains = domain_map.get(d.id, [])
        if not domains:
            continue

        desc = d.description or ""

        for domain in domains:
            # Run both signals
            s1 = _signal_1_invariant_cross_reference(desc, d.id, domain, invariant_lookup)
            s2 = _signal_2_no_error_path(desc, d.id, domain)

            # Combine signals
            mode = _combine_signals(s1, s2, d.id, domain)
            if mode is not None:
                results.append(mode)

    return results


def _signal_1_invariant_cross_reference(
    description: str,
    deliverable_id: str,
    domain: InputDomain,
    invariant_lookup: dict[str, InvariantEntry],
) -> FMEAFailureMode | None:
    """Signal 1: Cross-reference against invariant predicates.

    Violation without error path = silent corruption.
    """
    if not invariant_lookup:
        return None

    desc_lower = description.lower()

    for var_name, entry in invariant_lookup.items():
        var_lower = var_name.lower().lstrip("_")
        if var_lower not in desc_lower and var_name.lower() not in desc_lower:
            continue

        # Variable referenced in this deliverable
        has_mutation = bool(_STATE_MUTATION_RE.search(description))
        has_error_path = bool(_ERROR_PATH_RE.search(description))

        if has_mutation and not has_error_path:
            # Mutation without error handling = potential invariant violation
            return FMEAFailureMode(
                deliverable_id=deliverable_id,
                domain_description=domain.description,
                detection_difficulty=DetectionDifficulty.SILENT,
                severity=Severity.WRONG_STATE,
                signal_source="signal_1",
                description=(
                    f"State variable '{var_name}' mutated without error path. "
                    f"Invariant '{entry.invariant_predicate}' may be violated "
                    f"on {domain.description} input."
                ),
                invariant_predicate=entry.invariant_predicate,
            )

    return None


def _signal_2_no_error_path(
    description: str,
    deliverable_id: str,
    domain: InputDomain,
) -> FMEAFailureMode | None:
    """Signal 2: Independent no-error-path detection.

    Computation returns value on degenerate input without exception = potential silent corruption.
    Works even without invariant predicates registered.
    """
    has_error_path = bool(_ERROR_PATH_RE.search(description))
    has_return = bool(_SILENT_RETURN_RE.search(description))
    has_wrong = bool(_WRONG_OUTCOME_RE.search(description))
    has_mutation = bool(_STATE_MUTATION_RE.search(description))
    has_delayed = bool(_DELAYED_DETECTION_RE.search(description))

    # Degenerate domain categories that are high-risk for silent failures
    from .fmea_domains import DomainCategory

    degenerate_categories = {
        DomainCategory.EMPTY, DomainCategory.NULL, DomainCategory.ZERO,
        DomainCategory.NEGATIVE, DomainCategory.FILTER_ALL,
    }
    is_degenerate = domain.category in degenerate_categories

    if has_error_path:
        # Explicit error handling -> immediate detection
        severity = _infer_severity_from_description(description)
        return FMEAFailureMode(
            deliverable_id=deliverable_id,
            domain_description=domain.description,
            detection_difficulty=DetectionDifficulty.IMMEDIATE,
            severity=severity,
            signal_source="signal_2",
            description=(
                f"Error path exists for {domain.description} input. "
                f"Detection: immediate."
            ),
        )

    if has_wrong or (has_mutation and not has_error_path and is_degenerate):
        # Wrong outcome pattern or mutation without error on degenerate input
        return FMEAFailureMode(
            deliverable_id=deliverable_id,
            domain_description=domain.description,
            detection_difficulty=DetectionDifficulty.SILENT,
            severity=Severity.WRONG_STATE if has_mutation else Severity.DEGRADED,
            signal_source="signal_2",
            description=(
                f"No error path for {domain.description} input. "
                f"Computation may produce wrong result silently."
            ),
        )

    if has_return and is_degenerate and not has_error_path:
        # Returns value on degenerate input without error
        detection = DetectionDifficulty.DELAYED if has_delayed else DetectionDifficulty.SILENT
        return FMEAFailureMode(
            deliverable_id=deliverable_id,
            domain_description=domain.description,
            detection_difficulty=detection,
            severity=Severity.DEGRADED,
            signal_source="signal_2",
            description=(
                f"Returns value on {domain.description} input without error handling. "
                f"Potential silent failure."
            ),
        )

    return None


def _combine_signals(
    s1: FMEAFailureMode | None,
    s2: FMEAFailureMode | None,
    deliverable_id: str,
    domain: InputDomain,
) -> FMEAFailureMode | None:
    """Combine Signal 1 and Signal 2 into unified classification.

    Silent corruption from either signal = highest severity.
    """
    if s1 is None and s2 is None:
        return None

    if s1 is not None and s2 is not None:
        # Both signals fired -- take the more severe classification
        combined_difficulty = (
            DetectionDifficulty.SILENT
            if s1.detection_difficulty == DetectionDifficulty.SILENT
            or s2.detection_difficulty == DetectionDifficulty.SILENT
            else max(
                s1.detection_difficulty,
                s2.detection_difficulty,
                key=lambda d: {"immediate": 0, "delayed": 1, "silent": 2}[d.value],
            )
        )
        combined_severity = max(s1.severity, s2.severity)

        # Silent corruption = always highest severity (wrong_state minimum)
        if combined_difficulty == DetectionDifficulty.SILENT:
            if combined_severity < Severity.WRONG_STATE:
                combined_severity = Severity.WRONG_STATE

        return FMEAFailureMode(
            deliverable_id=deliverable_id,
            domain_description=domain.description,
            detection_difficulty=combined_difficulty,
            severity=combined_severity,
            signal_source="both",
            description=(
                f"Dual signal detection: {s1.description} | {s2.description}"
            ),
            invariant_predicate=s1.invariant_predicate,
        )

    # Single signal
    result = s1 if s1 is not None else s2
    assert result is not None

    # Silent corruption from any single signal = elevated to wrong_state minimum
    if result.detection_difficulty == DetectionDifficulty.SILENT:
        if result.severity < Severity.WRONG_STATE:
            result = FMEAFailureMode(
                deliverable_id=result.deliverable_id,
                domain_description=result.domain_description,
                detection_difficulty=result.detection_difficulty,
                severity=Severity.WRONG_STATE,
                signal_source=result.signal_source,
                description=result.description,
                invariant_predicate=result.invariant_predicate,
            )

    return result


def _infer_severity_from_description(description: str) -> Severity:
    """Infer severity from description keywords."""
    desc_lower = description.lower()

    if any(kw in desc_lower for kw in ("data loss", "corrupt", "destroy", "delete")):
        return Severity.DATA_LOSS
    if any(kw in desc_lower for kw in ("wrong", "incorrect", "invalid state", "mismatch")):
        return Severity.WRONG_STATE
    if any(kw in desc_lower for kw in ("slow", "degraded", "suboptimal", "partial")):
        return Severity.DEGRADED
    return Severity.COSMETIC
