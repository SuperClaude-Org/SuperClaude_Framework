"""Monorepo-aware batch decomposition with segment isolation.

Implements AC20 (supporting): batch decomposition that respects monorepo
segment boundaries for isolated analysis.

Detects monorepo segments via workspace config files (package.json, Cargo.toml,
go.mod) at directory roots. Creates isolated batches per segment with
configurable batch size limits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from .profiler import FileProfile

# Workspace config files that indicate a monorepo segment root
_SEGMENT_MARKERS: frozenset[str] = frozenset({
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pyproject.toml",
    "setup.py",
    "pom.xml",
    "build.gradle",
})

# Common monorepo root directories
_MONOREPO_ROOTS: frozenset[str] = frozenset({
    "packages",
    "apps",
    "services",
    "modules",
    "libs",
    "crates",
})

DEFAULT_BATCH_SIZE = 50


@dataclass
class Batch:
    """A single batch of files within one segment."""

    batch_id: str
    segment: str
    files: list[str] = field(default_factory=list)
    estimated_tokens: int = 0

    @property
    def file_count(self) -> int:
        return len(self.files)

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "segment": self.segment,
            "file_count": self.file_count,
            "estimated_tokens": self.estimated_tokens,
            "files": self.files,
        }


@dataclass
class DecompositionManifest:
    """Manifest describing all batches for a repository."""

    batches: list[Batch] = field(default_factory=list)
    segments_detected: list[str] = field(default_factory=list)
    total_files: int = 0
    max_batch_size: int = DEFAULT_BATCH_SIZE

    @property
    def batch_count(self) -> int:
        return len(self.batches)

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_count": self.batch_count,
            "total_files": self.total_files,
            "max_batch_size": self.max_batch_size,
            "segments_detected": self.segments_detected,
            "batches": [b.to_dict() for b in self.batches],
        }


def detect_segments(file_paths: list[str]) -> dict[str, list[str]]:
    """Detect monorepo segments from file paths.

    A segment is identified by:
    1. A directory under a monorepo root (packages/, apps/, services/, etc.)
       that contains a workspace config file.
    2. Files not under any segment root belong to the "__root__" segment.

    Returns mapping of segment_name -> list of file paths.
    """
    segments: dict[str, list[str]] = {}
    marker_dirs: set[str] = set()

    # First pass: find directories containing workspace markers
    for fp in file_paths:
        parts = PurePosixPath(fp.replace("\\", "/")).parts
        basename = parts[-1] if parts else ""
        if basename in _SEGMENT_MARKERS and len(parts) >= 2:
            # The parent directory of the marker is a potential segment
            parent = str(PurePosixPath(*parts[:-1]))
            # Check if it's under a monorepo root
            if len(parts) >= 3 and parts[0].lower() in _MONOREPO_ROOTS:
                marker_dirs.add(parent)

    # Second pass: assign files to segments
    for fp in file_paths:
        normalized = fp.replace("\\", "/")
        assigned = False

        for seg_dir in sorted(marker_dirs):
            if normalized.startswith(seg_dir + "/") or normalized == seg_dir:
                segments.setdefault(seg_dir, []).append(fp)
                assigned = True
                break

        if not assigned:
            # Fallback: group by top-level monorepo root directory
            parts = PurePosixPath(normalized).parts
            if len(parts) >= 2 and parts[0].lower() in _MONOREPO_ROOTS:
                seg_key = str(PurePosixPath(parts[0], parts[1]))
                segments.setdefault(seg_key, []).append(fp)
            else:
                segments.setdefault("__root__", []).append(fp)

    return segments


def _estimate_tokens(file_path: str, file_sizes: dict[str, int] | None = None) -> int:
    """Estimate token count for a file. Rough: ~4 chars per token."""
    if file_sizes and file_path in file_sizes:
        return file_sizes[file_path] // 4
    return 500  # Default estimate


def decompose(
    file_paths: list[str],
    *,
    max_batch_size: int = DEFAULT_BATCH_SIZE,
    file_sizes: dict[str, int] | None = None,
) -> DecompositionManifest:
    """Decompose files into segment-isolated batches.

    No batch contains files from different monorepo segments.
    Batch sizes respect the configured maximum.

    Args:
        file_paths: All file paths to decompose.
        max_batch_size: Maximum files per batch.
        file_sizes: Optional file_path -> size mapping for token estimation.

    Returns:
        DecompositionManifest with isolated batches and metadata.
    """
    segments = detect_segments(file_paths)
    manifest = DecompositionManifest(
        segments_detected=sorted(segments.keys()),
        total_files=len(file_paths),
        max_batch_size=max_batch_size,
    )

    batch_counter = 0
    for segment_name in sorted(segments.keys()):
        seg_files = segments[segment_name]

        # Split into batches respecting max size
        for i in range(0, len(seg_files), max_batch_size):
            chunk = seg_files[i : i + max_batch_size]
            batch_counter += 1
            batch = Batch(
                batch_id=f"B-{batch_counter:04d}",
                segment=segment_name,
                files=chunk,
                estimated_tokens=sum(
                    _estimate_tokens(f, file_sizes) for f in chunk
                ),
            )
            manifest.batches.append(batch)

    return manifest
