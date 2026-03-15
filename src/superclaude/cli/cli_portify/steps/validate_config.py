"""Step 1: validate-config — deterministic input validation (Step 0 equivalent).

Validates PortifyConfig without invoking Claude. Emits a JSON artifact.
Enforces SC-001: completes in <30s (in practice <1s for filesystem checks).

Error codes (per spec):
  ERR_INVALID_PATH        — workflow path does not exist
  ERR_MISSING_SKILL       — SKILL.md not found at resolved path
  ERR_OUTPUT_NOT_WRITABLE — output dir cannot be created or is not writable
  ERR_NAME_COLLISION      — derived CLI name collides with existing module
  ERR_BROKEN_ACTIVATION   — command_path set but workflow path is not a valid dir
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..config import validate_portify_config
from ..models import (
    ERR_BROKEN_ACTIVATION,
    WARN_MISSING_AGENTS,
    PortifyConfig,
    PortifyStatus,
    PortifyStepResult,
)

# Step-level error code constants
ERR_INVALID_PATH: str = "ERR_INVALID_PATH"
ERR_MISSING_SKILL: str = "ERR_MISSING_SKILL"
ERR_OUTPUT_NOT_WRITABLE: str = "ERR_OUTPUT_NOT_WRITABLE"
ERR_NAME_COLLISION: str = "ERR_NAME_COLLISION"

STEP_NAME = "validate-config"
STEP_NUMBER = 1
PHASE = 1
GATE_TIER = "EXEMPT"

# Steps that support --start resume
_RESUMABLE_STEPS = {"brainstorm-gaps", "synthesize-spec", "panel-review"}


@dataclass
class ValidateConfigResult:
    """Structured output of the validate-config step.

    Contains 13 fields (exactly) in to_dict() output.
    """

    valid: bool = False
    cli_name_kebab: str = ""
    cli_name_snake: str = ""
    workflow_path_resolved: str = ""
    output_dir: str = ""
    errors: list[dict[str, str]] = field(default_factory=list)
    duration_seconds: float = 0.0
    # v2.24.1 fields
    command_path: str = ""
    skill_dir: str = ""
    target_type: str = ""
    agent_count: int = 0
    warnings: list[str] = field(default_factory=list)
    step: str = STEP_NAME

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-serializable dict with exactly 13 fields."""
        return {
            "step": self.step,
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
    output_dir: Optional[Path] = None,
) -> tuple[ValidateConfigResult, PortifyStepResult]:
    """Execute the validate-config step.

    Returns:
        (ValidateConfigResult, PortifyStepResult) tuple.

    Does not invoke Claude. All checks are pure Python filesystem operations.
    """
    start = time.monotonic()
    errors: list[dict[str, str]] = []
    warnings: list[str] = []

    # --- Check 1: Workflow path existence ---
    resolved_path = ""
    try:
        resolved = config.resolve_workflow_path()
        resolved_path = str(resolved)
    except Exception as exc:
        errors.append({"code": ERR_INVALID_PATH, "message": str(exc)})
        resolved = None

    if resolved is not None and not resolved.exists():
        errors.append({
            "code": ERR_INVALID_PATH,
            "message": f"Workflow path does not exist: {resolved}",
        })
        resolved = None  # Skip remaining path-dependent checks

    # --- Check 2: SKILL.md ---
    skill_dir_str = ""
    if resolved is not None:
        skill_md = resolved / "SKILL.md"
        if not skill_md.exists():
            errors.append({
                "code": ERR_MISSING_SKILL,
                "message": f"SKILL.md not found at {resolved}",
            })
        else:
            skill_dir_str = str(resolved)

    # --- Check 3: Output directory writability ---
    if config.output_dir is not None:
        out_path = config.output_dir
        if out_path.exists() and not os.access(out_path, os.W_OK):
            errors.append({
                "code": ERR_OUTPUT_NOT_WRITABLE,
                "message": f"Output path is not writable: {out_path}",
            })
        elif not out_path.exists():
            try:
                out_path.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as exc:
                errors.append({
                    "code": ERR_OUTPUT_NOT_WRITABLE,
                    "message": f"Cannot create output directory {out_path}: {exc}",
                })

    # --- Check 4: Name collision ---
    cli_name_kebab = ""
    cli_name_snake = ""
    try:
        cli_name_kebab = config.derive_cli_name()
        cli_name_snake = config.to_snake_case(cli_name_kebab)
    except Exception as exc:
        errors.append({"code": ERR_NAME_COLLISION, "message": str(exc)})

    if cli_name_kebab:
        # Use the same collision check as validate_portify_config
        from ..config import _check_collision
        collision_errors = _check_collision(cli_name_kebab, config)
        for msg in collision_errors:
            errors.append({"code": ERR_NAME_COLLISION, "message": msg})

    # --- Check 5: Broken activation (command_path set but skill dir invalid) ---
    cmd_path_str = ""
    command_path = getattr(config, "command_path", None)
    if command_path is not None:
        cmd_path_str = str(command_path)
        # When command_path is set, verify the workflow path resolves to a
        # directory that contains SKILL.md (i.e., a valid skill directory).
        if resolved is None:
            errors.append({
                "code": ERR_BROKEN_ACTIVATION,
                "message": "command_path set but workflow path could not be resolved",
            })
        elif not resolved.is_dir():
            errors.append({
                "code": ERR_BROKEN_ACTIVATION,
                "message": (
                    f"command_path is set but workflow path '{resolved}' "
                    "is not a valid skill directory"
                ),
            })
        elif not (resolved / "SKILL.md").exists():
            # SKILL.md missing but also command_path set → broken activation
            # (ERR_MISSING_SKILL may already be in errors, but also report broken link)
            errors.append({
                "code": ERR_BROKEN_ACTIVATION,
                "message": (
                    f"command_path is set but workflow path '{resolved}' "
                    "does not contain SKILL.md"
                ),
            })

    # --- Check 6: Missing agents (non-fatal warnings) ---
    agent_count = 0
    component_tree = getattr(config, "component_tree", None)
    if component_tree is not None:
        all_agents = getattr(component_tree, "agents", [])
        agent_count = len(all_agents)
        for agent in all_agents:
            if not agent.found:
                warnings.append(f"{WARN_MISSING_AGENTS}: {agent.name}")

    # --- Determine validity ---
    valid = len(errors) == 0

    # --- Build result ---
    elapsed = time.monotonic() - start
    result = ValidateConfigResult(
        valid=valid,
        cli_name_kebab=cli_name_kebab,
        cli_name_snake=cli_name_snake,
        workflow_path_resolved=resolved_path,
        output_dir=str(config.output_dir) if config.output_dir else "",
        errors=errors,
        duration_seconds=elapsed,
        command_path=cmd_path_str,
        skill_dir=skill_dir_str,
        target_type="",  # Populated by resolution step if available
        agent_count=agent_count,
        warnings=warnings,
    )

    # --- Write artifact ---
    artifact_path = _write_artifact(result, config, output_dir)

    step_result = PortifyStepResult(
        step_name=STEP_NAME,
        step_number=STEP_NUMBER,
        phase=PHASE,
        portify_status=PortifyStatus.PASS if valid else PortifyStatus.FAIL,
        gate_tier=GATE_TIER,
        artifact_path=artifact_path,
        duration_seconds=elapsed,
    )

    return result, step_result


