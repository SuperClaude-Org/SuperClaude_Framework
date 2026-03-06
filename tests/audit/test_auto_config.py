"""Tests for auto-config generation (T02.04, D-0014)."""

from __future__ import annotations

import json

import pytest

from superclaude.cli.audit.auto_config import (
    AuditConfig,
    CONFIG_FILENAME,
    detect_cold_start,
    ensure_config,
    generate_config,
    write_config,
)
from superclaude.cli.audit.profiler import ProfileReport, profile_repository


@pytest.fixture
def sample_profile():
    files = [
        "src/api/users.py",
        "src/auth/login.py",
        "tests/test_api.py",
        "docs/README.md",
        "pyproject.toml",
    ]
    return profile_repository(files)


class TestDetectColdStart:
    def test_no_config_is_cold_start(self, tmp_path):
        assert detect_cold_start(tmp_path) is True

    def test_existing_config_is_not_cold_start(self, tmp_path):
        (tmp_path / CONFIG_FILENAME).write_text("{}")
        assert detect_cold_start(tmp_path) is False


class TestGenerateConfig:
    def test_returns_audit_config(self, sample_profile):
        config = generate_config(sample_profile)
        assert isinstance(config, AuditConfig)

    def test_all_required_fields(self, sample_profile):
        """AC: config contains batch_size, depth, report_mode, budget."""
        config = generate_config(sample_profile)
        d = config.to_dict()
        assert "batch_size" in d
        assert "depth" in d
        assert "report_mode" in d
        assert "budget" in d

    def test_batch_size_scales_with_repo(self):
        small = profile_repository([f"src/{i}.py" for i in range(20)])
        large = profile_repository([f"src/{i}.py" for i in range(300)])
        assert generate_config(small).batch_size <= generate_config(large).batch_size

    def test_budget_positive(self, sample_profile):
        config = generate_config(sample_profile)
        assert config.budget > 0


class TestWriteConfig:
    def test_writes_valid_json(self, tmp_path, sample_profile):
        config = generate_config(sample_profile)
        path = write_config(config, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert "batch_size" in data

    def test_config_logged(self, tmp_path, sample_profile, caplog):
        """AC: config generation is logged."""
        import logging
        with caplog.at_level(logging.INFO):
            config = generate_config(sample_profile)
            write_config(config, tmp_path)
        assert any("Auto-generated" in r.message for r in caplog.records)


class TestEnsureConfig:
    def test_cold_start_generates_config(self, tmp_path, sample_profile):
        """AC: cold-start with no config generates valid config."""
        config = ensure_config(tmp_path, sample_profile)
        assert isinstance(config, AuditConfig)
        assert (tmp_path / CONFIG_FILENAME).exists()

    def test_existing_config_loaded(self, tmp_path, sample_profile):
        data = {"batch_size": 99, "depth": "deep", "report_mode": "summary", "budget": 77777}
        (tmp_path / CONFIG_FILENAME).write_text(json.dumps(data))
        config = ensure_config(tmp_path, sample_profile)
        assert config.batch_size == 99

    def test_roundtrip(self, sample_profile):
        config = generate_config(sample_profile)
        d = config.to_dict()
        restored = AuditConfig.from_dict(d)
        assert restored.to_dict() == d
