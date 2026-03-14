"""Tests for panel-report.md generation (D-0034).

Covers:
- YAML frontmatter with all required fields
- Machine-readable convergence block
- Human-readable summary
- Converged and escalated states
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.cli_portify.convergence import (
    ConvergenceResult,
    ConvergenceState,
    EscalationReason,
)
from superclaude.cli.cli_portify.steps.panel_review import (
    compute_overall_score,
    generate_panel_report,
)
from superclaude.cli.cli_portify.utils import parse_frontmatter


class TestPanelReportFrontmatter:

    def test_contains_terminal_state(self, tmp_path):
        path = tmp_path / "report.md"
        generate_panel_report(
            convergence_result=ConvergenceResult(state=ConvergenceState.CONVERGED, iterations_completed=1),
            quality_scores={"clarity": 8.0, "completeness": 7.0, "testability": 9.0, "consistency": 8.0},
            overall_score=8.0,
            downstream_ready=True,
            output_path=path,
        )
        content = path.read_text()
        fm, _ = parse_frontmatter(content)
        assert fm["terminal_state"] == "converged"

    def test_contains_iteration_count(self, tmp_path):
        path = tmp_path / "report.md"
        generate_panel_report(
            convergence_result=ConvergenceResult(state=ConvergenceState.CONVERGED, iterations_completed=3),
            quality_scores={},
            overall_score=0.0,
            downstream_ready=False,
            output_path=path,
        )
        content = path.read_text()
        fm, _ = parse_frontmatter(content)
        assert fm["iteration_count"] == 3

    def test_contains_quality_scores(self, tmp_path):
        path = tmp_path / "report.md"
        scores = {"clarity": 8.5, "completeness": 7.0, "testability": 9.0, "consistency": 8.0}
        overall = compute_overall_score(scores)
        generate_panel_report(
            convergence_result=ConvergenceResult(state=ConvergenceState.CONVERGED, iterations_completed=1),
            quality_scores=scores,
            overall_score=overall,
            downstream_ready=True,
            output_path=path,
        )
        content = path.read_text()
        fm, _ = parse_frontmatter(content)
        assert fm["clarity"] == 8.5
        assert fm["completeness"] == 7.0
        assert fm["testability"] == 9.0
        assert fm["consistency"] == 8.0

    def test_contains_overall_score(self, tmp_path):
        path = tmp_path / "report.md"
        generate_panel_report(
            convergence_result=ConvergenceResult(state=ConvergenceState.CONVERGED, iterations_completed=1),
            quality_scores={"clarity": 8.0, "completeness": 7.0, "testability": 9.0, "consistency": 6.0},
            overall_score=7.5,
            downstream_ready=True,
            output_path=path,
        )
        content = path.read_text()
        fm, _ = parse_frontmatter(content)
        assert fm["overall"] == 7.5

    def test_contains_downstream_ready(self, tmp_path):
        path = tmp_path / "report.md"
        generate_panel_report(
            convergence_result=ConvergenceResult(state=ConvergenceState.CONVERGED, iterations_completed=1),
            quality_scores={},
            overall_score=8.0,
            downstream_ready=True,
            output_path=path,
        )
        content = path.read_text()
        fm, _ = parse_frontmatter(content)
        assert fm["downstream_ready"] is True


class TestPanelReportEscalation:

    def test_escalated_includes_reason(self, tmp_path):
        path = tmp_path / "report.md"
        generate_panel_report(
            convergence_result=ConvergenceResult(
                state=ConvergenceState.ESCALATED,
                iterations_completed=3,
                escalation_reason=EscalationReason.MAX_ITERATIONS,
            ),
            quality_scores={},
            overall_score=5.0,
            downstream_ready=False,
            output_path=path,
        )
        content = path.read_text()
        fm, _ = parse_frontmatter(content)
        assert fm["terminal_state"] == "escalated"
        assert fm["escalation_reason"] == "max_iterations"

    def test_budget_exhaustion_reason(self, tmp_path):
        path = tmp_path / "report.md"
        generate_panel_report(
            convergence_result=ConvergenceResult(
                state=ConvergenceState.ESCALATED,
                escalation_reason=EscalationReason.BUDGET_EXHAUSTED,
            ),
            quality_scores={},
            overall_score=0.0,
            downstream_ready=False,
            output_path=path,
        )
        content = path.read_text()
        assert "budget_exhausted" in content


class TestPanelReportHumanReadable:

    def test_contains_convergence_summary(self, tmp_path):
        path = tmp_path / "report.md"
        generate_panel_report(
            convergence_result=ConvergenceResult(state=ConvergenceState.CONVERGED, iterations_completed=2),
            quality_scores={"clarity": 8.0, "completeness": 7.0, "testability": 9.0, "consistency": 8.0},
            overall_score=8.0,
            downstream_ready=True,
            output_path=path,
        )
        content = path.read_text()
        assert "## Convergence Summary" in content
        assert "## Quality Scores" in content
        assert "## Downstream Readiness" in content

    def test_quality_scores_table(self, tmp_path):
        path = tmp_path / "report.md"
        generate_panel_report(
            convergence_result=ConvergenceResult(state=ConvergenceState.CONVERGED, iterations_completed=1),
            quality_scores={"clarity": 8.0, "completeness": 7.0, "testability": 9.0, "consistency": 8.0},
            overall_score=8.0,
            downstream_ready=True,
            output_path=path,
        )
        content = path.read_text()
        assert "| clarity | 8.0 |" in content
        assert "| **overall** |" in content

    def test_parseable_by_downstream_tooling(self, tmp_path):
        """Machine-readable convergence block must be parseable."""
        path = tmp_path / "report.md"
        generate_panel_report(
            convergence_result=ConvergenceResult(state=ConvergenceState.CONVERGED, iterations_completed=1),
            quality_scores={"clarity": 8.0, "completeness": 7.0, "testability": 9.0, "consistency": 8.0},
            overall_score=8.0,
            downstream_ready=True,
            output_path=path,
        )
        content = path.read_text()
        fm, body = parse_frontmatter(content)
        assert isinstance(fm, dict)
        assert "terminal_state" in fm
        assert "iteration_count" in fm
        assert "overall" in fm
