"""
MCP Server Installation Module for SuperClaude

Installs and manages MCP servers using the latest Claude Code API.
Based on the installer logic from commit d4a17fc but adapted for modern Claude Code.
"""

import os
import platform
import shlex
import subprocess
from typing import Dict, List, Optional, Tuple

import click

# MCP Server Registry
# Adapted from commit d4a17fc with modern transport configuration
MCP_SERVERS = {
    "sequential-thinking": {
        "name": "sequential-thinking",
        "description": "Multi-step problem solving and systematic analysis",
        "transport": "stdio",
        "command": "npx -y @modelcontextprotocol/server-sequential-thinking",
        "required": False,
    },
    "context7": {
        "name": "context7",
        "description": "Official library documentation and code examples",
        "transport": "stdio",
        "command": "npx -y @upstash/context7-mcp",
        "required": False,
    },
    "magic": {
        "name": "magic",
        "description": "Modern UI component generation and design systems",
        "transport": "stdio",
        "command": "npx -y @21st-dev/magic",
        "required": False,
        "api_key_env": "TWENTYFIRST_API_KEY",
        "api_key_description": "21st.dev API key for UI component generation",
    },
    "playwright": {
        "name": "playwright",
        "description": "Cross-browser E2E testing and automation",
        "transport": "stdio",
        "command": "npx -y @playwright/mcp@latest",
        "required": False,
    },
    "serena": {
        "name": "serena",
        "description": "Semantic code analysis and intelligent editing",
        "transport": "stdio",
        "command": "uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --enable-web-dashboard false --enable-gui-log-window false",
        "required": False,
    },
    "morphllm-fast-apply": {
        "name": "morphllm-fast-apply",
        "description": "Fast Apply capability for context-aware code modifications",
        "transport": "stdio",
        "command": "npx -y @morph-llm/morph-fast-apply",
        "required": False,
        "api_key_env": "MORPH_API_KEY",
        "api_key_description": "Morph API key for Fast Apply",
    },
    "tavily": {
        "name": "tavily",
        "description": "Web search and real-time information retrieval for deep research",
        "transport": "stdio",
        "command": "npx -y tavily-mcp@0.1.2",
        "required": False,
        "api_key_env": "TAVILY_API_KEY",
        "api_key_description": "Tavily API key for web search (get from https://app.tavily.com)",
    },
    "chrome-devtools": {
        "name": "chrome-devtools",
        "description": "Chrome DevTools debugging and performance analysis",
        "transport": "stdio",
        "command": "npx -y chrome-devtools-mcp@latest",
        "required": False,
    },
    "airis-mcp-gateway": {
        "name": "airis-mcp-gateway",
        "description": "Unified MCP Gateway with 25+ servers (90% token reduction via lazy loading)",
        "transport": "sse",
        "url": "http://localhost:9400/sse",
        "health_url": "http://localhost:9400/health",
        "required": False,
        "docker_based": True,
        "setup_instructions": [
            "1. Clone: git clone https://github.com/agiletec-inc/airis-mcp-gateway.git",
            "2. Setup: cd airis-mcp-gateway && cp .env.example .env",
            "3. Start: docker compose up -d",
        ],
        "homebrew_install": "brew tap agiletec-inc/tap && brew install airis-mcp-gateway",
    },
}


