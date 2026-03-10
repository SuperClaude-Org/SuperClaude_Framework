"""Known-issues registry for cross-run finding suppression.

Implements:
  T05.02 / D-0041 / AC20: load, match, suppress
  T05.03 / D-0042 / AC20: TTL expiration and LRU eviction

Features:
  - Loads a persistent JSON registry of known issues
  - Matches current findings against registered patterns (glob + classification)
  - Suppresses matched findings with ALREADY_TRACKED status
  - Updates last_matched timestamp for matched entries
  - Expires entries exceeding TTL on registry load
  - Evicts least-recently-matched entries when registry exceeds max size

Registry schema:
  {
    "entries": [
      {
        "issue_id": "KI-001",
        "pattern": "src/legacy/*.py",
        "classification": "DELETE",
        "created_date": "2026-01-01T00:00:00+00:00",
        "last_matched": "2026-03-01T00:00:00+00:00",
        "ttl_days": 90
      }
    ]
  }
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path
from typing import Any


@dataclass
class RegistryEntry:
    """A known-issue registry entry."""

    issue_id: str
    pattern: str  # File path glob pattern
    classification: str  # Classification type to match
    created_date: str  # ISO date
    last_matched: str | None = None  # ISO date
    ttl_days: int = 90

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "pattern": self.pattern,
            "classification": self.classification,
            "created_date": self.created_date,
            "last_matched": self.last_matched,
            "ttl_days": self.ttl_days,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> RegistryEntry:
        return cls(
            issue_id=d["issue_id"],
            pattern=d["pattern"],
            classification=d.get("classification", ""),
            created_date=d.get("created_date", ""),
            last_matched=d.get("last_matched"),
            ttl_days=d.get("ttl_days", 90),
        )


@dataclass
class MatchResult:
    """Result of matching a finding against the registry."""

    file_path: str
    classification: str
    matched: bool
    registry_entry_id: str | None = None
    matched_pattern: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "file_path": self.file_path,
            "classification": self.classification,
            "matched": self.matched,
        }
        if self.matched:
            d["registry_entry_id"] = self.registry_entry_id
            d["matched_pattern"] = self.matched_pattern
        return d


@dataclass
class KnownIssuesRegistry:
    """Persistent known-issues registry."""

    entries: list[RegistryEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> KnownIssuesRegistry:
        entries = [RegistryEntry.from_dict(e) for e in d.get("entries", [])]
        return cls(entries=entries)

    def match_finding(
        self,
        file_path: str,
        classification: str,
        now: datetime | None = None,
    ) -> MatchResult:
        """Match a finding against registry entries.

        Returns MatchResult with matched=True if a registry entry matches
        the file path glob and classification type.
        """
        for entry in self.entries:
            if entry.classification and entry.classification != classification:
                continue
            if fnmatch(file_path, entry.pattern):
                # Update last_matched
                ts = (now or datetime.now(timezone.utc)).isoformat()
                entry.last_matched = ts
                return MatchResult(
                    file_path=file_path,
                    classification=classification,
                    matched=True,
                    registry_entry_id=entry.issue_id,
                    matched_pattern=entry.pattern,
                )

        return MatchResult(
            file_path=file_path,
            classification=classification,
            matched=False,
        )

    def match_findings(
        self,
        findings: list[dict[str, str]],
        now: datetime | None = None,
    ) -> tuple[list[MatchResult], list[MatchResult]]:
        """Match multiple findings. Returns (suppressed, unsuppressed)."""
        suppressed = []
        unsuppressed = []
        for f in findings:
            result = self.match_finding(
                f["file_path"], f["classification"], now=now,
            )
            if result.matched:
                suppressed.append(result)
            else:
                unsuppressed.append(result)
        return suppressed, unsuppressed

    def expire_entries(
        self,
        now: datetime | None = None,
    ) -> list[EvictionEvent]:
        """Remove entries that have exceeded their TTL.

        An entry is expired if it has never been matched (uses created_date)
        or its last_matched date exceeds ttl_days from now.
        """
        current = now or datetime.now(timezone.utc)
        events = []
        surviving = []

        for entry in self.entries:
            ref_date_str = entry.last_matched or entry.created_date
            if not ref_date_str:
                surviving.append(entry)
                continue

            try:
                ref_date = datetime.fromisoformat(
                    ref_date_str.replace("Z", "+00:00"),
                )
                if ref_date.tzinfo is None:
                    ref_date = ref_date.replace(tzinfo=timezone.utc)
                days_since = (current - ref_date).days
                if days_since > entry.ttl_days:
                    events.append(EvictionEvent(
                        issue_id=entry.issue_id,
                        reason="ttl_expired",
                        detail=f"TTL {entry.ttl_days}d exceeded by {days_since - entry.ttl_days}d",
                    ))
                else:
                    surviving.append(entry)
            except (ValueError, TypeError):
                surviving.append(entry)

        self.entries = surviving
        return events

    def evict_lru(
        self,
        max_entries: int = 500,
    ) -> list[EvictionEvent]:
        """Evict least-recently-matched entries when registry exceeds max size.

        Entries are sorted by last_matched (or created_date as fallback).
        Least-recently-matched entries are removed first.
        """
        if len(self.entries) <= max_entries:
            return []

        def _sort_key(entry: RegistryEntry) -> str:
            return entry.last_matched or entry.created_date or ""

        self.entries.sort(key=_sort_key, reverse=True)

        to_evict = self.entries[max_entries:]
        self.entries = self.entries[:max_entries]

        return [
            EvictionEvent(
                issue_id=e.issue_id,
                reason="lru_eviction",
                detail=f"Registry exceeded {max_entries} entries",
            )
            for e in to_evict
        ]

    def apply_lifecycle(
        self,
        now: datetime | None = None,
        max_entries: int = 500,
    ) -> list[EvictionEvent]:
        """Apply TTL expiration then LRU eviction. Returns all events."""
        events = self.expire_entries(now=now)
        events.extend(self.evict_lru(max_entries=max_entries))
        return events


@dataclass
class EvictionEvent:
    """Log entry for a registry eviction."""

    issue_id: str
    reason: str  # ttl_expired | lru_eviction
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "reason": self.reason,
            "detail": self.detail,
        }


def load_registry(path: str | Path) -> KnownIssuesRegistry:
    """Load registry from a JSON file.

    Returns empty registry if file doesn't exist.
    """
    p = Path(path)
    if not p.exists():
        return KnownIssuesRegistry()
    data = json.loads(p.read_text(encoding="utf-8"))
    return KnownIssuesRegistry.from_dict(data)


def save_registry(registry: KnownIssuesRegistry, path: str | Path) -> None:
    """Save registry to a JSON file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(registry.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
