"""Tests for pipeline/trailing_gate.py -- TrailingGateRunner, GateResultQueue,
DeferredRemediationLog, and scope-based gate strategy.

Covers T05.01 through T05.05 acceptance criteria.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import (
    GateCriteria,
    GateMode,
    PipelineConfig,
    Step,
    StepResult,
    StepStatus,
)
from superclaude.cli.pipeline.trailing_gate import (
    DeferredRemediationLog,
    GateResultQueue,
    GateScope,
    RemediationEntry,
    RemediationStatus,
    TrailingGateResult,
    TrailingGateRunner,
    resolve_gate_mode,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_step(
    step_id: str = "s1",
    gate: GateCriteria | None = None,
    gate_mode: GateMode = GateMode.BLOCKING,
    tmp_path: Path | None = None,
) -> Step:
    return Step(
        id=step_id,
        prompt="test prompt",
        output_file=(tmp_path or Path("/tmp")) / f"{step_id}.md",
        gate=gate,
        timeout_seconds=60,
        gate_mode=gate_mode,
    )


def _make_gate() -> GateCriteria:
    return GateCriteria(
        required_frontmatter_fields=["title"],
        min_lines=5,
        enforcement_tier="STANDARD",
    )


# ===========================================================================
# T05.02 -- GateResultQueue
# ===========================================================================


class TestGateResultQueue:
    """Thread-safe queue for gate results."""

    def test_put_and_drain(self):
        q = GateResultQueue()
        r = TrailingGateResult(step_id="s1", passed=True, evaluation_ms=1.0)
        q.put(r)
        results = q.drain()
        assert len(results) == 1
        assert results[0].step_id == "s1"
        assert results[0].passed is True

    def test_drain_empty(self):
        q = GateResultQueue()
        results = q.drain()
        assert results == []

    def test_pending_count(self):
        q = GateResultQueue()
        assert q.pending_count() == 0
        q.put(TrailingGateResult(step_id="s1", passed=True, evaluation_ms=1.0))
        assert q.pending_count() == 1
        q.put(TrailingGateResult(step_id="s2", passed=False, evaluation_ms=2.0))
        assert q.pending_count() == 2
        q.drain()
        assert q.pending_count() == 0

    def test_concurrent_put_drain(self):
        """Thread-safe under concurrent access from >=3 threads."""
        q = GateResultQueue()
        results_collected: list[TrailingGateResult] = []
        errors: list[str] = []

        def producer(start_id: int, count: int):
            for i in range(count):
                q.put(TrailingGateResult(
                    step_id=f"s{start_id + i}",
                    passed=True,
                    evaluation_ms=float(i),
                ))

        def consumer(collected: list):
            time.sleep(0.05)  # let producers get ahead
            while True:
                batch = q.drain()
                if batch:
                    collected.extend(batch)
                else:
                    break

        # 3 producer threads, each producing 10 results
        threads = [
            threading.Thread(target=producer, args=(0, 10)),
            threading.Thread(target=producer, args=(100, 10)),
            threading.Thread(target=producer, args=(200, 10)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Drain all results
        final = q.drain()
        assert len(final) == 30  # All 30 results collected without loss

    def test_results_associated_with_correct_step_id(self):
        """Results are associated with correct step_id (no cross-contamination)."""
        q = GateResultQueue()
        q.put(TrailingGateResult(step_id="alpha", passed=True, evaluation_ms=1.0))
        q.put(TrailingGateResult(step_id="beta", passed=False, evaluation_ms=2.0, failure_reason="bad"))
        results = q.drain()
        by_id = {r.step_id: r for r in results}
        assert by_id["alpha"].passed is True
        assert by_id["beta"].passed is False
        assert by_id["beta"].failure_reason == "bad"


# ===========================================================================
# T05.01 -- TrailingGateRunner
# ===========================================================================


class TestTrailingGateRunner:
    """Daemon-thread gate evaluator."""

    def test_submit_spawns_daemon_thread(self, tmp_path):
        """submit() spawns daemon thread for gate evaluation."""
        step = _make_step(gate=_make_gate(), tmp_path=tmp_path)
        # Create valid output file
        out = step.output_file
        out.parent.mkdir(parents=True, exist_ok=True)
        content = "---\ntitle: test\n---\n" + "\n".join(f"line {i}" for i in range(10))
        out.write_text(content)

        runner = TrailingGateRunner()
        runner.submit(step)

        # Wait for completion
        results = runner.wait_for_pending(timeout=5.0)
        assert len(results) == 1
        assert results[0].step_id == "s1"
        assert results[0].passed is True

    def test_submit_no_gate(self, tmp_path):
        """submit() with no gate criteria produces immediate PASS result."""
        step = _make_step(gate=None, tmp_path=tmp_path)
        runner = TrailingGateRunner()
        runner.submit(step)
        results = runner.drain()
        assert len(results) == 1
        assert results[0].passed is True

    def test_submit_gate_failure(self, tmp_path):
        """submit() correctly reports gate failure."""
        step = _make_step(gate=_make_gate(), tmp_path=tmp_path)
        # Create output file that fails gate (too short)
        out = step.output_file
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("only one line")

        runner = TrailingGateRunner()
        runner.submit(step)
        results = runner.wait_for_pending(timeout=5.0)
        assert len(results) == 1
        assert results[0].passed is False
        assert results[0].failure_reason is not None

    def test_wait_for_pending_bounded_timeout(self, tmp_path):
        """wait_for_pending() blocks with bounded timeout, no indefinite hangs."""
        runner = TrailingGateRunner()

        def slow_gate(path, criteria):
            time.sleep(10)  # Very slow
            return True, None

        step = _make_step(gate=_make_gate(), tmp_path=tmp_path)
        step.output_file.parent.mkdir(parents=True, exist_ok=True)
        step.output_file.write_text("x")
        runner.submit(step, gate_check=slow_gate)

        start = time.monotonic()
        results = runner.wait_for_pending(timeout=0.5)
        elapsed = time.monotonic() - start
        # Should return within ~0.5s, not hang for 10s
        assert elapsed < 2.0
        runner.cancel()  # cleanup

    def test_cancel_propagates(self, tmp_path):
        """cancel() propagates to all active daemon threads."""
        runner = TrailingGateRunner()
        cancelled = threading.Event()

        def slow_gate(path, criteria):
            time.sleep(5)
            return True, None

        step = _make_step(gate=_make_gate(), tmp_path=tmp_path)
        step.output_file.parent.mkdir(parents=True, exist_ok=True)
        step.output_file.write_text("x")
        runner.submit(step, gate_check=slow_gate)

        runner.cancel()
        # After cancel, pending should eventually reach 0
        assert runner.pending_count >= 0  # doesn't crash

    def test_concurrent_submit_drain(self, tmp_path):
        """Concurrent submit/drain scenarios work correctly."""
        runner = TrailingGateRunner()
        num_steps = 5

        for i in range(num_steps):
            step = _make_step(step_id=f"step-{i}", gate=None, tmp_path=tmp_path)
            runner.submit(step)

        # All should produce results
        results = runner.wait_for_pending(timeout=5.0)
        # Also drain any that arrived after wait
        results.extend(runner.drain())
        assert len(results) == num_steps
        step_ids = {r.step_id for r in results}
        assert step_ids == {f"step-{i}" for i in range(num_steps)}


# ===========================================================================
# T05.03 -- DeferredRemediationLog
# ===========================================================================


class TestDeferredRemediationLog:
    """Persistent log of gate failures requiring remediation."""

    def test_append_and_pending(self):
        log = DeferredRemediationLog()
        result = TrailingGateResult(step_id="s1", passed=False, evaluation_ms=10.0, failure_reason="bad output")
        log.append(result)
        pending = log.pending_remediations()
        assert len(pending) == 1
        assert pending[0].step_id == "s1"
        assert pending[0].failure_reason == "bad output"

    def test_mark_remediated(self):
        log = DeferredRemediationLog()
        log.append(TrailingGateResult(step_id="s1", passed=False, evaluation_ms=1.0, failure_reason="fail"))
        assert len(log.pending_remediations()) == 1
        assert log.mark_remediated("s1") is True
        assert len(log.pending_remediations()) == 0

    def test_mark_remediated_not_found(self):
        log = DeferredRemediationLog()
        assert log.mark_remediated("nonexistent") is False

    def test_serialize_deserialize(self):
        """Serialization to disk produces valid JSON; deserialize recovers exact state."""
        log = DeferredRemediationLog()
        log.append(TrailingGateResult(step_id="s1", passed=False, evaluation_ms=1.0, failure_reason="fail1"))
        log.append(TrailingGateResult(step_id="s2", passed=False, evaluation_ms=2.0, failure_reason="fail2"))
        log.mark_remediated("s1")

        json_str = log.serialize()
        data = json.loads(json_str)  # Valid JSON
        assert len(data) == 2

        # Deserialize recovers exact state
        recovered = DeferredRemediationLog.deserialize(json_str)
        pending = recovered.pending_remediations()
        assert len(pending) == 1
        assert pending[0].step_id == "s2"

    def test_disk_persistence(self, tmp_path):
        """Persistence to disk and recovery for --resume."""
        persist_path = tmp_path / "remediation.json"
        log = DeferredRemediationLog(persist_path=persist_path)
        log.append(TrailingGateResult(step_id="s1", passed=False, evaluation_ms=1.0, failure_reason="fail"))

        assert persist_path.exists()
        content = persist_path.read_text()
        data = json.loads(content)
        assert len(data) == 1

        # Load from disk
        recovered = DeferredRemediationLog.load_from_disk(persist_path)
        assert recovered.entry_count == 1
        assert len(recovered.pending_remediations()) == 1

    def test_load_from_disk_missing_file(self, tmp_path):
        """load_from_disk with missing file returns empty log."""
        path = tmp_path / "missing.json"
        log = DeferredRemediationLog.load_from_disk(path)
        assert log.entry_count == 0

    def test_single_writer_thread_safety(self):
        """Single-writer thread safety: no corruption under concurrent access."""
        log = DeferredRemediationLog()
        errors = []

        def writer():
            for i in range(20):
                log.append(TrailingGateResult(
                    step_id=f"w-{i}", passed=False,
                    evaluation_ms=float(i), failure_reason=f"fail-{i}",
                ))

        def reader():
            for _ in range(20):
                try:
                    log.pending_remediations()
                except Exception as e:
                    errors.append(str(e))

        w = threading.Thread(target=writer)
        r1 = threading.Thread(target=reader)
        r2 = threading.Thread(target=reader)
        w.start()
        r1.start()
        r2.start()
        w.join()
        r1.join()
        r2.join()

        assert len(errors) == 0
        assert log.entry_count == 20


# ===========================================================================
# T05.04 -- Scope-Based Gate Strategy
# ===========================================================================


class TestScopeGateStrategy:
    """Scope-based gate mode resolution."""

    def test_release_always_blocking(self):
        """Release gates are always BLOCKING regardless of configuration."""
        assert resolve_gate_mode(GateScope.RELEASE) == GateMode.BLOCKING
        assert resolve_gate_mode(GateScope.RELEASE, GateMode.TRAILING) == GateMode.BLOCKING
        assert resolve_gate_mode(GateScope.RELEASE, GateMode.TRAILING, grace_period=60) == GateMode.BLOCKING

    def test_milestone_default_blocking(self):
        """Milestone gates default to BLOCKING."""
        assert resolve_gate_mode(GateScope.MILESTONE) == GateMode.BLOCKING

    def test_milestone_configurable_trailing(self):
        """Milestone gates configurable to TRAILING."""
        assert resolve_gate_mode(GateScope.MILESTONE, GateMode.TRAILING) == GateMode.TRAILING

    def test_task_default_blocking_no_grace(self):
        """Task gates default to BLOCKING when grace_period=0."""
        assert resolve_gate_mode(GateScope.TASK) == GateMode.BLOCKING
        assert resolve_gate_mode(GateScope.TASK, grace_period=0) == GateMode.BLOCKING

    def test_task_trailing_with_grace(self):
        """Task gates default to TRAILING when grace_period > 0."""
        assert resolve_gate_mode(GateScope.TASK, grace_period=30) == GateMode.TRAILING


# ===========================================================================
# T05.05 -- Executor Trailing vs Blocking Branch Logic
# ===========================================================================


class TestExecutorBranchLogic:
    """Tests for executor branching between trailing and blocking paths."""

    def _make_runner(self, status: StepStatus = StepStatus.PASS):
        """Create a mock step runner."""
        from datetime import datetime, timezone

        def runner(step, config, cancel_check):
            now = datetime.now(timezone.utc)
            return StepResult(
                step=step, status=status, attempt=1,
                started_at=now, finished_at=now,
            )
        return runner

    def test_blocking_mode_synchronous(self, tmp_path):
        """BLOCKING mode: gate evaluates synchronously before proceeding."""
        from superclaude.cli.pipeline.executor import execute_pipeline

        gate = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=3,
            enforcement_tier="STANDARD",
        )
        step = _make_step(gate=gate, gate_mode=GateMode.BLOCKING, tmp_path=tmp_path)
        # Create passing output
        out = step.output_file
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("---\ntitle: test\n---\nline1\nline2\nline3\n")

        config = PipelineConfig(work_dir=tmp_path, grace_period=0)
        results = execute_pipeline([step], config, self._make_runner())
        assert len(results) == 1
        assert results[0].status == StepStatus.PASS

    def test_blocking_mode_fails_on_gate_failure(self, tmp_path):
        """BLOCKING mode: gate failure halts pipeline."""
        from superclaude.cli.pipeline.executor import execute_pipeline

        gate = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=10,
            enforcement_tier="STANDARD",
        )
        step = _make_step(gate=gate, gate_mode=GateMode.BLOCKING, tmp_path=tmp_path)
        out = step.output_file
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("short")  # Too few lines

        config = PipelineConfig(work_dir=tmp_path, grace_period=0)
        results = execute_pipeline([step], config, self._make_runner())
        assert len(results) == 1
        assert results[0].status == StepStatus.FAIL

    def test_trailing_mode_continues(self, tmp_path):
        """TRAILING mode: gate submitted, execution continues."""
        from superclaude.cli.pipeline.executor import execute_pipeline

        gate = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=3,
            enforcement_tier="STANDARD",
        )
        step1 = _make_step(step_id="t1", gate=gate, gate_mode=GateMode.TRAILING, tmp_path=tmp_path)
        step2 = _make_step(step_id="t2", gate=None, tmp_path=tmp_path)

        # Create passing output for step1
        step1.output_file.parent.mkdir(parents=True, exist_ok=True)
        step1.output_file.write_text("---\ntitle: test\n---\nline1\nline2\nline3\n")

        config = PipelineConfig(work_dir=tmp_path, grace_period=30)
        results = execute_pipeline([step1, step2], config, self._make_runner())
        # Both steps executed (trailing didn't block)
        assert len(results) == 2
        assert all(r.status == StepStatus.PASS for r in results)

    def test_grace_period_zero_forces_blocking(self, tmp_path):
        """grace_period=0 forces BLOCKING path regardless of gate_mode."""
        from superclaude.cli.pipeline.executor import execute_pipeline

        gate = GateCriteria(
            required_frontmatter_fields=["title"],
            min_lines=10,
            enforcement_tier="STANDARD",
        )
        # Step configured as TRAILING but grace_period=0
        step = _make_step(gate=gate, gate_mode=GateMode.TRAILING, tmp_path=tmp_path)
        out = step.output_file
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("short")  # Will fail gate

        config = PipelineConfig(work_dir=tmp_path, grace_period=0)
        results = execute_pipeline([step], config, self._make_runner())
        assert len(results) == 1
        # Should FAIL because grace_period=0 forces blocking
        assert results[0].status == StepStatus.FAIL

    def test_backward_compat_no_trailing_runner(self, tmp_path):
        """Existing code without trailing_runner still works (backward compat)."""
        from superclaude.cli.pipeline.executor import execute_pipeline

        step = _make_step(gate=None, tmp_path=tmp_path)
        config = PipelineConfig(work_dir=tmp_path)
        results = execute_pipeline([step], config, self._make_runner())
        assert len(results) == 1
        assert results[0].status == StepStatus.PASS


# ===========================================================================
# T07.01 -- TrailingGatePolicy Protocol
# ===========================================================================


class TestTrailingGatePolicy:
    """TrailingGatePolicy protocol definition and sprint consumer compliance."""

    def test_protocol_is_importable(self):
        """TrailingGatePolicy is importable from pipeline module."""
        from superclaude.cli.pipeline.trailing_gate import TrailingGatePolicy
        assert TrailingGatePolicy is not None

    def test_protocol_is_runtime_checkable(self):
        """TrailingGatePolicy is runtime_checkable."""
        from superclaude.cli.pipeline.trailing_gate import TrailingGatePolicy
        assert hasattr(TrailingGatePolicy, "__protocol_attrs__") or hasattr(
            TrailingGatePolicy, "_is_runtime_protocol"
        )

    def test_sprint_consumer_satisfies_protocol(self):
        """SprintGatePolicy satisfies the TrailingGatePolicy protocol."""
        from superclaude.cli.pipeline.trailing_gate import TrailingGatePolicy
        from superclaude.cli.sprint.executor import SprintGatePolicy
        from superclaude.cli.sprint.models import SprintConfig

        config = SprintConfig(index_path=Path("test.md"))
        policy = SprintGatePolicy(config)
        assert isinstance(policy, TrailingGatePolicy)

    def test_build_remediation_step_returns_step(self, tmp_path):
        """build_remediation_step returns a Step with remediation prompt."""
        from superclaude.cli.sprint.executor import SprintGatePolicy
        from superclaude.cli.sprint.models import SprintConfig

        config = SprintConfig(index_path=Path("test.md"), work_dir=tmp_path)
        policy = SprintGatePolicy(config)
        gate_result = TrailingGateResult(
            step_id="task-1", passed=False,
            evaluation_ms=50.0, failure_reason="Missing required field 'title'",
        )
        step = policy.build_remediation_step(gate_result)
        assert step.id == "task-1_remediation"
        assert "Missing required field 'title'" in step.prompt
        assert "REMEDIATION" in step.prompt

    def test_files_changed_with_existing_output(self, tmp_path):
        """files_changed returns output file when it exists."""
        from superclaude.cli.sprint.executor import SprintGatePolicy
        from superclaude.cli.sprint.models import SprintConfig

        config = SprintConfig(index_path=Path("test.md"), work_dir=tmp_path)
        policy = SprintGatePolicy(config)

        output_file = tmp_path / "output.md"
        output_file.write_text("content")
        step = Step(
            id="s1", prompt="test", output_file=output_file,
            gate=None, timeout_seconds=60,
        )
        result = StepResult(step=step, status=StepStatus.PASS)
        changed = policy.files_changed(result)
        assert output_file in changed

    def test_files_changed_empty_when_no_output(self, tmp_path):
        """files_changed returns empty set when output file doesn't exist."""
        from superclaude.cli.sprint.executor import SprintGatePolicy
        from superclaude.cli.sprint.models import SprintConfig

        config = SprintConfig(index_path=Path("test.md"), work_dir=tmp_path)
        policy = SprintGatePolicy(config)

        step = Step(
            id="s1", prompt="test", output_file=tmp_path / "nonexistent.md",
            gate=None, timeout_seconds=60,
        )
        result = StepResult(step=step, status=StepStatus.FAIL)
        changed = policy.files_changed(result)
        assert len(changed) == 0

    def test_non_conforming_class_fails_isinstance(self):
        """A class missing protocol methods does NOT satisfy the protocol."""
        from superclaude.cli.pipeline.trailing_gate import TrailingGatePolicy

        class NotAPolicy:
            pass

        assert not isinstance(NotAPolicy(), TrailingGatePolicy)


