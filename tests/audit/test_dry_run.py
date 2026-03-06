"""Tests for dry-run mode (T02.05, D-0015)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.dry_run import DryRunEstimate, dry_run


FIXTURE_FILES = [
    "src/api/users.py",
    "src/components/Button.tsx",
    "tests/test_api.py",
    "docs/README.md",
    ".github/workflows/ci.yml",
    "src/auth/login.py",
    "pyproject.toml",
]


class TestDryRun:
    """Dry-run produces estimates without analysis."""

    def test_returns_estimate(self):
        result = dry_run(FIXTURE_FILES)
        assert isinstance(result, DryRunEstimate)

    def test_no_classification_output(self):
        """AC: dry-run produces estimates without executing analysis."""
        result = dry_run(FIXTURE_FILES)
        # DryRunEstimate has no classification fields
        d = result.to_dict()
        assert "classification" not in d
        assert "tier" not in d
        assert "action" not in d

    def test_required_fields(self):
        """AC: includes file_count, batch_count, estimated_tokens, domain_distribution."""
        result = dry_run(FIXTURE_FILES)
        d = result.to_dict()
        assert "file_count" in d
        assert "batch_count" in d
        assert "estimated_tokens" in d
        assert "domain_distribution" in d

    def test_file_count_correct(self):
        result = dry_run(FIXTURE_FILES)
        assert result.file_count == len(FIXTURE_FILES)

    def test_batch_count_positive(self):
        result = dry_run(FIXTURE_FILES)
        assert result.batch_count >= 1

    def test_estimated_tokens_positive(self):
        result = dry_run(FIXTURE_FILES)
        assert result.estimated_tokens > 0

    def test_runtime_estimate_positive(self):
        result = dry_run(FIXTURE_FILES)
        assert result.estimated_runtime_seconds > 0

    def test_domain_distribution_sums_to_file_count(self):
        result = dry_run(FIXTURE_FILES)
        total = sum(result.domain_distribution.values())
        assert total == len(FIXTURE_FILES)

    def test_risk_distribution_present(self):
        result = dry_run(FIXTURE_FILES)
        assert isinstance(result.risk_distribution, dict)
        assert sum(result.risk_distribution.values()) == len(FIXTURE_FILES)

    def test_serialization(self):
        result = dry_run(FIXTURE_FILES)
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["file_count"] == len(FIXTURE_FILES)

    def test_with_file_sizes(self):
        sizes = {"src/api/users.py": 10_000}
        result = dry_run(FIXTURE_FILES, file_sizes=sizes)
        assert result.estimated_tokens > 0

    def test_custom_batch_size(self):
        result = dry_run(FIXTURE_FILES, max_batch_size=3)
        assert result.batch_count >= 1
