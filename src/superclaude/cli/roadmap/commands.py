"""Roadmap CLI commands -- Click command group for ``superclaude roadmap``.

Defines the ``superclaude roadmap`` command with all flags per spec FR-009.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click


@click.group("roadmap")
def roadmap_group():
    """Generate project roadmaps from specification files.

    Orchestrates an 8-step pipeline: extract, generate (x2 parallel),
    diff, debate, score, merge, and test-strategy. Each step runs as
    a fresh Claude subprocess with file-on-disk gates between steps.

    Examples:
        superclaude roadmap run spec.md
        superclaude roadmap run spec.md --agents sonnet:security,haiku:qa
        superclaude roadmap run spec.md --depth deep
        superclaude roadmap run spec.md --dry-run
        superclaude roadmap run spec.md --resume
    """
    pass


@roadmap_group.command()
@click.argument("spec_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--agents",
    default="opus:architect,haiku:architect",
    help=(
        "Comma-separated agent specs: model[:persona]. "
        "Default: opus:architect,haiku:architect"
    ),
)
@click.option(
    "--output",
    "output_dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory for all artifacts. Default: parent dir of spec-file.",
)
@click.option(
    "--depth",
    type=click.Choice(["quick", "standard", "deep"], case_sensitive=False),
    default="standard",
    help="Debate round depth: quick=1, standard=2, deep=3. Default: standard.",
)
@click.option(
    "--resume",
    is_flag=True,
    help=(
        "Skip steps whose outputs already pass their gates. "
        "Re-run from the first failing step."
    ),
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print step plan and gate criteria, then exit without launching subprocesses.",
)
@click.option(
    "--model",
    default="",
    help="Override model for all steps. Default: per-agent model for generate steps.",
)
@click.option(
    "--max-turns",
    type=int,
    default=100,
    help="Max agent turns per claude subprocess. Default: 100.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging to output_dir/roadmap-debug.log.",
)
@click.option(
    "--no-validate",
    is_flag=True,
    help="Skip post-pipeline validation step.",
)
@click.option(
    "--retrospective",
    type=click.Path(exists=False, path_type=Path),
    default=None,
    help=(
        "Path to a retrospective file from a prior release cycle. "
        "Content is framed as advisory 'areas to watch' in extraction. "
        "Missing file is not an error -- extraction proceeds normally."
    ),
)
def run(
    spec_file: Path,
    agents: str,
    output_dir: Path | None,
    depth: str,
    resume: bool,
    dry_run: bool,
    model: str,
    max_turns: int,
    debug: bool,
    no_validate: bool,
    retrospective: Path | None,
) -> None:
    """Run the roadmap generation pipeline on SPEC_FILE.

    SPEC_FILE is the path to a specification markdown file.
    """
    from .executor import execute_roadmap
    from .models import AgentSpec, RoadmapConfig

    # Parse agents
    agent_specs = [AgentSpec.parse(a.strip()) for a in agents.split(",")]

    # Resolve output directory
    resolved_output = output_dir if output_dir is not None else spec_file.parent

    # Resolve retrospective file (missing file is not an error)
    retro_path = None
    if retrospective is not None:
        retro_path = Path(retrospective).resolve()
        if not retro_path.is_file():
            click.echo(
                f"[roadmap] Retrospective file not found: {retro_path} "
                "(proceeding without retrospective context)",
                err=True,
            )
            retro_path = None

    config = RoadmapConfig(
        spec_file=spec_file.resolve(),
        agents=agent_specs,
        depth=depth,
        output_dir=resolved_output.resolve(),
        work_dir=resolved_output.resolve(),
        dry_run=dry_run,
        max_turns=max_turns,
        model=model,
        debug=debug,
        retrospective_file=retro_path,
    )

    execute_roadmap(config, resume=resume, no_validate=no_validate)


@roadmap_group.command("accept-spec-change")
@click.argument("output_dir", type=click.Path(exists=True, path_type=Path))
def accept_spec_change(output_dir: Path) -> None:
    """Update spec_hash after accepted deviation records.

    When the spec file is edited to formalize an accepted deviation
    (documentation sync, not a functional change), this command updates
    the stored spec_hash so --resume can proceed without a full cascade.

    Requires at least one dev-*-accepted-deviation.md file with
    disposition: ACCEPTED and spec_update_required: true as evidence.

    OUTPUT_DIR is the directory containing .roadmap-state.json.

    Examples:
        superclaude roadmap accept-spec-change ./output
    """
    from .spec_patch import prompt_accept_spec_change

    sys.exit(prompt_accept_spec_change(output_dir.resolve()))


@roadmap_group.command()
@click.argument("output_dir", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--agents",
    default="opus:architect",
    help=(
        "Comma-separated agent specs: model[:persona]. "
        "Default: opus:architect (single-agent for cost efficiency)."
    ),
)
@click.option(
    "--model",
    default="",
    help="Override model for all validation steps.",
)
@click.option(
    "--max-turns",
    type=int,
    default=100,
    help="Max agent turns per claude subprocess. Default: 100.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging.",
)
def validate(
    output_dir: Path,
    agents: str,
    model: str,
    max_turns: int,
    debug: bool,
) -> None:
    """Validate roadmap pipeline outputs in OUTPUT_DIR.

    OUTPUT_DIR must contain roadmap.md, test-strategy.md, and extraction.md
    from a prior ``roadmap run``.

    Examples:
        superclaude roadmap validate ./output
        superclaude roadmap validate ./output --agents opus:architect,haiku:qa
    """
    from .models import AgentSpec, ValidateConfig
    from .validate_executor import execute_validate

    agent_specs = [AgentSpec.parse(a.strip()) for a in agents.split(",")]

    config = ValidateConfig(
        output_dir=output_dir.resolve(),
        agents=agent_specs,
        work_dir=output_dir.resolve(),
        max_turns=max_turns,
        model=model,
        debug=debug,
    )

    counts = execute_validate(config)

    # Surface results as CLI output (exit 0 per NFR-006)
    blocking = counts.get("blocking_count", 0)
    warning = counts.get("warning_count", 0)
    info = counts.get("info_count", 0)

    if blocking > 0:
        click.echo(
            click.style(
                f"WARNING: {blocking} blocking issue(s) found", fg="yellow"
            )
        )
    if warning > 0:
        click.echo(f"Warnings: {warning}")
    if info > 0:
        click.echo(f"Info: {info}")

    click.echo(
        f"\n[validate] Complete: {blocking} blocking, {warning} warning, {info} info"
    )
