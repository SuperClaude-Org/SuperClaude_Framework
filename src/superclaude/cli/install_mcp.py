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

# AIRIS MCP Gateway - Unified MCP solution (recommended)
AIRIS_GATEWAY = {
    "name": "airis-mcp-gateway",
    "description": "Unified MCP gateway with 60+ tools, HOT/COLD management, 98% token reduction",
    "transport": "sse",
    "endpoint": "http://localhost:9400/sse",
    "docker_compose_url": "https://raw.githubusercontent.com/agiletec-inc/airis-mcp-gateway/main/docker-compose.dist.yml",
    "repository": "https://github.com/agiletec-inc/airis-mcp-gateway",
}

# Individual MCP Server Registry (legacy, for users who prefer individual servers)
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
    # Ensure UTF-8 encoding on all platforms to handle Unicode output
    if "encoding" not in kwargs:
        kwargs["encoding"] = "utf-8"
    if "errors" not in kwargs:
        kwargs["errors"] = "replace"  # Replace undecodable bytes instead of raising

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


def check_docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = _run_command(
            ["docker", "info"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def install_airis_gateway(dry_run: bool = False) -> bool:
    """
    Install AIRIS MCP Gateway using Docker.

    Installs to ~/.superclaude/airis-mcp-gateway/ to avoid polluting the host.

    Returns:
        True if successful, False otherwise
    """
    from pathlib import Path

    click.echo("\n🚀 Installing AIRIS MCP Gateway (Recommended)")
    click.echo(
        "   This provides 60+ tools through a single endpoint with 98% token reduction.\n"
    )

    # Check Docker
    if not check_docker_available():
        click.echo("   ❌ Docker is required but not available.", err=True)
        click.echo(
            "   Please install Docker: https://docs.docker.com/get-docker/", err=True
        )
        return False

    click.echo("   ✅ Docker is available")

    # Create dedicated installation directory
    install_dir = Path.home() / ".superclaude" / "airis-mcp-gateway"
    compose_file = install_dir / "docker-compose.yml"

    if dry_run:
        click.echo(f"   [DRY RUN] Would create directory: {install_dir}")
        click.echo("   [DRY RUN] Would download docker-compose.yml")
        click.echo("   [DRY RUN] Would run: docker compose up -d")
        click.echo("   [DRY RUN] Would register with Claude Code")
        return True

    # Create installation directory
    install_dir.mkdir(parents=True, exist_ok=True)
    click.echo(f"   📁 Installation directory: {install_dir}")

    # Download docker-compose file
    click.echo("   📥 Downloading docker-compose configuration...")
    try:
        result = _run_command(
            [
                "curl",
                "-fsSL",
                "-o",
                str(compose_file),
                AIRIS_GATEWAY["docker_compose_url"],
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            click.echo(
                f"   ❌ Failed to download docker-compose file: {result.stderr}",
                err=True,
            )
            return False
    except Exception as e:
        click.echo(f"   ❌ Error downloading: {e}", err=True)
        return False

    # Create mcp-config.json if it doesn't exist (required for Docker volume mount)
    # Docker will create a directory instead of a file if the mount target doesn't exist
    mcp_config_file = install_dir / "mcp-config.json"
    if not mcp_config_file.exists():
        click.echo("   📄 Creating mcp-config.json...")
        try:
            # Download example config from upstream
            result = _run_command(
                [
                    "curl",
                    "-fsSL",
                    "-o",
                    str(mcp_config_file),
                    "https://raw.githubusercontent.com/agiletec-inc/airis-mcp-gateway/main/mcp-config.json.example",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                # Fallback: create minimal config
                click.echo("   ⚠️  Could not download example config, creating minimal config")
                mcp_config_file.write_text('{"mcpServers": {}}')
        except Exception:
            # Fallback: create minimal config
            mcp_config_file.write_text('{"mcpServers": {}}')
    elif mcp_config_file.is_dir():
        # Fix: mcp-config.json was incorrectly created as a directory
        click.echo("   🔧 Fixing mcp-config.json (was directory, converting to file)...")
        import shutil
        shutil.rmtree(mcp_config_file)
        mcp_config_file.write_text('{"mcpServers": {}}')

    # Create profiles directory if it doesn't exist
    profiles_dir = install_dir / "profiles"
    profiles_dir.mkdir(exist_ok=True)

    # Start the gateway from the installation directory
    click.echo("   🐳 Starting AIRIS MCP Gateway containers...")
    try:
        result = _run_command(
            [
                "docker",
                "compose",
                "-f",
                str(compose_file),
                "--project-directory",
                str(install_dir),
                "up",
                "-d",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            click.echo(f"   ❌ Failed to start containers: {result.stderr}", err=True)
            return False
    except subprocess.TimeoutExpired:
        click.echo("   ❌ Timeout starting containers", err=True)
        return False

    click.echo("   ✅ Gateway containers started")

    # Register with Claude Code
    click.echo("   📝 Registering with Claude Code...")
    try:
        cmd = [
            "claude",
            "mcp",
            "add",
            "--scope",
            "user",
            "--transport",
            "sse",
            AIRIS_GATEWAY["name"],
            "--",
            "npx",
            "-y",
            "mcp-remote",
            AIRIS_GATEWAY["endpoint"],
            "--allow-http",
        ]
        result = _run_command(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            # May already be registered
            if "already exists" in (result.stderr or "").lower():
                click.echo("   ✅ Already registered with Claude Code")
            else:
                click.echo(f"   ⚠️  Registration warning: {result.stderr}", err=True)
        else:
            click.echo("   ✅ Registered with Claude Code")
    except Exception as e:
        click.echo(f"   ⚠️  Registration error: {e}", err=True)

    click.echo("\n✅ AIRIS MCP Gateway installed successfully!")
    click.echo(f"\n📁 Installed to: {install_dir}")
    click.echo("\n📖 Next steps:")
    click.echo("   • Health check: curl http://localhost:9400/health")
    click.echo("   • Web UI: http://localhost:9400")
    click.echo(f"   • Manage: cd {install_dir} && docker compose logs -f")
    click.echo(f"   • Documentation: {AIRIS_GATEWAY['repository']}")
    return True


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

        if result is None or result.returncode != 0:
            return False

        # Handle case where stdout might be None
        output = result.stdout
        if output is None:
            return False

        # Parse output to check if server is installed
        return server_name.lower() in output.lower()

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
    command = server_info["command"]

    click.echo(f"📦 Installing MCP server: {server_name}")

    # Check if already installed
    if check_mcp_server_installed(server_name):
        click.echo(f"   ✅ Already installed: {server_name}")
        return True

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


def list_available_servers():
    """List all available MCP servers."""
    click.echo("📋 Available MCP Servers:\n")

    # Show gateway option first
    click.echo("   ┌─────────────────────────────────────────────────────────────┐")
    click.echo("   │  🚀 AIRIS MCP Gateway (Recommended)                         │")
    gateway_installed = check_mcp_server_installed("airis-mcp-gateway")
    gateway_status = "✅ installed" if gateway_installed else "⬜ not installed"
    click.echo(f"   │     Status: {gateway_status:40} │")
    click.echo("   │     60+ tools, 98% token reduction, Web UI                  │")
    click.echo("   │     Install: superclaude mcp --servers airis-mcp-gateway    │")
    click.echo("   └─────────────────────────────────────────────────────────────┘")
    click.echo()
    click.echo("   Individual Servers (legacy):\n")

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

    click.echo(
        f"Total: {len(MCP_SERVERS)} individual servers + AIRIS Gateway available"
    )


def install_mcp_servers(
    selected_servers: Optional[List[str]] = None,
    scope: str = "user",
    dry_run: bool = False,
    use_gateway: Optional[bool] = None,
) -> Tuple[bool, str]:
    """
    Install MCP servers for Claude Code.

    Args:
        selected_servers: List of server names to install, or None for interactive selection
        scope: Installation scope (local, project, user)
        dry_run: If True, only show what would be done
        use_gateway: If True, install AIRIS MCP Gateway. If None, prompt user.

    Returns:
        Tuple of (success, message)
    """
    # Check prerequisites
    success, errors = check_prerequisites()
    if not success:
        error_msg = "Prerequisites not met:\n" + "\n".join(f"  ❌ {e}" for e in errors)
        return False, error_msg

    # Handle explicit gateway selection
    if selected_servers and "airis-mcp-gateway" in selected_servers:
        if install_airis_gateway(dry_run):
            return True, "AIRIS MCP Gateway installed successfully!"
        return False, "Failed to install AIRIS MCP Gateway"

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
        # Interactive selection - offer gateway first
        click.echo("\n🔌 SuperClaude MCP Server Installation\n")
        click.echo("Choose your installation method:\n")
        click.echo("   ┌─────────────────────────────────────────────────────────────┐")
        click.echo("   │  🚀 AIRIS MCP Gateway (Recommended)                         │")
        click.echo("   │     • 60+ tools through single endpoint                     │")
        click.echo("   │     • 98% token reduction with HOT/COLD management          │")
        click.echo("   │     • Web UI for server management                          │")
        click.echo("   │     • Requires: Docker                                      │")
        click.echo("   └─────────────────────────────────────────────────────────────┘")
        click.echo()
        click.echo("   Or install individual servers (legacy method):\n")

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

        click.echo()
        click.echo("   ─────────────────────────────────────────────────────────────")
        click.echo("   g. Install AIRIS MCP Gateway (recommended)")
        click.echo("   0. Install all individual servers")
        click.echo()

        selection = click.prompt(
            "Select option (g for gateway, 0 for all, or comma-separated numbers)",
            default="g",
        )

        if selection.strip().lower() == "g":
            # Install gateway
            if install_airis_gateway(dry_run):
                return True, "AIRIS MCP Gateway installed successfully!"
            return False, "Failed to install AIRIS MCP Gateway"
        elif selection.strip() == "0":
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
