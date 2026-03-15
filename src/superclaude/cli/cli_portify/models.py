"""Domain models for the CLI Portify pipeline.

Extends shared pipeline base types with CliPortify-specific status tracking,
configuration, and result telemetry.

Error code constants (Phase 2 — T02.07):
  NAME_COLLISION, OUTPUT_NOT_WRITABLE, AMBIGUOUS_PATH, INVALID_PATH, DERIVATION_FAILED

Target resolution types (from v2.24.1):
  TargetInputType, ResolvedTarget, ComponentEntry, ComponentInventory, ComponentTree,
  CommandEntry, SkillEntry, AgentEntry
  ERR_TARGET_NOT_FOUND, ERR_AMBIGUOUS_TARGET, ERR_BROKEN_ACTIVATION, WARN_MISSING_AGENTS
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Phase 2 T02.07: Error Code Constants
# ---------------------------------------------------------------------------

NAME_COLLISION: str = "NAME_COLLISION"
OUTPUT_NOT_WRITABLE: str = "OUTPUT_NOT_WRITABLE"
AMBIGUOUS_PATH: str = "AMBIGUOUS_PATH"
INVALID_PATH: str = "INVALID_PATH"
DERIVATION_FAILED: str = "DERIVATION_FAILED"

# Legacy / v2.24.1 target-resolution error constants
ERR_TARGET_NOT_FOUND: str = "ERR_TARGET_NOT_FOUND"
ERR_AMBIGUOUS_TARGET: str = "ERR_AMBIGUOUS_TARGET"
ERR_BROKEN_ACTIVATION: str = "ERR_BROKEN_ACTIVATION"
WARN_MISSING_AGENTS: str = "WARN_MISSING_AGENTS"


# ---------------------------------------------------------------------------
# Phase 2 T02.07: PortifyValidationError Base Exception
# ---------------------------------------------------------------------------


class PortifyValidationError(Exception):
    """Base exception for portify validation failures.

    Attributes:
        error_code: One of the 5 error code constants.
        details: Optional additional diagnostic information.
    """

    def __init__(self, error_code: str, message: str, details: str = "") -> None:
        self.error_code = error_code
        self.details = details
        super().__init__(f"[{error_code}] {message}" + (f" — {details}" if details else ""))


class NameCollisionError(PortifyValidationError):
    """Raised when the derived CLI name collides with an existing non-portified module."""

    def __init__(self, cli_name: str, existing_path: str = "") -> None:
        super().__init__(
            NAME_COLLISION,
            f"CLI name '{cli_name}' collides with an existing module that was not portified",
            existing_path,
        )


class OutputNotWritableError(PortifyValidationError):
    """Raised when the output destination is not writable."""

    def __init__(self, path: str) -> None:
        super().__init__(
            OUTPUT_NOT_WRITABLE,
            f"Output path is not writable: {path}",
        )


class AmbiguousPathError(PortifyValidationError):
    """Raised when a partial skill name matches multiple skill directories."""

    def __init__(self, name: str, candidates: list[str]) -> None:
        super().__init__(
            AMBIGUOUS_PATH,
            f"Ambiguous skill name '{name}': matches {candidates}",
            ", ".join(candidates),
        )


class InvalidPathError(PortifyValidationError):
    """Raised when the resolved path does not contain SKILL.md."""

    def __init__(self, path: str) -> None:
        super().__init__(
            INVALID_PATH,
            f"Path does not contain SKILL.md: {path}",
        )


class DerivationFailedError(PortifyValidationError):
    """Raised when automatic CLI name derivation yields an empty or invalid result."""

    def __init__(self, workflow_name: str) -> None:
        super().__init__(
            DERIVATION_FAILED,
            f"Could not derive a valid CLI name from workflow '{workflow_name}'. "
            "Use --name to provide an explicit name.",
        )


# ---------------------------------------------------------------------------
# Phase 3 T03.01: PortifyPhaseType enum
# ---------------------------------------------------------------------------


class PortifyPhaseType(Enum):
    """Pipeline phase classification for dry-run filtering (SC-012)."""

    PREREQUISITES = "PREREQUISITES"
    ANALYSIS = "ANALYSIS"
    USER_REVIEW = "USER_REVIEW"
    SPECIFICATION = "SPECIFICATION"
    SYNTHESIS = "SYNTHESIS"
    CONVERGENCE = "CONVERGENCE"


# ---------------------------------------------------------------------------
# Phase 3 T03.01: ConvergenceState enum
# ---------------------------------------------------------------------------


class ConvergenceState(Enum):
    """State of the convergence loop for iterative review steps."""

    NOT_STARTED = "NOT_STARTED"
    REVIEWING = "REVIEWING"
    INCORPORATING = "INCORPORATING"
    SCORING = "SCORING"
    CONVERGED = "CONVERGED"
    ESCALATED = "ESCALATED"


# ---------------------------------------------------------------------------
# PortifyStatus
# ---------------------------------------------------------------------------


class PortifyStatus(Enum):
    """Step-level status for the CLI Portify pipeline."""

    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    PASS_NO_SIGNAL = "pass_no_signal"
    PASS_NO_REPORT = "pass_no_report"
    INCOMPLETE = "incomplete"
    HALT = "halt"
    TIMEOUT = "timeout"
    ERROR = "error"
    FAIL = "fail"
    SKIPPED = "skipped"


# ---------------------------------------------------------------------------
# FailureClassification
# ---------------------------------------------------------------------------


class FailureClassification(Enum):
    """Classification of failure types for the portify pipeline."""

    MISSING_ARTIFACT = "missing_artifact"
    MALFORMED_FRONTMATTER = "malformed_frontmatter"
    TIMEOUT = "timeout"
    PARTIAL_ARTIFACT = "partial_artifact"
    BUDGET_EXHAUSTION = "budget_exhaustion"
    USER_REJECTION = "user_rejection"
    GATE_FAILURE = "gate_failure"


# ---------------------------------------------------------------------------
# TargetInputType
# ---------------------------------------------------------------------------


class TargetInputType(Enum):
    """Classification of the input form provided by the user."""

    COMMAND_NAME = "command_name"
    COMMAND_PATH = "command_path"
    SKILL_DIR = "skill_dir"
    SKILL_NAME = "skill_name"
    SKILL_FILE = "skill_file"


# ---------------------------------------------------------------------------
# ResolvedTarget
# ---------------------------------------------------------------------------


@dataclass
class ResolvedTarget:
    """The fully-resolved input target after path resolution.

    Attributes:
        input_form: Raw user input string (command name, path, etc.)
        input_type: Classification of how the input was interpreted.
        command_path: Resolved path to the command .md file (if any).
        skill_dir: Resolved path to the skill directory (if any).
        project_root: Project root directory.
        commands_dir: Resolved commands directory.
        skills_dir: Resolved skills directory.
        agents_dir: Resolved agents directory.
    """

    input_form: str
    input_type: TargetInputType
    command_path: Optional[Path] = None
    skill_dir: Optional[Path] = None
    project_root: Optional[Path] = None
    commands_dir: Optional[Path] = None
    skills_dir: Optional[Path] = None
    agents_dir: Optional[Path] = None


# ---------------------------------------------------------------------------
# Component Entries
# ---------------------------------------------------------------------------


@dataclass
class ComponentEntry:
    """A single component discovered during inventory scan."""

    name: str = ""
    path: str = ""
    component_type: str = ""
    line_count: int = 0
    purpose: str = ""


@dataclass
class CommandEntry:
    """A command-tier component (Tier 0)."""

    name: str = ""
    path: Optional[Path] = None
    line_count: int = 0
    source_dir: Optional[Path] = None
    tier: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.tier = 0


@dataclass
class SkillEntry:
    """A skill-tier component (Tier 1)."""

    name: str = ""
    path: Optional[Path] = None
    line_count: int = 0
    source_dir: Optional[Path] = None
    tier: int = field(default=1, init=False)

    def __post_init__(self) -> None:
        self.tier = 1


@dataclass
class AgentEntry:
    """An agent-tier component (Tier 2)."""

    name: str = ""
    path: Optional[Path] = None
    line_count: int = 0
    source_dir: Optional[Path] = None
    found: bool = False
    referenced_in: str = "auto"
    tier: int = field(default=2, init=False)

    def __post_init__(self) -> None:
        self.tier = 2


# ---------------------------------------------------------------------------
# ComponentInventory
# ---------------------------------------------------------------------------


@dataclass
class ComponentInventory:
    """Flat list inventory produced by component discovery."""

    components: list[ComponentEntry] = field(default_factory=list)
    source_skill: str = ""
    source_command: str = ""

    @property
    def component_count(self) -> int:
        return len(self.components)

    @property
    def total_lines(self) -> int:
        return sum(c.line_count for c in self.components)


# ---------------------------------------------------------------------------
# ComponentTree
# ---------------------------------------------------------------------------


@dataclass
class ComponentTree:
    """Tiered component tree assembled from resolution results.

    Tier 0 — command (.md file)
    Tier 1 — skill (SKILL.md + supporting files)
    Tier 2 — agents (referenced agent .md files)
    """

    command: Optional[CommandEntry] = None
    skill: Optional[SkillEntry] = None
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
        for agent in self.agents:
            total += agent.line_count
        return total

    @property
    def all_source_dirs(self) -> list[Path]:
        dirs: list[Path] = []
        seen: set[Path] = set()
        for entry in [self.command, self.skill, *self.agents]:
            if entry is not None and entry.source_dir is not None:
                if entry.source_dir not in seen:
                    seen.add(entry.source_dir)
                    dirs.append(entry.source_dir)
        return dirs

    def to_flat_inventory(self) -> ComponentInventory:
        """Convert the tiered tree to a flat ComponentInventory."""
        components: list[ComponentEntry] = []
        source_skill = ""
        source_command = ""

        if self.command is not None:
            source_command = self.command.name
            components.append(
                ComponentEntry(
                    name=self.command.name,
                    path=str(self.command.path) if self.command.path else "",
                    component_type="command",
                    line_count=self.command.line_count,
                    purpose="command entry point",
                )
            )

        if self.skill is not None:
            source_skill = self.skill.name
            components.append(
                ComponentEntry(
                    name=self.skill.name,
                    path=str(self.skill.path) if self.skill.path else "",
                    component_type="skill",
                    line_count=self.skill.line_count,
                    purpose="skill definition",
                )
            )

        for agent in self.agents:
            components.append(
                ComponentEntry(
                    name=agent.name,
                    path=str(agent.path) if agent.path else "",
                    component_type="agent",
                    line_count=agent.line_count,
                    purpose="agent definition",
                )
            )

        return ComponentInventory(
            components=components,
            source_skill=source_skill,
            source_command=source_command,
        )

    def to_manifest_markdown(self) -> str:
        """Render a Markdown manifest with YAML frontmatter."""
        source_command = self.command.name if self.command else ""
        source_skill = self.skill.name if self.skill else ""

        lines = [
            "---",
            f"source_command: {source_command}",
            f"source_skill: {source_skill}",
            f"component_count: {self.component_count}",
            f"total_lines: {self.total_lines}",
            "---",
            "",
        ]

        if self.component_count == 0:
            lines.append("No components discovered.")
            return "\n".join(lines)

        if self.command is not None:
            lines += [
                "## Command (Tier 0)",
                f"- **{self.command.name}** ({self.command.line_count} lines)",
                "",
            ]

        if self.skill is not None:
            lines += [
                "## Skill (Tier 1)",
                f"- **{self.skill.name}** ({self.skill.line_count} lines)",
                "",
            ]

        if self.agents:
            lines += ["## Agents (Tier 2)"]
            for agent in self.agents:
                status = "found" if agent.found else "missing"
                lines.append(f"- **{agent.name}** ({agent.line_count} lines) [{status}]")
            lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# ResumeContext
# ---------------------------------------------------------------------------


@dataclass
class ResumeContext:
    """Context needed to resume a failed step."""

    resume_command: str = ""
    resume_step: str = ""
    resume_phase: int = 0


# ---------------------------------------------------------------------------
# PortifyStepResult
# ---------------------------------------------------------------------------


@dataclass
class PortifyStepResult:
    """Result of executing a single CLI Portify pipeline step."""

    step_name: str = ""
    step_number: int = 0
    phase: int = 0
    portify_status: PortifyStatus = PortifyStatus.PENDING
    failure_classification: Optional[FailureClassification] = None
    gate_tier: str = "STANDARD"
    artifact_path: str = ""
    resume_context: ResumeContext = field(default_factory=ResumeContext)
    iteration_number: int = 0
    iteration_timeout: int = 0
    error_message: str = ""
    duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# PortifyConfig
# ---------------------------------------------------------------------------


@dataclass
class PortifyConfig:
    """Configuration for a cli-portify pipeline run.

    Stores all resolved paths and user overrides needed to execute
    the full 12-step portification pipeline.
    """

    workflow_path: Path = field(default_factory=lambda: Path("."))
    cli_name: str = ""
    output_dir: Optional[Path] = None
    workdir_path: Optional[Path] = None

    # Optional CLI-override directories
    commands_dir: Optional[Path] = None
    skills_dir: Optional[Path] = None
    agents_dir: Optional[Path] = None

    # Agent selection
    include_agents: bool = False
    _include_agents_list: list[str] = field(default_factory=list)

    # Manifest output
    save_manifest_path: Optional[Path] = None

    # Raw target input (for resolution)
    target_input: str = ""

    # Optional resolved command path (populated by resolution step)
    command_path: Optional[Path] = None

    # Optional component tree (populated by discover step)
    component_tree: Optional["ComponentTree"] = None

    # Pipeline options
    dry_run: bool = False
    debug: bool = False
    max_turns: int = 200
    model: str = ""
    stall_timeout: int = 300

    def derive_cli_name(self) -> str:
        """Return the CLI name: explicit override or derived from workflow dir name.

        Derivation: strip sc- prefix, strip -protocol suffix, normalize to kebab-case.
        Raises DerivationFailedError if derivation yields empty string.
        """
        if self.cli_name:
            return self.cli_name
        return _derive_name_from_path(self.workflow_path)

    def resolve_workflow_path(self) -> Path:
        """Resolve workflow_path: if a file, return parent dir."""
        p = self.workflow_path
        if p.is_file():
            return p.parent
        return p

    @staticmethod
    def to_snake_case(kebab: str) -> str:
        """Convert a kebab-case string to snake_case."""
        return kebab.replace("-", "_")


# ---------------------------------------------------------------------------
# Phase 3 T03.01: PortifyOutcome enum
# ---------------------------------------------------------------------------


class PortifyOutcome(Enum):
    """Pipeline-level outcome classification (return contract)."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"
    INTERRUPTED = "INTERRUPTED"
    HALTED = "HALTED"
    DRY_RUN = "DRY_RUN"


