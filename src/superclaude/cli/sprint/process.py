"""Sprint process management — subprocess lifecycle, signal handling, and context injection.

ClaudeProcess extends pipeline.process.ClaudeProcess with sprint-specific
constructor (config, phase) and build_prompt(). Lifecycle hooks delegate
debug logging to factory closures, eliminating method overrides.
SignalHandler remains sprint-specific.

Context injection (build_task_context, get_git_diff_context, compress_context_summary)
ensures each task subprocess has visibility into prior work.
"""

from __future__ import annotations

import logging
import signal
import subprocess as _subprocess
from typing import TYPE_CHECKING, Optional

from superclaude.cli.pipeline.process import ClaudeProcess as _PipelineClaudeProcess

from .debug_logger import debug_log
from .models import Phase, SprintConfig

if TYPE_CHECKING:
    from .models import TaskResult

_dbg = logging.getLogger("superclaude.sprint.debug.process")


def _make_spawn_hook(phase: Phase, config: SprintConfig):
    """Factory returning an on_spawn closure for sprint debug logging.

    Captures phase number and config output/error paths so the hook
    can log spawn and files_opened events with full context.
    """
    output_file = config.output_file(phase)
    error_file = config.error_file(phase)
    phase_number = phase.number

    def on_spawn(pid: int) -> None:
        debug_log(
            _dbg,
            "spawn",
            pid=pid,
            cmd="['claude', '--print', '--verbose']",
            phase=phase_number,
        )
        debug_log(
            _dbg,
            "files_opened",
            stdout=str(output_file),
            stderr=str(error_file),
        )

    return on_spawn


def _make_signal_hook(phase: Phase, config: SprintConfig):
    """Factory returning an on_signal closure for sprint debug logging.

    Logs signal_sent events with the signal name and process id.
    """

    def on_signal(pid: int, signal_name: str) -> None:
        debug_log(_dbg, "signal_sent", signal=signal_name, pid=pid)

    return on_signal


def _make_exit_hook(phase: Phase, config: SprintConfig):
    """Factory returning an on_exit closure for sprint debug logging.

    Logs exit events with pid, return code, and timeout detection.
    """

    def on_exit(pid: int, returncode: int | None) -> None:
        debug_log(
            _dbg,
            "exit",
            pid=pid,
            code=returncode,
            was_timeout=(returncode == 124),
        )

    return on_exit


class ClaudeProcess(_PipelineClaudeProcess):
    """Sprint-specific claude process extending the pipeline base.

    Defines only __init__ (with hook wiring) and build_prompt().
    All subprocess lifecycle (start, wait, terminate) is inherited
    from the pipeline base class; sprint debug logging is injected
    via lifecycle hook factories.
    """

    def __init__(self, config: SprintConfig, phase: Phase):
        self.config = config
        self.phase = phase
        prompt = self.build_prompt()
        super().__init__(
            prompt=prompt,
            output_file=config.output_file(phase),
            error_file=config.error_file(phase),
            max_turns=config.max_turns,
            model=config.model,
            permission_flag=config.permission_flag,
            timeout_seconds=config.max_turns * 120 + 300,
            output_format="stream-json",
            on_spawn=_make_spawn_hook(phase, config),
            on_signal=_make_signal_hook(phase, config),
            on_exit=_make_exit_hook(phase, config),
        )

    def build_prompt(self) -> str:
        """Build the /sc:task-unified prompt for this phase."""
        pn = self.phase.number
        phase_file = self.phase.file

        return (
            f"/sc:task-unified Execute all tasks in @{phase_file} "
            f"--compliance strict --strategy systematic\n"
            f"\n"
            f"## Execution Rules\n"
            f"- Execute tasks in order (T{pn:02d}XX.01, T{pn:02d}XX.02, etc.)\n"
            f"- For STRICT tier tasks: use Sequential MCP for analysis, "
            f"run quality verification\n"
            f"- For STANDARD tier tasks: run direct test execution per "
            f"acceptance criteria\n"
            f"- For LIGHT tier tasks: quick sanity check only\n"
            f"- For EXEMPT tier tasks: skip formal verification\n"
            f"- If a STRICT-tier task fails, STOP and report -- "
            f"do not continue to next task\n"
            f"- For all other tier failures, log the failure and continue\n"
            f"\n"
            f"## Scope Boundary\n"
            f"- After completing all tasks, STOP immediately.\n"
            f"- Do not read, open, or act on any subsequent phase file.\n"
            f"\n"
            f"## Important\n"
            f"- This is Phase {pn} of a multi-phase sprint\n"
            f"- Previous phases have already been executed in separate sessions\n"
            f"- Do not re-execute work from prior phases\n"
            f"- Focus only on the tasks defined in the phase file"
        )


