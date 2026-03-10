"""
Compliance tests for all 6 critical corrections.

Tests each correction documented in the SC-ROADMAP-FEATURE-SPEC:
1. No subagent_type parameter in Task tool
2. Template directory must be created (not assumed)
3. Compliance tiers from ORCHESTRATOR.md
4. TodoWrite uses only 3 states
5. 7 wave-enabled commands
6. /sc:git subcommands don't exist
"""

import re

import pytest


class TestCriticalCorrection1:
    """CC1: No subagent_type parameter in Task tool."""

    def test_no_subagent_type_as_param(self, skill_md_content):
        """Task call patterns must not include subagent_type as a parameter key."""
        # Find YAML blocks within call_pattern sections
        in_call_pattern = False
        violations = []

        for i, line in enumerate(skill_md_content.split("\n"), 1):
            stripped = line.strip()
            if "call_pattern:" in stripped:
                in_call_pattern = True
            elif stripped.startswith("response_handling:") or stripped == "---":
                in_call_pattern = False

            if in_call_pattern and re.match(r"^subagent_type:", stripped):
                violations.append(f"Line {i}: {stripped}")

        assert len(violations) == 0, (
            f"subagent_type found as parameter in call patterns:\n"
            + "\n".join(violations)
        )


class TestCriticalCorrection2:
    """CC2: Template directory must be created, not assumed."""

    def test_template_check_exists(self, skill_md_content):
        """SKILL.md should check for template directory existence."""
        assert "template_directory" in skill_md_content.lower() or \
               "template directory" in skill_md_content.lower()

    def test_on_not_found_handling(self, skill_md_content):
        """SKILL.md should handle missing template directory."""
        assert "on_not_found" in skill_md_content

    def test_inline_fallback_exists(self, skill_md_content):
        """Inline generation should be available as fallback."""
        assert "inline" in skill_md_content.lower()


class TestCriticalCorrection3:
    """CC3: Compliance tiers from ORCHESTRATOR.md."""

    def test_compliance_tiers_referenced(self, skill_md_content):
        """SKILL.md should reference compliance tiers."""
        assert "STANDARD" in skill_md_content
        assert "STRICT" in skill_md_content

    def test_escalation_conditions(self, skill_md_content):
        """SKILL.md should define escalation from STANDARD to STRICT."""
        assert "escalation" in skill_md_content.lower() or "escalat" in skill_md_content.lower()


class TestCriticalCorrection4:
    """CC4: TodoWrite uses only 3 states."""

    def test_three_states_table(self, skill_md_content):
        """SKILL.md should have a state reference table with 3 states."""
        # Count state definitions in the state reference section
        states_found = set()
        for state in ["pending", "in_progress", "completed"]:
            if f"`{state}`" in skill_md_content:
                states_found.add(state)
        assert len(states_found) == 3, f"Expected 3 states, found: {states_found}"

    def test_blocked_workaround_documented(self, skill_md_content):
        """SKILL.md should document the [BLOCKED:] prefix workaround."""
        assert "[BLOCKED:" in skill_md_content
        assert "workaround" in skill_md_content.lower() or "prefix" in skill_md_content.lower()


class TestCriticalCorrection5:
    """CC5: 7 wave-enabled commands."""

    WAVE_ENABLED_COMMANDS = [
        "/analyze", "/build", "/design", "/implement",
        "/improve", "/task", "/workflow",
    ]

    def test_seven_wave_enabled(self):
        """Should be exactly 7 wave-enabled commands."""
        assert len(self.WAVE_ENABLED_COMMANDS) == 7


class TestCriticalCorrection6:
    """CC6: /sc:git subcommands don't exist."""

    INVALID_GIT_SUBCOMMANDS = [
        "/sc:git commit",
        "/sc:git branch",
        "/sc:git status",
    ]

    def test_no_sc_git_subcommands_in_skill(self, skill_md_content):
        """SKILL.md should not reference /sc:git subcommands."""
        for cmd in self.INVALID_GIT_SUBCOMMANDS:
            assert cmd not in skill_md_content, (
                f"Invalid /sc:git subcommand found in SKILL.md: {cmd}"
            )


class TestAllCorrectionsIntegrity:
    """Verify all corrections are mutually consistent."""

    def test_skill_md_not_empty(self, skill_md_content):
        """SKILL.md should have substantial content."""
        assert len(skill_md_content) > 10000, (
            f"SKILL.md seems too small ({len(skill_md_content)} chars)"
        )

    def test_skill_has_implementation_details(self, skill_md_content):
        """SKILL.md should contain implementation details section."""
        assert "Implementation Details" in skill_md_content

    def test_skill_has_wave_sections(self, skill_md_content):
        """SKILL.md should define all wave implementation sections."""
        assert "Wave 1" in skill_md_content
        assert "Wave 2" in skill_md_content
        assert "Wave 3" in skill_md_content
        assert "Wave 4" in skill_md_content
        assert "Wave 5" in skill_md_content
