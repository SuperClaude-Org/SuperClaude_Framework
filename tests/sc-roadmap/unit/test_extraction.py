"""
Unit tests for Wave 1 requirements extraction engine (T2.2).

Tests the extraction pipeline defined in SKILL.md:
- Title extraction (H1 heading)
- FR-XXX pattern extraction
- NFR-XXX pattern extraction
- Scope boundary detection
- Dependency extraction
- Success criteria extraction
- Risk extraction
- ID assignment
"""

import re

import pytest


class TestTitleExtraction:
    """Step 1: Extract title from H1 heading."""

    TITLE_PATTERN = re.compile(r"^# (.+)$", re.MULTILINE)

    def test_extract_sample_title(self, sample_spec_content):
        """Should extract 'User Authentication System' from sample spec."""
        match = self.TITLE_PATTERN.search(sample_spec_content)
        assert match is not None
        assert match.group(1) == "User Authentication System"

    def test_extract_minimal_title(self, minimal_spec_content):
        """Should extract 'Quick Fix' from minimal spec."""
        match = self.TITLE_PATTERN.search(minimal_spec_content)
        assert match is not None
        assert match.group(1) == "Quick Fix"

    def test_no_title_in_invalid(self, invalid_spec_content):
        """Invalid spec has no H1 heading."""
        match = self.TITLE_PATTERN.search(invalid_spec_content)
        assert match is None


class TestFunctionalRequirements:
    """Step 2: Extract FR-XXX patterns."""

    FR_PATTERNS = [
        re.compile(r"FR-(\d{3}):\s*(.+)", re.MULTILINE),
        re.compile(r"- FR-(\d{3}):\s*(.+)", re.MULTILINE),
    ]

    def _extract_frs(self, content: str) -> list:
        results = []
        for pattern in self.FR_PATTERNS:
            for match in pattern.finditer(content):
                fr_id = f"FR-{match.group(1)}"
                desc = match.group(2).strip()
                if fr_id not in [r[0] for r in results]:
                    results.append((fr_id, desc))
        return results

    def test_sample_has_12_frs(self, sample_spec_content):
        """Sample spec should have 12 functional requirements."""
        frs = self._extract_frs(sample_spec_content)
        assert len(frs) == 12, f"Expected 12 FRs, got {len(frs)}: {frs}"

    def test_fr_ids_sequential(self, sample_spec_content):
        """FR IDs should be sequential (FR-001 through FR-012)."""
        frs = self._extract_frs(sample_spec_content)
        ids = [fr[0] for fr in frs]
        expected = [f"FR-{str(i).zfill(3)}" for i in range(1, 13)]
        assert ids == expected

    def test_minimal_has_2_frs(self, minimal_spec_content):
        """Minimal spec should have 2 functional requirements."""
        frs = self._extract_frs(minimal_spec_content)
        assert len(frs) == 2

    def test_invalid_has_no_frs(self, invalid_spec_content):
        """Invalid spec should have no functional requirements."""
        frs = self._extract_frs(invalid_spec_content)
        assert len(frs) == 0


class TestNonFunctionalRequirements:
    """Step 3: Extract NFR-XXX patterns."""

    NFR_PATTERN = re.compile(r"- NFR-(\d{3}):\s*(.+)", re.MULTILINE)

    def _extract_nfrs(self, content: str) -> list:
        return [
            (f"NFR-{m.group(1)}", m.group(2).strip())
            for m in self.NFR_PATTERN.finditer(content)
        ]

    def test_sample_has_6_nfrs(self, sample_spec_content):
        """Sample spec should have 6 non-functional requirements."""
        nfrs = self._extract_nfrs(sample_spec_content)
        assert len(nfrs) == 6

    def test_nfr_ids_sequential(self, sample_spec_content):
        """NFR IDs should be sequential."""
        nfrs = self._extract_nfrs(sample_spec_content)
        ids = [nfr[0] for nfr in nfrs]
        expected = [f"NFR-{str(i).zfill(3)}" for i in range(1, 7)]
        assert ids == expected


class TestScopeBoundaries:
    """Step 4: Extract In Scope / Out of Scope sections."""

    IN_SCOPE_PATTERNS = [
        re.compile(r"## In Scope", re.MULTILINE),
        re.compile(r"### In Scope", re.MULTILINE),
    ]
    OUT_SCOPE_PATTERNS = [
        re.compile(r"## Out of Scope", re.MULTILINE),
        re.compile(r"### Out of Scope", re.MULTILINE),
    ]

    def test_sample_has_in_scope(self, sample_spec_content):
        """Sample spec should have In Scope section."""
        assert any(p.search(sample_spec_content) for p in self.IN_SCOPE_PATTERNS)

    def test_sample_has_out_scope(self, sample_spec_content):
        """Sample spec should have Out of Scope section."""
        assert any(p.search(sample_spec_content) for p in self.OUT_SCOPE_PATTERNS)


class TestDependencyExtraction:
    """Step 5: Extract dependencies."""

    DEP_PATTERN = re.compile(r"## Dependencies", re.MULTILINE)

    def test_sample_has_dependencies(self, sample_spec_content):
        """Sample spec should have Dependencies section."""
        assert self.DEP_PATTERN.search(sample_spec_content)

    def test_sample_dep_items(self, sample_spec_content):
        """Sample spec should list specific dependencies."""
        assert "PostgreSQL" in sample_spec_content
        assert "Redis" in sample_spec_content


class TestRiskExtraction:
    """Step 7: Extract risks."""

    RISK_PATTERN = re.compile(r"(?<![A-Za-z])R-(\d{3})")

    def test_sample_has_risks(self, sample_spec_content):
        """Sample spec should have R-XXX risk IDs."""
        risks = self.RISK_PATTERN.findall(sample_spec_content)
        assert len(risks) >= 4

    def test_risk_ids_sequential(self, sample_spec_content):
        """Risk IDs should be sequential."""
        risks = self.RISK_PATTERN.findall(sample_spec_content)
        expected = ["001", "002", "003", "004"]
        assert risks == expected


class TestSuccessCriteria:
    """Step 6: Extract success criteria."""

    CRITERIA_PATTERN = re.compile(r"- \[ \] (.+)", re.MULTILINE)

    def test_sample_has_criteria(self, sample_spec_content):
        """Sample spec should have success criteria."""
        criteria = self.CRITERIA_PATTERN.findall(sample_spec_content)
        assert len(criteria) >= 3

    def test_minimal_has_criteria(self, minimal_spec_content):
        """Minimal spec should have success criteria."""
        criteria = self.CRITERIA_PATTERN.findall(minimal_spec_content)
        assert len(criteria) == 2
