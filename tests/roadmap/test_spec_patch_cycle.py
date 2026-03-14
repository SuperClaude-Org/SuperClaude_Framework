"""Integration tests for the spec-patch auto-resume cycle in executor.py.

Covers FR-2.24.1.8 through FR-2.24.1.13, AC-5b through AC-10, AC-12, AC-13.
"""

from __future__ import annotations

import hashlib
import json
import os
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.roadmap.executor import (
    _apply_resume_after_spec_patch,
    _find_qualifying_deviation_files,
    read_state,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def setup_dirs(tmp_path: Path):
    """Create a complete output directory with state, spec, and deviation files."""
    spec_file = tmp_path / "spec.md"
    spec_file.write_text("# Original Spec", encoding="utf-8")
    original_hash = hashlib.sha256(spec_file.read_bytes()).hexdigest()

    started_at = datetime.now(timezone.utc)

    state = {
        "schema_version": 1,
        "spec_file": str(spec_file),
        "spec_hash": original_hash,
        "agents": [{"model": "opus", "persona": "architect"}],
        "depth": "standard",
        "last_run": started_at.isoformat(),
        "steps": {
            "spec-fidelity": {
                "status": "FAIL",
                "attempt": 1,
                "output_file": "spec-fidelity.md",
                "started_at": started_at.isoformat(),
                "completed_at": (started_at).isoformat(),
            }
        },
    }
    state_path = tmp_path / ".roadmap-state.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    return tmp_path, spec_file, original_hash, started_at


def _create_deviation(output_dir: Path, dev_id: str = "DEV-001") -> Path:
    """Create a deviation file with current mtime (after spec-fidelity started)."""
    # Small sleep to ensure mtime is strictly after started_at
    time.sleep(0.05)
    dev_file = output_dir / f"dev-{dev_id.lower()}-accepted-deviation.md"
    dev_file.write_text(
        textwrap.dedent(f"""\
        ---
        id: {dev_id}
        disposition: ACCEPTED
        spec_update_required: true
        affects_spec_sections:
          - "4.1"
        acceptance_rationale: test
        ---

        Test deviation.
        """),
        encoding="utf-8",
    )
    return dev_file


def _modify_spec(spec_file: Path) -> str:
    """Modify spec and return new hash."""
    spec_file.write_text("# Modified Spec\nNew content.", encoding="utf-8")
    return hashlib.sha256(spec_file.read_bytes()).hexdigest()


def _make_mock_config(tmp_path: Path, spec_file: Path):
    """Create a mock RoadmapConfig."""
    config = MagicMock()
    config.output_dir = tmp_path
    config.spec_file = spec_file
    config.dry_run = False
    config.work_dir = tmp_path
    return config


def _make_mock_results(status_value="FAIL"):
    """Create mock StepResult list with spec-fidelity step."""
    mock_step = MagicMock()
    mock_step.id = "spec-fidelity"

    mock_status = MagicMock()
    mock_status.value = status_value

    mock_result = MagicMock()
    mock_result.step = mock_step
    mock_result.status = mock_status
    mock_result.started_at = datetime.now(timezone.utc)
    mock_result.finished_at = datetime.now(timezone.utc)

    return [mock_result]


# ---------------------------------------------------------------------------
# TestCycleGuard (FR-2.24.1.11, AC-6)
# ---------------------------------------------------------------------------

class TestCycleGuard:
    """FR-2.24.1.11, AC-6: Cycle fires at most once per invocation."""

    def test_cycle_blocked_when_count_ge_1(self, setup_dirs) -> None:
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        result = _apply_resume_after_spec_patch(
            config=config,
            results=results,
            auto_accept=True,
            initial_spec_hash=original_hash,
            cycle_count=1,  # Already exhausted
        )
        assert result is False  # Cycle not attempted

    def test_cycle_allowed_when_count_0(self, setup_dirs) -> None:
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        # Mock the pipeline re-execution to avoid actually running
        with patch("superclaude.cli.roadmap.executor.execute_pipeline") as mock_exec, \
             patch("superclaude.cli.roadmap.executor._build_steps") as mock_build, \
             patch("superclaude.cli.roadmap.executor._apply_resume") as mock_resume, \
             patch("superclaude.cli.roadmap.executor._save_state"):
            mock_build.return_value = []
            mock_resume.return_value = []
            mock_exec.return_value = []

            result = _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=True,
                initial_spec_hash=original_hash,
                cycle_count=0,
            )
        assert result is True  # Cycle attempted


# ---------------------------------------------------------------------------
# TestDiskReread (FR-2.24.1.10, AC-7)
# ---------------------------------------------------------------------------

