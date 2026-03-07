"""Conflict review -- file-level overlap detection for remediation safety.

Detects when remediation output modifies files that intervening tasks have
also changed, signaling potential conflicts that require re-gating.

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

_log = logging.getLogger("superclaude.pipeline.conflict_review")


class ConflictAction(Enum):
    """Action to take based on conflict review outcome."""

    PASSTHROUGH = "passthrough"
    REGATE = "regate"


@dataclass
class ConflictReviewResult:
    """Result of a file-level overlap detection."""

    action: ConflictAction
    overlapping_files: set[Path] = field(default_factory=set)
    remediation_files: set[Path] = field(default_factory=set)
    intervening_files: set[Path] = field(default_factory=set)

    @property
    def has_conflict(self) -> bool:
        return len(self.overlapping_files) > 0


def detect_file_overlap(
    remediation_files: set[Path],
    intervening_files: set[Path],
) -> set[Path]:
    """Detect file-level overlap between remediation and intervening task work.

    Args:
        remediation_files: Files modified by the remediation step.
        intervening_files: Files modified by tasks that ran between the
            original step and its remediation.

    Returns:
        Set of overlapping file paths (intersection).
    """
    overlap = remediation_files & intervening_files
    if overlap:
        _log.warning(
            "File overlap detected: %d file(s) modified by both remediation "
            "and intervening tasks: %s",
            len(overlap),
            ", ".join(str(p) for p in sorted(overlap)),
        )
    return overlap


def review_conflicts(
    remediation_files: set[Path],
    intervening_files: set[Path],
) -> ConflictReviewResult:
    """Review remediation output for file-level conflicts with intervening work.

    When overlap is detected, the result indicates REGATE action so the
    merged output can be re-evaluated. When no overlap exists, the result
    is PASSTHROUGH.

    Handles edge cases gracefully:
    - Empty remediation_files: no conflict possible → PASSTHROUGH
    - Empty intervening_files: no conflict possible → PASSTHROUGH
    - Both empty: PASSTHROUGH

    Args:
        remediation_files: Files modified by the remediation step.
        intervening_files: Files modified by intervening tasks.

    Returns:
        ConflictReviewResult with action and overlap details.
    """
    overlap = detect_file_overlap(remediation_files, intervening_files)

    if overlap:
        _log.info(
            "Conflict review: REGATE required for %d overlapping file(s)",
            len(overlap),
        )
        return ConflictReviewResult(
            action=ConflictAction.REGATE,
            overlapping_files=overlap,
            remediation_files=remediation_files,
            intervening_files=intervening_files,
        )

    _log.debug("Conflict review: no overlap, PASSTHROUGH")
    return ConflictReviewResult(
        action=ConflictAction.PASSTHROUGH,
        overlapping_files=set(),
        remediation_files=remediation_files,
        intervening_files=intervening_files,
    )
