"""
SuperClaude CLI Main Entry Point

Provides command-line interface for SuperClaude operations.
"""

import sys
from pathlib import Path

import click

# Add parent directory to path to import superclaude
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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
    Install SuperClaude to Claude Code

    Installs core framework files, slash commands, agents, and skills
    to ~/.claude/ so you can use SuperClaude in Claude Code.

    Examples:
        superclaude install
        superclaude install --force
        superclaude install --list
        superclaude install --target /custom/path
    """
    from .install_agents import (
        install_agents,
        list_available_agents,
        list_installed_agents,
    )
    from .install_commands import (
        install_commands,
        list_available_commands,
        list_installed_commands,
    )
    from .install_core import (
        install_core_files,
        list_core_files,
        list_installed_core_files,
    )
    from .install_skill import list_available_skills
    from .install_skills import install_all_skills, list_installed_skills

    # List only mode
    if list_only:
        # Core files
        core_available = list_core_files()
        core_installed = list_installed_core_files()

        click.echo("📋 Core Framework Files:")
        for name in core_available:
            status = "✅ installed" if name in core_installed else "⬜ not installed"
            click.echo(f"   {name:35} {status}")

        click.echo(
            f"\nCore: {len(core_available)} available, {len(core_installed)} installed"
        )

        # Commands
        available = list_available_commands()
        installed = list_installed_commands()

        click.echo("\n📋 Slash Commands:")
        for cmd in available:
            status = "✅ installed" if cmd in installed else "⬜ not installed"
            click.echo(f"   /{cmd:20} {status}")

        click.echo(
            f"\nCommands: {len(available)} available, {len(installed)} installed"
        )

        # Agents
        agents_available = list_available_agents()
        agents_installed = list_installed_agents()

        click.echo("\n📋 Agents:")
        for name in agents_available:
            status = "✅ installed" if name in agents_installed else "⬜ not installed"
            click.echo(f"   {name:35} {status}")

        click.echo(
            f"\nAgents: {len(agents_available)} available, {len(agents_installed)} installed"
        )

        # Skills
        skills_available = list_available_skills()
        skills_installed = list_installed_skills()

        click.echo("\n📋 Skills:")
        for name in skills_available:
            status = "✅ installed" if name in skills_installed else "⬜ not installed"
            click.echo(f"   {name:35} {status}")

        click.echo(
            f"\nSkills: {len(skills_available)} available, {len(skills_installed)} installed"
        )
        return

    # Step 1: Install core framework files to ~/.claude/
    click.echo("📦 Installing core framework files to ~/.claude/...")
    click.echo()

    core_success, core_message = install_core_files(force=force)
    click.echo(core_message)
    click.echo()

    # Step 2: Install slash commands
    target_path = Path(target).expanduser()

    click.echo(f"📦 Installing slash commands to {target_path}...")
    click.echo()

    cmd_success, cmd_message = install_commands(target_path=target_path, force=force)
    click.echo(cmd_message)
    click.echo()

    # Step 3: Install agents
    click.echo("📦 Installing agents to ~/.claude/agents/...")
    click.echo()

    agent_success, agent_message = install_agents(force=force)
    click.echo(agent_message)
    click.echo()

    # Step 4: Install skills
    click.echo("📦 Installing skills to ~/.claude/skills/...")
    click.echo()

    skill_success, skill_message = install_all_skills(force=force)
    click.echo(skill_message)

    if not core_success or not cmd_success or not agent_success or not skill_success:
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
    Update SuperClaude to latest version

    Re-installs core framework files and slash commands to match
    the current package version. Equivalent to 'install --force'.

    Example:
        superclaude update
        superclaude update --target /custom/path
    """
    from .install_agents import install_agents
    from .install_commands import install_commands
    from .install_core import install_core_files
    from .install_skills import install_all_skills

    click.echo(f"🔄 Updating SuperClaude to version {__version__}...")
    click.echo()

    # Update core framework files
    click.echo("📦 Updating core framework files...")
    core_success, core_message = install_core_files(force=True)
    click.echo(core_message)
    click.echo()

    # Update slash commands
    target_path = Path(target).expanduser()
    click.echo("📦 Updating slash commands...")
    cmd_success, cmd_message = install_commands(target_path=target_path, force=True)
    click.echo(cmd_message)
    click.echo()

    # Update agents
    click.echo("📦 Updating agents...")
    agent_success, agent_message = install_agents(force=True)
    click.echo(agent_message)
    click.echo()

    # Update skills
    click.echo("📦 Updating skills...")
    skill_success, skill_message = install_all_skills(force=True)
    click.echo(skill_message)

    if not core_success or not cmd_success or not agent_success or not skill_success:
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


from superclaude.cli.sprint import sprint_group

main.add_command(sprint_group, name="sprint")

from superclaude.cli.roadmap import roadmap_group

main.add_command(roadmap_group, name="roadmap")

from superclaude.cli.cleanup_audit import cleanup_audit_group

main.add_command(cleanup_audit_group, name="cleanup-audit")

from superclaude.cli.tasklist import tasklist_group

main.add_command(tasklist_group, name="tasklist")


if __name__ == "__main__":
    main()
