"""Tests for roadmap/fidelity.py -- FidelityDeviation dataclass."""

from __future__ import annotations

import pytest

from superclaude.cli.roadmap.fidelity import FidelityDeviation, Severity


class TestSeverityEnum:
    def test_high(self):
        assert Severity.HIGH.value == "HIGH"

    def test_medium(self):
        assert Severity.MEDIUM.value == "MEDIUM"

    def test_low(self):
        assert Severity.LOW.value == "LOW"

    def test_three_members(self):
        assert len(Severity) == 3


class TestFidelityDeviationDataclass:
    def _make_deviation(self, **overrides):
        defaults = {
            "id": "DEV-001",
            "severity": Severity.HIGH,
            "deviation": "Missing FR-019",
            "upstream_quote": "Cross-references must be validated",
            "downstream_quote": "[MISSING]",
            "impact": "No cross-ref integrity",
            "recommended_correction": "Add FR-019 to Phase 2",
        }
        defaults.update(overrides)
        return FidelityDeviation(**defaults)

    def test_fidelity_deviation_dataclass(self):
        """Basic construction with valid fields."""
        dev = self._make_deviation()
        assert dev.id == "DEV-001"
        assert dev.severity == Severity.HIGH
        assert dev.deviation == "Missing FR-019"
        assert dev.upstream_quote == "Cross-references must be validated"
        assert dev.downstream_quote == "[MISSING]"
        assert dev.impact == "No cross-ref integrity"
        assert dev.recommended_correction == "Add FR-019 to Phase 2"

    def test_fidelity_deviation_all_seven_fields(self):
        """Dataclass has exactly 7 fields matching canonical schema."""
        import dataclasses
        fields = dataclasses.fields(FidelityDeviation)
        assert len(fields) == 7
        field_names = [f.name for f in fields]
        assert field_names == [
            "id",
            "severity",
            "deviation",
            "upstream_quote",
            "downstream_quote",
            "impact",
            "recommended_correction",
        ]

    def test_fidelity_deviation_invalid_severity(self):
        """Invalid severity value raises TypeError."""
        with pytest.raises(TypeError, match="severity must be a Severity enum member"):
            FidelityDeviation(
                id="DEV-001",
                severity="HIGH",  # type: ignore[arg-type] -- intentionally wrong type
                deviation="test",
                upstream_quote="quote",
                downstream_quote="quote",
                impact="impact",
                recommended_correction="fix",
            )

    def test_fidelity_deviation_medium_severity(self):
        """MEDIUM severity constructs correctly."""
        dev = self._make_deviation(severity=Severity.MEDIUM)
        assert dev.severity == Severity.MEDIUM

    def test_fidelity_deviation_low_severity(self):
        """LOW severity constructs correctly."""
        dev = self._make_deviation(severity=Severity.LOW)
        assert dev.severity == Severity.LOW

    def test_fidelity_deviation_empty_id_raises(self):
        """Empty id raises ValueError."""
        with pytest.raises(ValueError, match="id must be non-empty"):
            self._make_deviation(id="")

    def test_fidelity_deviation_empty_deviation_raises(self):
        """Empty deviation description raises ValueError."""
        with pytest.raises(ValueError, match="deviation must be non-empty"):
            self._make_deviation(deviation="")

    def test_fidelity_deviation_missing_downstream_marker(self):
        """[MISSING] marker is a valid downstream_quote value."""
        dev = self._make_deviation(downstream_quote="[MISSING]")
        assert dev.downstream_quote == "[MISSING]"

    def test_fidelity_deviation_importable(self):
        """Dataclass is importable from the fidelity module."""
        from superclaude.cli.roadmap.fidelity import FidelityDeviation as FD
        assert FD is FidelityDeviation
