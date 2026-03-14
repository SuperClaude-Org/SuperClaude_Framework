"""Click CLI commands for cli-portify pipeline.

Provides the ``superclaude cli-portify`` command group.

Per D-0002 Ownership Boundary 6 (CLI Integration): Click CLI group
and ``run`` subcommand.

v2.24.1: CLI argument changed from WORKFLOW_PATH to TARGET with
directory overrides and agent options (R-032 through R-035).
"""

from __future__ import annotations

import sys

import click

from .config import load_portify_config, validate_portify_config


@click.group("cli-portify")
def cli_portify_group():
    """Port inference-based workflows into programmatic CLI pipelines."""
    pass


@cli_portify_group.command("run")
@click.argument("target", type=click.Path(exists=True))
@click.option(
    "--output",
    "output_dir",
    default=None,
    type=click.Path(),
    help="Output directory for generated artifacts",
)
@click.option(
    "--cli-name",
    default="",
    help="Override derived CLI command name",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Validate and plan without executing Claude steps (halts after Step 2)",
)
@click.option(
    "--skip-review",
    is_flag=True,
    help="Skip interactive review gates",
)
@click.option(
    "--start",
    "start_step",
    default=None,
    help="Resume from a specific step (e.g. 'synthesize-spec')",
)
@click.option(
    "--max-convergence",
    default=3,
    type=int,
    help="Maximum convergence iterations for panel review (default: 3)",
)
@click.option(
    "--iteration-timeout",
    default=300,
    type=int,
    help="Per-iteration timeout in seconds (default: 300)",
)
@click.option(
    "--max-turns",
    default=100,
    type=int,
    help="Maximum turns per Claude subprocess (default: 100)",
)
@click.option("--model", default="", help="Claude model to use")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "--commands-dir",
    default=None,
    type=click.Path(exists=True),
    help="Override commands directory for resolution",
)
@click.option(
    "--skills-dir",
    default=None,
    type=click.Path(exists=True),
    help="Override skills directory for resolution",
)
@click.option(
    "--agents-dir",
    default=None,
    type=click.Path(exists=True),
    help="Override agents directory for resolution",
)
@click.option(
    "--include-agent",
    "include_agents_raw",
    multiple=True,
    default=(),
    help="Include additional agent(s) by name (repeatable)",
)
@click.option(
    "--save-manifest",
    "save_manifest_path",
    default=None,
    type=click.Path(),
    help="Save component manifest to specified path",
)
def run(
    target: str,
    output_dir: str | None,
    cli_name: str,
    dry_run: bool,
    skip_review: bool,
    start_step: str | None,
    max_convergence: int,
    iteration_timeout: int,
    max_turns: int,
    model: str,
    debug: bool,
    commands_dir: str | None,
    skills_dir: str | None,
    agents_dir: str | None,
    include_agents_raw: tuple[str, ...],
    save_manifest_path: str | None,
) -> None:
    """Execute the cli-portify pipeline on TARGET.

    TARGET is a command name, skill directory, skill name, or path to
    a SKILL.md file. Existing skill-directory invocations continue to
    work identically.
    """
    # Filter empty strings from --include-agent values
    include_agents = [a for a in include_agents_raw if a.strip()]

    config = load_portify_config(
        workflow_path=target,
        output_dir=output_dir,
        cli_name=cli_name,
        dry_run=dry_run,
        skip_review=skip_review,
        start_step=start_step,
        max_convergence=max_convergence,
        iteration_timeout=iteration_timeout,
        max_turns=max_turns,
        model=model,
        debug=debug,
        commands_dir=commands_dir,
        skills_dir=skills_dir,
        agents_dir=agents_dir,
        include_agents=include_agents or None,
        save_manifest_path=save_manifest_path,
    )

    # Validate configuration
    errors = validate_portify_config(config)
    if errors:
        for err in errors:
            click.echo(f"Error: {err}", err=True)
        sys.exit(1)

    if dry_run:
        _print_dry_run(config)
        return

    # Full execution deferred to Phase 3+
    click.echo(f"cli-portify: pipeline execution not yet implemented (start={start_step})")
    sys.exit(0)


def _print_dry_run(config) -> None:
    """Display execution plan without running."""
    click.echo("cli-portify dry-run plan:")
    click.echo(f"  Workflow: {config.workflow_path}")
    click.echo(f"  CLI name: {config.derive_cli_name()}")
    click.echo(f"  Output:   {config.output_dir}")
    click.echo(f"  Steps:    7 (Steps 3-7 require Claude)")
    click.echo(f"  Max convergence: {config.max_convergence}")
    click.echo(f"  Iteration timeout: {config.iteration_timeout}s")
