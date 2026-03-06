"""Smoke tests for unified-audit-gating-v1.2.1 release.

Verifies that all new/modified modules from this release can be imported
and that their public classes, enums, functions, and dataclasses can be
instantiated without errors.

Modules under test:
  - superclaude.cli.pipeline.models
  - superclaude.cli.pipeline.trailing_gate
  - superclaude.cli.pipeline.conflict_review
  - superclaude.cli.pipeline.diagnostic_chain
  - superclaude.cli.sprint.models
  - superclaude.cli.sprint.kpi
"""

from __future__ import annotations

from pathlib import Path

import pytest


# =========================================================================
# Section 1: Raw import verification (no circular import issues)
# =========================================================================


class TestPipelineModelsImport:
    """Verify superclaude.cli.pipeline.models imports cleanly."""

    def test_import_module(self):
        import superclaude.cli.pipeline.models  # noqa: F401

    def test_import_StepStatus(self):
        from superclaude.cli.pipeline.models import StepStatus  # noqa: F401

    def test_import_GateMode(self):
        from superclaude.cli.pipeline.models import GateMode  # noqa: F401

    def test_import_SemanticCheck(self):
        from superclaude.cli.pipeline.models import SemanticCheck  # noqa: F401

    def test_import_GateCriteria(self):
        from superclaude.cli.pipeline.models import GateCriteria  # noqa: F401

    def test_import_Step(self):
        from superclaude.cli.pipeline.models import Step  # noqa: F401

    def test_import_StepResult(self):
        from superclaude.cli.pipeline.models import StepResult  # noqa: F401

    def test_import_DeliverableKind(self):
        from superclaude.cli.pipeline.models import DeliverableKind  # noqa: F401

    def test_import_Deliverable(self):
        from superclaude.cli.pipeline.models import Deliverable  # noqa: F401

    def test_import_PipelineConfig(self):
        from superclaude.cli.pipeline.models import PipelineConfig  # noqa: F401


class TestTrailingGateImport:
    """Verify superclaude.cli.pipeline.trailing_gate imports cleanly."""

    def test_import_module(self):
        import superclaude.cli.pipeline.trailing_gate  # noqa: F401

    def test_import_TrailingGateResult(self):
        from superclaude.cli.pipeline.trailing_gate import TrailingGateResult  # noqa: F401

    def test_import_GateResultQueue(self):
        from superclaude.cli.pipeline.trailing_gate import GateResultQueue  # noqa: F401

    def test_import_TrailingGateRunner(self):
        from superclaude.cli.pipeline.trailing_gate import TrailingGateRunner  # noqa: F401

    def test_import_DeferredRemediationLog(self):
        from superclaude.cli.pipeline.trailing_gate import DeferredRemediationLog  # noqa: F401

    def test_import_RemediationEntry(self):
        from superclaude.cli.pipeline.trailing_gate import RemediationEntry  # noqa: F401

    def test_import_RemediationStatus(self):
        from superclaude.cli.pipeline.trailing_gate import RemediationStatus  # noqa: F401

    def test_import_RemediationRetryStatus(self):
        from superclaude.cli.pipeline.trailing_gate import RemediationRetryStatus  # noqa: F401

    def test_import_RemediationRetryResult(self):
        from superclaude.cli.pipeline.trailing_gate import RemediationRetryResult  # noqa: F401

    def test_import_TrailingGatePolicy(self):
        from superclaude.cli.pipeline.trailing_gate import TrailingGatePolicy  # noqa: F401

    def test_import_build_remediation_prompt(self):
        from superclaude.cli.pipeline.trailing_gate import build_remediation_prompt  # noqa: F401

    def test_import_attempt_remediation(self):
        from superclaude.cli.pipeline.trailing_gate import attempt_remediation  # noqa: F401

    def test_import_GateScope(self):
        from superclaude.cli.pipeline.trailing_gate import GateScope  # noqa: F401

    def test_import_resolve_gate_mode(self):
        from superclaude.cli.pipeline.trailing_gate import resolve_gate_mode  # noqa: F401


