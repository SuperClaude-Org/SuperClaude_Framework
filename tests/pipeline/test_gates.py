"""Tests for pipeline/gates.py -- 4-tier gate validation with edge cases."""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.pipeline.gates import gate_passed
from superclaude.cli.pipeline.models import GateCriteria, SemanticCheck


class TestExemptTier:
    def test_always_passes_even_nonexistent(self, tmp_path):
        gc = GateCriteria(required_frontmatter_fields=[], min_lines=0, enforcement_tier="EXEMPT")
        ok, reason = gate_passed(tmp_path / "nonexistent.md", gc)
        assert ok is True
        assert reason is None


class TestLightTier:
    def test_file_not_found(self, tmp_path):
        gc = GateCriteria(required_frontmatter_fields=[], min_lines=0, enforcement_tier="LIGHT")
        ok, reason = gate_passed(tmp_path / "missing.md", gc)
        assert ok is False
        assert "File not found" in reason

    def test_empty_file(self, make_file):
        gc = GateCriteria(required_frontmatter_fields=[], min_lines=0, enforcement_tier="LIGHT")
        f = make_file("empty.md", "")
        ok, reason = gate_passed(f, gc)
        assert ok is False
        assert "empty" in reason.lower()

    def test_whitespace_only_file(self, make_file):
        gc = GateCriteria(required_frontmatter_fields=[], min_lines=0, enforcement_tier="LIGHT")
        f = make_file("ws.md", "   \n  \n  ")
        ok, reason = gate_passed(f, gc)
        assert ok is False
        assert "empty" in reason.lower()

    def test_nonempty_passes(self, make_file):
        gc = GateCriteria(required_frontmatter_fields=[], min_lines=0, enforcement_tier="LIGHT")
        f = make_file("ok.md", "content here")
        ok, reason = gate_passed(f, gc)
        assert ok is True


class TestStandardTier:
    def test_below_min_lines(self, make_file):
        gc = GateCriteria(required_frontmatter_fields=[], min_lines=10, enforcement_tier="STANDARD")
        f = make_file("short.md", "line1\nline2\n")
        ok, reason = gate_passed(f, gc)
        assert ok is False
        assert "minimum line count" in reason.lower()
        assert "2 < 10" in reason

    def test_missing_frontmatter(self, make_file):
        gc = GateCriteria(required_frontmatter_fields=["title"], min_lines=3, enforcement_tier="STANDARD")
        f = make_file("nofm.md", "\n".join(["line"] * 10))
        ok, reason = gate_passed(f, gc)
        assert ok is False
        assert "frontmatter" in reason.lower()

    def test_malformed_yaml(self, make_file):
        gc = GateCriteria(required_frontmatter_fields=["title"], min_lines=3, enforcement_tier="STANDARD")
        f = make_file("bad.md", "---\nunclosed frontmatter\nno closing dashes\nmore text\nfiller\n")
        ok, reason = gate_passed(f, gc)
        assert ok is False
        assert "frontmatter" in reason.lower()

    def test_missing_required_field(self, make_file):
        gc = GateCriteria(required_frontmatter_fields=["title", "version"], min_lines=3, enforcement_tier="STANDARD")
        f = make_file("partial.md", "---\ntitle: Test\n---\n" + "\n".join(["x"] * 10))
        ok, reason = gate_passed(f, gc)
        assert ok is False
        assert "version" in reason

    def test_all_checks_pass(self, make_file):
        gc = GateCriteria(
            required_frontmatter_fields=["title", "version"],
            min_lines=5,
            enforcement_tier="STANDARD",
        )
        content = "---\ntitle: Test\nversion: 1.0\n---\n" + "\n".join(["x"] * 10)
        f = make_file("ok.md", content)
        ok, reason = gate_passed(f, gc)
        assert ok is True
        assert reason is None


class TestStrictTier:
    def test_semantic_check_fails(self, make_file):
        gc = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=3,
            enforcement_tier="STRICT",
            semantic_checks=[
                SemanticCheck(
                    name="has_heading",
                    check_fn=lambda c: "# " in c,
                    failure_message="No heading found",
                )
            ],
        )
        f = make_file("no_heading.md", "---\ntitle: T\n---\nno heading here\nmore lines\n")
        ok, reason = gate_passed(f, gc)
        assert ok is False
        assert "has_heading" in reason
        assert "No heading found" in reason

    def test_semantic_check_passes(self, make_file):
        gc = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=3,
            enforcement_tier="STRICT",
            semantic_checks=[
                SemanticCheck(
                    name="has_heading",
                    check_fn=lambda c: "# " in c,
                    failure_message="No heading found",
                )
            ],
        )
        f = make_file("ok.md", "---\ntitle: T\n---\n# Heading\nmore lines\n")
        ok, reason = gate_passed(f, gc)
        assert ok is True

    def test_no_semantic_checks_defined(self, make_file):
        gc = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=3,
            enforcement_tier="STRICT",
            semantic_checks=None,
        )
        f = make_file("ok.md", "---\ntitle: T\n---\ncontent\nmore\n")
        ok, reason = gate_passed(f, gc)
        assert ok is True

    def test_zero_byte_file(self, make_file):
        gc = GateCriteria(
            required_frontmatter_fields=[],
            min_lines=1,
            enforcement_tier="STRICT",
        )
        f = make_file("zero.md", "")
        ok, reason = gate_passed(f, gc)
        assert ok is False
