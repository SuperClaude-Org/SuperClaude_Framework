"""Tests for comprehensive failure-path handling for 7 failure types."""

from __future__ import annotations

import pytest

from superclaude.cli.cli_portify.failures import (
    FAILURE_HANDLERS,
    FailureHandlerResult,
    get_failure_handler_name,
    handle_budget_exhausted,
    handle_malformed_artifact,
    handle_missing_skills,
    handle_missing_template,
    handle_non_writable_output,
    handle_partial_artifact,
    handle_timeout,
    has_handler,
)
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyStatus,
)


class TestFailureHandlerResult:
    """Tests for the FailureHandlerResult structure."""

    def test_result_has_all_fields(self):
        result = handle_missing_template("test-step", 1, 1, "/path/template.md")
        assert isinstance(result, FailureHandlerResult)
        assert result.step_result is not None
        assert result.error_message != ""
        assert result.remediation != ""
        assert isinstance(result.is_terminal, bool)


class TestHandleMissingTemplate:
    """Tests for missing template failure handler."""

    def test_returns_fail_status(self):
        result = handle_missing_template("synthesize-spec", 5, 3, "/path/template.md")
        assert result.step_result.portify_status == PortifyStatus.FAIL

    def test_classifies_as_missing_artifact(self):
        result = handle_missing_template("synthesize-spec", 5, 3, "/path/template.md")
        assert result.step_result.failure_classification == FailureClassification.MISSING_ARTIFACT

    def test_is_terminal(self):
        result = handle_missing_template("synthesize-spec", 5, 3, "/path/template.md")
        assert result.is_terminal is True

    def test_error_mentions_path(self):
        result = handle_missing_template("synthesize-spec", 5, 3, "/path/template.md")
        assert "/path/template.md" in result.error_message

    def test_remediation_provides_guidance(self):
        result = handle_missing_template("synthesize-spec", 5, 3, "/path/template.md")
        assert "template" in result.remediation.lower()

    def test_step_metadata_populated(self):
        result = handle_missing_template("synthesize-spec", 5, 3, "/path/template.md")
        assert result.step_result.step_name == "synthesize-spec"
        assert result.step_result.step_number == 5
        assert result.step_result.phase == 3


class TestHandleMissingSkills:
    """Tests for missing skills failure handler (graceful fallback)."""

    def test_returns_pass_status(self):
        result = handle_missing_skills("analyze-workflow", 3, 2, ["skill-a"])
        assert result.step_result.portify_status == PortifyStatus.PASS

    def test_is_not_terminal(self):
        result = handle_missing_skills("analyze-workflow", 3, 2, ["skill-a"])
        assert result.is_terminal is False

    def test_no_failure_classification(self):
        result = handle_missing_skills("analyze-workflow", 3, 2, ["skill-a"])
        assert result.step_result.failure_classification is None

    def test_error_lists_missing_skills(self):
        result = handle_missing_skills("analyze-workflow", 3, 2, ["skill-a", "skill-b"])
        assert "skill-a" in result.error_message
        assert "skill-b" in result.error_message

    def test_remediation_suggests_install(self):
        result = handle_missing_skills("analyze-workflow", 3, 2, ["skill-a"])
        assert "install" in result.remediation.lower()


class TestHandleMalformedArtifact:
    """Tests for malformed artifact failure handler."""

    def test_returns_fail_status(self):
        result = handle_malformed_artifact("brainstorm-gaps", 6, 4, "/path/artifact.md")
        assert result.step_result.portify_status == PortifyStatus.FAIL

    def test_classifies_as_malformed_frontmatter(self):
        result = handle_malformed_artifact("brainstorm-gaps", 6, 4, "/path/artifact.md")
        assert result.step_result.failure_classification == FailureClassification.MALFORMED_FRONTMATTER

    def test_is_terminal(self):
        result = handle_malformed_artifact("brainstorm-gaps", 6, 4, "/path/artifact.md")
        assert result.is_terminal is True

    def test_includes_diagnostic(self):
        result = handle_malformed_artifact(
            "brainstorm-gaps", 6, 4, "/path/artifact.md", diagnostic="Missing --- delimiter"
        )
        assert "Missing --- delimiter" in result.error_message

    def test_resumable_step_has_resume_command(self):
        result = handle_malformed_artifact("brainstorm-gaps", 6, 4, "/path/artifact.md")
        assert result.step_result.resume_context.resume_command != ""
        assert "--start brainstorm-gaps" in result.step_result.resume_context.resume_command

    def test_non_resumable_step_has_empty_resume(self):
        result = handle_malformed_artifact("analyze-workflow", 3, 2, "/path/artifact.md")
        assert result.step_result.resume_context.resume_command == ""


