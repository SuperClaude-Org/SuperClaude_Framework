"""8-field profile generator for targeted file sets.

Implements T03.01 / D-0017: computes all 8 Phase-2 profile fields per file:
  imports, exports, size, complexity, age, churn, coupling, test_coverage

Data sources:
  - imports: from ToolOrchestrator static analysis (AST/line-based)
  - exports: from ToolOrchestrator static analysis
  - size: file stat (line count)
  - complexity: cyclomatic approximation (branch-counting heuristic)
  - age: git log --follow first commit date (ISO string)
  - churn: git log commit count
  - coupling: import graph in-degree from analysis cache
  - test_coverage: test file matching heuristic (None if no match found)

Deterministic: same file state produces identical profile across runs.
Leverages cached static-tool results from ToolOrchestrator (T02.03).
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Any

from .scanner_schema import PHASE2_PROFILE_FIELDS, validate_phase2
from .tool_orchestrator import FileAnalysis, ResultCache, ToolOrchestrator


# Complexity-counting patterns (branch keywords)
_BRANCH_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^\s*if\b"),
    re.compile(r"^\s*elif\b"),
    re.compile(r"^\s*else\b"),
    re.compile(r"^\s*for\b"),
    re.compile(r"^\s*while\b"),
    re.compile(r"^\s*except\b"),
    re.compile(r"^\s*case\b"),
    re.compile(r"^\s*catch\b"),
    re.compile(r"\bif\s*\("),  # JS/TS inline if
    re.compile(r"\belse\s+if\b"),
    re.compile(r"\?\s*"),  # ternary (rough)
]


@dataclass
class FullFileProfile:
    """8-field profile for a single file."""

    file_path: str
    imports: list[str]
    exports: list[str]
    size: int  # line count
    complexity: float  # cyclomatic approximation
    age: str  # ISO date of first commit
    churn: int  # total commit count
    coupling: float  # import in-degree ratio
    test_coverage: float | None  # None if no test file matched

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "imports": self.imports,
            "exports": self.exports,
            "size": self.size,
            "complexity": self.complexity,
            "age": self.age,
            "churn": self.churn,
            "coupling": self.coupling,
            "test_coverage": self.test_coverage,
        }

    def to_schema_dict(self) -> dict[str, Any]:
        """Return dict matching Phase-2 scanner schema (includes Phase-1 stubs)."""
        return {
            "file_path": self.file_path,
            "classification": "PROFILE",
            "evidence": [],
            "confidence": 1.0,
            "tier": "phase-2",
            "imports": self.imports,
            "exports": self.exports,
            "size": self.size,
            "complexity": self.complexity,
            "age": self.age,
            "churn": self.churn,
            "coupling": self.coupling,
            "test_coverage": self.test_coverage,
        }


def compute_complexity(content: str) -> float:
    """Approximate cyclomatic complexity by counting branch keywords.

    Returns a float >= 1.0 (base complexity of 1 + branch count).
    """
    count = 0
    for line in content.splitlines():
        for pat in _BRANCH_PATTERNS:
            if pat.search(line):
                count += 1
                break  # one match per line is enough
    return 1.0 + count


def _git_file_age(file_path: str, repo_root: str) -> str:
    """Get ISO date of first commit for a file using git log --follow.

    Returns ISO date string or "unknown" if git is unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "log", "--follow", "--diff-filter=A",
             "--format=%aI", "--", file_path],
            capture_output=True, text=True, cwd=repo_root, timeout=10,
        )
        dates = result.stdout.strip().splitlines()
        if dates:
            return dates[-1]  # earliest (last in output)
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return "unknown"


def _git_file_churn(file_path: str, repo_root: str) -> int:
    """Count total commits touching a file.

    Returns 0 if git is unavailable.
    """
    try:
        result = subprocess.run(
            ["git", "log", "--follow", "--oneline", "--", file_path],
            capture_output=True, text=True, cwd=repo_root, timeout=10,
        )
        return len(result.stdout.strip().splitlines())
    except (subprocess.SubprocessError, FileNotFoundError):
        return 0


