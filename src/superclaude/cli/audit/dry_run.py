"""Dry-run mode that outputs profile and token estimates without executing audit.

Implements AC19: dry-run mode returns estimates only, enabling operators
to assess cost before committing to a full run.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .batch_decomposer import DecompositionManifest, decompose
from .profiler import ProfileReport, profile_repository


@dataclass
class DryRunEstimate:
    """Dry-run output with estimates and no analysis artifacts."""

    file_count: int
    batch_count: int
    estimated_tokens: int
    estimated_runtime_seconds: float
    domain_distribution: dict[str, int]
    risk_distribution: dict[str, int]
    segments_detected: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_count": self.file_count,
            "batch_count": self.batch_count,
            "estimated_tokens": self.estimated_tokens,
            "estimated_runtime_seconds": round(self.estimated_runtime_seconds, 2),
            "domain_distribution": self.domain_distribution,
            "risk_distribution": self.risk_distribution,
            "segments_detected": self.segments_detected,
        }


# Average tokens per file for estimation (rough heuristic)
_AVG_TOKENS_PER_FILE = 500
# Seconds per batch for runtime estimation
_SECONDS_PER_BATCH = 5.0


def dry_run(
    file_paths: list[str],
    *,
    file_sizes: dict[str, int] | None = None,
    max_batch_size: int = 50,
) -> DryRunEstimate:
    """Execute profiling + batch planning only. No analysis.

    Returns estimated token cost, batch count, and expected runtime
    without producing any classification output.

    Args:
        file_paths: All repository file paths.
        file_sizes: Optional file_path -> size mapping.
        max_batch_size: Maximum files per batch.

    Returns:
        DryRunEstimate with cost projections.
    """
    # Phase 0: Profile
    profile = profile_repository(file_paths, file_sizes=file_sizes)

    # Phase 0: Batch plan
    manifest = decompose(
        file_paths,
        max_batch_size=max_batch_size,
        file_sizes=file_sizes,
    )

    # Estimate tokens from batch metadata
    total_tokens = sum(b.estimated_tokens for b in manifest.batches)
    if total_tokens == 0:
        total_tokens = len(file_paths) * _AVG_TOKENS_PER_FILE

    # Estimate runtime
    runtime = manifest.batch_count * _SECONDS_PER_BATCH

    return DryRunEstimate(
        file_count=len(file_paths),
        batch_count=manifest.batch_count,
        estimated_tokens=total_tokens,
        estimated_runtime_seconds=runtime,
        domain_distribution=profile.domain_distribution,
        risk_distribution=profile.risk_distribution,
        segments_detected=manifest.segments_detected,
    )