class TestConflictReviewImport:
    """Verify superclaude.cli.pipeline.conflict_review imports cleanly."""

    def test_import_module(self):
        import superclaude.cli.pipeline.conflict_review  # noqa: F401

    def test_import_ConflictAction(self):
        from superclaude.cli.pipeline.conflict_review import ConflictAction  # noqa: F401

    def test_import_ConflictReviewResult(self):
        from superclaude.cli.pipeline.conflict_review import ConflictReviewResult  # noqa: F401

    def test_import_detect_file_overlap(self):
        from superclaude.cli.pipeline.conflict_review import detect_file_overlap  # noqa: F401

    def test_import_review_conflicts(self):
        from superclaude.cli.pipeline.conflict_review import review_conflicts  # noqa: F401


class TestDiagnosticChainImport:
    """Verify superclaude.cli.pipeline.diagnostic_chain imports cleanly."""

    def test_import_module(self):
        import superclaude.cli.pipeline.diagnostic_chain  # noqa: F401

    def test_import_DiagnosticStage(self):
        from superclaude.cli.pipeline.diagnostic_chain import DiagnosticStage  # noqa: F401

    def test_import_StageResult(self):
        from superclaude.cli.pipeline.diagnostic_chain import StageResult  # noqa: F401

    def test_import_DiagnosticReport(self):
        from superclaude.cli.pipeline.diagnostic_chain import DiagnosticReport  # noqa: F401

    def test_import_run_diagnostic_chain(self):
        from superclaude.cli.pipeline.diagnostic_chain import run_diagnostic_chain  # noqa: F401


class TestSprintModelsImport:
    """Verify superclaude.cli.sprint.models imports cleanly."""

    def test_import_module(self):
        import superclaude.cli.sprint.models  # noqa: F401

    def test_import_TurnLedger(self):
        from superclaude.cli.sprint.models import TurnLedger  # noqa: F401

    def test_import_TaskResult(self):
        from superclaude.cli.sprint.models import TaskResult  # noqa: F401

    def test_import_TaskEntry(self):
        from superclaude.cli.sprint.models import TaskEntry  # noqa: F401

    def test_import_TaskStatus(self):
        from superclaude.cli.sprint.models import TaskStatus  # noqa: F401

    def test_import_GateDisplayState(self):
        from superclaude.cli.sprint.models import GateDisplayState  # noqa: F401

    def test_import_GateOutcome(self):
        from superclaude.cli.sprint.models import GateOutcome  # noqa: F401

    def test_import_ShadowGateMetrics(self):
        from superclaude.cli.sprint.models import ShadowGateMetrics  # noqa: F401

    def test_import_is_valid_gate_transition(self):
        from superclaude.cli.sprint.models import is_valid_gate_transition  # noqa: F401

    def test_import_build_resume_output(self):
        from superclaude.cli.sprint.models import build_resume_output  # noqa: F401


class TestSprintKpiImport:
    """Verify superclaude.cli.sprint.kpi imports cleanly."""

    def test_import_module(self):
        import superclaude.cli.sprint.kpi  # noqa: F401

    def test_import_GateKPIReport(self):
        from superclaude.cli.sprint.kpi import GateKPIReport  # noqa: F401

    def test_import_build_kpi_report(self):
        from superclaude.cli.sprint.kpi import build_kpi_report  # noqa: F401


# =========================================================================
# Section 2: Cross-module import (circular dependency detection)
# =========================================================================


class TestCrossModuleImports:
    """Verify that importing all modules together does not cause circular imports."""

    def test_all_pipeline_modules_together(self):
        from superclaude.cli.pipeline import models as pm  # noqa: F811
        from superclaude.cli.pipeline import trailing_gate as tg  # noqa: F811
        from superclaude.cli.pipeline import conflict_review as cr  # noqa: F811
        from superclaude.cli.pipeline import diagnostic_chain as dc  # noqa: F811
        # If we get here, no circular import
        assert pm is not None
        assert tg is not None
        assert cr is not None
        assert dc is not None

    def test_sprint_and_pipeline_together(self):
        from superclaude.cli.pipeline import models as pm  # noqa: F811
        from superclaude.cli.pipeline import trailing_gate as tg  # noqa: F811
        from superclaude.cli.sprint import models as sm  # noqa: F811
        from superclaude.cli.sprint import kpi as sk  # noqa: F811
        assert pm is not None
        assert tg is not None
        assert sm is not None
        assert sk is not None

    def test_nfr007_pipeline_does_not_import_sprint(self):
        """NFR-007: pipeline modules must not import from sprint or roadmap.

        Uses AST-level analysis to avoid false positives from docstrings
        or comments that mention these modules.
        """
        import ast
        import superclaude.cli.pipeline.models as pm
        import superclaude.cli.pipeline.trailing_gate as tg
        import superclaude.cli.pipeline.conflict_review as cr
        import superclaude.cli.pipeline.diagnostic_chain as dc

        for mod in [pm, tg, cr, dc]:
            source = Path(mod.__file__).read_text()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_name = ""
                    if isinstance(node, ast.ImportFrom) and node.module:
                        module_name = node.module
                    elif isinstance(node, ast.Import):
                        module_name = ", ".join(a.name for a in node.names)
                    assert "superclaude.cli.sprint" not in module_name, (
                        f"{mod.__name__} violates NFR-007: imports from sprint ({module_name})"
                    )
                    assert "superclaude.cli.roadmap" not in module_name, (
                        f"{mod.__name__} violates NFR-007: imports from roadmap ({module_name})"
                    )


