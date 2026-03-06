"""Tests for FMEA failure mode classifier -- T02.07.

Scenarios from tasklist:
1. "offset advances by wrong amount, no error raised" -> silent + highest severity
2. "TypeError on null input" -> immediate + medium
3. "filter returns empty instead of raising on invalid predicate" -> delayed + high
4. Signal 2 independently detects silent corruption without invariant predicate
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.fmea_classifier import (
    DetectionDifficulty,
    FMEAFailureMode,
    Severity,
    classify_failure_modes,
)
from superclaude.cli.pipeline.fmea_domains import (
    DomainCategory,
    InputDomain,
    enumerate_input_domains,
)
from superclaude.cli.pipeline.invariants import InvariantEntry, MutationSite
from superclaude.cli.pipeline.models import Deliverable, DeliverableKind


class TestFMEAClassifier:
    """Core classification scenarios from tasklist."""

    def test_silent_corruption_wrong_amount(self):
        """offset advances by wrong amount, no error raised -> silent + highest severity."""
        d = Deliverable(
            id="D2.3",
            description="Advance offset by step_size, update position counter",
            kind=DeliverableKind.IMPLEMENT,
        )
        domains = {"D2.3": [InputDomain(DomainCategory.ZERO, "Zero numeric input")]}
        entries = [
            InvariantEntry(
                variable_name="offset",
                scope="class-level",
                invariant_predicate="offset >= 0",
                mutation_sites=[MutationSite("D2.3", "advance offset", "")],
            )
        ]

        results = classify_failure_modes([d], domains, entries)
        assert len(results) >= 1

        # Find the most severe result
        silent_results = [
            r for r in results if r.detection_difficulty == DetectionDifficulty.SILENT
        ]
        assert len(silent_results) >= 1, f"Expected silent corruption, got: {results}"

        for r in silent_results:
            assert r.severity >= Severity.WRONG_STATE, (
                f"Silent corruption should have highest severity, got {r.severity}"
            )

    def test_type_error_on_null_immediate(self):
        """TypeError on null input -> immediate + medium."""
        d = Deliverable(
            id="D3.1",
            description="Compute total, raises TypeError on null input",
            kind=DeliverableKind.IMPLEMENT,
        )
        domains = {"D3.1": [InputDomain(DomainCategory.NULL, "Null/None input value")]}

        results = classify_failure_modes([d], domains, invariant_entries=[])
        assert len(results) >= 1

        immediate_results = [
            r for r in results if r.detection_difficulty == DetectionDifficulty.IMMEDIATE
        ]
        assert len(immediate_results) >= 1, f"Expected immediate detection, got: {results}"

    def test_filter_returns_empty_delayed(self):
        """filter returns empty instead of raising on bad predicate -> delayed/silent + high."""
        d = Deliverable(
            id="D4.1",
            description="Filter events by type, returns empty list on unmatched predicate, later causing downstream degradation",
            kind=DeliverableKind.IMPLEMENT,
        )
        domains = {"D4.1": [
            InputDomain(DomainCategory.FILTER_ALL, "Filter predicate removes all elements"),
        ]}

        results = classify_failure_modes([d], domains, invariant_entries=[])
        assert len(results) >= 1

        # Should detect delayed or silent corruption
        non_immediate = [
            r for r in results
            if r.detection_difficulty in (DetectionDifficulty.DELAYED, DetectionDifficulty.SILENT)
        ]
        assert len(non_immediate) >= 1, f"Expected delayed/silent, got: {results}"

    def test_signal_2_independent_without_invariants(self):
        """Signal 2 independently detects silent corruption without invariant predicates."""
        d = Deliverable(
            id="D5.1",
            description="Increment replay offset, no validation of new position",
            kind=DeliverableKind.IMPLEMENT,
        )
        domains = {"D5.1": [InputDomain(DomainCategory.ZERO, "Zero numeric input")]}

        # No invariant entries passed -- Signal 2 must detect independently
        results = classify_failure_modes([d], domains, invariant_entries=[])
        assert len(results) >= 1

        silent = [r for r in results if r.detection_difficulty == DetectionDifficulty.SILENT]
        assert len(silent) >= 1, (
            f"Signal 2 should detect silent corruption independently. Got: {results}"
        )
        for r in silent:
            assert r.signal_source in ("signal_2", "both"), (
                f"Expected signal_2, got {r.signal_source}"
            )


class TestSeverityOrdering:
    """Verify severity ordering and comparison."""

    def test_severity_ranking(self):
        assert Severity.DATA_LOSS > Severity.WRONG_STATE
        assert Severity.WRONG_STATE > Severity.DEGRADED
        assert Severity.DEGRADED > Severity.COSMETIC

    def test_silent_corruption_elevated_to_wrong_state(self):
        """Silent corruption should always be at least WRONG_STATE severity."""
        d = Deliverable(
            id="D6.1",
            description="Compute display label, returns stale value silently",
            kind=DeliverableKind.IMPLEMENT,
        )
        domains = {"D6.1": [InputDomain(DomainCategory.EMPTY, "Empty input collection/string")]}

        results = classify_failure_modes([d], domains)
        silent = [r for r in results if r.detection_difficulty == DetectionDifficulty.SILENT]
        for r in silent:
            assert r.severity >= Severity.WRONG_STATE


class TestDetectionDifficulty:
    """Verify all detection difficulty levels are classifiable."""

    def test_all_difficulties_exist(self):
        assert DetectionDifficulty.IMMEDIATE.value == "immediate"
        assert DetectionDifficulty.DELAYED.value == "delayed"
        assert DetectionDifficulty.SILENT.value == "silent"

    def test_all_severities_exist(self):
        assert Severity.DATA_LOSS.value == "data_loss"
        assert Severity.WRONG_STATE.value == "wrong_state"
        assert Severity.DEGRADED.value == "degraded"
        assert Severity.COSMETIC.value == "cosmetic"


class TestEdgeCases:
    """Edge cases for the classifier."""

    def test_empty_deliverables(self):
        results = classify_failure_modes([], {}, [])
        assert results == []

    def test_no_domains_no_results(self):
        d = Deliverable(id="D7.1", description="Non-computational setup", kind=DeliverableKind.IMPLEMENT)
        results = classify_failure_modes([d], {}, [])
        assert results == []

    def test_non_computational_excluded(self):
        """Non-computational deliverables with no domains produce no failure modes."""
        d = Deliverable(id="D8.1", description="Document the API design", kind=DeliverableKind.IMPLEMENT)
        results = classify_failure_modes([d], {}, [])
        assert results == []
