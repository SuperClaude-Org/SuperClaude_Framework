"""
MCP component for MCP server configuration via .claude.json
"""

import json
import shutil
import time
import sys
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# Platform-specific file locking imports
try:
    if sys.platform == "win32":
        import msvcrt
        LOCKING_AVAILABLE = "windows"
    else:
        import fcntl
        LOCKING_AVAILABLE = "unix"
except ImportError:
    LOCKING_AVAILABLE = None

from ..core.base import Component
from ..utils.ui import display_info, display_warning


class MCPComponent(Component):
    """MCP servers configuration component"""
    
    def __init__(self, install_dir: Optional[Path] = None):
        """Initialize MCP component"""
        super().__init__(install_dir)
        
        # Define MCP servers available for configuration
        self.mcp_servers = {
            "context7": {
                "name": "context7",
                "description": "Official library documentation and code examples",
                "config_file": "context7.json",
                "requires_api_key": False
            },
            "sequential": {
                "name": "sequential-thinking", 
                "description": "Multi-step problem solving and systematic analysis",
                "config_file": "sequential.json",
                "requires_api_key": False
            },
            "magic": {
                "name": "magic",
                "description": "Modern UI component generation and design systems",
                "config_file": "magic.json",
                "requires_api_key": True,
                "api_key_env": "TWENTYFIRST_API_KEY"
            },
            "playwright": {
                "name": "playwright",
                "description": "Cross-browser E2E testing and automation",
                "config_file": "playwright.json", 
                "requires_api_key": False
            },
            "serena": {
                "name": "serena",
                "description": "Semantic code analysis and intelligent editing",
                "config_file": "serena.json",
                "requires_api_key": False
            },
            "morphllm": {
                "name": "morphllm-fast-apply",
                "description": "Fast Apply capability for context-aware code modifications",
                "config_file": "morphllm.json",
                "requires_api_key": True,
                "api_key_env": "MORPH_API_KEY"
            }
        }
        
        # This will be set during installation - initialize as empty list
        self.selected_servers: List[str] = []
        
        # Store collected API keys for configuration
        self.collected_api_keys: Dict[str, str] = {}
    
    def _lock_file(self, file_handle, exclusive: bool = False):
        """Cross-platform file locking"""
        if LOCKING_AVAILABLE == "unix":
            lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(file_handle.fileno(), lock_type)
        elif LOCKING_AVAILABLE == "windows":
            # Windows locking using msvcrt
            if exclusive:
                msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, 1)
        # If no locking available, continue without locking
    
    def _unlock_file(self, file_handle):
        """Cross-platform file unlocking"""
        if LOCKING_AVAILABLE == "unix":
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
        elif LOCKING_AVAILABLE == "windows":
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
        # If no locking available, continue without unlocking
    
    def get_metadata(self) -> Dict[str, str]:
        """Get component metadata"""
        return {
            "name": "mcp",
            "version": "4.0.6",
            "description": "MCP server configuration management via .claude.json",
            "category": "integration"
        }
    
    def set_selected_servers(self, selected_servers: List[str]) -> None:
        """Set which MCP servers were selected for configuration"""
        self.selected_servers = selected_servers
        self.logger.debug(f"MCP servers to configure: {selected_servers}")
    
    def validate_prerequisites(self, installSubPath: Optional[Path] = None) -> Tuple[bool, List[str]]:
        """
        Check prerequisites for MCP component
        """
        errors = []
        
        # Check if config source directory exists
        source_dir = self._get_config_source_dir()
        if not source_dir or not source_dir.exists():
            errors.append(f"MCP config source directory not found: {source_dir}")
            return False, errors
        
        # Check if user's Claude config exists
        claude_config = Path.home() / ".claude.json"
        if not claude_config.exists():
            errors.append(f"Claude configuration file not found: {claude_config}")
            errors.append("Please run Claude Code at least once to create the configuration file")
        
        return len(errors) == 0, errors
    
    def get_files_to_install(self) -> List[Tuple[Path, Path]]:
        """MCP component doesn't install files - it modifies .claude.json"""
        return []
    
    def _get_config_source_dir(self) -> Optional[Path]:
        """Get source directory for MCP config files"""
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "SuperClaude" / "MCP" / "configs"
        
        if not config_dir.exists():
            return None
        
        return config_dir
    
    def _get_source_dir(self) -> Optional[Path]:
        """Override parent method - MCP component doesn't use traditional file installation"""
        return self._get_config_source_dir()
    
    def _load_claude_config(self) -> Tuple[Optional[Dict], Path]:
        """Load user's Claude configuration with file locking"""
        claude_config_path = Path.home() / ".claude.json"
        
        try:
            with open(claude_config_path, 'r') as f:
                # Apply shared lock for reading
                self._lock_file(f, exclusive=False)
                try:
                    config = json.load(f)
                    return config, claude_config_path
                finally:
                    self._unlock_file(f)
        except Exception as e:
            self.logger.error(f"Failed to load Claude config: {e}")
            return None, claude_config_path
    
    def _save_claude_config(self, config: Dict, config_path: Path) -> bool:
        """Save user's Claude configuration with backup and file locking"""
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Create backup first
                if config_path.exists():
                    backup_path = config_path.with_suffix('.json.backup')
                    shutil.copy2(config_path, backup_path)
                    self.logger.debug(f"Created backup: {backup_path}")
                
                # Save updated config with exclusive lock
                with open(config_path, 'w') as f:
                    # Apply exclusive lock for writing
                    self._lock_file(f, exclusive=True)
                    try:
                        json.dump(config, f, indent=2)
                        f.flush()  # Ensure data is written
                    finally:
                        self._unlock_file(f)
                
                self.logger.debug("Updated Claude configuration")
                return True
                
            except (OSError, IOError) as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"File lock attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    self.logger.error(f"Failed to save Claude config after {max_retries} attempts: {e}")
                    return False
            except Exception as e:
                self.logger.error(f"Failed to save Claude config: {e}")
                return False
        
        return False
    
    def _merge_mcp_server_config(self, existing_config: Dict, new_config: Dict, server_key: str) -> None:
        """Precisely merge MCP server config, preserving user customizations
        
        Args:
            existing_config: User's current mcpServers configuration
            new_config: New MCP server configuration to merge
            server_key: Server key for logging purposes
        """
        for server_name, server_def in new_config.items():
            if server_name in existing_config:
                # Server already exists - preserve user customizations
                existing_server = existing_config[server_name]
                
                # Only add missing keys, never overwrite existing ones
                for key, value in server_def.items():
                    if key not in existing_server:
                        existing_server[key] = value
                        self.logger.debug(f"Added missing key '{key}' to existing server '{server_name}'")
                    else:
                        self.logger.debug(f"Preserved user customization for '{server_name}.{key}'")
                
                # NEW: Apply environment variable references for API keys
                if "env" in existing_server and self.collected_api_keys:
                    for env_key, env_value in existing_server["env"].items():
                        if env_key in self.collected_api_keys and env_value == "":
                            # Update to use environment variable reference
                            existing_server["env"][env_key] = f"${{{env_key}}}"
                            self.logger.info(f"Configured {env_key} to use environment variable")
                
                self.logger.info(f"Updated existing MCP server '{server_name}' (preserved user customizations)")
            else:
                # New server - add complete configuration
                # Apply environment variable references if we have collected keys
                if "env" in server_def and self.collected_api_keys:
                    for env_key in server_def["env"]:
                        if env_key in self.collected_api_keys and server_def["env"][env_key] == "":
                            server_def["env"][env_key] = f"${{{env_key}}}"
                
                existing_config[server_name] = server_def
                self.logger.info(f"Added new MCP server '{server_name}' from {server_key}")
    
    def _load_mcp_server_config(self, server_key: str) -> Optional[Dict]:
        """Load MCP server configuration snippet"""
        if server_key not in self.mcp_servers:
            return None
        
        server_info = self.mcp_servers[server_key]
        config_file = server_info["config_file"]
        config_source_dir = self._get_config_source_dir()
        
        if not config_source_dir:
            return None
        
        config_path = config_source_dir / config_file
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load MCP config for {server_key}: {e}")
            return None
    
    def _install(self, config: Dict[str, Any]) -> bool:
        """Install MCP component by configuring .claude.json"""
        self.logger.info("Configuring MCP servers in Claude...")
        
        # Get selected servers from config
        selected_servers = config.get("selected_mcp_servers", [])
        if not selected_servers:
            self.logger.info("No MCP servers selected - skipping MCP configuration")
            return True
        
        self.set_selected_servers(selected_servers)
        
        # NEW: Log collected API keys information
        if hasattr(self, 'collected_api_keys') and self.collected_api_keys:
            self.logger.info(f"Using {len(self.collected_api_keys)} collected API keys for configuration")
        
        # Validate prerequisites
        success, errors = self.validate_prerequisites()
        if not success:
            for error in errors:
                self.logger.error(error)
            return False
        
        # Load Claude configuration
        claude_config, config_path = self._load_claude_config()
        if claude_config is None:
            return False
        
        # Ensure mcpServers section exists
        if "mcpServers" not in claude_config:
            claude_config["mcpServers"] = {}
        
        # Configure each selected server
        configured_count = 0
        for server_key in selected_servers:
            if server_key not in self.mcp_servers:
                self.logger.warning(f"Unknown MCP server: {server_key}")
                continue
            
            server_info = self.mcp_servers[server_key]
            server_config = self._load_mcp_server_config(server_key)
            
            if server_config is None:
                self.logger.error(f"Failed to load configuration for {server_key}")
                continue
            
            # Handle API key requirements
            if server_info.get("requires_api_key", False):
                api_key_env = server_info.get("api_key_env")
                if api_key_env:
                    display_info(f"Server '{server_key}' requires API key: {api_key_env}")
                    display_info("You can set this environment variable later")
            
            # Precisely merge server config, preserving user customizations
            self._merge_mcp_server_config(claude_config["mcpServers"], server_config, server_key)
            configured_count += 1
            
            self.logger.info(f"Configured MCP server: {server_info['name']}")
        
        if configured_count == 0:
            self.logger.error("No MCP servers were successfully configured")
            return False
        
        # Save updated configuration
        success = self._save_claude_config(claude_config, config_path)
        
        if success:
            self.logger.success(f"Successfully configured {configured_count} MCP servers")
            return self._post_install()
        else:
            return False
    
    def _post_install(self) -> bool:
        """Post-installation tasks"""
        try:
            # Update metadata
            metadata_mods = {
                "components": {
                    "mcp": {
                        "version": "4.0.6",
                        "installed": True,
                        "servers_configured": len(self.selected_servers),
                        "configured_servers": self.selected_servers
                    }
                }
            }
            self.settings_manager.update_metadata(metadata_mods)
            self.logger.info("Updated metadata with MCP component registration")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall MCP component by removing servers from .claude.json"""
        try:
            self.logger.info("Removing MCP server configurations...")
            
            # Load Claude configuration
            claude_config, config_path = self._load_claude_config()
            if claude_config is None:
                self.logger.warning("Could not load Claude config for cleanup")
                return True  # Not a failure if config doesn't exist
            
            if "mcpServers" not in claude_config:
                self.logger.info("No MCP servers configured")
                return True
            
            # Only remove servers that were installed by SuperClaude
            removed_count = 0
            installed_servers = self._get_installed_servers()
            
            for server_name in installed_servers:
                if server_name in claude_config["mcpServers"]:
                    # Check if this server was installed by SuperClaude by comparing with our configs
                    if self._is_superclaude_managed_server(claude_config["mcpServers"][server_name], server_name):
                        del claude_config["mcpServers"][server_name]
                        removed_count += 1
                        self.logger.debug(f"Removed SuperClaude-managed MCP server: {server_name}")
                    else:
                        self.logger.info(f"Preserved user-customized MCP server: {server_name}")
            
            # Save updated configuration
            if removed_count > 0:
                success = self._save_claude_config(claude_config, config_path)
                if not success:
                    self.logger.warning("Failed to save updated Claude configuration")
            
            # Update settings.json
            try:
                if self.settings_manager.is_component_installed("mcp"):
                    self.settings_manager.remove_component_registration("mcp")
                    self.logger.info("Removed MCP component from settings.json")
            except Exception as e:
                self.logger.warning(f"Could not update settings.json: {e}")
            
            if removed_count > 0:
                self.logger.success(f"MCP component uninstalled ({removed_count} SuperClaude-managed servers removed)")
            else:
                self.logger.info("MCP component uninstalled (no SuperClaude-managed servers to remove)")
            return True
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during MCP uninstallation: {e}")
            return False
    
    def _get_installed_servers(self) -> List[str]:
        """Get list of servers that were installed by SuperClaude"""
        try:
            metadata = self.settings_manager.get_metadata_setting("components")
            if metadata and "mcp" in metadata:
                return metadata["mcp"].get("configured_servers", [])
        except Exception:
            pass
        return []
    
    def _is_superclaude_managed_server(self, server_config: Dict, server_name: str) -> bool:
        """Check if a server configuration matches SuperClaude's templates
        
        This helps determine if a server was installed by SuperClaude or manually
        configured by the user, allowing us to preserve user customizations.
        """
        # Find the server key that maps to this server name
        server_key = None
        for key, info in self.mcp_servers.items():
            if info["name"] == server_name:
                server_key = key
                break
        
        if not server_key:
            return False  # Unknown server, don't remove
        
        # Load our template config for comparison
        template_config = self._load_mcp_server_config(server_key)
        if not template_config or server_name not in template_config:
            return False
        
        template_server = template_config[server_name]
        
        # Check if the current config has the same structure as our template
        # If user has customized it, the structure might be different
        required_keys = {"command", "args"}
        
        # Check if all required keys exist and match our template
        for key in required_keys:
            if key not in server_config or key not in template_server:
                return False
            # For command and basic structure, they should match our template
            if key == "command" and server_config[key] != template_server[key]:
                return False
        
        return True
    
    def get_dependencies(self) -> List[str]:
        """Get dependencies"""
        return ["core"]
    
    def get_size_estimate(self) -> int:
        """Get estimated size - minimal since we only modify config"""
        return 4096  # 4KB - just config modifications