# =========================================================================
# Section 3: Enum value accessibility
# =========================================================================


class TestEnumValues:
    """Verify all enum members are accessible and have expected values."""

    def test_StepStatus_values(self):
        from superclaude.cli.pipeline.models import StepStatus

        assert StepStatus.PENDING.value == "PENDING"
        assert StepStatus.PASS.value == "PASS"
        assert StepStatus.FAIL.value == "FAIL"
        assert StepStatus.TIMEOUT.value == "TIMEOUT"
        assert StepStatus.CANCELLED.value == "CANCELLED"
        assert StepStatus.SKIPPED.value == "SKIPPED"

    def test_StepStatus_properties(self):
        from superclaude.cli.pipeline.models import StepStatus

        assert StepStatus.PENDING.is_terminal is False
        assert StepStatus.PASS.is_terminal is True
        assert StepStatus.PASS.is_success is True
        assert StepStatus.FAIL.is_failure is True

    def test_GateMode_values(self):
        from superclaude.cli.pipeline.models import GateMode

        assert GateMode.BLOCKING.value == "BLOCKING"
        assert GateMode.TRAILING.value == "TRAILING"

    def test_DeliverableKind_values(self):
        from superclaude.cli.pipeline.models import DeliverableKind

        assert DeliverableKind.IMPLEMENT.value == "implement"
        assert DeliverableKind.VERIFY.value == "verify"
        assert DeliverableKind.INVARIANT_CHECK.value == "invariant_check"
        assert DeliverableKind.FMEA_TEST.value == "fmea_test"
        assert DeliverableKind.GUARD_TEST.value == "guard_test"
        assert DeliverableKind.CONTRACT_TEST.value == "contract_test"

    def test_DeliverableKind_from_str(self):
        from superclaude.cli.pipeline.models import DeliverableKind

        assert DeliverableKind.from_str("implement") == DeliverableKind.IMPLEMENT
        with pytest.raises(ValueError, match="Unknown deliverable kind"):
            DeliverableKind.from_str("nonexistent")

    def test_ConflictAction_values(self):
        from superclaude.cli.pipeline.conflict_review import ConflictAction

        assert ConflictAction.PASSTHROUGH.value == "passthrough"
        assert ConflictAction.REGATE.value == "regate"

    def test_DiagnosticStage_values(self):
        from superclaude.cli.pipeline.diagnostic_chain import DiagnosticStage

        assert DiagnosticStage.TROUBLESHOOT.value == "troubleshoot"
        assert DiagnosticStage.ROOT_CAUSES.value == "root_causes"
        assert DiagnosticStage.SOLUTIONS.value == "solutions"
        assert DiagnosticStage.SUMMARY.value == "summary"

    def test_RemediationStatus_values(self):
        from superclaude.cli.pipeline.trailing_gate import RemediationStatus

        assert RemediationStatus.PENDING.value == "pending"
        assert RemediationStatus.REMEDIATED.value == "remediated"
        assert RemediationStatus.WAIVED.value == "waived"

    def test_RemediationRetryStatus_values(self):
        from superclaude.cli.pipeline.trailing_gate import RemediationRetryStatus

        assert RemediationRetryStatus.PASS_FIRST_ATTEMPT.value == "pass_first_attempt"
        assert RemediationRetryStatus.PASS_SECOND_ATTEMPT.value == "pass_second_attempt"
        assert RemediationRetryStatus.PERSISTENT_FAILURE.value == "persistent_failure"
        assert RemediationRetryStatus.BUDGET_EXHAUSTED.value == "budget_exhausted"

    def test_GateScope_values(self):
        from superclaude.cli.pipeline.trailing_gate import GateScope

        assert GateScope.RELEASE.value == "release"
        assert GateScope.MILESTONE.value == "milestone"
        assert GateScope.TASK.value == "task"

    def test_TaskStatus_values(self):
        from superclaude.cli.sprint.models import TaskStatus

        assert TaskStatus.PASS.value == "pass"
        assert TaskStatus.FAIL.value == "fail"
        assert TaskStatus.INCOMPLETE.value == "incomplete"
        assert TaskStatus.SKIPPED.value == "skipped"
        assert TaskStatus.PASS.is_success is True
        assert TaskStatus.FAIL.is_failure is True

    def test_GateOutcome_values(self):
        from superclaude.cli.sprint.models import GateOutcome

        assert GateOutcome.PASS.value == "pass"
        assert GateOutcome.FAIL.value == "fail"
        assert GateOutcome.DEFERRED.value == "deferred"
        assert GateOutcome.PENDING.value == "pending"
        assert GateOutcome.PASS.is_success is True

    def test_GateDisplayState_values(self):
        from superclaude.cli.sprint.models import GateDisplayState

        assert GateDisplayState.NONE.value == "none"
        assert GateDisplayState.CHECKING.value == "checking"
        assert GateDisplayState.PASS.value == "pass"
        assert GateDisplayState.FAIL_DEFERRED.value == "fail_deferred"
        assert GateDisplayState.REMEDIATING.value == "remediating"
        assert GateDisplayState.REMEDIATED.value == "remediated"
        assert GateDisplayState.HALT.value == "halt"

    def test_GateDisplayState_properties(self):
        from superclaude.cli.sprint.models import GateDisplayState

        # Verify color/icon/label properties do not raise
        for state in GateDisplayState:
            assert isinstance(state.color, str)
            assert isinstance(state.icon, str)
            assert isinstance(state.label, str)

    def test_GateDisplayState_valid_transitions(self):
        from superclaude.cli.sprint.models import (
            GateDisplayState,
            is_valid_gate_transition,
        )

        assert is_valid_gate_transition(GateDisplayState.NONE, GateDisplayState.CHECKING) is True
        assert is_valid_gate_transition(GateDisplayState.CHECKING, GateDisplayState.PASS) is True
        assert is_valid_gate_transition(GateDisplayState.PASS, GateDisplayState.HALT) is False

    def test_SprintOutcome_values(self):
        from superclaude.cli.sprint.models import SprintOutcome

        assert SprintOutcome.SUCCESS.value == "success"
        assert SprintOutcome.HALTED.value == "halted"
        assert SprintOutcome.INTERRUPTED.value == "interrupted"
        assert SprintOutcome.ERROR.value == "error"

    def test_PhaseStatus_values(self):
        from superclaude.cli.sprint.models import PhaseStatus

        assert PhaseStatus.PENDING.value == "pending"
        assert PhaseStatus.RUNNING.value == "running"
        assert PhaseStatus.PASS.value == "pass"
        assert PhaseStatus.HALT.value == "halt"
        assert PhaseStatus.PASS.is_terminal is True
        assert PhaseStatus.PASS.is_success is True
        assert PhaseStatus.HALT.is_failure is True


