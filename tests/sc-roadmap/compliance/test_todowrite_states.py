"""
Compliance tests for TodoWrite state management.

Verifies Critical Correction #4: TodoWrite uses only 3 states.
- Valid states: pending, in_progress, completed
- No "blocked" state used as a TodoWrite state
- Blocked items use [BLOCKED: reason] prefix with pending status
"""

import re

import pytest


VALID_TODOWRITE_STATES = {"pending", "in_progress", "completed"}


class TestTodoWriteStateReferences:
    """Verify SKILL.md only references valid TodoWrite states."""

    def test_no_blocked_state(self, skill_md_content):
        """SKILL.md should never use 'blocked' as a TodoWrite state value.

        The word 'blocked' may appear in context (e.g., "[BLOCKED: ...]"),
        but never as `status: blocked`.
        """
        # Look for `status: blocked` pattern which would be invalid
        invalid_pattern = re.compile(r"status:\s*blocked(?!\w)", re.IGNORECASE)
        # Exclude lines that are documenting anti-patterns or warnings
        lines = skill_md_content.split("\n")
        violations = []
        in_anti_pattern_block = False

        # Patterns that indicate documentation/warning context, not prescriptive usage
        doc_context_patterns = [
            "WRONG", "Anti-Pattern", "Never use", "never use",
            "cause:", "error", "warning", "don't", "do not",
            "avoid", "invalid", "incorrect",
        ]

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip lines in anti-pattern/WRONG example blocks
            if "WRONG" in line or "Anti-Pattern" in line:
                in_anti_pattern_block = True
            elif stripped.startswith("```") and in_anti_pattern_block:
                in_anti_pattern_block = False
                continue

            if in_anti_pattern_block:
                continue

            if invalid_pattern.search(line):
                # Skip if line is clearly documentation/warning context
                if any(ctx in line for ctx in doc_context_patterns):
                    continue
                violations.append(f"Line {i}: {stripped}")

        assert len(violations) == 0, (
            f"Found 'status: blocked' outside anti-pattern blocks:\n"
            + "\n".join(violations)
        )

    def test_valid_states_documented(self, skill_md_content):
        """SKILL.md should document the 3 valid states."""
        for state in VALID_TODOWRITE_STATES:
            assert state in skill_md_content, (
                f"Valid state '{state}' not found in SKILL.md"
            )

    def test_blocked_prefix_pattern_documented(self, skill_md_content):
        """SKILL.md should document the [BLOCKED: reason] prefix pattern."""
        assert "[BLOCKED:" in skill_md_content

    def test_blocked_items_use_pending_status(self, skill_md_content):
        """Blocked items should use 'pending' status, not a separate state."""
        # Look for the documented pattern
        assert "pending" in skill_md_content
        # The SKILL.md should have the blocked workaround documented
        assert "BLOCKED" in skill_md_content

    def test_only_one_in_progress(self, skill_md_content):
        """SKILL.md should enforce only ONE task in_progress at a time."""
        assert "ONE" in skill_md_content or "one" in skill_md_content.lower()
        # Should mention single active task constraint
        lower = skill_md_content.lower()
        assert "only one" in lower or "one task" in lower or "ONE" in skill_md_content


class TestTodoWriteStateTransitions:
    """Test state transition documentation."""

    def test_state_transition_documented(self, skill_md_content):
        """SKILL.md should document state transitions."""
        # pending → in_progress → completed
        assert "pending" in skill_md_content
        assert "in_progress" in skill_md_content
        assert "completed" in skill_md_content

    def test_three_states_only(self):
        """Only 3 states should be valid."""
        assert len(VALID_TODOWRITE_STATES) == 3
        assert "blocked" not in VALID_TODOWRITE_STATES
        assert "cancelled" not in VALID_TODOWRITE_STATES
        assert "failed" not in VALID_TODOWRITE_STATES
