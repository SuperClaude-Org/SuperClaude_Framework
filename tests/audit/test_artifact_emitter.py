"""Tests for coverage and validation artifact emitters (T04.04 / D-0030)."""

import json
import pytest
from pathlib import Path

from superclaude.cli.audit.coverage import CoverageArtifact
from superclaude.cli.audit.spot_check import SpotCheckResult
from superclaude.cli.audit.artifact_emitter import (
    COVERAGE_SCHEMA_FIELDS,
    VALIDATION_SCHEMA_FIELDS,
    emit_coverage_artifact,
    emit_validation_artifact,
    validate_against_schema,
)


def _make_coverage() -> CoverageArtifact:
    return CoverageArtifact(
        total_files_scanned=100,
        total_files_classified=95,
        tier_breakdown={
            "tier-1": {"tier": "tier-1", "file_count": 30, "percentage": 31.58},
            "tier-2": {"tier": "tier-2", "file_count": 65, "percentage": 68.42},
        },
        percentages_sum=100.0,
    )


def _make_validation() -> SpotCheckResult:
    return SpotCheckResult(
        total_consolidated=95,
        sample_size=10,
        consistent_count=9,
        inconsistent_count=1,
        overall_consistency_rate=0.90,
        per_tier_rates={"tier-1": 0.85, "tier-2": 0.93},
        per_tier_sample_counts={"tier-1": 4, "tier-2": 6},
    )


class TestCoverageArtifact:
    """Verify coverage artifact emission."""

    def test_emit_creates_file(self, tmp_path: Path):
        """Coverage artifact is written to disk."""
        out = tmp_path / "coverage.json"
        emit_coverage_artifact(_make_coverage(), out)
        assert out.exists()

    def test_emit_valid_json(self, tmp_path: Path):
        """Coverage artifact is valid JSON."""
        out = tmp_path / "coverage.json"
        emit_coverage_artifact(_make_coverage(), out)
        data = json.loads(out.read_text())
        assert isinstance(data, dict)

    def test_schema_valid(self, tmp_path: Path):
        """Coverage artifact passes schema validation."""
        out = tmp_path / "coverage.json"
        result = emit_coverage_artifact(_make_coverage(), out)
        assert result.valid

    def test_creates_parent_dirs(self, tmp_path: Path):
        """Creates parent directories if they don't exist."""
        out = tmp_path / "nested" / "dir" / "coverage.json"
        emit_coverage_artifact(_make_coverage(), out)
        assert out.exists()


class TestValidationArtifact:
    """Verify validation artifact emission."""

    def test_emit_creates_file(self, tmp_path: Path):
        """Validation artifact is written to disk."""
        out = tmp_path / "validation.json"
        emit_validation_artifact(_make_validation(), out)
        assert out.exists()

    def test_emit_valid_json(self, tmp_path: Path):
        """Validation artifact is valid JSON."""
        out = tmp_path / "validation.json"
        emit_validation_artifact(_make_validation(), out)
        data = json.loads(out.read_text())
        assert isinstance(data, dict)

    def test_schema_valid(self, tmp_path: Path):
        """Validation artifact passes schema validation."""
        out = tmp_path / "validation.json"
        result = emit_validation_artifact(_make_validation(), out)
        assert result.valid

    def test_includes_calibration_notes(self, tmp_path: Path):
        """Validation artifact includes calibration notes."""
        out = tmp_path / "validation.json"
        emit_validation_artifact(_make_validation(), out)
        data = json.loads(out.read_text())
        assert "calibration_notes" in data
        assert len(data["calibration_notes"]) > 50


class TestSchemaValidation:
    """Verify schema validation mechanics."""

    def test_valid_data(self):
        """Valid data passes schema validation."""
        result = validate_against_schema(
            {"name": "test", "count": 5},
            {"name": str, "count": int},
        )
        assert result.valid

    def test_missing_field(self):
        """Missing field is detected."""
        result = validate_against_schema(
            {"name": "test"},
            {"name": str, "count": int},
        )
        assert not result.valid
        assert "count" in result.missing_fields

    def test_wrong_type(self):
        """Wrong type is detected."""
        result = validate_against_schema(
            {"name": "test", "count": "five"},
            {"name": str, "count": int},
        )
        assert not result.valid
        assert len(result.type_errors) == 1