# ---------------------------------------------------------------------------
# Phase 3 T03.01: PortifyStep dataclass
# ---------------------------------------------------------------------------


@dataclass
class PortifyStep:
    """A single step in the CLI Portify pipeline (extends Step contract).

    Extends pipeline base types per AC-003 / NFR-016.
    """

    step_id: str = ""
    phase_type: PortifyPhaseType = PortifyPhaseType.PREREQUISITES
    prompt: str = ""
    output_file: Optional[Path] = None
    error_file: Optional[Path] = None
    timeout_seconds: int = 300
    retry_limit: int = 1
    artifact_refs: list = field(default_factory=list)
    status: PortifyStatus = PortifyStatus.PENDING


# ---------------------------------------------------------------------------
# Phase 3 T03.01: MonitorState dataclass
# ---------------------------------------------------------------------------


@dataclass
class MonitorState:
    """Live telemetry captured by the OutputMonitor (NFR-009)."""

    output_bytes: int = 0
    growth_rate_bps: float = 0.0
    stall_seconds: float = 0.0
    events: int = 0
    line_count: int = 0
    convergence_iteration: int = 0
    findings_count: int = 0
    placeholder_count: int = 0


# ---------------------------------------------------------------------------
# Phase 3 T03.01: TurnLedger (executor-internal budget tracker, OQ-001)
# ---------------------------------------------------------------------------


