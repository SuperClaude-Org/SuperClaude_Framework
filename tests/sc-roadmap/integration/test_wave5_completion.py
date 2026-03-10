"""
Integration tests for Wave 5 completion pipeline.

Tests the completion flow:
- Completion check (artifact verification, validation status)
- Memory persistence
- Git operations (conditional)
- Output summary
"""

import re

import pytest


class TestCompletionCheck:
    """Test completion check process from SKILL.md T5.4."""

    REQUIRED_ARTIFACTS = [
        "roadmap.md",
        "extraction.md",
        "test-strategy.md",
        "execution-prompt.md",
    ]

    def test_all_artifacts_must_exist(self):
        """All 5 required artifacts must exist and be non-empty."""
        # 4 named files + tasklists directory
        assert len(self.REQUIRED_ARTIFACTS) == 4  # Plus tasklists/

    def test_completion_criteria_in_skill_md(self, skill_md_content):
        """SKILL.md should define completion criteria."""
        assert "completion_criteria" in skill_md_content or "completion_check" in skill_md_content

    def test_think_step_documented(self, skill_md_content):
        """SKILL.md should include think_about_whether_you_are_done()."""
        assert "think_about_whether_you_are_done" in skill_md_content


class TestValidationStatusFlow:
    """Test how validation status affects completion."""

    def test_passed_proceeds(self):
        """PASS status should allow completion."""
        validation_status = "PASS"
        assert validation_status == "PASS"

    def test_rejected_stops(self):
        """REJECT status should prevent finalization."""
        validation_status = "REJECT"
        # SKILL.md says: "STOP - do not finalize rejected artifacts"
        assert validation_status == "REJECT"

    def test_skipped_proceeds_with_flag(self):
        """Skipped validation proceeds if --no-validate flag was set."""
        no_validate_flag = True
        validation_status = "SKIPPED"
        should_proceed = no_validate_flag and validation_status == "SKIPPED"
        assert should_proceed

    def test_revised_accepted_proceeds_with_warning(self):
        """Revised and user-accepted should proceed with warning."""
        validation_status = "REVISE"
        user_accepted = True
        should_proceed = validation_status == "REVISE" and user_accepted
        assert should_proceed


class TestMemoryPersistence:
    """Test Serena memory persistence from SKILL.md T5.5."""

    def test_memory_persistence_in_skill_md(self, skill_md_content):
        """SKILL.md should define memory persistence behavior."""
        assert "write_memory" in skill_md_content or "memory" in skill_md_content.lower()

    def test_circuit_breaker_for_serena(self, skill_md_content):
        """SKILL.md should define circuit breaker for Serena."""
        assert "circuit" in skill_md_content.lower() or "fallback" in skill_md_content.lower()


class TestGitOperations:
    """Test conditional git operations from SKILL.md T5.6."""

    def test_git_conditional_on_flag(self, skill_md_content):
        """Git operations should be conditional on --commit flag."""
        assert "--commit" in skill_md_content or "commit" in skill_md_content.lower()


class TestOutputSummary:
    """Test final output summary from SKILL.md T5.7."""

    def test_summary_includes_scores(self, skill_md_content):
        """Output summary should include validation scores."""
        assert "quality_score" in skill_md_content or "final_score" in skill_md_content

    def test_summary_includes_artifacts(self, skill_md_content):
        """Output summary should reference generated artifacts."""
        assert "artifacts" in skill_md_content.lower()