# =========================================================================
# Section 4: Basic instantiation (construction with minimal args)
# =========================================================================


class TestPipelineModelsInstantiation:
    """Verify pipeline dataclasses can be constructed with minimal arguments."""

    def test_SemanticCheck(self):
        from superclaude.cli.pipeline.models import SemanticCheck

        sc = SemanticCheck(name="test", check_fn=lambda s: True, failure_message="fail")
        assert sc.name == "test"
        assert sc.check_fn("anything") is True

    def test_GateCriteria(self):
        from superclaude.cli.pipeline.models import GateCriteria

        gc = GateCriteria(required_frontmatter_fields=["title"], min_lines=10)
        assert gc.enforcement_tier == "STANDARD"
        assert gc.semantic_checks is None

    def test_Step(self):
        from superclaude.cli.pipeline.models import Step, GateMode

        s = Step(
            id="step-01",
            prompt="Do something",
            output_file=Path("/tmp/out.md"),
            gate=None,
            timeout_seconds=60,
        )
        assert s.id == "step-01"
        assert s.gate_mode == GateMode.BLOCKING
        assert s.retry_limit == 1

    def test_StepResult_defaults(self):
        from superclaude.cli.pipeline.models import StepResult, StepStatus

        sr = StepResult()
        assert sr.status == StepStatus.PENDING
        assert sr.attempt == 1
        assert sr.gate_failure_reason is None
        assert isinstance(sr.duration_seconds, float)

    def test_Deliverable(self):
        from superclaude.cli.pipeline.models import Deliverable, DeliverableKind

        d = Deliverable(id="D-0001", description="Build feature X")
        assert d.kind == DeliverableKind.IMPLEMENT
        assert d.metadata == {}
        # Round-trip serialization
        d_dict = d.to_dict()
        d2 = Deliverable.from_dict(d_dict)
        assert d2.id == d.id
        assert d2.kind == d.kind

    def test_PipelineConfig_defaults(self):
        from superclaude.cli.pipeline.models import PipelineConfig

        cfg = PipelineConfig()
        assert cfg.dry_run is False
        assert cfg.max_turns == 50
        assert cfg.grace_period == 0