class TurnLedger:
    """Tracks turn budget for Claude-assisted steps.

    One "turn" = one Claude subprocess invocation (including retries).
    can_launch() must return False when remaining turns are insufficient,
    triggering a HALTED outcome (FR-040).
    """

    def __init__(self, total_budget: int) -> None:
        self._total_budget: int = total_budget
        self._consumed: int = 0

    @property
    def total_budget(self) -> int:
        return self._total_budget

    @property
    def consumed(self) -> int:
        return self._consumed

    @property
    def remaining(self) -> int:
        return max(0, self._total_budget - self._consumed)

    def consume(self, turns: int = 1) -> None:
        """Record that `turns` turns were consumed."""
        self._consumed += turns

    def can_launch(self) -> bool:
        """Return True if at least one turn remains."""
        return self.remaining > 0

    def reset(self) -> None:
        """Reset consumed turns (for testing only)."""
        self._consumed = 0


def _derive_name_from_path(workflow_path: Path) -> str:
    """Derive CLI module name from a workflow directory path.

    Algorithm:
      1. Take directory name (not full path).
      2. Strip leading 'sc-' prefix (case-insensitive).
      3. Strip trailing '-protocol' suffix (case-insensitive).
      4. Normalize to lowercase kebab-case.
      5. If result is empty, raise DerivationFailedError.
    """
    name = workflow_path.name if workflow_path.is_file() else workflow_path.name
    # Normalize to lowercase
    name = name.lower()
    # Strip sc- prefix
    if name.startswith("sc-"):
        name = name[3:]
    # Strip -protocol suffix
    if name.endswith("-protocol"):
        name = name[: -len("-protocol")]
    # Normalize: keep only lowercase letters, digits, hyphens
    import re
    name = re.sub(r"[^a-z0-9-]", "-", name)
    # Collapse multiple hyphens
    name = re.sub(r"-+", "-", name).strip("-")

    if not name:
        raise DerivationFailedError(workflow_path.name)
    return name
