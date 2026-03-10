"""Integration tests for standalone validation modes -- SC-001 and SC-003.

SC-001: Single-agent validation produces validation-report.md with valid frontmatter.
SC-003: Multi-agent validation produces per-agent reflection files and merged report
        with agreement table.

Uses mock step runners (no real subprocesses) to verify report structure
and file output conventions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import StepResult, StepStatus
from superclaude.cli.roadmap.models import AgentSpec, ValidateConfig
from superclaude.cli.roadmap.validate_executor import execute_validate


def _now():
    return datetime.now(timezone.utc)


def _make_pipeline_outputs(output_dir: Path) -> None:
    """Write the 3 required input files."""
    (output_dir / "roadmap.md").write_text(
        "---\ntitle: Test Roadmap\n---\n## M1\n- D-001: deliverable\n"
    )
    (output_dir / "test-strategy.md").write_text(
        "---\ntitle: Test Strategy\n---\n## M1 Tests\n- T-001: test\n"
    )
    (output_dir / "extraction.md").write_text(
        "---\ntitle: Extraction\n---\n## Requirements\n- R-001: requirement\n"
    )


def _valid_single_agent_report() -> str:
    """Report with valid frontmatter for single-agent validation."""
    lines = [
        "---",
        "blocking_issues_count: 0",
        "warnings_count: 1",
        "tasklist_ready: true",
        "---",
        "",
        "## Findings",
        "",
        "- **[WARNING]** Decomposition: compound deliverable",
        "  - Location: roadmap.md:D-001",
        "  - Evidence: 'implement and test' joined",
        "  - Fix: split deliverable",
        "",
        "## Summary",
        "",
        "0 blocking, 1 warning, 0 info.",
    ]
    for i in range(10):
        lines.append(f"- Detail line {i}")
    return "\n".join(lines)


def _valid_multi_agent_merged_report() -> str:
    """Merged report with agreement table for multi-agent validation."""
    lines = [
        "---",
        "blocking_issues_count: 0",
        "warnings_count: 2",
        "tasklist_ready: true",
        "validation_mode: adversarial",
        "validation_agents: opus-architect, haiku-architect",
        "---",
        "",
        "## Agreement Table",
        "",
        "| Finding ID | Agent A | Agent B | Agreement Category |",
        "|---|---|---|---|",
        "| F-001 | FOUND | FOUND | BOTH_AGREE |",
        "| F-002 | FOUND | -- | ONLY_A |",
        "",
        "## Consolidated Findings",
        "",
        "- **[WARNING]** Decomposition: compound deliverable (BOTH_AGREE)",
        "  - Location: roadmap.md:D-001",
        "  - Evidence: multiple outputs described",
        "  - Fix: split into separate deliverables",
        "",
        "- **[WARNING]** Interleave: test back-loading (ONLY_A)",
        "  - Location: roadmap.md:M3",
        "  - Evidence: test activities only in final phase",
        "  - Fix: distribute test activities across phases",
        "",
        "## Summary",
        "",
        "0 blocking, 2 warnings, 0 info. Agreement: 1 BOTH_AGREE, 1 ONLY_A.",
    ]
    for i in range(5):
        lines.append(f"- Detail line {i}")
    return "\n".join(lines)


class TestSC001SingleAgentValidation:
    """SC-001: Single-agent validation produces validation-report.md with valid frontmatter."""

    def test_produces_report_file(self, tmp_path, monkeypatch):
        """Single-agent validation creates validate/validation-report.md."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)

        config = ValidateConfig(
            output_dir=output_dir,
            agents=[AgentSpec("opus", "architect")],
            dry_run=True,
        )

        def mock_pipeline(steps, config, run_step, **kwargs):
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)
            (validate_dir / "validation-report.md").write_text(
                _valid_single_agent_report(), encoding="utf-8"
            )
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
            mock_pipeline,
        )

        execute_validate(config)

        report = output_dir / "validate" / "validation-report.md"
        assert report.exists()

    def test_report_has_required_frontmatter(self, tmp_path, monkeypatch):
        """Report frontmatter contains blocking_issues_count, warnings_count, tasklist_ready."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)

        config = ValidateConfig(
            output_dir=output_dir,
            agents=[AgentSpec("opus", "architect")],
            dry_run=True,
        )

        def mock_pipeline(steps, config, run_step, **kwargs):
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)
            (validate_dir / "validation-report.md").write_text(
                _valid_single_agent_report(), encoding="utf-8"
            )
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
            mock_pipeline,
        )

        execute_validate(config)

        content = (output_dir / "validate" / "validation-report.md").read_text()
        assert "blocking_issues_count:" in content
        assert "warnings_count:" in content
        assert "tasklist_ready:" in content

    def test_returns_parsed_counts(self, tmp_path, monkeypatch):
        """execute_validate returns dict with blocking_count, warning_count, info_count."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)

        config = ValidateConfig(
            output_dir=output_dir,
            agents=[AgentSpec("opus", "architect")],
            dry_run=True,
        )

        def mock_pipeline(steps, config, run_step, **kwargs):
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)
            (validate_dir / "validation-report.md").write_text(
                _valid_single_agent_report(), encoding="utf-8"
            )
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
            mock_pipeline,
        )

        result = execute_validate(config)

        assert "blocking_count" in result
        assert "warning_count" in result
        assert "info_count" in result
        assert result["blocking_count"] == 0
        assert result["warning_count"] == 1

    def test_single_agent_builds_one_step(self, tmp_path, monkeypatch):
        """Single-agent mode produces exactly 1 reflect step."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)

        config = ValidateConfig(
            output_dir=output_dir,
            agents=[AgentSpec("opus", "architect")],
            dry_run=True,
        )

        captured_steps = {}

        def mock_pipeline(steps, config, run_step, **kwargs):
            captured_steps["steps"] = steps
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)
            (validate_dir / "validation-report.md").write_text(
                _valid_single_agent_report(), encoding="utf-8"
            )
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
            mock_pipeline,
        )

        execute_validate(config)

        steps = captured_steps["steps"]
        assert len(steps) == 1
        assert steps[0].id == "reflect"


class TestSC003MultiAgentValidation:
    """SC-003: Multi-agent produces per-agent reflection files and merged report."""

    def test_multi_agent_builds_parallel_reflects_and_merge(self, tmp_path, monkeypatch):
        """Multi-agent mode produces parallel reflect steps + sequential merge."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)

        config = ValidateConfig(
            output_dir=output_dir,
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
            dry_run=True,
        )

        captured_steps = {}

        def mock_pipeline(steps, config, run_step, **kwargs):
            captured_steps["steps"] = steps
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)

            # Write per-agent reflection files
            parallel_group = steps[0]
            for s in parallel_group:
                s.output_file.write_text(
                    _valid_single_agent_report(), encoding="utf-8"
                )

            # Write merged report
            (validate_dir / "validation-report.md").write_text(
                _valid_multi_agent_merged_report(), encoding="utf-8"
            )

            results = []
            for s in parallel_group:
                results.append(
                    StepResult(
                        step=s,
                        status=StepStatus.PASS,
                        attempt=1,
                        started_at=_now(),
                        finished_at=_now(),
                    )
                )
            results.append(
                StepResult(
                    step=steps[1],
                    status=StepStatus.PASS,
                    attempt=1,
                    started_at=_now(),
                    finished_at=_now(),
                )
            )
            return results

        monkeypatch.setattr(
            "superclaude.cli.roadmap.validate_executor.execute_pipeline",
            mock_pipeline,
        )

        execute_validate(config)

        steps = captured_steps["steps"]
        # First element is parallel group (list of reflect steps)
        assert isinstance(steps[0], list)
        assert len(steps[0]) == 2
        assert steps[0][0].id == "reflect-opus-architect"
        assert steps[0][1].id == "reflect-haiku-architect"
        # Second element is merge step
        assert steps[1].id == "adversarial-merge"

    def test_per_agent_reflection_files_exist(self, tmp_path, monkeypatch):
        """Per-agent reflection files are created in validate/ directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)

        config = ValidateConfig(
            output_dir=output_dir,
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
            dry_run=True,
        )

        def mock_pipeline(steps, config, run_step, **kwargs):
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)

            parallel_group = steps[0]
            for s in parallel_group:
                s.output_file.write_text(
                    _valid_single_agent_report(), encoding="utf-8"
                )

            (validate_dir / "validation-report.md").write_text(
                _valid_multi_agent_merged_report(), encoding="utf-8"
            )

            results = []
            for s in parallel_group:
                results.append(
                    StepResult(step=s, status=StepStatus.PASS, attempt=1,
                               started_at=_now(), finished_at=_now())
                )
            results.append(
                StepResult(step=steps[1], status=StepStatus.PASS, attempt=1,
                           started_at=_now(), finished_at=_now())
            )
            return results

        monkeypatch.setattr(
            "superclaude.cli.roadmap.validate_executor.execute_pipeline",
            mock_pipeline,
        )

        execute_validate(config)

        assert (output_dir / "validate" / "reflect-opus-architect.md").exists()
        assert (output_dir / "validate" / "reflect-haiku-architect.md").exists()

    def test_merged_report_has_agreement_table(self, tmp_path, monkeypatch):
        """Merged report contains an agreement table."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)

        config = ValidateConfig(
            output_dir=output_dir,
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
            dry_run=True,
        )

        def mock_pipeline(steps, config, run_step, **kwargs):
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)

            for s in steps[0]:
                s.output_file.write_text(
                    _valid_single_agent_report(), encoding="utf-8"
                )

            (validate_dir / "validation-report.md").write_text(
                _valid_multi_agent_merged_report(), encoding="utf-8"
            )

            results = [
                StepResult(step=s, status=StepStatus.PASS, attempt=1,
                           started_at=_now(), finished_at=_now())
                for s in steps[0]
            ]
            results.append(
                StepResult(step=steps[1], status=StepStatus.PASS, attempt=1,
                           started_at=_now(), finished_at=_now())
            )
            return results

        monkeypatch.setattr(
            "superclaude.cli.roadmap.validate_executor.execute_pipeline",
            mock_pipeline,
        )

        execute_validate(config)

        content = (output_dir / "validate" / "validation-report.md").read_text()
        assert "Agreement" in content
        assert "BOTH_AGREE" in content

    def test_merged_report_frontmatter_has_all_fields(self, tmp_path, monkeypatch):
        """Merged report frontmatter includes validation_mode and validation_agents."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _make_pipeline_outputs(output_dir)

        config = ValidateConfig(
            output_dir=output_dir,
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
            dry_run=True,
        )

        def mock_pipeline(steps, config, run_step, **kwargs):
            validate_dir = output_dir / "validate"
            validate_dir.mkdir(parents=True, exist_ok=True)

            for s in steps[0]:
                s.output_file.write_text(
                    _valid_single_agent_report(), encoding="utf-8"
                )

            (validate_dir / "validation-report.md").write_text(
                _valid_multi_agent_merged_report(), encoding="utf-8"
            )

            results = [
                StepResult(step=s, status=StepStatus.PASS, attempt=1,
                           started_at=_now(), finished_at=_now())
                for s in steps[0]
            ]
            results.append(
                StepResult(step=steps[1], status=StepStatus.PASS, attempt=1,
                           started_at=_now(), finished_at=_now())
            )
            return results

        monkeypatch.setattr(
            "superclaude.cli.roadmap.validate_executor.execute_pipeline",
            mock_pipeline,
        )

        execute_validate(config)

        content = (output_dir / "validate" / "validation-report.md").read_text()
        assert "blocking_issues_count:" in content
        assert "warnings_count:" in content
        assert "tasklist_ready:" in content
        assert "validation_mode:" in content
        assert "validation_agents:" in content
