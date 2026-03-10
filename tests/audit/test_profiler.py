"""Tests for domain and risk-tier profiling (T02.01, D-0011)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.profiler import (
    FileProfile,
    ProfileReport,
    classify_domain,
    classify_risk_tier,
    profile_file,
    profile_repository,
)


class TestDomainClassification:
    """Domain classifier assigns exactly one domain per file."""

    def test_test_domain(self):
        domain, _ = classify_domain("tests/unit/test_foo.py")
        assert domain == "test"

    def test_docs_domain(self):
        domain, _ = classify_domain("docs/user-guide/setup.md")
        assert domain == "docs"

    def test_infra_domain(self):
        domain, _ = classify_domain(".github/workflows/ci.yml")
        assert domain == "infra"

    def test_frontend_domain(self):
        domain, _ = classify_domain("src/components/Button.tsx")
        assert domain == "frontend"

    def test_backend_domain(self):
        domain, _ = classify_domain("src/api/users.py")
        assert domain == "backend"

    def test_superclaude_is_backend(self):
        domain, _ = classify_domain("src/superclaude/cli/main.py")
        assert domain == "backend"

    def test_readme_is_docs(self):
        domain, _ = classify_domain("README.md")
        assert domain == "docs"

    def test_makefile_is_infra(self):
        domain, _ = classify_domain("Makefile")
        assert domain == "infra"

    def test_unknown_file_defaults_to_backend(self):
        domain, conf = classify_domain("src/something/unknown.py")
        assert domain == "backend"
        assert conf < 0.80  # lower confidence for default

    def test_confidence_positive(self):
        _, conf = classify_domain("tests/test_foo.py")
        assert 0.0 < conf <= 1.0


class TestRiskTierClassification:
    """Risk tier assigns exactly one tier per file."""

    def test_auth_is_high_risk(self):
        tier, _ = classify_risk_tier("src/auth/login.py")
        assert tier == "high"

    def test_security_is_high_risk(self):
        tier, _ = classify_risk_tier("src/security/scanner.py")
        assert tier == "high"

    def test_config_is_medium_risk(self):
        tier, _ = classify_risk_tier("pyproject.toml")
        assert tier == "medium"

    def test_dockerfile_is_medium_risk(self):
        tier, _ = classify_risk_tier("Dockerfile")
        assert tier == "medium"

    def test_regular_file_is_low_risk(self):
        tier, _ = classify_risk_tier("src/utils/helpers.py")
        assert tier == "low"

    def test_large_file_bumped_to_medium(self):
        tier, _ = classify_risk_tier("src/utils/big.py", file_size=20_000)
        assert tier == "medium"

    def test_small_file_stays_low(self):
        tier, _ = classify_risk_tier("src/utils/tiny.py", file_size=500)
        assert tier == "low"

    def test_env_is_high_risk(self):
        tier, _ = classify_risk_tier(".env")
        assert tier == "high"

    def test_migration_is_high_risk(self):
        tier, _ = classify_risk_tier("db/migration/001_init.sql")
        assert tier == "high"


class TestProfileFile:
    """profile_file combines domain + risk tier."""

    def test_returns_file_profile(self):
        result = profile_file("src/auth/login.py")
        assert isinstance(result, FileProfile)
        assert result.domain in ("frontend", "backend", "infra", "docs", "test")
        assert result.risk_tier in ("high", "medium", "low")
        assert result.confidence > 0.0

    def test_all_fields_present(self):
        result = profile_file("tests/test_foo.py")
        d = result.to_dict()
        assert "file_path" in d
        assert "domain" in d
        assert "risk_tier" in d
        assert "confidence" in d
        assert d["file_path"] == "tests/test_foo.py"


class TestProfileRepository:
    """profile_repository profiles all files deterministically."""

    FIXTURE_FILES = [
        "src/api/users.py",
        "src/components/Button.tsx",
        "tests/test_api.py",
        "docs/README.md",
        ".github/workflows/ci.yml",
        "src/auth/login.py",
        "pyproject.toml",
    ]

    def test_every_file_profiled(self):
        report = profile_repository(self.FIXTURE_FILES)
        assert len(report.files) == len(self.FIXTURE_FILES)

    def test_no_null_fields(self):
        """AC: every file receives exactly one domain and one risk tier."""
        report = profile_repository(self.FIXTURE_FILES)
        for fp in report.files:
            assert fp.domain is not None, f"null domain for {fp.file_path}"
            assert fp.risk_tier is not None, f"null risk_tier for {fp.file_path}"
            assert fp.confidence is not None, f"null confidence for {fp.file_path}"

    def test_deterministic(self):
        """AC: same inputs produce identical output across runs."""
        r1 = profile_repository(self.FIXTURE_FILES)
        r2 = profile_repository(self.FIXTURE_FILES)
        assert r1.to_dict() == r2.to_dict()

    def test_domain_distribution(self):
        report = profile_repository(self.FIXTURE_FILES)
        dist = report.domain_distribution
        assert isinstance(dist, dict)
        assert sum(dist.values()) == len(self.FIXTURE_FILES)

    def test_risk_distribution(self):
        report = profile_repository(self.FIXTURE_FILES)
        dist = report.risk_distribution
        assert isinstance(dist, dict)
        assert sum(dist.values()) == len(self.FIXTURE_FILES)

    def test_report_serialization(self):
        report = profile_repository(self.FIXTURE_FILES)
        d = report.to_dict()
        assert d["file_count"] == len(self.FIXTURE_FILES)
        assert "domain_distribution" in d
        assert "risk_distribution" in d
        assert "files" in d

    def test_with_file_sizes(self):
        sizes = {"src/api/users.py": 20_000, "docs/README.md": 200}
        report = profile_repository(self.FIXTURE_FILES, file_sizes=sizes)
        assert len(report.files) == len(self.FIXTURE_FILES)

    def test_from_dict_roundtrip(self):
        original = profile_file("src/auth/login.py")
        d = original.to_dict()
        restored = FileProfile.from_dict(d)
        assert restored.to_dict() == d
