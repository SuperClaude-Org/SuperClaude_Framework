"""Cleanup Audit process management — subprocess lifecycle and signal handling.

CleanupAuditProcess extends pipeline ClaudeProcess with audit-specific
constructor and build_prompt(). SignalHandler provides graceful shutdown.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

import signal
from typing import TYPE_CHECKING

from superclaude.cli.pipeline.process import ClaudeProcess as _PipelineClaudeProcess

from .models import CleanupAuditConfig, CleanupAuditStep

if TYPE_CHECKING:
    pass


class CleanupAuditProcess(_PipelineClaudeProcess):
    """Audit-specific claude process extending the pipeline base.

    Defines __init__ and build_prompt(). All subprocess lifecycle
    (start, wait, terminate) is inherited from the pipeline base class.
    """

    def __init__(self, config: CleanupAuditConfig, step: CleanupAuditStep):
        self.config = config
        self.step = step
        prompt = self.build_prompt()
        super().__init__(
            prompt=prompt,
            output_file=config.work_dir / f"{step.id}-output.jsonl",
            error_file=config.work_dir / f"{step.id}-error.log",
            max_turns=config.max_turns,
            model=config.model,
            permission_flag=config.permission_flag,
            timeout_seconds=step.timeout_seconds,
            output_format="stream-json",
        )

    def build_prompt(self) -> str:
        """Build the prompt for this audit step."""
        return self.step.prompt


class SignalHandler:
    """Register signal handlers for graceful audit shutdown."""

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

    def restore(self):
        """Restore original signal handlers."""
        if self._original_sigint is not None:
            signal.signal(signal.SIGINT, self._original_sigint)
        if self._original_sigterm is not None:
            signal.signal(signal.SIGTERM, self._original_sigterm)

    def _handle(self, signum, frame):
        self.shutdown_requested = True
