"""Integration tests for roadmap file-passing via inline embedding.

Three scenarios per T03.03:
1. Prompt contains embedded content (fenced code blocks with file content)
2. Paths with spaces handled correctly
3. _EMBED_SIZE_LIMIT guard: oversized prompts embed inline with warning (--file fallback removed)
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


class TestEmbedSizeGuardFallback:
    """Scenario 3: _EMBED_SIZE_LIMIT (120 KB) guard — oversized prompts embed inline, no --file."""

    def test_embed_size_guard_fallback(self, tmp_path: Path, caplog):
        """Verify that composed prompt exceeding _EMBED_SIZE_LIMIT still embeds inline.

        --file fallback is removed because --file is broken (cloud download mechanism).
        Content must appear in the prompt; extra_args must be empty.
        """
        large_file = tmp_path / "large.md"
        # Write content exceeding _EMBED_SIZE_LIMIT
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
        # Prompt MUST contain the large content (always embedded inline now)
        assert "x" * 100 in captured_prompt["value"]
        # extra_args must be empty -- --file fallback is gone
        assert captured_prompt["extra_args"] == []
        # Warning should be logged about oversize (but still embedded inline)
        assert any("embedding inline anyway" in r.message for r in caplog.records)


def _capture_and_return(kwargs: dict, store: dict, instance: MagicMock) -> MagicMock:
    """Helper: capture ClaudeProcess kwargs and return the mock instance."""
    store["value"] = kwargs.get("prompt", "")
    store["extra_args"] = kwargs.get("extra_args", [])
    return instance


class TestComposedStringGuard:
    """Guard measures the composed string (prompt + embedded), not just the embedded file."""

    def test_prompt_plus_embedded_exceeds_limit(self, tmp_path: Path, caplog):
        """File at 90% of _EMBED_SIZE_LIMIT plus a large prompt exceeds composed limit.

        Verifies that when prompt + "\\n\\n" + embedded > _EMBED_SIZE_LIMIT, a warning
        is logged but content is still embedded inline (--file fallback is gone).
        """
        # File at 90% of _EMBED_SIZE_LIMIT: alone it would pass the guard
        file_size = int(_EMBED_SIZE_LIMIT * 0.9)
        input_file = tmp_path / "spec.md"
        input_file.write_text("y" * file_size)

        # Prompt large enough to push the composed string over the limit.
        remaining = _EMBED_SIZE_LIMIT - file_size  # gap before limit is hit by file alone
        large_prompt = "P" * (remaining + 1024)  # overshoot by 1 KB

        step = Step(
            id="composed-guard-test",
            prompt=large_prompt,
            output_file=tmp_path / "output.md",
            gate=None,
            timeout_seconds=60,
            inputs=[input_file],
        )
        config = PipelineConfig(max_turns=5, dry_run=False)

        captured_prompt: dict = {}

        with patch("superclaude.cli.roadmap.executor.ClaudeProcess") as MockProc:
            instance = MagicMock()
            instance._process = None
            MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured_prompt, instance)
            instance.wait.return_value = 0

            with caplog.at_level(logging.WARNING, logger="superclaude.roadmap.executor"):
                result = roadmap_run_step(step, config, cancel_check=lambda: False)

        assert result.status == StepStatus.PASS
        # File content MUST be present inline (always embedded, --file fallback gone)
        assert "y" * 100 in captured_prompt["value"]
        # extra_args must be empty
        assert captured_prompt["extra_args"] == []
        # Warning must be logged about oversize
        assert any("embedding inline anyway" in r.message for r in caplog.records)


class TestExactLimitBoundary:
    """Boundary semantics: composed length exactly equal to _EMBED_SIZE_LIMIT embeds inline."""

    def test_exact_limit_embeds_inline(self, tmp_path: Path):
        """Composed string of exactly _EMBED_SIZE_LIMIT bytes must embed inline (no fallback).

        Validates that the guard uses <= (at-limit input is accepted).
        """
        # We control the file content so that the full composed string is exactly
        # _EMBED_SIZE_LIMIT bytes.  The composed string is:
        #   prompt + "\n\n" + "# <path>\n```\n" + content + "\n```"
        step_prompt = "Run this analysis."
        input_file = tmp_path / "exact.md"

        # Build a dummy embedded block to calculate overhead precisely
        placeholder_content = ""
        header = f"# {input_file}\n```\n{placeholder_content}\n```"
        separator = "\n\n"
        overhead = len((step_prompt + separator + header).encode("utf-8"))
        fill_size = _EMBED_SIZE_LIMIT - overhead
        assert fill_size > 0, "Overhead already exceeds limit; adjust test constants"

        input_file.write_text("z" * fill_size)

        step = Step(
            id="exact-limit-test",
            prompt=step_prompt,
            output_file=tmp_path / "output.md",
            gate=None,
            timeout_seconds=60,
            inputs=[input_file],
        )
        config = PipelineConfig(max_turns=5, dry_run=False)

        captured_prompt: dict = {}

        with patch("superclaude.cli.roadmap.executor.ClaudeProcess") as MockProc:
            instance = MagicMock()
            instance._process = None
            MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured_prompt, instance)
            instance.wait.return_value = 0

            result = roadmap_run_step(step, config, cancel_check=lambda: False)

        assert result.status == StepStatus.PASS
        # Content must be present inline (no fallback)
        assert "z" * 100 in captured_prompt["value"]
        assert captured_prompt["extra_args"] == []  # No --file flags

    def test_one_over_limit_triggers_warning_and_embeds_inline(self, tmp_path: Path, caplog):
        """Composed string of _EMBED_SIZE_LIMIT + 1 bytes logs a warning but embeds inline.

        Validates the over-limit case: --file fallback is gone; content still delivered inline.
        """
        step_prompt = "Run this analysis."
        input_file = tmp_path / "over.md"

        placeholder_content = ""
        header = f"# {input_file}\n```\n{placeholder_content}\n```"
        separator = "\n\n"
        overhead = len((step_prompt + separator + header).encode("utf-8"))
        fill_size = _EMBED_SIZE_LIMIT - overhead + 1  # one byte over

        input_file.write_text("w" * fill_size)

        step = Step(
            id="over-limit-test",
            prompt=step_prompt,
            output_file=tmp_path / "output.md",
            gate=None,
            timeout_seconds=60,
            inputs=[input_file],
        )
        config = PipelineConfig(max_turns=5, dry_run=False)

        captured_prompt: dict = {}

        with patch("superclaude.cli.roadmap.executor.ClaudeProcess") as MockProc:
            instance = MagicMock()
            instance._process = None
            MockProc.side_effect = lambda **kw: _capture_and_return(kw, captured_prompt, instance)
            instance.wait.return_value = 0

            with caplog.at_level(logging.WARNING, logger="superclaude.roadmap.executor"):
                result = roadmap_run_step(step, config, cancel_check=lambda: False)

        assert result.status == StepStatus.PASS
        # Content MUST be present inline (always embedded now)
        assert "w" * 100 in captured_prompt["value"]
        # --file must NOT be in extra_args
        assert "--file" not in captured_prompt["extra_args"]
        assert captured_prompt["extra_args"] == []
        # Warning must be logged
        assert any("embedding inline anyway" in r.message for r in caplog.records)