class SignalHandler:
    """Register signal handlers for graceful sprint shutdown.

    On SIGINT/SIGTERM:
    1. Set the shutdown flag (checked by the executor loop)
    2. The executor terminates the current claude process
    3. Writes partial execution log
    4. Exits with appropriate code
    """

    def __init__(self):
        self.shutdown_requested = False
        self._original_sigint = None
        self._original_sigterm = None

    def install(self):
        """Install signal handlers."""
        self._original_sigint = signal.getsignal(signal.SIGINT)
        self._original_sigterm = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGINT, self._handle)
        signal.signal(signal.SIGTERM, self._handle)

    def uninstall(self):
        """Restore original signal handlers."""
        if self._original_sigint is not None:
            signal.signal(signal.SIGINT, self._original_sigint)
        if self._original_sigterm is not None:
            signal.signal(signal.SIGTERM, self._original_sigterm)

    def _handle(self, signum, frame):
        self.shutdown_requested = True


# ---------------------------------------------------------------------------
# Context Injection
# ---------------------------------------------------------------------------


def build_task_context(
    prior_results: list[TaskResult],
    *,
    start_commit: str = "",
    compress_threshold: int = 3,
) -> str:
    """Build deterministic context from prior task results for injection into prompts.

    Produces structured markdown containing:
    - Prior task results (status, gate outcome, key details)
    - Gate outcomes (pass/fail/deferred per prior task)
    - Remediation history (reimbursement amounts)
    - Git diff summary (if start_commit is provided)

    Context is compressed via progressive summarization when the number of
    prior results exceeds ``compress_threshold`` (default 3): older tasks
    are reduced to a one-line summary while recent tasks retain full detail.

    Args:
        prior_results: Ordered list of TaskResult from preceding tasks.
        start_commit: Git commit ref for diff context (empty = skip).
        compress_threshold: Number of recent tasks to keep at full detail.

    Returns:
        Structured markdown string for inclusion in task prompts.
    """
    if not prior_results:
        return ""

    sections: list[str] = ["## Prior Task Context\n"]

    # Apply progressive summarization
    if len(prior_results) > compress_threshold:
        compressed = compress_context_summary(prior_results, keep_recent=compress_threshold)
        sections.append(compressed)
    else:
        for result in prior_results:
            sections.append(result.to_context_summary(verbose=True))
            sections.append("")

    # Gate outcome summary
    sections.append("\n### Gate Outcomes\n")
    for result in prior_results:
        sections.append(
            f"- {result.task.task_id}: {result.gate_outcome.value}"
        )

    # Remediation history (only tasks with reimbursement)
    remediated = [r for r in prior_results if r.reimbursement_amount > 0]
    if remediated:
        sections.append("\n### Remediation History\n")
        for result in remediated:
            sections.append(
                f"- {result.task.task_id}: reimbursed {result.reimbursement_amount} turns"
            )

    # Git diff context
    if start_commit:
        diff_section = get_git_diff_context(start_commit)
        if diff_section:
            sections.append(f"\n{diff_section}")

    return "\n".join(sections) + "\n"


def get_git_diff_context(start_commit: str) -> str:
    """Run ``git diff --stat`` from start_commit and return structured section.

    Args:
        start_commit: Git ref (SHA or branch) marking the sprint start.

    Returns:
        Markdown section with the diff summary, or empty string on error.
    """
    try:
        result = _subprocess.run(
            ["git", "diff", "--stat", start_commit],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return ""
        return (
            "### Git Changes Since Sprint Start\n\n"
            "```\n"
            f"{result.stdout.strip()}\n"
            "```"
        )
    except (FileNotFoundError, _subprocess.TimeoutExpired, OSError):
        return ""


def compress_context_summary(
    results: list[TaskResult],
    *,
    keep_recent: int = 3,
) -> str:
    """Compress older task context while preserving recent detail.

    Tasks beyond the ``keep_recent`` window are reduced to a one-line
    summary (status + gate outcome). Recent tasks retain full detail.
    This bounds context growth for long sprints.

    Args:
        results: All prior TaskResult objects in execution order.
        keep_recent: Number of most recent tasks to keep at full detail.

    Returns:
        Markdown string with compressed older tasks and detailed recent tasks.
    """
    if not results:
        return ""

    lines: list[str] = []

    # Compressed older tasks
    if len(results) > keep_recent:
        older = results[:-keep_recent]
        lines.append("#### Earlier Tasks (compressed)\n")
        for result in older:
            lines.append(result.to_context_summary(verbose=False))
        lines.append("")

    # Recent tasks at full detail
    recent = results[-keep_recent:]
    lines.append("#### Recent Tasks\n")
    for result in recent:
        lines.append(result.to_context_summary(verbose=True))
        lines.append("")

    return "\n".join(lines)
