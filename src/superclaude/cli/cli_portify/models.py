"""Domain models for cli-portify pipeline.

Extends shared pipeline base types with portify-specific
configuration, status tracking, and result telemetry.

Per D-0002 Ownership Boundary 1 (Config/Model Layer), this module
contains: PortifyConfig, PortifyStepResult, PortifyStatus,
PortifyOutcome, ComponentInventory, PortifyMonitorState.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Literal

from superclaude.cli.pipeline.models import (
    PipelineConfig,
    StepResult,
    StepStatus,
)


# --- Error Code Constants (R-012) ---

ERR_TARGET_NOT_FOUND = "ERR_TARGET_NOT_FOUND"
ERR_AMBIGUOUS_TARGET = "ERR_AMBIGUOUS_TARGET"
ERR_BROKEN_ACTIVATION = "ERR_BROKEN_ACTIVATION"
WARN_MISSING_AGENTS = "WARN_MISSING_AGENTS"


# --- Enums ---


class TargetInputType(Enum):
    """Classification of the 5 input forms for target resolution.

    Used by resolve_target() to classify how the user specified the
    portify target.
    """

    COMMAND_NAME = "command_name"
    COMMAND_PATH = "command_path"
    SKILL_DIR = "skill_dir"
    SKILL_NAME = "skill_name"
    SKILL_FILE = "skill_file"


@dataclass
class ResolvedTarget:
    """Result of resolve_target() — the resolved command/skill pair.

    All path fields use Path for internal manipulation; boundary
    conversion to str happens via to_flat_inventory() on ComponentTree.
    """

    input_form: str
    input_type: TargetInputType
    command_path: Path | None = None
    skill_dir: Path | None = None
    project_root: Path | None = None
    commands_dir: Path | None = None
    skills_dir: Path | None = None
    agents_dir: Path | None = None


class PortifyStatus(Enum):
    """Step-level status for cli-portify pipeline."""

    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    FAIL = "fail"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"
    ERROR = "error"


class PortifyOutcome(Enum):
    """Aggregate pipeline outcome."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    DRY_RUN = "dry_run"


class FailureClassification(Enum):
    """Classification of step failures for diagnostics and resume logic.

    Per D-0003 NFR-009 failure/default population rules.
    """

    TIMEOUT = "timeout"
    MISSING_ARTIFACT = "missing_artifact"
    MALFORMED_FRONTMATTER = "malformed_frontmatter"
    GATE_FAILURE = "gate_failure"
    USER_REJECTION = "user_rejection"
    BUDGET_EXHAUSTION = "budget_exhaustion"
    PARTIAL_ARTIFACT = "partial_artifact"


# --- Configuration ---


