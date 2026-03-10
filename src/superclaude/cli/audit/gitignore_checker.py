"""Gitignore inconsistency detection between .gitignore and tracked files.

Implements AC8: flags files tracked by git that match .gitignore patterns,
indicating configuration drift.
"""

from __future__ import annotations

import fnmatch
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GitignoreInconsistency:
    """A file tracked by git that matches a .gitignore pattern."""

    file_path: str
    matching_pattern: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "matching_pattern": self.matching_pattern,
        }


@dataclass
class GitignoreCheckResult:
    """Result of checking for gitignore inconsistencies."""

    inconsistencies: list[GitignoreInconsistency] = field(default_factory=list)
    tracked_file_count: int = 0
    gitignore_pattern_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "inconsistencies": [i.to_dict() for i in self.inconsistencies],
            "tracked_file_count": self.tracked_file_count,
            "gitignore_pattern_count": self.gitignore_pattern_count,
            "inconsistency_count": len(self.inconsistencies),
        }


def parse_gitignore(gitignore_path: Path) -> list[str]:
    """Parse a .gitignore file into a list of patterns.

    Skips blank lines and comments.
    """
    if not gitignore_path.exists():
        return []

    patterns = []
    for line in gitignore_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def get_tracked_files(repo_root: Path) -> list[str]:
    """Get list of files tracked by git."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.splitlines() if f.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _matches_pattern(file_path: str, pattern: str) -> bool:
    """Check if a file path matches a gitignore pattern.

    Handles directory patterns (trailing /) and glob patterns.
    """
    clean = pattern.rstrip("/")

    # Direct match on filename
    filename = file_path.rsplit("/", 1)[-1] if "/" in file_path else file_path
    if fnmatch.fnmatch(filename, clean):
        return True

    # Full path match
    if fnmatch.fnmatch(file_path, clean):
        return True

    # Pattern with ** wildcard
    if "**" in clean:
        parts = clean.split("**")
        if len(parts) == 2 and file_path.startswith(parts[0].rstrip("/")) and file_path.endswith(parts[1].lstrip("/")):
            return True

    # Directory prefix match (e.g., "build/" matches "build/output.js")
    if pattern.endswith("/") and file_path.startswith(clean + "/"):
        return True

    return False


def check_gitignore_consistency(
    repo_root: Path,
    tracked_files: list[str] | None = None,
    gitignore_patterns: list[str] | None = None,
) -> GitignoreCheckResult:
    """Check for inconsistencies between tracked files and .gitignore patterns.

    Args:
        repo_root: Root of the git repository.
        tracked_files: Pre-loaded tracked files (optional, for testing).
        gitignore_patterns: Pre-loaded patterns (optional, for testing).

    Returns:
        GitignoreCheckResult with any inconsistencies found.
    """
    if tracked_files is None:
        tracked_files = get_tracked_files(repo_root)
    if gitignore_patterns is None:
        gitignore_patterns = parse_gitignore(repo_root / ".gitignore")

    result = GitignoreCheckResult(
        tracked_file_count=len(tracked_files),
        gitignore_pattern_count=len(gitignore_patterns),
    )

    for file_path in tracked_files:
        for pattern in gitignore_patterns:
            if _matches_pattern(file_path, pattern):
                result.inconsistencies.append(
                    GitignoreInconsistency(
                        file_path=file_path,
                        matching_pattern=pattern,
                    )
                )
                break  # One match per file is enough

    return result
