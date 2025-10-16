"""
Framework documentation component for SuperClaude
Manages core framework documentation files (CLAUDE.md, FLAGS.md, PRINCIPLES.md, etc.)
"""

from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import shutil

from ..core.base import Component
from ..services.claude_md import CLAUDEMdService
from setup import __version__


class FrameworkDocsComponent(Component):
    """SuperClaude framework documentation files component"""

    def __init__(self, install_dir: Optional[Path] = None):
        """Initialize framework docs component"""
        super().__init__(install_dir)

    def get_metadata(self) -> Dict[str, str]:
        """Get component metadata"""
        return {
            "name": "framework_docs",
            "version": __version__,
            "description": "SuperClaude framework documentation (CLAUDE.md, FLAGS.md, PRINCIPLES.md, RULES.md, etc.)",
            "category": "documentation",
        }

    def is_reinstallable(self) -> bool:
        """
        Framework docs should always be updated to latest version.
        SuperClaude-related documentation should always overwrite existing files.
        """
        return True

    def get_metadata_modifications(self) -> Dict[str, Any]:
        """Get metadata modifications for SuperClaude"""
        return {
            "framework": {
                "version": __version__,
                "name": "superclaude",
                "description": "AI-enhanced development framework for Claude Code",
                "installation_type": "global",
                "components": ["framework_docs"],
            },
            "superclaude": {
                "enabled": True,
                "version": __version__,
                "profile": "default",
                "auto_update": False,
            },
        }

    def _install(self, config: Dict[str, Any]) -> bool:
        """Install framework docs component"""
        self.logger.info("Installing SuperClaude framework documentation...")

        return super()._install(config)

    def _post_install(self) -> bool:
        # Create or update metadata
        try:
            metadata_mods = self.get_metadata_modifications()
            self.settings_manager.update_metadata(metadata_mods)
            self.logger.info("Updated metadata with framework configuration")

            # Add component registration to metadata (with file list for sync)
            self.settings_manager.add_component_registration(
                "framework_docs",
                {
                    "version": __version__,
                    "category": "documentation",
                    "files_count": len(self.component_files),
                    "files": list(self.component_files),  # Track for sync/deletion
                },
            )

            self.logger.info("Updated metadata with framework docs component registration")

            # Migrate any existing SuperClaude data from settings.json
            if self.settings_manager.migrate_superclaude_data():
                self.logger.info(
                    "Migrated existing SuperClaude data from settings.json"
                )
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {e}")
            return False

        # Create additional directories for other components
        additional_dirs = ["commands", "backups", "logs"]
        for dirname in additional_dirs:
            dir_path = self.install_dir / dirname
            if not self.file_manager.ensure_directory(dir_path):
                self.logger.warning(f"Could not create directory: {dir_path}")

        # Update CLAUDE.md with framework documentation imports
        try:
            manager = CLAUDEMdService(self.install_dir)
            manager.add_imports(self.component_files, category="Framework Documentation")
            self.logger.info("Updated CLAUDE.md with framework documentation imports")
        except Exception as e:
            self.logger.warning(
                f"Failed to update CLAUDE.md with framework documentation imports: {e}"
            )
            # Don't fail the whole installation for this

        return True

    def uninstall(self) -> bool:
        """Uninstall framework docs component"""
        try:
            self.logger.info("Uninstalling SuperClaude framework docs component...")

            # Remove framework files
            removed_count = 0
            for filename in self.component_files:
                file_path = self.install_dir / filename
                if self.file_manager.remove_file(file_path):
                    removed_count += 1
                    self.logger.debug(f"Removed {filename}")
                else:
                    self.logger.warning(f"Could not remove {filename}")

            # Update metadata to remove framework docs component
            try:
                if self.settings_manager.is_component_installed("framework_docs"):
                    self.settings_manager.remove_component_registration("framework_docs")
                    metadata_mods = self.get_metadata_modifications()
                    metadata = self.settings_manager.load_metadata()
                    for key in metadata_mods.keys():
                        if key in metadata:
                            del metadata[key]

                    self.settings_manager.save_metadata(metadata)
                    self.logger.info("Removed framework docs component from metadata")
            except Exception as e:
                self.logger.warning(f"Could not update metadata: {e}")

            self.logger.success(
                f"Framework docs component uninstalled ({removed_count} files removed)"
            )
            return True

        except Exception as e:
            self.logger.exception(f"Unexpected error during framework docs uninstallation: {e}")
            return False

    def get_dependencies(self) -> List[str]:
        """Get component dependencies (framework docs has none)"""
        return []

    def update(self, config: Dict[str, Any]) -> bool:
        """
        Sync framework docs component (overwrite + delete obsolete files).
        No backup needed - SuperClaude source files are always authoritative.
        """
        try:
            self.logger.info("Syncing SuperClaude framework docs component...")

            # Get previously installed files from metadata
            metadata = self.settings_manager.load_metadata()
            previous_files = set(
                metadata.get("components", {})
                .get("framework_docs", {})
                .get("files", [])
            )

            # Get current files from source
            current_files = set(self.component_files)

            # Files to delete (were installed before, but no longer in source)
            files_to_delete = previous_files - current_files

            # Delete obsolete files
            deleted_count = 0
            for filename in files_to_delete:
                file_path = self.install_dir / filename
                if file_path.exists():
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted obsolete file: {filename}")
                    except Exception as e:
                        self.logger.warning(f"Could not delete {filename}: {e}")

            # Install/overwrite current files (no backup)
            success = self.install(config)

            if success:
                # Update metadata with current file list
                self.settings_manager.add_component_registration(
                    "framework_docs",
                    {
                        "version": __version__,
                        "category": "documentation",
                        "files_count": len(current_files),
                        "files": list(current_files),  # Track installed files
                    },
                )

                self.logger.success(
                    f"Framework docs synced: {len(current_files)} files, {deleted_count} obsolete files removed"
                )
            else:
                self.logger.error("Framework docs sync failed")

            return success

        except Exception as e:
            self.logger.exception(f"Unexpected error during framework docs sync: {e}")
            return False

    def validate_installation(self) -> Tuple[bool, List[str]]:
        """Validate framework docs component installation"""
        errors = []

        # Check if all framework files exist
        for filename in self.component_files:
            file_path = self.install_dir / filename
            if not file_path.exists():
                errors.append(f"Missing framework file: {filename}")
            elif not file_path.is_file():
                errors.append(f"Framework file is not a regular file: {filename}")

        # Check metadata registration
        if not self.settings_manager.is_component_installed("framework_docs"):
            errors.append("Framework docs component not registered in metadata")
        else:
            # Check version matches
            installed_version = self.settings_manager.get_component_version("framework_docs")
            expected_version = self.get_metadata()["version"]
            if installed_version != expected_version:
                errors.append(
                    f"Version mismatch: installed {installed_version}, expected {expected_version}"
                )

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

    def _get_source_dir(self):
        """Get source directory for framework documentation files"""
        # Assume we're in superclaude/setup/components/framework_docs.py
        # and framework files are in superclaude/superclaude/core/
        project_root = Path(__file__).parent.parent.parent
        return project_root / "superclaude" / "core"

    def get_size_estimate(self) -> int:
        """Get estimated installation size"""
        total_size = 0
        source_dir = self._get_source_dir()

        for filename in self.component_files:
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
            "files_installed": len(self.component_files),
            "framework_files": self.component_files,
            "estimated_size": self.get_size_estimate(),
            "install_directory": str(self.install_dir),
            "dependencies": self.get_dependencies(),
        }
