"""Tests for panel-review step (Step 7).

Covers:
- Happy path: mock subprocess converges, SC-007 gate passes
- Quality scoring: clarity, completeness, testability, consistency
- Downstream readiness gate boundary: 7.0 passes, 6.9 fails (SC-009)
- Convergence integration: engine state transitions
- Section hashing additive-only enforcement
- Subprocess timeout
- User review gate
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.cli.cli_portify.config import load_portify_config
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyStatus,
)
from superclaude.cli.cli_portify.steps.panel_review import (
    check_downstream_readiness,
    compute_overall_score,
    count_unaddressed_criticals,
    parse_quality_scores,
    run_panel_review,
    capture_section_hashes,
    generate_panel_report,
    DOWNSTREAM_READINESS_THRESHOLD,
)
from superclaude.cli.cli_portify.convergence import ConvergenceResult, ConvergenceState
from superclaude.cli.cli_portify.utils import verify_additive_only
from tests.cli_portify.fixtures.mock_harness import (
    PANEL_REVIEW_GOOD,
    BRAINSTORM_GAPS_GOOD,
    SYNTHESIZE_SPEC_GOOD,
    patch_portify_process,
)


@pytest.fixture
def workflow_dir(tmp_path: Path) -> Path:
    wf = tmp_path / "sc-test-protocol"
    wf.mkdir()
    (wf / "SKILL.md").write_text("# Test Skill\n\nContent.\n")
    return wf


@pytest.fixture
def config_with_prior_artifacts(workflow_dir: Path, tmp_path: Path):
    """Config with all prior artifacts (Steps 5-6)."""
    output = tmp_path / "output"
    output.mkdir()
    results = output / "results"
    results.mkdir()

    (results / "synthesized-spec.md").write_text(SYNTHESIZE_SPEC_GOOD)
    (results / "brainstorm-gaps.md").write_text(BRAINSTORM_GAPS_GOOD)

    config = load_portify_config(
        workflow_path=str(workflow_dir),
        output_dir=str(output),
        skip_review=True,
    )
    return config


class TestQualityScoring:
    """SC-008: Quality scoring with 4 dimensions."""

    def test_parse_colon_format(self):
        content = """\
## Quality Scores
clarity: 8.5
completeness: 7.0
testability: 9.0
consistency: 8.0
"""
        scores = parse_quality_scores(content)
        assert scores["clarity"] == pytest.approx(8.5)
        assert scores["completeness"] == pytest.approx(7.0)
        assert scores["testability"] == pytest.approx(9.0)
        assert scores["consistency"] == pytest.approx(8.0)

    def test_parse_table_format(self):
        content = """\
| Dimension | Score |
|-----------|-------|
| clarity | 7.5 |
| completeness | 8.0 |
| testability | 6.5 |
| consistency | 9.0 |
"""
        scores = parse_quality_scores(content)
        assert len(scores) == 4

    def test_parse_no_scores(self):
        scores = parse_quality_scores("No quality scores here.")
        assert len(scores) == 0

    def test_overall_is_mean_of_4(self):
        scores = {
            "clarity": 8.0,
            "completeness": 7.0,
            "testability": 9.0,
            "consistency": 6.0,
        }
        overall = compute_overall_score(scores)
        # (8 + 7 + 9 + 6) / 4 = 7.5
        assert overall == pytest.approx(7.5, abs=0.01)

    def test_overall_empty_scores(self):
        assert compute_overall_score({}) == 0.0


class TestDownstreamReadinessGate:
    """SC-009: Boundary at 7.0."""

    def test_boundary_7_0_passes(self):
        assert check_downstream_readiness(7.0) is True

    def test_boundary_6_9_fails(self):
        assert check_downstream_readiness(6.9) is False

    def test_high_score_passes(self):
        assert check_downstream_readiness(9.5) is True

    def test_zero_fails(self):
        assert check_downstream_readiness(0.0) is False


class TestCriticalCounting:

    def test_count_unresolved_criticals(self):
        content = """\
## Findings
1. CRITICAL: Missing auth check
2. CRITICAL: SQL injection risk
3. MEDIUM: Unused import
"""
        assert count_unaddressed_criticals(content) == 2

    def test_resolved_criticals_not_counted(self):
        content = """\
## Findings
1. [RESOLVED] CRITICAL: Missing auth check
2. CRITICAL: SQL injection risk
"""
        assert count_unaddressed_criticals(content) == 1

    def test_no_criticals(self):
        assert count_unaddressed_criticals("All issues resolved.") == 0


class TestSectionHashing:
    """D-0033 / NFR-008: Additive-only enforcement."""

    def test_capture_section_hashes(self):
        content = """\
## Section A

Content for A.

## Section B

Content for B.
"""
        hashes = capture_section_hashes(content)
        assert "Section A" in hashes
        assert "Section B" in hashes
        assert len(hashes) == 2

    def test_additive_only_passes_with_new_section(self):
        old_content = """\
## Section A

Content for A.
"""
        old_hashes = capture_section_hashes(old_content)

        new_content = """\
## Section A

Content for A.

## Section B

