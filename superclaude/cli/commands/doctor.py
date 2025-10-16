"""
SuperClaude doctor command - System diagnostics and environment validation
"""

import typer
import sys
import shutil
from pathlib import Path
from rich.table import Table
from rich.panel import Panel
from superclaude.cli._console import console

app = typer.Typer(name="doctor", help="Diagnose system environment and installation", invoke_without_command=True)


def run_diagnostics() -> dict:
    """
    Run comprehensive system diagnostics

    Returns:
        Dict with diagnostic results: {check_name: {status: bool, message: str}}
    """
    results = {}

    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_ok = sys.version_info >= (3, 8)
    results["Python Version"] = {
        "status": python_ok,
        "message": f"{python_version} {'✓' if python_ok else '✗ Requires Python 3.8+'}",
    }

    # Check installation directory
    install_dir = Path.home() / ".claude"
    install_exists = install_dir.exists()
    results["Installation Directory"] = {
        "status": install_exists,
        "message": f"{install_dir} {'exists' if install_exists else 'not found'}",
    }

    # Check write permissions
    try:
        test_file = install_dir / ".write_test"
        if install_dir.exists():
            test_file.touch()
            test_file.unlink()
            write_ok = True
            write_msg = "Writable"
        else:
            write_ok = False
            write_msg = "Directory does not exist"
    except Exception as e:
        write_ok = False
        write_msg = f"No write permission: {e}"

    results["Write Permissions"] = {
        "status": write_ok,
        "message": write_msg,
    }

    # Check disk space (500MB minimum)
    try:
        stat = shutil.disk_usage(install_dir.parent if install_dir.exists() else Path.home())
        free_mb = stat.free / (1024 * 1024)
        disk_ok = free_mb >= 500
        results["Disk Space"] = {
            "status": disk_ok,
            "message": f"{free_mb:.1f} MB free {'✓' if disk_ok else '✗ Need 500+ MB'}",
        }
    except Exception as e:
        results["Disk Space"] = {
            "status": False,
            "message": f"Could not check: {e}",
        }

    # Check for required tools
    tools = {
        "git": "Git version control",
        "uv": "UV package manager (recommended)",
    }

    for tool, description in tools.items():
        tool_path = shutil.which(tool)
        results[f"{description}"] = {
            "status": tool_path is not None,
            "message": f"{tool_path if tool_path else 'Not found'}",
        }

    # Check SuperClaude components
    if install_dir.exists():
        components = {
            "CLAUDE.md": "Core framework entry point",
            "MODE_*.md": "Behavioral mode files",
        }

        claude_md = install_dir / "CLAUDE.md"
        results["Core Framework"] = {
            "status": claude_md.exists(),
            "message": "Installed" if claude_md.exists() else "Not installed",
        }

        # Count modes
        mode_files = list(install_dir.glob("MODE_*.md"))
        results["Behavioral Modes"] = {
            "status": len(mode_files) > 0,
            "message": f"{len(mode_files)} modes installed" if mode_files else "None installed",
        }

    return results


@app.callback(invoke_without_command=True)
def run(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed diagnostic information",
    )
):
    """
    Run system diagnostics and check environment

    This command validates your system environment and verifies
    SuperClaude installation status. It checks:
    - Python version compatibility
    - File system permissions
    - Available disk space
    - Required tools (git, uv)
    - Installed SuperClaude components
    """
    if ctx.invoked_subcommand is not None:
        return
    console.print(
        Panel.fit(
            "[bold cyan]SuperClaude System Diagnostics[/bold cyan]\n"
            "[dim]Checking system environment and installation status[/dim]",
            border_style="cyan",
        )
    )

    # Run diagnostics
    results = run_diagnostics()

    # Create rich table
    table = Table(title="\nDiagnostic Results", show_header=True, header_style="bold cyan")
    table.add_column("Check", style="cyan", width=30)
    table.add_column("Status", width=10)
    table.add_column("Details", style="dim")

    # Add rows
    all_passed = True
    for check_name, result in results.items():
        status = result["status"]
        message = result["message"]

        if status:
            status_str = "[green]✓ PASS[/green]"
        else:
            status_str = "[red]✗ FAIL[/red]"
            all_passed = False

        table.add_row(check_name, status_str, message)

    console.print(table)

    # Summary and recommendations
    if all_passed:
        console.print(
            "\n[bold green]✓ All checks passed![/bold green] "
            "Your system is ready for SuperClaude."
        )
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("  • Use [bold]superclaude install all[/bold] if not yet installed")
        console.print("  • Start using SuperClaude commands in Claude Code")
    else:
        console.print(
            "\n[bold yellow]⚠ Some checks failed[/bold yellow] "
            "Please address the issues below:"
        )

        # Specific recommendations
        console.print("\n[cyan]Recommendations:[/cyan]")

        if not results["Python Version"]["status"]:
            console.print("  • Upgrade Python to version 3.8 or higher")

        if not results["Installation Directory"]["status"]:
            console.print("  • Run [bold]superclaude install all[/bold] to install framework")

        if not results["Write Permissions"]["status"]:
            console.print(f"  • Ensure write permissions for {Path.home() / '.claude'}")

        if not results["Disk Space"]["status"]:
            console.print("  • Free up at least 500 MB of disk space")

        if not results.get("Git version control", {}).get("status"):
            console.print("  • Install Git: https://git-scm.com/downloads")

        if not results.get("UV package manager (recommended)", {}).get("status"):
            console.print("  • Install UV: https://docs.astral.sh/uv/")

        console.print("\n[dim]After addressing issues, run [bold]superclaude doctor[/bold] again[/dim]")

        raise typer.Exit(1)
