"""
Commands component for SuperClaude slash command definitions
"""

from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

from ..core.base import Component
from setup import __version__


class CommandsComponent(Component):
    """SuperClaude slash commands component"""

    def __init__(self, install_dir: Optional[Path] = None):
        """Initialize commands component"""
        if install_dir is None:
            install_dir = Path.home() / ".claude"

        # Commands are installed directly to ~/.claude/commands/sc/
        # not under superclaude/ subdirectory (Claude Code official location)
        if "superclaude" in str(install_dir):
            # ~/.claude/superclaude -> ~/.claude
            install_dir = install_dir.parent

        super().__init__(install_dir, Path("commands/sc"))

    def get_metadata(self) -> Dict[str, str]:
        """Get component metadata"""
        return {
            "name": "commands",
            "version": __version__,
            "description": "SuperClaude slash command definitions",
            "category": "commands",
        }

    def is_reinstallable(self) -> bool:
        """
        Commands should always be synced to latest version.
        SuperClaude command files always overwrite existing files.
        """
        return True

    def get_metadata_modifications(self) -> Dict[str, Any]:
        """Get metadata modifications for commands component"""
        return {
            "components": {
                "commands": {
                    "version": __version__,
                    "installed": True,
                    "files_count": len(self.component_files),
                }
            },
            "commands": {"enabled": True, "version": __version__, "auto_update": False},
        }

    def _install(self, config: Dict[str, Any]) -> bool:
        """Install commands component"""
        self.logger.info("Installing SuperClaude command definitions...")

        # Check for and migrate existing commands from old location
        self._migrate_existing_commands()

        return super()._install(config)

    def _post_install(self) -> bool:
        # Update metadata
        try:
            metadata_mods = self.get_metadata_modifications()
            self.settings_manager.update_metadata(metadata_mods)
            self.logger.info("Updated metadata with commands configuration")

            # Add component registration to metadata (with file list for sync)
            self.settings_manager.add_component_registration(
                "commands",
                {
                    "version": __version__,
                    "category": "commands",
                    "files_count": len(self.component_files),
                    "files": list(self.component_files),  # Track for sync/deletion
                },
            )
            self.logger.info("Updated metadata with commands component registration")
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {e}")
            return False

        # Clean up old commands directory in superclaude/ (from previous versions)
        try:
            old_superclaude_commands = Path.home() / ".claude" / "superclaude" / "commands"
            if old_superclaude_commands.exists():
                import shutil
                shutil.rmtree(old_superclaude_commands)
                self.logger.info("Removed old commands directory from superclaude/")
        except Exception as e:
            self.logger.debug(f"Could not remove old commands directory: {e}")

        return True

    def uninstall(self) -> bool:
        """Uninstall commands component"""
        try:
            self.logger.info("Uninstalling SuperClaude commands component...")

            # Remove command files from sc subdirectory
            commands_dir = self.install_dir / "commands" / "sc"
            removed_count = 0

            for filename in self.component_files:
                file_path = commands_dir / filename
                if self.file_manager.remove_file(file_path):
                    removed_count += 1
                    self.logger.debug(f"Removed {filename}")
                else:
                    self.logger.warning(f"Could not remove {filename}")

            # Also check and remove any old commands in root commands directory
            old_commands_dir = self.install_dir / "commands"
            old_removed_count = 0

            for filename in self.component_files:
                old_file_path = old_commands_dir / filename
                if old_file_path.exists() and old_file_path.is_file():
                    if self.file_manager.remove_file(old_file_path):
                        old_removed_count += 1
                        self.logger.debug(f"Removed old {filename}")
                    else:
                        self.logger.warning(f"Could not remove old {filename}")

            if old_removed_count > 0:
                self.logger.info(
                    f"Also removed {old_removed_count} commands from old location"
                )

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
                                self.logger.debug(
                                    "Removed empty parent commands directory"
                                )
            except Exception as e:
                self.logger.warning(f"Could not remove commands directory: {e}")

            # Update metadata to remove commands component
            try:
                if self.settings_manager.is_component_installed("commands"):
                    self.settings_manager.remove_component_registration("commands")
                    # Also remove commands configuration from metadata
                    metadata = self.settings_manager.load_metadata()
                    if "commands" in metadata:
                        del metadata["commands"]
                        self.settings_manager.save_metadata(metadata)
                    self.logger.info("Removed commands component from metadata")
            except Exception as e:
                self.logger.warning(f"Could not update metadata: {e}")

            self.logger.success(
                f"Commands component uninstalled ({removed_count} files removed)"
            )
            return True

        except Exception as e:
            self.logger.exception(
                f"Unexpected error during commands uninstallation: {e}"
            )
            return False

    def get_dependencies(self) -> List[str]:
        """Get dependencies"""
        return ["framework_docs"]

    def update(self, config: Dict[str, Any]) -> bool:
        """
        Sync commands component (overwrite + delete obsolete files).
        No backup needed - SuperClaude source files are always authoritative.
        """
        try:
            self.logger.info("Syncing SuperClaude commands component...")

            # Get previously installed files from metadata
            metadata = self.settings_manager.load_metadata()
            previous_files = set(
                metadata.get("components", {}).get("commands", {}).get("files", [])
            )

            # Get current files from source
            current_files = set(self.component_files)

            # Files to delete (were installed before, but no longer in source)
            files_to_delete = previous_files - current_files

            # Delete obsolete files
            deleted_count = 0
            commands_dir = self.install_dir / "commands" / "sc"
            for filename in files_to_delete:
                file_path = commands_dir / filename
                if file_path.exists():
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted obsolete command: {filename}")
                    except Exception as e:
                        self.logger.warning(f"Could not delete {filename}: {e}")

            # Install/overwrite current files (no backup)
            success = self.install(config)

            if success:
                # Update metadata with current file list
                self.settings_manager.add_component_registration(
                    "commands",
                    {
                        "version": __version__,
                        "category": "commands",
                        "files_count": len(current_files),
                        "files": list(current_files),  # Track installed files
                    },
                )

                self.logger.success(
                    f"Commands synced: {len(current_files)} files, {deleted_count} obsolete files removed"
                )
            else:
                self.logger.error("Commands sync failed")

            return success

        except Exception as e:
            self.logger.exception(f"Unexpected error during commands sync: {e}")
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
        for filename in self.component_files:
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
                errors.append(
                    f"Version mismatch: installed {installed_version}, expected {expected_version}"
                )

        return len(errors) == 0, errors

    def _get_source_dir(self) -> Path:
        """Get source directory for command files"""
        # Assume we're in superclaude/setup/components/commands.py
        # and command files are in superclaude/superclaude/Commands/
        project_root = Path(__file__).parent.parent.parent
        return project_root / "superclaude" / "commands"

    def get_size_estimate(self) -> int:
        """Get estimated installation size"""
        total_size = 0
        source_dir = self._get_source_dir()

        for filename in self.component_files:
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
            "files_installed": len(self.component_files),
            "command_files": self.component_files,
            "estimated_size": self.get_size_estimate(),
            "install_directory": str(self.install_dir / "commands" / "sc"),
            "dependencies": self.get_dependencies(),
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
                for filename in self.component_files:
                    old_file_path = old_commands_dir / filename
                    if old_file_path.exists() and old_file_path.is_file():
                        commands_to_migrate.append(filename)

            if commands_to_migrate:
                self.logger.info(
                    f"Found {len(commands_to_migrate)} existing commands to migrate to sc/ subdirectory"
                )

                # Ensure new directory exists
                if not self.file_manager.ensure_directory(new_commands_dir):
                    self.logger.error(
                        f"Could not create sc commands directory: {new_commands_dir}"
                    )
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
                                self.logger.debug(
                                    f"Migrated {filename} to sc/ subdirectory"
                                )
                            else:
                                self.logger.warning(f"Could not remove old {filename}")
                        else:
                            self.logger.warning(
                                f"Could not copy {filename} to sc/ subdirectory"
                            )
                    except Exception as e:
                        self.logger.warning(f"Error migrating {filename}: {e}")

                if migrated_count > 0:
                    self.logger.success(
                        f"Successfully migrated {migrated_count} commands to /sc: namespace"
                    )
                    self.logger.info(
                        "Commands are now available as /sc:analyze, /sc:build, etc."
                    )

                    # Try to remove old commands directory if empty
                    try:
                        if old_commands_dir.exists():
                            remaining_files = [
                                f for f in old_commands_dir.iterdir() if f.is_file()
                            ]
                            if not remaining_files:
                                # Only remove if no user files remain
                                old_commands_dir.rmdir()
                                self.logger.debug(
                                    "Removed empty old commands directory"
                                )
                    except Exception as e:
                        self.logger.debug(
                            f"Could not remove old commands directory: {e}"
                        )

        except Exception as e:
            self.logger.warning(f"Error during command migration: {e}")