def _compute_coupling(
    file_path: str,
    all_analyses: dict[str, FileAnalysis],
) -> float:
    """Compute import in-degree: how many other files import this file.

    Returns ratio: importers / total_files (0.0 to 1.0).
    """
    total = len(all_analyses)
    if total <= 1:
        return 0.0

    # Normalize target for matching
    base_name = os.path.basename(file_path)
    stem = os.path.splitext(base_name)[0]

    importers = 0
    for other_path, analysis in all_analyses.items():
        if other_path == file_path:
            continue
        for imp in analysis.imports:
            if stem in imp or base_name in imp:
                importers += 1
                break

    return round(importers / (total - 1), 4)


def _find_test_coverage(file_path: str, all_files: list[str]) -> float | None:
    """Heuristic test coverage: check if a matching test file exists.

    Returns 1.0 if test file found, 0.0 if no test file found,
    None for non-source files.
    """
    # Only compute for source files
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in {".py", ".js", ".ts", ".jsx", ".tsx", ".vue"}:
        return None

    base = os.path.basename(file_path)
    stem = os.path.splitext(base)[0]

    # Test file naming conventions
    test_patterns = [
        f"test_{stem}",
        f"{stem}_test",
        f"{stem}.test",
        f"{stem}.spec",
    ]

    for other in all_files:
        other_base = os.path.basename(other).lower()
        other_stem = os.path.splitext(other_base)[0]
        for pat in test_patterns:
            if other_stem == pat.lower():
                return 1.0

    return 0.0


class ProfileGenerator:
    """Generates 8-field profiles for targeted file sets.

    Leverages ToolOrchestrator cache for import/export data.
    Uses git for age/churn. Computes complexity from content.
    """

    def __init__(
        self,
        orchestrator: ToolOrchestrator | None = None,
        repo_root: str = ".",
    ) -> None:
        self._orchestrator = orchestrator or ToolOrchestrator()
        self._repo_root = repo_root

    @property
    def orchestrator(self) -> ToolOrchestrator:
        return self._orchestrator

    def profile_file(
        self,
        file_path: str,
        content: str,
        all_analyses: dict[str, FileAnalysis] | None = None,
        all_files: list[str] | None = None,
    ) -> FullFileProfile:
        """Generate 8-field profile for a single file."""
        # Get static analysis (uses cache)
        analysis = self._orchestrator.analyze_file(file_path, content)

        lines = content.splitlines()

        return FullFileProfile(
            file_path=file_path,
            imports=analysis.imports,
            exports=analysis.exports,
            size=len(lines),
            complexity=compute_complexity(content),
            age=_git_file_age(file_path, self._repo_root),
            churn=_git_file_churn(file_path, self._repo_root),
            coupling=_compute_coupling(
                file_path, all_analyses or {},
            ),
            test_coverage=_find_test_coverage(
                file_path, all_files or [],
            ),
        )

    def profile_batch(
        self,
        files: dict[str, str],
    ) -> list[FullFileProfile]:
        """Generate 8-field profiles for a batch of files.

        Args:
            files: Mapping of file_path -> content.

        Returns:
            List of FullFileProfile, one per file.
            All 8 fields are populated with non-null values
            (test_coverage may be None for non-source files).
        """
        # First pass: get all static analyses
        analyses: dict[str, FileAnalysis] = {}
        for path, content in files.items():
            analyses[path] = self._orchestrator.analyze_file(path, content)

        all_paths = list(files.keys())

        # Second pass: compute full profiles
        profiles = []
        for path, content in files.items():
            profile = self.profile_file(
                path, content,
                all_analyses=analyses,
                all_files=all_paths,
            )
            profiles.append(profile)

        return profiles

    def validate_profiles(
        self, profiles: list[FullFileProfile],
    ) -> list[dict[str, Any]]:
        """Validate all profiles against Phase-2 schema.

        Returns list of validation results (one per profile).
        """
        results = []
        for p in profiles:
            schema_dict = p.to_schema_dict()
            validation = validate_phase2(schema_dict)
            results.append(validation.to_dict())
        return results