class TestHandleTimeout:
    """Tests for timeout failure handler."""

    def test_returns_timeout_status(self):
        result = handle_timeout("synthesize-spec", 5, 3, 300.0)
        assert result.step_result.portify_status == PortifyStatus.TIMEOUT

    def test_per_iteration_timeout(self):
        result = handle_timeout(
            "panel-review", 7, 4, 300.0, is_per_iteration=True, iteration=2
        )
        assert result.step_result.failure_classification == FailureClassification.TIMEOUT
        assert "iteration 2" in result.error_message

    def test_total_budget_exhausted(self):
        result = handle_timeout(
            "panel-review", 7, 4, 300.0, total_budget_exhausted=True, iteration=3
        )
        assert result.step_result.failure_classification == FailureClassification.BUDGET_EXHAUSTION
        assert "budget exhausted" in result.error_message.lower()

    def test_is_terminal(self):
        result = handle_timeout("synthesize-spec", 5, 3, 300.0)
        assert result.is_terminal is True

    def test_resumable_step_has_resume_command(self):
        result = handle_timeout("panel-review", 7, 4, 300.0)
        assert result.step_result.resume_context.resume_command != ""

    def test_non_resumable_step_has_empty_resume(self):
        result = handle_timeout("analyze-workflow", 3, 2, 300.0)
        assert result.step_result.resume_context.resume_command == ""

    def test_iteration_number_captured(self):
        result = handle_timeout("panel-review", 7, 4, 300.0, iteration=5)
        assert result.step_result.iteration_number == 5

    def test_timeout_seconds_captured(self):
        result = handle_timeout("panel-review", 7, 4, 600.0)
        assert result.step_result.iteration_timeout == 600


class TestHandlePartialArtifact:
    """Tests for partial artifact failure handler."""

    def test_returns_fail_status(self):
        result = handle_partial_artifact("synthesize-spec", 5, 3, "/path/spec.md", 3)
        assert result.step_result.portify_status == PortifyStatus.FAIL

    def test_classifies_as_partial_artifact(self):
        result = handle_partial_artifact("synthesize-spec", 5, 3, "/path/spec.md", 3)
        assert result.step_result.failure_classification == FailureClassification.PARTIAL_ARTIFACT

    def test_is_terminal(self):
        result = handle_partial_artifact("synthesize-spec", 5, 3, "/path/spec.md")
        assert result.is_terminal is True

    def test_error_mentions_placeholder_count(self):
        result = handle_partial_artifact("synthesize-spec", 5, 3, "/path/spec.md", 5)
        assert "5 placeholder" in result.error_message

    def test_remediation_says_rerun(self):
        result = handle_partial_artifact("synthesize-spec", 5, 3, "/path/spec.md")
        assert "re-run" in result.remediation.lower()

    def test_resumable_step_has_resume_command(self):
        result = handle_partial_artifact("synthesize-spec", 5, 3, "/path/spec.md")
        assert result.step_result.resume_context.resume_command != ""


