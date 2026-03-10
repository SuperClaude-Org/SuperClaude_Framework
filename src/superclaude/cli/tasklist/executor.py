"""Tasklist validation executor -- orchestrates tasklist fidelity checking.

Reads a roadmap file and tasklist directory, builds a validation step,
applies the TASKLIST_FIDELITY_GATE, and writes a fidelity report.

Reuses ``execute_pipeline()`` and ``ClaudeProcess`` from the pipeline module.
No new subprocess abstractions.

Context isolation: each subprocess receives only its prompt and --file inputs.
"""

from __future__ import annotations

import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from ..pipeline.executor import execute_pipeline
from ..pipeline.models import PipelineConfig, Step, StepResult, StepStatus
from ..pipeline.process import ClaudeProcess
from .gates import TASKLIST_FIDELITY_GATE
from .models import TasklistValidateConfig
from .prompts import build_tasklist_fidelity_prompt

_log = logging.getLogger("superclaude.tasklist.executor")

# Threshold above which inline embedding falls back to --file flags
_EMBED_SIZE_LIMIT = 100 * 1024  # 100 KB


def _collect_tasklist_files(tasklist_dir: Path) -> list[Path]:
    """Collect all markdown files in the tasklist directory.

    Returns sorted list of .md files for deterministic ordering.
    """
    if not tasklist_dir.is_dir():
        raise FileNotFoundError(
            f"Tasklist directory not found: {tasklist_dir}"
        )
    files = sorted(tasklist_dir.glob("*.md"))
    if not files:
        raise FileNotFoundError(
            f"No markdown files found in tasklist directory: {tasklist_dir}"
        )
    return files


def _embed_inputs(input_paths: list[Path]) -> str:
    """Read input files and return their contents as fenced code blocks."""
    if not input_paths:
        return ""
    blocks: list[str] = []
    for p in input_paths:
        content = Path(p).read_text(encoding="utf-8")
        blocks.append(f"# {p}\n```\n{content}\n```")
    return "\n\n".join(blocks)


def _sanitize_output(output_file: Path) -> int:
    """Strip conversational preamble before YAML frontmatter."""
    try:
        content = output_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        return 0

    if content.lstrip().startswith("---"):
        return 0

    match = re.search(r"^---[ \t]*$", content, re.MULTILINE)
    if match is None:
        return 0

    preamble = content[: match.start()]
    cleaned = content[match.start():]
    preamble_bytes = len(preamble.encode("utf-8"))

    tmp_file = output_file.with_suffix(output_file.suffix + ".tmp")
    tmp_file.write_text(cleaned, encoding="utf-8")
    os.replace(tmp_file, output_file)

    _log.info("Stripped %d-byte preamble from %s", preamble_bytes, output_file)
    return preamble_bytes


def tasklist_run_step(
    step: Step,
    config: PipelineConfig,
    cancel_check: Callable[[], bool],
) -> StepResult:
    """Execute a single tasklist validation step as a Claude subprocess.

    Mirrors ``validate_run_step`` from ``roadmap/validate_executor.py``.
    """
    started_at = datetime.now(timezone.utc)

    if config.dry_run:
        _log.info("[dry-run] Would execute step '%s'", step.id)
        return StepResult(
            step=step,
            status=StepStatus.PASS,
            attempt=1,
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
        )

    # Inline embedding
    embedded = _embed_inputs(step.inputs)
    if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
        effective_prompt = step.prompt + "\n\n" + embedded
        extra_args: list[str] = []
    elif embedded:
        effective_prompt = step.prompt
        extra_args = [
            arg
            for input_path in step.inputs
            for arg in ("--file", str(input_path))
        ]
    else:
        effective_prompt = step.prompt
        extra_args = []

    proc = ClaudeProcess(
        prompt=effective_prompt,
        output_file=step.output_file,
        error_file=step.output_file.with_suffix(".err"),
        max_turns=config.max_turns,
        model=step.model or config.model,
        permission_flag=config.permission_flag,
        timeout_seconds=step.timeout_seconds,
        output_format="text",
        extra_args=extra_args,
    )

    proc.start()

    while proc._process is not None and proc._process.poll() is None:
        if cancel_check():
            proc.terminate()
            return StepResult(
                step=step,
                status=StepStatus.CANCELLED,
                attempt=1,
                gate_failure_reason="Cancelled by external signal",
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
            )
        time.sleep(1)

    exit_code = proc.wait()
    finished_at = datetime.now(timezone.utc)

    if exit_code == 124:
        return StepResult(
            step=step,
            status=StepStatus.TIMEOUT,
            attempt=1,
            gate_failure_reason=f"Step '{step.id}' timed out after {step.timeout_seconds}s",
            started_at=started_at,
            finished_at=finished_at,
        )

    if exit_code != 0:
        return StepResult(
            step=step,
            status=StepStatus.FAIL,
            attempt=1,
            gate_failure_reason=f"Step '{step.id}' exited with code {exit_code}",
            started_at=started_at,
            finished_at=finished_at,
        )

    _sanitize_output(step.output_file)

    return StepResult(
        step=step,
        status=StepStatus.PASS,
        attempt=1,
        started_at=started_at,
        finished_at=finished_at,
    )


def _build_steps(config: TasklistValidateConfig) -> list[Step]:
    """Build the tasklist validation pipeline steps."""
    tasklist_files = _collect_tasklist_files(config.tasklist_dir)
    all_inputs = [config.roadmap_file] + tasklist_files

    return [
        Step(
            id="tasklist-fidelity",
            prompt=build_tasklist_fidelity_prompt(
                config.roadmap_file, config.tasklist_dir,
            ),
            output_file=config.output_dir / "tasklist-fidelity.md",
            gate=TASKLIST_FIDELITY_GATE,
            timeout_seconds=600,
            inputs=all_inputs,
            retry_limit=1,
            model=config.model,
        ),
    ]


def _has_high_severity(report_path: Path) -> bool:
    """Check if the fidelity report has HIGH severity deviations.

    Returns True if high_severity_count > 0, used for CLI exit code.
    """
    if not report_path.exists():
        return True  # No report = assume failure

    content = report_path.read_text(encoding="utf-8")
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return True

    rest = stripped[3:].lstrip("\n")
    end_idx = rest.find("\n---")
    if end_idx == -1:
        return True

    for line in rest[:end_idx].splitlines():
        line = line.strip()
        if line.startswith("high_severity_count:"):
            value = line.split(":", 1)[1].strip()
            try:
                return int(value) > 0
            except (ValueError, TypeError):
                return True

    return True  # Field not found = assume failure


def execute_tasklist_validate(config: TasklistValidateConfig) -> bool:
    """Execute the tasklist validation pipeline.

    Returns True if validation passed (no HIGH severity deviations),
    False otherwise (used for CLI exit code).
    """
    steps = _build_steps(config)

    results = execute_pipeline(
        steps=steps,
        config=config,
        run_step=tasklist_run_step,
    )

    report_path = config.output_dir / "tasklist-fidelity.md"

    # Check for pipeline failures
    failures = [r for r in results if r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)]
    if failures:
        _log.error(
            "Tasklist validation pipeline halted: %d step(s) failed",
            len(failures),
        )
        return False

    return not _has_high_severity(report_path)