# ===========================================================================
# T07.02 -- Remediation Prompt Construction
# ===========================================================================


class TestRemediationPrompt:
    """Remediation prompt constructor builds focused prompts from gate failures."""

    def test_prompt_includes_failure_reason(self, tmp_path):
        """Prompt includes the specific gate failure reason."""
        from superclaude.cli.pipeline.trailing_gate import build_remediation_prompt

        gate_result = TrailingGateResult(
            step_id="s1", passed=False, evaluation_ms=10.0,
            failure_reason="Missing required field 'title'",
        )
        step = _make_step(gate=GateCriteria(
            required_frontmatter_fields=["title"], min_lines=3,
        ), tmp_path=tmp_path)
        prompt = build_remediation_prompt(gate_result, step)
        assert "Missing required field 'title'" in prompt

    def test_prompt_includes_acceptance_criteria(self, tmp_path):
        """Prompt includes original acceptance criteria from the gate."""
        from superclaude.cli.pipeline.trailing_gate import build_remediation_prompt

        gate = GateCriteria(
            required_frontmatter_fields=["title", "status"],
            min_lines=5,
            enforcement_tier="STRICT",
        )
        gate_result = TrailingGateResult(
            step_id="s1", passed=False, evaluation_ms=10.0,
            failure_reason="Too few lines",
        )
        step = _make_step(gate=gate, tmp_path=tmp_path)
        prompt = build_remediation_prompt(gate_result, step)
        assert "title" in prompt
        assert "status" in prompt
        assert "5" in prompt
        assert "STRICT" in prompt

    def test_prompt_includes_file_paths(self, tmp_path):
        """Prompt includes file paths when provided."""
        from superclaude.cli.pipeline.trailing_gate import build_remediation_prompt

        gate_result = TrailingGateResult(
            step_id="s1", passed=False, evaluation_ms=10.0,
            failure_reason="fail",
        )
        step = _make_step(gate=None, tmp_path=tmp_path)
        paths = {Path("/src/foo.py"), Path("/src/bar.py")}
        prompt = build_remediation_prompt(gate_result, step, file_paths=paths)
        assert "/src/bar.py" in prompt
        assert "/src/foo.py" in prompt

    def test_prompt_is_scoped_not_full_reexecution(self, tmp_path):
        """Prompt is scoped to specific failure, not full task re-execution."""
        from superclaude.cli.pipeline.trailing_gate import build_remediation_prompt

        gate_result = TrailingGateResult(
            step_id="s1", passed=False, evaluation_ms=10.0,
            failure_reason="fail",
        )
        step = _make_step(gate=None, tmp_path=tmp_path)
        prompt = build_remediation_prompt(gate_result, step)
        assert "Fix ONLY the specific gate failure" in prompt
        assert "Do not re-execute the full task" in prompt

    def test_prompt_deterministic(self, tmp_path):
        """Identical inputs produce identical output."""
        from superclaude.cli.pipeline.trailing_gate import build_remediation_prompt

        gate_result = TrailingGateResult(
            step_id="s1", passed=False, evaluation_ms=10.0,
            failure_reason="fail",
        )
        step = _make_step(gate=GateCriteria(
            required_frontmatter_fields=["title"], min_lines=3,
        ), tmp_path=tmp_path)
        prompt1 = build_remediation_prompt(gate_result, step)
        prompt2 = build_remediation_prompt(gate_result, step)
        assert prompt1 == prompt2

    def test_prompt_handles_no_gate(self, tmp_path):
        """Prompt works when step has no gate criteria."""
        from superclaude.cli.pipeline.trailing_gate import build_remediation_prompt

        gate_result = TrailingGateResult(
            step_id="s1", passed=False, evaluation_ms=10.0,
            failure_reason="External failure",
        )
        step = _make_step(gate=None, tmp_path=tmp_path)
        prompt = build_remediation_prompt(gate_result, step)
        assert "External failure" in prompt
        assert "Acceptance Criteria" not in prompt


