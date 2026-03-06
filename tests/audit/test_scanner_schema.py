"""Tests for scanner output schema validation (Phase-1 and Phase-2).

Validates AC11: locked scanner output contracts.
"""

from __future__ import annotations

import pytest

from superclaude.cli.audit.scanner_schema import (
    PHASE1_REQUIRED_FIELDS,
    PHASE2_PROFILE_FIELDS,
    has_full_profile,
    validate_phase1,
    validate_phase2,
)


# Fixtures
VALID_PHASE1_OUTPUT = {
    "file_path": "src/main.py",
    "classification": "DELETE",
    "evidence": ["zero references found"],
    "confidence": 0.9,
    "tier": "tier-1",
}

VALID_PHASE2_OUTPUT = {
    **VALID_PHASE1_OUTPUT,
    "imports": ["os", "sys"],
    "exports": ["main"],
    "size": 150,
    "complexity": 3.5,
    "age": "2024-01-15",
    "churn": 12,
    "coupling": 0.3,
    "test_coverage": 0.85,
}


class TestPhase1Schema:
    def test_valid_output_passes(self):
        result = validate_phase1(VALID_PHASE1_OUTPUT)
        assert result.valid
        assert result.schema_version == "phase-1"

    def test_missing_required_field_fails(self):
        incomplete = {k: v for k, v in VALID_PHASE1_OUTPUT.items() if k != "confidence"}
        result = validate_phase1(incomplete)
        assert not result.valid
        assert any(e.field == "confidence" for e in result.errors)

    def test_wrong_type_fails(self):
        bad_type = {**VALID_PHASE1_OUTPUT, "confidence": "high"}
        result = validate_phase1(bad_type)
        assert not result.valid
        assert any(e.field == "confidence" for e in result.errors)

    def test_all_required_fields_defined(self):
        assert PHASE1_REQUIRED_FIELDS == {"file_path", "classification", "evidence", "confidence", "tier"}

    def test_empty_output_fails(self):
        result = validate_phase1({})
        assert not result.valid
        assert len(result.errors) == len(PHASE1_REQUIRED_FIELDS)

    def test_serialization(self):
        result = validate_phase1(VALID_PHASE1_OUTPUT)
        d = result.to_dict()
        assert "valid" in d
        assert "errors" in d
        assert "schema_version" in d


class TestPhase2Schema:
    def test_phase1_output_passes_phase2(self):
        """Backward compatibility: Phase-1 output passes Phase-2 validation."""
        result = validate_phase2(VALID_PHASE1_OUTPUT)
        assert result.valid

    def test_full_phase2_output_passes(self):
        result = validate_phase2(VALID_PHASE2_OUTPUT)
        assert result.valid
        assert result.schema_version == "phase-2"

    def test_phase2_wrong_profile_type_fails(self):
        bad = {**VALID_PHASE2_OUTPUT, "size": "large"}
        result = validate_phase2(bad)
        assert not result.valid
        assert any(e.field == "size" for e in result.errors)

    def test_all_8_profile_fields(self):
        assert len(PHASE2_PROFILE_FIELDS) == 8
        assert PHASE2_PROFILE_FIELDS == {
            "imports", "exports", "size", "complexity",
            "age", "churn", "coupling", "test_coverage",
        }

    def test_has_full_profile(self):
        assert has_full_profile(VALID_PHASE2_OUTPUT)
        assert not has_full_profile(VALID_PHASE1_OUTPUT)

    def test_missing_phase1_field_fails_phase2(self):
        incomplete = {k: v for k, v in VALID_PHASE2_OUTPUT.items() if k != "file_path"}
        result = validate_phase2(incomplete)
        assert not result.valid

    def test_null_test_coverage_valid(self):
        output = {**VALID_PHASE2_OUTPUT, "test_coverage": None}
        result = validate_phase2(output)
        assert result.valid
