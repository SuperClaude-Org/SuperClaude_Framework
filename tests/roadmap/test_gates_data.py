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
    SPEC_FIDELITY_GATE,
    TEST_STRATEGY_GATE,
    _convergence_score_valid,
    _cross_refs_resolve,
    _frontmatter_values_non_empty,
    _has_actionable_content,
    _high_severity_count_zero,
    _no_duplicate_headings,
    _no_heading_gaps,
    _tasklist_ready_consistent,
)
from superclaude.cli.pipeline.models import GateCriteria


class TestGateInstances:
    def test_all_gates_are_gate_criteria(self):
        for name, gate in ALL_GATES:
            assert isinstance(gate, GateCriteria), f"{name} is not GateCriteria"

    def test_nine_gates_defined(self):
        assert len(ALL_GATES) == 9

    def test_extract_gate_fields(self):
        assert "functional_requirements" in EXTRACT_GATE.required_frontmatter_fields
        assert "complexity_score" in EXTRACT_GATE.required_frontmatter_fields
        assert "complexity_class" in EXTRACT_GATE.required_frontmatter_fields
        assert "spec_source" in EXTRACT_GATE.required_frontmatter_fields
        assert "generated" in EXTRACT_GATE.required_frontmatter_fields
        assert "generator" in EXTRACT_GATE.required_frontmatter_fields
        assert "nonfunctional_requirements" in EXTRACT_GATE.required_frontmatter_fields
        assert "total_requirements" in EXTRACT_GATE.required_frontmatter_fields
        assert "domains_detected" in EXTRACT_GATE.required_frontmatter_fields
        assert "risks_identified" in EXTRACT_GATE.required_frontmatter_fields
        assert "dependencies_identified" in EXTRACT_GATE.required_frontmatter_fields
        assert "success_criteria_count" in EXTRACT_GATE.required_frontmatter_fields
        assert "extraction_mode" in EXTRACT_GATE.required_frontmatter_fields
        assert len(EXTRACT_GATE.required_frontmatter_fields) == 13
        assert EXTRACT_GATE.enforcement_tier == "STRICT"
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


class TestCrossRefsResolve:
    def test_cross_refs_resolve_valid(self):
        """Valid cross-references resolve to existing headings."""
        content = (
            "# Document\n"
            "## 1.0 Introduction\n"
            "### 1.1 Overview\n"
            "See section 1.1 for details.\n"
        )
        assert _cross_refs_resolve(content) is True

    def test_cross_refs_resolve_invalid(self):
        """Dangling cross-references emit warnings but return True (warning-only mode)."""
        content = (
            "# Document\n"
            "## 1.0 Introduction\n"
            "See section 9.9 for details.\n"
        )
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = _cross_refs_resolve(content)
            # Warning-only mode: returns True despite dangling ref
            assert result is True
            # But a warning was emitted
            assert len(w) == 1
            assert "9.9" in str(w[0].message)

    def test_cross_refs_resolve_no_refs(self):
        """Documents with no cross-references pass without warnings."""
        content = (
            "# Document\n"
            "## Introduction\n"
            "This document has no cross-references.\n"
        )
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = _cross_refs_resolve(content)
            assert result is True
            assert len(w) == 0


class TestHighSeverityCountZero:
    def test_high_severity_count_zero_passes(self):
        """count=0 returns True."""
        content = "---\nhigh_severity_count: 0\n---\n"
        assert _high_severity_count_zero(content) is True

    def test_high_severity_count_nonzero_fails(self):
        """count>0 returns False."""
        content = "---\nhigh_severity_count: 3\n---\n"
        assert _high_severity_count_zero(content) is False

    def test_high_severity_count_missing_field(self):
        """Missing high_severity_count field returns False."""
        content = "---\nother_field: value\n---\n"
        assert _high_severity_count_zero(content) is False

    def test_high_severity_count_non_integer(self):
        """Non-integer value raises TypeError."""
        content = "---\nhigh_severity_count: high\n---\n"
        with pytest.raises(TypeError, match="must be an integer"):
            _high_severity_count_zero(content)

    def test_high_severity_count_no_frontmatter(self):
        """Missing frontmatter returns False."""
        content = "No frontmatter here.\n"
        assert _high_severity_count_zero(content) is False


