"""Concurrent-run isolation tests (T05.07 / D-0046).

Validates that two audit runs on the same repository produce
independent outputs with no cross-contamination.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.audit.batch_decomposer import decompose
from superclaude.cli.audit.checkpoint import (
    BatchStatus, CheckpointState, CheckpointWriter, CheckpointReader,
)
from superclaude.cli.audit.known_issues import (
    KnownIssuesRegistry, RegistryEntry, save_registry, load_registry,
)
from superclaude.cli.audit.tool_orchestrator import ResultCache


def _run_id(n: int) -> str:
    return f"run-{n:03d}"


class TestProgressIsolation:
    """progress.json files are independently maintained per run."""

    def test_separate_progress_files(self, tmp_path):
        run1_dir = tmp_path / "run1"
        run2_dir = tmp_path / "run2"
        run1_dir.mkdir()
        run2_dir.mkdir()

        state1 = CheckpointState(
            run_id=_run_id(1),
            total_batches=3,
            batches=[
                BatchStatus(batch_id="b1-001", status="COMPLETED", files_processed=10),
            ],
        )
        state2 = CheckpointState(
            run_id=_run_id(2),
            total_batches=3,
            batches=[
                BatchStatus(batch_id="b2-001", status="COMPLETED", files_processed=15),
            ],
        )

        writer1 = CheckpointWriter(run1_dir / "progress.json")
        writer2 = CheckpointWriter(run2_dir / "progress.json")
        writer1.write(state1)
        writer2.write(state2)

        reader1 = CheckpointReader(run1_dir / "progress.json")
        reader2 = CheckpointReader(run2_dir / "progress.json")
        r1_state = reader1.read()
        r2_state = reader2.read()

        assert r1_state.run_id == _run_id(1)
        assert r2_state.run_id == _run_id(2)
        assert "b1-001" in reader1.completed_batch_ids()
        assert "b2-001" in reader2.completed_batch_ids()
        # No cross-contamination
        assert "b2-001" not in reader1.completed_batch_ids()
        assert "b1-001" not in reader2.completed_batch_ids()

    def test_concurrent_checkpoint_writes(self, tmp_path):
        """Two threads write checkpoints simultaneously without corruption."""
        errors = []

        def write_checkpoint(run_dir: Path, run_id: str, batch_id: str):
            try:
                run_dir.mkdir(parents=True, exist_ok=True)
                state = CheckpointState(
                    run_id=run_id,
                    total_batches=1,
                    batches=[
                        BatchStatus(batch_id=batch_id, status="COMPLETED", files_processed=5),
                    ],
                )
                writer = CheckpointWriter(run_dir / "progress.json")
                writer.write(state)
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(
            target=write_checkpoint,
            args=(tmp_path / "run1", "run-001", "b1-001"),
        )
        t2 = threading.Thread(
            target=write_checkpoint,
            args=(tmp_path / "run2", "run-002", "b2-001"),
        )
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert not errors, f"Thread errors: {errors}"

        r1 = CheckpointReader(tmp_path / "run1" / "progress.json").read()
        r2 = CheckpointReader(tmp_path / "run2" / "progress.json").read()
        assert r1.run_id == "run-001"
        assert r2.run_id == "run-002"


class TestCacheIsolation:
    """Cache entries are namespaced per run."""

    def test_separate_caches(self):
        cache1 = ResultCache()
        cache2 = ResultCache()

        from superclaude.cli.audit.tool_orchestrator import FileAnalysis

        fa1 = FileAnalysis(file_path="a.py", content_hash="hash1", exports=["run1"])
        fa2 = FileAnalysis(file_path="a.py", content_hash="hash1", exports=["run2"])

        cache1.put("hash1", fa1)
        cache2.put("hash1", fa2)

        assert cache1.get("hash1").exports == ["run1"]
        assert cache2.get("hash1").exports == ["run2"]

    def test_cache_stats_independent(self):
        cache1 = ResultCache()
        cache2 = ResultCache()

        from superclaude.cli.audit.tool_orchestrator import FileAnalysis

        fa = FileAnalysis(file_path="a.py", content_hash="h1")
        cache1.put("h1", fa)
        cache1.get("h1")     # hit
        cache2.get("h1")     # miss

        stats1 = cache1.stats
        stats2 = cache2.stats
        assert stats1.hits == 1
        assert stats2.misses == 1


class TestRegistryIsolation:
    """Known-issues registries are independent per run."""

    def test_registries_on_separate_paths(self, tmp_path):
        reg1 = KnownIssuesRegistry(entries=[
            RegistryEntry("KI-R1", "src/*.py", "DELETE", "2026-01-01"),
        ])
        reg2 = KnownIssuesRegistry(entries=[
            RegistryEntry("KI-R2", "lib/*.js", "KEEP", "2026-01-01"),
        ])

        path1 = tmp_path / "run1" / "registry.json"
        path2 = tmp_path / "run2" / "registry.json"
        save_registry(reg1, path1)
        save_registry(reg2, path2)

        loaded1 = load_registry(path1)
        loaded2 = load_registry(path2)

        assert loaded1.entries[0].issue_id == "KI-R1"
        assert loaded2.entries[0].issue_id == "KI-R2"

    def test_match_does_not_cross_registries(self, tmp_path):
        reg1 = KnownIssuesRegistry(entries=[
            RegistryEntry("KI-R1", "src/*.py", "DELETE", "2026-01-01"),
        ])
        reg2 = KnownIssuesRegistry()

        m1 = reg1.match_finding("src/old.py", "DELETE")
        m2 = reg2.match_finding("src/old.py", "DELETE")

        assert m1.matched is True
        assert m2.matched is False


class TestOutputIsolation:
    """Concurrent runs produce identical output to sequential runs."""

    def test_decomposition_deterministic(self):
        files = [f"src/file_{i}.py" for i in range(20)]

        manifest1 = decompose(file_paths=files, max_batch_size=10)
        manifest2 = decompose(file_paths=files, max_batch_size=10)

        ids1 = [b.batch_id for b in manifest1.batches]
        ids2 = [b.batch_id for b in manifest2.batches]
        assert ids1 == ids2

    def test_batch_ids_unique_within_run(self):
        files = [f"src/file_{i}.py" for i in range(50)]
        manifest = decompose(file_paths=files, max_batch_size=10)
        ids = [b.batch_id for b in manifest.batches]
        assert len(ids) == len(set(ids)), "Batch IDs must be unique"
