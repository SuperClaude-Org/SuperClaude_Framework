"""Functional test: error_max_turns detection and INCOMPLETE reclassification.

Validates the core fix for the "silent incompletion" bug where phases that
exhausted their turn budget were incorrectly reported as PASS_NO_REPORT
(a success status) instead of INCOMPLETE (a failure status).

Test targets:
  - src/superclaude/cli/sprint/monitor.py :: detect_error_max_turns()
  - src/superclaude/cli/sprint/monitor.py :: ERROR_MAX_TURNS_PATTERN
  - src/superclaude/cli/sprint/executor.py :: _determine_phase_status()
  - src/superclaude/cli/sprint/models.py :: PhaseStatus.INCOMPLETE
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from superclaude.cli.sprint.monitor import (
    ERROR_MAX_TURNS_PATTERN,
    detect_error_max_turns,
)
from superclaude.cli.sprint.executor import _determine_phase_status
from superclaude.cli.sprint.models import PhaseStatus


# ---------------------------------------------------------------------------
# Synthetic NDJSON fixtures
# ---------------------------------------------------------------------------

# Realistic NDJSON output ending with error_max_turns — the budget-exhaustion
# signal emitted by Claude Code when a subprocess hits its turn limit.
NDJSON_WITH_ERROR_MAX_TURNS = textwrap.dedent("""\
    {"type":"system","subtype":"init","session_id":"sess-abc123"}
    {"type":"assistant","message":{"role":"assistant","content":"Starting task T01.01..."}}
    {"type":"tool_use","tool":"Read","input":{"file_path":"/src/main.py"}}
    {"type":"tool_result","tool":"Read","output":"contents here..."}
    {"type":"assistant","message":{"role":"assistant","content":"Analyzing the file..."}}
    {"type":"tool_use","tool":"Edit","input":{"file_path":"/src/main.py"}}
    {"type":"tool_result","tool":"Edit","output":"edited successfully"}
    {"type":"assistant","message":{"role":"assistant","content":"I need to continue but..."}}
    {"type":"system","subtype":"error_max_turns","message":"Max turns reached"}
""")

# Normal NDJSON output that completes successfully — no error_max_turns.
NDJSON_NORMAL_COMPLETION = textwrap.dedent("""\
    {"type":"system","subtype":"init","session_id":"sess-def456"}
    {"type":"assistant","message":{"role":"assistant","content":"Starting task T01.01..."}}
    {"type":"tool_use","tool":"Read","input":{"file_path":"/src/main.py"}}
    {"type":"tool_result","tool":"Read","output":"contents here..."}
    {"type":"assistant","message":{"role":"assistant","content":"Task complete."}}
    {"type":"result","subtype":"success","result":"All tasks completed."}
""")

# Edge case: error_max_turns appears in the middle but NOT the last line.
# This should NOT trigger detection — only the last line matters.
NDJSON_ERROR_MID_STREAM = textwrap.dedent("""\
    {"type":"system","subtype":"init","session_id":"sess-ghi789"}
    {"type":"system","subtype":"error_max_turns","message":"Mid-stream noise"}
    {"type":"assistant","message":{"role":"assistant","content":"Recovered and continuing..."}}
    {"type":"result","subtype":"success","result":"Completed after recovery."}
""")

# Edge case: output with trailing blank lines after error_max_turns.
NDJSON_ERROR_MAX_TURNS_TRAILING_BLANKS = textwrap.dedent("""\
    {"type":"system","subtype":"init","session_id":"sess-trail"}
    {"type":"assistant","message":{"role":"assistant","content":"Working..."}}
    {"type":"system","subtype":"error_max_turns","message":"Max turns reached"}


