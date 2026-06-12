"""Configuration and data types for the head-to-head eval harness.

Gate-zero principle: nothing gets ported into the SuperClaude plugin until an
A/B against the corresponding *native* Claude Code behaviour shows it wins
beyond noise and is not a net loss on cost. This module fixes the knobs that
A/B depends on so they are explicit and pre-registered, not improvised.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# The model is pinned so an A/B varies ONLY the framework, never the model.
# Default is Fable 5 (the current frontier tier and the project's "Fable 5
# forward" target). Confirmed as the CLI default in claude 2.1.173.
DEFAULT_MODEL = "claude-fable-5"

# Headless execution edits files in a throwaway working copy, so we bypass
# permission prompts. Confirmed choice from `claude --permission-mode`.
PERMISSION_MODE = "bypassPermissions"

# Trials per (task, arm). LLM output is non-deterministic; a single run measures
# nothing. Kept low for smoke; raise for the real corpus.
DEFAULT_TRIALS = 5

# Hard ceiling on agent turns per task, so a stuck arm cannot run unbounded
# (SlopCodeBench: unbounded retry loops degrade sharpest).
DEFAULT_MAX_TURNS = 40


@dataclass(frozen=True)
class Arm:
    """One experimental condition.

    `A` (native baseline) carries no plugin_dir. `B_<comp>` points plugin_dir at
    a minimal single-component plugin under eval/variants/<comp>/ so exactly one
    candidate is isolated — no confounding with the rest of the framework.
    """

    name: str
    plugin_dir: Path | None = None  # None => native baseline

    @property
    def is_baseline(self) -> bool:
        return self.plugin_dir is None


@dataclass(frozen=True)
class Task:
    """A Terminal-Bench-shaped task: instruction + reproducible env + machine
    verifier + (optional) oracle. The agent only ever sees `environment/`; the
    verifier and oracle are isolated so the model cannot read the test."""

    id: str
    root: Path
    source: str  # self | swebench | terminalbench
    verify_image: str  # docker image that provides the verify runtime
    max_turns: int = DEFAULT_MAX_TURNS
    difficulty: str = "unknown"
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def prompt_file(self) -> Path:
        return self.root / "task.md"

    @property
    def environment_dir(self) -> Path:
        return self.root / "environment"

    @property
    def verify_script(self) -> Path:
        return self.root / "verify.sh"

    def prompt(self) -> str:
        return self.prompt_file.read_text()


@dataclass
class TrialResult:
    task_id: str
    arm: str
    trial: int
    passed: bool
    is_error: bool
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: int
    num_turns: int
    notes: str = ""

    def as_dict(self) -> dict:
        return self.__dict__.copy()
