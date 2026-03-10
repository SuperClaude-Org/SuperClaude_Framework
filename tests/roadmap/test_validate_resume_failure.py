"""Additional integration tests for CLI integration and resume paths -- SC-004, SC-005.

Supplements test_validate_cli.py with the resume-failure test case:
- Resume-failure: pipeline halts on failed step, validation does NOT run.

The other acceptance criteria are already covered:
- SC-004: test_auto_invoke_after_success
- SC-005: test_no_validate_skips_auto_invoke
- Resume-success: test_resume_invokes_when_not_yet_validated
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.cli.pipeline.models import StepResult, StepStatus, Step
from superclaude.cli.roadmap.executor import execute_roadmap, write_state
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig


def _now():
    return datetime.now(timezone.utc)


class TestResumeFailureSkipsValidation:
    """Resume-failure: pipeline halts on failed step, validation does NOT run.

    When --resume is used and the pipeline halts due to a step failure,
    execute_roadmap calls sys.exit(1) before reaching the validation code.
    Therefore _auto_invoke_validate is never called.
    """

    def test_resume_halt_skips_validation(self, tmp_path):
        """Resumed pipeline that halts on a failed step does NOT invoke validation."""
        spec = tmp_path / "spec.md"
        spec.write_text("# Spec\nContent.\n")
        output = tmp_path / "output"
        output.mkdir()

        # Pre-populate state
        write_state(
            {"schema_version": 1, "spec_hash": ""},
            output / ".roadmap-state.json",
        )

        config = RoadmapConfig(
            spec_file=spec,
            output_dir=output,
            work_dir=output,
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
        )

        # Mock execute_pipeline to return a failure
        fail_step = Step(
            id="merge",
            prompt="test",
            output_file=output / "roadmap.md",
            gate=None,
            timeout_seconds=300,
            retry_limit=1,
        )
        fail_result = StepResult(
            step=fail_step,
            status=StepStatus.FAIL,
            attempt=2,
            gate_failure_reason="Gate check failed: min_lines not met",
            started_at=_now(),
            finished_at=_now(),
        )

        with (
            patch(
                "superclaude.cli.roadmap.executor.execute_pipeline",
                return_value=[fail_result],
            ),
            patch(
                "superclaude.cli.roadmap.executor._auto_invoke_validate"
            ) as mock_validate,
            patch(
                "superclaude.cli.roadmap.executor._apply_resume",
                return_value=[fail_step],
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            execute_roadmap(config, resume=True)

        # Pipeline halted with exit code 1
        assert exc_info.value.code == 1
        # Validation was never called
        mock_validate.assert_not_called()

    def test_non_resume_halt_also_skips_validation(self, tmp_path):
        """Normal (non-resume) pipeline halt also does NOT invoke validation."""
        spec = tmp_path / "spec.md"
        spec.write_text("# Spec\nContent.\n")
        output = tmp_path / "output"
        output.mkdir()

        config = RoadmapConfig(
            spec_file=spec,
            output_dir=output,
            work_dir=output,
        )

        fail_step = Step(
            id="extract",
            prompt="test",
            output_file=output / "extraction.md",
            gate=None,
            timeout_seconds=300,
            retry_limit=1,
        )
        fail_result = StepResult(
            step=fail_step,
            status=StepStatus.FAIL,
            attempt=2,
            gate_failure_reason="Process exited with code 1",
            started_at=_now(),
            finished_at=_now(),
        )

        with (
            patch(
                "superclaude.cli.roadmap.executor.execute_pipeline",
                return_value=[fail_result],
            ),
            patch(
                "superclaude.cli.roadmap.executor._auto_invoke_validate"
            ) as mock_validate,
            pytest.raises(SystemExit),
        ):
            execute_roadmap(config)

        mock_validate.assert_not_called()
