"""Tests for section hashing additive-only enforcement (D-0033 / NFR-008).

Covers:
- Hash capture and comparison
- Additive changes accepted
- Modifications rejected
- Section removal rejected
- Multiple section handling
"""

from __future__ import annotations

import pytest

from superclaude.cli.cli_portify.utils import (
    extract_sections,
    hash_section,
    verify_additive_only,
)
from superclaude.cli.cli_portify.steps.panel_review import capture_section_hashes


class TestHashSection:

    def test_deterministic_hash(self):
        h1 = hash_section("Hello world")
        h2 = hash_section("Hello world")
        assert h1 == h2

    def test_different_content_different_hash(self):
        h1 = hash_section("Hello world")
        h2 = hash_section("Hello world!")
        assert h1 != h2

    def test_whitespace_normalized(self):
        """Leading/trailing whitespace is stripped."""
        h1 = hash_section("  Hello world  ")
        h2 = hash_section("Hello world")
        assert h1 == h2


class TestExtractSections:

    def test_single_section(self):
        content = "## Section One\n\nContent here.\n"
        sections = extract_sections(content)
        assert "Section One" in sections
        assert "Content here." in sections["Section One"]

    def test_multiple_sections(self):
        content = """\
## Alpha

Alpha content.

## Beta

Beta content.

## Gamma

Gamma content.
"""
        sections = extract_sections(content)
        assert len(sections) == 3
        assert "Alpha" in sections
        assert "Beta" in sections
        assert "Gamma" in sections

    def test_no_sections(self):
        content = "Just plain text without headings."
        sections = extract_sections(content)
        assert len(sections) == 0


class TestVerifyAdditiveOnly:

    def test_no_changes_passes(self):
        content = "## Section A\n\nContent A.\n"
        hashes = {h: hash_section(b) for h, b in extract_sections(content).items()}
        violations = verify_additive_only(hashes, content)
        assert violations == []

    def test_new_section_added_passes(self):
        old = "## Section A\n\nContent A.\n"
        old_hashes = {h: hash_section(b) for h, b in extract_sections(old).items()}
        new = "## Section A\n\nContent A.\n\n## Section B\n\nNew content.\n"
        violations = verify_additive_only(old_hashes, new)
        assert violations == []

    def test_section_modified_fails(self):
        old = "## Section A\n\nOriginal content.\n"
        old_hashes = {h: hash_section(b) for h, b in extract_sections(old).items()}
        new = "## Section A\n\nModified content.\n"
        violations = verify_additive_only(old_hashes, new)
        assert len(violations) == 1
        assert "modified" in violations[0].lower()

    def test_section_removed_fails(self):
        old = "## Section A\n\nContent A.\n\n## Section B\n\nContent B.\n"
        old_hashes = {h: hash_section(b) for h, b in extract_sections(old).items()}
        new = "## Section A\n\nContent A.\n"
        violations = verify_additive_only(old_hashes, new)
        assert len(violations) == 1
        assert "removed" in violations[0].lower()

    def test_section_modified_and_removed(self):
        old = "## A\n\nOriginal.\n\n## B\n\nContent B.\n\n## C\n\nContent C.\n"
        old_hashes = {h: hash_section(b) for h, b in extract_sections(old).items()}
        new = "## A\n\nChanged.\n"  # B and C removed, A modified
        violations = verify_additive_only(old_hashes, new)
        assert len(violations) == 3  # A modified, B removed, C removed

    def test_empty_old_hashes_always_passes(self):
        violations = verify_additive_only({}, "## New\n\nContent.\n")
        assert violations == []


class TestCaptureAndCompare:
    """Integration test for capture -> compare flow."""

    def test_full_flow_additive(self):
        initial = "## Overview\n\nInitial overview.\n"
        hashes = capture_section_hashes(initial)

        updated = "## Overview\n\nInitial overview.\n\n## Details\n\nNew details.\n"
        violations = verify_additive_only(hashes, updated)
        assert violations == []

    def test_full_flow_modification(self):
        initial = "## Overview\n\nInitial overview.\n"
        hashes = capture_section_hashes(initial)

        updated = "## Overview\n\nRewritten overview.\n"
        violations = verify_additive_only(hashes, updated)
        assert len(violations) == 1