def _write_artifact(
    result: ValidateConfigResult,
    config: PortifyConfig,
    output_dir: Optional[Path],
) -> str:
    """Write validate-config-result.json to the output directory.

    Falls back to a temp directory if neither output_dir nor config.output_dir
    is accessible.
    """
    import tempfile

    # Determine write location
    write_dir: Optional[Path] = None
    if output_dir is not None:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            write_dir = output_dir
        except OSError:
            pass

    if write_dir is None and config.output_dir is not None:
        try:
            config.output_dir.mkdir(parents=True, exist_ok=True)
            write_dir = config.output_dir
        except OSError:
            pass

    if write_dir is None:
        write_dir = Path(tempfile.mkdtemp())

    artifact_path = write_dir / "validate-config-result.json"
    try:
        artifact_path.write_text(json.dumps(result.to_dict(), indent=2))
    except OSError:
        artifact_path = Path(tempfile.mkdtemp()) / "validate-config-result.json"
        artifact_path.write_text(json.dumps(result.to_dict(), indent=2))

    return str(artifact_path)


def _classify_warnings(component_tree: Any) -> list[str]:
    """Classify agent warnings from a component tree.

    Returns list of warning strings in format: 'WARN_MISSING_AGENTS: <name>'
    """
    warnings: list[str] = []
    if component_tree is None:
        return warnings
    for agent in getattr(component_tree, "agents", []):
        if not agent.found:
            warnings.append(f"{WARN_MISSING_AGENTS}: {agent.name}")
    return warnings