@dataclass
class PortifyConfig(PipelineConfig):
    """Cli-portify pipeline configuration.

    Extends PipelineConfig with portify-specific settings:
    - Workflow path resolution (directory containing SKILL.md)
    - CLI name derivation (strip sc-/-protocol, kebab/snake conversion)
    - Output directory writability check
    - Name collision detection

    Per D-0001 Resolution 1: iteration_timeout is per-iteration
    independent (default 300s). max_convergence controls iteration
    count, not timeout division.
    """

    workflow_path: Path = field(default_factory=lambda: Path("."))
    output_dir: Path = field(default_factory=lambda: Path("."))
    cli_name: str = ""
    skip_review: bool = False
    start_step: str | None = None
    iteration_timeout: int = 300
    max_convergence: int = 3
    # v2.24.1 resolution fields (R-008)
    target_input: str | None = None
    target_type: TargetInputType | None = None
    command_path: Path | None = None
    commands_dir: Path | None = None
    skills_dir: Path | None = None
    agents_dir: Path | None = None
    project_root: Path | None = None
    include_agents: bool = True
    save_manifest_path: Path | None = None
    component_tree: ComponentTree | None = None

    def __post_init__(self) -> None:
        """Resolve workflow path and derive CLI name."""
        if not self.work_dir or self.work_dir == Path("."):
            self.work_dir = self.output_dir

    def resolve_workflow_path(self) -> Path:
        """Resolve and validate the workflow path.

        Returns the resolved path to the directory containing SKILL.md.

        Raises:
            FileNotFoundError: If workflow_path does not exist.
            ValueError: If no SKILL.md found in workflow_path.
        """
        resolved = self.workflow_path.resolve()
        if not resolved.exists():
            raise FileNotFoundError(
                f"Workflow path does not exist: {resolved}"
            )
        if resolved.is_file():
            if resolved.name == "SKILL.md":
                return resolved.parent
            raise ValueError(
                f"Workflow path is a file but not SKILL.md: {resolved}"
            )
        skill_file = resolved / "SKILL.md"
        if not skill_file.exists():
            raise ValueError(
                f"No SKILL.md found in workflow directory: {resolved}"
            )
        return resolved

    def derive_cli_name(self) -> str:
        """Derive CLI command name from workflow directory name.

        Prefers resolved command filename (R-009) when ``command_path``
        is set, stripping the ``.md`` extension.  Falls back to the
        existing workflow-directory logic: strips ``sc-`` prefix and
        ``-protocol`` suffix, then converts to kebab-case.  If
        ``cli_name`` is already set, returns it unchanged.

        Returns:
            Derived CLI name in kebab-case.
        """
        if self.cli_name:
            return self.cli_name
        # R-009: prefer resolved command name when available
        if self.command_path is not None:
            name = self.command_path.stem
            name = name.replace("_", "-")
            return name
        name = self.workflow_path.resolve().name
        # Strip sc- prefix
        if name.startswith("sc-"):
            name = name[3:]
        # Strip -protocol suffix
        if name.endswith("-protocol"):
            name = name[: -len("-protocol")]
        # Normalise to kebab-case (replace underscores)
        name = name.replace("_", "-")
        return name

    def check_output_writable(self) -> None:
        """Check that the output directory is writable.

        Creates the directory if it doesn't exist.

        Raises:
            PermissionError: If the output directory is not writable.
        """
        out = self.output_dir.resolve()
        try:
            out.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise PermissionError(
                f"Cannot create output directory: {out}"
            ) from exc
        if not out.is_dir():
            raise PermissionError(
                f"Output path exists but is not a directory: {out}"
            )

    def check_name_collision(self, existing_commands: list[str] | None = None) -> str | None:
        """Check if the derived CLI name collides with existing commands.

        Args:
            existing_commands: List of existing CLI command names. If None,
                checks against known built-in superclaude commands.

        Returns:
            The colliding command name if collision detected, else None.
        """
        cli_name = self.derive_cli_name()
        builtins = existing_commands or [
            "install", "mcp", "update", "install-skill", "doctor",
            "version", "sprint", "roadmap", "cleanup-audit", "tasklist",
        ]
        if cli_name in builtins:
            return cli_name
        return None

    def to_snake_case(self, name: str | None = None) -> str:
        """Convert a kebab-case name to snake_case.

        Args:
            name: Name to convert. Defaults to derived CLI name.

        Returns:
            snake_case version of the name.
        """
        target = name or self.derive_cli_name()
        return target.replace("-", "_")

    @property
    def results_dir(self) -> Path:
        return self.output_dir / "results"

    @property
    def artifacts_dir(self) -> Path:
        return self.output_dir / "artifacts"


# --- Resume Metadata (Typed Fields per D-0001) ---


@dataclass
class ResumeContext:
    """Typed resume metadata for pipeline re-entry.

    Per D-0001 Resolution 2: resume uses typed fields, not generic dict.
    """

    last_completed_step: str = ""
    last_completed_step_number: int = 0
    failed_step: str = ""
    failed_step_number: int = 0
    failure_classification: FailureClassification | None = None
    re_run_required: bool = False
    artifacts_preserved: list[str] = field(default_factory=list)
    resume_command: str = ""


# --- Step Result ---


@dataclass
class PortifyStepResult(StepResult):
    """Result for a single cli-portify pipeline step.

    Extends StepResult with portify-specific metadata:
    - Step metadata (name, number, phase)
    - Artifact paths
    - Gate tier metadata
    - Timeout settings (per-iteration, per D-0001)
    - Review flags
    - Typed resume metadata (not generic dict)
    """

    portify_status: PortifyStatus = PortifyStatus.PENDING
    step_name: str = ""
    step_number: int = 0
    phase: int = 0
    artifact_path: str = ""
    gate_tier: Literal["STRICT", "STANDARD", "LIGHT", "EXEMPT"] = "STANDARD"
    iteration_timeout: int = 300
    iteration_number: int = 0
    review_required: bool = False
    review_accepted: bool | None = None
    failure_classification: FailureClassification | None = None
    resume_context: ResumeContext = field(default_factory=ResumeContext)

    @property
    def is_resumable(self) -> bool:
        """Whether this failed step can be resumed."""
        non_resumable = {
            FailureClassification.USER_REJECTION,
        }
        if self.failure_classification in non_resumable:
            return False
        return self.portify_status in (
            PortifyStatus.FAIL,
            PortifyStatus.TIMEOUT,
            PortifyStatus.ERROR,
        )


# --- Component Inventory ---


@dataclass
class ComponentEntry:
    """A single component discovered in a workflow."""

    name: str
    path: str
    component_type: str
    line_count: int


@dataclass
class ComponentInventory:
    """Inventory of components discovered in a workflow.

    Produced by Step 2 (discover-components).
    """

    source_skill: str = ""
    components: list[ComponentEntry] = field(default_factory=list)

    @property
    def component_count(self) -> int:
        return len(self.components)

    @property
    def total_lines(self) -> int:
        return sum(c.line_count for c in self.components)


# --- Tiered Component Entries (v2.24.1 Resolution) ---