class TestDiskReread:
    """FR-2.24.1.10, AC-7: Resume uses post-write disk state."""

    def test_post_write_state_has_new_hash(self, setup_dirs) -> None:
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        new_hash = _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        resume_state_seen = {}

        def capture_resume(steps, config, gate_fn):
            # Read the state that _apply_resume would see
            state = read_state(tmp_path / ".roadmap-state.json")
            resume_state_seen["spec_hash"] = state["spec_hash"]
            return steps

        with patch("superclaude.cli.roadmap.executor.execute_pipeline") as mock_exec, \
             patch("superclaude.cli.roadmap.executor._build_steps") as mock_build, \
             patch("superclaude.cli.roadmap.executor._apply_resume", side_effect=capture_resume), \
             patch("superclaude.cli.roadmap.executor._save_state"):
            mock_build.return_value = []
            mock_exec.return_value = []

            _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=True,
                initial_spec_hash=original_hash,
                cycle_count=0,
            )

        # The state at resume time must have the NEW hash, not the old one
        assert resume_state_seen["spec_hash"] == new_hash


# ---------------------------------------------------------------------------
# TestConditionChecks (FR-2.24.1.9)
# ---------------------------------------------------------------------------

class TestConditionChecks:
    """FR-2.24.1.9: All three conditions required."""

    def test_no_qualifying_files_blocks_cycle(self, setup_dirs) -> None:
        """Condition 2 fails: no deviation files → no cycle."""
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _modify_spec(spec_file)  # Condition 3 met
        # No deviation file created → Condition 2 not met

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        result = _apply_resume_after_spec_patch(
            config=config,
            results=results,
            auto_accept=True,
            initial_spec_hash=original_hash,
            cycle_count=0,
        )
        assert result is False

    def test_spec_hash_unchanged_blocks_cycle(self, setup_dirs) -> None:
        """Condition 3 fails: spec not modified → no cycle."""
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        # Spec NOT modified → Condition 3 not met

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        result = _apply_resume_after_spec_patch(
            config=config,
            results=results,
            auto_accept=True,
            initial_spec_hash=original_hash,
            cycle_count=0,
        )
        assert result is False

    def test_missing_started_at_blocks_cycle(self, setup_dirs) -> None:
        """Fail-closed: absent started_at → condition not met."""
        tmp_path, spec_file, original_hash, _ = setup_dirs

        # Remove started_at from state
        state = json.loads((tmp_path / ".roadmap-state.json").read_text())
        del state["steps"]["spec-fidelity"]["started_at"]
        (tmp_path / ".roadmap-state.json").write_text(
            json.dumps(state, indent=2), encoding="utf-8"
        )

        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        result = _apply_resume_after_spec_patch(
            config=config,
            results=results,
            auto_accept=True,
            initial_spec_hash=original_hash,
            cycle_count=0,
        )
        assert result is False

    def test_mtime_type_conversion(self, setup_dirs) -> None:
        """Verify ISO string → float timestamp conversion works correctly."""
        tmp_path, spec_file, _, started_at = setup_dirs
        config = _make_mock_config(tmp_path, spec_file)

        # Create deviation with known mtime > started_at
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        qualifying = _find_qualifying_deviation_files(config, _make_mock_results())
        assert len(qualifying) >= 1
        # Verify mtime is a float, not a string comparison
        for rec in qualifying:
            assert isinstance(rec.mtime, float)
            assert rec.mtime > started_at.timestamp()


# ---------------------------------------------------------------------------
# TestAutoAccept (FR-2.24.1.8, AC-9)
# ---------------------------------------------------------------------------

class TestAutoAccept:
    """FR-2.24.1.8, AC-9: auto_accept behavior."""

    def test_auto_accept_true_skips_prompt(self, setup_dirs) -> None:
        """auto_accept=True → no interactive prompt."""
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        # Should not call input()
        with patch("superclaude.cli.roadmap.executor.execute_pipeline") as mock_exec, \
             patch("superclaude.cli.roadmap.executor._build_steps") as mock_build, \
             patch("superclaude.cli.roadmap.executor._apply_resume") as mock_resume, \
             patch("superclaude.cli.roadmap.executor._save_state"), \
             patch("builtins.input") as mock_input:
            mock_build.return_value = []
            mock_resume.return_value = []
            mock_exec.return_value = []

            _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=True,
                initial_spec_hash=original_hash,
                cycle_count=0,
            )
            mock_input.assert_not_called()


# ---------------------------------------------------------------------------
# TestBackwardCompat (AC-10)
# ---------------------------------------------------------------------------

class TestBackwardCompat:
    """AC-10: execute_roadmap() callable without auto_accept."""

    def test_signature_backward_compatible(self) -> None:
        """The function should accept old-style calls without auto_accept."""
        import inspect

        from superclaude.cli.roadmap.executor import execute_roadmap

        sig = inspect.signature(execute_roadmap)
        params = list(sig.parameters.keys())
        assert "auto_accept" in params
        # Default should be False
        assert sig.parameters["auto_accept"].default is False


