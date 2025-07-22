"""
MCP component for MCP server integration
"""

import subprocess
import sys
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

from ..base.component import Component
from ..utils.ui import display_info, display_warning


class MCPComponent(Component):
    """MCP servers integration component"""
    
    def __init__(self, install_dir: Optional[Path] = None):
        """Initialize MCP component"""
        super().__init__(install_dir)
        
        # Define MCP servers to install
        self.mcp_servers = {
            "sequential-thinking": {
                "name": "sequential-thinking",
                "description": "Multi-step problem solving and systematic analysis",
                "npm_package": "@modelcontextprotocol/server-sequential-thinking",
                "required": True
            },
            "context7": {
                "name": "context7", 
                "description": "Official library documentation and code examples",
                "npm_package": "@upstash/context7-mcp",
                "required": True
            },
            "magic": {
                "name": "magic",
                "description": "Modern UI component generation and design systems",
                "npm_package": "@21st-dev/magic",
                "required": False,
                "api_key_env": "TWENTYFIRST_API_KEY",
                "api_key_description": "21st.dev API key for UI component generation"
            },
            "playwright": {
                "name": "playwright",
                "description": "Cross-browser E2E testing and automation",
                "npm_package": "@playwright/mcp@latest",
                "required": False
            }
        }
    
    def get_metadata(self) -> Dict[str, str]:
        """Get component metadata"""
        return {
            "name": "mcp",
            "version": "3.0.0",
            "description": "MCP server integration (Context7, Sequential, Magic, Playwright)",
            "category": "integration"
        }
    
    def validate_prerequisites(self, installSubPath: Optional[Path] = None) -> Tuple[bool, List[str]]:
        """Check prerequisites"""
        errors = []
        
        # Check if Node.js is available
        try:
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10,
                shell=(sys.platform == "win32")
            )
            if result.returncode != 0:
                errors.append("Node.js not found - required for MCP servers")
            else:
                version = result.stdout.strip()
                self.logger.debug(f"Found Node.js {version}")
                
                # Check version (require 18+)
                try:
                    version_num = int(version.lstrip('v').split('.')[0])
                    if version_num < 18:
                        errors.append(f"Node.js version {version} found, but version 18+ required")
                except:
                    self.logger.warning(f"Could not parse Node.js version: {version}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("Node.js not found - required for MCP servers")
        
        # Check if Claude CLI is available
        try:
            result = subprocess.run(
                ["claude", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10,
                shell=(sys.platform == "win32")
            )
            if result.returncode != 0:
                errors.append("Claude CLI not found - required for MCP server management")
            else:
                version = result.stdout.strip()
                self.logger.debug(f"Found Claude CLI {version}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("Claude CLI not found - required for MCP server management")
        
        # Check if npm is available
        try:
            result = subprocess.run(
                ["npm", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10,
                shell=(sys.platform == "win32")
            )
            if result.returncode != 0:
                errors.append("npm not found - required for MCP server installation")
            else:
                version = result.stdout.strip()
                self.logger.debug(f"Found npm {version}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("npm not found - required for MCP server installation")
        
        return len(errors) == 0, errors
    
    def get_files_to_install(self) -> List[Tuple[Path, Path]]:
        """Get files to install (none for MCP component)"""
        return []
    
    def get_metadata_modifications(self) -> Dict[str, Any]:
        """Get metadata modifications for MCP component"""
        return {
            "components": {
                "mcp": {
                    "version": "3.0.0",
                    "installed": True,
                    "servers_count": len(self.mcp_servers)
                }
            },
            "mcp": {
                "enabled": True,
                "servers": list(self.mcp_servers.keys()),
                "auto_update": False
            }
        }
    
    def _check_mcp_server_installed(self, server_name: str) -> bool:
        """Check if MCP server is already installed"""
        try:
            result = subprocess.run(
                ["claude", "mcp", "list"], 
                capture_output=True, 
                text=True, 
                timeout=15,
                shell=(sys.platform == "win32")
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
    
    def _install_mcp_server(self, server_info: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Install a single MCP server"""
        server_name = server_info["name"]
        npm_package = server_info["npm_package"]
        
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
                api_key_desc = server_info.get("api_key_description", f"API key for {server_name}")
                
                if not config.get("dry_run", False):
                    display_info(f"MCP server '{server_name}' requires an API key")
                    display_info(f"Environment variable: {api_key_env}")
                    display_info(f"Description: {api_key_desc}")
                    
                    # Check if API key is already set
                    import os
                    if not os.getenv(api_key_env):
                        display_warning(f"API key {api_key_env} not found in environment")
                        self.logger.warning(f"Proceeding without {api_key_env} - server may not function properly")
            
            # Install using Claude CLI
            if config.get("dry_run"):
                self.logger.info(f"Would install MCP server (user scope): claude mcp add -s user {server_name} {command} -y {npm_package}")
                return True
            
            self.logger.debug(f"Running: claude mcp add -s user {server_name} {command} -y {npm_package}")
            
            result = subprocess.run(
                ["claude", "mcp", "add", "-s", "user", "--", server_name, command, "-y", npm_package],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minutes timeout for installation
                shell=(sys.platform == "win32")
            )
            
            if result.returncode == 0:
                self.logger.success(f"Successfully installed MCP server (user scope): {server_name}")
                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.logger.error(f"Failed to install MCP server {server_name}: {error_msg}")
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
            
            self.logger.debug(f"Running: claude mcp remove {server_name} (auto-detect scope)")
            
            result = subprocess.run(
                ["claude", "mcp", "remove", server_name],
                capture_output=True,
                text=True,
                timeout=60,
                shell=(sys.platform == "win32")
            )
            
            if result.returncode == 0:
                self.logger.success(f"Successfully uninstalled MCP server: {server_name}")
                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.logger.error(f"Failed to uninstall MCP server {server_name}: {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout uninstalling MCP server {server_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error uninstalling MCP server {server_name}: {e}")
            return False
    
    def _install(self, config: Dict[str, Any]) -> bool:
        """Install MCP component"""
        self.logger.info("Installing SuperClaude MCP servers...")

        # Validate prerequisites
        success, errors = self.validate_prerequisites()
        if not success:
            for error in errors:
                self.logger.error(error)
            return False

        # Install each MCP server
        installed_count = 0
        failed_servers = []

        for server_name, server_info in self.mcp_servers.items():
            if self._install_mcp_server(server_info, config):
                installed_count += 1
            else:
                failed_servers.append(server_name)
                
                # Check if this is a required server
                if server_info.get("required", False):
                    self.logger.error(f"Required MCP server {server_name} failed to install")
                    return False

        # Verify installation
        if not config.get("dry_run", False):
            self.logger.info("Verifying MCP server installation...")
            try:
                result = subprocess.run(
                    ["claude", "mcp", "list"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    shell=(sys.platform == "win32")
                )
                
                if result.returncode == 0:
                    self.logger.debug("MCP servers list:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            self.logger.debug(f"  {line.strip()}")
                else:
                    self.logger.warning("Could not verify MCP server installation")
                    
            except Exception as e:
                self.logger.warning(f"Could not verify MCP installation: {e}")

        if failed_servers:
            self.logger.warning(f"Some MCP servers failed to install: {failed_servers}")
            self.logger.success(f"MCP component partially installed ({installed_count} servers)")
        else:
            self.logger.success(f"MCP component installed successfully ({installed_count} servers)")

        return self._post_install()

    def _post_install(self) -> bool:
        # Update metadata
        try:
            metadata_mods = self.get_metadata_modifications()
            self.settings_manager.update_metadata(metadata_mods)

            # Add component registration to metadata
            self.settings_manager.add_component_registration("mcp", {
                "version": "3.0.0",
                "category": "integration",
                "servers_count": len(self.mcp_servers)
            })

            self.logger.info("Updated metadata with MCP component registration")
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {e}")
            return False

        return True

    
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
            
            self.logger.success(f"MCP component uninstalled ({uninstalled_count} servers removed)")
            return True
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during MCP uninstallation: {e}")
            return False
    
    def get_dependencies(self) -> List[str]:
        """Get dependencies"""
        return ["core"]
    
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
            
            self.logger.info(f"Updating MCP component from {current_version} to {target_version}")
            
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
                    metadata["components"]["mcp"]["servers_count"] = len(self.mcp_servers)
                if "mcp" in metadata:
                    metadata["mcp"]["servers"] = list(self.mcp_servers.keys())
                self.settings_manager.save_metadata(metadata)
            except Exception as e:
                self.logger.warning(f"Could not update metadata: {e}")
            
            if failed_servers:
                self.logger.warning(f"Some MCP servers failed to update: {failed_servers}")
                return False
            else:
                self.logger.success(f"MCP component updated to version {target_version}")
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
            errors.append(f"Version mismatch: installed {installed_version}, expected {expected_version}")
        
        # Check if Claude CLI is available
        try:
            result = subprocess.run(
                ["claude", "mcp", "list"],
                capture_output=True,
                text=True,
                timeout=15,
                shell=(sys.platform == "win32")
            )
            
            if result.returncode != 0:
                errors.append("Could not communicate with Claude CLI for MCP server verification")
            else:
                # Check if required servers are installed
                output = result.stdout.lower()
                for server_name, server_info in self.mcp_servers.items():
                    if server_info.get("required", False):
                        if server_name.lower() not in output:
                            errors.append(f"Required MCP server not found: {server_name}")
                            
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
            "servers_count": len(self.mcp_servers),
            "mcp_servers": list(self.mcp_servers.keys()),
            "estimated_size": self.get_size_estimate(),
            "dependencies": self.get_dependencies(),
            "required_tools": ["node", "npm", "claude"]
        }
