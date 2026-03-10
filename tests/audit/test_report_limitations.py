"""Tests for limitations section (T05.08 / D-0047)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.report_limitations import (
    KNOWN_LIMITATIONS,
    build_limitations_section,
    render_limitations_markdown,
)


class TestLimitationsSection:
    def test_at_least_3_sources(self):
        assert len(KNOWN_LIMITATIONS) >= 3

    def test_each_limitation_has_impact(self):
        for lim in KNOWN_LIMITATIONS:
            assert lim.impact, f"Limitation '{lim.source}' missing impact"

    def test_each_limitation_has_mitigation(self):
        for lim in KNOWN_LIMITATIONS:
            assert lim.mitigation, f"Limitation '{lim.source}' missing mitigation"

    def test_build_section_dict(self):
        section = build_limitations_section()
        assert section["limitation_count"] >= 3
        assert len(section["limitations"]) >= 3
        assert "overall_assessment" in section

    def test_render_markdown_contains_all_sources(self):
        md = render_limitations_markdown()
        for lim in KNOWN_LIMITATIONS:
            assert lim.source in md

    def test_render_markdown_contains_table(self):
        md = render_limitations_markdown()
        assert "| # | Source |" in md

    def test_section_serializable(self):
        section = build_limitations_section()
        import json
        json.dumps(section)  # Should not raise