# ---------------------------------------------------------------------------
# TestCycleExhaustion (FR-2.24.1.13, AC-8)
# ---------------------------------------------------------------------------

class TestCycleExhaustion:
    """FR-2.24.1.13, AC-8: Second fidelity fail → exit 1, no loop."""

    def test_resumed_failure_exits_via_sys_exit(self, setup_dirs) -> None:
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        # Simulate resumed pipeline also failing
        mock_fail_result = MagicMock()
        mock_fail_step = MagicMock()
        mock_fail_step.id = "spec-fidelity"
        mock_fail_result.step = mock_fail_step
        from superclaude.cli.roadmap.executor import StepStatus
        mock_fail_result.status = StepStatus.FAIL
        mock_fail_result.started_at = datetime.now(timezone.utc)
        mock_fail_result.finished_at = datetime.now(timezone.utc)

        with patch("superclaude.cli.roadmap.executor.execute_pipeline") as mock_exec, \
             patch("superclaude.cli.roadmap.executor._build_steps") as mock_build, \
             patch("superclaude.cli.roadmap.executor._apply_resume") as mock_resume, \
             patch("superclaude.cli.roadmap.executor._save_state"), \
             patch("superclaude.cli.roadmap.executor._format_halt_output", return_value="HALT"):
            mock_build.return_value = []
            mock_resume.return_value = []
            mock_exec.return_value = [mock_fail_result]

            with pytest.raises(SystemExit) as exc_info:
                _apply_resume_after_spec_patch(
                    config=config,
                    results=results,
                    auto_accept=True,
                    initial_spec_hash=original_hash,
                    cycle_count=0,
                )
            assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# TestWriteFailure (FR-2.24.1.10 Step 3, AC-13)
# ---------------------------------------------------------------------------

class TestWriteFailure:
    """FR-2.24.1.10 Step 3: Atomic write failure → abort cycle."""

    def test_write_failure_aborts_cycle(self, setup_dirs) -> None:
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        with patch("superclaude.cli.roadmap.executor.write_state", side_effect=OSError("disk full")):
            result = _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=True,
                initial_spec_hash=original_hash,
                cycle_count=0,
            )
        # Cycle was attempted but failed — returns True (don't retry)
        assert result is True

    def test_write_failure_logs_to_stderr(self, setup_dirs, capsys) -> None:
        """AC-13: write failure logs error to stderr."""
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        with patch("superclaude.cli.roadmap.executor.write_state", side_effect=OSError("disk full")):
            _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=True,
                initial_spec_hash=original_hash,
                cycle_count=0,
            )
        captured = capsys.readouterr()
        assert "[roadmap] ERROR" in captured.err
        assert "disk full" in captured.err

    def test_write_failure_preserves_state_mtime(self, setup_dirs) -> None:
        """State file mtime unchanged after write-failure abort."""
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        state_path = tmp_path / ".roadmap-state.json"
        mtime_before = os.path.getmtime(state_path)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        with patch("superclaude.cli.roadmap.executor.write_state", side_effect=OSError("disk full")):
            _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=True,
                initial_spec_hash=original_hash,
                cycle_count=0,
            )
        mtime_after = os.path.getmtime(state_path)
        assert mtime_before == mtime_after

    def test_write_failure_preserves_all_state_keys(self, setup_dirs) -> None:
        """All non-spec_hash keys preserved after write-failure abort."""
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        state_path = tmp_path / ".roadmap-state.json"
        state_before = json.loads(state_path.read_text(encoding="utf-8"))

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        with patch("superclaude.cli.roadmap.executor.write_state", side_effect=OSError("disk full")):
            _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=True,
                initial_spec_hash=original_hash,
                cycle_count=0,
            )
        state_after = json.loads(state_path.read_text(encoding="utf-8"))
        assert state_before == state_after


# ---------------------------------------------------------------------------
# TestStateIntegrity (T04.04)
# ---------------------------------------------------------------------------

