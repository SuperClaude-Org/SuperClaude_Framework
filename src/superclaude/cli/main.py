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


def _run_install(skills_dir: str, agents_dir: str, force: bool, minimal: bool) -> bool:
    """Install skills (and agents unless minimal). Returns True on success."""
    from .install_assets import install_agents
    from .install_skill import install_all_skills

    skills_path = Path(skills_dir).expanduser()

    only = ["confidence-check"] if minimal else None

    click.echo(f"📦 Installing SuperClaude skills to {skills_path}...")
    click.echo()

    skill_success, skill_message = install_all_skills(
        target_path=skills_path, force=force, only=only
    )
    click.echo(skill_message)

    if minimal:
        return skill_success

    agents_path = Path(agents_dir).expanduser()

    click.echo()
    click.echo(f"📦 Installing SuperClaude agents to {agents_path}...")
    click.echo()

    agent_success, agent_message = install_agents(target_path=agents_path, force=force)
    click.echo(agent_message)

    return skill_success and agent_success


@main.command()
@click.option(
    "--skills-dir",
    default="~/.claude/skills",
    help="Skills installation directory (default: ~/.claude/skills)",
)
@click.option(
    "--agents-dir",
    default="~/.claude/agents",
    help="Agents installation directory (default: ~/.claude/agents)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force reinstall if skills or agents already exist",
)
@click.option(
    "--minimal",
    is_flag=True,
    help="Install only the confidence-check skill (no agents)",
)
@click.option(
    "--list",
    "list_only",
    is_flag=True,
    help="List available skills and agents without installing",
)
def install(
    skills_dir: str, agents_dir: str, force: bool, minimal: bool, list_only: bool
):
    """
    Install SuperClaude skills and agents to Claude Code

    Installs all skills (confidence-check, spec-panel, socratic, pm-reflexion)
    to ~/.claude/skills/ and agents (explore-haiku) to ~/.claude/agents/.

    Examples:
        superclaude install
        superclaude install --force
        superclaude install --minimal
        superclaude install --list
    """
    from .install_assets import list_available_agents
    from .install_skill import list_available_skills

    # List only mode
    if list_only:
        skills = list_available_skills()
        click.echo(f"📋 Available Skills: {len(skills)}")
        for skill in skills:
            click.echo(f"   {skill}")

        agents = list_available_agents()
        click.echo(f"\n📋 Available Agents: {len(agents)}")
        for agent in agents:
            click.echo(f"   @{agent}")

        click.echo(f"\nTotal: {len(skills)} skills, {len(agents)} agents")
        return

    if not _run_install(skills_dir, agents_dir, force, minimal):
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
    "--skills-dir",
    default="~/.claude/skills",
    help="Skills installation directory (default: ~/.claude/skills)",
)
@click.option(
    "--agents-dir",
    default="~/.claude/agents",
    help="Agents installation directory (default: ~/.claude/agents)",
)
@click.option(
    "--minimal",
    is_flag=True,
    help="Update only the confidence-check skill (no agents)",
)
def update(skills_dir: str, agents_dir: str, minimal: bool):
    """
    Update SuperClaude skills and agents to latest version

    Re-installs all skills and agents to match the current package version.
    This is a convenience command equivalent to 'install --force'.

    Example:
        superclaude update
    """
    click.echo(f"🔄 Updating SuperClaude to version {__version__}...")
    click.echo()

    if not _run_install(skills_dir, agents_dir, force=True, minimal=minimal):
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

    SKILL_NAME: Name of the skill to install (e.g., confidence-check)

    Example:
        superclaude install-skill confidence-check
        superclaude install-skill confidence-check --target ~/.claude/skills --force
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
