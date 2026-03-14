"""Step 1: validate-config — deterministic config validation.

Resolves workflow path, derives CLI name, validates output directory
writability, and detects name collisions. Runs without Claude subprocesses.

Produces: validate-config-result.json

Per SC-001: must complete under 1s for both valid and invalid inputs.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from superclaude.cli.cli_portify.config import validate_portify_config
from superclaude.cli.cli_portify.models import (
    ERR_BROKEN_ACTIVATION,
    WARN_MISSING_AGENTS,
    PortifyConfig,
    PortifyStatus,
    PortifyStepResult,
)


# --- Error Codes ---

ERR_INVALID_PATH = "ERR_INVALID_PATH"
ERR_MISSING_SKILL = "ERR_MISSING_SKILL"
ERR_OUTPUT_NOT_WRITABLE = "ERR_OUTPUT_NOT_WRITABLE"
ERR_NAME_COLLISION = "ERR_NAME_COLLISION"


@dataclass
class ValidateConfigResult:
    """Result of the validate-config step.

    v2.24.1: Extended with command_path, skill_dir, target_type,
    agent_count, and warnings fields (R-037).
    """

    valid: bool = True
    cli_name_kebab: str = ""
    cli_name_snake: str = ""
    workflow_path_resolved: str = ""
    output_dir: str = ""
    errors: list[dict[str, str]] = field(default_factory=list)
    duration_seconds: float = 0.0
    # v2.24.1 resolution metadata
    command_path: str = ""
    skill_dir: str = ""
    target_type: str = ""
    agent_count: int = 0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": "validate-config",
            "valid": self.valid,
            "cli_name_kebab": self.cli_name_kebab,
            "cli_name_snake": self.cli_name_snake,
            "workflow_path_resolved": self.workflow_path_resolved,
            "output_dir": self.output_dir,
            "errors": self.errors,
            "duration_seconds": self.duration_seconds,
            "command_path": self.command_path,
            "skill_dir": self.skill_dir,
            "target_type": self.target_type,
            "agent_count": self.agent_count,
            "warnings": self.warnings,
        }


def run_validate_config(
    config: PortifyConfig,
    output_dir: Path | None = None,
) -> tuple[ValidateConfigResult, PortifyStepResult]:
    """Execute the validate-config step.

    Args:
        config: Pipeline configuration to validate.
        output_dir: Directory to write the result JSON artifact.
            Defaults to config.results_dir.

    Returns:
        Tuple of (ValidateConfigResult, PortifyStepResult).
    """
    start = time.monotonic()
    result = ValidateConfigResult()

    # Run the 4 validation checks
    errors = _classify_errors(config)

    if errors:
        result.valid = False
        result.errors = errors
    else:
        # Derive names on success
        cli_name = config.derive_cli_name()
        result.cli_name_kebab = cli_name
        result.cli_name_snake = config.to_snake_case(cli_name)
        try:
            result.workflow_path_resolved = str(config.resolve_workflow_path())
        except (FileNotFoundError, ValueError):
            result.workflow_path_resolved = str(config.workflow_path)
        result.output_dir = str(config.output_dir)

        # v2.24.1 resolution metadata
        result.command_path = str(config.command_path) if config.command_path else ""
        result.skill_dir = str(config.workflow_path)
        result.target_type = config.target_type.value if config.target_type else ""
        if config.component_tree is not None:
            result.agent_count = len(config.component_tree.agents)

    # Warnings are non-fatal — always run regardless of errors
    result.warnings = _classify_warnings(config)

    elapsed = time.monotonic() - start
    result.duration_seconds = round(elapsed, 4)

    # Write artifact — try results_dir, fall back to work_dir or cwd
    artifact_dir = output_dir or config.results_dir
    artifact_path: Path | None = None
    for candidate in [artifact_dir, config.work_dir, Path(".")]:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            artifact_path = candidate / "validate-config-result.json"
            artifact_path.write_text(
                json.dumps(result.to_dict(), indent=2), encoding="utf-8"
            )
            break
        except OSError:
            continue

    if artifact_path is None:
        artifact_path = Path("validate-config-result.json")

    # Build step result
    step_result = PortifyStepResult(
        portify_status=PortifyStatus.PASS if result.valid else PortifyStatus.FAIL,
        step_name="validate-config",
        step_number=1,
        phase=1,
        artifact_path=str(artifact_path),
        gate_tier="EXEMPT",
    )

    return result, step_result


def _classify_errors(config: PortifyConfig) -> list[dict[str, str]]:
    """Run all 6 validation checks and classify each error.

    Checks 1-4 produce errors; checks 5-6 produce warnings that are
    non-fatal but reported in the validation result.

    Returns a list of dicts with 'code' and 'message' keys.
    """
    classified: list[dict[str, str]] = []

    # 1. Workflow path exists
    try:
        config.resolve_workflow_path()
    except FileNotFoundError as exc:
        classified.append({"code": ERR_INVALID_PATH, "message": str(exc)})
        # If path doesn't exist, remaining checks may still be meaningful
    except ValueError as exc:
        classified.append({"code": ERR_MISSING_SKILL, "message": str(exc)})

    # 2. Output directory writability
    try:
        config.check_output_writable()
    except PermissionError as exc:
        classified.append({"code": ERR_OUTPUT_NOT_WRITABLE, "message": str(exc)})

    # 3. Name collision
    collision = config.check_name_collision()
    if collision:
        classified.append({
            "code": ERR_NAME_COLLISION,
            "message": (
                f"CLI name '{collision}' collides with existing command. "
                f"Use --cli-name to specify a different name."
            ),
        })

    # 4 is implicit (covered by checks 1-3 above — no separate check needed)

    # 5. Command-to-skill link validity (R-038)
    if config.command_path is not None and config.command_path.exists():
        # If command_path is set but no skill_dir can be resolved, the link is broken
        skill_dir = config.workflow_path
        if not skill_dir.is_dir():
            classified.append({
                "code": ERR_BROKEN_ACTIVATION,
                "message": (
                    f"Command '{config.command_path}' has no linked skill directory. "
                    f"Workflow path '{skill_dir}' is not a valid directory."
                ),
            })

    return classified


def _classify_warnings(config: PortifyConfig) -> list[str]:
    """Run warning-only validation checks (checks 5b and 6).

    Returns a list of warning strings (non-fatal).
    """
    warnings: list[str] = []

    # 6. Referenced agent existence (R-039)
    if config.component_tree is not None:
        for agent in config.component_tree.agents:
            if not agent.found:
                warnings.append(
                    f"{WARN_MISSING_AGENTS}: {agent.name}"
                )

    return warnings
