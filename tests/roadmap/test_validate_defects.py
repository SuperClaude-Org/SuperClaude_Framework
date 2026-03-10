"""Known-defect detection tests -- SC-006.

Tests with intentionally defective inputs that verify the validation subsystem
detects known classes of defects:

1. Duplicate D-IDs: _no_duplicate_headings semantic check
2. Missing milestone/frontmatter: gate_passed rejects missing fields
3. Untraced requirements: frontmatter_values_non_empty rejects empty values
4. Cross-file inconsistency: gate_passed rejects missing required fields

Since the LLM-based validator detects semantic defects, these tests validate
the gate checking layer that enforces structural correctness on validator output.
Each test uses intentionally defective input and asserts the gate produces a
failure (BLOCKING finding equivalent).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.pipeline.gates import gate_passed
from superclaude.cli.pipeline.models import GateCriteria, SemanticCheck
from superclaude.cli.roadmap.gates import (
    _frontmatter_values_non_empty,
    _no_duplicate_headings,
    _no_heading_gaps,
)
from superclaude.cli.roadmap.validate_gates import (
    ADVERSARIAL_MERGE_GATE,
    REFLECT_GATE,
    _has_agreement_table,
)


class TestDuplicateDIDDetection:
    """Defect class: duplicate deliverable IDs (duplicate headings)."""

    def test_duplicate_h2_headings_detected(self):
        """_no_duplicate_headings rejects content with duplicate H2 headings."""
        content = (
            "## Phase 1: Setup\n"
            "Content for phase 1\n"
            "## Phase 2: Implementation\n"
            "Content for phase 2\n"
            "## Phase 1: Setup\n"  # Duplicate!
            "Duplicate content\n"
        )
        assert _no_duplicate_headings(content) is False

    def test_duplicate_h3_headings_detected(self):
        """_no_duplicate_headings rejects content with duplicate H3 headings."""
        content = (
            "## Phase 1\n"
            "### D-001: Auth Module\n"
            "Description\n"
            "### D-002: Database\n"
            "Description\n"
            "### D-001: Auth Module\n"  # Duplicate D-ID!
            "Duplicate\n"
        )
        assert _no_duplicate_headings(content) is False

    def test_unique_headings_pass(self):
        """Unique headings pass the check."""
        content = (
            "## Phase 1\n"
            "### D-001: Auth\n"
            "## Phase 2\n"
            "### D-002: Database\n"
        )
        assert _no_duplicate_headings(content) is True

    def test_gate_rejects_duplicate_headings_in_strict_mode(self, tmp_path):
        """STRICT gate with no_duplicate_headings semantic check rejects duplicates."""
        gate = GateCriteria(
            required_frontmatter_fields=["spec_source"],
            min_lines=5,
            enforcement_tier="STRICT",
            semantic_checks=[
                SemanticCheck(
                    name="no_duplicate_headings",
                    check_fn=_no_duplicate_headings,
                    failure_message="Duplicate headings detected",
                ),
            ],
        )
        f = tmp_path / "roadmap.md"
        f.write_text(
            "---\nspec_source: test\n---\n"
            "## Phase 1\n"
            "### D-001: Module A\n"
            "Content\n"
            "### D-001: Module A\n"  # Duplicate
            "More content\n"
            + "\n".join(f"line {i}" for i in range(10)),
        )
        passed, reason = gate_passed(f, gate)
        assert passed is False
        assert "no_duplicate_headings" in reason


class TestMissingMilestoneDetection:
    """Defect class: missing milestone references (missing frontmatter fields)."""

    def test_missing_frontmatter_field_detected(self, tmp_path):
        """Gate rejects output missing required frontmatter field."""
        f = tmp_path / "report.md"
        f.write_text(
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: 0\n"
            # tasklist_ready missing!
            "---\n"
            + "\n".join(f"line {i}" for i in range(25)),
        )
        passed, reason = gate_passed(f, REFLECT_GATE)
        assert passed is False
        assert "tasklist_ready" in reason

    def test_missing_validation_mode_detected(self, tmp_path):
        """Adversarial merge gate rejects output missing validation_mode."""
        f = tmp_path / "report.md"
        f.write_text(
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: 0\n"
            "tasklist_ready: true\n"
            # validation_mode missing!
            "validation_agents: opus,haiku\n"
            "---\n"
            + "\n".join(f"line {i}" for i in range(35)),
        )
        passed, reason = gate_passed(f, ADVERSARIAL_MERGE_GATE)
        assert passed is False
        assert "validation_mode" in reason

    def test_all_required_fields_present_passes(self, tmp_path):
        """Gate passes when all required fields are present."""
        f = tmp_path / "report.md"
        content = (
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: 0\n"
            "tasklist_ready: true\n"
            "---\n"
            + "\n".join(f"line {i}" for i in range(25))
        )
        f.write_text(content)
        passed, reason = gate_passed(f, REFLECT_GATE)
        # REFLECT_GATE is STANDARD tier, so semantic checks are not run
        assert passed is True


class TestUntracedRequirementDetection:
    """Defect class: untraced requirements (empty frontmatter values)."""

    def test_empty_frontmatter_value_detected(self):
        """_frontmatter_values_non_empty rejects empty field values."""
        content = (
            "---\n"
            "blocking_issues_count: \n"  # Empty value!
            "warnings_count: 0\n"
            "tasklist_ready: true\n"
            "---\n"
        )
        assert _frontmatter_values_non_empty(content) is False

    def test_all_empty_values_detected(self):
        """All-empty frontmatter values are rejected."""
        content = (
            "---\n"
            "blocking_issues_count: \n"
            "warnings_count: \n"
            "tasklist_ready: \n"
            "---\n"
        )
        assert _frontmatter_values_non_empty(content) is False

    def test_non_empty_values_pass(self):
        """All non-empty frontmatter values pass."""
        content = (
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: 2\n"
            "tasklist_ready: true\n"
            "---\n"
        )
        assert _frontmatter_values_non_empty(content) is True

    def test_strict_gate_rejects_empty_values(self, tmp_path):
        """STRICT gate with frontmatter_values_non_empty rejects empty values."""
        f = tmp_path / "report.md"
        f.write_text(
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: \n"  # Empty!
            "tasklist_ready: true\n"
            "validation_mode: adversarial\n"
            "validation_agents: opus,haiku\n"
            "---\n"
            "\n"
            "## Agreement Table\n"
            "| Item | Agreement |\n"
            "|------|----------|\n"
            "| R-001 | Yes |\n"
            + "\n".join(f"line {i}" for i in range(25)),
        )
        passed, reason = gate_passed(f, ADVERSARIAL_MERGE_GATE)
        assert passed is False
        assert "frontmatter_values_non_empty" in reason


class TestCrossFileInconsistencyDetection:
    """Defect class: cross-file inconsistency (heading gaps, missing agreement table)."""

    def test_heading_gap_detected(self):
        """_no_heading_gaps rejects content with H2 -> H4 skip."""
        content = (
            "## Phase 1\n"
            "#### D-001: Implementation\n"  # Skips H3!
            "Content\n"
        )
        assert _no_heading_gaps(content) is False

    def test_no_heading_gap_passes(self):
        """Proper heading hierarchy passes."""
        content = (
            "## Phase 1\n"
            "### Milestone 1\n"
            "#### D-001: Implementation\n"
            "Content\n"
        )
        assert _no_heading_gaps(content) is True

    def test_missing_agreement_table_in_adversarial_merge(self, tmp_path):
        """Adversarial merge gate rejects output without agreement table."""
        f = tmp_path / "report.md"
        f.write_text(
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: 0\n"
            "tasklist_ready: true\n"
            "validation_mode: adversarial\n"
            "validation_agents: opus,haiku\n"
            "---\n"
            "\n"
            "## Findings\n"
            "No findings.\n"
            "\n"
            "## Summary\n"
            "All good.\n"
            + "\n".join(f"line {i}" for i in range(25)),
        )
        passed, reason = gate_passed(f, ADVERSARIAL_MERGE_GATE)
        assert passed is False
        assert "agreement_table_present" in reason

    def test_gate_file_below_min_lines(self, tmp_path):
        """Gate rejects output below minimum line count."""
        f = tmp_path / "report.md"
        f.write_text(
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: 0\n"
            "tasklist_ready: true\n"
            "---\n"
            "Short content.\n"
        )
        passed, reason = gate_passed(f, REFLECT_GATE)
        assert passed is False
        assert "minimum line count" in reason
