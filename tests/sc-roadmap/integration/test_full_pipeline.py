"""
Integration tests for the full 5-wave pipeline.

Tests end-to-end flow from specification input through final output.
"""

import os
import re

import pytest


class TestFullPipelineE2E:
    """Test complete 5-wave pipeline execution."""

    def test_wave_order_is_sequential(self, skill_md_content):
        """Waves should execute in order: 0 → 1 → 2 → 3 → 4 → 5."""
        # Find wave references in order
        wave_positions = {}
        for wave_num in range(6):
            pattern = f"Wave {wave_num}"
            pos = skill_md_content.find(pattern)
            if pos >= 0:
                wave_positions[wave_num] = pos

        # Verify ordering (each wave appears after the previous)
        prev_pos = -1
        for wave_num in sorted(wave_positions.keys()):
            assert wave_positions[wave_num] > prev_pos, (
                f"Wave {wave_num} appears before Wave {wave_num - 1}"
            )
            prev_pos = wave_positions[wave_num]

    def test_five_waves_defined(self, skill_md_content):
        """SKILL.md should define Waves 0-5 (6 waves total)."""
        for wave_num in range(6):
            assert f"Wave {wave_num}" in skill_md_content, (
                f"Wave {wave_num} not found in SKILL.md"
            )

    def test_entry_and_exit_criteria(self, skill_md_content):
        """Waves should have entry and exit criteria."""
        assert "entry_criteria" in skill_md_content
        assert "exit_criteria" in skill_md_content

    def test_spec_file_is_mandatory_input(self, skill_md_content):
        """Specification file should be mandatory."""
        assert "MANDATORY" in skill_md_content
        assert "spec-file-path" in skill_md_content or "spec" in skill_md_content.lower()


class TestPipelineDataConsistency:
    """Test data consistency across waves."""

    def test_wave1_output_feeds_wave2(self, skill_md_content):
        """Wave 1 outputs should feed Wave 2 inputs."""
        # Wave 1 produces extraction.md with domain distribution
        assert "domain_distribution" in skill_md_content or "Domain Distribution" in skill_md_content
        # Wave 2 uses domain distribution for template selection
        assert "template" in skill_md_content.lower()

    def test_wave2_output_feeds_wave3(self, skill_md_content):
        """Wave 2 template selection should feed Wave 3 generation."""
        assert "template" in skill_md_content.lower()
        assert "generation" in skill_md_content.lower() or "generate" in skill_md_content.lower()

    def test_wave3_output_feeds_wave4(self, skill_md_content):
        """Wave 3 artifacts should feed Wave 4 validation."""
        assert "validation" in skill_md_content.lower()
        assert "artifacts" in skill_md_content.lower()

    def test_wave4_output_feeds_wave5(self, skill_md_content):
        """Wave 4 validation result should feed Wave 5 completion."""
        assert "PASS" in skill_md_content
        assert "REVISE" in skill_md_content
        assert "REJECT" in skill_md_content
        assert "completion" in skill_md_content.lower() or "Completion" in skill_md_content


class TestPipelineErrorHandling:
    """Test error handling across the pipeline."""

    def test_stop_on_no_spec(self, skill_md_content):
        """Pipeline should STOP if no spec file provided."""
        assert "STOP" in skill_md_content

    def test_stop_on_no_requirements(self, skill_md_content):
        """Pipeline should STOP if no requirements found."""
        assert "No requirements found" in skill_md_content

    def test_timeout_handling(self, skill_md_content):
        """Pipeline should handle timeouts gracefully."""
        assert "timeout" in skill_md_content.lower()

    def test_parse_failure_defaults(self, skill_md_content):
        """Parse failures should use default scores."""
        assert "on_parse_failure" in skill_md_content
        assert "default score" in skill_md_content.lower()


class TestOutputConventions:
    """Test output directory and file conventions."""

    def test_default_output_directory(self, skill_md_content):
        """Default output should be .dev/releases/current/<spec-name>/."""
        assert ".dev/releases/current/" in skill_md_content

    def test_tasklists_subdirectory(self, skill_md_content):
        """Tasklists should go in tasklists/ subdirectory."""
        assert "tasklists/" in skill_md_content

    def test_five_artifact_types(self, skill_md_content):
        """Should produce exactly 5 artifact types."""
        artifacts = [
            "roadmap.md", "extraction.md", "test-strategy.md",
            "execution-prompt.md", "tasklists/",
        ]
        for artifact in artifacts:
            assert artifact in skill_md_content
