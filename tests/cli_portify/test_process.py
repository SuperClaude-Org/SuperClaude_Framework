"""Tests for PortifyProcess subprocess wrapper.

Covers:
- PortifyProcess extends ClaudeProcess
- Dual --add-dir for work_dir and workflow_path
- Prompt construction with @path references
- ProcessResult captures exit code, stdout, stderr, timeout, duration
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.cli_portify.process import (
    MAX_ADDITIONAL_DIRS,
    PortifyProcess,
    ProcessResult,
    consolidate_dirs,
)
from superclaude.cli.pipeline.process import ClaudeProcess


class TestPortifyProcessInheritance:
    """PortifyProcess extends ClaudeProcess."""

    def test_is_subclass_of_claude_process(self):
        assert issubclass(PortifyProcess, ClaudeProcess)

    def test_instantiation(self, tmp_path):
        proc = PortifyProcess(
            prompt="test prompt",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=tmp_path / "work",
            workflow_path=tmp_path / "workflow",
        )
        assert isinstance(proc, ClaudeProcess)
        assert proc.work_dir == (tmp_path / "work").resolve()
        assert proc.workflow_path == (tmp_path / "workflow").resolve()


class TestDualAddDir:
    """--add-dir is passed for both work directory and workflow path."""

    def test_both_dirs_in_command(self, tmp_path):
        work = tmp_path / "work"
        wf = tmp_path / "workflow"
        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=work,
            workflow_path=wf,
        )
        cmd = proc.build_command()
        # Find all --add-dir occurrences
        add_dir_indices = [i for i, v in enumerate(cmd) if v == "--add-dir"]
        assert len(add_dir_indices) == 2
        # First is work_dir, second is workflow_path
        assert cmd[add_dir_indices[0] + 1] == str(work.resolve())
        assert cmd[add_dir_indices[1] + 1] == str(wf.resolve())

    def test_same_dir_deduplicates(self, tmp_path):
        """When work_dir == workflow_path, only one --add-dir is passed."""
        same = tmp_path / "same"
        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=same,
            workflow_path=same,
        )
        cmd = proc.build_command()
        add_dir_count = cmd.count("--add-dir")
        assert add_dir_count == 1

    def test_extra_args_preserved(self, tmp_path):
        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=tmp_path / "w",
            workflow_path=tmp_path / "wf",
            extra_args=["--custom", "value"],
        )
        cmd = proc.build_command()
        assert "--custom" in cmd
        assert "value" in cmd


class TestPromptConstruction:
    """Prompt construction supports @path references to prior step artifacts."""

    def test_no_refs_passes_prompt_unchanged(self, tmp_path):
        proc = PortifyProcess(
            prompt="do the thing",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=tmp_path,
            workflow_path=tmp_path,
        )
        assert proc.prompt == "do the thing"

    def test_artifact_refs_prepended(self, tmp_path):
        ref1 = tmp_path / "artifacts" / "step1.md"
        ref2 = tmp_path / "artifacts" / "step2.md"
        proc = PortifyProcess(
            prompt="analyze this",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=tmp_path,
            workflow_path=tmp_path,
            artifact_refs=[ref1, ref2],
        )
        assert proc.prompt.startswith(f"@{ref1.resolve()}")
        assert f"@{ref2.resolve()}" in proc.prompt
        assert proc.prompt.endswith("analyze this")

    def test_artifact_refs_list_preserved(self, tmp_path):
        ref1 = tmp_path / "a.md"
        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=tmp_path,
            workflow_path=tmp_path,
            artifact_refs=[ref1],
        )
        refs = proc.artifact_refs
        assert len(refs) == 1
        assert refs[0] == ref1


class TestProcessResult:
    """ProcessResult captures all execution metadata."""

    def test_succeeded_when_exit_zero(self):
        r = ProcessResult(exit_code=0, timed_out=False)
        assert r.succeeded is True

    def test_not_succeeded_on_nonzero_exit(self):
        r = ProcessResult(exit_code=1, timed_out=False)
        assert r.succeeded is False

    def test_not_succeeded_on_timeout(self):
        r = ProcessResult(exit_code=124, timed_out=True)
        assert r.succeeded is False

    def test_default_values(self):
        r = ProcessResult()
        assert r.exit_code == -1
        assert r.stdout_text == ""
        assert r.stderr_text == ""
        assert r.timed_out is False
        assert r.duration_seconds == 0.0
        assert r.output_file is None
        assert r.error_file is None


class TestPortifyProcessRun:
    """run() captures exit code, stdout, stderr, timeout state, and diagnostics."""

    @patch.object(ClaudeProcess, "start")
    @patch.object(ClaudeProcess, "wait", return_value=0)
    def test_run_captures_stdout(self, mock_wait, mock_start, tmp_path):
        out_file = tmp_path / "out.md"
        err_file = tmp_path / "err.log"
        out_file.write_text("output content")
        err_file.write_text("error content")

        proc = PortifyProcess(
            prompt="test",
            output_file=out_file,
            error_file=err_file,
            work_dir=tmp_path,
            workflow_path=tmp_path,
        )
        result = proc.run()

        assert result.exit_code == 0
        assert result.stdout_text == "output content"
        assert result.stderr_text == "error content"
        assert result.timed_out is False
        assert result.duration_seconds >= 0
        assert result.succeeded is True

    @patch.object(ClaudeProcess, "start")
    @patch.object(ClaudeProcess, "wait", return_value=124)
    def test_run_detects_timeout(self, mock_wait, mock_start, tmp_path):
        out_file = tmp_path / "out.md"
        err_file = tmp_path / "err.log"
        out_file.write_text("")
        err_file.write_text("")

        proc = PortifyProcess(
            prompt="test",
            output_file=out_file,
            error_file=err_file,
            work_dir=tmp_path,
            workflow_path=tmp_path,
        )
        result = proc.run()

        assert result.exit_code == 124
        assert result.timed_out is True
        assert result.succeeded is False

    @patch.object(ClaudeProcess, "start")
    @patch.object(ClaudeProcess, "wait", return_value=1)
    def test_run_captures_failure(self, mock_wait, mock_start, tmp_path):
        out_file = tmp_path / "out.md"
        err_file = tmp_path / "err.log"
        out_file.write_text("partial output")
        err_file.write_text("some error")

        proc = PortifyProcess(
            prompt="test",
            output_file=out_file,
            error_file=err_file,
            work_dir=tmp_path,
            workflow_path=tmp_path,
        )
        result = proc.run()

        assert result.exit_code == 1
        assert result.timed_out is False
        assert result.succeeded is False
        assert result.stdout_text == "partial output"
        assert result.stderr_text == "some error"


# --- T02.03: additional_dirs with Directory Cap and Consolidation ---


class TestAdditionalDirs:
    """PortifyProcess accepts additional_dirs and produces --add-dir args."""

    def test_zero_additional_dirs(self, tmp_path):
        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=tmp_path / "work",
            workflow_path=tmp_path / "wf",
            additional_dirs=[],
        )
        cmd = proc.build_command()
        add_dir_count = cmd.count("--add-dir")
        # Only work_dir + workflow_path = 2
        assert add_dir_count == 2

    def test_five_additional_dirs(self, tmp_path):
        extra_dirs = []
        for i in range(5):
            d = tmp_path / f"extra_{i}"
            d.mkdir()
            extra_dirs.append(d)

        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=tmp_path / "work",
            workflow_path=tmp_path / "wf",
            additional_dirs=extra_dirs,
        )
        cmd = proc.build_command()
        add_dir_count = cmd.count("--add-dir")
        # work_dir + workflow_path + 5 additional = 7
        assert add_dir_count == 7

    def test_fifteen_dirs_capped_to_ten(self, tmp_path):
        extra_dirs = []
        for i in range(15):
            d = tmp_path / f"dir_{i:02d}"
            d.mkdir()
            (d / "file.txt").write_text("content")
            extra_dirs.append(d)

        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=tmp_path / "work",
            workflow_path=tmp_path / "wf",
            additional_dirs=extra_dirs,
        )
        cmd = proc.build_command()
        add_dir_count = cmd.count("--add-dir")
        # work_dir + workflow_path + at most 10 additional = 12
        assert add_dir_count <= 12

    def test_additional_dirs_deduplicated_with_base(self, tmp_path):
        work = tmp_path / "work"
        work.mkdir()
        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=work,
            workflow_path=work,
            additional_dirs=[work],
        )
        cmd = proc.build_command()
        # work_dir == workflow_path (1) + work already excluded from additional = 1
        add_dir_count = cmd.count("--add-dir")
        assert add_dir_count == 1

    def test_resolution_log_populated(self, tmp_path):
        extra_dirs = []
        for i in range(15):
            d = tmp_path / f"dir_{i:02d}"
            d.mkdir()
            (d / "file.txt").write_text("content")
            extra_dirs.append(d)

        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=tmp_path / "work",
            workflow_path=tmp_path / "wf",
            additional_dirs=extra_dirs,
        )
        log = proc.resolution_log
        assert "input_count" in log
        assert log["input_count"] == 15


class TestConsolidateDirs:
    """consolidate_dirs() two-tier directory consolidation."""

    def test_under_limit_no_consolidation(self, tmp_path):
        dirs = []
        for i in range(5):
            d = tmp_path / f"d{i}"
            d.mkdir()
            dirs.append(d)
        result = consolidate_dirs(dirs)
        assert len(result["dirs"]) == 5
        assert result["log"]["tier_applied"] == "none"

    def test_over_limit_applies_tier2(self, tmp_path):
        dirs = []
        for i in range(15):
            d = tmp_path / f"d{i:02d}"
            d.mkdir()
            (d / "file.txt").write_text("content")
            dirs.append(d)
        result = consolidate_dirs(dirs)
        assert len(result["dirs"]) <= MAX_ADDITIONAL_DIRS
        assert result["log"]["tier_applied"] in ("tier1", "tier2")

    def test_excludes_specified_dirs(self, tmp_path):
        d1 = tmp_path / "a"
        d1.mkdir()
        d2 = tmp_path / "b"
        d2.mkdir()
        result = consolidate_dirs([d1, d2], exclude={d1})
        dirs_strs = {str(d) for d in result["dirs"]}
        assert str(d1.resolve()) not in dirs_strs

    def test_deduplicates(self, tmp_path):
        d = tmp_path / "dup"
        d.mkdir()
        result = consolidate_dirs([d, d, d])
        assert len(result["dirs"]) == 1

    def test_deterministic_selection(self, tmp_path):
        """With >10 dirs, selection is deterministic (sorted by path)."""
        dirs = []
        for i in range(15):
            d = tmp_path / f"d{i:02d}"
            d.mkdir()
            (d / "file.txt").write_text("content")
            dirs.append(d)
        result1 = consolidate_dirs(dirs)
        result2 = consolidate_dirs(dirs)
        assert result1["dirs"] == result2["dirs"]


# --- T02.04: Backward Compatibility (SC-11) ---


class TestBackwardCompatibilitySC11:
    """SC-11: additional_dirs=None preserves exact v2.24 subprocess command."""

    def test_additional_dirs_none_matches_v224_baseline(self, tmp_path):
        """Subprocess command with additional_dirs=None is identical to v2.24."""
        work = tmp_path / "work"
        wf = tmp_path / "workflow"

        # v2.24 behavior: no additional_dirs parameter
        proc_v224 = PortifyProcess(
            prompt="test prompt",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=work,
            workflow_path=wf,
        )
        cmd_v224 = proc_v224.build_command()

        # v2.24.1 behavior: additional_dirs=None explicitly
        proc_new = PortifyProcess(
            prompt="test prompt",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=work,
            workflow_path=wf,
            additional_dirs=None,
        )
        cmd_new = proc_new.build_command()

        assert cmd_v224 == cmd_new

    def test_no_add_dir_flags_from_none(self, tmp_path):
        """No extra --add-dir flags appear when additional_dirs=None."""
        work = tmp_path / "work"
        wf = tmp_path / "workflow"

        proc = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=work,
            workflow_path=wf,
            additional_dirs=None,
        )
        cmd = proc.build_command()
        add_dir_indices = [i for i, v in enumerate(cmd) if v == "--add-dir"]
        # Only work_dir and workflow_path (2 --add-dir flags)
        assert len(add_dir_indices) == 2
        assert cmd[add_dir_indices[0] + 1] == str(work.resolve())
        assert cmd[add_dir_indices[1] + 1] == str(wf.resolve())

    def test_default_omitted_additional_dirs_matches_none(self, tmp_path):
        """Omitting additional_dirs entirely is equivalent to None."""
        work = tmp_path / "work"
        wf = tmp_path / "workflow"

        proc_omitted = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=work,
            workflow_path=wf,
        )
        proc_none = PortifyProcess(
            prompt="test",
            output_file=tmp_path / "out.md",
            error_file=tmp_path / "err.log",
            work_dir=work,
            workflow_path=wf,
            additional_dirs=None,
        )
        assert proc_omitted.build_command() == proc_none.build_command()
