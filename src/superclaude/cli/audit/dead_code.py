"""Cross-boundary dead code candidate detection.

Implements T03.07 / D-0023: identifies exported symbols with zero
cross-boundary importers using the 3-tier dependency graph.

Exclusion rules: entry points, framework hooks, dynamic imports.
Each candidate includes evidence (export location, boundary search scope).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from .dependency_graph import DependencyGraph, EdgeTier
from .tool_orchestrator import FileAnalysis


# Default entry point patterns
_ENTRY_POINT_PATTERNS: list[str] = [
    "__main__", "main.py", "cli.py", "app.py", "wsgi.py",
    "asgi.py", "manage.py", "setup.py", "conftest.py",
    "__init__.py", "index.js", "index.ts", "server.js", "server.ts",
]

# Framework hook patterns (exports used by frameworks, not direct imports)
_FRAMEWORK_HOOK_PATTERNS: list[str] = [
    "pytest_", "conftest", "plugin", "middleware",
    "migration", "fixture", "hook", "signal",
    "celery", "task", "command", "admin",
]


@dataclass
class DeadCodeCandidate:
    """A dead code candidate with evidence."""

    file_path: str
    export_location: str  # what is exported
    boundary_search_scope: str  # what boundaries were searched
    tier_a_importers: int
    tier_b_importers: int
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "export_location": self.export_location,
            "boundary_search_scope": self.boundary_search_scope,
            "tier_a_importers": self.tier_a_importers,
            "tier_b_importers": self.tier_b_importers,
            "reason": self.reason,
        }


@dataclass
class ExcludedCandidate:
    """A file excluded from dead code candidates with reason."""

    file_path: str
    exclusion_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "exclusion_reason": self.exclusion_reason,
        }


@dataclass
class DeadCodeReport:
    """Report of dead code detection."""

    candidates: list[DeadCodeCandidate] = field(default_factory=list)
    excluded: list[ExcludedCandidate] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "excluded": [e.to_dict() for e in self.excluded],
            "candidate_count": len(self.candidates),
            "excluded_count": len(self.excluded),
        }


def _is_entry_point(file_path: str) -> bool:
    """Check if file is an entry point."""
    base = os.path.basename(file_path).lower()
    return any(pat in base for pat in _ENTRY_POINT_PATTERNS)


def _is_framework_hook(file_path: str, analysis: FileAnalysis) -> bool:
    """Check if file contains framework hooks."""
    base = os.path.basename(file_path).lower()
    if any(pat in base for pat in _FRAMEWORK_HOOK_PATTERNS):
        return True

    # Check exports for hook patterns
    for exp in analysis.exports:
        exp_lower = exp.lower()
        if any(pat in exp_lower for pat in _FRAMEWORK_HOOK_PATTERNS):
            return True

    return False


def detect_dead_code(
    graph: DependencyGraph,
    analyses: dict[str, FileAnalysis],
    entry_points: list[str] | None = None,
) -> DeadCodeReport:
    """Detect dead code candidates using the dependency graph.

    A dead code candidate is a file with exports that has:
    - 0 Tier-A importers across all module boundaries
    - 0 Tier-B references across all module boundaries
    - Is not an entry point or framework hook

    Args:
        graph: 3-tier dependency graph.
        analyses: File analyses with export information.
        entry_points: Additional entry point file paths.

    Returns:
        DeadCodeReport with candidates and exclusions.
    """
    report = DeadCodeReport()
    extra_entries = set(entry_points or [])

    for file_path, analysis in analyses.items():
        # Only consider files with exports
        if not analysis.exports:
            continue

        # Exclusion: entry points
        if _is_entry_point(file_path) or file_path in extra_entries:
            report.excluded.append(ExcludedCandidate(
                file_path=file_path,
                exclusion_reason="entry_point",
            ))
            continue

        # Exclusion: framework hooks
        if _is_framework_hook(file_path, analysis):
            report.excluded.append(ExcludedCandidate(
                file_path=file_path,
                exclusion_reason="framework_hook",
            ))
            continue

        # Check importers
        tier_a = graph.tier_a_importers_of(file_path)
        tier_b = graph.tier_b_importers_of(file_path)

        if len(tier_a) == 0 and len(tier_b) == 0:
            exports_str = "; ".join(analysis.exports[:3])
            report.candidates.append(DeadCodeCandidate(
                file_path=file_path,
                export_location=exports_str,
                boundary_search_scope=f"all {len(analyses)} files",
                tier_a_importers=0,
                tier_b_importers=0,
                reason="Zero Tier-A importers and zero Tier-B references",
            ))

    return report
