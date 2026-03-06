"""Manifest completeness gate that blocks analysis if profiling coverage is insufficient.

Implements AC2 (quality extension): ensures profiling covers all repository
files before analysis begins. Default threshold: 95%.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_COVERAGE_THRESHOLD = 0.95

# File patterns excluded from completeness check (binary, vendor)
_EXCLUDED_PATTERNS: frozenset[str] = frozenset({
    ".git/",
    "node_modules/",
    "vendor/",
    "__pycache__/",
    ".venv/",
    "venv/",
    ".tox/",
    "dist/",
    "build/",
    ".egg-info/",
})

_EXCLUDED_EXTENSIONS: frozenset[str] = frozenset({
    ".pyc", ".pyo", ".so", ".dylib", ".dll",
    ".exe", ".bin", ".dat",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".tar", ".gz", ".bz2",
    ".pdf", ".doc", ".docx",
})


@dataclass
class GateResult:
    """Result of the manifest completeness gate check."""

    passed: bool
    coverage: float
    threshold: float
    total_eligible: int
    total_profiled: int
    missing_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "coverage": round(self.coverage, 4),
            "threshold": self.threshold,
            "total_eligible": self.total_eligible,
            "total_profiled": self.total_profiled,
            "missing_count": len(self.missing_files),
            "missing_files": self.missing_files,
        }


def is_excluded(file_path: str) -> bool:
    """Check if a file should be excluded from completeness check."""
    normalized = file_path.replace("\\", "/").lower()

    for pattern in _EXCLUDED_PATTERNS:
        if pattern in normalized:
            return True

    for ext in _EXCLUDED_EXTENSIONS:
        if normalized.endswith(ext):
            return True

    return False


def check_manifest_completeness(
    all_files: list[str],
    profiled_files: set[str],
    *,
    threshold: float = DEFAULT_COVERAGE_THRESHOLD,
) -> GateResult:
    """Check if profiling coverage meets the threshold.

    Args:
        all_files: All repository file paths (the ground truth).
        profiled_files: Set of file paths that were profiled.
        threshold: Minimum coverage fraction (default 0.95).

    Returns:
        GateResult with pass/fail, coverage percentage, and missing files.
    """
    # Filter to eligible files (exclude binary, vendor, etc.)
    eligible = [f for f in all_files if not is_excluded(f)]
    total_eligible = len(eligible)

    if total_eligible == 0:
        return GateResult(
            passed=True,
            coverage=1.0,
            threshold=threshold,
            total_eligible=0,
            total_profiled=0,
        )

    # Count profiled among eligible
    profiled_eligible = [f for f in eligible if f in profiled_files]
    total_profiled = len(profiled_eligible)

    coverage = total_profiled / total_eligible
    missing = [f for f in eligible if f not in profiled_files]

    passed = coverage >= threshold

    if not passed:
        logger.warning(
            "Manifest completeness gate BLOCKED: coverage=%.2f%% (threshold=%.2f%%), "
            "missing %d files",
            coverage * 100,
            threshold * 100,
            len(missing),
        )
        for f in missing[:20]:  # Log up to 20 missing files
            logger.warning("  Missing: %s", f)

    return GateResult(
        passed=passed,
        coverage=coverage,
        threshold=threshold,
        total_eligible=total_eligible,
        total_profiled=total_profiled,
        missing_files=missing,
    )
