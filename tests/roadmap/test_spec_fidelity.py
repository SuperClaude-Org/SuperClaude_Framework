"""Tests for Phase 3 -- spec-fidelity prompt, pipeline integration, state persistence, degraded reporting.

Covers:
- T03.01: build_spec_fidelity_prompt() structure validation
- T03.03: spec-fidelity step in pipeline (position, timeout, --no-validate)
- T03.04: fidelity_status state persistence, degraded report generation
- SC-001: blocks HIGH severity
- SC-002: passes clean
- SC-007: degraded non-blocking
- SC-008: state records fidelity
- SC-014: --no-validate keeps fidelity step
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import (
    GateCriteria,
    Step,
    StepResult,
    StepStatus,
)
from superclaude.cli.roadmap.executor import (
    _build_steps,
    _derive_fidelity_status,
    _save_state,
    generate_degraded_report,
    read_state,
)
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig
from superclaude.cli.roadmap.prompts import build_spec_fidelity_prompt


def _now():
    return datetime.now(timezone.utc)


def _make_config(tmp_path: Path) -> RoadmapConfig:
    spec = tmp_path / "spec.md"
    spec.write_text("# Test Spec\nContent for testing.\n")
    output = tmp_path / "output"
    output.mkdir(exist_ok=True)
    return RoadmapConfig(
        spec_file=spec,
        output_dir=output,
        agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
        depth="standard",
    )


class TestBuildSpecFidelityPrompt:
    """T03.01: build_spec_fidelity_prompt() function tests."""

    def test_spec_fidelity_prompt_returns_string(self):
        prompt = build_spec_fidelity_prompt(Path("/tmp/spec.md"), Path("/tmp/roadmap.md"))
        assert isinstance(prompt, str)

    def test_spec_fidelity_prompt_includes_severity_definitions(self):
        """Prompt includes explicit severity definitions (HIGH/MEDIUM/LOW)."""
        prompt = build_spec_fidelity_prompt(Path("/tmp/spec.md"), Path("/tmp/roadmap.md"))
        assert "**HIGH**:" in prompt
        assert "**MEDIUM**:" in prompt
        assert "**LOW**:" in prompt

    def test_spec_fidelity_prompt_requires_quoting_both_docs(self):
        """Prompt requires quoting both spec and roadmap text for each deviation."""
        prompt = build_spec_fidelity_prompt(Path("/tmp/spec.md"), Path("/tmp/roadmap.md"))
        assert "Spec Quote" in prompt
        assert "Roadmap Quote" in prompt
        assert "[MISSING]" in prompt

    def test_spec_fidelity_prompt_specifies_yaml_frontmatter(self):
        """Output format specifies YAML frontmatter with severity_counts and tasklist_ready."""
        prompt = build_spec_fidelity_prompt(Path("/tmp/spec.md"), Path("/tmp/roadmap.md"))
        assert "high_severity_count" in prompt
        assert "medium_severity_count" in prompt
        assert "low_severity_count" in prompt
        assert "total_deviations" in prompt
        assert "validation_complete" in prompt
        assert "tasklist_ready" in prompt

    def test_spec_fidelity_prompt_includes_output_format_block(self):
        """Prompt includes the standard output format block."""
        prompt = build_spec_fidelity_prompt(Path("/tmp/spec.md"), Path("/tmp/roadmap.md"))
        assert "<output_format>" in prompt
        assert "YAML frontmatter" in prompt

    def test_spec_fidelity_prompt_comparison_dimensions(self):
        """Prompt includes all 5 comparison dimensions."""
        prompt = build_spec_fidelity_prompt(Path("/tmp/spec.md"), Path("/tmp/roadmap.md"))
        assert "Signatures" in prompt
        assert "Data Models" in prompt
        assert "Gates" in prompt
        assert "CLI Options" in prompt
        assert "NFRs" in prompt

    def test_spec_fidelity_prompt_deviation_format(self):
        """Prompt specifies the 7-column deviation format."""
        prompt = build_spec_fidelity_prompt(Path("/tmp/spec.md"), Path("/tmp/roadmap.md"))
        assert "DEV-NNN" in prompt
        assert "Impact" in prompt
        assert "Recommended Correction" in prompt


class TestSpecFidelityPipelineIntegration:
    """T03.03: spec-fidelity step integration into pipeline."""

    def test_spec_fidelity_step_after_test_strategy(self, tmp_path):
        """Step is positioned after test-strategy in pipeline execution order."""
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        ids = []
        for entry in steps:
            if isinstance(entry, list):
                ids.extend(s.id for s in entry)
            else:
                ids.append(entry.id)
        test_strategy_idx = ids.index("test-strategy")
        spec_fidelity_idx = ids.index("spec-fidelity")
        assert spec_fidelity_idx == test_strategy_idx + 1

    def test_spec_fidelity_step_timeout_600s(self, tmp_path):
        """Step has timeout=600s."""
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        spec_fidelity = None
        for entry in steps:
            if isinstance(entry, list):
                continue
            if entry.id == "spec-fidelity":
                spec_fidelity = entry
                break
        assert spec_fidelity is not None
        assert spec_fidelity.timeout_seconds == 600

    def test_spec_fidelity_step_retry_limit_1(self, tmp_path):
        """Step has retry_limit=1."""
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        spec_fidelity = next(
            e for e in steps if not isinstance(e, list) and e.id == "spec-fidelity"
        )
        assert spec_fidelity.retry_limit == 1

    def test_spec_fidelity_step_output_path(self, tmp_path):
        """Step output is {output_dir}/spec-fidelity.md."""
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        spec_fidelity = next(
            e for e in steps if not isinstance(e, list) and e.id == "spec-fidelity"
        )
        assert spec_fidelity.output_file == config.output_dir / "spec-fidelity.md"

    def test_spec_fidelity_step_inputs(self, tmp_path):
        """Step inputs include spec_file and merged roadmap."""
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        spec_fidelity = next(
            e for e in steps if not isinstance(e, list) and e.id == "spec-fidelity"
        )
        assert config.spec_file in spec_fidelity.inputs
        assert config.output_dir / "roadmap.md" in spec_fidelity.inputs

    def test_no_validate_does_not_skip_spec_fidelity(self, tmp_path):
        """SC-014: --no-validate flag does NOT skip spec-fidelity step.

        The spec-fidelity step is part of _build_steps(), not the
        post-pipeline validation subsystem. --no-validate only skips
        the validate subsystem invocation.
        """
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        step_ids = []
        for entry in steps:
            if isinstance(entry, list):
                step_ids.extend(s.id for s in entry)
            else:
                step_ids.append(entry.id)
        # spec-fidelity is always in steps regardless of --no-validate
        assert "spec-fidelity" in step_ids

    def test_spec_fidelity_gate_is_strict(self, tmp_path):
        """Spec-fidelity step gate is STRICT enforcement."""
        config = _make_config(tmp_path)
        steps = _build_steps(config)
        spec_fidelity = next(
            e for e in steps if not isinstance(e, list) and e.id == "spec-fidelity"
        )
        assert spec_fidelity.gate is not None
        assert spec_fidelity.gate.enforcement_tier == "STRICT"


class TestDeriveFidelityStatus:
    """T03.04: fidelity_status derivation."""

    def test_pass_status(self, tmp_path):
        out = tmp_path / "spec-fidelity.md"
        out.write_text(
            "---\nhigh_severity_count: 0\nvalidation_complete: true\n---\n"
            "## Clean\n"
        )
        step = Step(
            id="spec-fidelity", prompt="p", output_file=out,
            gate=None, timeout_seconds=600,
        )
        result = StepResult(step=step, status=StepStatus.PASS)
        assert _derive_fidelity_status(result) == "pass"

    def test_degraded_status(self, tmp_path):
        out = tmp_path / "spec-fidelity.md"
        out.write_text(
            "---\nhigh_severity_count: 0\nvalidation_complete: false\n---\n"
            "## Degraded\n"
        )
        step = Step(
            id="spec-fidelity", prompt="p", output_file=out,
            gate=None, timeout_seconds=600,
        )
        result = StepResult(step=step, status=StepStatus.PASS)
        assert _derive_fidelity_status(result) == "degraded"

    def test_fail_status(self):
        step = Step(
            id="spec-fidelity", prompt="p", output_file=Path("/tmp/x.md"),
            gate=None, timeout_seconds=600,
        )
        result = StepResult(step=step, status=StepStatus.FAIL)
        assert _derive_fidelity_status(result) == "fail"

    def test_timeout_status(self):
        step = Step(
            id="spec-fidelity", prompt="p", output_file=Path("/tmp/x.md"),
            gate=None, timeout_seconds=600,
        )
        result = StepResult(step=step, status=StepStatus.TIMEOUT)
        assert _derive_fidelity_status(result) == "fail"

    def test_skipped_status(self):
        step = Step(
            id="spec-fidelity", prompt="p", output_file=Path("/tmp/x.md"),
            gate=None, timeout_seconds=600,
        )
        result = StepResult(step=step, status=StepStatus.SKIPPED)
        assert _derive_fidelity_status(result) == "skipped"


class TestStatePersistence:
    """T03.04 / SC-008: fidelity_status persisted in .roadmap-state.json."""

    def test_state_includes_fidelity_status_pass(self, tmp_path):
        """SC-008: state records fidelity_status when spec-fidelity passes."""
        config = _make_config(tmp_path)
        out = config.output_dir / "spec-fidelity.md"
        out.write_text(
            "---\nhigh_severity_count: 0\nvalidation_complete: true\n---\n"
            "## Clean\n"
        )
        step = Step(
            id="spec-fidelity", prompt="p", output_file=out,
            gate=None, timeout_seconds=600,
        )
        results = [
            StepResult(step=step, status=StepStatus.PASS, started_at=_now(), finished_at=_now()),
        ]
        _save_state(config, results)

        state = read_state(config.output_dir / ".roadmap-state.json")
        assert state is not None
        assert state["fidelity_status"] == "pass"

    def test_state_includes_fidelity_status_fail(self, tmp_path):
        config = _make_config(tmp_path)
        step = Step(
            id="spec-fidelity", prompt="p", output_file=config.output_dir / "spec-fidelity.md",
            gate=None, timeout_seconds=600,
        )
        results = [
            StepResult(step=step, status=StepStatus.FAIL, started_at=_now(), finished_at=_now()),
        ]
        _save_state(config, results)

        state = read_state(config.output_dir / ".roadmap-state.json")
        assert state is not None
        assert state["fidelity_status"] == "fail"

    def test_state_fidelity_valid_enum(self, tmp_path):
        """fidelity_status has valid enum values."""
        config = _make_config(tmp_path)
        for status_val, expected in [
            (StepStatus.PASS, "pass"),
            (StepStatus.FAIL, "fail"),
            (StepStatus.SKIPPED, "skipped"),
        ]:
            out = config.output_dir / "spec-fidelity.md"
            if status_val == StepStatus.PASS:
                out.write_text(
                    "---\nhigh_severity_count: 0\nvalidation_complete: true\n---\nClean\n"
                )
            step = Step(
                id="spec-fidelity", prompt="p", output_file=out,
                gate=None, timeout_seconds=600,
            )
            results = [
                StepResult(step=step, status=status_val, started_at=_now(), finished_at=_now()),
            ]
            _save_state(config, results)
            state = read_state(config.output_dir / ".roadmap-state.json")
            assert state["fidelity_status"] == expected


class TestGenerateDegradedReport:
    """T03.04: degraded report generation (NFR-007)."""

    def test_degraded_report_created(self, tmp_path):
        out = tmp_path / "spec-fidelity.md"
        generate_degraded_report(out, "claude-agent", "API timeout")
        assert out.exists()

    def test_degraded_report_validation_complete_false(self, tmp_path):
        out = tmp_path / "spec-fidelity.md"
        generate_degraded_report(out, "claude-agent", "API timeout")
        content = out.read_text(encoding="utf-8")
        assert "validation_complete: false" in content

    def test_degraded_report_fidelity_check_attempted(self, tmp_path):
        out = tmp_path / "spec-fidelity.md"
        generate_degraded_report(out, "claude-agent", "API timeout")
        content = out.read_text(encoding="utf-8")
        assert "fidelity_check_attempted: true" in content

    def test_degraded_report_names_failed_agent(self, tmp_path):
        out = tmp_path / "spec-fidelity.md"
        generate_degraded_report(out, "claude-agent", "API timeout")
        content = out.read_text(encoding="utf-8")
        assert "claude-agent" in content

    def test_degraded_report_names_failure_reason(self, tmp_path):
        out = tmp_path / "spec-fidelity.md"
        generate_degraded_report(out, "claude-agent", "API timeout")
        content = out.read_text(encoding="utf-8")
        assert "API timeout" in content

    def test_degraded_report_distinguishable_from_clean_pass(self, tmp_path):
        """NFR-007: Degraded reports are distinguishable from clean passes."""
        out_degraded = tmp_path / "degraded.md"
        generate_degraded_report(out_degraded, "agent", "timeout")
        degraded = out_degraded.read_text(encoding="utf-8")

        clean_pass = (
            "---\n"
            "high_severity_count: 0\n"
            "medium_severity_count: 0\n"
            "low_severity_count: 0\n"
            "total_deviations: 0\n"
            "validation_complete: true\n"
            "tasklist_ready: true\n"
            "---\n"
            "## Deviation Report\n"
            "No deviations found.\n"
        )

        # Key distinguishing features:
        assert "validation_complete: false" in degraded
        assert "validation_complete: true" in clean_pass
        assert "Degraded" in degraded
        assert "Degraded" not in clean_pass
        assert "fidelity_check_attempted: true" in degraded
        assert "fidelity_check_attempted" not in clean_pass

    def test_degraded_report_tasklist_ready_false(self, tmp_path):
        out = tmp_path / "spec-fidelity.md"
        generate_degraded_report(out, "agent", "error")
        content = out.read_text(encoding="utf-8")
        assert "tasklist_ready: false" in content

    def test_degraded_report_has_yaml_frontmatter(self, tmp_path):
        out = tmp_path / "spec-fidelity.md"
        generate_degraded_report(out, "agent", "error")
        content = out.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert "\n---\n" in content[4:]
