"""Tests for sprint monitor — signal extraction from output files."""

import time

from superclaude.cli.sprint.monitor import (
    FILES_CHANGED_PATTERN,
    TASK_ID_PATTERN,
    TOOL_PATTERN,
    OutputMonitor,
    count_turns_from_output,
    detect_error_max_turns,
)


class TestPatterns:
    """Test regex patterns for signal extraction."""

    def test_task_id_pattern(self):
        text = "Working on T02.05 now"
        matches = TASK_ID_PATTERN.findall(text)
        assert "T02.05" in matches

    def test_task_id_multiple(self):
        text = "T01.01 done, starting T01.02"
        matches = TASK_ID_PATTERN.findall(text)
        assert matches == ["T01.01", "T01.02"]

    def test_tool_pattern(self):
        text = "Using Read tool to examine file"
        matches = TOOL_PATTERN.findall(text)
        assert "Read" in matches

    def test_tool_pattern_multiple(self):
        text = "Read the file, then Edit it, then Bash to test"
        matches = TOOL_PATTERN.findall(text)
        assert "Read" in matches
        assert "Edit" in matches
        assert "Bash" in matches

    def test_files_changed_pattern(self):
        text = "modified `src/main.py`"
        matches = FILES_CHANGED_PATTERN.findall(text)
        assert "src/main.py" in matches

    def test_files_changed_multiple_verbs(self):
        text = "created foo.py, edited bar.ts, wrote config.json"
        matches = FILES_CHANGED_PATTERN.findall(text)
        assert "foo.py" in matches
        assert "bar.ts" in matches
        assert "config.json" in matches


class TestOutputMonitor:
    """Test the background output monitor."""

    def test_initial_state(self, tmp_path):
        output_file = tmp_path / "output.txt"
        monitor = OutputMonitor(output_file)
        assert monitor.state.output_bytes == 0
        assert monitor.state.last_task_id == ""

    def test_detects_new_content(self, tmp_path):
        output_file = tmp_path / "output.txt"
        output_file.write_text("Working on T01.01\n")

        monitor = OutputMonitor(output_file, poll_interval=0.1)
        monitor.start()
        time.sleep(0.3)  # Give monitor time to poll
        monitor.stop()

        assert monitor.state.output_bytes > 0
        assert monitor.state.last_task_id == "T01.01"

    def test_detects_tool_usage(self, tmp_path):
        output_file = tmp_path / "output.txt"
        output_file.write_text("Using Edit tool\n")

        monitor = OutputMonitor(output_file, poll_interval=0.1)
        monitor.start()
        time.sleep(0.3)
        monitor.stop()

        assert monitor.state.last_tool_used == "Edit"

    def test_stop_terminates_thread(self, tmp_path):
        output_file = tmp_path / "output.txt"
        output_file.write_text("")

        monitor = OutputMonitor(output_file, poll_interval=0.1)
        monitor.start()
        monitor.stop()
        assert not monitor._thread.is_alive()

    def test_reset_clears_state(self, tmp_path):
        output_file = tmp_path / "output.txt"
        output_file.write_text("T01.01 Read\n")

        monitor = OutputMonitor(output_file, poll_interval=0.1)
        monitor.start()
        time.sleep(0.3)
        monitor.stop()

        # Reset
        new_output = tmp_path / "output2.txt"
        monitor.reset(new_output)
        assert monitor.state.output_bytes == 0
        assert monitor.state.last_task_id == ""

    def test_handles_missing_file(self, tmp_path):
        output_file = tmp_path / "nonexistent.txt"
        monitor = OutputMonitor(output_file, poll_interval=0.1)
        monitor.start()
        time.sleep(0.3)
        monitor.stop()
        # Should not crash, just return 0 bytes
        assert monitor.state.output_bytes == 0

    def test_incremental_read(self, tmp_path):
        output_file = tmp_path / "output.txt"
        output_file.write_text("Line 1\n")

        monitor = OutputMonitor(output_file, poll_interval=0.1)
        monitor.start()
        time.sleep(0.3)

        # Append more data
        with open(output_file, "a") as f:
            f.write("T02.03 using Grep\n")

        time.sleep(0.3)
        monitor.stop()

        assert monitor.state.last_task_id == "T02.03"
        assert monitor.state.last_tool_used == "Grep"


class TestDetectErrorMaxTurns:
    """Tests for error_max_turns NDJSON detection."""

    def test_detects_error_max_turns_last_line(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text(
            '{"type":"result","subtype":"success"}\n'
            '{"type":"result","subtype":"error_max_turns"}\n'
        )
        assert detect_error_max_turns(output) is True

    def test_no_false_positive_on_success(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text('{"type":"result","subtype":"success"}\n')
        assert detect_error_max_turns(output) is False

    def test_no_false_positive_on_other_error(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text('{"type":"result","subtype":"error_timeout"}\n')
        assert detect_error_max_turns(output) is False

    def test_empty_output(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text("")
        assert detect_error_max_turns(output) is False

    def test_missing_file(self, tmp_path):
        output = tmp_path / "nonexistent.txt"
        assert detect_error_max_turns(output) is False

    def test_truncated_ndjson(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text('{"type":"result","sub')
        assert detect_error_max_turns(output) is False

    def test_multiple_lines_only_checks_last(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text(
            '{"type":"result","subtype":"error_max_turns"}\n'
            '{"type":"result","subtype":"success"}\n'
        )
        assert detect_error_max_turns(output) is False

    def test_trailing_whitespace(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text('{"type":"result","subtype":"error_max_turns"}\n\n\n')
        assert detect_error_max_turns(output) is True


class TestCountTurnsFromOutput:
    """Tests for turn counting from NDJSON subprocess output."""

    def test_counts_assistant_turns(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text(
            '{"type":"assistant","text":"Hello"}\n'
            '{"type":"tool_use","name":"Read"}\n'
            '{"type":"tool_result","content":"file content"}\n'
            '{"type":"assistant","text":"I see the file"}\n'
            '{"type":"result","subtype":"success"}\n'
        )
        assert count_turns_from_output(output) == 2

    def test_zero_turns_on_empty(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text("")
        assert count_turns_from_output(output) == 0

    def test_zero_turns_missing_file(self, tmp_path):
        output = tmp_path / "nonexistent.txt"
        assert count_turns_from_output(output) == 0

    def test_no_assistant_messages(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text(
            '{"type":"tool_use","name":"Read"}\n'
            '{"type":"tool_result","content":"data"}\n'
        )
        assert count_turns_from_output(output) == 0

    def test_many_turns(self, tmp_path):
        output = tmp_path / "output.txt"
        lines = [f'{{"type":"assistant","text":"turn {i}"}}\n' for i in range(10)]
        output.write_text("".join(lines))
        assert count_turns_from_output(output) == 10

    def test_handles_malformed_json_lines(self, tmp_path):
        output = tmp_path / "output.txt"
        output.write_text(
            '{"type":"assistant","text":"Hello"}\n'
            "not valid json\n"
            '{"type":"assistant","text":"World"}\n'
        )
        # Should still count the valid assistant lines
        assert count_turns_from_output(output) == 2
