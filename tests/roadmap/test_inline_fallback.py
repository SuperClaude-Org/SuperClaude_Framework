"""Conditional tests for inline embedding fallback across non-inheriting executors.

FR-ATL.5 (Phase 1.5): When --file is BROKEN, all three non-inheriting executors
must route oversized inputs via inline embedding, never via --file flags.

Parameterized over:
- validate_executor (validate_run_step, _EMBED_SIZE_LIMIT = 100 KB)
- tasklist/executor (tasklist_run_step, _EMBED_SIZE_LIMIT = 100 KB)
- remediate_executor (_run_agent_for_file, _EMBED_SIZE_LIMIT = 120 KB)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.pipeline.models import PipelineConfig, Step, StepStatus
from superclaude.cli.roadmap.models import Finding


# ── Helpers ───────────────────────────────────────────────────────────────────


def _now():
    return datetime.now(timezone.utc)


def _make_step(tmp_path: Path, inputs: list[Path]) -> Step:
    return Step(
        id="inline-fallback-test",
        prompt="Validate this content.",
        output_file=tmp_path / "output.md",
        gate=None,
        timeout_seconds=60,
        inputs=inputs,
    )


def _make_finding(target_file: str) -> Finding:
    return Finding(
        id="F-01",
        severity="BLOCKING",
        dimension="spec-fidelity",
        description="Test finding",
        location=f"{target_file}:1",
        evidence="Evidence text",
        fix_guidance="Apply fix",
        files_affected=[target_file],
        status="PENDING",
    )


def _capture_and_return(kwargs: dict, store: dict, instance: MagicMock) -> MagicMock:
    store["prompt"] = kwargs.get("prompt", "")
    store["extra_args"] = kwargs.get("extra_args", [])
    return instance


# ── Parameterized test ────────────────────────────────────────────────────────


EXECUTOR_PARAMS = [
    pytest.param(
        "validate_executor",
        "superclaude.cli.roadmap.validate_executor",
        id="validate_executor",
    ),
    pytest.param(
        "tasklist_executor",
        "superclaude.cli.tasklist.executor",
        id="tasklist_executor",
    ),
    pytest.param(
        "remediate_executor",
        "superclaude.cli.roadmap.remediate_executor",
        id="remediate_executor",
    ),
]


class TestInlineEmbedFallbackWhenFileBroken:
    """FR-ATL.5: all three conditional executors route oversized inputs via inline embedding.

    Parameterized over each executor's _EMBED_SIZE_LIMIT value.
    --file must never appear in extra_args; content must always be in the prompt.
    """

    @pytest.mark.parametrize("executor_name,module_path", EXECUTOR_PARAMS)
    def test_inline_embed_fallback_when_file_broken(
        self,
        tmp_path: Path,
        caplog,
        executor_name: str,
        module_path: str,
    ):
        """Oversized input is embedded inline; --file is not used."""
        import importlib

        module = importlib.import_module(module_path)
        embed_limit = module._EMBED_SIZE_LIMIT
        config = PipelineConfig(max_turns=5, dry_run=False)
        captured: dict = {}

        if executor_name == "remediate_executor":
            # remediate_executor uses _run_agent_for_file, not a step-based function
            target = tmp_path / "roadmap.md"
            target.write_text("R" * (embed_limit + 2048))
            finding = _make_finding(str(target))

            with patch(f"{module_path}.ClaudeProcess") as MockProc:
                instance = MagicMock()
                instance._process = None
                instance.wait.return_value = 0
                MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured, instance)

                with caplog.at_level(logging.WARNING, logger=module_path.replace("/", ".")):
                    module._run_agent_for_file(str(target), [finding], config, tmp_path)

            # Content must be embedded inline (not absent due to --file fallback)
            assert "R" * 100 in captured["prompt"], (
                f"{executor_name}: oversized content missing from prompt"
            )
            assert "--file" not in captured["extra_args"], (
                f"{executor_name}: --file found in extra_args (should be absent)"
            )

        else:
            # validate_executor and tasklist_executor use step-based run functions
            input_file = tmp_path / "spec.md"
            input_file.write_text("S" * (embed_limit + 2048))
            step = _make_step(tmp_path, inputs=[input_file])

            if executor_name == "validate_executor":
                run_fn = module.validate_run_step
                cancel_check = lambda: False
            else:
                run_fn = module.tasklist_run_step
                cancel_check = lambda: False

            with patch(f"{module_path}.ClaudeProcess") as MockProc:
                instance = MagicMock()
                instance._process = None
                instance.wait.return_value = 0
                MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured, instance)

                with caplog.at_level(logging.WARNING):
                    result = run_fn(step, config, cancel_check=cancel_check)

            assert result.status == StepStatus.PASS, (
                f"{executor_name}: step did not PASS"
            )
            # Content must be embedded inline
            assert "S" * 100 in captured["prompt"], (
                f"{executor_name}: oversized content missing from prompt"
            )
            assert "--file" not in captured["extra_args"], (
                f"{executor_name}: --file found in extra_args (should be absent)"
            )

    @pytest.mark.parametrize("executor_name,module_path", EXECUTOR_PARAMS)
    def test_no_file_flag_in_any_execution_path(
        self,
        tmp_path: Path,
        executor_name: str,
        module_path: str,
    ):
        """Normal (under-limit) execution also produces no --file in extra_args."""
        import importlib

        module = importlib.import_module(module_path)
        config = PipelineConfig(max_turns=5, dry_run=False)
        captured: dict = {}

        if executor_name == "remediate_executor":
            target = tmp_path / "roadmap.md"
            target.write_text("Small content for remediation.\n")
            finding = _make_finding(str(target))

            with patch(f"{module_path}.ClaudeProcess") as MockProc:
                instance = MagicMock()
                instance._process = None
                instance.wait.return_value = 0
                MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured, instance)

                module._run_agent_for_file(str(target), [finding], config, tmp_path)

            assert "--file" not in captured["extra_args"]
            assert "Small content for remediation." in captured["prompt"]

        else:
            input_file = tmp_path / "spec.md"
            input_file.write_text("Small content.\n")
            step = _make_step(tmp_path, inputs=[input_file])

            if executor_name == "validate_executor":
                run_fn = module.validate_run_step
            else:
                run_fn = module.tasklist_run_step

            with patch(f"{module_path}.ClaudeProcess") as MockProc:
                instance = MagicMock()
                instance._process = None
                instance.wait.return_value = 0
                MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured, instance)

                result = run_fn(step, config, cancel_check=lambda: False)

            assert result.status == StepStatus.PASS
            assert "--file" not in captured["extra_args"]
            assert "Small content." in captured["prompt"]
