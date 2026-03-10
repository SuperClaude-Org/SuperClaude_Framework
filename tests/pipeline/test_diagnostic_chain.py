"""Tests for pipeline/diagnostic_chain.py -- failure analysis chain.

Covers T07.05 acceptance criteria.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from superclaude.cli.pipeline.diagnostic_chain import (
    DiagnosticReport,
    DiagnosticStage,
    StageResult,
    run_diagnostic_chain,
)


class TestDiagnosticChain:
    """Diagnostic chain fires on persistent failure with graceful degradation."""

    def test_complete_chain_all_stages(self):
        """Full chain produces 4 stage results."""
        report = run_diagnostic_chain(
            step_id="task-1",
            failure_reason="Missing required field 'title'",
            remediation_output="attempted fix but failed",
        )
        assert len(report.stage_results) == 4
        assert report.is_complete
        assert report.stages_completed == 4

    def test_chain_includes_troubleshoot(self):
        """Chain includes troubleshoot stage with failure analysis."""
        report = run_diagnostic_chain(
            step_id="task-1",
            failure_reason="Too few lines",
        )
        troubleshoot = report.get_stage(DiagnosticStage.TROUBLESHOOT)
        assert troubleshoot is not None
        assert troubleshoot.success
        assert "Too few lines" in troubleshoot.output

    def test_chain_includes_root_causes(self):
        """Chain includes root cause hypotheses."""
        report = run_diagnostic_chain(
            step_id="task-1",
            failure_reason="fail",
        )
        root_causes = report.get_stage(DiagnosticStage.ROOT_CAUSES)
        assert root_causes is not None
        assert root_causes.success
        assert "hypothesis" in root_causes.output.lower()

    def test_chain_includes_solutions(self):
        """Chain includes solution proposals."""
        report = run_diagnostic_chain(
            step_id="task-1",
            failure_reason="fail",
        )
        solutions = report.get_stage(DiagnosticStage.SOLUTIONS)
        assert solutions is not None
        assert solutions.success
        assert "solution" in solutions.output.lower() or "fix" in solutions.output.lower()

    def test_chain_includes_summary(self):
        """Chain produces a summary report."""
        report = run_diagnostic_chain(
            step_id="task-1",
            failure_reason="fail",
        )
        summary = report.get_stage(DiagnosticStage.SUMMARY)
        assert summary is not None
        assert summary.success
        assert report.summary != ""

    def test_graceful_degradation_troubleshoot_failure(self):
        """Chain degrades gracefully when troubleshoot stage fails."""
        with patch(
            "superclaude.cli.pipeline.diagnostic_chain._run_troubleshoot",
            side_effect=RuntimeError("simulated failure"),
        ):
            report = run_diagnostic_chain(
                step_id="task-1",
                failure_reason="fail",
            )
        # Chain continues despite troubleshoot failure
        assert len(report.stage_results) == 4
        troubleshoot = report.get_stage(DiagnosticStage.TROUBLESHOOT)
        assert troubleshoot is not None
        assert not troubleshoot.success
        assert "simulated failure" in troubleshoot.error

        # Subsequent stages still ran
        root_causes = report.get_stage(DiagnosticStage.ROOT_CAUSES)
        assert root_causes is not None
        assert root_causes.success

    def test_graceful_degradation_root_causes_failure(self):
        """Chain degrades gracefully when root_causes stage fails."""
        with patch(
            "superclaude.cli.pipeline.diagnostic_chain._run_root_causes",
            side_effect=RuntimeError("root cause error"),
        ):
            report = run_diagnostic_chain(
                step_id="task-1",
                failure_reason="fail",
            )
        root_causes = report.get_stage(DiagnosticStage.ROOT_CAUSES)
        assert not root_causes.success
        # Solutions still ran
        solutions = report.get_stage(DiagnosticStage.SOLUTIONS)
        assert solutions.success

    def test_graceful_degradation_solutions_failure(self):
        """Chain degrades gracefully when solutions stage fails."""
        with patch(
            "superclaude.cli.pipeline.diagnostic_chain._run_solutions",
            side_effect=RuntimeError("solutions error"),
        ):
            report = run_diagnostic_chain(
                step_id="task-1",
                failure_reason="fail",
            )
        solutions = report.get_stage(DiagnosticStage.SOLUTIONS)
        assert not solutions.success
        # Summary still ran and mentions degraded stages
        summary = report.get_stage(DiagnosticStage.SUMMARY)
        assert summary.success

    def test_no_turnledger_turns_consumed(self):
        """Diagnostic chain is runner-side: no TurnLedger integration needed."""
        # This test verifies the design: run_diagnostic_chain accepts no
        # TurnLedger parameter and operates purely on provided data.
        # If it accepted a ledger, its signature would be different.
        import inspect
        sig = inspect.signature(run_diagnostic_chain)
        param_names = list(sig.parameters.keys())
        assert "ledger" not in param_names
        assert "turn_ledger" not in param_names

    def test_empty_remediation_output(self):
        """Chain handles empty remediation output gracefully."""
        report = run_diagnostic_chain(
            step_id="task-1",
            failure_reason="fail",
            remediation_output="",
        )
        assert report.is_complete
        troubleshoot = report.get_stage(DiagnosticStage.TROUBLESHOOT)
        assert "(no output)" in troubleshoot.output

    def test_report_stages_completed_partial(self):
        """stages_completed reflects partial completion."""
        with patch(
            "superclaude.cli.pipeline.diagnostic_chain._run_troubleshoot",
            side_effect=RuntimeError("fail"),
        ):
            report = run_diagnostic_chain(
                step_id="task-1", failure_reason="fail",
            )
        assert report.stages_completed == 3  # 4 stages, 1 failed
        assert not report.is_complete
