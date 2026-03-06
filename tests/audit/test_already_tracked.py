"""Tests for ALREADY_TRACKED report section (T05.04 / D-0043)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.already_tracked import (
    AlreadyTrackedSection,
    build_already_tracked_section,
)
from superclaude.cli.audit.known_issues import MatchResult


class TestAlreadyTrackedSection:
    def test_present_when_matches_exist(self):
        matches = [
            MatchResult(
                file_path="src/legacy/old.py",
                classification="DELETE",
                matched=True,
                registry_entry_id="KI-001",
                matched_pattern="src/legacy/*.py",
            ),
        ]
        section = build_already_tracked_section(matches)
        assert section.is_present is True

    def test_absent_when_no_matches(self):
        section = build_already_tracked_section([])
        assert section.is_present is False

    def test_to_dict_with_matches(self):
        matches = [
            MatchResult(
                file_path="src/legacy/old.py",
                classification="DELETE",
                matched=True,
                registry_entry_id="KI-001",
                matched_pattern="src/legacy/*.py",
            ),
            MatchResult(
                file_path="src/legacy/dead.py",
                classification="DELETE",
                matched=True,
                registry_entry_id="KI-001",
                matched_pattern="src/legacy/*.py",
            ),
        ]
        section = build_already_tracked_section(matches)
        d = section.to_dict()
        assert d["already_tracked_count"] == 2
        assert len(d["already_tracked"]) == 2

    def test_to_dict_empty_when_absent(self):
        section = build_already_tracked_section([])
        d = section.to_dict()
        assert d == {}

    def test_render_markdown_with_matches(self):
        matches = [
            MatchResult(
                file_path="src/legacy/old.py",
                classification="DELETE",
                matched=True,
                registry_entry_id="KI-001",
                matched_pattern="src/legacy/*.py",
            ),
        ]
        section = build_already_tracked_section(matches)
        md = section.render_markdown()
        assert "## Already Tracked" in md
        assert "KI-001" in md
        assert "src/legacy/old.py" in md

    def test_render_markdown_empty_when_absent(self):
        section = build_already_tracked_section([])
        assert section.render_markdown() == ""

    def test_section_lists_both_suppressed_findings(self):
        matches = [
            MatchResult(
                file_path="a.py", classification="DELETE", matched=True,
                registry_entry_id="KI-001", matched_pattern="*.py",
            ),
            MatchResult(
                file_path="b.py", classification="DELETE", matched=True,
                registry_entry_id="KI-002", matched_pattern="b.*",
            ),
        ]
        section = build_already_tracked_section(matches)
        d = section.to_dict()
        ids = {e["registry_entry_id"] for e in d["already_tracked"]}
        assert ids == {"KI-001", "KI-002"}
