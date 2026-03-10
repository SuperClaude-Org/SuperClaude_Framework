"""
Unit tests for Wave 3 artifact generation.

Tests the 5 required artifacts defined in SKILL.md:
- roadmap.md
- extraction.md
- tasklists/M{N}-*.md
- test-strategy.md
- execution-prompt.md
"""

import re

import pytest


# Required artifacts from SKILL.md Outputs section
REQUIRED_ARTIFACTS = [
    {"name": "roadmap.md", "location": "<output>/roadmap.md"},
    {"name": "extraction.md", "location": "<output>/extraction.md"},
    {"name": "tasklists/M{N}-*.md", "location": "<output>/tasklists/"},
    {"name": "test-strategy.md", "location": "<output>/test-strategy.md"},
    {"name": "execution-prompt.md", "location": "<output>/execution-prompt.md"},
]


class TestArtifactDefinitions:
    """Verify artifact definitions in SKILL.md."""

    def test_five_required_artifacts(self):
        """Should define exactly 5 required artifacts."""
        assert len(REQUIRED_ARTIFACTS) == 5

    def test_artifact_names_in_skill_md(self, skill_md_content):
        """All artifact names should appear in SKILL.md."""
        for artifact in REQUIRED_ARTIFACTS:
            name = artifact["name"].split("/")[-1].replace("{N}-*.md", "")
            # The base name should be in the skill doc
            assert name.rstrip("*") in skill_md_content or name in skill_md_content

    def test_artifacts_table_exists(self, skill_md_content):
        """SKILL.md should have an artifacts/outputs table."""
        assert "roadmap.md" in skill_md_content
        assert "extraction.md" in skill_md_content
        assert "test-strategy.md" in skill_md_content
        assert "execution-prompt.md" in skill_md_content


class TestExtractionMdTemplate:
    """Verify extraction.md template sections from SKILL.md."""

    EXPECTED_SECTIONS = [
        "Metadata",
        "Extracted Requirements",
        "Domain Distribution",
        "Complexity Analysis",
        "Persona Assignment",
        "Dependencies",
        "Risks Identified",
        "Success Criteria",
    ]

    def test_all_sections_in_template(self, skill_md_content):
        """Extraction template should define all required sections."""
        for section in self.EXPECTED_SECTIONS:
            assert section in skill_md_content, (
                f"Section '{section}' not found in extraction template"
            )

    def test_metadata_fields(self, skill_md_content):
        """Extraction metadata should include source, generated, generator."""
        assert "Source:" in skill_md_content
        assert "Generated:" in skill_md_content
        assert "Generator:" in skill_md_content


class TestRoadmapMdStructure:
    """Verify roadmap.md output structure."""

    def test_roadmap_defined_as_master(self, skill_md_content):
        """roadmap.md should be described as the master roadmap document."""
        assert "Master roadmap" in skill_md_content or "master roadmap" in skill_md_content

    def test_milestone_hierarchy_described(self, skill_md_content):
        """Roadmap should describe milestone hierarchy."""
        assert "milestone" in skill_md_content.lower()


class TestTasklistMdStructure:
    """Verify tasklist file structure."""

    def test_tasklist_file_pattern(self, skill_md_content):
        """Tasklist files should follow M{N}-{name}.md pattern."""
        pattern = r"M\{N\}-"
        assert re.search(pattern, skill_md_content)

    def test_tasklist_in_subdirectory(self, skill_md_content):
        """Tasklists should be in tasklists/ subdirectory."""
        assert "tasklists/" in skill_md_content


class TestTestStrategyMd:
    """Verify test-strategy.md output."""

    def test_test_strategy_defined(self, skill_md_content):
        """test-strategy.md should be defined as an artifact."""
        assert "test-strategy.md" in skill_md_content


class TestExecutionPromptMd:
    """Verify execution-prompt.md output."""

    def test_execution_prompt_defined(self, skill_md_content):
        """execution-prompt.md should be defined as an artifact."""
        assert "execution-prompt.md" in skill_md_content

    def test_execution_prompt_sections(self, skill_md_content):
        """Execution prompt should have 7 sections per SKILL.md."""
        # The SKILL.md says "sections: 7" for execution-prompt.md
        assert "sections: 7" in skill_md_content


class TestWave3OutputValidation:
    """Test Wave 3 output validation criteria."""

    def test_all_artifacts_exist_check(self, skill_md_content):
        """SKILL.md should verify all artifacts exist."""
        assert "all_artifacts_exist" in skill_md_content

    def test_id_schema_consistency_check(self, skill_md_content):
        """SKILL.md should verify ID schema consistency."""
        assert "id_schema_consistent" in skill_md_content

    def test_cross_references_check(self, skill_md_content):
        """SKILL.md should verify cross-references."""
        assert "cross_references_valid" in skill_md_content
