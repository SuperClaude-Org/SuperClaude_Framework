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


class GateMode(Enum):
    """Gating behavior for pipeline steps.

    BLOCKING: Step must pass before the next step can begin (default).
    TRAILING: Step runs but does not block subsequent steps; failures
              are evaluated after a grace period.
    """

    BLOCKING = "BLOCKING"
    TRAILING = "TRAILING"


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
    gate_mode: GateMode = GateMode.BLOCKING


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


class DeliverableKind(Enum):
    """Classification of deliverable type for decomposition and analysis."""

    IMPLEMENT = "implement"
    VERIFY = "verify"
    INVARIANT_CHECK = "invariant_check"
    FMEA_TEST = "fmea_test"
    GUARD_TEST = "guard_test"
    CONTRACT_TEST = "contract_test"

    @classmethod
    def from_str(cls, value: str) -> DeliverableKind:
        """Parse a string into a DeliverableKind, raising ValueError on unknown."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(k.value for k in cls)
            raise ValueError(
                f"Unknown deliverable kind: {value!r}. Valid kinds: {valid}"
            )


@dataclass
class Deliverable:
    """A single deliverable within a pipeline step or roadmap task.

    Attributes:
        id: Unique identifier (e.g. 'D-0001', 'D-0001.a').
        description: Human-readable description of what this deliverable produces.
        kind: Classification for decomposition passes. Defaults to 'implement'
              for backward compatibility with pre-extension deliverables.
        metadata: Attachment point for analytical passes (M2-M4). Defaults to
                  empty dict. Round-trip serializable.
    """

    id: str
    description: str
    kind: DeliverableKind = DeliverableKind.IMPLEMENT
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to a dict for JSON round-trip."""
        return {
            "id": self.id,
            "description": self.description,
            "kind": self.kind.value,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Deliverable:
        """Deserialize from a dict. Pre-extension dicts without 'kind' default to 'implement'."""
        kind_str = data.get("kind", "implement")
        return cls(
            id=data["id"],
            description=data["description"],
            kind=DeliverableKind.from_str(kind_str),
            metadata=data.get("metadata", {}),
        )


@dataclass
class PipelineConfig:
    """Configuration shared by both sprint and roadmap pipelines."""

    work_dir: Path = field(default_factory=lambda: Path("."))
    dry_run: bool = False
    max_turns: int = 100
    model: str = ""
    permission_flag: str = "--dangerously-skip-permissions"
    debug: bool = False
    grace_period: int = 0