class TestStateIntegrity:
    """State integrity across all mutation and abort paths."""

    def test_only_spec_hash_changes_in_auto_resume(self, setup_dirs) -> None:
        """After auto-resume cycle, only spec_hash differs from original state."""
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        state_path = tmp_path / ".roadmap-state.json"
        state_before = json.loads(state_path.read_text(encoding="utf-8"))

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        with patch("superclaude.cli.roadmap.executor.execute_pipeline") as mock_exec, \
             patch("superclaude.cli.roadmap.executor._build_steps") as mock_build, \
             patch("superclaude.cli.roadmap.executor._apply_resume") as mock_resume, \
             patch("superclaude.cli.roadmap.executor._save_state"):
            mock_build.return_value = []
            mock_resume.return_value = []
            mock_exec.return_value = []

            _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=True,
                initial_spec_hash=original_hash,
                cycle_count=0,
            )

        state_after = json.loads(state_path.read_text(encoding="utf-8"))
        # spec_hash must have changed
        assert state_after["spec_hash"] != state_before["spec_hash"]
        # All other keys must be byte-identical
        for key in state_before:
            if key != "spec_hash":
                assert state_after[key] == state_before[key], f"Key '{key}' changed unexpectedly"

    def test_disk_reread_passed_to_apply_resume(self, setup_dirs) -> None:
        """AC-7: _apply_resume receives disk-reread state, not in-memory."""
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        new_hash = _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        resume_called_with_config = {}

        def spy_resume(steps, config, gate_fn):
            # At this point, state on disk should have the new hash
            state = read_state(tmp_path / ".roadmap-state.json")
            resume_called_with_config["spec_hash"] = state["spec_hash"]
            return steps

        with patch("superclaude.cli.roadmap.executor.execute_pipeline") as mock_exec, \
             patch("superclaude.cli.roadmap.executor._build_steps") as mock_build, \
             patch("superclaude.cli.roadmap.executor._apply_resume", side_effect=spy_resume), \
             patch("superclaude.cli.roadmap.executor._save_state"):
            mock_build.return_value = []
            mock_exec.return_value = []

            _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=True,
                initial_spec_hash=original_hash,
                cycle_count=0,
            )

        # _apply_resume must have seen the post-write (new) hash
        assert resume_called_with_config["spec_hash"] == new_hash
        assert resume_called_with_config["spec_hash"] != original_hash

    def test_cli_abort_n_preserves_mtime(self, setup_dirs) -> None:
        """CLI N-answer abort leaves file mtime unchanged."""
        tmp_path, spec_file, _, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        state_path = tmp_path / ".roadmap-state.json"
        mtime_before = os.path.getmtime(state_path)

        from superclaude.cli.roadmap.spec_patch import prompt_accept_spec_change
        with patch("builtins.input", return_value="n"), \
             patch("superclaude.cli.roadmap.spec_patch.sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            prompt_accept_spec_change(tmp_path)

        mtime_after = os.path.getmtime(state_path)
        assert mtime_before == mtime_after


# ---------------------------------------------------------------------------
# TestLogging (FR-2.24.1.12, AC-12)
# ---------------------------------------------------------------------------

class TestLogging:
    """FR-2.24.1.12, AC-12: Log messages with [roadmap] prefix."""

    def test_cycle_entry_logging(self, setup_dirs, capsys) -> None:
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        with patch("superclaude.cli.roadmap.executor.execute_pipeline") as mock_exec, \
             patch("superclaude.cli.roadmap.executor._build_steps") as mock_build, \
             patch("superclaude.cli.roadmap.executor._apply_resume") as mock_resume, \
             patch("superclaude.cli.roadmap.executor._save_state"):
            mock_build.return_value = []
            mock_resume.return_value = []
            mock_exec.return_value = []

            _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=True,
                initial_spec_hash=original_hash,
                cycle_count=0,
            )

        captured = capsys.readouterr()
        assert "[roadmap] Spec patched by subprocess." in captured.out
        assert "accepted deviation record(s)" in captured.out
        assert "[roadmap] Triggering spec-hash sync and resume (cycle 1/1)." in captured.out
        assert "[roadmap] Spec-patch resume cycle complete." in captured.out

    def test_cycle_guard_preserves_state_mtime(self, setup_dirs) -> None:
        """State mtime unchanged when cycle guard blocks."""
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        state_path = tmp_path / ".roadmap-state.json"
        mtime_before = os.path.getmtime(state_path)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        _apply_resume_after_spec_patch(
            config=config,
            results=results,
            auto_accept=True,
            initial_spec_hash=original_hash,
            cycle_count=1,  # Exhausted
        )
        mtime_after = os.path.getmtime(state_path)
        assert mtime_before == mtime_after

    def test_suppression_logging(self, setup_dirs, capsys) -> None:
        tmp_path, spec_file, original_hash, _ = setup_dirs
        _create_deviation(tmp_path)
        _modify_spec(spec_file)

        config = _make_mock_config(tmp_path, spec_file)
        results = _make_mock_results()

        _apply_resume_after_spec_patch(
            config=config,
            results=results,
            auto_accept=True,
            initial_spec_hash=original_hash,
            cycle_count=1,  # Exhausted
        )

        captured = capsys.readouterr()
        assert "Spec-patch cycle already exhausted" in captured.out
        assert "cycle_count=1" in captured.out
