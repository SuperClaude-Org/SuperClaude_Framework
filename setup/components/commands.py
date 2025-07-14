"""
Commands component for SuperClaude slash command definitions
"""

from typing import Dict, List, Tuple, Any
from pathlib import Path

from ..base.component import Component
from ..core.file_manager import FileManager
from ..core.settings_manager import SettingsManager
from ..utils.security import SecurityValidator
from ..utils.logger import get_logger


class CommandsComponent(Component):
    """SuperClaude slash commands component"""
    
    def __init__(self, install_dir: Path = None):
        """Initialize commands component"""
        super().__init__(install_dir)
        self.logger = get_logger()
        self.file_manager = FileManager()
        self.settings_manager = SettingsManager(self.install_dir)
        
        # Define command files to install
        self.command_files = [
            "analyze.md",
            "build.md", 
            "implement.md",
            "cleanup.md",
            "design.md",
            "document.md",
            "estimate.md",
            "explain.md",
            "git.md",
            "improve.md",
            "index.md",
            "load.md",
            "spawn.md",
            "task.md",
            "test.md",
            "troubleshoot.md"
        ]
    
    def get_metadata(self) -> Dict[str, str]:
        """Get component metadata"""
        return {
            "name": "commands",
            "version": "3.0.0",
            "description": "SuperClaude slash command definitions",
            "category": "commands"
        }
    
    def validate_prerequisites(self) -> Tuple[bool, List[str]]:
        """Check prerequisites"""
        errors = []
        
        # Check if we have read access to source files
        source_dir = self._get_source_dir()
        if not source_dir.exists():
            errors.append(f"Source directory not found: {source_dir}")
            return False, errors
        
        # Check if all required command files exist
        missing_files = []
        for filename in self.command_files:
            source_file = source_dir / filename
            if not source_file.exists():
                missing_files.append(filename)
        
        if missing_files:
            errors.append(f"Missing command files: {missing_files}")
        
        # Check write permissions to install directory
        commands_dir = self.install_dir / "commands" / "sc"
        has_perms, missing = SecurityValidator.check_permissions(
            self.install_dir, {'write'}
        )
        if not has_perms:
            errors.append(f"No write permissions to {self.install_dir}: {missing}")
        
        # Validate installation target
        is_safe, validation_errors = SecurityValidator.validate_installation_target(commands_dir)
        if not is_safe:
            errors.extend(validation_errors)
        
        return len(errors) == 0, errors
    
    def get_files_to_install(self) -> List[Tuple[Path, Path]]:
        """Get files to install"""
        source_dir = self._get_source_dir()
        files = []
        
        for filename in self.command_files:
            source = source_dir / filename
            target = self.install_dir / "commands" / "sc" / filename
            files.append((source, target))
        
        return files
    
    def get_metadata_modifications(self) -> Dict[str, Any]:
        """Get metadata modifications for commands component"""
        return {
            "components": {
                "commands": {
                    "version": "3.0.0",
                    "installed": True,
                    "files_count": len(self.command_files)
                }
            }
        }
    
    def get_settings_modifications(self) -> Dict[str, Any]:
        """Get settings.json modifications (now only Claude Code compatible settings)"""
        # Return empty dict as we don't modify Claude Code settings
        return {}
    
    def install(self, config: Dict[str, Any]) -> bool:
        """Install commands component"""
        try:
            self.logger.info("Installing SuperClaude command definitions...")
            
            # Check for and migrate existing commands from old location
            self._migrate_existing_commands()
            
            # Validate installation
            success, errors = self.validate_prerequisites()
            if not success:
                for error in errors:
                    self.logger.error(error)
                return False
            
            # Get files to install
            files_to_install = self.get_files_to_install()
            
            # Validate all files for security
            source_dir = self._get_source_dir()
            commands_dir = self.install_dir / "commands" / "sc"
            is_safe, security_errors = SecurityValidator.validate_component_files(
                files_to_install, source_dir, commands_dir
            )
            if not is_safe:
                for error in security_errors:
                    self.logger.error(f"Security validation failed: {error}")
                return False
            
            # Ensure commands directory exists
            if not self.file_manager.ensure_directory(commands_dir):
                self.logger.error(f"Could not create commands directory: {commands_dir}")
                return False
            
            # Copy command files
            success_count = 0
            for source, target in files_to_install:
                self.logger.debug(f"Copying {source.name} to {target}")
                
                if self.file_manager.copy_file(source, target):
                    success_count += 1
                    self.logger.debug(f"Successfully copied {source.name}")
                else:
                    self.logger.error(f"Failed to copy {source.name}")
            
            if success_count != len(files_to_install):
                self.logger.error(f"Only {success_count}/{len(files_to_install)} command files copied successfully")
                return False
            
            # Update metadata
            try:
                # Add component registration to metadata
                self.settings_manager.add_component_registration("commands", {
                    "version": "3.0.0",
                    "category": "commands",
                    "files_count": len(self.command_files)
                })
                self.logger.info("Updated metadata with commands component registration")
            except Exception as e:
                self.logger.error(f"Failed to update metadata: {e}")
                return False
            
            self.logger.success(f"Commands component installed successfully ({success_count} command files)")
            return True
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during commands installation: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall commands component"""
        try:
            self.logger.info("Uninstalling SuperClaude commands component...")
            
            # Remove command files from sc subdirectory
            commands_dir = self.install_dir / "commands" / "sc"
            removed_count = 0
            
            for filename in self.command_files:
                file_path = commands_dir / filename
                if self.file_manager.remove_file(file_path):
                    removed_count += 1
                    self.logger.debug(f"Removed {filename}")
                else:
                    self.logger.warning(f"Could not remove {filename}")
            
            # Also check and remove any old commands in root commands directory
            old_commands_dir = self.install_dir / "commands"
            old_removed_count = 0
            
            for filename in self.command_files:
                old_file_path = old_commands_dir / filename
                if old_file_path.exists() and old_file_path.is_file():
                    if self.file_manager.remove_file(old_file_path):
                        old_removed_count += 1
                        self.logger.debug(f"Removed old {filename}")
                    else:
                        self.logger.warning(f"Could not remove old {filename}")
            
            if old_removed_count > 0:
                self.logger.info(f"Also removed {old_removed_count} commands from old location")
            
            removed_count += old_removed_count
            
            # Remove sc subdirectory if empty
            try:
                if commands_dir.exists():
                    remaining_files = list(commands_dir.iterdir())
                    if not remaining_files:
                        commands_dir.rmdir()
                        self.logger.debug("Removed empty sc commands directory")
                        
                        # Also remove parent commands directory if empty
                        parent_commands_dir = self.install_dir / "commands"
                        if parent_commands_dir.exists():
                            remaining_files = list(parent_commands_dir.iterdir())
                            if not remaining_files:
                                parent_commands_dir.rmdir()
                                self.logger.debug("Removed empty parent commands directory")
            except Exception as e:
                self.logger.warning(f"Could not remove commands directory: {e}")
            
            # Update metadata to remove commands component
            try:
                if self.settings_manager.is_component_installed("commands"):
                    self.settings_manager.remove_component_registration("commands")
                    self.logger.info("Removed commands component from metadata")
            except Exception as e:
                self.logger.warning(f"Could not update metadata: {e}")
            
            self.logger.success(f"Commands component uninstalled ({removed_count} files removed)")
            return True
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during commands uninstallation: {e}")
            return False
    
    def get_dependencies(self) -> List[str]:
        """Get dependencies"""
        return ["core"]
    
    def update(self, config: Dict[str, Any]) -> bool:
        """Update commands component"""
        try:
            self.logger.info("Updating SuperClaude commands component...")
            
            # Check current version
            current_version = self.settings_manager.get_component_version("commands")
            target_version = self.get_metadata()["version"]
            
            if current_version == target_version:
                self.logger.info(f"Commands component already at version {target_version}")
                return True
            
            self.logger.info(f"Updating commands component from {current_version} to {target_version}")
            
            # Create backup of existing command files
            commands_dir = self.install_dir / "commands" / "sc"
            backup_files = []
            
            if commands_dir.exists():
                for filename in self.command_files:
                    file_path = commands_dir / filename
                    if file_path.exists():
                        backup_path = self.file_manager.backup_file(file_path)
                        if backup_path:
                            backup_files.append(backup_path)
                            self.logger.debug(f"Backed up {filename}")
            
            # Perform installation (overwrites existing files)
            success = self.install(config)
            
            if success:
                # Remove backup files on successful update
                for backup_path in backup_files:
                    try:
                        backup_path.unlink()
                    except Exception:
                        pass  # Ignore cleanup errors
                
                self.logger.success(f"Commands component updated to version {target_version}")
            else:
                # Restore from backup on failure
                self.logger.warning("Update failed, restoring from backup...")
                for backup_path in backup_files:
                    try:
                        original_path = backup_path.with_suffix('')
                        backup_path.rename(original_path)
                        self.logger.debug(f"Restored {original_path.name}")
                    except Exception as e:
                        self.logger.error(f"Could not restore {backup_path}: {e}")
            
            return success
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during commands update: {e}")
            return False
    
    def validate_installation(self) -> Tuple[bool, List[str]]:
        """Validate commands component installation"""
        errors = []
        
        # Check if sc commands directory exists
        commands_dir = self.install_dir / "commands" / "sc"
        if not commands_dir.exists():
            errors.append("SC commands directory not found")
            return False, errors
        
        # Check if all command files exist
        for filename in self.command_files:
            file_path = commands_dir / filename
            if not file_path.exists():
                errors.append(f"Missing command file: {filename}")
            elif not file_path.is_file():
                errors.append(f"Command file is not a regular file: {filename}")
        
        # Check metadata registration
        if not self.settings_manager.is_component_installed("commands"):
            errors.append("Commands component not registered in metadata")
        else:
            # Check version matches
            installed_version = self.settings_manager.get_component_version("commands")
            expected_version = self.get_metadata()["version"]
            if installed_version != expected_version:
                errors.append(f"Version mismatch: installed {installed_version}, expected {expected_version}")
        
        return len(errors) == 0, errors
    
    def _get_source_dir(self) -> Path:
        """Get source directory for command files"""
        # Assume we're in SuperClaude/setup/components/commands.py
        # and command files are in SuperClaude/SuperClaude/Commands/
        project_root = Path(__file__).parent.parent.parent
        return project_root / "SuperClaude" / "Commands"
    
    def get_size_estimate(self) -> int:
        """Get estimated installation size"""
        total_size = 0
        source_dir = self._get_source_dir()
        
        for filename in self.command_files:
            file_path = source_dir / filename
            if file_path.exists():
                total_size += file_path.stat().st_size
        
        # Add overhead for directory and settings
        total_size += 5120  # ~5KB overhead
        
        return total_size
    
    def get_installation_summary(self) -> Dict[str, Any]:
        """Get installation summary"""
        return {
            "component": self.get_metadata()["name"],
            "version": self.get_metadata()["version"],
            "files_installed": len(self.command_files),
            "command_files": self.command_files,
            "estimated_size": self.get_size_estimate(),
            "install_directory": str(self.install_dir / "commands" / "sc"),
            "dependencies": self.get_dependencies()
        }
    
    def _migrate_existing_commands(self) -> None:
        """Migrate existing commands from old location to new sc subdirectory"""
        try:
            old_commands_dir = self.install_dir / "commands"
            new_commands_dir = self.install_dir / "commands" / "sc"
            
            # Check if old commands exist in root commands directory
            migrated_count = 0
            commands_to_migrate = []
            
            if old_commands_dir.exists():
                for filename in self.command_files:
                    old_file_path = old_commands_dir / filename
                    if old_file_path.exists() and old_file_path.is_file():
                        commands_to_migrate.append(filename)
            
            if commands_to_migrate:
                self.logger.info(f"Found {len(commands_to_migrate)} existing commands to migrate to sc/ subdirectory")
                
                # Ensure new directory exists
                if not self.file_manager.ensure_directory(new_commands_dir):
                    self.logger.error(f"Could not create sc commands directory: {new_commands_dir}")
                    return
                
                # Move files from old to new location
                for filename in commands_to_migrate:
                    old_file_path = old_commands_dir / filename
                    new_file_path = new_commands_dir / filename
                    
                    try:
                        # Copy file to new location
                        if self.file_manager.copy_file(old_file_path, new_file_path):
                            # Remove old file
                            if self.file_manager.remove_file(old_file_path):
                                migrated_count += 1
                                self.logger.debug(f"Migrated {filename} to sc/ subdirectory")
                            else:
                                self.logger.warning(f"Could not remove old {filename}")
                        else:
                            self.logger.warning(f"Could not copy {filename} to sc/ subdirectory")
                    except Exception as e:
                        self.logger.warning(f"Error migrating {filename}: {e}")
                
                if migrated_count > 0:
                    self.logger.success(f"Successfully migrated {migrated_count} commands to /sc: namespace")
                    self.logger.info("Commands are now available as /sc:analyze, /sc:build, etc.")
                    
                    # Try to remove old commands directory if empty
                    try:
                        if old_commands_dir.exists():
                            remaining_files = [f for f in old_commands_dir.iterdir() if f.is_file()]
                            if not remaining_files:
                                # Only remove if no user files remain
                                old_commands_dir.rmdir()
                                self.logger.debug("Removed empty old commands directory")
                    except Exception as e:
                        self.logger.debug(f"Could not remove old commands directory: {e}")
                        
        except Exception as e:
            self.logger.warning(f"Error during command migration: {e}")
