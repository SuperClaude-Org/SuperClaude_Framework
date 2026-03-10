"""Cleanup Audit logging — dual-format JSONL + Markdown execution logs.

Follows the sprint logging pattern. See src/superclaude/cli/sprint/logging_.py.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

import json
import time

from rich.console import Console

from .models import (
    CleanupAuditConfig,
    CleanupAuditResult,
    CleanupAuditStatus,
    CleanupAuditStep,
    CleanupAuditStepResult,
)


class CleanupAuditLogger:
    """Dual-format audit logger: JSONL (machine) + Markdown (human)."""

    def __init__(self, config: CleanupAuditConfig):
        self.config = config
        self.console = Console(stderr=True)
        config.work_dir.mkdir(parents=True, exist_ok=True)

    def write_header(self):
        """Write audit header to both log formats."""
        self._jsonl(
            {
                "event": "audit_start",
                "timestamp": time.time(),
                "target": str(self.config.target_path),
                "pass_selection": self.config.pass_selection,
                "focus": self.config.focus,
                "batch_size": self.config.batch_size,
                "max_turns": self.config.max_turns,
                "model": self.config.model or "default",
            }
        )

        md = [
            "# Cleanup Audit Execution Log",
            "",
            f"**Target**: {self.config.target_path}",
            f"**Pass**: {self.config.pass_selection}",
            f"**Focus**: {self.config.focus}",
            f"**Batch size**: {self.config.batch_size}",
            f"**Max turns**: {self.config.max_turns}",
            f"**Model**: {self.config.model or 'default'}",
            "",
            "| Step | Status | Duration | Output |",
            "|------|--------|----------|--------|",
        ]
        self.config.execution_log_md.write_text("\n".join(md) + "\n")

    def write_step_start(self, step: CleanupAuditStep):
        """Log step start."""
        self._jsonl(
            {
                "event": "step_start",
                "step_id": step.id,
                "pass_type": step.pass_type.value,
                "agent_type": step.agent_type,
                "timestamp": time.time(),
            }
        )

    def write_step_result(self, result: CleanupAuditStepResult):
        """Log step completion."""
        self._jsonl(
            {
                "event": "step_complete",
                "step_id": result.step.id if result.step else "unknown",
                "status": result.status.value,
                "exit_code": result.exit_code,
                "duration_seconds": result.duration_seconds,
                "output_bytes": result.output_bytes,
            }
        )

        row = (
            f"| {result.step.id if result.step else '?'} "
            f"| {result.status.value} "
            f"| {result.duration_seconds:.1f}s "
            f"| {result.output_bytes}B |"
        )
        with open(self.config.execution_log_md, "a") as f:
            f.write(row + "\n")

        # Screen output
        if result.status == CleanupAuditStatus.ERROR:
            self._screen_error(
                f"Step {result.step.id if result.step else '?'}: {result.status.value}"
            )
        elif result.status in (CleanupAuditStatus.HALT, CleanupAuditStatus.TIMEOUT):
            self._screen_warn(
                f"Step {result.step.id if result.step else '?'}: {result.status.value}"
            )
        elif result.status in (
            CleanupAuditStatus.PASS,
            CleanupAuditStatus.PASS_NO_REPORT,
        ):
            self._screen_info(
                f"Step {result.step.id if result.step else '?'}: {result.status.value}"
            )

    def write_summary(self, result: CleanupAuditResult):
        """Write audit summary to both logs."""
        self._jsonl(
            {
                "event": "audit_complete",
                "outcome": result.outcome.value,
                "duration_seconds": result.duration_seconds,
                "steps_passed": result.steps_passed,
                "steps_failed": result.steps_failed,
                "halt_step": result.halt_step,
            }
        )

        with open(self.config.execution_log_md, "a") as f:
            f.write(f"\n**Outcome**: {result.outcome.value}\n")
            f.write(f"**Total duration**: {result.duration_seconds:.1f}s\n")
            if result.halt_step:
                f.write(f"**Halted at**: {result.halt_step}\n")
                resume = result.resume_command()
                if resume:
                    f.write(f"**Resume**: `{resume}`\n")

    def _jsonl(self, data: dict):
        with open(self.config.execution_log_jsonl, "a") as f:
            f.write(json.dumps(data, default=str) + "\n")

    def _screen_info(self, msg: str):
        self.console.print(f"[green][INFO][/] {msg}")

    def _screen_warn(self, msg: str):
        self.console.print(f"[yellow][WARN][/] {msg}")

    def _screen_error(self, msg: str):
        self.console.print(f"[bold red][ERROR][/] {msg}\a")