class TestTrailingGateInstantiation:
    """Verify trailing_gate classes can be constructed with minimal arguments."""

    def test_TrailingGateResult(self):
        from superclaude.cli.pipeline.trailing_gate import TrailingGateResult

        r = TrailingGateResult(step_id="s1", passed=True, evaluation_ms=12.5)
        assert r.step_id == "s1"
        assert r.passed is True
        assert r.failure_reason is None

    def test_GateResultQueue(self):
        from superclaude.cli.pipeline.trailing_gate import (
            GateResultQueue,
            TrailingGateResult,
        )

        q = GateResultQueue()
        assert q.pending_count() == 0

        # Put and drain round-trip
        q.put(TrailingGateResult(step_id="s1", passed=True, evaluation_ms=1.0))
        results = q.drain()
        assert len(results) == 1
        assert results[0].step_id == "s1"

    def test_TrailingGateRunner(self):
        from superclaude.cli.pipeline.trailing_gate import TrailingGateRunner

        runner = TrailingGateRunner()
        assert runner.pending_count == 0
        assert runner.result_queue is not None
        runner.cancel()  # Should not raise on empty runner

    def test_TrailingGateRunner_with_custom_queue(self):
        from superclaude.cli.pipeline.trailing_gate import (
            GateResultQueue,
            TrailingGateRunner,
        )

        q = GateResultQueue()
        runner = TrailingGateRunner(result_queue=q)
        assert runner.result_queue is q
        runner.cancel()

    def test_RemediationEntry(self):
        from superclaude.cli.pipeline.trailing_gate import (
            RemediationEntry,
            RemediationStatus,
        )

        entry = RemediationEntry(
            step_id="s1",
            gate_result={"step_id": "s1", "passed": False},
            failure_reason="missing frontmatter",
        )
        assert entry.remediation_status == RemediationStatus.PENDING.value
        # Round-trip serialization
        d = entry.to_dict()
        entry2 = RemediationEntry.from_dict(d)
        assert entry2.step_id == entry.step_id

    def test_DeferredRemediationLog_in_memory(self):
        from superclaude.cli.pipeline.trailing_gate import (
            DeferredRemediationLog,
            TrailingGateResult,
        )

        log = DeferredRemediationLog()
        assert log.entry_count == 0

        log.append(
            TrailingGateResult(
                step_id="s1", passed=False, evaluation_ms=5.0,
                failure_reason="test failure",
            )
        )
        assert log.entry_count == 1
        assert len(log.pending_remediations()) == 1

        # Mark remediated
        assert log.mark_remediated("s1") is True
        assert len(log.pending_remediations()) == 0

    def test_DeferredRemediationLog_serialization(self):
        from superclaude.cli.pipeline.trailing_gate import (
            DeferredRemediationLog,
            TrailingGateResult,
        )

        log = DeferredRemediationLog()
        log.append(
            TrailingGateResult(
                step_id="s2", passed=False, evaluation_ms=3.0,
                failure_reason="too short",
            )
        )
        json_str = log.serialize()
        log2 = DeferredRemediationLog.deserialize(json_str)
        assert log2.entry_count == 1

    def test_RemediationRetryResult(self):
        from superclaude.cli.pipeline.trailing_gate import (
            RemediationRetryResult,
            RemediationRetryStatus,
        )

        r = RemediationRetryResult(
            status=RemediationRetryStatus.BUDGET_EXHAUSTED,
            attempts_made=0,
            turns_consumed=0,
        )
        assert r.final_gate_result is None

    def test_resolve_gate_mode(self):
        from superclaude.cli.pipeline.trailing_gate import (
            GateMode,
            GateScope,
            resolve_gate_mode,
        )
        from superclaude.cli.pipeline.models import GateMode as GateModeModel

        # Release scope is always BLOCKING
        assert resolve_gate_mode(GateScope.RELEASE) == GateMode.BLOCKING
        # Task scope with grace_period > 0 is TRAILING
        assert resolve_gate_mode(GateScope.TASK, grace_period=5) == GateMode.TRAILING
        # Task scope without grace is BLOCKING
        assert resolve_gate_mode(GateScope.TASK, grace_period=0) == GateMode.BLOCKING

    def test_build_remediation_prompt(self):
        from superclaude.cli.pipeline.trailing_gate import (
            TrailingGateResult,
            build_remediation_prompt,
        )
        from superclaude.cli.pipeline.models import GateCriteria, Step

        step = Step(
            id="s1",
            prompt="Write docs",
            output_file=Path("/tmp/out.md"),
            gate=GateCriteria(
                required_frontmatter_fields=["title", "version"],
                min_lines=20,
            ),
            timeout_seconds=60,
        )
        gate_result = TrailingGateResult(
            step_id="s1", passed=False, evaluation_ms=10.0,
            failure_reason="Missing frontmatter: title",
        )
        prompt = build_remediation_prompt(gate_result, step)
        assert "Remediation for step 's1'" in prompt
        assert "Missing frontmatter: title" in prompt
        assert "title, version" in prompt


