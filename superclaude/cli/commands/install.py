"""
SuperClaude install command - Modern interactive installation with rich UI
"""

import typer
from typing import Optional, List
from pathlib import Path
from rich.panel import Panel
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from superclaude.cli._console import console

# Create install command group
app = typer.Typer(name="install", help="Install SuperClaude framework components")


@app.command("all")
def install_all(
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        "-y",
        help="Non-interactive installation with default configuration",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        help="Installation profile: api (with API keys), noapi (without), or custom",
    ),
    install_dir: Path = typer.Option(
        Path.home() / ".claude",
        "--install-dir",
        help="Installation directory",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force reinstallation of existing components",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Simulate installation without making changes",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output with detailed logging",
    ),
):
    """
    Install SuperClaude with all recommended components

    This command installs the complete SuperClaude framework including:
    - Core framework files and documentation
    - Behavioral modes (7 modes)
    - Slash commands (26 commands)
    - Specialized agents (17 agents)
    - MCP server integrations (optional)
    """
    # Display installation header
    console.print(
        Panel.fit(
            "[bold cyan]SuperClaude Framework Installer[/bold cyan]\n"
            "[dim]Modern AI-enhanced development framework for Claude Code[/dim]",
            border_style="cyan",
        )
    )

    # Confirm installation if interactive
    if not non_interactive and not dry_run:
        proceed = Confirm.ask(
            "\n[bold]Install SuperClaude with recommended configuration?[/bold]",
            default=True,
        )
        if not proceed:
            console.print("[yellow]Installation cancelled by user[/yellow]")
            raise typer.Exit(0)

    # Import and run existing installer logic
    # This bridges to the existing setup/cli/commands/install.py implementation
    try:
        from setup.cli.commands.install import run
        import argparse

        # Create argparse namespace for backward compatibility
        args = argparse.Namespace(
            install_dir=install_dir,
            force=force,
            dry_run=dry_run,
            verbose=verbose,
            quiet=False,
            yes=non_interactive,
            components=["core", "modes", "commands", "agents", "mcp_docs"],  # Full install
            no_backup=False,
            list_components=False,
            diagnose=False,
        )

        # Show progress with rich spinner
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=False,
        ) as progress:
            task = progress.add_task("Installing SuperClaude...", total=None)

            # Run existing installer
            exit_code = run(args)

            if exit_code == 0:
                progress.update(task, description="[green]Installation complete![/green]")
                console.print("\n[bold green]✓ SuperClaude installed successfully![/bold green]")
                console.print("\n[cyan]Next steps:[/cyan]")
                console.print("  1. Restart your Claude Code session")
                console.print(f"  2. Framework files are now available in {install_dir}")
                console.print("  3. Use SuperClaude commands and features in Claude Code")
            else:
                progress.update(task, description="[red]Installation failed[/red]")
                console.print("\n[bold red]✗ Installation failed[/bold red]")
                console.print("[yellow]Check logs for details[/yellow]")
                raise typer.Exit(1)

    except ImportError as e:
        console.print(f"[bold red]Error:[/bold red] Could not import installer: {e}")
        console.print("[yellow]Ensure SuperClaude is properly installed[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command("components")
def install_components(
    components: List[str] = typer.Argument(
        ...,
        help="Component names to install (e.g., core modes commands agents)",
    ),
    install_dir: Path = typer.Option(
        Path.home() / ".claude",
        "--install-dir",
        help="Installation directory",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force reinstallation",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Simulate installation",
    ),
):
    """
    Install specific SuperClaude components

    Available components:
    - core: Core framework files and documentation
    - modes: Behavioral modes (7 modes)
    - commands: Slash commands (26 commands)
    - agents: Specialized agents (17 agents)
    - mcp: MCP server integrations
    - mcp_docs: MCP documentation
    """
    console.print(
        Panel.fit(
            f"[bold]Installing components:[/bold] {', '.join(components)}",
            border_style="cyan",
        )
    )

    try:
        from setup.cli.commands.install import run
        import argparse

        args = argparse.Namespace(
            install_dir=install_dir,
            force=force,
            dry_run=dry_run,
            verbose=False,
            quiet=False,
            yes=True,  # Non-interactive for component installation
            components=components,
            no_backup=False,
            list_components=False,
            diagnose=False,
        )

        exit_code = run(args)

        if exit_code == 0:
            console.print(f"\n[bold green]✓ Components installed: {', '.join(components)}[/bold green]")
        else:
            console.print("\n[bold red]✗ Component installation failed[/bold red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
