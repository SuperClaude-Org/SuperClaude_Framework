"""Tests for sprint executor — status determination and orchestration."""


from superclaude.cli.sprint.executor import _determine_phase_status
from superclaude.cli.sprint.models import PhaseStatus


class TestDeterminePhaseStatus:
    """Test the 7-level status priority chain."""

    def test_timeout_exit_code(self, tmp_path):
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"
        output_file.write_text("some output")

        status = _determine_phase_status(
            exit_code=124,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.TIMEOUT

    def test_timeout_overrides_result_file(self, tmp_path):
        """Timeout (exit 124) takes priority over result file content."""
        result_file = tmp_path / "result.md"
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=124,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.TIMEOUT

    def test_nonzero_exit_error(self, tmp_path):
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"
        output_file.write_text("some output")

        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.ERROR

    def test_nonzero_exit_overrides_continue_signal(self, tmp_path):
        """Non-zero exit takes priority over CONTINUE signal."""
        result_file = tmp_path / "result.md"
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.ERROR

    def test_halt_signal(self, tmp_path):
        result_file = tmp_path / "result.md"
        result_file.write_text("EXIT_RECOMMENDATION: HALT")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT

    def test_continue_signal(self, tmp_path):
        result_file = tmp_path / "result.md"
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS

    def test_yaml_status_pass(self, tmp_path):
        result_file = tmp_path / "result.md"
        result_file.write_text("---\nstatus: PASS\n---\n")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS

    def test_yaml_status_fail(self, tmp_path):
        result_file = tmp_path / "result.md"
        result_file.write_text("---\nstatus: FAIL\n---\n")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT

    def test_result_file_no_signals(self, tmp_path):
        result_file = tmp_path / "result.md"
        result_file.write_text("Some result content without signals")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS_NO_SIGNAL

    def test_no_result_file_with_output(self, tmp_path):
        result_file = tmp_path / "result.md"
        # Don't create result file
        output_file = tmp_path / "output.txt"
        output_file.write_text("Claude output here")

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS_NO_REPORT

    def test_no_result_no_output(self, tmp_path):
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"
        # Neither file exists

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.ERROR

    def test_empty_output_file(self, tmp_path):
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"
        output_file.write_text("")  # empty

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.ERROR

    # --- Regression tests for case-sensitivity and signal conflict fixes ---

    def test_continue_signal_case_insensitive(self, tmp_path):
        """Lowercase EXIT_RECOMMENDATION: continue must still produce PASS."""
        result_file = tmp_path / "result.md"
        result_file.write_text("exit_recommendation: continue\n")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS

    def test_halt_signal_case_insensitive(self, tmp_path):
        """Lowercase EXIT_RECOMMENDATION: halt must still produce HALT."""
        result_file = tmp_path / "result.md"
        result_file.write_text("exit_recommendation: halt\n")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT

    def test_both_continue_and_halt_halt_wins(self, tmp_path):
        """When both EXIT_RECOMMENDATION tokens appear, HALT must win (safer outcome)."""
        result_file = tmp_path / "result.md"
        # CONTINUE appears before HALT — HALT must still win
        result_file.write_text(
            "EXIT_RECOMMENDATION: CONTINUE\n"
            "Some tasks failed.\n"
            "EXIT_RECOMMENDATION: HALT\n"
        )
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT

    def test_partial_status_produces_halt(self, tmp_path):
        """PARTIAL status in result file must produce HALT (existing behavior, regression guard)."""
        result_file = tmp_path / "result.md"
        result_file.write_text("---\nstatus: PARTIAL\n---\n")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT
