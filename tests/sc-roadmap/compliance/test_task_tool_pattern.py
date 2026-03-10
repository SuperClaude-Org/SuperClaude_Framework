"""
Compliance tests for Task tool usage patterns.

Verifies Critical Correction #1: No subagent_type parameter in Task calls.
Agent specialization must be embedded in the prompt text.
"""

import re

import pytest


class TestNoSubagentType:
    """Verify SKILL.md does not use subagent_type parameter."""

    def test_no_subagent_type_in_skill_md(self, skill_md_content):
        """SKILL.md should never contain 'subagent_type' as a Task parameter.

        The word may appear in documentation warnings, but never as an
        actual parameter in a call_pattern or task invocation.
        """
        # Find all YAML blocks that look like task call patterns
        call_pattern_blocks = re.findall(
            r"call_pattern:.*?(?=\n\S|\n---|\Z)",
            skill_md_content,
            re.DOTALL,
        )

        for i, block in enumerate(call_pattern_blocks):
            # Within call patterns, subagent_type should NOT appear as a parameter
            lines = block.split("\n")
            for line_num, line in enumerate(lines):
                stripped = line.strip()
                # Skip comment lines and warning documentation
                if stripped.startswith("#") or "CRITICAL" in line:
                    continue
                # Check for subagent_type as a YAML key
                if re.match(r"^subagent_type:", stripped):
                    pytest.fail(
                        f"Found 'subagent_type' as parameter in call_pattern "
                        f"block {i + 1}, line {line_num + 1}: {stripped}"
                    )

    def test_critical_warning_present(self, skill_md_content):
        """SKILL.md should contain the CRITICAL warning about subagent_type."""
        assert "CRITICAL" in skill_md_content
        assert "subagent_type" in skill_md_content
        # The warning text
        assert "does NOT have" in skill_md_content or "does not have" in skill_md_content.lower()

    def test_agent_type_in_prompt(self, skill_md_content):
        """Agent type should be embedded in the prompt text."""
        # Look for prompts that specify agent identity
        assert "You are a quality-engineer" in skill_md_content or \
               "quality-engineer agent" in skill_md_content
        assert "self-review" in skill_md_content


class TestTaskCallStructure:
    """Verify Task call structure matches expected pattern."""

    def test_task_has_description(self, skill_md_content):
        """Task calls should have a 'description' field."""
        # In call_pattern blocks
        assert "description:" in skill_md_content

    def test_task_has_prompt(self, skill_md_content):
        """Task calls should have a 'prompt' field."""
        assert "prompt:" in skill_md_content

    def test_task_tool_referenced(self, skill_md_content):
        """SKILL.md should reference the Task tool."""
        assert "tool: Task" in skill_md_content or "Task" in skill_md_content


class TestParallelTaskExecution:
    """Verify parallel task execution patterns."""

    def test_parallel_validation_documented(self, skill_md_content):
        """Wave 4 parallel validation should be documented."""
        assert "parallel" in skill_md_content.lower()

    def test_quality_and_review_are_independent(self, skill_md_content):
        """Quality engineer and self-review should be marked as independent."""
        assert "independent" in skill_md_content.lower() or "parallel_eligible" in skill_md_content
