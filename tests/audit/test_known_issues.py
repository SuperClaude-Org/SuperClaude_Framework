"""Tests for known-issues registry (T05.02 / D-0041)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from superclaude.cli.audit.known_issues import (
    KnownIssuesRegistry,
    RegistryEntry,
    load_registry,
    save_registry,
)


def _make_entry(
    issue_id: str = "KI-001",
    pattern: str = "src/legacy/*.py",
    classification: str = "DELETE",
    ttl_days: int = 90,
) -> RegistryEntry:
    return RegistryEntry(
        issue_id=issue_id,
        pattern=pattern,
        classification=classification,
        created_date="2026-01-01T00:00:00+00:00",
        ttl_days=ttl_days,
    )


class TestRegistryMatch:
    def test_matching_pattern_suppresses(self):
        reg = KnownIssuesRegistry(entries=[_make_entry()])
        result = reg.match_finding("src/legacy/old.py", "DELETE")
        assert result.matched is True
        assert result.registry_entry_id == "KI-001"

    def test_non_matching_path_not_suppressed(self):
        reg = KnownIssuesRegistry(entries=[_make_entry()])
        result = reg.match_finding("src/core/new.py", "DELETE")
        assert result.matched is False

    def test_non_matching_classification_not_suppressed(self):
        reg = KnownIssuesRegistry(entries=[_make_entry()])
        result = reg.match_finding("src/legacy/old.py", "KEEP")
        assert result.matched is False

    def test_last_matched_updated_on_match(self):
        entry = _make_entry()
        reg = KnownIssuesRegistry(entries=[entry])
        now = datetime(2026, 3, 5, tzinfo=timezone.utc)
        reg.match_finding("src/legacy/old.py", "DELETE", now=now)
        assert entry.last_matched is not None
        assert "2026-03-05" in entry.last_matched

    def test_last_matched_not_updated_on_miss(self):
        entry = _make_entry()
        reg = KnownIssuesRegistry(entries=[entry])
        reg.match_finding("src/core/new.py", "DELETE")
        assert entry.last_matched is None

    def test_empty_classification_matches_any(self):
        entry = _make_entry(classification="")
        reg = KnownIssuesRegistry(entries=[entry])
        result = reg.match_finding("src/legacy/old.py", "KEEP")
        assert result.matched is True


class TestMatchFindings:
    def test_batch_matching(self):
        reg = KnownIssuesRegistry(entries=[_make_entry()])
        findings = [
            {"file_path": "src/legacy/old.py", "classification": "DELETE"},
            {"file_path": "src/core/new.py", "classification": "KEEP"},
        ]
        suppressed, unsuppressed = reg.match_findings(findings)
        assert len(suppressed) == 1
        assert len(unsuppressed) == 1

    def test_empty_registry_suppresses_nothing(self):
        reg = KnownIssuesRegistry()
        findings = [
            {"file_path": "src/foo.py", "classification": "DELETE"},
        ]
        suppressed, unsuppressed = reg.match_findings(findings)
        assert len(suppressed) == 0
        assert len(unsuppressed) == 1


class TestPersistence:
    def test_save_and_load(self, tmp_path):
        reg = KnownIssuesRegistry(entries=[_make_entry()])
        path = tmp_path / "registry.json"
        save_registry(reg, path)

        loaded = load_registry(path)
        assert len(loaded.entries) == 1
        assert loaded.entries[0].issue_id == "KI-001"

    def test_load_nonexistent_returns_empty(self, tmp_path):
        loaded = load_registry(tmp_path / "missing.json")
        assert len(loaded.entries) == 0

    def test_roundtrip_preserves_fields(self, tmp_path):
        entry = _make_entry()
        entry.last_matched = "2026-02-15T00:00:00+00:00"
        reg = KnownIssuesRegistry(entries=[entry])
        path = tmp_path / "reg.json"
        save_registry(reg, path)
        loaded = load_registry(path)
        assert loaded.entries[0].last_matched == "2026-02-15T00:00:00+00:00"
        assert loaded.entries[0].ttl_days == 90

    def test_registry_file_updated_after_match(self, tmp_path):
        reg = KnownIssuesRegistry(entries=[_make_entry()])
        path = tmp_path / "reg.json"
        save_registry(reg, path)
        loaded = load_registry(path)
        now = datetime(2026, 3, 5, tzinfo=timezone.utc)
        loaded.match_finding("src/legacy/old.py", "DELETE", now=now)
        save_registry(loaded, path)
        reloaded = load_registry(path)
        assert "2026-03-05" in reloaded.entries[0].last_matched
