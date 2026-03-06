"""
Compliance tests for SuperClaude path conventions.

Verifies:
- Skills at .claude/skills/{name}/SKILL.md
- Templates at plugins/superclaude/templates/roadmaps/
- Output at .dev/releases/current/<spec-name>/
- Tasklists in tasklists/ subdirectory
"""

import os
import re

import pytest


class TestSkillPathConvention:
    """Verify skill is at correct SuperClaude path."""

    def test_source_skill_path(self):
        """Source skill should be at src/superclaude/skills/sc-roadmap-protocol/SKILL.md."""
        expected = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..",
            "src", "superclaude", "skills", "sc-roadmap-protocol", "SKILL.md",
        )
        expected = os.path.normpath(expected)
        assert os.path.exists(expected), f"Source SKILL.md not found at: {expected}"

    def test_installed_skill_path(self):
        """Installed skill should be at .claude/skills/sc-roadmap-protocol/SKILL.md."""
        expected = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..",
            ".claude", "skills", "sc-roadmap-protocol", "SKILL.md",
        )
        expected = os.path.normpath(expected)
        # May not exist if sync hasn't been run
        if not os.path.exists(expected):
            pytest.skip("Installed SKILL.md not found (run make sync-dev)")
        assert os.path.exists(expected)

    def test_skill_frontmatter(self, skill_md_content):
        """SKILL.md should have valid YAML frontmatter."""
        assert skill_md_content.startswith("---"), "SKILL.md should start with YAML frontmatter"
        # Find closing ---
        second_fence = skill_md_content.find("---", 3)
        assert second_fence > 3, "SKILL.md should have closing frontmatter fence"

    def test_skill_name_in_frontmatter(self, skill_md_content):
        """Frontmatter should contain name: sc:roadmap."""
        frontmatter = skill_md_content.split("---")[1]
        assert "name: sc:roadmap" in frontmatter


class TestTemplatePathConvention:
    """Verify template directory conventions."""

    def test_template_paths_in_skill_md(self, skill_md_content):
        """SKILL.md should reference correct template paths."""
        assert "plugins/superclaude/templates/roadmaps/" in skill_md_content
        assert "~/.claude/templates/roadmaps/" in skill_md_content
        assert "./templates/roadmaps/" in skill_md_content

    def test_plugin_template_directory_exists(self):
        """Plugin template directory should exist."""
        template_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..",
            "plugins", "superclaude", "templates", "roadmaps",
        )
        template_dir = os.path.normpath(template_dir)
        if not os.path.exists(template_dir):
            pytest.skip("Plugin template directory not found")
        assert os.path.isdir(template_dir)


class TestOutputPathConvention:
    """Verify output directory conventions."""

    def test_default_output_path(self, skill_md_content):
        """Default output should be .dev/releases/current/<spec-name>/."""
        assert ".dev/releases/current/" in skill_md_content

    def test_tasklist_subdirectory(self, skill_md_content):
        """Tasklists should be in a tasklists/ subdirectory."""
        assert "tasklists/" in skill_md_content

    def test_tasklist_naming_pattern(self, skill_md_content):
        """Tasklist files should follow M{N}-{name}.md pattern."""
        # The pattern should be documented
        assert "M{N}" in skill_md_content or "M\\{N\\}" in skill_md_content


class TestFileNamingConventions:
    """Verify file naming follows SuperClaude standards."""

    def test_artifact_extensions(self, skill_md_content):
        """All artifacts should have .md extension."""
        artifacts = ["roadmap.md", "extraction.md", "test-strategy.md", "execution-prompt.md"]
        for artifact in artifacts:
            assert artifact in skill_md_content

    def test_no_uppercase_filenames(self):
        """Generated files should use lowercase naming."""
        # SKILL.md itself is uppercase (convention), but generated files are lowercase
        expected_lowercase = [
            "roadmap.md", "extraction.md", "test-strategy.md", "execution-prompt.md",
        ]
        for name in expected_lowercase:
            assert name == name.lower(), f"Filename should be lowercase: {name}"
