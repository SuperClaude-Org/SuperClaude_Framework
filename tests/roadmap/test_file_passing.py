"""Integration tests for roadmap file-passing via inline embedding.

Three scenarios per T03.03:
1. Prompt contains embedded content (fenced code blocks with file content)
2. Paths with spaces handled correctly
3. 100KB guard triggers fallback to --file flags
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.pipeline.models import PipelineConfig, Step, StepResult, StepStatus
from superclaude.cli.roadmap.executor import (
    _EMBED_SIZE_LIMIT,
    _embed_inputs,
    roadmap_run_step,
)


def _now():
    return datetime.now(timezone.utc)


def _make_step(tmp_path: Path, inputs: list[Path], step_id: str = "test-step") -> Step:
    return Step(
        id=step_id,
        prompt="Run this analysis.",
        output_file=tmp_path / "output.md",
        gate=None,
        timeout_seconds=60,
        inputs=inputs,
    )


class TestPromptContainsEmbeddedContent:
    """Scenario 1: Prompt includes fenced code blocks with file content."""

    def test_prompt_contains_embedded_content(self, tmp_path: Path):
        """Verify that when inputs are small, their contents appear inline in the prompt."""
        input_file = tmp_path / "spec.md"
        input_file.write_text("# Specification\nKey requirement here.\n")

        step = _make_step(tmp_path, inputs=[input_file])
        config = PipelineConfig(max_turns=5, dry_run=False)

        captured_prompt = {}

        def fake_init(self_, **kwargs):
            captured_prompt["value"] = kwargs.get("prompt", "")
            captured_prompt["extra_args"] = kwargs.get("extra_args", [])
            self_._process = None

        with patch("superclaude.cli.roadmap.executor.ClaudeProcess") as MockProc:
            instance = MagicMock()
            instance._process = None
            MockProc.return_value = instance
            MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured_prompt, instance)
            instance.wait.return_value = 0

            result = roadmap_run_step(step, config, cancel_check=lambda: False)

        assert result.status == StepStatus.PASS
        assert "# Specification" in captured_prompt["value"]
        assert "Key requirement here." in captured_prompt["value"]
        assert "```" in captured_prompt["value"]
        assert captured_prompt["extra_args"] == []  # No --file flags


class TestPathsWithSpaces:
    """Scenario 2: Paths containing spaces are embedded correctly."""

    def test_paths_with_spaces(self, tmp_path: Path):
        """Verify paths with spaces are handled in inline embedding."""
        spaced_dir = tmp_path / "my project"
        spaced_dir.mkdir()
        input_file = spaced_dir / "my spec.md"
        input_file.write_text("Content from spaced path.\n")

        step = _make_step(tmp_path, inputs=[input_file])
        config = PipelineConfig(max_turns=5, dry_run=False)

        captured_prompt = {}

        with patch("superclaude.cli.roadmap.executor.ClaudeProcess") as MockProc:
            instance = MagicMock()
            instance._process = None
            MockProc.return_value = instance
            MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured_prompt, instance)
            instance.wait.return_value = 0

            result = roadmap_run_step(step, config, cancel_check=lambda: False)

        assert result.status == StepStatus.PASS
        assert "Content from spaced path." in captured_prompt["value"]
        assert str(input_file) in captured_prompt["value"]
        assert captured_prompt["extra_args"] == []


class TestSizeGuardFallback:
    """Scenario 3: 100KB guard triggers fallback to --file flags."""

    def test_100kb_guard_fallback(self, tmp_path: Path, caplog):
        """Verify that inputs exceeding 100KB fall back to --file flags."""
        large_file = tmp_path / "large.md"
        # Write content exceeding 100KB
        large_file.write_text("x" * (_EMBED_SIZE_LIMIT + 1024))

        step = _make_step(tmp_path, inputs=[large_file])
        config = PipelineConfig(max_turns=5, dry_run=False)

        captured_prompt = {}

        with patch("superclaude.cli.roadmap.executor.ClaudeProcess") as MockProc:
            instance = MagicMock()
            instance._process = None
            MockProc.return_value = instance
            MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured_prompt, instance)
            instance.wait.return_value = 0

            with caplog.at_level(logging.WARNING, logger="superclaude.roadmap.executor"):
                result = roadmap_run_step(step, config, cancel_check=lambda: False)

        assert result.status == StepStatus.PASS
        # Prompt should NOT contain the large content
        assert "x" * 100 not in captured_prompt["value"]
        # extra_args should contain --file flags
        assert "--file" in captured_prompt["extra_args"]
        assert str(large_file) in captured_prompt["extra_args"]
        # Warning should be logged
        assert any("falling back to --file" in r.message for r in caplog.records)


def _capture_and_return(kwargs: dict, store: dict, instance: MagicMock) -> MagicMock:
    """Helper: capture ClaudeProcess kwargs and return the mock instance."""
    store["value"] = kwargs.get("prompt", "")
    store["extra_args"] = kwargs.get("extra_args", [])
    return instance