class TestHandleNonWritableOutput:
    """Tests for non-writable output directory failure handler."""

    def test_returns_fail_status(self):
        result = handle_non_writable_output("/readonly/dir")
        assert result.step_result.portify_status == PortifyStatus.FAIL

    def test_step_is_validate_config(self):
        result = handle_non_writable_output("/readonly/dir")
        assert result.step_result.step_name == "validate-config"
        assert result.step_result.step_number == 1

    def test_is_terminal(self):
        result = handle_non_writable_output("/readonly/dir")
        assert result.is_terminal is True

    def test_error_mentions_directory(self):
        result = handle_non_writable_output("/readonly/dir")
        assert "/readonly/dir" in result.error_message

    def test_remediation_suggests_fix(self):
        result = handle_non_writable_output("/readonly/dir")
        assert "writable" in result.remediation.lower()

    def test_gate_tier_is_exempt(self):
        result = handle_non_writable_output("/readonly/dir")
        assert result.step_result.gate_tier == "EXEMPT"


class TestHandleBudgetExhausted:
    """Tests for exhausted budget failure handler."""

    def test_returns_fail_status(self):
        result = handle_budget_exhausted("panel-review", 7, 4, 3, 3)
        assert result.step_result.portify_status == PortifyStatus.FAIL

    def test_classifies_as_budget_exhaustion(self):
        result = handle_budget_exhausted("panel-review", 7, 4, 3, 3)
        assert result.step_result.failure_classification == FailureClassification.BUDGET_EXHAUSTION

    def test_is_terminal(self):
        result = handle_budget_exhausted("panel-review", 7, 4, 3, 3)
        assert result.is_terminal is True

    def test_error_mentions_iterations(self):
        result = handle_budget_exhausted("panel-review", 7, 4, 3, 5)
        assert "3/5" in result.error_message

    def test_resume_command_with_increased_budget(self):
        result = handle_budget_exhausted("panel-review", 7, 4, 3, 3)
        # Budget should be suggested as max_convergence + 2
        assert "--max-convergence 5" in result.step_result.resume_context.resume_command

    def test_iteration_number_captured(self):
        result = handle_budget_exhausted("panel-review", 7, 4, 3, 3)
        assert result.step_result.iteration_number == 3


class TestFailureHandlersRegistry:
    """Tests for the failure handlers registry."""

    def test_all_7_failure_types_in_registry(self):
        assert len(FAILURE_HANDLERS) == 7

    def test_all_classifications_covered(self):
        for fc in FailureClassification:
            assert fc in FAILURE_HANDLERS

    def test_has_handler_for_missing_artifact(self):
        assert has_handler(FailureClassification.MISSING_ARTIFACT) is True

    def test_has_handler_for_malformed_frontmatter(self):
        assert has_handler(FailureClassification.MALFORMED_FRONTMATTER) is True

    def test_has_handler_for_timeout(self):
        assert has_handler(FailureClassification.TIMEOUT) is True

    def test_has_handler_for_partial_artifact(self):
        assert has_handler(FailureClassification.PARTIAL_ARTIFACT) is True

    def test_has_handler_for_budget_exhaustion(self):
        assert has_handler(FailureClassification.BUDGET_EXHAUSTION) is True

    def test_user_rejection_handled_by_review_module(self):
        assert has_handler(FailureClassification.USER_REJECTION) is False

    def test_gate_failure_handled_inline(self):
        assert has_handler(FailureClassification.GATE_FAILURE) is False

    def test_get_handler_name(self):
        name = get_failure_handler_name(FailureClassification.MISSING_ARTIFACT)
        assert name == "handle_missing_template"

    def test_get_handler_name_none_for_review(self):
        name = get_failure_handler_name(FailureClassification.USER_REJECTION)
        assert name is None


