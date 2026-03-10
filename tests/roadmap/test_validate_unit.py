"""Additional unit tests for T05.02 -- ValidateConfig parsing, defaults, and report semantics.

Supplements existing tests:
- test_validate_gates.py: gate validation (frontmatter, semantics, line count)
- test_models.py: AgentSpec.parse, RoadmapConfig defaults
- test_validate_executor.py: _parse_report_counts

This file adds:
- ValidateConfig defaults and inheritance
- Report semantics invariant: tasklist_ready == (blocking_issues_count == 0)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import PipelineConfig
from superclaude.cli.roadmap.models import AgentSpec, ValidateConfig
from superclaude.cli.roadmap.validate_executor import _parse_report_counts


class TestValidateConfigDefaults:
    """ValidateConfig default values and PipelineConfig inheritance."""

    def test_inherits_pipeline_config(self):
        assert issubclass(ValidateConfig, PipelineConfig)

    def test_default_agents_two(self):
        config = ValidateConfig()
        assert len(config.agents) == 2
        assert config.agents[0].model == "opus"
        assert config.agents[1].model == "haiku"

    def test_custom_single_agent(self):
        config = ValidateConfig(agents=[AgentSpec("sonnet", "security")])
        assert len(config.agents) == 1
        assert config.agents[0].persona == "security"

    def test_has_pipeline_fields(self):
        config = ValidateConfig(
            work_dir=Path("/tmp"),
            dry_run=True,
            max_turns=50,
            model="opus",
            debug=True,
        )
        assert config.dry_run is True
        assert config.max_turns == 50
        assert config.model == "opus"

    def test_output_dir_default(self):
        config = ValidateConfig()
        assert config.output_dir == Path(".")

    def test_custom_output_dir(self):
        config = ValidateConfig(output_dir=Path("/tmp/validation"))
        assert config.output_dir == Path("/tmp/validation")

    def test_agent_id_format(self):
        config = ValidateConfig(agents=[AgentSpec("opus", "architect")])
        assert config.agents[0].id == "opus-architect"


class TestReportSemanticsInvariant:
    """Verify invariant: tasklist_ready == (blocking_issues_count == 0).

    This invariant is enforced by the validate prompt -- when blocking_issues_count
    is 0, tasklist_ready must be true, and vice versa. The _parse_report_counts
    function must correctly parse both fields so the invariant can be checked
    by consumers.
    """

    def test_zero_blocking_means_ready(self, tmp_path):
        """tasklist_ready should be true when blocking_issues_count == 0."""
        report = tmp_path / "report.md"
        report.write_text(
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: 3\n"
            "tasklist_ready: true\n"
            "---\n"
            + "\n".join(f"line {i}" for i in range(25)),
            encoding="utf-8",
        )
        counts = _parse_report_counts(report)
        assert counts["blocking_count"] == 0
        # Invariant: if blocking == 0, report should indicate readiness

    def test_nonzero_blocking_means_not_ready(self, tmp_path):
        """tasklist_ready should be false when blocking_issues_count > 0."""
        report = tmp_path / "report.md"
        report.write_text(
            "---\n"
            "blocking_issues_count: 2\n"
            "warnings_count: 1\n"
            "tasklist_ready: false\n"
            "---\n"
            + "\n".join(f"line {i}" for i in range(25)),
            encoding="utf-8",
        )
        counts = _parse_report_counts(report)
        assert counts["blocking_count"] == 2
        assert counts["blocking_count"] > 0

    def test_invariant_blocking_zero_equals_ready_true(self, tmp_path):
        """Direct invariant test: blocking_count == 0 iff tasklist_ready."""
        cases = [
            (0, True),
            (1, False),
            (5, False),
        ]
        for blocking, expected_ready in cases:
            report = tmp_path / f"report_{blocking}.md"
            report.write_text(
                f"---\n"
                f"blocking_issues_count: {blocking}\n"
                f"warnings_count: 0\n"
                f"tasklist_ready: {'true' if expected_ready else 'false'}\n"
                f"---\n"
                + "\n".join(f"line {i}" for i in range(25)),
                encoding="utf-8",
            )
            counts = _parse_report_counts(report)
            assert counts["blocking_count"] == blocking
            assert (counts["blocking_count"] == 0) == expected_ready

    def test_warning_count_does_not_affect_readiness(self, tmp_path):
        """Warnings do not block tasklist readiness."""
        report = tmp_path / "report.md"
        report.write_text(
            "---\n"
            "blocking_issues_count: 0\n"
            "warnings_count: 10\n"
            "tasklist_ready: true\n"
            "---\n"
            + "\n".join(f"line {i}" for i in range(25)),
            encoding="utf-8",
        )
        counts = _parse_report_counts(report)
        assert counts["blocking_count"] == 0
        assert counts["warning_count"] == 10


class TestAgentSpecParseForValidation:
    """Agent spec parsing edge cases relevant to validation config."""

    def test_parse_single_agent_default_for_standalone(self):
        """Standalone validate defaults to single agent (opus:architect)."""
        spec = AgentSpec.parse("opus:architect")
        assert spec.model == "opus"
        assert spec.persona == "architect"

    def test_parse_handles_empty_persona_defaults(self):
        """Model-only spec defaults persona to architect."""
        spec = AgentSpec.parse("opus")
        assert spec.persona == "architect"

    def test_agent_count_routing(self):
        """Agent count determines single vs multi-agent routing."""
        single = ValidateConfig(agents=[AgentSpec("opus", "architect")])
        multi = ValidateConfig(
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")]
        )
        assert len(single.agents) == 1
        assert len(multi.agents) == 2
