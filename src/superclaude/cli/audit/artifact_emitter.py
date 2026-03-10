"""Coverage and validation artifact emitters.

Implements T04.04 / D-0030 / AC2+AC6: emits schema-validated JSON artifacts
for coverage metrics and validation results at standard paths.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .coverage import CoverageArtifact
from .spot_check import SpotCheckResult
from .validation_output import CALIBRATION_NOTES, METHODOLOGY_LIMITATIONS

# Schema definitions for validation

COVERAGE_SCHEMA_FIELDS = {
    "total_files_scanned": int,
    "total_files_classified": int,
    "tier_breakdown": dict,
    "percentages_sum": float,
}

VALIDATION_SCHEMA_FIELDS = {
    "total_consolidated": int,
    "sample_size": int,
    "consistent_count": int,
    "inconsistent_count": int,
    "overall_consistency_rate": float,
    "per_tier_rates": dict,
    "per_tier_sample_counts": dict,
    "calibration_notes": str,
}


@dataclass
class SchemaValidationResult:
    """Result of validating an artifact against its schema."""

    valid: bool
    missing_fields: list[str]
    type_errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "missing_fields": self.missing_fields,
            "type_errors": self.type_errors,
        }


def validate_against_schema(
    data: dict[str, Any],
    schema: dict[str, type],
) -> SchemaValidationResult:
    """Validate a dict against a field-type schema."""
    missing = []
    type_errors = []
    for field_name, expected_type in schema.items():
        if field_name not in data:
            missing.append(field_name)
        elif not isinstance(data[field_name], expected_type):
            type_errors.append(
                f"{field_name}: expected {expected_type.__name__}, "
                f"got {type(data[field_name]).__name__}"
            )
    return SchemaValidationResult(
        valid=len(missing) == 0 and len(type_errors) == 0,
        missing_fields=missing,
        type_errors=type_errors,
    )


def emit_coverage_artifact(
    coverage: CoverageArtifact,
    output_path: Path,
) -> SchemaValidationResult:
    """Emit coverage artifact as schema-validated JSON.

    Args:
        coverage: CoverageArtifact from CoverageTracker.
        output_path: Path to write the JSON artifact.

    Returns:
        SchemaValidationResult indicating whether the artifact is valid.
    """
    data = coverage.to_dict()
    validation = validate_against_schema(data, COVERAGE_SCHEMA_FIELDS)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return validation


def emit_validation_artifact(
    result: SpotCheckResult,
    output_path: Path,
) -> SchemaValidationResult:
    """Emit validation artifact as schema-validated JSON.

    Args:
        result: SpotCheckResult from spot_check_validate.
        output_path: Path to write the JSON artifact.

    Returns:
        SchemaValidationResult indicating whether the artifact is valid.
    """
    data = result.to_dict()
    data["calibration_notes"] = CALIBRATION_NOTES
    data["methodology_limitations"] = METHODOLOGY_LIMITATIONS

    validation = validate_against_schema(data, VALIDATION_SCHEMA_FIELDS)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return validation
