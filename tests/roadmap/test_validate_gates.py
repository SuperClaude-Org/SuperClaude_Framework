"""Tests for roadmap/validate_gates.py -- validation gate criteria and semantic checks."""

from __future__ import annotations

import pytest

from superclaude.cli.roadmap.validate_gates import (
    ADVERSARIAL_MERGE_GATE,
    REFLECT_GATE,
    _has_agreement_table,
)
from superclaude.cli.pipeline.models import GateCriteria


class TestReflectGate:
    def test_is_gate_criteria(self):
        assert isinstance(REFLECT_GATE, GateCriteria)

    def test_reflect_gate_is_strict(self):
        assert REFLECT_GATE.enforcement_tier == "STRICT"

    def test_reflect_gate_semantic_checks_execute(self):
        """Verify semantic checks execute and produce correct results under STRICT tier."""
        content = "---\nblocking_issues_count: 0\nwarnings_count: 2\ntasklist_ready: true\n---\n"
        assert REFLECT_GATE.semantic_checks is not None
        for check in REFLECT_GATE.semantic_checks:
            assert check.check_fn(content) is True

    def test_min_lines(self):
        assert REFLECT_GATE.min_lines == 20

    def test_required_frontmatter_fields(self):
        assert "blocking_issues_count" in REFLECT_GATE.required_frontmatter_fields
        assert "warnings_count" in REFLECT_GATE.required_frontmatter_fields
        assert "tasklist_ready" in REFLECT_GATE.required_frontmatter_fields
        assert len(REFLECT_GATE.required_frontmatter_fields) == 3

    def test_has_semantic_checks(self):
        assert REFLECT_GATE.semantic_checks is not None
        assert len(REFLECT_GATE.semantic_checks) == 1
        assert REFLECT_GATE.semantic_checks[0].name == "frontmatter_values_non_empty"

    def test_valid_input_passes_semantic(self):
        content = "---\nblocking_issues_count: 0\nwarnings_count: 2\ntasklist_ready: true\n---\n"
        for check in REFLECT_GATE.semantic_checks:
            assert check.check_fn(content) is True

    def test_empty_value_fails_semantic(self):
        content = "---\nblocking_issues_count: \nwarnings_count: 2\ntasklist_ready: true\n---\n"
        check = REFLECT_GATE.semantic_checks[0]
        assert check.check_fn(content) is False

    def test_missing_frontmatter_fails_semantic(self):
        content = "No frontmatter here, just plain text.\n"
        check = REFLECT_GATE.semantic_checks[0]
        assert check.check_fn(content) is False


class TestAdversarialMergeGate:
    def test_is_gate_criteria(self):
        assert isinstance(ADVERSARIAL_MERGE_GATE, GateCriteria)

    def test_enforcement_strict(self):
        assert ADVERSARIAL_MERGE_GATE.enforcement_tier == "STRICT"

    def test_min_lines(self):
        assert ADVERSARIAL_MERGE_GATE.min_lines == 30

    def test_required_frontmatter_fields(self):
        fields = ADVERSARIAL_MERGE_GATE.required_frontmatter_fields
        assert "blocking_issues_count" in fields
        assert "warnings_count" in fields
        assert "tasklist_ready" in fields
        assert "validation_mode" in fields
        assert "validation_agents" in fields
        assert len(fields) == 5

    def test_has_two_semantic_checks(self):
        assert ADVERSARIAL_MERGE_GATE.semantic_checks is not None
        assert len(ADVERSARIAL_MERGE_GATE.semantic_checks) == 2
        check_names = {c.name for c in ADVERSARIAL_MERGE_GATE.semantic_checks}
        assert check_names == {"frontmatter_values_non_empty", "agreement_table_present"}

    def test_valid_input_passes_all_semantics(self):
        content = (
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: 1\n"
            "tasklist_ready: true\n"
            "validation_mode: adversarial\n"
            "validation_agents: opus,haiku\n"
            "---\n"
            "\n"
            "## Results\n"
            "\n"
            "| Item | Agreement | Notes |\n"
            "|------|-----------|-------|\n"
            "| R-001 | Yes | Both agents agree |\n"
        )
        for check in ADVERSARIAL_MERGE_GATE.semantic_checks:
            assert check.check_fn(content) is True, f"Failed: {check.name}"

    def test_missing_agreement_table_fails(self):
        content = (
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: 0\n"
            "tasklist_ready: true\n"
            "validation_mode: adversarial\n"
            "validation_agents: opus,haiku\n"
            "---\n"
            "\n"
            "## Results\n"
            "No table here, just text.\n"
        )
        agreement_check = next(
            c for c in ADVERSARIAL_MERGE_GATE.semantic_checks
            if c.name == "agreement_table_present"
        )
        assert agreement_check.check_fn(content) is False

    def test_empty_frontmatter_value_fails(self):
        content = "---\nblocking_issues_count: \nwarnings_count: 0\ntasklist_ready: true\nvalidation_mode: adversarial\nvalidation_agents: opus\n---\n"
        fm_check = next(
            c for c in ADVERSARIAL_MERGE_GATE.semantic_checks
            if c.name == "frontmatter_values_non_empty"
        )
        assert fm_check.check_fn(content) is False


class TestHasAgreementTable:
    def test_valid_table(self):
        content = "| Item | Agreement |\n|------|----------|\n| R-001 | Yes |\n"
        assert _has_agreement_table(content) is True

    def test_no_table(self):
        assert _has_agreement_table("Just plain text.\n") is False

    def test_table_without_agreement_keyword(self):
        content = "| Item | Status |\n|------|--------|\n| R-001 | Done |\n"
        assert _has_agreement_table(content) is False

    def test_agreement_in_header_case_insensitive(self):
        content = "| Item | AGREEMENT |\n|------|----------|\n| R-001 | Yes |\n"
        assert _has_agreement_table(content) is True

    def test_agree_keyword_matches(self):
        content = "| Item | Agree |\n|------|-------|\n| R-001 | Yes |\n"
        assert _has_agreement_table(content) is True

    def test_empty_content(self):
        assert _has_agreement_table("") is False
