"""PortifyProcess — subprocess wrapper for CLI Portify pipeline steps.

Extends ClaudeProcess from the pipeline base with:
- Dual --add-dir for work_dir and workflow_path (T01.03)
- @path prompt construction for prior-step artifact references
- ProcessResult capturing exit code, stdout, stderr, timeout, duration
- claude binary detection via shutil.which (T03.05 / FR-036)
- Additional dirs consolidation with cap at MAX_ADDITIONAL_DIRS (T02.03)
"""

from __future__ import annotations

import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from superclaude.cli.pipeline.process import ClaudeProcess

# ---------------------------------------------------------------------------
# T03.05: Claude binary detection (FR-036, NFR-017)
# ---------------------------------------------------------------------------

MAX_ADDITIONAL_DIRS: int = 10


def detect_claude_binary() -> str:
    """Detect the claude CLI binary using shutil.which.

    Returns the path to the binary if found.
    Raises RuntimeError with installation instructions if not found.
    """
    binary = shutil.which("claude")
    if binary is None:
        raise RuntimeError(
            "claude CLI binary not found in PATH.\n"
            "Install Claude Code: https://claude.ai/code\n"
            "After installation, ensure 'claude' is on your PATH."
        )
    return binary


# ---------------------------------------------------------------------------
# ProcessResult
# ---------------------------------------------------------------------------


@dataclass
class ProcessResult:
    """Captures all metadata from a subprocess invocation."""

    exit_code: int = -1
    stdout_text: str = ""
    stderr_text: str = ""
    timed_out: bool = False
    duration_seconds: float = 0.0
    output_file: Optional[Path] = None
    error_file: Optional[Path] = None

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


# ---------------------------------------------------------------------------
# consolidate_dirs()
# ---------------------------------------------------------------------------


def consolidate_dirs(
    dirs: list[Path],
    exclude: Optional[set[Path]] = None,
) -> dict:
    """Two-tier directory consolidation: cap at MAX_ADDITIONAL_DIRS.

    Returns a dict with:
      - "dirs": list[Path] of resolved, deduplicated dirs (≤ MAX_ADDITIONAL_DIRS)
      - "log": dict with consolidation metadata
    """
    exclude_resolved: set[Path] = {p.resolve() for p in (exclude or set())}

    # Deduplicate and resolve
    seen: set[Path] = set()
    unique: list[Path] = []
    for d in dirs:
        r = d.resolve()
        if r not in seen and r not in exclude_resolved:
            seen.add(r)
            unique.append(r)

    input_count = len(dirs)
    if len(unique) <= MAX_ADDITIONAL_DIRS:
        return {
            "dirs": unique,
            "log": {
                "input_count": input_count,
                "output_count": len(unique),
                "tier_applied": "none",
            },
        }

    # Tier 2: sort by path and take first MAX_ADDITIONAL_DIRS
    selected = sorted(unique)[:MAX_ADDITIONAL_DIRS]
    return {
        "dirs": selected,
        "log": {
            "input_count": input_count,
            "output_count": len(selected),
            "tier_applied": "tier2",
            "dropped": len(unique) - len(selected),
        },
    }


# ---------------------------------------------------------------------------
# PortifyProcess
# ---------------------------------------------------------------------------


class PortifyProcess(ClaudeProcess):
    """Extends ClaudeProcess for CLI Portify pipeline step invocations.

    Adds:
    - Dual --add-dir flags for work_dir and workflow_path
    - @path prompt construction for artifact_refs
    - additional_dirs support with MAX_ADDITIONAL_DIRS cap
    - ProcessResult via run()
    """

    def __init__(
        self,
        *,
        prompt: str,
        output_file: Path,
        error_file: Path,
        work_dir: Path,
        workflow_path: Path,
        max_turns: int = 100,
        model: str = "",
        timeout_seconds: int = 300,
        extra_args: Optional[list[str]] = None,
        artifact_refs: Optional[list[Path]] = None,
        additional_dirs: Optional[list[Path]] = None,
    ) -> None:
        self.work_dir = work_dir.resolve()
        self.workflow_path = workflow_path.resolve()
        self.artifact_refs: list[Path] = artifact_refs or []
        self._additional_dirs_input = additional_dirs

        # Build @path-prefixed prompt
        built_prompt = self._build_prompt(prompt, self.artifact_refs)

        super().__init__(
            prompt=built_prompt,
            output_file=output_file,
            error_file=error_file,
            max_turns=max_turns,
            model=model,
            timeout_seconds=timeout_seconds,
            extra_args=extra_args,
            output_format="text",
        )

        # Consolidate additional_dirs
        if additional_dirs is not None:
            result = consolidate_dirs(
                additional_dirs,
                exclude={self.work_dir, self.workflow_path},
            )
            self._consolidated_dirs: list[Path] = result["dirs"]
            self.resolution_log: dict = result["log"]
            self.resolution_log["input_count"] = len(additional_dirs)
        else:
            self._consolidated_dirs = []
            self.resolution_log: dict = {"input_count": 0, "tier_applied": "none"}

    @staticmethod
    def _build_prompt(base_prompt: str, artifact_refs: list[Path]) -> str:
        if not artifact_refs:
            return base_prompt
        ref_lines = "\n".join(f"@{ref.resolve()}" for ref in artifact_refs)
        return f"{ref_lines}\n{base_prompt}"

    def build_command(self) -> list[str]:
        """Build claude CLI command with dual --add-dir flags."""
        cmd = super().build_command()

        # Insert --add-dir flags before -p (deduplicate work_dir / workflow_path)
        add_dirs: list[Path] = []
        seen: set[Path] = set()
        for d in [self.work_dir, self.workflow_path]:
            if d not in seen:
                seen.add(d)
                add_dirs.append(d)

        # Additional dirs
        for d in self._consolidated_dirs:
            if d not in seen:
                seen.add(d)
                add_dirs.append(d)

        # Inject --add-dir args after the fixed base flags
        add_dir_args: list[str] = []
        for d in add_dirs:
            add_dir_args.extend(["--add-dir", str(d)])

        # Insert before -p
        try:
            p_idx = cmd.index("-p")
            cmd[p_idx:p_idx] = add_dir_args
        except ValueError:
            cmd.extend(add_dir_args)

        return cmd

    def run(self) -> ProcessResult:
        """Start the subprocess, wait for completion, return ProcessResult."""
        start = time.monotonic()
        self.start()
        exit_code = self.wait()
        duration = time.monotonic() - start

        timed_out = exit_code == 124
        stdout_text = ""
        stderr_text = ""

        try:
            stdout_text = self.output_file.read_text(errors="replace")
        except OSError:
            pass
        try:
            stderr_text = self.error_file.read_text(errors="replace")
        except OSError:
            pass

        return ProcessResult(
            exit_code=exit_code,
            stdout_text=stdout_text,
            stderr_text=stderr_text,
            timed_out=timed_out,
            duration_seconds=duration,
            output_file=self.output_file,
            error_file=self.error_file,
        )
