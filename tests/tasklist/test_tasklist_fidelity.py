"""Tests for Phase 4 -- tasklist-fidelity prompt, gate, and layering guard.

Covers:
- T04.01: build_tasklist_fidelity_prompt() structure validation
- T04.02: TASKLIST_FIDELITY_GATE semantic checks and enforcement
- Layering guard: validates roadmap→tasklist ONLY, NOT spec→tasklist
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import GateCriteria
from superclaude.cli.roadmap.gates import (
    _high_severity_count_zero,
    _tasklist_ready_consistent,
)
from superclaude.cli.tasklist.gates import TASKLIST_FIDELITY_GATE
from superclaude.cli.tasklist.prompts import build_tasklist_fidelity_prompt


class TestBuildTasklistFidelityPrompt:
    """T04.01: build_tasklist_fidelity_prompt() function tests."""

    def test_tasklist_fidelity_prompt_returns_string(self):
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert isinstance(prompt, str)

    def test_tasklist_fidelity_prompt_includes_severity_definitions(self):
        """Prompt includes explicit severity definitions (HIGH/MEDIUM/LOW)."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "**HIGH**:" in prompt
        assert "**MEDIUM**:" in prompt
        assert "**LOW**:" in prompt

    def test_tasklist_fidelity_prompt_specifies_yaml_frontmatter(self):
        """Output format specifies YAML frontmatter with severity_counts and tasklist_ready."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "high_severity_count" in prompt
        assert "medium_severity_count" in prompt
        assert "low_severity_count" in prompt
        assert "total_deviations" in prompt
        assert "validation_complete" in prompt
        assert "tasklist_ready" in prompt

    def test_tasklist_fidelity_prompt_includes_output_format_block(self):
        """Prompt includes the standard output format block."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "<output_format>" in prompt
        assert "YAML frontmatter" in prompt

    def test_tasklist_fidelity_prompt_comparison_dimensions(self):
        """Prompt includes all 5 tasklist comparison dimensions."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "Deliverable Coverage" in prompt
        assert "Signature Preservation" in prompt
        assert "Traceability ID Validity" in prompt
        assert "Dependency Chain Correctness" in prompt
        assert "Acceptance Criteria Completeness" in prompt

    def test_tasklist_fidelity_prompt_deviation_format(self):
        """Prompt specifies the 7-column deviation format from Phase 2."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "DEV-NNN" in prompt
        assert "Impact" in prompt
        assert "Recommended Correction" in prompt
        assert "Upstream Quote" in prompt
        assert "Downstream Quote" in prompt
        assert "[MISSING]" in prompt

    def test_tasklist_fidelity_prompt_source_pair(self):
        """Prompt requests source_pair field in frontmatter."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "source_pair" in prompt
        assert "roadmap-to-tasklist" in prompt

    def test_tasklist_fidelity_prompt_fabricated_traceability(self):
        """Prompt explicitly instructs checking for fabricated traceability IDs."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "fabricated" in prompt.lower()
        assert "D-NNNN" in prompt


