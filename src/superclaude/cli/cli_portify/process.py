"""Subprocess orchestration for cli-portify Claude-assisted steps.

PortifyProcess extends pipeline.ClaudeProcess with:
- Dual --add-dir scoping (work directory + workflow path)
- Prompt construction with @path references to prior artifacts
- Exit code, stdout, stderr, timeout state, and diagnostics capture

Per D-0017: All Claude-assisted steps (3-7) depend on this wrapper.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from superclaude.cli.pipeline.process import ClaudeProcess

_log = logging.getLogger("superclaude.cli_portify.process")

# Maximum number of --add-dir arguments beyond work_dir/workflow_path
MAX_ADDITIONAL_DIRS = 10


@dataclass
class ProcessResult:
    """Captured result from a PortifyProcess execution."""

    exit_code: int = -1
    stdout_text: str = ""
    stderr_text: str = ""
    timed_out: bool = False
    duration_seconds: float = 0.0
    output_file: Path | None = None
    error_file: Path | None = None

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


def consolidate_dirs(
    dirs: list[Path],
    exclude: set[Path] | None = None,
) -> dict[str, object]:
    """Consolidate directories with two-tier algorithm, capped at MAX_ADDITIONAL_DIRS.

    Tier 1: Merge directories sharing common ancestors via os.path.commonpath(),
    only when the common parent contains no more than 3x the total file count
    of the constituent directories.

    Tier 2: If still >MAX_ADDITIONAL_DIRS after Tier 1, select top N by
    constituent count (deterministic sort by path).

    Args:
        dirs: Input directories to consolidate.
        exclude: Directories to exclude (already added as base dirs).

    Returns:
        Dict with 'dirs' (consolidated list) and 'log' (consolidation decisions).
    """
    log: dict[str, object] = {"input_count": len(dirs)}

    # Deduplicate and resolve
    resolved: list[Path] = []
    seen: set[str] = set()
    exclude_strs = {str(p) for p in (exclude or set())}
    for d in dirs:
        r = d.resolve()
        rs = str(r)
        if rs not in seen and rs not in exclude_strs:
            seen.add(rs)
            resolved.append(r)

    log["after_dedup"] = len(resolved)

    if len(resolved) <= MAX_ADDITIONAL_DIRS:
        log["tier_applied"] = "none"
        return {"dirs": sorted(resolved), "log": log}

    # Tier 1: commonpath consolidation
    tier1 = _tier1_commonpath(resolved)
    log["after_tier1"] = len(tier1)

    if len(tier1) <= MAX_ADDITIONAL_DIRS:
        log["tier_applied"] = "tier1"
        return {"dirs": sorted(tier1), "log": log}

    # Tier 2: select top N by deterministic sort
    tier2 = sorted(tier1)[:MAX_ADDITIONAL_DIRS]
    log["tier_applied"] = "tier2"
    log["after_tier2"] = len(tier2)
    log["dropped"] = len(tier1) - len(tier2)

    return {"dirs": tier2, "log": log}


def _tier1_commonpath(dirs: list[Path]) -> list[Path]:
    """Tier 1: merge dirs sharing common ancestors.

    Groups directories that share a common parent, and replaces the group
    with the common parent only if the parent directory's file count
    is <= 3x the total file count of the constituent directories.
    """
    if len(dirs) <= 1:
        return list(dirs)

    # Group by parent directory
    by_parent: dict[str, list[Path]] = {}
    for d in dirs:
        parent = str(d.parent)
        by_parent.setdefault(parent, []).append(d)

    result: list[Path] = []
    for parent_str, group in by_parent.items():
        if len(group) <= 1:
            result.extend(group)
            continue

        # Try common path merge
        try:
            common = Path(os.path.commonpath([str(g) for g in group]))
        except ValueError:
            result.extend(group)
            continue

        # Count files in constituents
        constituent_files = 0
        for g in group:
            if g.is_dir():
                constituent_files += sum(1 for _ in g.rglob("*") if _.is_file())

        # Count files in common parent
        parent_files = 0
        if common.is_dir():
            parent_files = sum(1 for _ in common.rglob("*") if _.is_file())

        # Only merge if parent file count <= 3x constituent total
        if constituent_files > 0 and parent_files <= 3 * constituent_files:
            result.append(common)
        else:
            result.extend(group)

    # Deduplicate result
    seen: set[str] = set()
    deduped: list[Path] = []
    for r in result:
        rs = str(r)
        if rs not in seen:
            seen.add(rs)
            deduped.append(r)

    return deduped


class PortifyProcess(ClaudeProcess):
    """Claude subprocess wrapper for cli-portify pipeline steps.

    Extends ClaudeProcess with:
    - Dual --add-dir for work_dir and workflow_path
    - @path reference injection into prompts
    - Post-execution capture of stdout/stderr/diagnostics
    """

    def __init__(
        self,
        *,
        prompt: str,
        output_file: Path,
        error_file: Path,
        work_dir: Path,
        workflow_path: Path,
        artifact_refs: list[Path] | None = None,
        additional_dirs: list[Path] | None = None,
        max_turns: int = 100,
        model: str = "",
        timeout_seconds: int = 300,
        output_format: str = "text",
        extra_args: list[str] | None = None,
    ):
        self._work_dir = work_dir.resolve()
        self._workflow_path = workflow_path.resolve()
        self._artifact_refs = artifact_refs or []
        self._additional_dirs_input = additional_dirs
        self._resolution_log: dict[str, object] = {}

        # Build --add-dir args for dual path scoping + additional dirs
        add_dir_args = self._build_add_dir_args()

        # Merge with any extra args
        all_extra = add_dir_args + (extra_args or [])

        # Build the full prompt with @path references
        full_prompt = self._build_prompt_with_refs(prompt)

        super().__init__(
            prompt=full_prompt,
            output_file=output_file,
            error_file=error_file,
            max_turns=max_turns,
            model=model,
            timeout_seconds=timeout_seconds,
            output_format=output_format,
            extra_args=all_extra,
        )

    def _build_add_dir_args(self) -> list[str]:
        """Build --add-dir arguments for work directory, workflow path, and additional dirs.

        Both base directories are scoped via --add-dir so the Claude subprocess
        can read files from the output workspace and the source workflow.
        Additional directories from ComponentTree.all_source_dirs are consolidated
        and capped.
        """
        args: list[str] = []

        # Work directory (output artifacts live here)
        args.extend(["--add-dir", str(self._work_dir)])

        # Workflow path (source skill files)
        if self._workflow_path != self._work_dir:
            args.extend(["--add-dir", str(self._workflow_path)])

        # Additional dirs from component tree (when provided)
        if self._additional_dirs_input is not None:
            consolidated = consolidate_dirs(
                self._additional_dirs_input,
                exclude={self._work_dir, self._workflow_path},
            )
            self._resolution_log = consolidated["log"]
            for d in consolidated["dirs"]:
                args.extend(["--add-dir", str(d)])

        return args

    def _build_prompt_with_refs(self, base_prompt: str) -> str:
        """Inject @path references to prior artifacts into the prompt.

        Each artifact_ref is prepended as an @path directive so the
        Claude subprocess can access prior step outputs.
        """
        if not self._artifact_refs:
            return base_prompt

        ref_lines = []
        for ref in self._artifact_refs:
            resolved = ref.resolve()
            ref_lines.append(f"@{resolved}")

        refs_block = "\n".join(ref_lines)
        return f"{refs_block}\n\n{base_prompt}"

    def run(self) -> ProcessResult:
        """Execute the subprocess and capture all outputs.

        Returns a ProcessResult with exit code, stdout/stderr text,
        timeout state, and timing.
        """
        start_time = time.monotonic()
        timed_out = False

        self.start()
        exit_code = self.wait()

        duration = time.monotonic() - start_time

        # Timeout detection: exit code 124 is the bash timeout convention
        if exit_code == 124:
            timed_out = True

        # Read captured output
        stdout_text = self._read_file_safe(self.output_file)
        stderr_text = self._read_file_safe(self.error_file)

        _log.debug(
            "process_complete exit=%d timeout=%s duration=%.1fs stdout_len=%d stderr_len=%d",
            exit_code,
            timed_out,
            duration,
            len(stdout_text),
            len(stderr_text),
        )

        return ProcessResult(
            exit_code=exit_code,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
            timed_out=timed_out,
            duration_seconds=duration,
            output_file=self.output_file,
            error_file=self.error_file,
        )

    @staticmethod
    def _read_file_safe(path: Path) -> str:
        """Read file content, returning empty string on failure."""
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ""

    @property
    def work_dir(self) -> Path:
        return self._work_dir

    @property
    def workflow_path(self) -> Path:
        return self._workflow_path

    @property
    def artifact_refs(self) -> list[Path]:
        return list(self._artifact_refs)

    @property
    def resolution_log(self) -> dict[str, object]:
        return dict(self._resolution_log)
