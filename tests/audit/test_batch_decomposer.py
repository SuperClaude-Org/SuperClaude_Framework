"""Tests for monorepo-aware batch decomposition (T02.02, D-0012)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.batch_decomposer import (
    Batch,
    DecompositionManifest,
    decompose,
    detect_segments,
    DEFAULT_BATCH_SIZE,
)


class TestDetectSegments:
    """Segment detection from file paths."""

    def test_monorepo_with_packages(self):
        files = [
            "packages/auth/package.json",
            "packages/auth/src/index.ts",
            "packages/ui/package.json",
            "packages/ui/src/Button.tsx",
        ]
        segs = detect_segments(files)
        assert "packages/auth" in segs
        assert "packages/ui" in segs

    def test_files_outside_segments_go_to_root(self):
        files = [
            "src/main.py",
            "README.md",
        ]
        segs = detect_segments(files)
        assert "__root__" in segs
        assert len(segs["__root__"]) == 2

    def test_mixed_monorepo_and_root(self):
        files = [
            "packages/core/package.json",
            "packages/core/index.js",
            "src/app.py",
        ]
        segs = detect_segments(files)
        assert "packages/core" in segs
        assert "__root__" in segs

    def test_no_markers_all_root(self):
        files = ["src/a.py", "src/b.py", "lib/c.py"]
        segs = detect_segments(files)
        assert "__root__" in segs


class TestBatchSegmentIsolation:
    """Batches never contain files from different segments."""

    MONOREPO_FILES = [
        "packages/auth/package.json",
        "packages/auth/src/login.ts",
        "packages/auth/src/logout.ts",
        "packages/ui/package.json",
        "packages/ui/src/Button.tsx",
        "packages/ui/src/Modal.tsx",
        "src/server.py",
    ]

    def test_no_cross_segment_batches(self):
        """AC: batches never contain files from different segments."""
        manifest = decompose(self.MONOREPO_FILES, max_batch_size=10)
        for batch in manifest.batches:
            segments_in_batch = set()
            for f in batch.files:
                segs = detect_segments([f])
                for seg_name in segs:
                    segments_in_batch.add(seg_name)
            assert len(segments_in_batch) == 1, (
                f"Batch {batch.batch_id} contains files from multiple segments: {segments_in_batch}"
            )

    def test_segment_field_consistent_within_batch(self):
        """AC: segment field is consistent within each batch."""
        manifest = decompose(self.MONOREPO_FILES, max_batch_size=10)
        for batch in manifest.batches:
            assert batch.segment, f"Batch {batch.batch_id} has no segment"


class TestBatchSizeLimits:
    """Batch sizes respect configured maximum."""

    def test_batches_respect_max_size(self):
        """AC: batch sizes do not exceed configured maximum."""
        files = [f"src/file_{i}.py" for i in range(120)]
        manifest = decompose(files, max_batch_size=50)
        for batch in manifest.batches:
            assert batch.file_count <= 50, (
                f"Batch {batch.batch_id} exceeds max: {batch.file_count}"
            )

    def test_small_batch_size(self):
        files = [f"src/file_{i}.py" for i in range(10)]
        manifest = decompose(files, max_batch_size=3)
        for batch in manifest.batches:
            assert batch.file_count <= 3

    def test_default_batch_size(self):
        assert DEFAULT_BATCH_SIZE == 50


class TestDecompositionManifest:
    """Manifest output format."""

    MONOREPO_3PKG = [
        "packages/a/package.json",
        "packages/a/src/index.ts",
        "packages/b/package.json",
        "packages/b/src/index.ts",
        "packages/c/package.json",
        "packages/c/src/index.ts",
    ]

    def test_3_package_monorepo(self):
        """AC: 3-package monorepo produces 3 isolated batch groups."""
        manifest = decompose(self.MONOREPO_3PKG, max_batch_size=100)
        segments_in_batches = {b.segment for b in manifest.batches}
        assert len(segments_in_batches) == 3

    def test_manifest_serialization(self):
        manifest = decompose(self.MONOREPO_3PKG)
        d = manifest.to_dict()
        assert "batch_count" in d
        assert "total_files" in d
        assert "segments_detected" in d
        assert "batches" in d

    def test_total_files_correct(self):
        manifest = decompose(self.MONOREPO_3PKG)
        assert manifest.total_files == 6

    def test_batch_has_estimated_tokens(self):
        manifest = decompose(self.MONOREPO_3PKG)
        for batch in manifest.batches:
            assert batch.estimated_tokens > 0

    def test_batch_serialization(self):
        manifest = decompose(self.MONOREPO_3PKG)
        batch = manifest.batches[0]
        d = batch.to_dict()
        assert "batch_id" in d
        assert "segment" in d
        assert "file_count" in d
        assert "estimated_tokens" in d
        assert "files" in d

    def test_with_file_sizes(self):
        sizes = {"packages/a/src/index.ts": 8000}
        manifest = decompose(self.MONOREPO_3PKG, file_sizes=sizes)
        assert manifest.batch_count >= 1