class TestTasklistValidatesAgainstRoadmapNotSpec:
    """Validation layering guard: tasklist fidelity checks roadmap→tasklist ONLY."""

    def test_prompt_contains_layering_guard(self):
        """Prompt includes explicit validation layering guard."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "VALIDATION LAYERING GUARD" in prompt

    def test_prompt_prohibits_spec_comparison(self):
        """Prompt explicitly prohibits comparing tasklist against specification."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "Do NOT compare the tasklist against the original specification" in prompt

    def test_prompt_restricts_to_roadmap_tasklist(self):
        """Prompt restricts validation to roadmap→tasklist alignment."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "ROADMAP → TASKLIST alignment ONLY" in prompt

    def test_prompt_references_separate_spec_fidelity(self):
        """Prompt explains that spec checks are handled elsewhere."""
        prompt = build_tasklist_fidelity_prompt(
            Path("/tmp/roadmap.md"), Path("/tmp/tasklist/")
        )
        assert "spec-fidelity" in prompt.lower()


class TestTasklistFidelityGate:
    """T04.02: TASKLIST_FIDELITY_GATE semantic checks and enforcement."""

    def test_tasklist_fidelity_gate_is_gate_criteria(self):
        assert isinstance(TASKLIST_FIDELITY_GATE, GateCriteria)

    def test_tasklist_fidelity_gate_is_strict(self):
        """Gate must be STRICT enforcement."""
        assert TASKLIST_FIDELITY_GATE.enforcement_tier == "STRICT"

    def test_tasklist_fidelity_gate_required_frontmatter_fields(self):
        fields = TASKLIST_FIDELITY_GATE.required_frontmatter_fields
        assert "high_severity_count" in fields
        assert "medium_severity_count" in fields
        assert "low_severity_count" in fields
        assert "total_deviations" in fields
        assert "validation_complete" in fields
        assert "tasklist_ready" in fields
        assert len(fields) == 6

    def test_tasklist_fidelity_gate_has_two_semantic_checks(self):
        assert TASKLIST_FIDELITY_GATE.semantic_checks is not None
        assert len(TASKLIST_FIDELITY_GATE.semantic_checks) == 2
        check_names = {c.name for c in TASKLIST_FIDELITY_GATE.semantic_checks}
        assert check_names == {"high_severity_count_zero", "tasklist_ready_consistent"}

    def test_tasklist_fidelity_gate_reuses_phase2_checks(self):
        """Gate reuses _high_severity_count_zero() and _tasklist_ready_consistent() from Phase 2."""
        checks = TASKLIST_FIDELITY_GATE.semantic_checks
        hsc_check = next(c for c in checks if c.name == "high_severity_count_zero")
        trc_check = next(c for c in checks if c.name == "tasklist_ready_consistent")
        assert hsc_check.check_fn is _high_severity_count_zero
        assert trc_check.check_fn is _tasklist_ready_consistent

    def test_tasklist_fidelity_gate_blocks_high_severity(self):
        """Gate blocks when high_severity_count > 0."""
        content = (
            "---\n"
            "high_severity_count: 2\n"
            "medium_severity_count: 1\n"
            "low_severity_count: 0\n"
            "total_deviations: 3\n"
            "validation_complete: true\n"
            "tasklist_ready: false\n"
            "---\n"
            "## Deviation Report\n"
            "- DEV-001: HIGH severity\n"
            "- DEV-002: HIGH severity\n"
            "- DEV-003: MEDIUM severity\n"
        )
        hsc_check = next(
            c for c in TASKLIST_FIDELITY_GATE.semantic_checks
            if c.name == "high_severity_count_zero"
        )
        assert hsc_check.check_fn(content) is False

    def test_tasklist_fidelity_gate_passes_clean_tasklist(self):
        """Gate passes on clean tasklist with no deviations."""
        content = (
            "---\n"
            "high_severity_count: 0\n"
            "medium_severity_count: 0\n"
            "low_severity_count: 0\n"
            "total_deviations: 0\n"
            "validation_complete: true\n"
            "tasklist_ready: true\n"
            "---\n"
            "## Deviation Report\n"
            "No deviations found.\n"
        )
        for check in TASKLIST_FIDELITY_GATE.semantic_checks:
            assert check.check_fn(content) is True, f"Failed: {check.name}"

    def test_tasklist_fidelity_gate_passes_with_medium_low(self):
        """Gate passes when only medium/low severity deviations exist."""
        content = (
            "---\n"
            "high_severity_count: 0\n"
            "medium_severity_count: 2\n"
            "low_severity_count: 1\n"
            "total_deviations: 3\n"
            "validation_complete: true\n"
            "tasklist_ready: true\n"
            "---\n"
            "## Deviation Report\n"
            "- DEV-001: MEDIUM severity\n"
            "- DEV-002: MEDIUM severity\n"
            "- DEV-003: LOW severity\n"
        )
        for check in TASKLIST_FIDELITY_GATE.semantic_checks:
            assert check.check_fn(content) is True, f"Failed: {check.name}"

    def test_tasklist_fidelity_gate_min_lines(self):
        assert TASKLIST_FIDELITY_GATE.min_lines == 20
