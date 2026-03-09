"""Integration tests for validate_executor -- known-good and known-bad scenarios.

Uses mock step runners (no real subprocesses) to verify:
- Single-agent: known-good input produces report with blocking_count == 0
- Single-agent: known-bad input produces report with blocking_count > 0
- Multi-agent: partial failure produces degraded report
- Missing input files raise FileNotFoundError
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.executor import execute_pipeline
from superclaude.cli.pipeline.models import (
    PipelineConfig,
    Step,
    StepResult,
    StepStatus,
)
from superclaude.cli.roadmap.models import AgentSpec, ValidateConfig
from superclaude.cli.roadmap.validate_executor import (
    _parse_report_counts,
    _write_degraded_report,
    execute_validate,
)


def _now():
    return datetime.now(timezone.utc)


def _make_pipeline_outputs(output_dir: Path) -> None:
    """Write the 3 required input files that the validator reads."""
    (output_dir / "roadmap.md").write_text(
        "---\ntitle: Test Roadmap\n---\n## M1\n- D-001: deliverable\n",
        encoding="utf-8",
    )
    (output_dir / "test-strategy.md").write_text(
        "---\ntitle: Test Strategy\n---\n## M1 Tests\n- T-001: test\n",
        encoding="utf-8",
    )
    (output_dir / "extraction.md").write_text(
        "---\ntitle: Extraction\n---\n## Requirements\n- R-001: requirement\n",
        encoding="utf-8",
    )


def _make_validate_config(
    output_dir: Path,
    agent_count: int = 1,
) -> ValidateConfig:
    """Create a ValidateConfig for testing."""
    agents = [AgentSpec("opus", "architect")]
    if agent_count > 1:
        agents.append(AgentSpec("haiku", "architect"))
    return ValidateConfig(
        output_dir=output_dir,
        agents=agents,
        dry_run=True,  # Use dry_run to avoid real subprocess calls
    )


def _known_good_report() -> str:
    """Report content with 0 blocking issues."""
    lines = [
        "---",
        "blocking_issues_count: 0",
        "warnings_count: 2",
        "tasklist_ready: true",
        "---",
        "",
        "## Findings",
        "",
        "- **[WARNING]** Interleave: ratio at lower bound",
        "  - Location: roadmap.md:section M3",
        "  - Evidence: ratio = 0.15",
        "  - Fix: distribute test activities",
        "",
        "- **[WARNING]** Decomposition: compound deliverable",
        "  - Location: roadmap.md:D-003",
        "  - Evidence: 'implement and test' joined",
        "  - Fix: split into separate deliverables",
        "",
        "- **[INFO]** Schema: all fields present",
        "  - Location: roadmap.md:frontmatter",
        "",
        "## Summary",
        "",
        "0 blocking, 2 warnings, 1 info.",
    ]
    # Pad to meet min_lines
    for i in range(10):
        lines.append(f"- Additional detail line {i}")
    return "\n".join(lines)


def _known_bad_report() -> str:
    """Report content with blocking issues."""
    lines = [
        "---",
        "blocking_issues_count: 3",
        "warnings_count: 1",
        "tasklist_ready: false",
        "---",
        "",
        "## Findings",
        "",
        "- **[BLOCKING]** Schema: missing milestone_count field",
        "  - Location: roadmap.md:frontmatter",
        "  - Evidence: field absent",
        "  - Fix: add milestone_count to frontmatter",
        "",
        "- **[BLOCKING]** Structure: DAG cycle detected",
        "  - Location: roadmap.md:M2->M1",
        "  - Evidence: M2 depends on M1, M1 depends on M2",
        "  - Fix: remove circular dependency",
        "",
        "- **[BLOCKING]** Traceability: untraced requirement R-005",
        "  - Location: extraction.md:R-005",
        "  - Evidence: no deliverable maps to R-005",
        "  - Fix: add deliverable for R-005",
        "",
        "- **[WARNING]** Decomposition: compound deliverable",
        "  - Location: roadmap.md:D-002",
        "  - Evidence: multiple outputs",
        "  - Fix: split deliverable",
        "",
        "## Summary",
        "",
        "3 blocking, 1 warning, 0 info.",
    ]
    for i in range(10):
        lines.append(f"- Additional detail line {i}")
    return "\n".join(lines)


class TestExecuteValidateKnownGood:
    """Known-good input: validation report produced, blocking_count == 0."""

    def test_known_good_single_agent(self, tmp_path, monkeypatch):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)
        config = _make_validate_config(output_dir, agent_count=1)

        # Mock execute_pipeline to write a known-good report
        def mock_execute_pipeline(steps, config, run_step, **kwargs):
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)
            report = validate_dir / "validation-report.md"
            report.write_text(_known_good_report(), encoding="utf-8")
            return [
                StepResult(
                    step=steps[0],
                    status=StepStatus.PASS,
                    attempt=1,
                    started_at=_now(),
                    finished_at=_now(),
                )
            ]

        monkeypatch.setattr(
            "superclaude.cli.roadmap.validate_executor.execute_pipeline",
            mock_execute_pipeline,
        )

        result = execute_validate(config)

        assert result["blocking_count"] == 0
        assert result["warning_count"] == 2
        assert result["info_count"] == 1
        assert (output_dir / "validate" / "validation-report.md").exists()


class TestExecuteValidateKnownBad:
    """Known-bad input: blocking issues detected, blocking_count > 0."""

    def test_known_bad_single_agent(self, tmp_path, monkeypatch):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)
        config = _make_validate_config(output_dir, agent_count=1)

        def mock_execute_pipeline(steps, config, run_step, **kwargs):
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)
            report = validate_dir / "validation-report.md"
            report.write_text(_known_bad_report(), encoding="utf-8")
            return [
                StepResult(
                    step=steps[0],
                    status=StepStatus.PASS,
                    attempt=1,
                    started_at=_now(),
                    finished_at=_now(),
                )
            ]

        monkeypatch.setattr(
            "superclaude.cli.roadmap.validate_executor.execute_pipeline",
            mock_execute_pipeline,
        )

        result = execute_validate(config)

        assert result["blocking_count"] == 3
        assert result["warning_count"] == 1
        assert result["blocking_count"] > 0


class TestExecuteValidateMissingInputs:
    """Missing input files raise FileNotFoundError."""

    def test_missing_roadmap(self, tmp_path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        # Only write 2 of 3 required files
        (output_dir / "test-strategy.md").write_text("content")
        (output_dir / "extraction.md").write_text("content")
        config = _make_validate_config(output_dir)

        with pytest.raises(FileNotFoundError, match="roadmap.md"):
            execute_validate(config)

    def test_missing_test_strategy(self, tmp_path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "roadmap.md").write_text("content")
        (output_dir / "extraction.md").write_text("content")
        config = _make_validate_config(output_dir)

        with pytest.raises(FileNotFoundError, match="test-strategy.md"):
            execute_validate(config)

    def test_missing_extraction(self, tmp_path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "roadmap.md").write_text("content")
        (output_dir / "test-strategy.md").write_text("content")
        config = _make_validate_config(output_dir)

        with pytest.raises(FileNotFoundError, match="extraction.md"):
            execute_validate(config)


class TestPartialFailure:
    """Multi-agent partial failure produces degraded report."""

    def test_degraded_report_on_partial_failure(self, tmp_path, monkeypatch):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)
        config = _make_validate_config(output_dir, agent_count=2)

        def mock_execute_pipeline(steps, config, run_step, **kwargs):
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)

            # Parallel group is steps[0] (list of reflect steps)
            parallel_group = steps[0]
            agent_a_step = parallel_group[0]
            agent_b_step = parallel_group[1]

            # Agent A succeeds, agent B fails
            # Write agent A's reflection file
            agent_a_step.output_file.write_text(
                _known_good_report(), encoding="utf-8"
            )
            return [
                StepResult(
                    step=agent_a_step,
                    status=StepStatus.PASS,
                    attempt=1,
                    started_at=_now(),
                    finished_at=_now(),
                ),
                StepResult(
                    step=agent_b_step,
                    status=StepStatus.FAIL,
                    attempt=2,
                    gate_failure_reason="Step timed out",
                    started_at=_now(),
                    finished_at=_now(),
                ),
            ]

        monkeypatch.setattr(
            "superclaude.cli.roadmap.validate_executor.execute_pipeline",
            mock_execute_pipeline,
        )

        result = execute_validate(config)

        report_path = output_dir / "validate" / "validation-report.md"
        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")
        assert "validation_complete: false" in content
        assert "DEGRADED VALIDATION REPORT" in content
        assert "reflect-haiku-architect" in content

    def test_degraded_report_preserves_successful_reflection(
        self, tmp_path, monkeypatch
    ):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)
        config = _make_validate_config(output_dir, agent_count=2)

        def mock_execute_pipeline(steps, config, run_step, **kwargs):
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)

            parallel_group = steps[0]
            agent_a_step = parallel_group[0]
            agent_b_step = parallel_group[1]

            # Agent A succeeds -- write its file
            agent_a_step.output_file.write_text(
                _known_good_report(), encoding="utf-8"
            )
            return [
                StepResult(
                    step=agent_a_step,
                    status=StepStatus.PASS,
                    attempt=1,
                    started_at=_now(),
                    finished_at=_now(),
                ),
                StepResult(
                    step=agent_b_step,
                    status=StepStatus.FAIL,
                    attempt=2,
                    gate_failure_reason="Agent failed",
                    started_at=_now(),
                    finished_at=_now(),
                ),
            ]

        monkeypatch.setattr(
            "superclaude.cli.roadmap.validate_executor.execute_pipeline",
            mock_execute_pipeline,
        )

        execute_validate(config)

        # Agent A's reflection file is preserved
        reflect_a = output_dir / "validate" / "reflect-opus-architect.md"
        assert reflect_a.exists()


class TestWriteDegradedReport:
    """Unit tests for _write_degraded_report."""

    def test_frontmatter_contains_validation_complete_false(self, tmp_path):
        report = tmp_path / "report.md"
        _write_degraded_report(
            report,
            failed_ids=["reflect-haiku-architect"],
            passed_ids=["reflect-opus-architect"],
        )
        content = report.read_text(encoding="utf-8")
        assert "validation_complete: false" in content

    def test_banner_names_failed_agents(self, tmp_path):
        report = tmp_path / "report.md"
        _write_degraded_report(
            report,
            failed_ids=["reflect-haiku-architect"],
            passed_ids=["reflect-opus-architect"],
        )
        content = report.read_text(encoding="utf-8")
        assert "reflect-haiku-architect" in content
        assert "DEGRADED VALIDATION REPORT" in content

    def test_multiple_failed_agents(self, tmp_path):
        report = tmp_path / "report.md"
        _write_degraded_report(
            report,
            failed_ids=["agent-1", "agent-2"],
            passed_ids=[],
        )
        content = report.read_text(encoding="utf-8")
        assert "agent-1" in content
        assert "agent-2" in content
        assert "passed_agents: none" in content

    def test_creates_parent_directory(self, tmp_path):
        report = tmp_path / "nested" / "dir" / "report.md"
        _write_degraded_report(report, failed_ids=["a"], passed_ids=["b"])
        assert report.exists()


class TestParseReportCounts:
    """Unit tests for _parse_report_counts."""

    def test_parses_known_good(self, tmp_path):
        report = tmp_path / "report.md"
        report.write_text(_known_good_report(), encoding="utf-8")
        result = _parse_report_counts(report)
        assert result["blocking_count"] == 0
        assert result["warning_count"] == 2
        assert result["info_count"] == 1

    def test_parses_known_bad(self, tmp_path):
        report = tmp_path / "report.md"
        report.write_text(_known_bad_report(), encoding="utf-8")
        result = _parse_report_counts(report)
        assert result["blocking_count"] == 3
        assert result["warning_count"] == 1

    def test_missing_file_returns_zeros(self, tmp_path):
        report = tmp_path / "nonexistent.md"
        result = _parse_report_counts(report)
        assert result == {"blocking_count": 0, "warning_count": 0, "info_count": 0}

    def test_no_frontmatter_returns_zeros(self, tmp_path):
        report = tmp_path / "report.md"
        report.write_text("Just plain text, no frontmatter.\n")
        result = _parse_report_counts(report)
        assert result == {"blocking_count": 0, "warning_count": 0, "info_count": 0}
