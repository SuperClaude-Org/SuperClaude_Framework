"""Resume semantics for interrupted audit runs.

Implements T04.11 / D-0037 / AC3: reads progress.json, identifies last
completed phase/batch, resumes from next pending unit, merges partial results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .checkpoint import CheckpointReader, CheckpointState, CheckpointWriter
from .consolidation import ConsolidatedFinding, ConsolidationReport


@dataclass
class ResumePoint:
    """Identifies where to resume an interrupted audit run."""

    has_checkpoint: bool
    completed_phases: list[str]
    completed_batch_ids: set[str]
    next_phase: str | None
    next_batch_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_checkpoint": self.has_checkpoint,
            "completed_phases": self.completed_phases,
            "completed_batch_ids": sorted(self.completed_batch_ids),
            "next_phase": self.next_phase,
            "next_batch_id": self.next_batch_id,
        }


@dataclass
class MergedResults:
    """Results merged from completed and partial runs."""

    findings: list[ConsolidatedFinding] = field(default_factory=list)
    completed_batch_ids: set[str] = field(default_factory=set)
    is_complete: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_count": len(self.findings),
            "completed_batch_ids": sorted(self.completed_batch_ids),
            "is_complete": self.is_complete,
        }


class ResumeController:
    """Controls resume logic for interrupted audit runs.

    Reads progress.json to determine resume point and merges results
    from completed and new phases without duplication.
    """

    def __init__(self, reader: CheckpointReader) -> None:
        self._reader = reader

    def determine_resume_point(
        self,
        all_phases: list[str],
        all_batch_ids: list[str],
    ) -> ResumePoint:
        """Determine where to resume from checkpoint state.

        Args:
            all_phases: Ordered list of all phase names.
            all_batch_ids: Ordered list of all batch IDs.

        Returns:
            ResumePoint indicating where to start.
        """
        state = self._reader.read()

        if state is None:
            return ResumePoint(
                has_checkpoint=False,
                completed_phases=[],
                completed_batch_ids=set(),
                next_phase=all_phases[0] if all_phases else None,
                next_batch_id=all_batch_ids[0] if all_batch_ids else None,
            )

        completed_ids = self._reader.completed_batch_ids()

        # Determine completed phases (all batches for that phase completed)
        # Phase is completed when all its batches are in completed_ids
        # For simplicity, we track batch-level resume
        next_batch = None
        for bid in all_batch_ids:
            if bid not in completed_ids:
                next_batch = bid
                break

        # Determine completed phases by checking phase-prefixed batches
        completed_phases: list[str] = []
        for phase in all_phases:
            phase_batches = [b for b in all_batch_ids if b.startswith(phase)]
            if phase_batches and all(b in completed_ids for b in phase_batches):
                completed_phases.append(phase)

        next_phase = None
        for phase in all_phases:
            if phase not in completed_phases:
                next_phase = phase
                break

        return ResumePoint(
            has_checkpoint=True,
            completed_phases=completed_phases,
            completed_batch_ids=completed_ids,
            next_phase=next_phase,
            next_batch_id=next_batch,
        )

    def should_skip_batch(self, batch_id: str) -> bool:
        """Check if a batch should be skipped (already completed)."""
        return batch_id in self._reader.completed_batch_ids()

    def merge_results(
        self,
        previous_findings: list[ConsolidatedFinding],
        new_findings: list[ConsolidatedFinding],
    ) -> MergedResults:
        """Merge previous and new findings without duplication.

        Uses file_path as dedup key. New findings take precedence
        over previous findings for the same file.

        Args:
            previous_findings: Findings from completed phases.
            new_findings: Findings from the resumed phase.

        Returns:
            MergedResults with deduplicated findings.
        """
        by_path: dict[str, ConsolidatedFinding] = {}

        # Add previous findings first
        for f in previous_findings:
            by_path[f.file_path] = f

        # New findings overwrite previous (take precedence)
        for f in new_findings:
            by_path[f.file_path] = f

        return MergedResults(
            findings=sorted(by_path.values(), key=lambda f: f.file_path),
            completed_batch_ids=self._reader.completed_batch_ids(),
        )
