"""Tests for prompts.py depth-to-prompt mapping (T04.06)."""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.roadmap.prompts import (
    _DEPTH_INSTRUCTIONS,
    build_debate_prompt,
)


class TestDepthInstructions:
    def test_quick_maps_to_1_round(self):
        instruction = _DEPTH_INSTRUCTIONS["quick"]
        assert "single" in instruction.lower() or "1" in instruction

    def test_standard_maps_to_2_rounds(self):
        instruction = _DEPTH_INSTRUCTIONS["standard"]
        assert "two" in instruction.lower() or "2" in instruction

    def test_deep_maps_to_3_rounds(self):
        instruction = _DEPTH_INSTRUCTIONS["deep"]
        assert "three" in instruction.lower() or "3" in instruction

    def test_all_depth_values_present(self):
        assert set(_DEPTH_INSTRUCTIONS.keys()) == {"quick", "standard", "deep"}


class TestBuildDebatePrompt:
    def test_quick_depth_includes_round_instruction(self):
        prompt = build_debate_prompt(
            Path("/tmp/diff.md"),
            Path("/tmp/a.md"),
            Path("/tmp/b.md"),
            "quick",
        )
        assert "single" in prompt.lower() or "1" in prompt.lower()
        assert "debate" in prompt.lower()

    def test_standard_depth_includes_2_rounds(self):
        prompt = build_debate_prompt(
            Path("/tmp/diff.md"),
            Path("/tmp/a.md"),
            Path("/tmp/b.md"),
            "standard",
        )
        assert "Round 1" in prompt
        assert "Round 2" in prompt

    def test_deep_depth_includes_3_rounds(self):
        prompt = build_debate_prompt(
            Path("/tmp/diff.md"),
            Path("/tmp/a.md"),
            Path("/tmp/b.md"),
            "deep",
        )
        assert "Round 1" in prompt
        assert "Round 2" in prompt
        assert "Round 3" in prompt

    def test_prompt_includes_frontmatter_instruction(self):
        prompt = build_debate_prompt(
            Path("/tmp/diff.md"),
            Path("/tmp/a.md"),
            Path("/tmp/b.md"),
            "standard",
        )
        assert "convergence_score" in prompt
        assert "rounds_completed" in prompt

    def test_each_depth_produces_different_prompts(self):
        prompts = {
            d: build_debate_prompt(
                Path("/tmp/diff.md"),
                Path("/tmp/a.md"),
                Path("/tmp/b.md"),
                d,
            )
            for d in ("quick", "standard", "deep")
        }
        assert prompts["quick"] != prompts["standard"]
        assert prompts["standard"] != prompts["deep"]
        assert prompts["quick"] != prompts["deep"]
