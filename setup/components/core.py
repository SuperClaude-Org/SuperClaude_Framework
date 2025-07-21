"""
Core component for SuperClaude framework files installation
"""

from typing import Dict, List, Tuple, Any
from pathlib import Path
import json
import shutil

from ..base.component import Component
from ..core.file_manager import FileManager
from ..core.settings_manager import SettingsManager
from ..utils.security import SecurityValidator
from ..utils.logger import get_logger


class CoreComponent(Component):
    """Core SuperClaude framework files component"""
    
    def __init__(self, install_dir: Path = None):
        """Initialize core component"""
        super().__init__(install_dir)
        self.logger = get_logger()
        self.file_manager = FileManager()
        self.settings_manager = SettingsManager(self.install_dir)
        
        # Dynamically discover framework files to install
        self.framework_files = self._discover_framework_files()
    
    def get_metadata(self) -> Dict[str, str]:
        """Get component metadata"""
        return {
            "name": "core",
            "version": "3.0.0",
            "description": "SuperClaude framework documentation and core files",
            "category": "core"
        }
    
    def validate_prerequisites(self) -> Tuple[bool, List[str]]:
        """Check prerequisites for core component"""
        errors = []
        
        # Check if we have read access to source files
        source_dir = self._get_source_dir()
        if not source_dir.exists():
            errors.append(f"Source directory not found: {source_dir}")
            return False, errors
        
        # Check if all required framework files exist
        missing_files = []
        for filename in self.framework_files:
            source_file = source_dir / filename
            if not source_file.exists():
                missing_files.append(filename)
        
        if missing_files:
            errors.append(f"Missing framework files: {missing_files}")
        
        # Check write permissions to install directory
        has_perms, missing = SecurityValidator.check_permissions(
            self.install_dir, {'write'}
        )
        if not has_perms:
            errors.append(f"No write permissions to {self.install_dir}: {missing}")
        
        # Validate installation target
        is_safe, validation_errors = SecurityValidator.validate_installation_target(self.install_dir)
        if not is_safe:
            errors.extend(validation_errors)
        
        return len(errors) == 0, errors
    
    def get_files_to_install(self) -> List[Tuple[Path, Path]]:
        """Get list of files to install"""
        source_dir = self._get_source_dir()
        files = []
        
        for filename in self.framework_files:
            source = source_dir / filename
            target = self.install_dir / filename
            files.append((source, target))
        
        return files
    
    def get_metadata_modifications(self) -> Dict[str, Any]:
        """Get metadata modifications for SuperClaude"""
        return {
            "framework": {
                "version": "3.0.0",
                "name": "SuperClaude",
                "description": "AI-enhanced development framework for Claude Code",
                "installation_type": "global",
                "components": ["core"]
            },
            "superclaude": {
                "enabled": True,
                "version": "3.0.0",
                "profile": "default",
                "auto_update": False
            }
        }
    
    def get_settings_modifications(self) -> Dict[str, Any]:
        """Get settings.json modifications (now only Claude Code compatible settings)"""
        # Return empty dict as we don't modify Claude Code settings
        return {}
    
    def install(self, config: Dict[str, Any]) -> bool:
        """Install core component"""
        try:
            self.logger.info("Installing SuperClaude core framework files...")
            
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
            is_safe, security_errors = SecurityValidator.validate_component_files(
                files_to_install, source_dir, self.install_dir
            )
            if not is_safe:
                for error in security_errors:
                    self.logger.error(f"Security validation failed: {error}")
                return False
            
            # Ensure install directory exists
            if not self.file_manager.ensure_directory(self.install_dir):
                self.logger.error(f"Could not create install directory: {self.install_dir}")
                return False
            
            # Protect existing user configuration
            user_config_preserved = self._protect_user_configuration()
            
            # Copy framework files
            success_count = 0
            for source, target in files_to_install:
                self.logger.debug(f"Copying {source.name} to {target}")
                
                if self.file_manager.copy_file(source, target):
                    success_count += 1
                    self.logger.debug(f"Successfully copied {source.name}")
                else:
                    self.logger.error(f"Failed to copy {source.name}")
            
            if success_count != len(files_to_install):
                self.logger.error(f"Only {success_count}/{len(files_to_install)} files copied successfully")
                return False
            
            # Update CLAUDE.md to conditionally include USER.md
            self._update_claude_md_user_reference(user_config_preserved)
            
            # Create or update metadata
            try:
                metadata_mods = self.get_metadata_modifications()
                # Update metadata directly
                existing_metadata = self.settings_manager.load_metadata()
                merged_metadata = self.settings_manager._deep_merge(existing_metadata, metadata_mods)
                self.settings_manager.save_metadata(merged_metadata)
                self.logger.info("Updated metadata with framework configuration")
                
                # Add component registration to metadata
                self.settings_manager.add_component_registration("core", {
                    "version": "3.0.0",
                    "category": "core",
                    "files_count": len(self.framework_files)
                })
                self.logger.info("Updated metadata with core component registration")
                
                # Migrate any existing SuperClaude data from settings.json
                if self.settings_manager.migrate_superclaude_data():
                    self.logger.info("Migrated existing SuperClaude data from settings.json")
            except Exception as e:
                self.logger.error(f"Failed to update metadata: {e}")
                return False
            
            # Create additional directories for other components
            additional_dirs = ["commands", "hooks", "backups", "logs"]
            for dirname in additional_dirs:
                dir_path = self.install_dir / dirname
                if not self.file_manager.ensure_directory(dir_path):
                    self.logger.warning(f"Could not create directory: {dir_path}")
            
            self.logger.success(f"Core component installed successfully ({success_count} files)")
            return True
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during core installation: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall core component"""
        try:
            self.logger.info("Uninstalling SuperClaude core component...")
            
            # Remove framework files
            removed_count = 0
            for filename in self.framework_files:
                file_path = self.install_dir / filename
                if self.file_manager.remove_file(file_path):
                    removed_count += 1
                    self.logger.debug(f"Removed {filename}")
                else:
                    self.logger.warning(f"Could not remove {filename}")
            
            # Update metadata to remove core component
            try:
                if self.settings_manager.is_component_installed("core"):
                    self.settings_manager.remove_component_registration("core")
                    self.logger.info("Removed core component from metadata")
            except Exception as e:
                self.logger.warning(f"Could not update metadata: {e}")
            
            self.logger.success(f"Core component uninstalled ({removed_count} files removed)")
            return True
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during core uninstallation: {e}")
            return False
    
    def get_dependencies(self) -> List[str]:
        """Get component dependencies (core has none)"""
        return []
    
    def update(self, config: Dict[str, Any]) -> bool:
        """Update core component"""
        try:
            self.logger.info("Updating SuperClaude core component...")
            
            # Check current version
            current_version = self.settings_manager.get_component_version("core")
            target_version = self.get_metadata()["version"]
            
            if current_version == target_version:
                self.logger.info(f"Core component already at version {target_version}")
                return True
            
            self.logger.info(f"Updating core component from {current_version} to {target_version}")
            
            # Create backup of existing files
            backup_files = []
            for filename in self.framework_files:
                file_path = self.install_dir / filename
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
                
                self.logger.success(f"Core component updated to version {target_version}")
            else:
                # Restore from backup on failure
                self.logger.warning("Update failed, restoring from backup...")
                for backup_path in backup_files:
                    try:
                        original_path = backup_path.with_suffix('')
                        shutil.move(str(backup_path), str(original_path))
                        self.logger.debug(f"Restored {original_path.name}")
                    except Exception as e:
                        self.logger.error(f"Could not restore {backup_path}: {e}")
            
            return success
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during core update: {e}")
            return False
    
    def validate_installation(self) -> Tuple[bool, List[str]]:
        """Validate core component installation"""
        errors = []
        
        # Check if all framework files exist
        for filename in self.framework_files:
            file_path = self.install_dir / filename
            if not file_path.exists():
                errors.append(f"Missing framework file: {filename}")
            elif not file_path.is_file():
                errors.append(f"Framework file is not a regular file: {filename}")
        
        # Check metadata registration
        if not self.settings_manager.is_component_installed("core"):
            errors.append("Core component not registered in metadata")
        else:
            # Check version matches
            installed_version = self.settings_manager.get_component_version("core")
            expected_version = self.get_metadata()["version"]
            if installed_version != expected_version:
                errors.append(f"Version mismatch: installed {installed_version}, expected {expected_version}")
        
        # Check metadata structure
        try:
            framework_config = self.settings_manager.get_metadata_setting("framework")
            if not framework_config:
                errors.append("Missing framework configuration in metadata")
            else:
                required_keys = ["version", "name", "description"]
                for key in required_keys:
                    if key not in framework_config:
                        errors.append(f"Missing framework.{key} in metadata")
        except Exception as e:
            errors.append(f"Could not validate metadata: {e}")
        
        return len(errors) == 0, errors
    
    def _discover_framework_files(self) -> List[str]:
        """
        Dynamically discover framework .md files in the Core directory
        
        Returns:
            List of framework filenames (e.g., ['CLAUDE.md', 'COMMANDS.md', ...])
        """
        return self._discover_files_in_directory(
            self._get_source_dir(),
            extension='.md',
            exclude_patterns=['README.md', 'CHANGELOG.md', 'LICENSE.md']
        )
    
    def _discover_files_in_directory(self, directory: Path, extension: str = '.md', 
                                   exclude_patterns: List[str] = None) -> List[str]:
        """
        Shared utility for discovering files in a directory
        
        Args:
            directory: Directory to scan
            extension: File extension to look for (default: '.md')
            exclude_patterns: List of filename patterns to exclude
            
        Returns:
            List of filenames found in the directory
        """
        if exclude_patterns is None:
            exclude_patterns = []
        
        try:
            if not directory.exists():
                self.logger.warning(f"Source directory not found: {directory}")
                return []
            
            if not directory.is_dir():
                self.logger.warning(f"Source path is not a directory: {directory}")
                return []
            
            # Discover files with the specified extension
            files = []
            for file_path in directory.iterdir():
                if (file_path.is_file() and 
                    file_path.suffix.lower() == extension.lower() and
                    file_path.name not in exclude_patterns):
                    files.append(file_path.name)
            
            # Sort for consistent ordering
            files.sort()
            
            self.logger.debug(f"Discovered {len(files)} {extension} files in {directory}")
            if files:
                self.logger.debug(f"Files found: {files}")
            
            return files
            
        except PermissionError:
            self.logger.error(f"Permission denied accessing directory: {directory}")
            return []
        except Exception as e:
            self.logger.error(f"Error discovering files in {directory}: {e}")
            return []

    def _get_source_dir(self) -> Path:
        """Get source directory for framework files"""
        # Assume we're in SuperClaude/setup/components/core.py
        # and framework files are in SuperClaude/SuperClaude/Core/
        project_root = Path(__file__).parent.parent.parent
        return project_root / "SuperClaude" / "Core"
    
    def get_size_estimate(self) -> int:
        """Get estimated installation size"""
        total_size = 0
        source_dir = self._get_source_dir()
        
        for filename in self.framework_files:
            file_path = source_dir / filename
            if file_path.exists():
                total_size += file_path.stat().st_size
        
        # Add overhead for settings.json and directories
        total_size += 10240  # ~10KB overhead
        
        return total_size
    
    def get_installation_summary(self) -> Dict[str, Any]:
        """Get installation summary"""
        return {
            "component": self.get_metadata()["name"],
            "version": self.get_metadata()["version"],
            "files_installed": len(self.framework_files),
            "framework_files": self.framework_files,
            "estimated_size": self.get_size_estimate(),
            "install_directory": str(self.install_dir),
            "dependencies": self.get_dependencies()
        }
    
    def _protect_user_configuration(self) -> bool:
        """
        Protect existing user CLAUDE.md configuration file
        
        If an existing CLAUDE.md file is detected, rename it to USER.md to preserve
        user customizations before installing SuperClaude framework files.
        
        Returns:
            bool: True if user configuration was protected, False if no protection needed
        """
        existing_claude_md = self.install_dir / "CLAUDE.md"
        user_config_file = self.install_dir / "USER.md"
        
        # Check if existing CLAUDE.md file exists
        if not existing_claude_md.exists():
            self.logger.debug("No existing CLAUDE.md file found, no user configuration to protect")
            return False
        
        # Check if file is already a SuperClaude framework file (avoid duplicate protection)
        if self._is_superclaude_framework_file(existing_claude_md):
            self.logger.debug("Existing CLAUDE.md appears to be SuperClaude framework file, no protection needed")
            return False
        
        try:
            # If USER.md already exists, create backup
            if user_config_file.exists():
                backup_path = self.file_manager.backup_file(user_config_file)
                if backup_path:
                    self.logger.info(f"Existing USER.md backed up to: {backup_path.name}")
            
            # Rename existing CLAUDE.md to USER.md
            existing_claude_md.rename(user_config_file)
            
            # Log successful protection
            self.logger.success("🛡️  User configuration protected!")
            self.logger.info(f"Your existing CLAUDE.md has been preserved as USER.md")
            self.logger.info(f"SuperClaude will automatically include your configuration")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to protect user configuration: {e}")
            self.logger.warning("Your existing CLAUDE.md may be overwritten")
            return False
    
    def _is_superclaude_framework_file(self, file_path: Path) -> bool:
        """
        Check if file is a SuperClaude framework file
        
        Args:
            file_path: Path to file to check
            
        Returns:
            bool: True if it's a framework file, False if it's a user file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for SuperClaude framework file markers
            superclaude_markers = [
                "# SuperClaude Entry Point",
                "@COMMANDS.md",
                "@FLAGS.md", 
                "@PRINCIPLES.md",
                "@ORCHESTRATOR.md"
            ]
            
            # If file contains multiple framework markers, consider it a framework file
            marker_count = sum(1 for marker in superclaude_markers if marker in content)
            return marker_count >= 2
            
        except Exception:
            # If reading fails, assume it's a user file for safety
            return False
    
    def _update_claude_md_user_reference(self, user_config_preserved: bool) -> None:
        """
        Update CLAUDE.md to conditionally include USER.md reference
        
        If user configuration was preserved, ensure the @USER.md reference is active.
        If no user configuration exists, comment out the @USER.md reference.
        
        Args:
            user_config_preserved: Whether user configuration was preserved
        """
        claude_md_path = self.install_dir / "CLAUDE.md"
        
        if not claude_md_path.exists():
            self.logger.warning("CLAUDE.md not found, cannot update user reference")
            return
        
        try:
            # Read current content
            with open(claude_md_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Update USER.md reference based on whether user config was preserved
            updated_lines = []
            for line in lines:
                if line.strip() == "@USER.md":
                    if user_config_preserved:
                        # Keep active reference
                        updated_lines.append(line)
                        self.logger.debug("Activated @USER.md reference in CLAUDE.md")
                    else:
                        # Comment out reference
                        updated_lines.append("# @USER.md  # No user configuration found\n")
                        self.logger.debug("Commented out @USER.md reference in CLAUDE.md")
                else:
                    updated_lines.append(line)
            
            # Write updated content
            with open(claude_md_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            if user_config_preserved:
                self.logger.info("CLAUDE.md updated to include your preserved configuration")
            
        except Exception as e:
            self.logger.error(f"Failed to update CLAUDE.md user reference: {e}")
            # This is not critical, so we don't fail the installation