class TestConflictReviewInstantiation:
    """Verify conflict_review classes and functions work with minimal arguments."""

    def test_ConflictReviewResult_no_conflict(self):
        from superclaude.cli.pipeline.conflict_review import (
            ConflictAction,
            ConflictReviewResult,
        )

        r = ConflictReviewResult(action=ConflictAction.PASSTHROUGH)
        assert r.has_conflict is False

    def test_ConflictReviewResult_with_conflict(self):
        from superclaude.cli.pipeline.conflict_review import (
            ConflictAction,
            ConflictReviewResult,
        )

        r = ConflictReviewResult(
            action=ConflictAction.REGATE,
            overlapping_files={Path("a.py")},
        )
        assert r.has_conflict is True

    def test_detect_file_overlap(self):
        from superclaude.cli.pipeline.conflict_review import detect_file_overlap

        overlap = detect_file_overlap(
            remediation_files={Path("a.py"), Path("b.py")},
            intervening_files={Path("b.py"), Path("c.py")},
        )
        assert overlap == {Path("b.py")}

    def test_detect_file_overlap_empty(self):
        from superclaude.cli.pipeline.conflict_review import detect_file_overlap

        overlap = detect_file_overlap(set(), set())
        assert overlap == set()

    def test_review_conflicts_passthrough(self):
        from superclaude.cli.pipeline.conflict_review import (
            ConflictAction,
            review_conflicts,
        )

        result = review_conflicts(
            remediation_files={Path("a.py")},
            intervening_files={Path("b.py")},
        )
        assert result.action == ConflictAction.PASSTHROUGH

    def test_review_conflicts_regate(self):
        from superclaude.cli.pipeline.conflict_review import (
            ConflictAction,
            review_conflicts,
        )

        result = review_conflicts(
            remediation_files={Path("shared.py")},
            intervening_files={Path("shared.py")},
        )
        assert result.action == ConflictAction.REGATE
        assert Path("shared.py") in result.overlapping_files


