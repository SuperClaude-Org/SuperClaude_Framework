"""Tests for _embed_inputs() helper in roadmap/executor.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.roadmap.executor import _embed_inputs


class TestEmbedInputs:
    """T03.01: Verify _embed_inputs() produces correct fenced blocks."""

    def test_empty_list_returns_empty_string(self):
        assert _embed_inputs([]) == ""

    def test_single_file_produces_fenced_block(self, tmp_path: Path):
        f = tmp_path / "input.md"
        f.write_text("hello world\n")
        result = _embed_inputs([f])
        assert f"# {f}" in result
        assert "```" in result
        assert "hello world" in result

    def test_multiple_files_produce_multiple_blocks(self, tmp_path: Path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("content A\n")
        f2.write_text("content B\n")
        result = _embed_inputs([f1, f2])
        assert f"# {f1}" in result
        assert f"# {f2}" in result
        assert "content A" in result
        assert "content B" in result
        # Two separate fenced blocks
        assert result.count("```") == 4  # open + close for each file

    def test_path_header_format(self, tmp_path: Path):
        f = tmp_path / "sub dir" / "file.md"
        f.parent.mkdir(parents=True)
        f.write_text("data\n")
        result = _embed_inputs([f])
        # Header line starts with "# " followed by path
        lines = result.splitlines()
        assert lines[0] == f"# {f}"
