"""Tests for gate engine bindings (Steps 3-7).

Covers:
- All gate functions return tuple[bool, str] per NFR-004
- Gate functions exist for SC-001 through SC-007
- STRICT gates enforce: required section count (SC-003), frontmatter
  field counts (SC-004), zero placeholder sentinels (SC-005),
  convergence terminal state (SC-007)
- Gates integrate with pipeline.gates.gate_passed()
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.cli_portify.gates import (
    ANALYZE_WORKFLOW_GATE,
    BRAINSTORM_GAPS_GATE,
    DESIGN_PIPELINE_GATE,
    GATE_REGISTRY,
    PANEL_REVIEW_GATE,
    SYNTHESIZE_SPEC_GATE,
    gate_analyze_workflow,
    gate_brainstorm_gaps,
    gate_design_pipeline,
    gate_panel_review,
    gate_synthesize_spec,
    get_gate_criteria,
)
from superclaude.cli.pipeline.gates import gate_passed
from tests.cli_portify.fixtures.mock_harness import STEP_FIXTURES, get_fixture


def _write_artifact(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class TestGateRegistry:
    """Gate functions exist for SC-001 through SC-007."""

    def test_registry_has_seven_entries(self):
        assert len(GATE_REGISTRY) == 7

    EXPECTED_STEPS = [
        "validate-config",
        "discover-components",
        "analyze-workflow",
        "design-pipeline",
        "synthesize-spec",
        "brainstorm-gaps",
        "panel-review",
    ]

    @pytest.mark.parametrize("step", EXPECTED_STEPS)
    def test_step_in_registry(self, step):
        assert step in GATE_REGISTRY

    def test_get_gate_criteria_works(self):
        criteria = get_gate_criteria("analyze-workflow")
        assert criteria.enforcement_tier == "STRICT"

    def test_get_gate_criteria_raises_on_unknown(self):
        with pytest.raises(KeyError, match="No gate criteria"):
            get_gate_criteria("nonexistent")


class TestGateReturnTypes:
    """All gate functions return tuple[bool, str] per NFR-004."""

    @pytest.mark.parametrize(
        "gate_fn,fixture_name",
        [
            (gate_analyze_workflow, "analyze-workflow"),
            (gate_design_pipeline, "design-pipeline"),
            (gate_synthesize_spec, "synthesize-spec"),
            (gate_brainstorm_gaps, "brainstorm-gaps"),
            (gate_panel_review, "panel-review"),
        ],
    )
    def test_returns_tuple_bool_str(self, gate_fn, fixture_name, tmp_path):
        artifact = _write_artifact(
            tmp_path / f"{fixture_name}.md",
            get_fixture(fixture_name),
        )
        result = gate_fn(artifact)
        assert isinstance(result, tuple)
        assert len(result) == 2
        passed, msg = result
        assert isinstance(passed, bool)
        assert isinstance(msg, str)


class TestAnalyzeWorkflowGate:
    """STRICT gate for SC-003: required section count."""

    def test_passes_on_good_fixture(self, tmp_path):
        artifact = _write_artifact(
            tmp_path / "analysis.md", get_fixture("analyze-workflow")
        )
        passed, msg = gate_analyze_workflow(artifact)
        assert passed is True

    def test_fails_on_missing_file(self, tmp_path):
        passed, msg = gate_analyze_workflow(tmp_path / "nonexistent.md")
        assert passed is False
        assert "not found" in msg.lower()

    def test_fails_on_too_few_sections(self, tmp_path):
        content = """\
---
step: analyze-workflow
source_skill: test
cli_name: test
component_count: 1
analysis_sections: 2
---

## Workflow Summary

Brief summary only.

## Component Analysis

One component.
"""
        # Pad to meet min_lines
        content += "\n" * 10
        artifact = _write_artifact(tmp_path / "analysis.md", content)
        passed, msg = gate_analyze_workflow(artifact)
        assert passed is False
        assert "section_count" in msg.lower() or "sections" in msg.lower()

    def test_enforcement_tier_is_strict(self):
        assert ANALYZE_WORKFLOW_GATE.enforcement_tier == "STRICT"


class TestDesignPipelineGate:
    """STRICT gate for SC-004: frontmatter field counts."""

    def test_passes_on_good_fixture(self, tmp_path):
        artifact = _write_artifact(
            tmp_path / "design.md", get_fixture("design-pipeline")
        )
        passed, msg = gate_design_pipeline(artifact)
        assert passed is True

    def test_fails_on_missing_frontmatter_fields(self, tmp_path):
        content = """\
---
step: design-pipeline
---

## Pipeline Overview

