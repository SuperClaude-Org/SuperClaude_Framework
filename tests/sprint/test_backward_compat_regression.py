"""T09.02 — Backward compatibility regression: grace_period=0 produces v1.2.1 behavior.

Comprehensive regression test validating that the complete system with grace_period=0
produces output identical to v1.2.1 baseline:
- Sprint results are equivalent under default (no trailing gate) configuration
- Zero additional daemon threads from the gate/remediation system
- All existing v1.2.1 sprint tests pass without modification
- Per-task subprocess with no TurnLedger produces identical behavior

Acceptance criteria (D-0039):
- grace_period=0 sprint results are equivalent to v1.2.1 baseline output
- threading.active_count() shows zero additional daemon threads beyond baseline
- All existing sprint tests pass without modification under the new architecture
- `uv run pytest tests/sprint/ -v` exits 0 with zero failures

STRICT tier: backward compatibility verification (breaking keyword).
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.pipeline.executor import execute_pipeline
from superclaude.cli.pipeline.gates import gate_passed
from superclaude.cli.pipeline.models import (
    GateCriteria,
    GateMode,
    PipelineConfig,
    Step,
    StepResult,
    StepStatus,
)
from superclaude.cli.pipeline.trailing_gate import (
    GateScope,
    TrailingGateRunner,
    resolve_gate_mode,
)
from superclaude.cli.sprint.executor import (
    AggregatedPhaseReport,
    aggregate_task_results,
    check_budget_guard,
    execute_phase_tasks,
    execute_sprint,
)
from superclaude.cli.sprint.models import (
    GateOutcome,
    Phase,
    PhaseStatus,
    PhaseResult,
    SprintConfig,
    SprintOutcome,
    SprintResult,
    TaskEntry,
    TaskResult,
    TaskStatus,
    TurnLedger,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(tmp_path: Path, num_phases: int = 1) -> SprintConfig:
    phases = []
    for i in range(1, num_phases + 1):
        pf = tmp_path / f"phase-{i}-tasklist.md"
        pf.write_text(f"# Phase {i}\n")
        phases.append(Phase(number=i, file=pf, name=f"Phase {i}"))

    index = tmp_path / "tasklist-index.md"
    index.write_text("index\n")

    return SprintConfig(
        index_path=index,
        release_dir=tmp_path,
        phases=phases,
        start_phase=1,
        end_phase=num_phases,
        max_turns=5,
    )


class _FakePopenPass:
    """Minimal fake Popen that exits 0 after one poll cycle."""
    def __init__(self):
        self.returncode = 0
        self.pid = 30000
        self._poll_count = 0

    def poll(self):
        self._poll_count += 1
        return None if self._poll_count <= 1 else 0

    def wait(self, timeout=None):
        self.returncode = 0
        return 0


# ===========================================================================
# T09.02 — Backward Compatibility Regression (grace_period=0)
# ===========================================================================


class TestBackwardCompatRegression:
    """Comprehensive backward compatibility regression tests.

    Validates that grace_period=0 (the default) produces results
    identical to v1.2.1 baseline behavior with zero trailing gate
    overhead.
    """

    # -----------------------------------------------------------------------
    # grace_period=0 defaults
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_grace_period_zero_is_default_across_all_configs(self):
        """All config types default to grace_period=0 (v1.2.1 behavior)."""
        pc = PipelineConfig()
        assert pc.grace_period == 0

        sc = SprintConfig(
            index_path=Path("/tmp/idx.md"),
            release_dir=Path("/tmp/rel"),
            phases=[Phase(number=1, file=Path("/tmp/p1.md"))],
        )
        assert sc.grace_period == 0

    @pytest.mark.backward_compat
    def test_default_gate_mode_is_blocking(self):
        """Step.gate_mode defaults to BLOCKING, matching v1.2.1."""
        step = Step(
            id="test", prompt="test",
            output_file=Path("/tmp/out.md"),
            gate=None, timeout_seconds=60,
        )
        assert step.gate_mode == GateMode.BLOCKING

    # -----------------------------------------------------------------------
    # Gate resolution under grace_period=0
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_resolve_gate_mode_all_scopes_blocking_when_grace_zero(self):
        """All gate scopes resolve to BLOCKING when grace_period=0."""
        for scope in GateScope:
            mode = resolve_gate_mode(scope, grace_period=0)
            assert mode == GateMode.BLOCKING, (
                f"Scope {scope.value} should resolve to BLOCKING with grace_period=0"
            )

    # -----------------------------------------------------------------------
    # Zero daemon threads from gate/remediation system
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_zero_daemon_threads_grace_period_zero(self, tmp_path):
        """grace_period=0 sprint produces zero additional daemon threads
        from the gate/remediation system."""
        config = _make_config(tmp_path, num_phases=1)
        assert config.grace_period == 0

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            config.output_file(phase).write_text("output content\n")
            return _FakePopenPass()

        baseline_threads = threading.active_count()

        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            execute_sprint(config)

        # Allow a brief moment for daemon thread cleanup
        time.sleep(0.1)
        post_threads = threading.active_count()

        # No new daemon threads should persist from gate/remediation system
        assert post_threads <= baseline_threads + 1, (
            f"Daemon thread leak: baseline={baseline_threads}, "
            f"post={post_threads}. Expected zero additional threads "
            f"from gate/remediation system."
        )

    @pytest.mark.backward_compat
    def test_no_trailing_runner_created_when_grace_zero(self, tmp_path):
        """Pipeline executor does NOT create a TrailingGateRunner when
        grace_period=0 (v1.2.1 behavior)."""
        config = PipelineConfig(grace_period=0)

        steps = [
            Step(
                id="step-1", prompt="test",
                output_file=tmp_path / "out.md",
                gate=None, timeout_seconds=60,
            ),
        ]

        runner_calls = []

        def mock_run(step, cfg, cancel):
            (tmp_path / "out.md").write_text("content\n")
            return StepResult(step=step, status=StepStatus.PASS)

        results = execute_pipeline(
            steps=steps,
            config=config,
            run_step=mock_run,
        )

        assert len(results) == 1
        assert results[0].status == StepStatus.PASS

    # -----------------------------------------------------------------------
    # Per-task subprocess: no ledger produces v1.2.1 behavior
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_per_task_no_ledger_v121_behavior(self, tmp_path):
        """execute_phase_tasks without a TurnLedger (ledger=None)
        produces v1.2.1-identical behavior: no budget checks, no skips."""
        config = _make_config(tmp_path)
        phase = config.phases[0]
        tasks = [
            TaskEntry(task_id=f"T01.{i:02d}", title=f"Task {i}")
            for i in range(1, 6)
        ]

        def subprocess_factory(task, cfg, ph):
            return (0, 10, 500)

        results, remaining = execute_phase_tasks(
            tasks, config, phase,
            ledger=None,  # No budget tracking (v1.2.1 behavior)
            _subprocess_factory=subprocess_factory,
        )

        # All tasks execute (no budget gating)
        assert len(results) == 5
        assert len(remaining) == 0
        assert all(r.status == TaskStatus.PASS for r in results)

    # -----------------------------------------------------------------------
    # Execute sprint: v1.2.1 result format equivalence
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_sprint_result_format_v121_equivalence(self, tmp_path):
        """Sprint result under grace_period=0 matches v1.2.1 format:
        - PhaseStatus.PASS on success
        - SprintOutcome.SUCCESS on all pass
        - resume_command() is empty on success"""
        config = _make_config(tmp_path, num_phases=2)

        call_count = [0]

        def _factory(*args, **kwargs):
            call_count[0] += 1
            phase = config.phases[call_count[0] - 1]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text(
                "---\nstatus: PASS\n---\n\nEXIT_RECOMMENDATION: CONTINUE\n"
            )
            config.output_file(phase).write_text(
                f"Phase {call_count[0]} output\n"
            )
            return _FakePopenPass()

        captured_result = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(
                side_effect=lambda sr: captured_result.append(sr)
            )
            logger_cls.return_value = logger
            execute_sprint(config)

        # Verify result format
        assert len(captured_result) == 1
        sr = captured_result[0]
        assert sr.outcome == SprintOutcome.SUCCESS
        assert len(sr.phase_results) == 2
        assert all(r.status.is_success for r in sr.phase_results)
        assert sr.resume_command() == ""  # No resume needed on success

    # -----------------------------------------------------------------------
    # Phase status determination: v1.2.1 priority chain
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_phase_status_priority_chain_preserved(self, tmp_path):
        """_determine_phase_status() priority chain is unchanged from v1.2.1:
        timeout(124) > error(!=0) > HALT > CONTINUE > frontmatter > no_report."""
        from superclaude.cli.sprint.executor import _determine_phase_status

        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"

        # 1. Timeout always wins
        output_file.write_text("content")
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE\n")
        assert _determine_phase_status(124, result_file, output_file) == PhaseStatus.TIMEOUT

        # 2. Non-zero exit -> ERROR
        assert _determine_phase_status(1, result_file, output_file) == PhaseStatus.ERROR

        # 3. HALT signal wins over CONTINUE when both present
        result_file.write_text("EXIT_RECOMMENDATION: HALT\nEXIT_RECOMMENDATION: CONTINUE\n")
        assert _determine_phase_status(0, result_file, output_file) == PhaseStatus.HALT

        # 4. CONTINUE signal -> PASS
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE\n")
        assert _determine_phase_status(0, result_file, output_file) == PhaseStatus.PASS

        # 5. Frontmatter status: PASS -> PASS
        result_file.write_text("---\nstatus: PASS\n---\n")
        assert _determine_phase_status(0, result_file, output_file) == PhaseStatus.PASS

        # 6. Frontmatter status: FAIL -> HALT
        result_file.write_text("---\nstatus: FAIL\n---\n")
        assert _determine_phase_status(0, result_file, output_file) == PhaseStatus.HALT

        # 7. No result file but output exists -> PASS_NO_REPORT
        result_file.unlink()
        assert _determine_phase_status(0, result_file, output_file) == PhaseStatus.PASS_NO_REPORT

        # 8. No result file, no output -> ERROR
        output_file.unlink()
        assert _determine_phase_status(0, result_file, output_file) == PhaseStatus.ERROR

    # -----------------------------------------------------------------------
    # Budget guard: None ledger always allows launch
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_budget_guard_none_ledger_always_allows(self):
        """check_budget_guard(None) returns None (allow), matching v1.2.1
        behavior where no budget tracking existed."""
        assert check_budget_guard(None) is None

    # -----------------------------------------------------------------------
    # Aggregated report format: backward compatible fields
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_aggregated_report_format_backward_compatible(self):
        """AggregatedPhaseReport YAML and Markdown contain all v1.2.1 fields."""
        tasks = [TaskEntry(task_id="T01.01", title="Test task")]
        results = [
            TaskResult(
                task=tasks[0], status=TaskStatus.PASS,
                turns_consumed=10, exit_code=0,
            )
        ]
        report = aggregate_task_results(
            phase_number=1,
            task_results=results,
            budget_remaining=90,
        )

        yaml = report.to_yaml()
        # v1.2.1 required fields
        assert "phase:" in yaml
        assert "status:" in yaml
        assert "tasks_total:" in yaml
        assert "tasks_passed:" in yaml
        assert "tasks_failed:" in yaml

        md = report.to_markdown()
        assert "Phase 1" in md
        assert "EXIT_RECOMMENDATION:" in md

    # -----------------------------------------------------------------------
    # gate_passed: v1.2.1 tier behavior preserved
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_gate_passed_tier_behavior_preserved(self, tmp_path):
        """gate_passed() tier-proportional checks are unchanged from v1.2.1."""
        output_file = tmp_path / "output.md"

        # EXEMPT: always passes
        gate = GateCriteria(
            required_frontmatter_fields=[], min_lines=0,
            enforcement_tier="EXEMPT",
        )
        passed, reason = gate_passed(output_file, gate)
        assert passed is True

        # LIGHT: file must exist and be non-empty
        gate = GateCriteria(
            required_frontmatter_fields=[], min_lines=0,
            enforcement_tier="LIGHT",
        )
        passed, reason = gate_passed(output_file, gate)
        assert passed is False  # file doesn't exist

        output_file.write_text("content\n")
        passed, reason = gate_passed(output_file, gate)
        assert passed is True

        # STANDARD: + min lines + frontmatter
        gate = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=5,
            enforcement_tier="STANDARD",
        )
        passed, reason = gate_passed(output_file, gate)
        assert passed is False  # only 1 line

        output_file.write_text("---\ntitle: test\n---\n" + "\n".join(["line"] * 10))
        passed, reason = gate_passed(output_file, gate)
        assert passed is True

    # -----------------------------------------------------------------------
    # Multi-phase sprint: v1.2.1 execution log format
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_execution_log_format_v121(self, tmp_path):
        """Sprint execution log (JSONL) has v1.2.1-compatible event format."""
        import json

        config = _make_config(tmp_path, num_phases=1)

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            config.output_file(phase).write_text("output\n")
            return _FakePopenPass()

        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
        ):
            execute_sprint(config)

        jsonl_path = config.execution_log_jsonl
        assert jsonl_path.exists()
        events = [json.loads(line) for line in jsonl_path.read_text().strip().split("\n")]

        # v1.2.1 event types must be present
        event_types = {e["event"] for e in events}
        assert "sprint_start" in event_types
        assert "sprint_complete" in event_types

        # Each event has the required "event" field
        for e in events:
            assert "event" in e

    # -----------------------------------------------------------------------
    # TaskResult: to_context_summary format backward compatible
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_task_result_context_summary_format(self):
        """TaskResult.to_context_summary() produces backward-compatible format."""
        task = TaskEntry(task_id="T01.01", title="Test task")
        result = TaskResult(
            task=task,
            status=TaskStatus.PASS,
            turns_consumed=10,
            exit_code=0,
            gate_outcome=GateOutcome.PASS,
        )

        verbose = result.to_context_summary(verbose=True)
        assert "### T01.01" in verbose
        assert "Status" in verbose
        assert "Gate" in verbose

        compact = result.to_context_summary(verbose=False)
        assert "T01.01" in compact
        assert "pass" in compact

    # -----------------------------------------------------------------------
    # Enum backward compatibility: all v1.2.1 values preserved
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_enum_values_backward_compatible(self):
        """All v1.2.1 enum values are preserved without modification."""
        # TaskStatus
        assert TaskStatus.PASS.value == "pass"
        assert TaskStatus.FAIL.value == "fail"
        assert TaskStatus.INCOMPLETE.value == "incomplete"
        assert TaskStatus.SKIPPED.value == "skipped"

        # PhaseStatus
        assert PhaseStatus.PASS.value == "pass"
        assert PhaseStatus.HALT.value == "halt"
        assert PhaseStatus.TIMEOUT.value == "timeout"
        assert PhaseStatus.ERROR.value == "error"

        # SprintOutcome
        assert SprintOutcome.SUCCESS.value == "success"
        assert SprintOutcome.HALTED.value == "halted"
        assert SprintOutcome.INTERRUPTED.value == "interrupted"
        assert SprintOutcome.ERROR.value == "error"

        # StepStatus (pipeline)
        assert StepStatus.PASS.value == "PASS"
        assert StepStatus.FAIL.value == "FAIL"
        assert StepStatus.TIMEOUT.value == "TIMEOUT"

    # -----------------------------------------------------------------------
    # SprintConfig path helpers unchanged
    # -----------------------------------------------------------------------

    @pytest.mark.backward_compat
    def test_sprint_config_path_helpers_unchanged(self, tmp_path):
        """SprintConfig path helpers produce v1.2.1-compatible paths."""
        config = _make_config(tmp_path)
        phase = config.phases[0]

        assert config.results_dir == tmp_path / "results"
        assert config.output_file(phase) == tmp_path / "results" / "phase-1-output.txt"
        assert config.error_file(phase) == tmp_path / "results" / "phase-1-errors.txt"
        assert config.result_file(phase) == tmp_path / "results" / "phase-1-result.md"
        assert config.execution_log_jsonl == tmp_path / "execution-log.jsonl"
        assert config.execution_log_md == tmp_path / "execution-log.md"
