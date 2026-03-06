"""Roadmap CLI commands -- Click command group for ``superclaude roadmap``.

Defines the ``superclaude roadmap`` command with all flags per spec FR-009.
"""

from __future__ import annotations

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
    default=50,
    help="Max agent turns per claude subprocess. Default: 50.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging to output_dir/roadmap-debug.log.",
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
    )

    execute_roadmap(config, resume=resume)
