"""Pipeline data models -- shared dataclasses consumed by sprint and roadmap.

This module has zero imports from superclaude.cli.sprint or
superclaude.cli.roadmap (NFR-007). All types here are generic pipeline
primitives that both consumers extend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Literal, Optional


class StepStatus(Enum):
    """Lifecycle status of a single pipeline step."""

    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"

    @property
    def is_terminal(self) -> bool:
        return self in (
            StepStatus.PASS,
            StepStatus.FAIL,
            StepStatus.TIMEOUT,
            StepStatus.CANCELLED,
            StepStatus.SKIPPED,
        )

    @property
    def is_success(self) -> bool:
        return self == StepStatus.PASS

    @property
    def is_failure(self) -> bool:
        return self in (StepStatus.FAIL, StepStatus.TIMEOUT)


@dataclass
class SemanticCheck:
    """Pure Python check applied to file content. No LLM invocation."""

    name: str
    check_fn: Callable[[str], bool]
    failure_message: str


@dataclass
class GateCriteria:
    """Defines what constitutes a passing output for a pipeline step."""

    required_frontmatter_fields: list[str]
    min_lines: int
    enforcement_tier: Literal["STRICT", "STANDARD", "LIGHT", "EXEMPT"] = "STANDARD"
    semantic_checks: list[SemanticCheck] | None = None


@dataclass
class Step:
    """A single pipeline step."""

    id: str
    prompt: str
    output_file: Path
    gate: Optional[GateCriteria]
    timeout_seconds: int
    inputs: list[Path] = field(default_factory=list)
    retry_limit: int = 1
    model: str = ""


@dataclass
class StepResult:
    """Outcome of executing a single pipeline step."""

    step: Optional[Step] = None
    status: StepStatus = StepStatus.PENDING
    attempt: int = 1
    gate_failure_reason: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def duration_seconds(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()


@dataclass
class PipelineConfig:
    """Configuration shared by both sprint and roadmap pipelines."""

    work_dir: Path = field(default_factory=lambda: Path("."))
    dry_run: bool = False
    max_turns: int = 50
    model: str = ""
    permission_flag: str = "--dangerously-skip-permissions"
    debug: bool = False
