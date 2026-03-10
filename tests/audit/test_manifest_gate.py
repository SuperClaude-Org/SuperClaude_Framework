"""Tests for manifest completeness gate (T02.06, D-0016)."""

from __future__ import annotations

import logging

import pytest

from superclaude.cli.audit.manifest_gate import (
    DEFAULT_COVERAGE_THRESHOLD,
    GateResult,
    check_manifest_completeness,
    is_excluded,
)


class TestExclusions:
    """File exclusion rules."""

    def test_git_excluded(self):
        assert is_excluded(".git/objects/abc123") is True

    def test_node_modules_excluded(self):
        assert is_excluded("node_modules/express/index.js") is True

    def test_pyc_excluded(self):
        assert is_excluded("src/__pycache__/foo.cpython-312.pyc") is True

    def test_binary_excluded(self):
        assert is_excluded("assets/logo.png") is True

    def test_source_not_excluded(self):
        assert is_excluded("src/main.py") is False

    def test_markdown_not_excluded(self):
        assert is_excluded("docs/README.md") is False


class TestManifestGateBlocking:
    """Gate blocks when coverage is below threshold."""

    def test_blocks_at_90_percent(self):
        """AC: gate blocks when coverage < 95%."""
        all_files = [f"src/file_{i}.py" for i in range(100)]
        profiled = set(all_files[:90])  # 90% coverage
        result = check_manifest_completeness(all_files, profiled)
        assert result.passed is False
        assert result.coverage < DEFAULT_COVERAGE_THRESHOLD

    def test_blocks_at_50_percent(self):
        all_files = [f"src/file_{i}.py" for i in range(100)]
        profiled = set(all_files[:50])
        result = check_manifest_completeness(all_files, profiled)
        assert result.passed is False

    def test_missing_files_logged(self):
        """AC: missing files logged when gate blocks."""
        all_files = [f"src/file_{i}.py" for i in range(10)]
        profiled = set(all_files[:5])
        result = check_manifest_completeness(all_files, profiled)
        assert len(result.missing_files) == 5


class TestManifestGatePassing:
    """Gate passes when coverage meets threshold."""

    def test_passes_at_100_percent(self):
        """AC: gate passes at 100% coverage."""
        all_files = [f"src/file_{i}.py" for i in range(100)]
        profiled = set(all_files)
        result = check_manifest_completeness(all_files, profiled)
        assert result.passed is True
        assert result.coverage == 1.0

    def test_passes_at_95_percent(self):
        """AC: gate passes at exactly 95%."""
        all_files = [f"src/file_{i}.py" for i in range(100)]
        profiled = set(all_files[:95])
        result = check_manifest_completeness(all_files, profiled)
        assert result.passed is True

    def test_passes_at_96_percent(self):
        all_files = [f"src/file_{i}.py" for i in range(100)]
        profiled = set(all_files[:96])
        result = check_manifest_completeness(all_files, profiled)
        assert result.passed is True

    def test_empty_repo_passes(self):
        result = check_manifest_completeness([], set())
        assert result.passed is True


class TestManifestGateExclusions:
    """Excluded files don't count toward coverage."""

    def test_binary_files_excluded_from_count(self):
        all_files = [
            "src/main.py",
            "src/utils.py",
            "assets/logo.png",  # excluded
            "node_modules/lib.js",  # excluded
        ]
        profiled = {"src/main.py", "src/utils.py"}
        result = check_manifest_completeness(all_files, profiled)
        assert result.passed is True
        assert result.total_eligible == 2
        assert result.total_profiled == 2


class TestManifestGateCustomThreshold:
    """Custom threshold support."""

    def test_lower_threshold(self):
        all_files = [f"src/file_{i}.py" for i in range(100)]
        profiled = set(all_files[:80])
        result = check_manifest_completeness(
            all_files, profiled, threshold=0.75
        )
        assert result.passed is True

    def test_higher_threshold(self):
        all_files = [f"src/file_{i}.py" for i in range(100)]
        profiled = set(all_files[:95])
        result = check_manifest_completeness(
            all_files, profiled, threshold=0.99
        )
        assert result.passed is False


class TestGateResultSerialization:
    def test_to_dict(self):
        result = GateResult(
            passed=False,
            coverage=0.90,
            threshold=0.95,
            total_eligible=100,
            total_profiled=90,
            missing_files=["a.py", "b.py"],
        )
        d = result.to_dict()
        assert d["passed"] is False
        assert d["coverage"] == 0.90
        assert d["missing_count"] == 2