@dataclass
class CommandEntry:
    """Tier 0: Command file entry."""

    tier: int = 0
    name: str = ""
    path: Path | None = None
    line_count: int = 0
    source_dir: Path | None = None


@dataclass
class SkillEntry:
    """Tier 1: Skill directory entry."""

    tier: int = 1
    name: str = ""
    path: Path | None = None
    line_count: int = 0
    source_dir: Path | None = None


@dataclass
class AgentEntry:
    """Tier 2: Agent file entry."""

    tier: int = 2
    name: str = ""
    path: Path | None = None
    line_count: int = 0
    source_dir: Path | None = None
    found: bool = True
    referenced_in: str = "auto"


@dataclass
class ComponentTree:
    """Aggregated component hierarchy from resolution.

    Holds the resolved command (Tier 0), skill (Tier 1), and
    agents (Tier 2) discovered for a target.
    """

    command: CommandEntry | None = None
    skill: SkillEntry | None = None
    agents: list[AgentEntry] = field(default_factory=list)

    @property
    def component_count(self) -> int:
        count = 0
        if self.command is not None:
            count += 1
        if self.skill is not None:
            count += 1
        count += len(self.agents)
        return count

    @property
    def total_lines(self) -> int:
        total = 0
        if self.command is not None:
            total += self.command.line_count
        if self.skill is not None:
            total += self.skill.line_count
        total += sum(a.line_count for a in self.agents)
        return total

    @property
    def all_source_dirs(self) -> list[Path]:
        dirs: list[Path] = []
        if self.command is not None and self.command.source_dir is not None:
            dirs.append(self.command.source_dir)
        if self.skill is not None and self.skill.source_dir is not None:
            if self.skill.source_dir not in dirs:
                dirs.append(self.skill.source_dir)
        for agent in self.agents:
            if agent.source_dir is not None and agent.source_dir not in dirs:
                dirs.append(agent.source_dir)
        return dirs

    def to_flat_inventory(self) -> ComponentInventory:
        """Convert to backward-compatible ComponentInventory (Path -> str boundary).

        All Path fields are converted to str for the legacy interface.
        """
        components: list[ComponentEntry] = []
        if self.command is not None:
            components.append(ComponentEntry(
                name=self.command.name,
                path=str(self.command.path) if self.command.path else "",
                component_type="command",
                line_count=self.command.line_count,
            ))
        if self.skill is not None:
            components.append(ComponentEntry(
                name=self.skill.name,
                path=str(self.skill.path) if self.skill.path else "",
                component_type="skill",
                line_count=self.skill.line_count,
            ))
        for agent in self.agents:
            components.append(ComponentEntry(
                name=agent.name,
                path=str(agent.path) if agent.path else "",
                component_type="agent",
                line_count=agent.line_count,
            ))
        source_skill = self.skill.name if self.skill else ""
        return ComponentInventory(
            source_skill=source_skill,
            components=components,
        )

    def to_manifest_markdown(self) -> str:
        """Produce human-readable Markdown manifest with YAML frontmatter."""
        cmd_name = self.command.name if self.command else ""
        skill_name = self.skill.name if self.skill else ""
        lines = [
            "---",
            f"source_command: {cmd_name}",
            f"source_skill: {skill_name}",
            f"component_count: {self.component_count}",
            f"total_lines: {self.total_lines}",
            "---",
            "",
            "# Component Manifest",
            "",
        ]
        if self.command is not None:
            lines.append(f"## Command (Tier 0)")
            lines.append(f"- **{self.command.name}**: {self.command.path} ({self.command.line_count} lines)")
            lines.append("")
        if self.skill is not None:
            lines.append(f"## Skill (Tier 1)")
            lines.append(f"- **{self.skill.name}**: {self.skill.path} ({self.skill.line_count} lines)")
            lines.append("")
        if self.agents:
            lines.append(f"## Agents (Tier 2)")
            for agent in self.agents:
                lines.append(f"- **{agent.name}**: {agent.path} ({agent.line_count} lines)")
            lines.append("")
        if self.component_count == 0:
            lines.append("No components discovered.")
            lines.append("")
        return "\n".join(lines)


# --- Monitor State ---


@dataclass
class PortifyMonitorState:
    """Live execution state for TUI rendering."""

    output_bytes: int = 0
    output_bytes_prev: int = 0
    last_growth_time: float = 0.0
    last_event_time: float = 0.0
    step_started_at: float = 0.0
    events_received: int = 0
    lines_total: int = 0
    growth_rate_bps: float = 0.0
    stall_seconds: float = 0.0
    current_step: str = ""
    current_iteration: int = 0

    @property
    def stall_status(self) -> str:
        if self.events_received == 0:
            elapsed = (
                time.time() - self.step_started_at if self.step_started_at else 0
            )
            return "waiting..." if elapsed < 30 else "STALLED"
        if self.stall_seconds > 120:
            return "STALLED"
        if self.stall_seconds > 30:
            return "thinking..."
        return "active"
