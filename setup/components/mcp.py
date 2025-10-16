"""
MCP component for MCP server integration
"""

import os
import platform
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from setup import __version__

from ..core.base import Component


class MCPComponent(Component):
    """MCP servers integration component"""

    def __init__(self, install_dir: Optional[Path] = None):
        """Initialize MCP component"""
        super().__init__(install_dir)
        self.installed_servers_in_session: List[str] = []

        # Define MCP servers to install
        # Default: airis-mcp-gateway (unified gateway with all tools)
        # Legacy mode (--legacy flag): individual official servers
        self.mcp_servers_default = {
            "airis-mcp-gateway": {
                "name": "airis-mcp-gateway",
                "description": "Unified MCP Gateway with all tools (sequential-thinking, context7, magic, playwright, serena, morphllm, tavily, chrome-devtools, git, puppeteer)",
                "install_method": "github",
                "install_command": "uvx --from git+https://github.com/oraios/airis-mcp-gateway airis-mcp-gateway --help",
                "run_command": "uvx --from git+https://github.com/oraios/airis-mcp-gateway airis-mcp-gateway",
                "required": True,
            },
        }

        self.mcp_servers_legacy = {
            "sequential-thinking": {
                "name": "sequential-thinking",
                "description": "Multi-step problem solving and systematic analysis",
                "npm_package": "@modelcontextprotocol/server-sequential-thinking",
                "required": True,
            },
            "context7": {
                "name": "context7",
                "description": "Official library documentation and code examples",
                "npm_package": "@upstash/context7-mcp",
                "required": True,
            },
            "magic": {
                "name": "magic",
                "description": "Modern UI component generation and design systems",
                "npm_package": "@21st-dev/magic",
                "required": False,
                "api_key_env": "TWENTYFIRST_API_KEY",
                "api_key_description": "21st.dev API key for UI component generation",
            },
            "playwright": {
                "name": "playwright",
                "description": "Cross-browser E2E testing and automation",
                "npm_package": "@playwright/mcp@latest",
                "required": False,
            },
        }

        # Default to unified gateway
        self.mcp_servers = self.mcp_servers_default

    def get_metadata(self) -> Dict[str, str]:
        """Get component metadata"""
        return {
            "name": "mcp",
            "version": __version__,
            "description": "Unified MCP Gateway (airis-mcp-gateway) with all integrated tools",
            "category": "integration",
        }

    def is_reinstallable(self) -> bool:
        """This component manages sub-components (servers) and should be re-run."""
        return True

    def _run_command_cross_platform(
        self, cmd: List[str], **kwargs
    ) -> subprocess.CompletedProcess:
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

    def validate_prerequisites(
        self, installSubPath: Optional[Path] = None
    ) -> Tuple[bool, List[str]]:
        """Check prerequisites (varies based on legacy mode)"""
        errors = []

        # Check which server set we're using
        is_legacy = self.mcp_servers == self.mcp_servers_legacy

        # Check if Claude CLI is available (always required)
        try:
            result = self._run_command_cross_platform(
                ["claude", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                errors.append(
                    "Claude CLI not found - required for MCP server management"
                )
            else:
                version = result.stdout.strip()
                self.logger.debug(f"Found Claude CLI {version}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("Claude CLI not found - required for MCP server management")

        if is_legacy:
            # Legacy mode: requires Node.js and npm for official servers
            try:
                result = self._run_command_cross_platform(
                    ["node", "--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    errors.append("Node.js not found - required for legacy MCP servers")
                else:
                    version = result.stdout.strip()
                    self.logger.debug(f"Found Node.js {version}")
                    # Check version (require 18+)
                    try:
                        version_num = int(version.lstrip("v").split(".")[0])
                        if version_num < 18:
                            errors.append(
                                f"Node.js version {version} found, but version 18+ required"
                            )
                    except:
                        self.logger.warning(f"Could not parse Node.js version: {version}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                errors.append("Node.js not found - required for legacy MCP servers")

            try:
                result = self._run_command_cross_platform(
                    ["npm", "--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    errors.append("npm not found - required for legacy MCP server installation")
                else:
                    version = result.stdout.strip()
                    self.logger.debug(f"Found npm {version}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                errors.append("npm not found - required for legacy MCP server installation")
        else:
            # Default mode: requires uv for airis-mcp-gateway
            try:
                result = self._run_command_cross_platform(
                    ["uv", "--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    errors.append("uv not found - required for airis-mcp-gateway installation")
                else:
                    version = result.stdout.strip()
                    self.logger.debug(f"Found uv {version}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                errors.append("uv not found - required for airis-mcp-gateway installation")

        return len(errors) == 0, errors

    def get_files_to_install(self) -> List[Tuple[Path, Path]]:
        """Get files to install (none for MCP component)"""
        return []

    def get_metadata_modifications(self) -> Dict[str, Any]:
        """Get metadata modifications for MCP component"""
        return {
            "components": {
                "mcp": {
                    "version": __version__,
                    "installed": True,
                    "servers_count": len(self.installed_servers_in_session),
                }
            },
            "mcp": {
                "enabled": True,
                "servers": self.installed_servers_in_session,
                "auto_update": False,
            },
        }

    def _install_uv_mcp_server(
        self, server_info: Dict[str, Any], config: Dict[str, Any]
    ) -> bool:
        """Install a single MCP server using uv"""
        server_name = server_info["name"]
        install_command = server_info.get("install_command")
        run_command = server_info.get("run_command")

        if not install_command:
            self.logger.error(
                f"No install_command found for uv-based server {server_name}"
            )
            return False
        if not run_command:
            self.logger.error(f"No run_command found for uv-based server {server_name}")
            return False

        try:
            self.logger.info(f"Installing MCP server using uv: {server_name}")

            if self._check_mcp_server_installed(server_name):
                self.logger.info(f"MCP server {server_name} already installed")
                return True

            # Check if uv is available
            try:
                uv_check = self._run_command_cross_platform(
                    ["uv", "--version"], capture_output=True, text=True, timeout=10
                )
                if uv_check.returncode != 0:
                    self.logger.error(
                        f"uv not found - required for {server_name} installation"
                    )
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.logger.error(
                    f"uv not found - required for {server_name} installation"
                )
                return False

            if config.get("dry_run"):
                self.logger.info(
                    f"Would install MCP server (user scope): {install_command}"
                )
                self.logger.info(
                    f"Would register MCP server run command: {run_command}"
                )
                return True

            # Run install command
            self.logger.debug(f"Running: {install_command}")
            cmd_parts = shlex.split(install_command)
            result = self._run_command_cross_platform(
                cmd_parts, capture_output=True, text=True, timeout=900  # 15 minutes
            )

            if result.returncode == 0:
                self.logger.success(
                    f"Successfully installed MCP server (user scope): {server_name}"
                )

                # For Serena, we need to handle the run command specially
                if server_name == "serena":
                    # Serena needs project-specific registration, use current working directory
                    current_dir = os.getcwd()
                    serena_run_cmd = (
                        f"{run_command} --project {shlex.quote(current_dir)}"
                    )
                    self.logger.info(
                        f"Registering {server_name} with Claude CLI for project: {current_dir}"
                    )
                    reg_cmd = [
                        "claude",
                        "mcp",
                        "add",
                        "-s",
                        "user",
                        "--",
                        server_name,
                    ] + shlex.split(serena_run_cmd)
                else:
                    self.logger.info(
                        f"Registering {server_name} with Claude CLI. Run command: {run_command}"
                    )
                    reg_cmd = [
                        "claude",
                        "mcp",
                        "add",
                        "-s",
                        "user",
                        "--",
                        server_name,
                    ] + shlex.split(run_command)

                reg_result = self._run_command_cross_platform(
                    reg_cmd, capture_output=True, text=True, timeout=120
                )

                if reg_result.returncode == 0:
                    self.logger.success(
                        f"Successfully registered {server_name} with Claude CLI."
                    )
                    return True
                else:
                    error_msg = (
                        reg_result.stderr.strip()
                        if reg_result.stderr
                        else "Unknown error"
                    )
                    self.logger.error(
                        f"Failed to register MCP server {server_name} with Claude CLI: {error_msg}"
                    )
                    return False
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.logger.error(
                    f"Failed to install MCP server {server_name} using uv: {error_msg}\n{result.stdout}"
                )
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout installing MCP server {server_name} using uv")
            return False
        except Exception as e:
            self.logger.error(
                f"Error installing MCP server {server_name} using uv: {e}"
            )
            return False

    def _install_github_mcp_server(
        self, server_info: Dict[str, Any], config: Dict[str, Any]
    ) -> bool:
        """Install a single MCP server from GitHub using uvx"""
        server_name = server_info["name"]
        install_command = server_info.get("install_command")
        run_command = server_info.get("run_command")

        if not install_command:
            self.logger.error(
                f"No install_command found for GitHub-based server {server_name}"
            )
            return False
        if not run_command:
            self.logger.error(
                f"No run_command found for GitHub-based server {server_name}"
            )
            return False

        try:
            self.logger.info(f"Installing MCP server from GitHub: {server_name}")

            if self._check_mcp_server_installed(server_name):
                self.logger.info(f"MCP server {server_name} already installed")
                return True

            # Check if uvx is available
            try:
                uvx_check = self._run_command_cross_platform(
                    ["uvx", "--version"], capture_output=True, text=True, timeout=10
                )
                if uvx_check.returncode != 0:
                    self.logger.error(
                        f"uvx not found - required for {server_name} installation"
                    )
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.logger.error(
                    f"uvx not found - required for {server_name} installation"
                )
                return False

            if config.get("dry_run"):
                self.logger.info(
                    f"Would install MCP server from GitHub: {install_command}"
                )
                self.logger.info(
                    f"Would register MCP server run command: {run_command}"
                )
                return True

            # Run install command to test the GitHub installation
            self.logger.debug(f"Testing GitHub installation: {install_command}")
            cmd_parts = shlex.split(install_command)
            result = self._run_command_cross_platform(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for GitHub clone and build
            )

            if result.returncode == 0:
                self.logger.success(
                    f"Successfully tested GitHub MCP server: {server_name}"
                )

                # Register with Claude CLI using the run command
                self.logger.info(
                    f"Registering {server_name} with Claude CLI. Run command: {run_command}"
                )
                reg_cmd = [
                    "claude",
                    "mcp",
                    "add",
                    "-s",
                    "user",
                    "--",
                    server_name,
                ] + shlex.split(run_command)

                reg_result = self._run_command_cross_platform(
                    reg_cmd, capture_output=True, text=True, timeout=120
                )

                if reg_result.returncode == 0:
                    self.logger.success(
                        f"Successfully registered {server_name} with Claude CLI."
                    )
                    return True
                else:
                    error_msg = (
                        reg_result.stderr.strip()
                        if reg_result.stderr
                        else "Unknown error"
                    )
                    self.logger.error(
                        f"Failed to register MCP server {server_name} with Claude CLI: {error_msg}"
                    )
                    return False
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.logger.error(
                    f"Failed to install MCP server {server_name} from GitHub: {error_msg}\n{result.stdout}"
                )
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(
                f"Timeout installing MCP server {server_name} from GitHub"
            )
            return False
        except Exception as e:
            self.logger.error(
                f"Error installing MCP server {server_name} from GitHub: {e}"
            )
            return False

    def _check_mcp_server_installed(self, server_name: str) -> bool:
        """Check if MCP server is already installed"""
        try:
            result = self._run_command_cross_platform(
                ["claude", "mcp", "list"], capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                self.logger.warning(f"Could not list MCP servers: {result.stderr}")
                return False

            # Parse output to check if server is installed
            output = result.stdout.lower()
            return server_name.lower() in output

        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            self.logger.warning(f"Error checking MCP server status: {e}")
            return False

    def _detect_existing_mcp_servers_from_config(self) -> List[str]:
        """Detect existing MCP servers from Claude Desktop config"""
        detected_servers = []

        try:
            # Try to find Claude Desktop config file
            config_paths = [
                self.install_dir / "claude_desktop_config.json",
                Path.home() / ".claude" / "claude_desktop_config.json",
                Path.home() / ".claude.json",  # Claude CLI config
                Path.home()
                / "AppData"
                / "Roaming"
                / "Claude"
                / "claude_desktop_config.json",  # Windows
                Path.home()
                / "Library"
                / "Application Support"
                / "Claude"
                / "claude_desktop_config.json",  # macOS
            ]

            config_file = None
            for path in config_paths:
                if path.exists():
                    config_file = path
                    break

            if not config_file:
                self.logger.debug("No Claude Desktop config file found")
                return detected_servers

            import json

            with open(config_file, "r") as f:
                config = json.load(f)

            # Extract MCP server names from mcpServers section
            mcp_servers = config.get("mcpServers", {})
            for server_name in mcp_servers.keys():
                # Map common name variations to our standard names
                normalized_name = self._normalize_server_name(server_name)
                if normalized_name and normalized_name in self.mcp_servers:
                    detected_servers.append(normalized_name)

            if detected_servers:
                self.logger.info(
                    f"Detected existing MCP servers from config: {detected_servers}"
                )

        except Exception as e:
            self.logger.warning(f"Could not read Claude Desktop config: {e}")

        return detected_servers

    def _detect_existing_mcp_servers_from_cli(self) -> List[str]:
        """Detect existing MCP servers from Claude CLI"""
        detected_servers = []

        try:
            result = self._run_command_cross_platform(
                ["claude", "mcp", "list"], capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                self.logger.debug(f"Could not list MCP servers: {result.stderr}")
                return detected_servers

            # Parse the output to extract server names
            output_lines = result.stdout.strip().split("\n")
            for line in output_lines:
                line = line.strip().lower()
                if line and not line.startswith("#") and not line.startswith("no"):
                    # Extract server name (usually the first word or before first space/colon)
                    server_name = line.split()[0] if line.split() else ""
                    normalized_name = self._normalize_server_name(server_name)
                    if normalized_name and normalized_name in self.mcp_servers:
                        detected_servers.append(normalized_name)

            if detected_servers:
                self.logger.info(
                    f"Detected existing MCP servers from CLI: {detected_servers}"
                )

        except Exception as e:
            self.logger.warning(f"Could not detect existing MCP servers from CLI: {e}")

        return detected_servers

    def _normalize_server_name(self, server_name: str) -> Optional[str]:
        """Normalize server name to match our internal naming"""
        if not server_name:
            return None

        server_name = server_name.lower().strip()

        # Map common variations to our standard names
        name_mappings = {
            "airis-mcp-gateway": "airis-mcp-gateway",
            "airis": "airis-mcp-gateway",
            "gateway": "airis-mcp-gateway",
        }

        return name_mappings.get(server_name)

    def _merge_server_lists(
        self,
        existing_servers: List[str],
        selected_servers: List[str],
        previous_servers: List[str],
    ) -> List[str]:
        """Merge existing, selected, and previously installed servers"""
        all_servers = set()

        # Add all detected servers
        all_servers.update(existing_servers)
        all_servers.update(selected_servers)
        all_servers.update(previous_servers)

        # Filter to only include servers we know how to install
        valid_servers = [s for s in all_servers if s in self.mcp_servers]

        if valid_servers:
            self.logger.info(f"Total servers to manage: {valid_servers}")
            if existing_servers:
                self.logger.info(f"  - Existing: {existing_servers}")
            if selected_servers:
                self.logger.info(f"  - Newly selected: {selected_servers}")
            if previous_servers:
                self.logger.info(f"  - Previously installed: {previous_servers}")

        return valid_servers

    def _install_mcp_server(
        self, server_info: Dict[str, Any], config: Dict[str, Any]
    ) -> bool:
        """Install a single MCP server"""
        if server_info.get("install_method") == "uv":
            return self._install_uv_mcp_server(server_info, config)
        elif server_info.get("install_method") == "github":
            return self._install_github_mcp_server(server_info, config)

        server_name = server_info["name"]
        npm_package = server_info.get("npm_package")
        install_command = server_info.get("install_command")

        if not npm_package and not install_command:
            self.logger.error(
                f"No npm_package or install_command found for server {server_name}"
            )
            return False

        command = "npx"

        try:
            self.logger.info(f"Installing MCP server: {server_name}")

            # Check if already installed
            if self._check_mcp_server_installed(server_name):
                self.logger.info(f"MCP server {server_name} already installed")
                return True

            # Handle API key requirements
            if "api_key_env" in server_info:
                api_key_env = server_info["api_key_env"]
                api_key_desc = server_info.get(
                    "api_key_description", f"API key for {server_name}"
                )

                if not config.get("dry_run", False):
                    self.logger.info(f"MCP server '{server_name}' requires an API key")
                    self.logger.info(f"Environment variable: {api_key_env}")
                    self.logger.info(f"Description: {api_key_desc}")

                    # Check if API key is already set
                    import os

                    if not os.getenv(api_key_env):
                        self.logger.warning(
                            f"API key {api_key_env} not found in environment"
                        )
                        self.logger.warning(
                            f"Proceeding without {api_key_env} - server may not function properly"
                        )

            # Install using Claude CLI
            if install_command:
                # Use the full install command (e.g., for tavily-mcp@0.1.2)
                install_args = install_command.split()
                if config.get("dry_run"):
                    self.logger.info(
                        f"Would install MCP server (user scope): claude mcp add -s user {server_name} {' '.join(install_args)}"
                    )
                    return True

                self.logger.debug(
                    f"Running: claude mcp add -s user {server_name} {' '.join(install_args)}"
                )

                result = self._run_command_cross_platform(
                    ["claude", "mcp", "add", "-s", "user", "--", server_name]
                    + install_args,
                    capture_output=True,
                    text=True,
                    timeout=120,  # 2 minutes timeout for installation
                )
            else:
                # Use npm_package
                if config.get("dry_run"):
                    self.logger.info(
                        f"Would install MCP server (user scope): claude mcp add -s user {server_name} {command} -y {npm_package}"
                    )
                    return True

                self.logger.debug(
                    f"Running: claude mcp add -s user {server_name} {command} -y {npm_package}"
                )

                result = self._run_command_cross_platform(
                    [
                        "claude",
                        "mcp",
                        "add",
                        "-s",
                        "user",
                        "--",
                        server_name,
                        command,
                        "-y",
                        npm_package,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,  # 2 minutes timeout for installation
                )

            if result.returncode == 0:
                self.logger.success(
                    f"Successfully installed MCP server (user scope): {server_name}"
                )
                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.logger.error(
                    f"Failed to install MCP server {server_name}: {error_msg}"
                )
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout installing MCP server {server_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error installing MCP server {server_name}: {e}")
            return False

    def _uninstall_mcp_server(self, server_name: str) -> bool:
        """Uninstall a single MCP server"""
        try:
            self.logger.info(f"Uninstalling MCP server: {server_name}")

            # Check if installed
            if not self._check_mcp_server_installed(server_name):
                self.logger.info(f"MCP server {server_name} not installed")
                return True

            self.logger.debug(
                f"Running: claude mcp remove {server_name} (auto-detect scope)"
            )

            result = self._run_command_cross_platform(
                ["claude", "mcp", "remove", server_name],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.logger.success(
                    f"Successfully uninstalled MCP server: {server_name}"
                )
                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.logger.error(
                    f"Failed to uninstall MCP server {server_name}: {error_msg}"
                )
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout uninstalling MCP server {server_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error uninstalling MCP server {server_name}: {e}")
            return False

    def _install(self, config: Dict[str, Any]) -> bool:
        """Install MCP component with auto-detection of existing servers"""
        # Check for legacy mode flag
        use_legacy = config.get("legacy_mode", False) or config.get("official_servers", False)

        if use_legacy:
            self.logger.info("Installing individual official MCP servers (legacy mode)...")
            self.mcp_servers = self.mcp_servers_legacy
        else:
            self.logger.info("Installing unified MCP gateway (airis-mcp-gateway)...")
            self.mcp_servers = self.mcp_servers_default

        # Validate prerequisites
        success, errors = self.validate_prerequisites()
        if not success:
            for error in errors:
                self.logger.error(error)
            return False

        # Auto-detect existing servers
        self.logger.info("Auto-detecting existing MCP servers...")
        existing_from_config = self._detect_existing_mcp_servers_from_config()
        existing_from_cli = self._detect_existing_mcp_servers_from_cli()
        existing_servers = list(set(existing_from_config + existing_from_cli))

        # Get selected servers from config
        selected_servers = config.get("selected_mcp_servers", [])

        # Get previously installed servers from metadata
        previous_servers = self.settings_manager.get_metadata_setting("mcp.servers", [])

        # Merge all server lists
        all_servers = self._merge_server_lists(
            existing_servers, selected_servers, previous_servers
        )

        if not all_servers:
            self.logger.info(
                "No MCP servers detected or selected. Skipping MCP installation."
            )
            # Still run post-install to update metadata
            return self._post_install()

        self.logger.info(f"Managing MCP servers: {', '.join(all_servers)}")

        # Install/verify each server
        installed_count = 0
        failed_servers = []
        verified_servers = []

        for server_name in all_servers:
            if server_name in self.mcp_servers:
                server_info = self.mcp_servers[server_name]

                # Check if already installed and working
                if self._check_mcp_server_installed(server_name):
                    self.logger.info(
                        f"MCP server {server_name} already installed and working"
                    )
                    installed_count += 1
                    verified_servers.append(server_name)
                else:
                    # Try to install
                    if self._install_mcp_server(server_info, config):
                        installed_count += 1
                        verified_servers.append(server_name)
                    else:
                        failed_servers.append(server_name)

                        # Check if this is a required server
                        if server_info.get("required", False):
                            self.logger.error(
                                f"Required MCP server {server_name} failed to install"
                            )
                            return False
            else:
                self.logger.warning(
                    f"Unknown MCP server '{server_name}' cannot be managed by SuperClaude"
                )

        # Update the list of successfully managed servers
        self.installed_servers_in_session = verified_servers

        # Verify installation
        if not config.get("dry_run", False):
            self.logger.info("Verifying MCP server installation...")
            try:
                result = self._run_command_cross_platform(
                    ["claude", "mcp", "list"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    self.logger.debug("MCP servers list:")
                    for line in result.stdout.strip().split("\n"):
                        if line.strip():
                            self.logger.debug(f"  {line.strip()}")
                else:
                    self.logger.warning("Could not verify MCP server installation")

            except Exception as e:
                self.logger.warning(f"Could not verify MCP installation: {e}")

        if failed_servers:
            self.logger.warning(f"Some MCP servers failed to install: {failed_servers}")
            self.logger.success(
                f"MCP component partially managed ({installed_count} servers)"
            )
        else:
            self.logger.success(
                f"MCP component successfully managing ({installed_count} servers)"
            )

        return self._post_install()

    def _post_install(self) -> bool:
        """Post-installation tasks"""
        # Update metadata
        try:
            metadata_mods = self.get_metadata_modifications()
            self.settings_manager.update_metadata(metadata_mods)

            # Add component registration to metadata
            self.settings_manager.add_component_registration(
                "mcp",
                {
                    "version": __version__,
                    "category": "integration",
                    "servers_count": len(self.installed_servers_in_session),
                    "installed_servers": self.installed_servers_in_session,
                },
            )

            self.logger.info("Updated metadata with MCP component registration")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {e}")
            return False

    def uninstall(self) -> bool:
        """Uninstall MCP component"""
        try:
            self.logger.info("Uninstalling SuperClaude MCP servers...")

            # Uninstall each MCP server
            uninstalled_count = 0

            for server_name in self.mcp_servers.keys():
                if self._uninstall_mcp_server(server_name):
                    uninstalled_count += 1

            # Update metadata to remove MCP component
            try:
                if self.settings_manager.is_component_installed("mcp"):
                    self.settings_manager.remove_component_registration("mcp")
                    # Also remove MCP configuration from metadata
                    metadata = self.settings_manager.load_metadata()
                    if "mcp" in metadata:
                        del metadata["mcp"]
                        self.settings_manager.save_metadata(metadata)
                    self.logger.info("Removed MCP component from metadata")
            except Exception as e:
                self.logger.warning(f"Could not update metadata: {e}")

            self.logger.success(
                f"MCP component uninstalled ({uninstalled_count} servers removed)"
            )
            return True

        except Exception as e:
            self.logger.exception(f"Unexpected error during MCP uninstallation: {e}")
            return False

    def get_dependencies(self) -> List[str]:
        """Get dependencies"""
        return ["framework_docs"]

    def update(self, config: Dict[str, Any]) -> bool:
        """Update MCP component"""
        try:
            self.logger.info("Updating SuperClaude MCP servers...")

            # Check current version
            current_version = self.settings_manager.get_component_version("mcp")
            target_version = self.get_metadata()["version"]

            if current_version == target_version:
                self.logger.info(f"MCP component already at version {target_version}")
                return True

            self.logger.info(
                f"Updating MCP component from {current_version} to {target_version}"
            )

            # For MCP servers, update means reinstall to get latest versions
            updated_count = 0
            failed_servers = []

            for server_name, server_info in self.mcp_servers.items():
                try:
                    # Uninstall old version
                    if self._check_mcp_server_installed(server_name):
                        self._uninstall_mcp_server(server_name)

                    # Install new version
                    if self._install_mcp_server(server_info, config):
                        updated_count += 1
                    else:
                        failed_servers.append(server_name)

                except Exception as e:
                    self.logger.error(f"Error updating MCP server {server_name}: {e}")
                    failed_servers.append(server_name)

            # Update metadata
            try:
                # Update component version in metadata
                metadata = self.settings_manager.load_metadata()
                if "components" in metadata and "mcp" in metadata["components"]:
                    metadata["components"]["mcp"]["version"] = target_version
                    metadata["components"]["mcp"]["servers_count"] = len(
                        self.mcp_servers
                    )
                if "mcp" in metadata:
                    metadata["mcp"]["servers"] = list(self.mcp_servers.keys())
                self.settings_manager.save_metadata(metadata)
            except Exception as e:
                self.logger.warning(f"Could not update metadata: {e}")

            if failed_servers:
                self.logger.warning(
                    f"Some MCP servers failed to update: {failed_servers}"
                )
                return False
            else:
                self.logger.success(
                    f"MCP component updated to version {target_version}"
                )
                return True

        except Exception as e:
            self.logger.exception(f"Unexpected error during MCP update: {e}")
            return False

    def validate_installation(self) -> Tuple[bool, List[str]]:
        """Validate MCP component installation"""
        errors = []

        # Check metadata registration
        if not self.settings_manager.is_component_installed("mcp"):
            errors.append("MCP component not registered in metadata")
            return False, errors

        # Check version matches
        installed_version = self.settings_manager.get_component_version("mcp")
        expected_version = self.get_metadata()["version"]
        if installed_version != expected_version:
            errors.append(
                f"Version mismatch: installed {installed_version}, expected {expected_version}"
            )

        # Check if Claude CLI is available and validate installed servers
        try:
            result = self._run_command_cross_platform(
                ["claude", "mcp", "list"], capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                errors.append(
                    "Could not communicate with Claude CLI for MCP server verification"
                )
            else:
                claude_mcp_output = result.stdout.lower()

                # Get the list of servers that should be installed from metadata
                installed_servers = self.settings_manager.get_metadata_setting(
                    "mcp.servers", []
                )

                for server_name in installed_servers:
                    if server_name.lower() not in claude_mcp_output:
                        errors.append(
                            f"Installed MCP server '{server_name}' not found in 'claude mcp list' output."
                        )

        except Exception as e:
            errors.append(f"Could not verify MCP server installation: {e}")

        return len(errors) == 0, errors

    def _get_source_dir(self):
        """Get source directory for framework files"""
        return None

    def get_size_estimate(self) -> int:
        """Get estimated installation size"""
        # MCP servers are installed via npm, estimate based on typical sizes
        base_size = 50 * 1024 * 1024  # ~50MB for all servers combined
        return base_size

    def get_installation_summary(self) -> Dict[str, Any]:
        """Get installation summary"""
        return {
            "component": self.get_metadata()["name"],
            "version": self.get_metadata()["version"],
            "servers_count": 1,  # Only airis-mcp-gateway
            "mcp_servers": ["airis-mcp-gateway"],
            "included_tools": [
                "sequential-thinking",
                "context7",
                "magic",
                "playwright",
                "serena",
                "morphllm",
                "tavily",
                "chrome-devtools",
                "git",
                "puppeteer",
            ],
            "estimated_size": self.get_size_estimate(),
            "dependencies": self.get_dependencies(),
            "required_tools": ["uv", "claude"],
        }