Some content here.
""" + "\n" * 30
        artifact = _write_artifact(tmp_path / "design.md", content)
        passed, msg = gate_design_pipeline(artifact)
        assert passed is False

    def test_enforcement_tier_is_strict(self):
        assert DESIGN_PIPELINE_GATE.enforcement_tier == "STRICT"


class TestSynthesizeSpecGate:
    """STRICT gate for SC-005: zero placeholder sentinels."""

    def test_passes_on_good_fixture(self, tmp_path):
        artifact = _write_artifact(
            tmp_path / "synth.md", get_fixture("synthesize-spec")
        )
        passed, msg = gate_synthesize_spec(artifact)
        assert passed is True

    def test_fails_on_placeholder_sentinels(self, tmp_path):
        content = """\
---
step: synthesize-spec
source_skill: test
cli_name: test
synthesis_version: 1
placeholder_count: 1
---

## Spec

Content with {{SC_PLACEHOLDER:missing_section}} sentinel.
""" + "\n" * 10
        artifact = _write_artifact(tmp_path / "synth.md", content)
        passed, msg = gate_synthesize_spec(artifact)
        assert passed is False
        assert "placeholder" in msg.lower()

    def test_enforcement_tier_is_strict(self):
        assert SYNTHESIZE_SPEC_GATE.enforcement_tier == "STRICT"


class TestBrainstormGapsGate:
    """STANDARD gate for SC-006."""

    def test_passes_on_good_fixture(self, tmp_path):
        artifact = _write_artifact(
            tmp_path / "gaps.md", get_fixture("brainstorm-gaps")
        )
        passed, msg = gate_brainstorm_gaps(artifact)
        assert passed is True

    def test_enforcement_tier_is_standard(self):
        assert BRAINSTORM_GAPS_GATE.enforcement_tier == "STANDARD"

    def test_fails_on_missing_frontmatter(self, tmp_path):
        content = "# No frontmatter\n\nJust content.\n" * 5
        artifact = _write_artifact(tmp_path / "gaps.md", content)
        passed, msg = gate_brainstorm_gaps(artifact)
        assert passed is False


class TestPanelReviewGate:
    """STRICT gate for SC-007: convergence terminal state."""

    def test_passes_on_converged(self, tmp_path):
        artifact = _write_artifact(
            tmp_path / "review.md", get_fixture("panel-review")
        )
        passed, msg = gate_panel_review(artifact)
        assert passed is True

    def test_fails_on_iterate_state(self, tmp_path):
        content = """\
---
step: panel-review
source_skill: test
cli_name: test
iteration: 1
convergence_state: iterate
---

## Review Summary

More work needed.

## Findings

Finding 1.

## Convergence Assessment

Not converged yet.

## Action Items

- Fix item 1
"""
        artifact = _write_artifact(tmp_path / "review.md", content)
        passed, msg = gate_panel_review(artifact)
        assert passed is False
        assert "convergence" in msg.lower()

    def test_passes_on_blocked_state(self, tmp_path):
        content = """\
---
step: panel-review
source_skill: test
cli_name: test
iteration: 3
convergence_state: blocked
---

## Review Summary

Blocked on external dependency.

## Findings

Cannot proceed without API access.

## Convergence Assessment

Blocked - requires external resolution.
"""
        artifact = _write_artifact(tmp_path / "review.md", content)
        passed, msg = gate_panel_review(artifact)
        assert passed is True

    def test_enforcement_tier_is_strict(self):
        assert PANEL_REVIEW_GATE.enforcement_tier == "STRICT"


class TestPipelineGateIntegration:
    """Gates integrate with pipeline.gates.gate_passed()."""

    @pytest.mark.parametrize(
        "step_name",
        [
            "analyze-workflow",
            "design-pipeline",
            "synthesize-spec",
            "brainstorm-gaps",
            "panel-review",
        ],
    )
    def test_gate_passed_with_good_fixture(self, step_name, tmp_path):
        """Known-good fixtures pass through pipeline.gates.gate_passed()."""
        criteria = get_gate_criteria(step_name)
        artifact = _write_artifact(
            tmp_path / f"{step_name}.md",
            get_fixture(step_name),
        )
        passed, reason = gate_passed(artifact, criteria)
        assert passed is True, f"{step_name} failed: {reason}"

    def test_exempt_gate_always_passes(self, tmp_path):
        """EXEMPT tier (validate-config) always passes."""
        criteria = get_gate_criteria("validate-config")
        artifact = tmp_path / "anything.txt"
        # Don't even create the file -- EXEMPT should pass
        passed, reason = gate_passed(artifact, criteria)
        assert passed is True

    def test_strict_gate_fails_on_empty(self, tmp_path):
        """STRICT gate fails on empty file."""
        criteria = get_gate_criteria("analyze-workflow")
        artifact = _write_artifact(tmp_path / "empty.md", "")
        passed, reason = gate_passed(artifact, criteria)
        assert passed is False