""")

# Edge case: empty file.
NDJSON_EMPTY = ""

# Edge case: whitespace-only file.
NDJSON_WHITESPACE_ONLY = "   \n\n   \n"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_output(tmp_path: Path, content: str, name: str = "output.txt") -> Path:
    """Write synthetic NDJSON content to a temporary file."""
    p = tmp_path / name
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# Test Suite 1: Regex pattern matching (ERROR_MAX_TURNS_PATTERN)
# ---------------------------------------------------------------------------

class TestErrorMaxTurnsPattern:
    """Verify the regex matches real and varied NDJSON error_max_turns lines."""

    def test_matches_compact_json(self):
        line = '{"type":"system","subtype":"error_max_turns","message":"Max turns reached"}'
        assert ERROR_MAX_TURNS_PATTERN.search(line) is not None

    def test_matches_spaced_json(self):
        line = '{"type": "system", "subtype": "error_max_turns", "message": "Max turns reached"}'
        assert ERROR_MAX_TURNS_PATTERN.search(line) is not None

    def test_matches_extra_whitespace(self):
        line = '{"subtype"  :  "error_max_turns"}'
        assert ERROR_MAX_TURNS_PATTERN.search(line) is not None

    def test_no_match_on_success(self):
        line = '{"type":"result","subtype":"success","result":"All tasks completed."}'
        assert ERROR_MAX_TURNS_PATTERN.search(line) is None

    def test_no_match_on_init(self):
        line = '{"type":"system","subtype":"init","session_id":"sess-abc"}'
        assert ERROR_MAX_TURNS_PATTERN.search(line) is None

    def test_no_match_on_plain_text(self):
        line = "error_max_turns happened"
        assert ERROR_MAX_TURNS_PATTERN.search(line) is None

    def test_no_match_on_partial_key(self):
        """The pattern requires the JSON key-value structure, not just the value."""
        line = '"error_max_turns"'
        assert ERROR_MAX_TURNS_PATTERN.search(line) is None


# ---------------------------------------------------------------------------
# Test Suite 2: detect_error_max_turns() function
# ---------------------------------------------------------------------------

class TestDetectErrorMaxTurns:
    """Verify the file-level detection function scans the last NDJSON line."""

    def test_detects_error_max_turns_in_last_line(self, tmp_path):
        path = _write_output(tmp_path, NDJSON_WITH_ERROR_MAX_TURNS)
        assert detect_error_max_turns(path) is True

    def test_no_detection_on_normal_completion(self, tmp_path):
        path = _write_output(tmp_path, NDJSON_NORMAL_COMPLETION)
        assert detect_error_max_turns(path) is False

    def test_no_detection_when_error_only_mid_stream(self, tmp_path):
        """error_max_turns in the middle of the stream should be ignored."""
        path = _write_output(tmp_path, NDJSON_ERROR_MID_STREAM)
        assert detect_error_max_turns(path) is False

    def test_detects_with_trailing_blank_lines(self, tmp_path):
        """Trailing whitespace/blank lines should be skipped to find the real last line."""
        path = _write_output(tmp_path, NDJSON_ERROR_MAX_TURNS_TRAILING_BLANKS)
        assert detect_error_max_turns(path) is True

    def test_returns_false_for_empty_file(self, tmp_path):
        path = _write_output(tmp_path, NDJSON_EMPTY)
        assert detect_error_max_turns(path) is False

    def test_returns_false_for_whitespace_only_file(self, tmp_path):
        path = _write_output(tmp_path, NDJSON_WHITESPACE_ONLY)
        assert detect_error_max_turns(path) is False

    def test_returns_false_for_missing_file(self, tmp_path):
        path = tmp_path / "nonexistent.txt"
        assert detect_error_max_turns(path) is False


# ---------------------------------------------------------------------------
# Test Suite 3: _determine_phase_status() reclassification
# ---------------------------------------------------------------------------

class TestDeterminePhaseStatusReclassification:
    """Verify the executor reclassifies PASS_NO_REPORT to INCOMPLETE
    when error_max_turns is detected in the output file.

    This is the core "silent incompletion" bug fix: previously, exit_code=0
    with output but no result file yielded PASS_NO_REPORT (success).
    Now it checks for error_max_turns and returns INCOMPLETE (failure).
    """

    def test_exit0_no_result_with_error_max_turns_yields_incomplete(self, tmp_path):
        """The primary reclassification case: PASS_NO_REPORT -> INCOMPLETE."""
        result_file = tmp_path / "result.md"  # does not exist
        output_file = _write_output(tmp_path, NDJSON_WITH_ERROR_MAX_TURNS, "output.txt")

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )

        assert status == PhaseStatus.INCOMPLETE
        assert status.is_failure is True
        assert status.is_success is False

    def test_exit0_no_result_normal_completion_yields_pass_no_report(self, tmp_path):
        """Normal completion without a result file should still be PASS_NO_REPORT."""
        result_file = tmp_path / "result.md"  # does not exist
        output_file = _write_output(tmp_path, NDJSON_NORMAL_COMPLETION, "output.txt")

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )

        assert status == PhaseStatus.PASS_NO_REPORT
        assert status.is_success is True
        assert status.is_failure is False

    def test_exit0_with_result_file_ignores_error_max_turns(self, tmp_path):
        """When a result file exists with CONTINUE, the output file is not checked."""
        result_file = tmp_path / "result.md"
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE\nstatus: PASS\n")
        output_file = _write_output(tmp_path, NDJSON_WITH_ERROR_MAX_TURNS, "output.txt")

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )

        # Result file takes priority — error_max_turns in output is not consulted
        assert status == PhaseStatus.PASS

    def test_nonzero_exit_yields_error_regardless(self, tmp_path):
        """Non-zero exit code -> ERROR, regardless of output content."""
        result_file = tmp_path / "result.md"
        output_file = _write_output(tmp_path, NDJSON_WITH_ERROR_MAX_TURNS, "output.txt")

        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
        )

        assert status == PhaseStatus.ERROR

    def test_timeout_exit_yields_timeout_regardless(self, tmp_path):
        """Exit code 124 (timeout) -> TIMEOUT, regardless of output content."""
        result_file = tmp_path / "result.md"
        output_file = _write_output(tmp_path, NDJSON_WITH_ERROR_MAX_TURNS, "output.txt")

        status = _determine_phase_status(
            exit_code=124,
            result_file=result_file,
            output_file=output_file,
        )

        assert status == PhaseStatus.TIMEOUT

    def test_no_output_no_result_yields_error(self, tmp_path):
        """No output file and no result file -> ERROR."""
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"
        # Neither file exists

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )

        assert status == PhaseStatus.ERROR


# ---------------------------------------------------------------------------
# Test Suite 4: PhaseStatus.INCOMPLETE properties
# ---------------------------------------------------------------------------

class TestPhaseStatusIncompleteProperties:
    """Confirm INCOMPLETE is classified correctly in the status hierarchy."""

    def test_incomplete_is_terminal(self):
        assert PhaseStatus.INCOMPLETE.is_terminal is True

    def test_incomplete_is_failure(self):
        assert PhaseStatus.INCOMPLETE.is_failure is True

    def test_incomplete_is_not_success(self):
        assert PhaseStatus.INCOMPLETE.is_success is False

    def test_pass_no_report_is_success(self):
        """Confirm the status that INCOMPLETE replaces is indeed a success status."""
        assert PhaseStatus.PASS_NO_REPORT.is_success is True
        assert PhaseStatus.PASS_NO_REPORT.is_failure is False