New content for B.
"""
        violations = verify_additive_only(old_hashes, new_content)
        assert violations == []

    def test_additive_only_fails_on_modification(self):
        old_content = """\
## Section A

Original content.
"""
        old_hashes = capture_section_hashes(old_content)

        new_content = """\
## Section A

Modified content.
"""
        violations = verify_additive_only(old_hashes, new_content)
        assert len(violations) == 1
        assert "Section A" in violations[0]

    def test_additive_only_fails_on_removal(self):
        old_content = """\
## Section A

Content for A.

## Section B

Content for B.
"""
        old_hashes = capture_section_hashes(old_content)

        new_content = """\
## Section A

Content for A.
"""
        violations = verify_additive_only(old_hashes, new_content)
        assert len(violations) == 1
        assert "Section B" in violations[0]


class TestPanelReportGeneration:
    """D-0034: panel-report.md with machine-readable convergence block."""

    def test_generates_report_with_frontmatter(self, tmp_path):
        conv_result = ConvergenceResult(
            state=ConvergenceState.CONVERGED,
            iterations_completed=2,
        )
        scores = {"clarity": 8.0, "completeness": 7.5, "testability": 9.0, "consistency": 8.5}
        overall = compute_overall_score(scores)
        report_path = tmp_path / "panel-report.md"

        generate_panel_report(
            convergence_result=conv_result,
            quality_scores=scores,
            overall_score=overall,
            downstream_ready=True,
            output_path=report_path,
        )

        assert report_path.exists()
        content = report_path.read_text()
        assert "terminal_state: converged" in content
        assert "iteration_count: 2" in content
        assert "downstream_ready: true" in content
        assert "clarity: 8.0" in content

    def test_escalated_report_includes_reason(self, tmp_path):
        from superclaude.cli.cli_portify.convergence import EscalationReason

        conv_result = ConvergenceResult(
            state=ConvergenceState.ESCALATED,
            iterations_completed=3,
            escalation_reason=EscalationReason.MAX_ITERATIONS,
        )
        report_path = tmp_path / "panel-report.md"

        generate_panel_report(
            convergence_result=conv_result,
            quality_scores={},
            overall_score=0.0,
            downstream_ready=False,
            output_path=report_path,
        )

        content = report_path.read_text()
        assert "terminal_state: escalated" in content
        assert "escalation_reason: max_iterations" in content
        assert "downstream_ready: false" in content


class TestPanelReviewHappyPath:

    def test_produces_pass_result(self, config_with_prior_artifacts):
        with patch_portify_process("panel-review"):
            result = run_panel_review(config_with_prior_artifacts)

        assert result.portify_status == PortifyStatus.PASS
        assert result.step_name == "panel-review"
        assert result.step_number == 7
        assert result.phase == 4
        assert result.gate_tier == "STRICT"

    def test_produces_artifact(self, config_with_prior_artifacts):
        with patch_portify_process("panel-review"):
            result = run_panel_review(config_with_prior_artifacts)

        artifact = Path(result.artifact_path)
        assert artifact.exists()

    def test_produces_panel_report(self, config_with_prior_artifacts):
        with patch_portify_process("panel-review"):
            run_panel_review(config_with_prior_artifacts)

        report = config_with_prior_artifacts.results_dir / "panel-report.md"
        assert report.exists()
        content = report.read_text()
        assert "terminal_state:" in content


class TestPanelReviewFailures:

    def test_missing_synthesized_spec_fails(self, workflow_dir, tmp_path):
        output = tmp_path / "output"
        output.mkdir()
        results = output / "results"
        results.mkdir()
        (results / "brainstorm-gaps.md").write_text(BRAINSTORM_GAPS_GOOD)
        # No synthesized-spec.md

        config = load_portify_config(
            workflow_path=str(workflow_dir),
            output_dir=str(output),
        )
        result = run_panel_review(config)
        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.MISSING_ARTIFACT

    def test_missing_brainstorm_gaps_fails(self, workflow_dir, tmp_path):
        output = tmp_path / "output"
        output.mkdir()
        results = output / "results"
        results.mkdir()
        (results / "synthesized-spec.md").write_text(SYNTHESIZE_SPEC_GOOD)
        # No brainstorm-gaps.md

        config = load_portify_config(
            workflow_path=str(workflow_dir),
            output_dir=str(output),
        )
        result = run_panel_review(config)
        assert result.portify_status == PortifyStatus.FAIL

    def test_subprocess_timeout(self, config_with_prior_artifacts):
        with patch_portify_process("panel-review", exit_code=124, timed_out=True):
            result = run_panel_review(config_with_prior_artifacts)
        assert result.portify_status == PortifyStatus.TIMEOUT

    def test_user_rejection(self, config_with_prior_artifacts):
        """User rejection at review gate should produce FAIL."""
        # Need to enable review gate and mock user input
        config_with_prior_artifacts.skip_review = False
        with (
            patch_portify_process("panel-review"),
            patch(
                "superclaude.cli.cli_portify.steps.panel_review.prompt_user_review",
                return_value=False,
            ),
        ):
            result = run_panel_review(config_with_prior_artifacts)

        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.USER_REJECTION
        assert result.review_accepted is False
