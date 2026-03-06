"""Tests for pipeline/models.py -- dataclass instantiation, defaults, types."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import (
    GateCriteria,
    PipelineConfig,
    SemanticCheck,
    Step,
    StepResult,
    StepStatus,
)


class TestStepStatus:
    def test_values(self):
        assert StepStatus.PENDING.value == "PENDING"
        assert StepStatus.PASS.value == "PASS"
        assert StepStatus.FAIL.value == "FAIL"
        assert StepStatus.TIMEOUT.value == "TIMEOUT"
        assert StepStatus.CANCELLED.value == "CANCELLED"
        assert StepStatus.SKIPPED.value == "SKIPPED"

    def test_is_terminal(self):
        assert StepStatus.PASS.is_terminal
        assert StepStatus.FAIL.is_terminal
        assert StepStatus.TIMEOUT.is_terminal
        assert StepStatus.CANCELLED.is_terminal
        assert StepStatus.SKIPPED.is_terminal
        assert not StepStatus.PENDING.is_terminal

    def test_is_success(self):
        assert StepStatus.PASS.is_success
        assert not StepStatus.FAIL.is_success
        assert not StepStatus.PENDING.is_success

    def test_is_failure(self):
        assert StepStatus.FAIL.is_failure
        assert StepStatus.TIMEOUT.is_failure
        assert not StepStatus.PASS.is_failure
        assert not StepStatus.CANCELLED.is_failure


class TestPipelineConfig:
    def test_defaults(self, tmp_path):
        cfg = PipelineConfig(work_dir=tmp_path)
        assert cfg.dry_run is False
        assert cfg.max_turns == 50
        assert cfg.model == ""
        assert cfg.permission_flag == "--dangerously-skip-permissions"
        assert cfg.debug is False

    def test_custom_values(self, tmp_path):
        cfg = PipelineConfig(
            work_dir=tmp_path,
            dry_run=True,
            max_turns=100,
            model="opus",
            debug=True,
        )
        assert cfg.dry_run is True
        assert cfg.max_turns == 100
        assert cfg.model == "opus"


class TestGateCriteria:
    def test_defaults(self):
        gc = GateCriteria(required_frontmatter_fields=["title"], min_lines=10)
        assert gc.enforcement_tier == "STANDARD"
        assert gc.semantic_checks is None

    def test_all_tiers(self):
        for tier in ("EXEMPT", "LIGHT", "STANDARD", "STRICT"):
            gc = GateCriteria(
                required_frontmatter_fields=[], min_lines=0, enforcement_tier=tier
            )
            assert gc.enforcement_tier == tier

    def test_with_semantic_checks(self):
        sc = SemanticCheck(name="test", check_fn=lambda c: True, failure_message="fail")
        gc = GateCriteria(
            required_frontmatter_fields=[],
            min_lines=0,
            enforcement_tier="STRICT",
            semantic_checks=[sc],
        )
        assert len(gc.semantic_checks) == 1
        assert gc.semantic_checks[0].name == "test"


class TestSemanticCheck:
    def test_creation(self):
        sc = SemanticCheck(
            name="has_heading",
            check_fn=lambda c: "# " in c,
            failure_message="No heading found",
        )
        assert sc.name == "has_heading"
        assert sc.check_fn("# Hello")
        assert not sc.check_fn("no heading")


class TestStep:
    def test_with_gate(self, tmp_path):
        gc = GateCriteria(required_frontmatter_fields=["a"], min_lines=5)
        s = Step(
            id="extract",
            prompt="do the thing",
            output_file=tmp_path / "out.md",
            gate=gc,
            timeout_seconds=300,
        )
        assert s.id == "extract"
        assert s.retry_limit == 1
        assert s.model == ""
        assert s.inputs == []
        assert s.gate is gc

    def test_without_gate(self, tmp_path):
        s = Step(
            id="sprint-phase",
            prompt="p",
            output_file=tmp_path / "o",
            gate=None,
            timeout_seconds=60,
        )
        assert s.gate is None

    def test_model_override(self, tmp_path):
        s = Step(
            id="gen",
            prompt="p",
            output_file=tmp_path / "o",
            gate=None,
            timeout_seconds=60,
            model="sonnet",
        )
        assert s.model == "sonnet"


class TestStepResult:
    def test_duration(self):
        t1 = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 1, 1, 0, 1, 30, tzinfo=timezone.utc)
        step = Step(id="s", prompt="p", output_file=Path("/tmp/o"), gate=None, timeout_seconds=60)
        sr = StepResult(step=step, status=StepStatus.PASS, attempt=1, gate_failure_reason=None, started_at=t1, finished_at=t2)
        assert sr.duration_seconds == 90.0

    def test_gate_failure_reason(self):
        step = Step(id="s", prompt="p", output_file=Path("/tmp/o"), gate=None, timeout_seconds=60)
        now = datetime.now(timezone.utc)
        sr = StepResult(step=step, status=StepStatus.FAIL, attempt=2, gate_failure_reason="Missing field 'title'", started_at=now, finished_at=now)
        assert sr.gate_failure_reason == "Missing field 'title'"
        assert sr.attempt == 2
