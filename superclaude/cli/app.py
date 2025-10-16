"""
SuperClaude CLI - Root application with typer
Modern, type-safe command-line interface with rich formatting
"""

import sys
import typer
from typing import Optional
from superclaude.cli._console import console
from superclaude.cli.commands import install, doctor, config

# Create root typer app
app = typer.Typer(
    name="superclaude",
    help="SuperClaude Framework CLI - AI-enhanced development framework for Claude Code",
    add_completion=False,  # Disable shell completion for now
    no_args_is_help=True,  # Show help when no args provided
    pretty_exceptions_enable=True,  # Rich exception formatting
)

# Register command groups
app.add_typer(install.app, name="install", help="Install SuperClaude components")
app.add_typer(doctor.app, name="doctor", help="Diagnose system environment")
app.add_typer(config.app, name="config", help="Manage configuration")


def version_callback(value: bool):
    """Show version and exit"""
    if value:
        from superclaude import __version__
        console.print(f"[bold cyan]SuperClaude[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    SuperClaude Framework CLI

    Modern command-line interface for managing SuperClaude installation,
    configuration, and diagnostic operations.
    """
    pass


def cli_main():
    """Entry point for CLI (called from pyproject.toml)"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[bold red]Unhandled error:[/bold red] {e}")
        if "--debug" in sys.argv or "--verbose" in sys.argv:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
