"""Click CLI commands for Cleanup Audit pipeline.

Provides the `superclaude cleanup-audit` command group.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

import sys

import click

from .config import load_cleanup_audit_config
from .executor import execute_cleanup_audit


@click.group("cleanup-audit")
def cleanup_audit_group():
    """Multi-pass read-only repository audit with evidence-backed cleanup recommendations."""
    pass


@cleanup_audit_group.command("run")
@click.argument("target", default=".")
@click.option(
    "--pass",
    "pass_selection",
    default="all",
    type=click.Choice(["surface", "structural", "cross-cutting", "all"]),
    help="Which audit pass(es) to run",
)
@click.option(
    "--batch-size",
    default=20,
    type=int,
    help="Number of files per batch",
)
@click.option(
    "--focus",
    default="all",
    type=click.Choice(["infrastructure", "frontend", "backend", "all"]),
    help="Focus area for the audit",
)
@click.option(
    "--output",
    "output_dir",
    default=None,
    type=click.Path(),
    help="Output directory for audit results",
)
@click.option(
    "--max-turns",
    default=100,
    type=int,
    help="Maximum turns per subprocess",
)
@click.option("--model", default="", help="Claude model to use")
@click.option("--dry-run", is_flag=True, help="Show execution plan without running")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def run(
    target: str,
    pass_selection: str,
    batch_size: int,
    focus: str,
    output_dir: str | None,
    max_turns: int,
    model: str,
    dry_run: bool,
    debug: bool,
):
    """Execute the Cleanup Audit pipeline."""
    config = load_cleanup_audit_config(
        target=target,
        output_dir=output_dir,
        pass_selection=pass_selection,
        batch_size=batch_size,
        focus=focus,
        max_turns=max_turns,
        model=model,
        dry_run=dry_run,
        debug=debug,
    )

    if dry_run:
        _print_dry_run(config)
        return

    result = execute_cleanup_audit(config)
    sys.exit(0 if result.outcome.value == "success" else 1)


def _print_dry_run(config):
    """Display execution plan without running."""
    from rich.console import Console
    from rich.table import Table

    from .executor import _build_steps

    console = Console()
    table = Table(title="Cleanup Audit Pipeline Plan")
    table.add_column("Step", style="cyan")
    table.add_column("Pass Type", style="magenta")
    table.add_column("Output", style="green")
    table.add_column("Gate Tier", style="yellow")
    table.add_column("Timeout", style="dim")
    table.add_column("Agent", style="blue")

    for step in _build_steps(config):
        gate_tier = step.gate.enforcement_tier if step.gate else "EXEMPT"
        table.add_row(
            step.id,
            step.pass_type.value,
            str(step.output_file),
            gate_tier,
            f"{step.timeout_seconds}s",
            step.agent_type or "default",
        )

    console.print(table)
