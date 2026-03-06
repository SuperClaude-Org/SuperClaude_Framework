"""Tests for resume semantics (T04.11 / D-0037)."""

import json
import pytest
from pathlib import Path

from superclaude.cli.audit.checkpoint import (
    BatchStatus,
    CheckpointReader,
    CheckpointState,
    CheckpointWriter,
)
from superclaude.cli.audit.classification import V2Action, V2Tier
from superclaude.cli.audit.consolidation import ConsolidatedFinding
from superclaude.cli.audit.resume import MergedResults, ResumeController, ResumePoint


def _make_finding(path: str) -> ConsolidatedFinding:
    return ConsolidatedFinding(
        file_path=path,
        tier=V2Tier.TIER_2,
        action=V2Action.KEEP,
        confidence=0.85,
        evidence=["ev"],
        source_phases=["surface"],
    )


def _write_checkpoint(path: Path, completed_ids: list[str]) -> None:
    """Write a checkpoint with specified completed batch IDs."""
    state = CheckpointState(
        run_id="test-run",
        total_batches=5,
        batches=[
            BatchStatus(batch_id=bid, status="COMPLETED", files_processed=10)
            for bid in completed_ids
        ],
    )
    writer = CheckpointWriter(path)
    writer.write(state)


class TestResumePoint:
    """Verify resume point determination."""

    def test_no_checkpoint(self, tmp_path: Path):
        """Without checkpoint, resume from beginning."""
        reader = CheckpointReader(tmp_path / "progress.json")
        ctrl = ResumeController(reader)
        point = ctrl.determine_resume_point(
            ["phase1", "phase2"], ["B-0001", "B-0002"]
        )
        assert not point.has_checkpoint
        assert point.next_phase == "phase1"
        assert point.next_batch_id == "B-0001"

    def test_partial_checkpoint(self, tmp_path: Path):
        """With partial checkpoint, resume from next pending batch."""
        progress = tmp_path / "progress.json"
        _write_checkpoint(progress, ["B-0001", "B-0002"])
        reader = CheckpointReader(progress)
        ctrl = ResumeController(reader)
        point = ctrl.determine_resume_point(
            ["phase1", "phase2"],
            ["B-0001", "B-0002", "B-0003", "B-0004"],
        )
        assert point.has_checkpoint
        assert point.next_batch_id == "B-0003"
        assert "B-0001" in point.completed_batch_ids
        assert "B-0002" in point.completed_batch_ids

    def test_should_skip_completed(self, tmp_path: Path):
        """Completed batches are skipped."""
        progress = tmp_path / "progress.json"
        _write_checkpoint(progress, ["B-0001"])
        reader = CheckpointReader(progress)
        ctrl = ResumeController(reader)
        assert ctrl.should_skip_batch("B-0001")
        assert not ctrl.should_skip_batch("B-0002")


class TestMergeResults:
    """Verify result merging without duplication."""

    def test_no_duplicates(self, tmp_path: Path):
        """Merged results have no duplicate file entries."""
        progress = tmp_path / "progress.json"
        _write_checkpoint(progress, [])
        reader = CheckpointReader(progress)
        ctrl = ResumeController(reader)

        prev = [_make_finding("a.py"), _make_finding("b.py")]
        new = [_make_finding("b.py"), _make_finding("c.py")]
        merged = ctrl.merge_results(prev, new)

        paths = [f.file_path for f in merged.findings]
        assert len(paths) == len(set(paths))
        assert set(paths) == {"a.py", "b.py", "c.py"}

    def test_new_findings_take_precedence(self, tmp_path: Path):
        """New findings overwrite previous for same file."""
        progress = tmp_path / "progress.json"
        _write_checkpoint(progress, [])
        reader = CheckpointReader(progress)
        ctrl = ResumeController(reader)

        prev_finding = ConsolidatedFinding(
            file_path="a.py", tier=V2Tier.TIER_1, action=V2Action.DELETE,
            confidence=0.70, evidence=["old"], source_phases=["surface"],
        )
        new_finding = ConsolidatedFinding(
            file_path="a.py", tier=V2Tier.TIER_2, action=V2Action.KEEP,
            confidence=0.90, evidence=["new"], source_phases=["structural"],
        )
        merged = ctrl.merge_results([prev_finding], [new_finding])
        a = [f for f in merged.findings if f.file_path == "a.py"][0]
        assert a.action == V2Action.KEEP
        assert a.confidence == 0.90

    def test_empty_merge(self, tmp_path: Path):
        """Empty inputs produce empty merge."""
        progress = tmp_path / "progress.json"
        _write_checkpoint(progress, [])
        reader = CheckpointReader(progress)
        ctrl = ResumeController(reader)
        merged = ctrl.merge_results([], [])
        assert len(merged.findings) == 0

    def test_serialization(self, tmp_path: Path):
        """MergedResults serializes to dict."""
        progress = tmp_path / "progress.json"
        _write_checkpoint(progress, [])
        reader = CheckpointReader(progress)
        ctrl = ResumeController(reader)
        merged = ctrl.merge_results([_make_finding("a.py")], [])
        d = merged.to_dict()
        assert d["finding_count"] == 1
