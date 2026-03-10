"""
Unit tests for Wave 2 milestone generation (inline template).

Tests the inline template generation algorithm from SKILL.md:
- Milestone count based on complexity
- Domain-specific milestone injection
- Required sections per milestone
- ID schema validation
"""

import re

import pytest


def milestone_count_range(complexity_score: float) -> tuple:
    """
    Determine milestone count range from SKILL.md inline_template_generation:
    - LOW (< 0.4): 3-4 milestones
    - MEDIUM (0.4-0.7): 4-6 milestones
    - HIGH (> 0.7): 5-8 milestones
    """
    if complexity_score < 0.4:
        return (3, 4)
    elif complexity_score <= 0.7:
        return (4, 6)
    else:
        return (5, 8)


def get_required_domain_milestone(domain_dist: dict) -> list:
    """
    Determine domain-specific milestones from SKILL.md:
    - frontend >= 40%: UX Validation
    - backend >= 40%: API Specification
    - security >= 40%: Security Audit
    - performance >= 40%: Performance Baseline
    """
    mapping = {
        "frontend": "UX Validation",
        "backend": "API Specification",
        "security": "Security Audit",
        "performance": "Performance Baseline",
    }
    required = []
    for domain, milestone in mapping.items():
        if domain_dist.get(domain, 0) >= 40:
            required.append(milestone)
    return required


# Required sections per milestone from SKILL.md
REQUIRED_MILESTONE_SECTIONS = [
    "Objective",
    "Type",
    "Priority",
    "Deliverables",
    "Dependencies",
    "Acceptance_Criteria",
    "Risk_Level",
    "Files_Affected",
]


class TestMilestoneCountFormula:
    """Test milestone count ranges by complexity."""

    def test_low_complexity_3_to_4(self):
        """Low complexity (< 0.4) should produce 3-4 milestones."""
        assert milestone_count_range(0.1) == (3, 4)
        assert milestone_count_range(0.3) == (3, 4)
        assert milestone_count_range(0.39) == (3, 4)

    def test_medium_complexity_4_to_6(self):
        """Medium complexity (0.4-0.7) should produce 4-6 milestones."""
        assert milestone_count_range(0.4) == (4, 6)
        assert milestone_count_range(0.55) == (4, 6)
        assert milestone_count_range(0.7) == (4, 6)

    def test_high_complexity_5_to_8(self):
        """High complexity (> 0.7) should produce 5-8 milestones."""
        assert milestone_count_range(0.71) == (5, 8)
        assert milestone_count_range(0.85) == (5, 8)
        assert milestone_count_range(1.0) == (5, 8)

    def test_boundary_0_4(self):
        """Score exactly 0.4 should be MEDIUM (4-6)."""
        assert milestone_count_range(0.4) == (4, 6)

    def test_boundary_0_7(self):
        """Score exactly 0.7 should be MEDIUM (4-6)."""
        assert milestone_count_range(0.7) == (4, 6)


class TestDomainMilestones:
    """Test domain-specific milestone injection."""

    def test_security_adds_audit(self):
        """Security >= 40% should require Security Audit milestone."""
        dist = {"security": 45, "backend": 30, "frontend": 25}
        required = get_required_domain_milestone(dist)
        assert "Security Audit" in required

    def test_frontend_adds_ux_validation(self):
        """Frontend >= 40% should require UX Validation milestone."""
        dist = {"frontend": 50, "backend": 30, "security": 20}
        required = get_required_domain_milestone(dist)
        assert "UX Validation" in required

    def test_backend_adds_api_spec(self):
        """Backend >= 40% should require API Specification milestone."""
        dist = {"backend": 60, "frontend": 25, "security": 15}
        required = get_required_domain_milestone(dist)
        assert "API Specification" in required

    def test_performance_adds_baseline(self):
        """Performance >= 40% should require Performance Baseline milestone."""
        dist = {"performance": 45, "backend": 30, "frontend": 25}
        required = get_required_domain_milestone(dist)
        assert "Performance Baseline" in required

    def test_no_domain_at_40_returns_empty(self):
        """No domain at 40% should return no required milestones."""
        dist = {"frontend": 30, "backend": 30, "security": 20, "performance": 20}
        required = get_required_domain_milestone(dist)
        assert len(required) == 0

    def test_multiple_domains_at_40(self):
        """Multiple domains at 40% should each add their milestone."""
        dist = {"security": 50, "backend": 50, "frontend": 0}
        required = get_required_domain_milestone(dist)
        assert "Security Audit" in required
        assert "API Specification" in required


class TestRequiredMilestoneSections:
    """Test required sections per milestone."""

    def test_eight_sections_required(self):
        """Should require exactly 8 sections per milestone."""
        assert len(REQUIRED_MILESTONE_SECTIONS) == 8

    def test_sections_in_skill_md(self, skill_md_content):
        """All required sections should appear in SKILL.md."""
        for section in REQUIRED_MILESTONE_SECTIONS:
            assert section in skill_md_content, (
                f"Required section '{section}' not found in SKILL.md"
            )


class TestIDSchema:
    """Test milestone and deliverable ID conventions."""

    def test_milestone_id_pattern(self):
        """Milestone IDs should match M{digit} pattern."""
        valid = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"]
        pattern = re.compile(r"^M\d+$")
        for mid in valid:
            assert pattern.match(mid), f"Invalid milestone ID: {mid}"

    def test_deliverable_id_pattern(self):
        """Deliverable IDs should match D{M}.{D}.{N} format."""
        pattern = re.compile(r"^D\d+\.\d+\.\d+$")
        valid = ["D1.1.1", "D2.3.1", "D5.2.4"]
        for did in valid:
            assert pattern.match(did), f"Invalid deliverable ID: {did}"

    def test_task_id_pattern(self):
        """Task IDs should match T{M}.{N} format."""
        pattern = re.compile(r"^T\d+\.\d+$")
        valid = ["T1.1", "T2.3", "T5.5"]
        for tid in valid:
            assert pattern.match(tid), f"Invalid task ID: {tid}"

    def test_risk_id_pattern(self):
        """Risk IDs should match R-{3digits} format."""
        pattern = re.compile(r"^R-\d{3}$")
        valid = ["R-001", "R-002", "R-010"]
        for rid in valid:
            assert pattern.match(rid), f"Invalid risk ID: {rid}"
