"""Integration tests for cli-portify orchestration flows.

Tests end-to-end orchestration through the mock harness:
- Happy path: all 5 Claude-assisted steps pass through mock harness
- --dry-run halt: emits dry_run contract with phases 3-4 skipped (SC-011)
- Review rejection: produces USER_REJECTED
- Brainstorm fallback: activates when skill missing
- Convergence boundaries: converge at iteration 1, escalate at max
- Template missing: triggers fail-fast
- Timeout: per-iteration and total budget behavior

Per D-0041: Integration test suite for Phase 8 validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.cli.cli_portify.config import load_portify_config
from superclaude.cli.cli_portify.contract import (
    ContractStatus,
    build_dry_run_contract,
    build_failed_contract,
    build_partial_contract,
    build_success_contract,
    StepTiming,
)
from superclaude.cli.cli_portify.convergence import (
    ConvergenceEngine,
    ConvergenceState,
    EscalationReason,
    IterationResult,
    SimpleBudgetGuard,
)
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyConfig,
    PortifyStatus,
    PortifyStepResult,
)
from superclaude.cli.cli_portify.review import ReviewDecision, review_gate
from superclaude.cli.cli_portify.steps.analyze_workflow import run_analyze_workflow
from superclaude.cli.cli_portify.steps.brainstorm_gaps import run_brainstorm_gaps
from superclaude.cli.cli_portify.steps.design_pipeline import run_design_pipeline
from superclaude.cli.cli_portify.steps.panel_review import (
    check_downstream_readiness,
    compute_overall_score,
    run_panel_review,
)
from superclaude.cli.cli_portify.steps.synthesize_spec import run_synthesize_spec
from tests.cli_portify.fixtures.mock_harness import (
    ANALYZE_WORKFLOW_GOOD,
    BRAINSTORM_GAPS_GOOD,
    DESIGN_PIPELINE_GOOD,
    PANEL_REVIEW_GOOD,
    SYNTHESIZE_SPEC_GOOD,
    patch_portify_process,
)


# --- Fixtures ---


@pytest.fixture
def tmp_workflow(tmp_path):
    """Create a minimal workflow directory with SKILL.md."""
    wf_dir = tmp_path / "sc-test-workflow-protocol"
    wf_dir.mkdir()
    (wf_dir / "SKILL.md").write_text("# Test Skill\n\nA test skill.")
    return wf_dir


@pytest.fixture
def tmp_output(tmp_path):
    """Create an output directory."""
    out = tmp_path / "output"
    out.mkdir()
    return out


@pytest.fixture
def base_config(tmp_workflow, tmp_output):
    """Create a base config for integration tests."""
    return load_portify_config(
        workflow_path=str(tmp_workflow),
        output_dir=str(tmp_output),
        skip_review=True,
        max_convergence=3,
        iteration_timeout=300,
    )


@pytest.fixture
def config_with_inventory(base_config):
    """Config with component-inventory.md (prerequisite for Step 3)."""
    results_dir = base_config.results_dir
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "component-inventory.md").write_text(
        "---\nsource_skill: test\ncomponent_count: 3\n---\n\n## Components\n\n1. A\n2. B\n3. C\n"
    )
    return base_config


@pytest.fixture
def config_with_analysis(config_with_inventory):
    """Config with analyze-workflow artifact (prerequisite for Step 4)."""
    results_dir = config_with_inventory.results_dir
    (results_dir / "portify-analysis.md").write_text(ANALYZE_WORKFLOW_GOOD)
    return config_with_inventory


@pytest.fixture
def config_with_design(config_with_analysis):
    """Config with design-pipeline artifact (prerequisite for Step 5)."""
    results_dir = config_with_analysis.results_dir
    (results_dir / "portify-spec.md").write_text(DESIGN_PIPELINE_GOOD)
    # synthesize-spec also requires a release-spec-template.md in workflow dir
    template = config_with_analysis.workflow_path / "release-spec-template.md"
    if not template.exists():
        template.write_text("# Release Spec Template\n\nTemplate for synthesis.\n")
    return config_with_analysis


@pytest.fixture
def config_with_synthesis(config_with_design):
    """Config with synthesized-spec (prerequisite for Step 6)."""
    results_dir = config_with_design.results_dir
    (results_dir / "synthesized-spec.md").write_text(SYNTHESIZE_SPEC_GOOD)
    return config_with_design


@pytest.fixture
def config_with_brainstorm(config_with_synthesis):
    """Config with brainstorm-gaps artifact (prerequisite for Step 7)."""
    results_dir = config_with_synthesis.results_dir
    (results_dir / "brainstorm-gaps.md").write_text(BRAINSTORM_GAPS_GOOD)
    return config_with_synthesis


# --- Happy Path Integration Tests ---


class TestHappyPathIntegration:
    """Full happy path: mock subprocess for each step converges."""

    def test_analyze_workflow_happy_path(self, config_with_inventory):
        with patch_portify_process("analyze-workflow"):
            result = run_analyze_workflow(config_with_inventory)
        assert result.portify_status == PortifyStatus.PASS
        assert result.step_name == "analyze-workflow"
        assert result.gate_tier == "STRICT"

    def test_design_pipeline_happy_path(self, config_with_analysis):
        with patch_portify_process("design-pipeline"):
            result = run_design_pipeline(config_with_analysis)
        assert result.portify_status == PortifyStatus.PASS
        assert result.step_name == "design-pipeline"

    def test_synthesize_spec_happy_path(self, config_with_design):
        with patch_portify_process("synthesize-spec"):
            result = run_synthesize_spec(config_with_design)
        assert result.portify_status == PortifyStatus.PASS

    def test_brainstorm_gaps_happy_path(self, config_with_synthesis):
        with patch_portify_process("brainstorm-gaps"):
            result = run_brainstorm_gaps(config_with_synthesis)
        assert result.portify_status == PortifyStatus.PASS

    def test_panel_review_happy_path(self, config_with_brainstorm):
        with patch_portify_process("panel-review"):
            result = run_panel_review(config_with_brainstorm)
        assert result.portify_status == PortifyStatus.PASS
        assert result.review_accepted is True

    def test_all_steps_produce_artifacts(self, config_with_brainstorm):
        """Verify all 5 Claude-assisted steps produce their expected artifacts."""
        results_dir = config_with_brainstorm.results_dir

        # Step 3
        with patch_portify_process("analyze-workflow"):
            run_analyze_workflow(config_with_brainstorm)
        assert (results_dir / "portify-analysis.md").exists()

        # Step 4
        with patch_portify_process("design-pipeline"):
            run_design_pipeline(config_with_brainstorm)
        assert (results_dir / "portify-spec.md").exists()

        # Step 5
        with patch_portify_process("synthesize-spec"):
            run_synthesize_spec(config_with_brainstorm)
        assert (results_dir / "synthesized-spec.md").exists()

        # Step 6
        with patch_portify_process("brainstorm-gaps"):
            run_brainstorm_gaps(config_with_brainstorm)
        assert (results_dir / "brainstorm-gaps.md").exists()

        # Step 7
        with patch_portify_process("panel-review"):
            run_panel_review(config_with_brainstorm)
        assert (results_dir / "panel-review.md").exists()
        assert (results_dir / "panel-report.md").exists()


# --- Dry-Run Integration Tests (SC-011) ---


class TestDryRunIntegration:
    """--dry-run halts after Step 4, phases 3-4 marked skipped."""

    def test_dry_run_emits_contract(self, config_with_analysis, capsys):
        config_with_analysis.dry_run = True
        with patch_portify_process("design-pipeline"):
            result = run_design_pipeline(config_with_analysis)

        assert result.portify_status == PortifyStatus.SKIPPED
        captured = capsys.readouterr()
        contract = json.loads(captured.out)
        assert contract["status"] == "dry_run"

    def test_dry_run_phases_3_4_skipped(self, config_with_analysis, capsys):
        config_with_analysis.dry_run = True
        with patch_portify_process("design-pipeline"):
            run_design_pipeline(config_with_analysis)

        captured = capsys.readouterr()
        contract = json.loads(captured.out)
        # Phases 3-4 (indices 2, 3) should be skipped
        assert contract["phases"][2]["status"] == "skipped"
        assert contract["phases"][3]["status"] == "skipped"

    def test_dry_run_phases_1_2_completed(self, config_with_analysis, capsys):
        config_with_analysis.dry_run = True
        with patch_portify_process("design-pipeline"):
            run_design_pipeline(config_with_analysis)

        captured = capsys.readouterr()
        contract = json.loads(captured.out)
        assert contract["phases"][0]["status"] == "completed"
        assert contract["phases"][1]["status"] == "completed"

    def test_dry_run_contract_builder(self):
        """build_dry_run_contract marks phases 3-4 as skipped per SC-011."""
        contract = build_dry_run_contract(
            step_results=[], artifacts=["inv.md"],
            step_timings=[], total_duration=1.0,
        )
        d = contract.to_dict()
        assert d["status"] == "dry_run"
        assert d["phases"][2]["status"] == "skipped"
        assert d["phases"][3]["status"] == "skipped"


# --- Review Rejection Integration Tests ---


class TestReviewRejectionIntegration:
    """Review rejection produces USER_REJECTED."""

    def test_design_pipeline_review_reject(self, config_with_analysis):
        config_with_analysis.skip_review = False
        with (
            patch_portify_process("design-pipeline"),
            patch("builtins.input", return_value="n"),
        ):
            result = run_design_pipeline(config_with_analysis)

        assert result.portify_status == PortifyStatus.FAIL
        assert result.review_required is True
        assert result.review_accepted is False
        assert result.failure_classification == FailureClassification.USER_REJECTION

    def test_panel_review_review_reject(self, config_with_brainstorm):
        config_with_brainstorm.skip_review = False
        with (
            patch_portify_process("panel-review"),
            patch("builtins.input", return_value="n"),
        ):
            result = run_panel_review(config_with_brainstorm)

        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.USER_REJECTION

    def test_review_gate_skip_returns_skipped(self):
        passed, decision = review_gate("design-pipeline", "/fake", skip_review=True)
        assert passed is True
        assert decision == ReviewDecision.SKIPPED


# --- Brainstorm Fallback Integration Tests ---


class TestBrainstormFallbackIntegration:
    """Brainstorm fallback activates when /sc:brainstorm skill missing."""

    def test_fallback_when_skill_missing(self, config_with_synthesis):
        with (
            patch_portify_process("brainstorm-gaps"),
            patch(
                "superclaude.cli.cli_portify.steps.brainstorm_gaps.check_brainstorm_skill_available",
                return_value=False,
            ),
        ):
            result = run_brainstorm_gaps(config_with_synthesis)

        # Should still pass with inline fallback
        assert result.portify_status == PortifyStatus.PASS

    def test_fallback_when_skill_available(self, config_with_synthesis):
        with (
            patch_portify_process("brainstorm-gaps"),
            patch(
                "superclaude.cli.cli_portify.steps.brainstorm_gaps.check_brainstorm_skill_available",
                return_value=True,
            ),
        ):
            result = run_brainstorm_gaps(config_with_synthesis)

        assert result.portify_status == PortifyStatus.PASS


# --- Convergence Boundary Integration Tests ---


class TestConvergenceBoundaryIntegration:
    """Convergence engine boundary cases."""

    def test_converge_at_iteration_1(self):
        """Zero criticals on first iteration -> CONVERGED immediately."""
        engine = ConvergenceEngine(max_iterations=3)
        engine.submit(IterationResult(iteration=1, unaddressed_criticals=0))
        assert engine.state == ConvergenceState.CONVERGED
        assert engine.is_done is True
        result = engine.result()
        assert result.iterations_completed == 1
        assert result.is_converged

    def test_escalate_at_max_convergence(self):
        """Non-zero criticals across all iterations -> ESCALATED."""
        engine = ConvergenceEngine(max_iterations=3)
        for i in range(3):
            engine.submit(IterationResult(iteration=i + 1, unaddressed_criticals=2))
        assert engine.state == ConvergenceState.ESCALATED
        result = engine.result()
        assert result.escalation_reason == EscalationReason.MAX_ITERATIONS
        assert result.iterations_completed == 3

    def test_budget_exhaustion_escalates(self):
        """Budget exhaustion before max iterations -> ESCALATED."""
        budget = SimpleBudgetGuard(total_budget=1.0, per_iteration_cost=1.0)
        engine = ConvergenceEngine(max_iterations=5, budget_guard=budget)

        # Budget check after spending should fail
        budget.record_spend(1.0)
        assert not engine.check_budget(1.0)
        engine.escalate_budget()
        assert engine.state == ConvergenceState.ESCALATED
        result = engine.result()
        assert result.escalation_reason == EscalationReason.BUDGET_EXHAUSTED

    def test_convergence_quality_scores_integration(self):
        """Quality scores flow through convergence to result."""
        engine = ConvergenceEngine(max_iterations=3)
        scores = {
            "clarity": 8.0, "completeness": 7.0,
            "testability": 9.0, "consistency": 8.0,
        }
        engine.submit(IterationResult(
            iteration=1, unaddressed_criticals=0, quality_scores=scores,
        ))
        result = engine.result()
        assert result.is_converged
        # Overall = mean(8, 7, 9, 8) = 8.0
        assert abs(result.overall_score - 8.0) < 0.01
        assert check_downstream_readiness(result.overall_score)

    def test_panel_review_converges_at_iteration_1(self, config_with_brainstorm):
        """Full panel-review step converges on first iteration via mock."""
        with patch_portify_process("panel-review"):
            result = run_panel_review(config_with_brainstorm)
        # Mock outputs zero CRITICALs -> converges immediately
        assert result.portify_status == PortifyStatus.PASS


# --- Template Missing Integration Tests ---


class TestTemplateMissingIntegration:
    """Missing artifacts trigger fail-fast."""

    def test_analyze_workflow_missing_inventory(self, base_config):
        """Step 3 fails fast if component-inventory.md is missing."""
        base_config.results_dir.mkdir(parents=True, exist_ok=True)
        # Do NOT create component-inventory.md
        result = run_analyze_workflow(base_config)
        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.MISSING_ARTIFACT

    def test_brainstorm_missing_synthesized_spec(self, config_with_analysis):
        """Step 6 fails fast if synthesized-spec.md is missing."""
        # synthesized-spec.md does NOT exist
        result = run_brainstorm_gaps(config_with_analysis)
        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.MISSING_ARTIFACT

    def test_panel_review_missing_prerequisites(self, config_with_synthesis):
        """Step 7 fails fast if brainstorm-gaps.md is missing."""
        # brainstorm-gaps.md does NOT exist
        result = run_panel_review(config_with_synthesis)
        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.MISSING_ARTIFACT


# --- Timeout Integration Tests (SC-016) ---


class TestTimeoutIntegration:
    """Per-iteration independent timeout behavior (SC-016)."""

    def test_subprocess_timeout_returns_timeout_status(self, config_with_inventory):
        """Timeout during subprocess produces TIMEOUT status."""
        with patch_portify_process("analyze-workflow", timed_out=True, exit_code=124):
            result = run_analyze_workflow(config_with_inventory)
        assert result.portify_status == PortifyStatus.TIMEOUT
        assert result.failure_classification == FailureClassification.TIMEOUT

    def test_panel_review_per_iteration_timeout(self, config_with_brainstorm):
        """Panel review respects per-iteration timeout on subprocess timeout."""
        with patch_portify_process("panel-review", timed_out=True, exit_code=124):
            result = run_panel_review(config_with_brainstorm)
        assert result.portify_status == PortifyStatus.TIMEOUT
        assert result.failure_classification == FailureClassification.TIMEOUT

    def test_iteration_timeout_is_independent(self, base_config):
        """Iteration timeout is per-iteration, not total divided by max_convergence."""
        # With max_convergence=3 and iteration_timeout=300
        # Each iteration gets 300s, NOT 300/3=100s
        assert base_config.iteration_timeout == 300
        assert base_config.max_convergence == 3
        # The timeout is the same regardless of max_convergence
        config2 = load_portify_config(
            workflow_path=str(base_config.workflow_path),
            output_dir=str(base_config.output_dir),
            max_convergence=10,
            iteration_timeout=300,
        )
        assert config2.iteration_timeout == 300  # Same, not 300/10


# --- Contract Exit Path Integration Tests (SC-010) ---


class TestContractExitPathIntegration:
    """All 4 exit paths produce populated contracts."""

    def test_success_contract_populated(self):
        c = build_success_contract(
            artifacts=["a.md", "b.md"],
            step_timings=[StepTiming(step="s1", duration_seconds=1.0)],
            gate_results={"s1": "pass"},
            total_duration=5.0,
        )
        d = c.to_dict()
        assert d["status"] == "success"
        assert len(d["phases"]) == 4
        assert len(d["artifacts"]) == 2

    def test_partial_contract_populated(self):
        c = build_partial_contract(
            step_results=[], artifacts=["a.md"],
            step_timings=[], gate_results={},
            total_duration=3.0, resume_step="panel-review",
        )
        d = c.to_dict()
        assert d["status"] == "partial"
        assert "--start panel-review" in d["resume_command"]

    def test_failed_contract_populated(self):
        c = build_failed_contract(
            step_results=[], artifacts=[],
            step_timings=[], gate_results={},
            total_duration=2.0, error_message="Gate failure",
            resume_step="synthesize-spec",
        )
        d = c.to_dict()
        assert d["status"] == "failed"
        assert d["error_message"] == "Gate failure"
        assert "--start synthesize-spec" in d["resume_command"]

    def test_dry_run_contract_populated(self):
        c = build_dry_run_contract(
            step_results=[], artifacts=["inv.md"],
            step_timings=[], total_duration=1.0,
        )
        d = c.to_dict()
        assert d["status"] == "dry_run"
        assert d["phases"][2]["status"] == "skipped"
        assert d["phases"][3]["status"] == "skipped"
