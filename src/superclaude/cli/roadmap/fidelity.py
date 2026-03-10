"""Fidelity deviation data model -- 7-column deviation report schema.

Implements the canonical deviation report schema defined in D-0003 (OQ-006)
and docs/reference/deviation-report-format.md as a Python dataclass.

This module has zero imports from pipeline or gate enforcement code.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Deviation severity classification per D-0016."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class FidelityDeviation:
    """A single deviation row from a fidelity report.

    Represents one row of the 7-column deviation table defined in the
    canonical schema (D-0003, docs/reference/deviation-report-format.md).

    Fields:
        id: Unique deviation identifier, format DEV-NNN (zero-padded 3-digit).
        severity: Classification level (HIGH, MEDIUM, or LOW).
        deviation: Concise description of what differs.
        upstream_quote: Verbatim quote from the upstream document.
        downstream_quote: Verbatim quote from the downstream document,
            or '[MISSING]' if absent.
        impact: Assessment of how the deviation affects correctness.
        recommended_correction: Specific action to resolve the deviation.
    """

    id: str
    severity: Severity
    deviation: str
    upstream_quote: str
    downstream_quote: str
    impact: str
    recommended_correction: str

    def __post_init__(self) -> None:
        """Validate field constraints."""
        if not isinstance(self.severity, Severity):
            raise TypeError(
                f"severity must be a Severity enum member, got {type(self.severity).__name__}"
            )
        if not self.id:
            raise ValueError("id must be non-empty")
        if not self.deviation:
            raise ValueError("deviation must be non-empty")
        if not self.upstream_quote:
            raise ValueError("upstream_quote must be non-empty")
        if not self.downstream_quote:
            raise ValueError("downstream_quote must be non-empty")
        if not self.impact:
            raise ValueError("impact must be non-empty")
        if not self.recommended_correction:
            raise ValueError("recommended_correction must be non-empty")
