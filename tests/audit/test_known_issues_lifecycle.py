"""Tests for TTL and LRU lifecycle rules (T05.03 / D-0042)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from superclaude.cli.audit.known_issues import (
    EvictionEvent,
    KnownIssuesRegistry,
    RegistryEntry,
)


def _make_entry(
    issue_id: str = "KI-001",
    pattern: str = "src/legacy/*.py",
    created_date: str = "2026-01-01T00:00:00+00:00",
    last_matched: str | None = None,
    ttl_days: int = 90,
) -> RegistryEntry:
    return RegistryEntry(
        issue_id=issue_id,
        pattern=pattern,
        classification="DELETE",
        created_date=created_date,
        last_matched=last_matched,
        ttl_days=ttl_days,
    )


class TestTTLExpiration:
    def test_expired_entry_removed(self):
        now = datetime(2026, 6, 1, tzinfo=timezone.utc)
        entry = _make_entry(ttl_days=90, created_date="2026-01-01T00:00:00+00:00")
        reg = KnownIssuesRegistry(entries=[entry])
        events = reg.expire_entries(now=now)
        assert len(reg.entries) == 0
        assert len(events) == 1
        assert events[0].reason == "ttl_expired"

    def test_fresh_entry_kept(self):
        now = datetime(2026, 3, 1, tzinfo=timezone.utc)
        entry = _make_entry(ttl_days=90, created_date="2026-01-01T00:00:00+00:00")
        reg = KnownIssuesRegistry(entries=[entry])
        events = reg.expire_entries(now=now)
        assert len(reg.entries) == 1
        assert len(events) == 0

    def test_ttl_uses_last_matched_when_present(self):
        now = datetime(2026, 6, 1, tzinfo=timezone.utc)
        entry = _make_entry(
            ttl_days=90,
            created_date="2025-01-01T00:00:00+00:00",
            last_matched="2026-04-01T00:00:00+00:00",
        )
        reg = KnownIssuesRegistry(entries=[entry])
        events = reg.expire_entries(now=now)
        assert len(reg.entries) == 1  # last_matched is within TTL
        assert len(events) == 0

    def test_negative_ttl_immediately_expires(self):
        now = datetime(2026, 3, 5, tzinfo=timezone.utc)
        entry = _make_entry(ttl_days=-1, created_date="2026-03-05T00:00:00+00:00")
        reg = KnownIssuesRegistry(entries=[entry])
        events = reg.expire_entries(now=now)
        assert len(reg.entries) == 0
        assert len(events) == 1

    def test_empty_registry_no_events(self):
        reg = KnownIssuesRegistry()
        events = reg.expire_entries()
        assert len(events) == 0


class TestLRUEviction:
    def test_evicts_when_over_limit(self):
        entries = [
            _make_entry(
                issue_id=f"KI-{i:03d}",
                last_matched=f"2026-03-{i+1:02d}T00:00:00+00:00",
            )
            for i in range(10)
        ]
        reg = KnownIssuesRegistry(entries=entries)
        events = reg.evict_lru(max_entries=5)
        assert len(reg.entries) == 5
        assert len(events) == 5

    def test_keeps_most_recently_matched(self):
        old = _make_entry(
            issue_id="OLD",
            last_matched="2026-01-01T00:00:00+00:00",
        )
        new = _make_entry(
            issue_id="NEW",
            last_matched="2026-03-01T00:00:00+00:00",
        )
        reg = KnownIssuesRegistry(entries=[old, new])
        events = reg.evict_lru(max_entries=1)
        assert len(reg.entries) == 1
        assert reg.entries[0].issue_id == "NEW"
        assert events[0].issue_id == "OLD"

    def test_no_eviction_under_limit(self):
        entries = [_make_entry(issue_id=f"KI-{i}") for i in range(3)]
        reg = KnownIssuesRegistry(entries=entries)
        events = reg.evict_lru(max_entries=500)
        assert len(reg.entries) == 3
        assert len(events) == 0

    def test_boundary_exact_limit(self):
        entries = [_make_entry(issue_id=f"KI-{i}") for i in range(500)]
        reg = KnownIssuesRegistry(entries=entries)
        events = reg.evict_lru(max_entries=500)
        assert len(reg.entries) == 500
        assert len(events) == 0

    def test_eviction_events_have_details(self):
        entries = [_make_entry(issue_id=f"KI-{i}") for i in range(3)]
        reg = KnownIssuesRegistry(entries=entries)
        events = reg.evict_lru(max_entries=1)
        for ev in events:
            assert ev.reason == "lru_eviction"
            assert "1" in ev.detail


class TestApplyLifecycle:
    def test_combined_ttl_and_lru(self):
        now = datetime(2026, 6, 1, tzinfo=timezone.utc)
        expired = _make_entry(
            issue_id="EXPIRED",
            ttl_days=30,
            created_date="2025-01-01T00:00:00+00:00",
        )
        recent = _make_entry(
            issue_id="RECENT",
            ttl_days=365,
            last_matched="2026-05-01T00:00:00+00:00",
        )
        reg = KnownIssuesRegistry(entries=[expired, recent])
        events = reg.apply_lifecycle(now=now, max_entries=500)
        assert len(reg.entries) == 1
        assert reg.entries[0].issue_id == "RECENT"
        ttl_events = [e for e in events if e.reason == "ttl_expired"]
        assert len(ttl_events) == 1

    def test_eviction_event_serializable(self):
        ev = EvictionEvent(issue_id="KI-001", reason="ttl_expired", detail="test")
        d = ev.to_dict()
        assert d["issue_id"] == "KI-001"
        assert d["reason"] == "ttl_expired"