class TestDiagnosticChainInstantiation:
    """Verify diagnostic_chain classes and functions work with minimal arguments."""

    def test_StageResult(self):
        from superclaude.cli.pipeline.diagnostic_chain import (
            DiagnosticStage,
            StageResult,
        )

        sr = StageResult(stage=DiagnosticStage.TROUBLESHOOT, output="analysis here")
        assert sr.success is True
        assert sr.error is None

    def test_DiagnosticReport_empty(self):
        from superclaude.cli.pipeline.diagnostic_chain import DiagnosticReport

        report = DiagnosticReport()
        assert report.is_complete is False
        assert report.stages_completed == 0
        assert report.summary == ""

    def test_run_diagnostic_chain(self):
        from superclaude.cli.pipeline.diagnostic_chain import (
            DiagnosticStage,
            run_diagnostic_chain,
        )

        report = run_diagnostic_chain(
            step_id="s1",
            failure_reason="Missing required field: title",
            remediation_output="attempted fix output",
        )
        assert report.is_complete is True
        assert report.stages_completed == 4
        assert report.summary != ""

        # Verify all stages present
        stages_present = {r.stage for r in report.stage_results}
        assert stages_present == {
            DiagnosticStage.TROUBLESHOOT,
            DiagnosticStage.ROOT_CAUSES,
            DiagnosticStage.SOLUTIONS,
            DiagnosticStage.SUMMARY,
        }

    def test_run_diagnostic_chain_empty_output(self):
        from superclaude.cli.pipeline.diagnostic_chain import run_diagnostic_chain

        report = run_diagnostic_chain(
            step_id="s2",
            failure_reason="gate timeout",
        )
        assert report.stages_completed == 4


class TestSprintModelsInstantiation:
    """Verify sprint model dataclasses can be constructed with minimal arguments."""

    def test_TaskEntry(self):
        from superclaude.cli.sprint.models import TaskEntry

        t = TaskEntry(task_id="T01.01", title="Implement feature")
        assert t.description == ""
        assert t.dependencies == []

    def test_TaskResult(self):
        from superclaude.cli.sprint.models import TaskEntry, TaskResult, TaskStatus

        task = TaskEntry(task_id="T01.01", title="Test task")
        tr = TaskResult(task=task)
        assert tr.status == TaskStatus.SKIPPED
        assert tr.turns_consumed == 0
        assert isinstance(tr.duration_seconds, float)

    def test_TaskResult_context_summary(self):
        from superclaude.cli.sprint.models import TaskEntry, TaskResult, TaskStatus

        task = TaskEntry(task_id="T01.01", title="Test task")
        tr = TaskResult(task=task, status=TaskStatus.PASS)
        verbose = tr.to_context_summary(verbose=True)
        assert "T01.01" in verbose
        compact = tr.to_context_summary(verbose=False)
        assert "T01.01" in compact

    def test_TurnLedger(self):
        from superclaude.cli.sprint.models import TurnLedger

        ledger = TurnLedger(initial_budget=50)
        assert ledger.available() == 50
        assert ledger.can_launch() is True
        assert ledger.can_remediate() is True

        ledger.debit(10)
        assert ledger.consumed == 10
        assert ledger.available() == 40

        ledger.credit(5)
        assert ledger.reimbursed == 5
        assert ledger.available() == 45

    def test_TurnLedger_debit_validation(self):
        from superclaude.cli.sprint.models import TurnLedger

        ledger = TurnLedger(initial_budget=10)
        with pytest.raises(ValueError, match="non-negative"):
            ledger.debit(-1)
        with pytest.raises(ValueError, match="non-negative"):
            ledger.credit(-1)

    def test_ShadowGateMetrics(self):
        from superclaude.cli.sprint.models import ShadowGateMetrics

        m = ShadowGateMetrics()
        assert m.total_evaluated == 0
        assert m.pass_rate == 0.0
        assert m.p50_latency_ms == 0.0
        assert m.p95_latency_ms == 0.0

        m.record(passed=True, evaluation_ms=10.0)
        m.record(passed=False, evaluation_ms=20.0)
        assert m.total_evaluated == 2
        assert m.passed == 1
        assert m.failed == 1
        assert m.pass_rate == 0.5

    def test_GateDisplayState_all_states_have_display_properties(self):
        from superclaude.cli.sprint.models import GateDisplayState

        for state in GateDisplayState:
            assert state.color, f"{state} has no color"
            assert state.icon, f"{state} has no icon"
            assert state.label, f"{state} has no label"

    def test_Phase(self):
        from superclaude.cli.sprint.models import Phase

        p = Phase(number=1, file=Path("phase-01.md"), name="Setup")
        assert p.display_name == "Setup"
        assert p.basename == "phase-01.md"

    def test_Phase_auto_name(self):
        from superclaude.cli.sprint.models import Phase

        p = Phase(number=3, file=Path("phase-03.md"))
        assert p.display_name == "Phase 3"

    def test_SprintConfig(self):
        from superclaude.cli.sprint.models import SprintConfig

        cfg = SprintConfig()
        assert cfg.dry_run is False
        assert cfg.shadow_gates is False
        assert cfg.debug is False

    def test_build_resume_output(self):
        from superclaude.cli.sprint.models import (
            SprintConfig,
            TaskEntry,
            TurnLedger,
            build_resume_output,
        )

        cfg = SprintConfig(index_path=Path("index.md"))
        tasks = [TaskEntry(task_id="T02.01", title="Continue work")]
        ledger = TurnLedger(initial_budget=50, consumed=20)

        output = build_resume_output(
            config=cfg,
            halt_task_id="T02.01",
            remaining_tasks=tasks,
            ledger=ledger,
        )
        assert "T02.01" in output
        assert "Resume Command" in output
        assert "Budget Status" in output