def _run_command(cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Run a command with proper cross-platform shell handling.

    Args:
        cmd: Command as list of strings
        **kwargs: Additional subprocess.run arguments

    Returns:
        CompletedProcess result
    """
    if platform.system() == "Windows":
        # On Windows, wrap command in 'cmd /c' to properly handle commands like npx
        cmd = ["cmd", "/c"] + cmd
        return subprocess.run(cmd, **kwargs)
    else:
        # macOS/Linux: Use string format with proper shell to support aliases
        cmd_str = " ".join(shlex.quote(str(arg)) for arg in cmd)

        # Use the user's shell to execute the command, supporting aliases
        user_shell = os.environ.get("SHELL", "/bin/bash")
        return subprocess.run(
            cmd_str, shell=True, env=os.environ, executable=user_shell, **kwargs
        )


def check_prerequisites() -> Tuple[bool, List[str]]:
    """Check if required tools are available."""
    errors = []

    # Check Claude CLI
    try:
        result = _run_command(
            ["claude", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            errors.append("Claude CLI not found - required for MCP server management")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        errors.append("Claude CLI not found - required for MCP server management")

    # Check Node.js for npm-based servers
    try:
        result = _run_command(
            ["node", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            errors.append("Node.js not found - required for npm-based MCP servers")
        else:
            version = result.stdout.strip()
            try:
                version_num = int(version.lstrip("v").split(".")[0])
                if version_num < 18:
                    errors.append(
                        f"Node.js version {version} found, but version 18+ required"
                    )
            except (ValueError, IndexError):
                pass
    except (subprocess.TimeoutExpired, FileNotFoundError):
        errors.append("Node.js not found - required for npm-based MCP servers")

    # Check uv for Python-based servers (optional)
    try:
        result = _run_command(
            ["uv", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            click.echo("⚠️  uv not found - required for Serena MCP server", err=True)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        click.echo("⚠️  uv not found - required for Serena MCP server", err=True)

    return len(errors) == 0, errors


def check_mcp_server_installed(server_name: str) -> bool:
    """Check if an MCP server is already installed."""
    try:
        result = _run_command(
            ["claude", "mcp", "list"], capture_output=True, text=True, timeout=60
        )

        if result.returncode != 0:
            return False

        # Parse output to check if server is installed
        output = result.stdout.lower()
        return server_name.lower() in output

    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False


def prompt_for_api_key(
    server_name: str, env_var: str, description: str
) -> Optional[str]:
    """Prompt user for API key if needed."""
    click.echo(f"\n🔑 MCP server '{server_name}' requires an API key")
    click.echo(f"   Environment variable: {env_var}")
    click.echo(f"   Description: {description}")

    # Check if already set in environment
    if os.getenv(env_var):
        click.echo(f"   ✅ {env_var} already set in environment")
        return os.getenv(env_var)

    # Prompt user
    if click.confirm(f"   Would you like to set {env_var} now?", default=True):
        api_key = click.prompt(f"   Enter {env_var}", hide_input=True)
        return api_key
    else:
        click.echo(
            f"   ⚠️  Proceeding without {env_var} - server may not function properly"
        )
        return None


def install_mcp_server(
    server_info: Dict, scope: str = "user", dry_run: bool = False
) -> bool:
    """
    Install a single MCP server using modern Claude Code API.

    Args:
        server_info: Server configuration dictionary
        scope: Installation scope (local, project, user)
        dry_run: If True, only show what would be done

    Returns:
        True if successful, False otherwise
    """
    server_name = server_info["name"]
    transport = server_info["transport"]

    click.echo(f"📦 Installing MCP server: {server_name}")

    # Check if already installed
    if check_mcp_server_installed(server_name):
        click.echo(f"   ✅ Already installed: {server_name}")
        return True

    # Handle Docker-based servers (like airis-mcp-gateway)
    if server_info.get("docker_based"):
        return _install_docker_based_server(server_info, scope, dry_run)

    command = server_info["command"]

    # Handle API key requirements
    env_args = []
    if "api_key_env" in server_info:
        api_key_env = server_info["api_key_env"]
        api_key = prompt_for_api_key(
            server_name,
            api_key_env,
            server_info.get("api_key_description", f"API key for {server_name}"),
        )

        if api_key:
            env_args = ["--env", f"{api_key_env}={api_key}"]

    # Build installation command using modern Claude Code API
    # Format: claude mcp add --transport <transport> [--scope <scope>] [--env KEY=VALUE] <name> -- <command>

    cmd = ["claude", "mcp", "add", "--transport", transport]

    # Add scope if not default
    if scope != "local":
        cmd.extend(["--scope", scope])

    # Add environment variables if any
    if env_args:
        cmd.extend(env_args)

    # Add server name
    cmd.append(server_name)

    # Add separator
    cmd.append("--")

    # Add server command (split into parts)
    cmd.extend(shlex.split(command))

    if dry_run:
        click.echo(f"   [DRY RUN] Would run: {' '.join(cmd)}")
        return True

    try:
        click.echo(
            f"   Running: claude mcp add --transport {transport} {server_name} -- {command}"
        )
        result = _run_command(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            click.echo(f"   ✅ Successfully installed: {server_name}")
            return True
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            click.echo(f"   ❌ Failed to install {server_name}: {error_msg}", err=True)
            return False

    except subprocess.TimeoutExpired:
        click.echo(f"   ❌ Timeout installing {server_name}", err=True)
        return False
    except Exception as e:
        click.echo(f"   ❌ Error installing {server_name}: {e}", err=True)
        return False


def _install_docker_based_server(
    server_info: Dict, scope: str = "user", dry_run: bool = False
) -> bool:
    """
    Install a Docker-based MCP server (like airis-mcp-gateway).

    For Docker-based servers, we:
    1. Check if the gateway is reachable (Docker running)
    2. If reachable, register with Claude Code
    3. If not reachable, show setup instructions

    Args:
        server_info: Server configuration dictionary
        scope: Installation scope
        dry_run: If True, only show what would be done

    Returns:
        True if successful, False otherwise
    """
    import urllib.request
    import urllib.error

    server_name = server_info["name"]
    transport = server_info["transport"]
    url = server_info["url"]
    setup_instructions = server_info.get("setup_instructions", [])
    homebrew_install = server_info.get("homebrew_install")

    click.echo(f"\n   🐳 {server_name} is a Docker-based unified MCP gateway")
    click.echo(f"   📊 Provides 90% token reduction via lazy loading (12,500 → 1,250 tokens)")

    # Check if gateway is reachable
    health_url = server_info.get("health_url") or url.replace("/sse", "/health").replace("/mcp", "/health")
    gateway_running = False

    try:
        click.echo(f"   🔍 Checking if gateway is running at {health_url}...")
        req = urllib.request.Request(health_url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                gateway_running = True
                click.echo("   ✅ Gateway is running!")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        click.echo("   ⚠️  Gateway not reachable (Docker may not be running)")

    if gateway_running:
        # Gateway is running, register with Claude Code
        # Format: claude mcp add --transport http <name> <url>
        cmd = ["claude", "mcp", "add", "--transport", transport]

        if scope != "local":
            cmd.extend(["--scope", scope])

        cmd.extend([server_name, url])

        if dry_run:
            click.echo(f"   [DRY RUN] Would run: {' '.join(cmd)}")
            return True

        try:
            click.echo(f"   Running: claude mcp add --transport {transport} {server_name} {url}")
            result = _run_command(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                click.echo(f"   ✅ Successfully registered: {server_name}")
                click.echo(f"\n   📋 Included servers: tavily, context7, serena, mindbase, github, filesystem, and 20+ more")
                click.echo(f"   🌐 Settings UI: http://ui.gateway.localhost:5273")
                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                click.echo(f"   ❌ Failed to register {server_name}: {error_msg}", err=True)
                return False

        except subprocess.TimeoutExpired:
            click.echo(f"   ❌ Timeout registering {server_name}", err=True)
            return False
        except Exception as e:
            click.echo(f"   ❌ Error registering {server_name}: {e}", err=True)
            return False
    else:
        # Gateway not running, show setup instructions
        click.echo(f"\n   📝 Setup Instructions for {server_name}:")
        click.echo("   " + "-" * 50)

        if homebrew_install:
            click.echo(f"\n   Option A: Homebrew (recommended for macOS)")
            click.echo(f"   $ {homebrew_install}")

        click.echo(f"\n   Option B: Docker Compose")
        for instruction in setup_instructions:
            click.echo(f"   {instruction}")

        click.echo("\n   After setup, run this command again to register the gateway.")
        click.echo("   " + "-" * 50)

        # Ask user if they want to proceed with manual registration anyway
        if click.confirm("\n   Register anyway (gateway must be started manually)?", default=False):
            cmd = ["claude", "mcp", "add", "--transport", transport]
            if scope != "local":
                cmd.extend(["--scope", scope])
            cmd.extend([server_name, url])

            if dry_run:
                click.echo(f"   [DRY RUN] Would run: {' '.join(cmd)}")
                return True

            try:
                result = _run_command(cmd, capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    click.echo(f"   ✅ Registered (start gateway with 'docker compose up -d' before using)")
                    return True
                else:
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    click.echo(f"   ❌ Failed: {error_msg}", err=True)
                    return False
            except Exception as e:
                click.echo(f"   ❌ Error: {e}", err=True)
                return False

        return False


def list_available_servers():
    """List all available MCP servers."""
    click.echo("📋 Available MCP Servers:\n")

    for server_key, server_info in MCP_SERVERS.items():
        name = server_info["name"]
        description = server_info["description"]
        api_key_note = ""

        if "api_key_env" in server_info:
            api_key_note = f" (requires {server_info['api_key_env']})"

        # Check if installed
        is_installed = check_mcp_server_installed(name)
        status = "✅ installed" if is_installed else "⬜ not installed"

        click.echo(f"   {name:25} {status}")
        click.echo(f"      {description}{api_key_note}")
        click.echo()

    click.echo(f"Total: {len(MCP_SERVERS)} servers available")


def install_mcp_servers(
    selected_servers: Optional[List[str]] = None,
    scope: str = "user",
    dry_run: bool = False,
) -> Tuple[bool, str]:
    """
    Install MCP servers for Claude Code.

    Args:
        selected_servers: List of server names to install, or None for interactive selection
        scope: Installation scope (local, project, user)
        dry_run: If True, only show what would be done

    Returns:
        Tuple of (success, message)
    """
    # Check prerequisites
    success, errors = check_prerequisites()
    if not success:
        error_msg = "Prerequisites not met:\n" + "\n".join(f"  ❌ {e}" for e in errors)
        return False, error_msg

    # Determine which servers to install
    if selected_servers:
        # Use explicitly selected servers
        servers_to_install = []
        for server_name in selected_servers:
            if server_name in MCP_SERVERS:
                servers_to_install.append(server_name)
            else:
                click.echo(f"⚠️  Unknown server: {server_name}", err=True)

        if not servers_to_install:
            return False, "No valid servers selected"
    else:
        # Interactive selection
        click.echo("📋 Available MCP servers:\n")

        server_options = []
        for key, info in MCP_SERVERS.items():
            api_note = (
                f" (requires {info['api_key_env']})" if "api_key_env" in info else ""
            )
            server_options.append(
                f"{info['name']:25} - {info['description']}{api_note}"
            )

        for i, option in enumerate(server_options, 1):
            click.echo(f"   {i}. {option}")

        click.echo("\n   0. Install all servers")
        click.echo()

        selection = click.prompt(
            "Select servers to install (comma-separated numbers, or 0 for all)",
            default="0",
        )

        if selection.strip() == "0":
            servers_to_install = list(MCP_SERVERS.keys())
        else:
            try:
                indices = [int(x.strip()) for x in selection.split(",")]
                server_list = list(MCP_SERVERS.keys())
                servers_to_install = [
                    server_list[i - 1] for i in indices if 0 < i <= len(server_list)
                ]
            except (ValueError, IndexError):
                return False, "Invalid selection"

    if not servers_to_install:
        return False, "No servers selected"

    # Install each server
    click.echo(f"\n🔌 Installing {len(servers_to_install)} MCP server(s)...\n")

    installed_count = 0
    failed_servers = []

    for server_name in servers_to_install:
        server_info = MCP_SERVERS[server_name]
        if install_mcp_server(server_info, scope, dry_run):
            installed_count += 1
        else:
            failed_servers.append(server_name)

    # Generate result message
    if failed_servers:
        message = f"\n⚠️  Partially completed: {installed_count}/{len(servers_to_install)} servers installed\n"
        message += f"Failed servers: {', '.join(failed_servers)}"
        return False, message
    else:
        message = f"\n✅ Successfully installed {installed_count} MCP server(s)!\n"
        message += "\nℹ️  Use 'claude mcp list' to see all installed servers"
        message += "\nℹ️  Use '/mcp' in Claude Code to check server status"
        return True, message
