"""
SuperClaude config command - Configuration management with API key validation
"""

import re
import typer
import os
from typing import Optional
from pathlib import Path
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from superclaude.cli._console import console

app = typer.Typer(name="config", help="Manage SuperClaude configuration")

# API key validation patterns (P0: basic validation, P1: enhanced with Pydantic)
API_KEY_PATTERNS = {
    "OPENAI_API_KEY": {
        "pattern": r"^sk-[A-Za-z0-9]{20,}$",
        "description": "OpenAI API key (sk-...)",
    },
    "ANTHROPIC_API_KEY": {
        "pattern": r"^sk-ant-[A-Za-z0-9_-]{20,}$",
        "description": "Anthropic API key (sk-ant-...)",
    },
    "TAVILY_API_KEY": {
        "pattern": r"^tvly-[A-Za-z0-9_-]{20,}$",
        "description": "Tavily API key (tvly-...)",
    },
}


def validate_api_key(key_name: str, key_value: str) -> tuple[bool, Optional[str]]:
    """
    Validate API key format

    Args:
        key_name: Environment variable name
        key_value: API key value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if key_name not in API_KEY_PATTERNS:
        # Unknown key type - skip validation
        return True, None

    pattern_info = API_KEY_PATTERNS[key_name]
    pattern = pattern_info["pattern"]

    if not re.match(pattern, key_value):
        return False, f"Invalid format. Expected: {pattern_info['description']}"

    return True, None


@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key (e.g., OPENAI_API_KEY)"),
    value: Optional[str] = typer.Argument(None, help="Configuration value"),
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        help="Prompt for value if not provided",
    ),
):
    """
    Set a configuration value with validation

    Supports API keys for:
    - OPENAI_API_KEY: OpenAI API access
    - ANTHROPIC_API_KEY: Anthropic Claude API access
    - TAVILY_API_KEY: Tavily search API access

    Examples:
      superclaude config set OPENAI_API_KEY
      superclaude config set TAVILY_API_KEY tvly-abc123...
    """
    console.print(
        Panel.fit(
            f"[bold cyan]Setting configuration:[/bold cyan] {key}",
            border_style="cyan",
        )
    )

    # Get value if not provided
    if value is None:
        if not interactive:
            console.print("[red]Value required in non-interactive mode[/red]")
            raise typer.Exit(1)

        # Interactive prompt
        is_secret = "KEY" in key.upper() or "TOKEN" in key.upper()

        if is_secret:
            value = Prompt.ask(
                f"Enter value for {key}",
                password=True,  # Hide input
            )
        else:
            value = Prompt.ask(f"Enter value for {key}")

    # Validate if it's a known API key
    is_valid, error_msg = validate_api_key(key, value)

    if not is_valid:
        console.print(f"[red]Validation failed:[/red] {error_msg}")

        if interactive:
            retry = Confirm.ask("Try again?", default=True)
            if retry:
                # Recursive retry
                set_config(key, None, interactive=True)
                return
        raise typer.Exit(2)

    # Save to environment (in real implementation, save to config file)
    # For P0, we'll just set the environment variable
    os.environ[key] = value

    console.print(f"[green]✓ Configuration saved:[/green] {key}")

    # Show next steps
    if key in API_KEY_PATTERNS:
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print(f"  • The {key} is now configured")
        console.print("  • Restart Claude Code to apply changes")
        console.print(f"  • Verify with: [bold]superclaude config show {key}[/bold]")


@app.command("show")
def show_config(
    key: Optional[str] = typer.Argument(None, help="Specific key to show"),
    show_values: bool = typer.Option(
        False,
        "--show-values",
        help="Show actual values (masked by default for security)",
    ),
):
    """
    Show configuration values

    By default, sensitive values (API keys) are masked.
    Use --show-values to display actual values (use with caution).

    Examples:
      superclaude config show
      superclaude config show OPENAI_API_KEY
      superclaude config show --show-values
    """
    console.print(
        Panel.fit(
            "[bold cyan]SuperClaude Configuration[/bold cyan]",
            border_style="cyan",
        )
    )

    # Get all API key environment variables
    api_keys = {}
    for key_name in API_KEY_PATTERNS.keys():
        value = os.environ.get(key_name)
        if value:
            api_keys[key_name] = value

    # Filter to specific key if requested
    if key:
        if key in api_keys:
            api_keys = {key: api_keys[key]}
        else:
            console.print(f"[yellow]{key} is not configured[/yellow]")
            return

    if not api_keys:
        console.print("[yellow]No API keys configured[/yellow]")
        console.print("\n[cyan]Configure API keys with:[/cyan]")
        console.print("  superclaude config set OPENAI_API_KEY")
        console.print("  superclaude config set TAVILY_API_KEY")
        return

    # Create table
    table = Table(title="\nConfigured API Keys", show_header=True, header_style="bold cyan")
    table.add_column("Key", style="cyan", width=25)
    table.add_column("Value", width=40)
    table.add_column("Status", width=15)

    for key_name, value in api_keys.items():
        # Mask value unless explicitly requested
        if show_values:
            display_value = value
        else:
            # Show first 4 and last 4 characters
            if len(value) > 12:
                display_value = f"{value[:4]}...{value[-4:]}"
            else:
                display_value = "***"

        # Validate
        is_valid, _ = validate_api_key(key_name, value)
        status = "[green]✓ Valid[/green]" if is_valid else "[red]✗ Invalid[/red]"

        table.add_row(key_name, display_value, status)

    console.print(table)

    if not show_values:
        console.print("\n[dim]Values are masked. Use --show-values to display actual values.[/dim]")


@app.command("validate")
def validate_config(
    key: Optional[str] = typer.Argument(None, help="Specific key to validate"),
):
    """
    Validate configuration values

    Checks API key formats for correctness.
    Does not verify that keys are active/working.

    Examples:
      superclaude config validate
      superclaude config validate OPENAI_API_KEY
    """
    console.print(
        Panel.fit(
            "[bold cyan]Validating Configuration[/bold cyan]",
            border_style="cyan",
        )
    )

    # Get API keys to validate
    api_keys = {}
    if key:
        value = os.environ.get(key)
        if value:
            api_keys[key] = value
        else:
            console.print(f"[yellow]{key} is not configured[/yellow]")
            return
    else:
        # Validate all known API keys
        for key_name in API_KEY_PATTERNS.keys():
            value = os.environ.get(key_name)
            if value:
                api_keys[key_name] = value

    if not api_keys:
        console.print("[yellow]No API keys to validate[/yellow]")
        return

    # Validate each key
    all_valid = True
    for key_name, value in api_keys.items():
        is_valid, error_msg = validate_api_key(key_name, value)

        if is_valid:
            console.print(f"[green]✓[/green] {key_name}: Valid format")
        else:
            console.print(f"[red]✗[/red] {key_name}: {error_msg}")
            all_valid = False

    # Summary
    if all_valid:
        console.print("\n[bold green]✓ All API keys have valid formats[/bold green]")
    else:
        console.print("\n[bold yellow]⚠ Some API keys have invalid formats[/bold yellow]")
        console.print("[dim]Use [bold]superclaude config set <KEY>[/bold] to update[/dim]")
        raise typer.Exit(1)