class TestSprintKpiInstantiation:
    """Verify sprint KPI classes and functions work with minimal arguments."""

    def test_GateKPIReport_empty(self):
        from superclaude.cli.sprint.kpi import GateKPIReport

        report = GateKPIReport()
        assert report.gate_pass_rate == 0.0
        assert report.gate_fail_rate == 0.0
        assert report.remediation_frequency == 0.0
        assert report.conflict_review_rate == 0.0
        assert report.p50_latency_ms == 0.0
        assert report.p95_latency_ms == 0.0

    def test_GateKPIReport_format_report(self):
        from superclaude.cli.sprint.kpi import GateKPIReport

        report = GateKPIReport(
            total_gates_evaluated=10,
            gates_passed=8,
            gates_failed=2,
            gate_latency_ms=[1.0, 2.0, 3.0],
        )
        text = report.format_report()
        assert "Gate & Remediation KPI Report" in text
        assert "80.0%" in text  # pass rate

    def test_build_kpi_report(self):
        from superclaude.cli.pipeline.trailing_gate import (
            DeferredRemediationLog,
            TrailingGateResult,
        )
        from superclaude.cli.sprint.kpi import build_kpi_report

        results = [
            TrailingGateResult(step_id="s1", passed=True, evaluation_ms=5.0),
            TrailingGateResult(step_id="s2", passed=False, evaluation_ms=15.0,
                               failure_reason="too short"),
        ]
        log = DeferredRemediationLog()
        log.append(results[1])

        report = build_kpi_report(
            gate_results=results,
            remediation_log=log,
            conflict_reviews_total=3,
            conflicts_detected=1,
        )
        assert report.total_gates_evaluated == 2
        assert report.gates_passed == 1
        assert report.gates_failed == 1
        assert report.total_remediations == 1
        assert report.conflicts_detected == 1

    def test_build_kpi_report_no_optional_args(self):
        from superclaude.cli.sprint.kpi import build_kpi_report

        report = build_kpi_report(gate_results=[])
        assert report.total_gates_evaluated == 0
        assert report.total_remediations == 0


# =========================================================================
# Section 5: Protocol / ABC verification
# =========================================================================


class TestProtocols:
    """Verify runtime-checkable protocols are functional."""

    def test_TrailingGatePolicy_is_runtime_checkable(self):
        from superclaude.cli.pipeline.trailing_gate import TrailingGatePolicy

        # A conforming class
        class FakePolicy:
            def build_remediation_step(self, gate_result):
                pass

            def files_changed(self, step_result):
                return set()

        assert isinstance(FakePolicy(), TrailingGatePolicy)

    def test_non_conforming_is_not_TrailingGatePolicy(self):
        from superclaude.cli.pipeline.trailing_gate import TrailingGatePolicy

        class NotAPolicy:
            pass

        assert not isinstance(NotAPolicy(), TrailingGatePolicy)