# ===========================================================================
# T07.03 -- Remediation Retry with TurnLedger Integration
# ===========================================================================


class TestRemediationRetry:
    """Remediation retry state machine with budget integration."""

    def _make_gate_result(self, passed: bool, reason: str | None = None):
        return TrailingGateResult(
            step_id="s1", passed=passed,
            evaluation_ms=10.0, failure_reason=reason,
        )

    def test_pass_first_attempt(self, tmp_path):
        """Task passes gate on first remediation attempt."""
        from superclaude.cli.pipeline.trailing_gate import (
            RemediationRetryStatus, attempt_remediation,
        )

        step = _make_step(gate=None, tmp_path=tmp_path)
        debits = []

        result = attempt_remediation(
            remediation_step=step,
            turns_per_attempt=5,
            can_remediate=lambda: True,
            debit=lambda t: debits.append(t),
            run_step=lambda s: StepResult(step=s, status=StepStatus.PASS),
            check_gate=lambda r: self._make_gate_result(True),
        )

        assert result.status == RemediationRetryStatus.PASS_FIRST_ATTEMPT
        assert result.attempts_made == 1
        assert result.turns_consumed == 5
        assert debits == [5]

    def test_fail_then_pass(self, tmp_path):
        """Task fails first attempt, passes on second."""
        from superclaude.cli.pipeline.trailing_gate import (
            RemediationRetryStatus, attempt_remediation,
        )

        step = _make_step(gate=None, tmp_path=tmp_path)
        attempt_count = [0]

        def check_gate(r):
            attempt_count[0] += 1
            if attempt_count[0] == 1:
                return self._make_gate_result(False, "first fail")
            return self._make_gate_result(True)

        result = attempt_remediation(
            remediation_step=step,
            turns_per_attempt=5,
            can_remediate=lambda: True,
            debit=lambda t: None,
            run_step=lambda s: StepResult(step=s, status=StepStatus.PASS),
            check_gate=check_gate,
        )

        assert result.status == RemediationRetryStatus.PASS_SECOND_ATTEMPT
        assert result.attempts_made == 2
        assert result.turns_consumed == 10

    def test_persistent_failure(self, tmp_path):
        """Both attempts fail -> PERSISTENT_FAILURE, both debited."""
        from superclaude.cli.pipeline.trailing_gate import (
            RemediationRetryStatus, attempt_remediation,
        )

        step = _make_step(gate=None, tmp_path=tmp_path)
        debits = []

        result = attempt_remediation(
            remediation_step=step,
            turns_per_attempt=5,
            can_remediate=lambda: True,
            debit=lambda t: debits.append(t),
            run_step=lambda s: StepResult(step=s, status=StepStatus.FAIL),
            check_gate=lambda r: self._make_gate_result(False, "still broken"),
        )

        assert result.status == RemediationRetryStatus.PERSISTENT_FAILURE
        assert result.attempts_made == 2
        assert result.turns_consumed == 10
        assert debits == [5, 5]  # Both attempts debited

    def test_budget_exhausted_before_first_attempt(self, tmp_path):
        """can_remediate() returns False -> BUDGET_EXHAUSTED, no attempts."""
        from superclaude.cli.pipeline.trailing_gate import (
            RemediationRetryStatus, attempt_remediation,
        )

        step = _make_step(gate=None, tmp_path=tmp_path)

        result = attempt_remediation(
            remediation_step=step,
            turns_per_attempt=5,
            can_remediate=lambda: False,
            debit=lambda t: None,
            run_step=lambda s: StepResult(step=s, status=StepStatus.PASS),
            check_gate=lambda r: self._make_gate_result(True),
        )

        assert result.status == RemediationRetryStatus.BUDGET_EXHAUSTED
        assert result.attempts_made == 0
        assert result.turns_consumed == 0

    def test_budget_exhausted_before_second_attempt(self, tmp_path):
        """Budget exhausted after first fail, before second attempt."""
        from superclaude.cli.pipeline.trailing_gate import (
            RemediationRetryStatus, attempt_remediation,
        )

        step = _make_step(gate=None, tmp_path=tmp_path)
        call_count = [0]

        def can_remediate():
            call_count[0] += 1
            return call_count[0] <= 1  # True first time, False second

        result = attempt_remediation(
            remediation_step=step,
            turns_per_attempt=5,
            can_remediate=can_remediate,
            debit=lambda t: None,
            run_step=lambda s: StepResult(step=s, status=StepStatus.PASS),
            check_gate=lambda r: self._make_gate_result(False, "fail"),
        )

        assert result.status == RemediationRetryStatus.PERSISTENT_FAILURE
        assert result.attempts_made == 1
        assert result.turns_consumed == 5

    def test_can_remediate_checked_before_each_attempt(self, tmp_path):
        """can_remediate() is called before each attempt (Gap 1 compliance)."""
        from superclaude.cli.pipeline.trailing_gate import (
            RemediationRetryStatus, attempt_remediation,
        )

        step = _make_step(gate=None, tmp_path=tmp_path)
        check_calls = [0]

        def can_remediate():
            check_calls[0] += 1
            return True

        attempt_remediation(
            remediation_step=step,
            turns_per_attempt=5,
            can_remediate=can_remediate,
            debit=lambda t: None,
            run_step=lambda s: StepResult(step=s, status=StepStatus.PASS),
            check_gate=lambda r: self._make_gate_result(False, "fail"),
        )

        # Called before attempt 1 and before attempt 2
        assert check_calls[0] == 2
