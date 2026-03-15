"""Tests for Phase 8 halt fix — recovery logic, fidelity preflight, context exhaustion."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from superclaude.cli.sprint.executor import (
    _determine_phase_status,
    _write_executor_result_file,
)
from superclaude.cli.sprint.models import (
    MonitorState,
    Phase,
    PhaseStatus,
    SprintConfig,
)


def _make_config(tmp_path: Path, num_phases: int = 1) -> SprintConfig:
    """Create a minimal SprintConfig for testing."""
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


class TestPassRecovered:
    """T09.01: PASS_RECOVERED enum properties."""

    def test_pass_recovered_properties(self):
        """PASS_RECOVERED: is_terminal=True, is_success=True, is_failure=False."""
        s = PhaseStatus.PASS_RECOVERED
        assert s.value == "pass_recovered"
        assert s.is_terminal is True
        assert s.is_success is True
        assert s.is_failure is False


class TestDetectPromptTooLong:
    """T09.02-T09.03: detect_prompt_too_long detection."""

    def test_positive_match(self, tmp_path):
        """detect_prompt_too_long returns True when pattern present."""
        output = tmp_path / "output.jsonl"
        output.write_text(
            '{"type":"error","error":{"type":"invalid_request_error",'
            '"message":"Prompt is too long"}}\n'
        )
        from superclaude.cli.sprint.monitor import detect_prompt_too_long

        assert detect_prompt_too_long(output) is True

    def test_negative_clean(self, tmp_path):
        """detect_prompt_too_long returns False on clean output."""
        output = tmp_path / "output.jsonl"
        output.write_text('{"type":"assistant","content":"hello"}\n')
        from superclaude.cli.sprint.monitor import detect_prompt_too_long

        assert detect_prompt_too_long(output) is False


class TestContextExhaustionRecovery:
    """T09.04-T09.05: Context exhaustion recovery paths."""

    def test_recovery_with_continue_file(self, tmp_path):
        """exit=1 + prompt-too-long + fresh CONTINUE file → PASS_RECOVERED."""
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.jsonl"
        output_file.write_text(
            '{"error":{"message":"Prompt is too long"}}\n'
        )
        started_at = time.time() - 10  # 10 seconds ago
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE\n")
        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
            started_at=started_at,
        )
        assert status == PhaseStatus.PASS_RECOVERED

    def test_stale_file_gives_incomplete(self, tmp_path):
        """exit=1 + prompt-too-long + stale file → INCOMPLETE."""
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.jsonl"
        output_file.write_text(
            '{"error":{"message":"Prompt is too long"}}\n'
        )
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE\n")
        # Make file appear to be from before the phase started
        old_time = time.time() - 3600
        os.utime(result_file, (old_time, old_time))
        started_at = time.time() - 10  # phase started 10s ago, file is 1h old
        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
            started_at=started_at,
        )
        assert status == PhaseStatus.INCOMPLETE


class TestCheckpointInference:
    """T09.06-T09.07: SOL-C checkpoint inference."""

    def test_pass_checkpoint_no_contamination(self, tmp_path):
        """exit=1 + PASS checkpoint + no contamination → PASS_RECOVERED."""
        config = _make_config(tmp_path)
        phase = config.phases[0]
        # Create checkpoint file with PASS
        cp_dir = tmp_path / "checkpoints"
        cp_dir.mkdir()
        cp_file = cp_dir / f"CP-P{phase.number:02d}-END.md"
        cp_file.write_text("## Checkpoint\n**RESULT**: PASS\n")
        # Create results dir for crash recovery log
        (tmp_path / "results").mkdir(exist_ok=True)
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.jsonl"
        output_file.write_text('{"type":"assistant"}\n')
        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
            config=config,
            phase=phase,
        )
        assert status == PhaseStatus.PASS_RECOVERED

    def test_pass_checkpoint_with_contamination(self, tmp_path):
        """exit=1 + PASS checkpoint + contamination → ERROR."""
        config = _make_config(tmp_path)
        phase = config.phases[0]
        # Create checkpoint with PASS
        cp_dir = tmp_path / "checkpoints"
        cp_dir.mkdir()
        cp_file = cp_dir / f"CP-P{phase.number:02d}-END.md"
        cp_file.write_text("STATUS: PASS\n")
        # Create results dir for crash recovery log
        (tmp_path / "results").mkdir(exist_ok=True)
        # Create contaminated artifact (next phase task ID)
        art_dir = tmp_path / "artifacts"
        art_dir.mkdir()
        (art_dir / "test.md").write_text("Working on T02.01 task\n")
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.jsonl"
        output_file.write_text('{"type":"assistant"}\n')
        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
            config=config,
            phase=phase,
        )
        assert status == PhaseStatus.ERROR


class TestFidelityCheck:
    """T09.08-T09.09: Fidelity preflight."""

    def test_fidelity_blocks(self, tmp_path):
        """fidelity_status=fail without override → blocked."""
        state_file = tmp_path / ".roadmap-state.json"
        state_file.write_text(json.dumps({"fidelity_status": "fail"}))
        from superclaude.cli.sprint.commands import _check_fidelity

        blocked, msg = _check_fidelity(tmp_path / "index.md")
        assert blocked is True
        assert "FAILED" in msg

    def test_fidelity_passes(self, tmp_path):
        """fidelity_status=pass → not blocked."""
        state_file = tmp_path / ".roadmap-state.json"
        state_file.write_text(json.dumps({"fidelity_status": "pass"}))
        from superclaude.cli.sprint.commands import _check_fidelity

        blocked, _ = _check_fidelity(tmp_path / "index.md")
        assert blocked is False


class TestExecutorResultFile:
    """T09.10: Executor result file writer."""

    def test_produces_valid_output(self, tmp_path):
        """Executor result file contains correct EXIT_RECOMMENDATION."""
        config = _make_config(tmp_path)
        phase = config.phases[0]
        (tmp_path / "results").mkdir(exist_ok=True)
        ms = MonitorState()
        now = datetime.now(timezone.utc)
        _write_executor_result_file(
            config=config,
            phase=phase,
            status=PhaseStatus.PASS,
            exit_code=0,
            monitor_state=ms,
            started_at=now,
            finished_at=now,
        )
        content = config.result_file(phase).read_text()
        assert "EXIT_RECOMMENDATION: CONTINUE" in content


class TestFailureCategoryContextExhaustion:
    """T09.11: FailureCategory.CONTEXT_EXHAUSTION enum."""

    def test_context_exhaustion_value(self):
        """FailureCategory.CONTEXT_EXHAUSTION exists."""
        from superclaude.cli.sprint.diagnostics import FailureCategory

        assert FailureCategory.CONTEXT_EXHAUSTION.value == "context_exhaustion"


class TestBackwardCompat:
    """T09.12: Backward compatibility of 3-arg _determine_phase_status."""

    def test_three_arg_call(self, tmp_path):
        """3-arg call continues to work (keyword-only defaults)."""
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.jsonl"
        output_file.write_text("some output")
        # 3-arg call should not raise TypeError
        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS_NO_REPORT
