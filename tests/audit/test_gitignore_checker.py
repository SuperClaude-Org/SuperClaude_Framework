"""Tests for gitignore inconsistency detection.

Validates AC8: detects files tracked by git that match .gitignore patterns.
"""

from __future__ import annotations

from pathlib import Path

from superclaude.cli.audit.gitignore_checker import (
    check_gitignore_consistency,
    parse_gitignore,
)


class TestParseGitignore:
    def test_parses_patterns(self, tmp_path: Path):
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n# comment\n\n.env\n")
        patterns = parse_gitignore(gitignore)
        assert patterns == ["*.pyc", "__pycache__/", ".env"]

    def test_no_gitignore_returns_empty(self, tmp_path: Path):
        patterns = parse_gitignore(tmp_path / ".gitignore")
        assert patterns == []


class TestCheckConsistency:
    def test_detects_inconsistencies(self, tmp_path: Path):
        tracked = ["src/main.py", "build/output.js", ".env", "README.md"]
        patterns = ["build/", ".env"]

        result = check_gitignore_consistency(
            tmp_path, tracked_files=tracked, gitignore_patterns=patterns
        )
        assert len(result.inconsistencies) == 2

        paths = {i.file_path for i in result.inconsistencies}
        assert "build/output.js" in paths
        assert ".env" in paths

    def test_no_inconsistencies(self, tmp_path: Path):
        tracked = ["src/main.py", "README.md"]
        patterns = ["*.pyc", "node_modules/"]

        result = check_gitignore_consistency(
            tmp_path, tracked_files=tracked, gitignore_patterns=patterns
        )
        assert len(result.inconsistencies) == 0

    def test_glob_pattern_match(self, tmp_path: Path):
        tracked = ["old.pyc", "src/test.pyc"]
        patterns = ["*.pyc"]

        result = check_gitignore_consistency(
            tmp_path, tracked_files=tracked, gitignore_patterns=patterns
        )
        assert len(result.inconsistencies) == 2

    def test_no_gitignore_no_crash(self, tmp_path: Path):
        result = check_gitignore_consistency(
            tmp_path, tracked_files=["file.py"], gitignore_patterns=[]
        )
        assert len(result.inconsistencies) == 0
        assert result.tracked_file_count == 1
        assert result.gitignore_pattern_count == 0

    def test_output_includes_matching_pattern(self, tmp_path: Path):
        tracked = [".env"]
        patterns = [".env"]
        result = check_gitignore_consistency(
            tmp_path, tracked_files=tracked, gitignore_patterns=patterns
        )
        assert result.inconsistencies[0].matching_pattern == ".env"

    def test_serialization(self, tmp_path: Path):
        tracked = [".env"]
        patterns = [".env"]
        result = check_gitignore_consistency(
            tmp_path, tracked_files=tracked, gitignore_patterns=patterns
        )
        d = result.to_dict()
        assert "inconsistencies" in d
        assert "tracked_file_count" in d
        assert "inconsistency_count" in d
