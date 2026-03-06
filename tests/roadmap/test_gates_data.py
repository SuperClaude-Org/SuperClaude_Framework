"""Tests for roadmap/gates.py -- gate criteria data definitions and semantic checks."""

from __future__ import annotations

import pytest

from superclaude.cli.roadmap.gates import (
    ALL_GATES,
    DEBATE_GATE,
    DIFF_GATE,
    EXTRACT_GATE,
    GENERATE_A_GATE,
    GENERATE_B_GATE,
    MERGE_GATE,
    SCORE_GATE,
    TEST_STRATEGY_GATE,
    _convergence_score_valid,
    _frontmatter_values_non_empty,
    _has_actionable_content,
    _no_duplicate_headings,
    _no_heading_gaps,
)
from superclaude.cli.pipeline.models import GateCriteria


class TestGateInstances:
    def test_all_gates_are_gate_criteria(self):
        for name, gate in ALL_GATES:
            assert isinstance(gate, GateCriteria), f"{name} is not GateCriteria"

    def test_eight_gates_defined(self):
        assert len(ALL_GATES) == 8

    def test_extract_gate_fields(self):
        assert "functional_requirements" in EXTRACT_GATE.required_frontmatter_fields
        assert "complexity_score" in EXTRACT_GATE.required_frontmatter_fields
        assert "complexity_class" in EXTRACT_GATE.required_frontmatter_fields
        assert EXTRACT_GATE.enforcement_tier == "STANDARD"
        assert EXTRACT_GATE.min_lines == 50

    def test_generate_gates_are_strict(self):
        assert GENERATE_A_GATE.enforcement_tier == "STRICT"
        assert GENERATE_B_GATE.enforcement_tier == "STRICT"

    def test_generate_gates_have_semantic_checks(self):
        assert GENERATE_A_GATE.semantic_checks is not None
        assert len(GENERATE_A_GATE.semantic_checks) == 2
        assert GENERATE_B_GATE.semantic_checks is not None
        assert len(GENERATE_B_GATE.semantic_checks) == 2

    def test_diff_gate_standard(self):
        assert DIFF_GATE.enforcement_tier == "STANDARD"
        assert "total_diff_points" in DIFF_GATE.required_frontmatter_fields

    def test_debate_gate_strict_with_convergence(self):
        assert DEBATE_GATE.enforcement_tier == "STRICT"
        assert "convergence_score" in DEBATE_GATE.required_frontmatter_fields
        assert DEBATE_GATE.semantic_checks is not None

    def test_merge_gate_has_three_semantic_checks(self):
        assert MERGE_GATE.enforcement_tier == "STRICT"
        assert len(MERGE_GATE.semantic_checks) == 3
        check_names = {c.name for c in MERGE_GATE.semantic_checks}
        assert check_names == {"no_heading_gaps", "cross_refs_resolve", "no_duplicate_headings"}

    def test_score_gate_standard(self):
        assert SCORE_GATE.enforcement_tier == "STANDARD"
        assert "base_variant" in SCORE_GATE.required_frontmatter_fields

    def test_test_strategy_gate_standard(self):
        assert TEST_STRATEGY_GATE.enforcement_tier == "STANDARD"
        assert "validation_milestones" in TEST_STRATEGY_GATE.required_frontmatter_fields


class TestSemanticCheckFunctions:
    def test_no_heading_gaps_valid(self):
        content = "# H1\n## H2\n### H3\n#### H4\n"
        assert _no_heading_gaps(content) is True

    def test_no_heading_gaps_skip(self):
        content = "## H2\n#### H4\n"
        assert _no_heading_gaps(content) is False

    def test_no_heading_gaps_empty(self):
        assert _no_heading_gaps("") is True

    def test_no_duplicate_headings_clean(self):
        content = "## Alpha\n### Beta\n## Gamma\n### Delta\n"
        assert _no_duplicate_headings(content) is True

    def test_no_duplicate_headings_h2_dup(self):
        content = "## Alpha\n### Beta\n## Alpha\n"
        assert _no_duplicate_headings(content) is False

    def test_no_duplicate_headings_h3_dup(self):
        content = "### Beta\ntext\n### Beta\n"
        assert _no_duplicate_headings(content) is False

    def test_frontmatter_values_non_empty_valid(self):
        content = "---\ntitle: Hello\nversion: 1.0\n---\n"
        assert _frontmatter_values_non_empty(content) is True

    def test_frontmatter_values_non_empty_missing_value(self):
        content = "---\ntitle: \nversion: 1.0\n---\n"
        assert _frontmatter_values_non_empty(content) is False

    def test_has_actionable_content_with_bullets(self):
        content = "## Plan\n- Step one\n- Step two\n"
        assert _has_actionable_content(content) is True

    def test_has_actionable_content_with_numbers(self):
        content = "## Plan\n1. Step one\n2. Step two\n"
        assert _has_actionable_content(content) is True

    def test_has_actionable_content_none(self):
        content = "## Plan\nJust text here\nNo lists\n"
        assert _has_actionable_content(content) is False

    def test_convergence_score_valid_good(self):
        content = "---\nconvergence_score: 0.85\nrounds_completed: 2\n---\n"
        assert _convergence_score_valid(content) is True

    def test_convergence_score_valid_boundary_zero(self):
        content = "---\nconvergence_score: 0.0\n---\n"
        assert _convergence_score_valid(content) is True

    def test_convergence_score_valid_boundary_one(self):
        content = "---\nconvergence_score: 1.0\n---\n"
        assert _convergence_score_valid(content) is True

    def test_convergence_score_out_of_range(self):
        content = "---\nconvergence_score: 1.5\n---\n"
        assert _convergence_score_valid(content) is False

    def test_convergence_score_not_a_number(self):
        content = "---\nconvergence_score: high\n---\n"
        assert _convergence_score_valid(content) is False

    def test_convergence_score_missing(self):
        content = "---\nother_field: value\n---\n"
        assert _convergence_score_valid(content) is False
