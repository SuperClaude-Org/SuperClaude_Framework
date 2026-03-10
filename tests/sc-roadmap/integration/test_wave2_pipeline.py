"""
Integration tests for Wave 2 pipeline: Template discovery → Selection → Task init.

Tests Wave 2 flow from template discovery through milestone planning.
"""

import pytest


def discover_template(complexity_score, domain_dist, template_dirs_exist=None):
    """
    Simulate template discovery from SKILL.md:
    1. Check local → user → plugin → inline
    2. Return template source and type
    """
    if template_dirs_exist is None:
        template_dirs_exist = {"local": False, "user": False, "plugin": True}

    # Simulate search order
    if template_dirs_exist.get("local"):
        return {"source": "local", "path": "./templates/roadmaps/", "priority": 1}
    if template_dirs_exist.get("user"):
        return {"source": "user", "path": "~/.claude/templates/roadmaps/", "priority": 2}
    if template_dirs_exist.get("plugin"):
        return {"source": "plugin", "path": "plugins/superclaude/templates/roadmaps/", "priority": 3}

    return {"source": "inline", "path": None, "priority": 4}


def select_template_type(domain_dist):
    """Select template type based on dominant domain."""
    TEMPLATE_MAP = {
        "security": "security-release",
        "performance": "performance-release",
        "documentation": "documentation-release",
        "frontend": "feature-release",
        "backend": "feature-release",
    }
    top_domain = max(domain_dist, key=domain_dist.get)
    return TEMPLATE_MAP.get(top_domain, "feature-release")


def plan_milestones(complexity_score, domain_dist):
    """Plan milestone count and structure."""
    if complexity_score < 0.4:
        count_range = (3, 4)
    elif complexity_score <= 0.7:
        count_range = (4, 6)
    else:
        count_range = (5, 8)

    # Add domain-required milestones
    required = []
    domain_milestones = {
        "frontend": "UX Validation",
        "backend": "API Specification",
        "security": "Security Audit",
        "performance": "Performance Baseline",
    }
    for domain, milestone in domain_milestones.items():
        if domain_dist.get(domain, 0) >= 40:
            required.append(milestone)

    return {
        "count_range": count_range,
        "required_milestones": required,
        "complexity": complexity_score,
    }


class TestWave2Pipeline:
    """Test complete Wave 2 pipeline."""

    def test_template_discovery_with_plugin(self):
        """Should find plugin templates when available."""
        result = discover_template(0.5, {}, {"local": False, "user": False, "plugin": True})
        assert result["source"] == "plugin"
        assert result["priority"] == 3

    def test_template_discovery_local_wins(self):
        """Local templates should override plugin templates."""
        result = discover_template(0.5, {}, {"local": True, "user": True, "plugin": True})
        assert result["source"] == "local"
        assert result["priority"] == 1

    def test_template_discovery_fallback_to_inline(self):
        """Should fallback to inline when no templates found."""
        result = discover_template(0.5, {}, {"local": False, "user": False, "plugin": False})
        assert result["source"] == "inline"
        assert result["priority"] == 4

    def test_template_type_for_auth_spec(self):
        """Auth spec should select security-release template."""
        dist = {"security": 45, "backend": 30, "frontend": 15, "performance": 5, "documentation": 5}
        template = select_template_type(dist)
        assert template == "security-release"

    def test_template_type_for_ui_spec(self):
        """UI spec should select feature-release template."""
        dist = {"frontend": 55, "backend": 20, "security": 10, "performance": 10, "documentation": 5}
        template = select_template_type(dist)
        assert template == "feature-release"

    def test_milestone_planning_medium_complexity(self):
        """Medium complexity should plan 4-6 milestones."""
        dist = {"security": 45, "backend": 30, "frontend": 15, "performance": 5, "documentation": 5}
        plan = plan_milestones(0.59, dist)
        assert plan["count_range"] == (4, 6)
        assert "Security Audit" in plan["required_milestones"]

    def test_milestone_planning_low_complexity(self):
        """Low complexity should plan 3-4 milestones."""
        dist = {"frontend": 50, "backend": 20, "security": 10, "performance": 10, "documentation": 10}
        plan = plan_milestones(0.2, dist)
        assert plan["count_range"] == (3, 4)
        assert "UX Validation" in plan["required_milestones"]


class TestWave2DataFlow:
    """Test data flowing through Wave 2 stages."""

    def test_discovery_feeds_selection(self):
        """Template discovery result should inform selection."""
        discovery = discover_template(0.5, {})
        assert "source" in discovery
        assert "priority" in discovery

    def test_selection_feeds_planning(self):
        """Template selection should feed milestone planning."""
        dist = {"security": 45, "backend": 30, "frontend": 15, "performance": 5, "documentation": 5}
        template = select_template_type(dist)
        plan = plan_milestones(0.59, dist)
        # Template and plan should be consistent
        assert template == "security-release"
        assert "Security Audit" in plan["required_milestones"]
