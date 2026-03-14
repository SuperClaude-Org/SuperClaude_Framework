"""Configuration loading and validation for cli-portify pipeline.

Handles CLI argument resolution, workflow path validation, and
config construction.

Per D-0002 Ownership Boundary 1: config validation step including
workflow path resolution, CLI name derivation, output-dir writability,
and collision detection.

v2.24.1: Extended with target, commands_dir, skills_dir, agents_dir,
include_agents, save_manifest_path parameters (R-036, R-037).
"""

from __future__ import annotations

from pathlib import Path

from .models import PortifyConfig


def load_portify_config(
    workflow_path: str | Path,
    output_dir: str | Path | None = None,
    cli_name: str = "",
    dry_run: bool = False,
    skip_review: bool = False,
    start_step: str | None = None,
    max_convergence: int = 3,
    iteration_timeout: int = 300,
    max_turns: int = 100,
    model: str = "",
    debug: bool = False,
    commands_dir: str | Path | None = None,
    skills_dir: str | Path | None = None,
    agents_dir: str | Path | None = None,
    include_agents: list[str] | None = None,
    save_manifest_path: str | Path | None = None,
) -> PortifyConfig:
    """Construct and validate pipeline configuration from CLI arguments.

    Args:
        workflow_path: Target path (directory, file, or name).
        output_dir: Output directory for artifacts.
        cli_name: Override CLI command name.
        dry_run: Validate-only mode.
        skip_review: Skip interactive review gates.
        start_step: Resume from specific step.
        max_convergence: Max convergence iterations.
        iteration_timeout: Per-iteration timeout.
        max_turns: Max Claude subprocess turns.
        model: Claude model override.
        debug: Enable debug logging.
        commands_dir: Override commands directory.
        skills_dir: Override skills directory.
        agents_dir: Override agents directory.
        include_agents: Additional agent names from CLI.
        save_manifest_path: Path to save component manifest.
    """
    wf_path = Path(workflow_path).resolve()

    # Default output dir: sibling of workflow path
    if output_dir is None:
        resolved_output = wf_path.parent / f"{wf_path.name}-output"
    else:
        resolved_output = Path(output_dir).resolve()

    config = PortifyConfig(
        workflow_path=wf_path,
        output_dir=resolved_output,
        work_dir=resolved_output,
        cli_name=cli_name,
        dry_run=dry_run,
        skip_review=skip_review,
        start_step=start_step,
        max_convergence=max_convergence,
        iteration_timeout=iteration_timeout,
        max_turns=max_turns,
        model=model,
        debug=debug,
        target_input=str(workflow_path),
        commands_dir=Path(commands_dir).resolve() if commands_dir else None,
        skills_dir=Path(skills_dir).resolve() if skills_dir else None,
        agents_dir=Path(agents_dir).resolve() if agents_dir else None,
        include_agents=include_agents is not None,
        save_manifest_path=Path(save_manifest_path).resolve() if save_manifest_path else None,
    )

    # Store the raw include_agents list for later deduplication
    config._include_agents_list = include_agents

    return config


def validate_portify_config(config: PortifyConfig) -> list[str]:
    """Validate a PortifyConfig, returning a list of error messages.

    Validates:
    1. Workflow path exists
    2. SKILL.md is present
    3. Output directory is writable
    4. No CLI name collision

    Returns:
        Empty list if valid, otherwise list of error descriptions.
    """
    errors: list[str] = []

    # 1. Workflow path resolution
    try:
        config.resolve_workflow_path()
    except FileNotFoundError as exc:
        errors.append(str(exc))
    except ValueError as exc:
        errors.append(str(exc))

    # 2. Output directory writability
    try:
        config.check_output_writable()
    except PermissionError as exc:
        errors.append(str(exc))

    # 3. Name collision detection
    collision = config.check_name_collision()
    if collision:
        errors.append(
            f"CLI name '{collision}' collides with existing command. "
            f"Use --cli-name to specify a different name."
        )

    return errors
