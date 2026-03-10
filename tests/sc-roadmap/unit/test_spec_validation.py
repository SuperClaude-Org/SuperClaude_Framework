"""
Unit tests for Wave 1 specification file validation (T2.1).

Tests the 4-step validation process defined in SKILL.md:
- Step 1: File existence check
- Step 2: File readability (content length > 0)
- Step 3: Minimum content check (> 100 characters)
- Step 4: Required section detection (H1 heading + requirements)
"""

import os
import re

import pytest


class TestFileExistenceValidation:
    """Step 1: File existence check."""

    def test_valid_spec_file_exists(self, sample_spec_path):
        """Valid spec file should exist."""
        assert os.path.exists(sample_spec_path)

    def test_minimal_spec_file_exists(self, minimal_spec_path):
        """Minimal spec file should exist."""
        assert os.path.exists(minimal_spec_path)

    def test_invalid_spec_file_exists(self, invalid_spec_path):
        """Invalid spec file should exist (file exists but content is bad)."""
        assert os.path.exists(invalid_spec_path)

    def test_nonexistent_file_fails(self, tmp_path):
        """Non-existent file should fail validation."""
        fake_path = str(tmp_path / "nonexistent.md")
        assert not os.path.exists(fake_path)


class TestFileReadabilityValidation:
    """Step 2: File readability (content length > 0)."""

    def test_sample_spec_not_empty(self, sample_spec_content):
        """Sample spec should have content."""
        assert len(sample_spec_content) > 0

    def test_minimal_spec_not_empty(self, minimal_spec_content):
        """Minimal spec should have content."""
        assert len(minimal_spec_content) > 0

    def test_empty_file_fails(self, tmp_path):
        """Empty file should fail readability check."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")
        content = empty_file.read_text()
        assert len(content) == 0


class TestMinimumContentCheck:
    """Step 3: Minimum content check (> 100 characters)."""

    def test_sample_spec_exceeds_minimum(self, sample_spec_content):
        """Sample spec should exceed 100 characters."""
        assert len(sample_spec_content) > 100

    def test_minimal_spec_exceeds_minimum(self, minimal_spec_content):
        """Minimal spec should exceed 100 characters."""
        assert len(minimal_spec_content) > 100

    def test_short_content_warns(self):
        """Content under 100 chars should trigger warning."""
        short_content = "# Title\n\nShort content."
        assert len(short_content) < 100


class TestRequiredSectionDetection:
    """Step 4: Required section detection."""

    # H1 heading detection
    H1_PATTERN = re.compile(r"^# .+$", re.MULTILINE)

    # Requirements patterns from SKILL.md
    REQUIREMENTS_PATTERNS = [
        re.compile(r"## Requirements", re.MULTILINE),
        re.compile(r"## Functional Requirements", re.MULTILINE),
        re.compile(r"## FR-", re.MULTILINE),
        re.compile(r"## NFR-", re.MULTILINE),
        re.compile(r"- FR-\d{3}:", re.MULTILINE),
        re.compile(r"- NFR-\d{3}:", re.MULTILINE),
    ]

    def _has_title(self, content: str) -> bool:
        return bool(self.H1_PATTERN.search(content))

    def _has_requirements(self, content: str) -> bool:
        return any(p.search(content) for p in self.REQUIREMENTS_PATTERNS)

    def test_sample_spec_has_title(self, sample_spec_content):
        """Sample spec should have H1 heading."""
        assert self._has_title(sample_spec_content)

    def test_sample_spec_has_requirements(self, sample_spec_content):
        """Sample spec should have FR-XXX patterns."""
        assert self._has_requirements(sample_spec_content)

    def test_minimal_spec_has_title(self, minimal_spec_content):
        """Minimal spec should have H1 heading."""
        assert self._has_title(minimal_spec_content)

    def test_minimal_spec_has_requirements(self, minimal_spec_content):
        """Minimal spec should have requirements section."""
        assert self._has_requirements(minimal_spec_content)

    def test_invalid_spec_no_title(self, invalid_spec_content):
        """Invalid spec should not have H1 heading."""
        assert not self._has_title(invalid_spec_content)

    def test_invalid_spec_no_requirements(self, invalid_spec_content):
        """Invalid spec should not have requirements patterns."""
        assert not self._has_requirements(invalid_spec_content)


class TestErrorMessages:
    """Error messages should match spec Section 8.1."""

    EXPECTED_ERRORS = {
        "file_not_found": "Specification file not found:",
        "empty_file": "Specification file is empty",
        "no_requirements": "No requirements found in specification",
    }

    def test_error_messages_defined_in_skill(self, skill_md_content):
        """All error messages should appear in SKILL.md."""
        for key, msg in self.EXPECTED_ERRORS.items():
            assert msg in skill_md_content, (
                f"Error message '{key}' not found in SKILL.md: {msg}"
            )