class TestNFR009Compliance:
    """Tests that all handlers produce populated contracts (no None/empty per NFR-009)."""

    def test_missing_template_populated(self):
        result = handle_missing_template("test", 1, 1, "/path")
        sr = result.step_result
        assert sr.portify_status is not None
        assert sr.step_name != ""
        assert sr.failure_classification is not None

    def test_malformed_artifact_populated(self):
        result = handle_malformed_artifact("test", 1, 1, "/path")
        sr = result.step_result
        assert sr.portify_status is not None
        assert sr.step_name != ""
        assert sr.failure_classification is not None
        assert sr.resume_context is not None

    def test_timeout_populated(self):
        result = handle_timeout("test", 1, 1, 300.0)
        sr = result.step_result
        assert sr.portify_status is not None
        assert sr.step_name != ""
        assert sr.failure_classification is not None
        assert sr.resume_context is not None

    def test_partial_artifact_populated(self):
        result = handle_partial_artifact("test", 1, 1, "/path")
        sr = result.step_result
        assert sr.portify_status is not None
        assert sr.step_name != ""
        assert sr.failure_classification is not None
        assert sr.resume_context is not None

    def test_non_writable_output_populated(self):
        result = handle_non_writable_output("/path")
        sr = result.step_result
        assert sr.portify_status is not None
        assert sr.step_name != ""
        assert sr.failure_classification is not None

    def test_budget_exhausted_populated(self):
        result = handle_budget_exhausted("panel-review", 7, 4, 3, 3)
        sr = result.step_result
        assert sr.portify_status is not None
        assert sr.step_name != ""
        assert sr.failure_classification is not None
        assert sr.resume_context is not None

    def test_missing_skills_has_status(self):
        result = handle_missing_skills("test", 1, 1, ["skill-a"])
        sr = result.step_result
        assert sr.portify_status is not None
        assert sr.step_name != ""


# ---------------------------------------------------------------------------
# T02.06 acceptance criteria: test_timeout
# ---------------------------------------------------------------------------


from superclaude.cli.cli_portify.failures import (
    STEP_0_TIMEOUT_SECONDS,
    STEP_1_TIMEOUT_SECONDS,
)


class TestTimeoutConstants:
    """T02.06 — NFR-001 timeout values enforced for Step 0 (30s) and Step 1 (60s).

    These tests satisfy the validation command:
        uv run pytest tests/ -k "test_timeout"
    """

    def test_timeout_step0_value_is_30(self):
        """Step 0 input-validation timeout must be exactly 30 seconds (NFR-001)."""
        assert STEP_0_TIMEOUT_SECONDS == 30

    def test_timeout_step1_value_is_60(self):
        """Step 1 component-discovery timeout must be exactly 60 seconds (NFR-001)."""
        assert STEP_1_TIMEOUT_SECONDS == 60

    def test_timeout_step0_handler_raises_on_expiry(self):
        """handle_timeout produces TIMEOUT status with correct step 0 metadata."""
        result = handle_timeout(
            step_name="validate-config",
            step_number=0,
            phase=0,
            timeout_seconds=STEP_0_TIMEOUT_SECONDS,
        )
        assert result.step_result.portify_status == PortifyStatus.TIMEOUT
        assert str(STEP_0_TIMEOUT_SECONDS) in result.error_message

    def test_timeout_step1_handler_raises_on_expiry(self):
        """handle_timeout produces TIMEOUT status with correct step 1 metadata."""
        result = handle_timeout(
            step_name="discover-components",
            step_number=1,
            phase=1,
            timeout_seconds=STEP_1_TIMEOUT_SECONDS,
        )
        assert result.step_result.portify_status == PortifyStatus.TIMEOUT
        assert str(STEP_1_TIMEOUT_SECONDS) in result.error_message

    def test_timeout_is_terminal(self):
        """Timeout failure is terminal — pipeline must stop."""
        result = handle_timeout("validate-config", 0, 0, STEP_0_TIMEOUT_SECONDS)
        assert result.is_terminal is True

    def test_timeout_step0_matches_nfr001(self):
        """Step 0 timeout constant matches NFR-001 specification of 30s."""
        assert STEP_0_TIMEOUT_SECONDS == 30, (
            f"NFR-001 requires Step 0 timeout = 30s, got {STEP_0_TIMEOUT_SECONDS}s"
        )

    def test_timeout_step1_matches_nfr001(self):
        """Step 1 timeout constant matches NFR-001 specification of 60s."""
        assert STEP_1_TIMEOUT_SECONDS == 60, (
            f"NFR-001 requires Step 1 timeout = 60s, got {STEP_1_TIMEOUT_SECONDS}s"
        )
