"""
SuperClaude CLI Main Entry Point

Provides command-line interface for SuperClaude operations.
"""

import sys
from pathlib import Path

import click

from superclaude import __version__


@click.group()
@click.version_option(version=__version__, prog_name="SuperClaude")
def main():
    """
    SuperClaude - AI-enhanced development framework for Claude Code

    A pytest plugin providing PM Agent capabilities and optional skills system.
    """
    pass


@main.command()
@click.option(
    "--target",
    default="~/.claude/commands/sc",
    help="Installation directory (default: ~/.claude/commands/sc)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force reinstall if commands already exist",
)
@click.option(
    "--list",
    "list_only",
    is_flag=True,
    help="List available commands without installing",
)
def install(target: str, force: bool, list_only: bool):
    """
    Install SuperClaude commands to Claude Code

    Installs all slash commands (/sc:research, /sc:index-repo, etc.) to your
    ~/.claude/commands/sc directory so you can use them in Claude Code.

    Examples:
        superclaude install
        superclaude install --force
        superclaude install --list
        superclaude install --target /custom/path
    """
    from .install_commands import (
        install_agents,
        install_commands,
        list_available_agents,
        list_available_commands,
        list_installed_commands,
    )

    # List only mode
    if list_only:
        available = list_available_commands()
        installed = list_installed_commands()

        click.echo("📋 Available Commands:")
        for cmd in available:
            status = "✅ installed" if cmd in installed else "⬜ not installed"
            click.echo(f"   /{cmd:20} {status}")

        agents = list_available_agents()
        click.echo(f"\n📋 Available Agents: {len(agents)}")
        for agent in agents:
            click.echo(f"   @{agent}")

        click.echo(f"\nTotal: {len(available)} commands, {len(agents)} agents")
        return

    # Install commands
    target_path = Path(target).expanduser()

    click.echo(f"📦 Installing SuperClaude commands to {target_path}...")
    click.echo()

    success, message = install_commands(target_path=target_path, force=force)
    click.echo(message)

    # Also install agents to ~/.claude/agents/
    click.echo()
    click.echo("📦 Installing SuperClaude agents...")
    click.echo()

    agent_success, agent_message = install_agents(force=force)
    click.echo(agent_message)

    if not success or not agent_success:
        sys.exit(1)


@main.command()
@click.option("--servers", "-s", multiple=True, help="Specific MCP servers to install")
@click.option("--list", "list_only", is_flag=True, help="List available MCP servers")
@click.option(
    "--scope",
    default="user",
    type=click.Choice(["local", "project", "user"]),
    help="Installation scope",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be installed without actually installing",
)
def mcp(servers, list_only, scope, dry_run):
    """
    Install and manage MCP servers for Claude Code

    Examples:
        superclaude mcp --list
        superclaude mcp --servers tavily --servers context7
        superclaude mcp --scope project
        superclaude mcp --dry-run
    """
    from .install_mcp import install_mcp_servers, list_available_servers

    if list_only:
        list_available_servers()
        return

    click.echo(f"🔌 Installing MCP servers (scope: {scope})...")
    click.echo()

    success, message = install_mcp_servers(
        selected_servers=list(servers) if servers else None,
        scope=scope,
        dry_run=dry_run,
    )

    click.echo(message)

    if not success:
        sys.exit(1)


@main.command()
@click.option(
    "--target",
    default="~/.claude/commands/sc",
    help="Installation directory (default: ~/.claude/commands/sc)",
)
def update(target: str):
    """
    Update SuperClaude commands to latest version

    Re-installs all slash commands to match the current package version.
    This is a convenience command equivalent to 'install --force'.

    Example:
        superclaude update
        superclaude update --target /custom/path
    """
    from .install_commands import install_agents, install_commands

    target_path = Path(target).expanduser()

    click.echo(f"🔄 Updating SuperClaude commands to version {__version__}...")
    click.echo()

    success, message = install_commands(target_path=target_path, force=True)
    click.echo(message)

    click.echo()
    agent_success, agent_message = install_agents(force=True)
    click.echo(agent_message)

    if not success or not agent_success:
        sys.exit(1)


@main.command()
@click.argument("skill_name")
@click.option(
    "--target",
    default="~/.claude/skills",
    help="Installation directory (default: ~/.claude/skills)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force reinstall if skill already exists",
)
def install_skill(skill_name: str, target: str, force: bool):
    """
    Install a SuperClaude skill to Claude Code

    SKILL_NAME: Name of the skill to install (e.g., pm-agent)

    Example:
        superclaude install-skill pm-agent
        superclaude install-skill pm-agent --target ~/.claude/skills --force
    """
    from .install_skill import install_skill_command

    target_path = Path(target).expanduser()

    click.echo(f"📦 Installing skill '{skill_name}' to {target_path}...")

    success, message = install_skill_command(
        skill_name=skill_name, target_path=target_path, force=force
    )

    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed diagnostic information",
)
def doctor(verbose: bool):
    """
    Check SuperClaude installation health

    Verifies:
        - pytest plugin loaded correctly
        - Skills installed (if any)
        - Configuration files present
    """
    from .doctor import run_doctor

    click.echo("🔍 SuperClaude Doctor\n")

    results = run_doctor(verbose=verbose)

    # Display results
    for check in results["checks"]:
        status_symbol = "✅" if check["passed"] else "❌"
        click.echo(f"{status_symbol} {check['name']}")

        if verbose and check.get("details"):
            for detail in check["details"]:
                click.echo(f"    {detail}")

    # Summary
    click.echo()
    total = len(results["checks"])
    passed = sum(1 for check in results["checks"] if check["passed"])

    if passed == total:
        click.echo("✅ SuperClaude is healthy")
    else:
        click.echo(f"⚠️  {total - passed}/{total} checks failed")
        sys.exit(1)


@main.command()
def version():
    """Show SuperClaude version"""
    click.echo(f"SuperClaude version {__version__}")


if __name__ == "__main__":
    main()
