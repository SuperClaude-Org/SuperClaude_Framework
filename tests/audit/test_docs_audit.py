"""Tests for minimal docs audit (T03.09 / D-0025)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from superclaude.cli.audit.docs_audit import (
    audit_docs,
    check_broken_links,
    check_staleness,
    extract_internal_links,
)


class TestExtractInternalLinks:
    def test_relative_link(self):
        content = "[Guide](./guide.md)"
        links = extract_internal_links(content)
        assert len(links) == 1
        assert links[0][2] == "./guide.md"

    def test_skips_external_links(self):
        content = "[Docs](https://example.com)"
        links = extract_internal_links(content)
        assert len(links) == 0

    def test_skips_anchors(self):
        content = "[Section](#section)"
        links = extract_internal_links(content)
        assert len(links) == 0

    def test_strips_anchors_from_paths(self):
        content = "[Guide](./guide.md#section)"
        links = extract_internal_links(content)
        assert links[0][2] == "./guide.md"

    def test_multiple_links(self):
        content = "[A](a.md) and [B](b.md)"
        links = extract_internal_links(content)
        assert len(links) == 2


class TestCheckBrokenLinks:
    def test_existing_link_not_broken(self):
        known = {"docs/guide.md"}
        broken = check_broken_links(
            "docs/README.md", "[Guide](guide.md)", known,
        )
        assert len(broken) == 0

    def test_missing_link_detected(self):
        known = {"docs/README.md"}
        broken = check_broken_links(
            "docs/README.md", "[Guide](./missing.md)", known,
        )
        assert len(broken) == 1
        assert broken[0].target_path == "./missing.md"

    def test_broken_link_has_line_number(self):
        known = set()
        broken = check_broken_links(
            "docs/README.md",
            "line1\n[Guide](./missing.md)\nline3\n",
            known,
        )
        assert broken[0].line_number == 2


class TestCheckStaleness:
    def test_stale_doc(self):
        now = datetime(2026, 3, 5, tzinfo=timezone.utc)
        result = check_staleness(
            "old.md", "2024-01-01T00:00:00+00:00",
            threshold_days=365, current_date=now,
        )
        assert result is not None
        assert result.days_stale > 365

    def test_fresh_doc(self):
        now = datetime(2026, 3, 5, tzinfo=timezone.utc)
        result = check_staleness(
            "new.md", "2026-01-01T00:00:00+00:00",
            threshold_days=365, current_date=now,
        )
        assert result is None

    def test_unknown_date(self):
        result = check_staleness("x.md", "unknown")
        assert result is None


class TestAuditDocs:
    def test_full_audit(self):
        now = datetime(2026, 3, 5, tzinfo=timezone.utc)
        doc_files = {
            "docs/README.md": "[Guide](./guide.md)\n[Missing](./missing.md)\n",
            "docs/old.md": "# Old doc\n",
        }
        known_files = {"docs/README.md", "docs/old.md", "docs/guide.md"}
        last_modified = {
            "docs/README.md": "2026-01-01T00:00:00+00:00",
            "docs/old.md": "2023-01-01T00:00:00+00:00",
        }
        result = audit_docs(
            doc_files, known_files, last_modified,
            threshold_days=365, current_date=now,
        )
        # 1 broken link (missing.md)
        assert result.broken_links[0].target_path == "./missing.md"
        # 1 stale doc (old.md)
        assert len(result.stale_docs) == 1
        assert result.stale_docs[0].file_path == "docs/old.md"

    def test_result_serializable(self):
        result = audit_docs({}, set())
        d = result.to_dict()
        assert "broken_links" in d
        assert "stale_docs" in d
