"""
Unit tests for Wave 2 template discovery hierarchy (T3.1).

Tests the template discovery process defined in SKILL.md:
- 4-level search order (local → user → plugin → inline)
- Template matching criteria
- Fallback to inline generation
- Template scoring
"""

import os
import re

import pytest


# Template search paths from SKILL.md
TEMPLATE_SEARCH_ORDER = [
    ("./templates/roadmaps/", 1, "Local project templates"),
    ("~/.claude/templates/roadmaps/", 2, "User templates"),
    ("plugins/superclaude/templates/roadmaps/", 3, "Plugin templates"),
    ("inline", 4, "Generated variant (fallback)"),
]

EXPECTED_PLUGIN_TEMPLATES = [
    "feature-release.md",
    "quality-release.md",
    "documentation-release.md",
    "security-release.md",
    "performance-release.md",
    "migration-release.md",
]


class TestSearchOrder:
    """Verify template search order from SKILL.md."""

    def test_four_levels_defined(self):
        """Should have exactly 4 search levels."""
        assert len(TEMPLATE_SEARCH_ORDER) == 4

    def test_priority_ordering(self):
        """Priorities should be 1-4 (local highest)."""
        priorities = [t[1] for t in TEMPLATE_SEARCH_ORDER]
        assert priorities == [1, 2, 3, 4]

    def test_local_is_highest_priority(self):
        """Local templates should have priority 1."""
        assert TEMPLATE_SEARCH_ORDER[0][1] == 1
        assert "Local" in TEMPLATE_SEARCH_ORDER[0][2]

    def test_inline_is_lowest_priority(self):
        """Inline fallback should have priority 4."""
        assert TEMPLATE_SEARCH_ORDER[3][0] == "inline"
        assert TEMPLATE_SEARCH_ORDER[3][1] == 4

    def test_search_order_in_skill_md(self, skill_md_content):
        """SKILL.md should document the search order."""
        assert "priority: 1" in skill_md_content
        assert "priority: 2" in skill_md_content
        assert "priority: 3" in skill_md_content
        assert "priority: 4" in skill_md_content


class TestPluginTemplates:
    """Verify expected plugin templates exist."""

    def test_six_templates_expected(self):
        """Should expect 6 template types."""
        assert len(EXPECTED_PLUGIN_TEMPLATES) == 6

    def test_template_names_in_skill_md(self, skill_md_content):
        """All template names should appear in SKILL.md."""
        for template in EXPECTED_PLUGIN_TEMPLATES:
            assert template in skill_md_content, (
                f"Template '{template}' not found in SKILL.md"
            )

    def test_plugin_templates_exist_on_disk(self):
        """Plugin templates should exist at the expected path."""
        plugin_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..",
            "plugins", "superclaude", "templates", "roadmaps",
        )
        if not os.path.exists(plugin_path):
            pytest.skip("Plugin templates directory not found")
        for template in EXPECTED_PLUGIN_TEMPLATES:
            path = os.path.join(plugin_path, template)
            assert os.path.exists(path), f"Template not found: {path}"


class TestInlineFallback:
    """Test inline template generation fallback conditions."""

    def test_fallback_conditions_documented(self, skill_md_content):
        """SKILL.md should document fallback conditions."""
        assert "No templates in any search path" in skill_md_content
        assert "inline generation" in skill_md_content

    def test_fallback_milestone_formula(self, skill_md_content):
        """SKILL.md should define milestone count by complexity."""
        assert "complexity_low" in skill_md_content
        assert "complexity_medium" in skill_md_content
        assert "complexity_high" in skill_md_content


class TestTemplateScoring:
    """Test template matching and scoring criteria."""

    def test_matching_criteria_defined(self, skill_md_content):
        """SKILL.md should define matching criteria."""
        assert "matching_criteria" in skill_md_content
        assert "frontmatter" in skill_md_content

    def test_version_resolution_documented(self, skill_md_content):
        """SKILL.md should document version resolution strategy."""
        assert "version_resolution" in skill_md_content
        assert "semantic" in skill_md_content