class TestTasklistReadyConsistent:
    def test_consistent_ready_true(self):
        """tasklist_ready=true with high=0 and validation_complete=true is consistent."""
        content = "---\ntasklist_ready: true\nhigh_severity_count: 0\nvalidation_complete: true\n---\n"
        assert _tasklist_ready_consistent(content) is True

    def test_inconsistent_ready_true_high_nonzero(self):
        """tasklist_ready=true but high_severity_count>0 is inconsistent."""
        content = "---\ntasklist_ready: true\nhigh_severity_count: 2\nvalidation_complete: true\n---\n"
        assert _tasklist_ready_consistent(content) is False

    def test_consistent_ready_false(self):
        """tasklist_ready=false is always consistent regardless of counts."""
        content = "---\ntasklist_ready: false\nhigh_severity_count: 5\nvalidation_complete: false\n---\n"
        assert _tasklist_ready_consistent(content) is True

    def test_missing_tasklist_ready(self):
        """Missing tasklist_ready field returns False."""
        content = "---\nhigh_severity_count: 0\n---\n"
        assert _tasklist_ready_consistent(content) is False

    def test_missing_high_severity_when_ready_true(self):
        """tasklist_ready=true but missing high_severity_count returns False."""
        content = "---\ntasklist_ready: true\nvalidation_complete: true\n---\n"
        assert _tasklist_ready_consistent(content) is False

    def test_inconsistent_validation_incomplete(self):
        """tasklist_ready=true but validation_complete=false is inconsistent."""
        content = "---\ntasklist_ready: true\nhigh_severity_count: 0\nvalidation_complete: false\n---\n"
        assert _tasklist_ready_consistent(content) is False

    def test_no_frontmatter(self):
        """Missing frontmatter returns False."""
        content = "No frontmatter.\n"
        assert _tasklist_ready_consistent(content) is False


class TestSpecFidelityGate:
    """Tests for SPEC_FIDELITY_GATE -- SC-001, SC-002, SC-007."""

    def test_spec_fidelity_gate_is_gate_criteria(self):
        assert isinstance(SPEC_FIDELITY_GATE, GateCriteria)

    def test_spec_fidelity_gate_is_strict(self):
        """SC-001: Gate must be STRICT enforcement."""
        assert SPEC_FIDELITY_GATE.enforcement_tier == "STRICT"

    def test_spec_fidelity_gate_required_frontmatter_fields(self):
        fields = SPEC_FIDELITY_GATE.required_frontmatter_fields
        assert "high_severity_count" in fields
        assert "medium_severity_count" in fields
        assert "low_severity_count" in fields
        assert "total_deviations" in fields
        assert "validation_complete" in fields
        assert "tasklist_ready" in fields
        assert len(fields) == 6

    def test_spec_fidelity_gate_has_two_semantic_checks(self):
        assert SPEC_FIDELITY_GATE.semantic_checks is not None
        assert len(SPEC_FIDELITY_GATE.semantic_checks) == 2
        check_names = {c.name for c in SPEC_FIDELITY_GATE.semantic_checks}
        assert check_names == {"high_severity_count_zero", "tasklist_ready_consistent"}

    def test_spec_fidelity_gate_reuses_phase2_checks(self):
        """Gate reuses _high_severity_count_zero() and _tasklist_ready_consistent() from Phase 2."""
        checks = SPEC_FIDELITY_GATE.semantic_checks
        hsc_check = next(c for c in checks if c.name == "high_severity_count_zero")
        trc_check = next(c for c in checks if c.name == "tasklist_ready_consistent")
        assert hsc_check.check_fn is _high_severity_count_zero
        assert trc_check.check_fn is _tasklist_ready_consistent

    def test_spec_fidelity_gate_blocks_high_severity(self):
        """SC-001: Gate blocks when high_severity_count > 0."""
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
            c for c in SPEC_FIDELITY_GATE.semantic_checks
            if c.name == "high_severity_count_zero"
        )
        assert hsc_check.check_fn(content) is False

    def test_spec_fidelity_gate_passes_clean(self):
        """SC-002: Gate passes when high_severity_count == 0 and all consistent."""
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
        for check in SPEC_FIDELITY_GATE.semantic_checks:
            assert check.check_fn(content) is True, f"Failed: {check.name}"

    def test_spec_fidelity_gate_degraded_passthrough(self):
        """SC-007: Gate passes in degraded mode (validation_complete=false, fidelity_check_attempted=true).

        When validation_complete=false AND tasklist_ready=false, semantic checks
        should not block: _high_severity_count_zero returns True for count=0,
        and _tasklist_ready_consistent returns True for tasklist_ready=false.
        """
        content = (
            "---\n"
            "high_severity_count: 0\n"
            "medium_severity_count: 0\n"
            "low_severity_count: 0\n"
            "total_deviations: 0\n"
            "validation_complete: false\n"
            "fidelity_check_attempted: true\n"
            "tasklist_ready: false\n"
            "---\n"
            "## Degraded Fidelity Report\n"
            "Spec-fidelity validation could not be completed.\n"
        )
        for check in SPEC_FIDELITY_GATE.semantic_checks:
            assert check.check_fn(content) is True, f"Failed: {check.name}"

    def test_spec_fidelity_gate_min_lines(self):
        assert SPEC_FIDELITY_GATE.min_lines == 20

    def test_spec_fidelity_gate_in_all_gates(self):
        """SPEC_FIDELITY_GATE is registered in ALL_GATES."""
        gate_names = {name for name, _gate in ALL_GATES}
        assert "spec-fidelity" in gate_names
        gate = next(g for name, g in ALL_GATES if name == "spec-fidelity")
        assert gate is SPEC_FIDELITY_GATE
