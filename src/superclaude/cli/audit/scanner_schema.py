"""Scanner output schema definition and validation.

Implements AC11:
- Phase-1 simplified schema: file_path, classification, evidence, confidence, tier
- Phase-2 extended schema: adds 8 profiling fields (imports, exports, size,
  complexity, age, churn, coupling, test_coverage)

Phase-2 schema is a superset of Phase-1; Phase-1 output remains valid
against Phase-2 validation (backward compatible).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Phase-1 required fields
PHASE1_REQUIRED_FIELDS = frozenset({
    "file_path",
    "classification",
    "evidence",
    "confidence",
    "tier",
})

# Phase-2 additional profile fields (all optional for backward compat)
PHASE2_PROFILE_FIELDS = frozenset({
    "imports",
    "exports",
    "size",
    "complexity",
    "age",
    "churn",
    "coupling",
    "test_coverage",
})

# Expected types for Phase-1 fields
_PHASE1_TYPES: dict[str, type | tuple[type, ...]] = {
    "file_path": str,
    "classification": str,
    "evidence": list,
    "confidence": (int, float),
    "tier": str,
}

# Expected types for Phase-2 profile fields
_PHASE2_TYPES: dict[str, type | tuple[type, ...]] = {
    "imports": list,
    "exports": list,
    "size": int,
    "complexity": (int, float),
    "age": str,
    "churn": int,
    "coupling": (int, float),
    "test_coverage": (int, float, type(None)),
}


@dataclass
class ValidationError:
    """A single schema validation error."""

    field: str
    error: str

    def to_dict(self) -> dict[str, str]:
        return {"field": self.field, "error": self.error}


@dataclass
class SchemaValidationResult:
    """Result of validating scanner output against a schema."""

    valid: bool
    errors: list[ValidationError]
    schema_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "schema_version": self.schema_version,
        }


def validate_phase1(output: dict[str, Any]) -> SchemaValidationResult:
    """Validate scanner output against the Phase-1 schema.

    Phase-1 requires: file_path, classification, evidence, confidence, tier.
    All must be present with correct types.
    """
    errors: list[ValidationError] = []

    for field_name in PHASE1_REQUIRED_FIELDS:
        if field_name not in output:
            errors.append(ValidationError(
                field=field_name,
                error=f"Missing required field: {field_name}",
            ))
        else:
            expected = _PHASE1_TYPES[field_name]
            if not isinstance(output[field_name], expected):
                errors.append(ValidationError(
                    field=field_name,
                    error=f"Wrong type for {field_name}: expected {expected}, got {type(output[field_name]).__name__}",
                ))

    return SchemaValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        schema_version="phase-1",
    )


def validate_phase2(output: dict[str, Any]) -> SchemaValidationResult:
    """Validate scanner output against the Phase-2 schema.

    Phase-2 is a superset of Phase-1:
    - Phase-1 required fields are still required
    - Phase-2 profile fields are optional (for backward compatibility)
    - If present, profile fields must have correct types
    """
    errors: list[ValidationError] = []

    # Phase-1 fields still required
    for field_name in PHASE1_REQUIRED_FIELDS:
        if field_name not in output:
            errors.append(ValidationError(
                field=field_name,
                error=f"Missing required field: {field_name}",
            ))
        else:
            expected = _PHASE1_TYPES[field_name]
            if not isinstance(output[field_name], expected):
                errors.append(ValidationError(
                    field=field_name,
                    error=f"Wrong type for {field_name}: expected {expected}, got {type(output[field_name]).__name__}",
                ))

    # Phase-2 profile fields: optional, but type-checked if present
    for field_name in PHASE2_PROFILE_FIELDS:
        if field_name in output:
            expected = _PHASE2_TYPES[field_name]
            if not isinstance(output[field_name], expected):
                errors.append(ValidationError(
                    field=field_name,
                    error=f"Wrong type for {field_name}: expected {expected}, got {type(output[field_name]).__name__}",
                ))

    return SchemaValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        schema_version="phase-2",
    )


def has_full_profile(output: dict[str, Any]) -> bool:
    """Check whether output includes all 8 Phase-2 profile fields."""
    return PHASE2_PROFILE_FIELDS.issubset(output.keys())
