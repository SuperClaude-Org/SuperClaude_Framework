"""
MCP Documentation component for SuperClaude MCP server documentation
"""

from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

from ..core.base import Component
from setup import __version__
from ..services.claude_md import CLAUDEMdService


class MCPDocsComponent(Component):
    """MCP documentation component - installs docs for selected MCP servers"""
    
    def __init__(self, install_dir: Optional[Path] = None):
        """Initialize MCP docs component"""
        # Initialize attributes before calling parent constructor
        # because parent calls _discover_component_files() which needs these
        self.selected_servers: List[str] = []
        
        # Map server names to documentation files
        self.server_docs_map = {
            "context7": "MCP_Context7.md",
            "sequential": "MCP_Sequential.md", 
            "magic": "MCP_Magic.md",
            "playwright": "MCP_Playwright.md",
            "serena": "MCP_Serena.md",
            "morphllm": "MCP_Morphllm.md"
        }
        
        super().__init__(install_dir, Path(""))
    
    def get_metadata(self) -> Dict[str, str]:
        """Get component metadata"""
        return {
            "name": "mcp_docs",
            "version": __version__,
            "description": "MCP server documentation and usage guides",
            "category": "documentation"
        }
    
    def set_selected_servers(self, selected_servers: List[str]) -> None:
        """Set which MCP servers were selected for documentation installation"""
        self.selected_servers = selected_servers
        self.logger.debug(f"MCP docs will be installed for: {selected_servers}")
    
    def get_files_to_install(self) -> List[Tuple[Path, Path]]:
        """
        Return list of files to install based on selected MCP servers
        
        Returns:
            List of tuples (source_path, target_path)
        """
        source_dir = self._get_source_dir()
        files = []

        if source_dir and self.selected_servers:
            for server_name in self.selected_servers:
                if server_name in self.server_docs_map:
                    doc_file = self.server_docs_map[server_name]
                    source = source_dir / doc_file
                    target = self.install_dir / doc_file
                    if source.exists():
                        files.append((source, target))
                        self.logger.debug(f"Will install documentation for {server_name}: {doc_file}")
                    else:
                        self.logger.warning(f"Documentation file not found for {server_name}: {doc_file}")

        return files
    
    def _discover_component_files(self) -> List[str]:
        """
        Override parent method to dynamically discover files based on selected servers
        """
        files = []
        # Check if selected_servers is not empty
        if self.selected_servers:
            for server_name in self.selected_servers:
                if server_name in self.server_docs_map:
                    files.append(self.server_docs_map[server_name])
        return files
    
    def _install(self, config: Dict[str, Any]) -> bool:
        """Install MCP documentation component"""
        self.logger.info("Installing MCP server documentation...")
        
        # Get selected servers from config
        selected_servers = config.get("selected_mcp_servers", [])
        self.set_selected_servers(selected_servers)
        self.component_files = self._discover_component_files()

        if not selected_servers:
            self.logger.info("No MCP servers selected - skipping documentation installation")
            return self._post_install()

        # Validate installation
        success, errors = self.validate_prerequisites()
        if not success:
            for error in errors:
                self.logger.error(error)
            return False

        # Get files to install
        files_to_install = self.get_files_to_install()

        if not files_to_install:
            self.logger.warning("No MCP documentation files found to install")
            return self._post_install()

        # Copy documentation files
        success_count = 0
        for source, target in files_to_install:
            self.logger.debug(f"Copying {source.name} to {target}")
            
            if self.file_manager.copy_file(source, target):
                success_count += 1
                self.logger.debug(f"Successfully copied {source.name}")
            else:
                self.logger.error(f"Failed to copy {source.name}")

        if success_count != len(files_to_install):
            self.logger.error(f"Only {success_count}/{len(files_to_install)} documentation files copied successfully")
            return False

        self.logger.success(f"MCP documentation installed successfully ({success_count} files for {len(selected_servers)} servers)")

        return self._post_install()

    def _post_install(self) -> bool:
        """Post-installation tasks"""
        try:
            # Update metadata
            metadata_mods = {
                "components": {
                    "mcp_docs": {
                        "version": __version__,
                        "installed": True,
                        "files_count": len(self.component_files),
                        "servers_documented": self.selected_servers
                    }
                }
            }
            self.settings_manager.update_metadata(metadata_mods)
            self.logger.info("Updated metadata with MCP docs component registration")
            
            # Update CLAUDE.md with MCP documentation imports
            try:
                manager = CLAUDEMdService(self.install_dir)
                manager.add_imports(self.component_files, category="MCP Documentation")
                self.logger.info("Updated CLAUDE.md with MCP documentation imports")
            except Exception as e:
                self.logger.warning(f"Failed to update CLAUDE.md with MCP documentation imports: {e}")
                # Don't fail the whole installation for this
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall MCP documentation component"""
        try:
            self.logger.info("Uninstalling MCP documentation component...")
            
            # Remove all MCP documentation files
            removed_count = 0
            source_dir = self._get_source_dir()
            
            if source_dir and source_dir.exists():
                # Remove all possible MCP doc files
                for doc_file in self.server_docs_map.values():
                    file_path = self.install_component_subdir / doc_file
                    if self.file_manager.remove_file(file_path):
                        removed_count += 1
                        self.logger.debug(f"Removed {doc_file}")
            
            # Remove mcp directory if empty
            try:
                if self.install_component_subdir.exists():
                    remaining_files = list(self.install_component_subdir.iterdir())
                    if not remaining_files:
                        self.install_component_subdir.rmdir()
                        self.logger.debug("Removed empty mcp directory")
            except Exception as e:
                self.logger.warning(f"Could not remove mcp directory: {e}")
            
            # Update settings.json
            try:
                if self.settings_manager.is_component_installed("mcp_docs"):
                    self.settings_manager.remove_component_registration("mcp_docs")
                    self.logger.info("Removed MCP docs component from settings.json")
            except Exception as e:
                self.logger.warning(f"Could not update settings.json: {e}")
            
            self.logger.success(f"MCP documentation uninstalled ({removed_count} files removed)")
            return True
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during MCP docs uninstallation: {e}")
            return False
    
    def get_dependencies(self) -> List[str]:
        """Get dependencies"""
        return ["core"]
    
    def _get_source_dir(self) -> Optional[Path]:
        """Get source directory for MCP documentation files"""
        # Assume we're in SuperClaude/setup/components/mcp_docs.py
        # and MCP docs are in SuperClaude/SuperClaude/MCP/
        project_root = Path(__file__).parent.parent.parent
        mcp_dir = project_root / "SuperClaude" / "MCP"
        
        # Return None if directory doesn't exist to prevent warning
        if not mcp_dir.exists():
            return None
        
        return mcp_dir
    
    def get_size_estimate(self) -> int:
        """Get estimated installation size"""
        source_dir = self._get_source_dir()
        total_size = 0
        
        if source_dir and source_dir.exists() and self.selected_servers:
            for server_name in self.selected_servers:
                if server_name in self.server_docs_map:
                    doc_file = self.server_docs_map[server_name]
                    file_path = source_dir / doc_file
                    if file_path.exists():
                        total_size += file_path.stat().st_size
        
        # Minimum size estimate
        total_size = max(total_size, 10240)  # At least 10KB
        
        return total_size