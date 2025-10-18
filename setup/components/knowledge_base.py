"""
Knowledge Base Component for SuperClaude

Responsibility: Provides structured knowledge initialization for the framework.
Manages framework knowledge documents (principles, rules, flags, research config, business patterns).
These files form the foundation of Claude's understanding of the SuperClaude framework.
"""

from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import shutil

from ..core.base import Component
from ..services.claude_md import CLAUDEMdService
from setup import __version__


class KnowledgeBaseComponent(Component):
    """
    Knowledge Base Component

    Responsibility: Initialize and maintain SuperClaude's knowledge base.
    Installs framework knowledge documents that guide Claude's behavior and decision-making.
    """

    def __init__(self, install_dir: Optional[Path] = None):
        """Initialize knowledge base component"""
        super().__init__(install_dir)

    def get_metadata(self) -> Dict[str, str]:
        """Get component metadata"""
        return {
            "name": "knowledge_base",
            "version": __version__,
            "description": "SuperClaude knowledge base (principles, rules, flags, patterns)",
            "category": "knowledge",
        }

    def is_reinstallable(self) -> bool:
        """
        Framework docs should always be updated to latest version.
        SuperClaude-related documentation should always overwrite existing files.
        """
        return True

    def validate_prerequisites(
        self, installSubPath: Optional[Path] = None
    ) -> Tuple[bool, List[str]]:
        """
        Check prerequisites for framework docs component (multi-directory support)

        Returns:
            Tuple of (success: bool, error_messages: List[str])
        """
        from ..utils.security import SecurityValidator

        errors = []

        # Check if all source directories exist
        for source_dir in self._get_source_dirs():
            if not source_dir.exists():
                errors.append(f"Source directory not found: {source_dir}")

        # Check if all required framework files exist
        missing_files = []
        for source, _ in self.get_files_to_install():
            if not source.exists():
                missing_files.append(str(source.relative_to(Path(__file__).parent.parent.parent / "superclaude")))

        if missing_files:
            errors.append(f"Missing component files: {missing_files}")

        # Check write permissions to install directory
        has_perms, missing = SecurityValidator.check_permissions(
            self.install_dir, {"write"}
        )
        if not has_perms:
            errors.append(f"No write permissions to {self.install_dir}: {missing}")

        # Validate installation target
        is_safe, validation_errors = SecurityValidator.validate_installation_target(
            self.install_component_subdir
        )
        if not is_safe:
            errors.extend(validation_errors)

        # Validate files individually (each file with its own source dir)
        for source, target in self.get_files_to_install():
            # Get the appropriate base source directory for this file
            source_parent = source.parent

            # Validate source path
            is_safe, msg = SecurityValidator.validate_path(source, source_parent)
            if not is_safe:
                errors.append(f"Invalid source path {source}: {msg}")

            # Validate target path
            is_safe, msg = SecurityValidator.validate_path(target, self.install_component_subdir)
            if not is_safe:
                errors.append(f"Invalid target path {target}: {msg}")

            # Validate file extension
            is_allowed, msg = SecurityValidator.validate_file_extension(source)
            if not is_allowed:
                errors.append(f"File {source}: {msg}")

        if not self.file_manager.ensure_directory(self.install_component_subdir):
            errors.append(
                f"Could not create install directory: {self.install_component_subdir}"
            )

        return len(errors) == 0, errors

    def get_metadata_modifications(self) -> Dict[str, Any]:
        """Get metadata modifications for SuperClaude"""
        return {
            "framework": {
                "version": __version__,
                "name": "superclaude",
                "description": "AI-enhanced development framework for Claude Code",
                "installation_type": "global",
                "components": ["knowledge_base"],
            },
            "superclaude": {
                "enabled": True,
                "version": __version__,
                "profile": "default",
                "auto_update": False,
            },
        }

    def _install(self, config: Dict[str, Any]) -> bool:
        """Install knowledge base component"""
        self.logger.info("Installing SuperClaude knowledge base...")

        return super()._install(config)

    def _post_install(self) -> bool:
        # Create or update metadata
        try:
            metadata_mods = self.get_metadata_modifications()
            self.settings_manager.update_metadata(metadata_mods)
            self.logger.info("Updated metadata with framework configuration")

            # Add component registration to metadata (with file list for sync)
            self.settings_manager.add_component_registration(
                "knowledge_base",
                {
                    "version": __version__,
                    "category": "documentation",
                    "files_count": len(self.component_files),
                    "files": list(self.component_files),  # Track for sync/deletion
                },
            )

            self.logger.info("Updated metadata with knowledge base component registration")

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
        """Uninstall knowledge base component"""
        try:
            self.logger.info("Uninstalling SuperClaude knowledge base component...")

            # Remove framework files
            removed_count = 0
            for filename in self.component_files:
                file_path = self.install_component_subdir / filename
                if self.file_manager.remove_file(file_path):
                    removed_count += 1
                    self.logger.debug(f"Removed {filename}")
                else:
                    self.logger.warning(f"Could not remove {filename}")

            # Update metadata to remove knowledge base component
            try:
                if self.settings_manager.is_component_installed("framework_docs"):
                    self.settings_manager.remove_component_registration("framework_docs")
                    metadata_mods = self.get_metadata_modifications()
                    metadata = self.settings_manager.load_metadata()
                    for key in metadata_mods.keys():
                        if key in metadata:
                            del metadata[key]

                    self.settings_manager.save_metadata(metadata)
                    self.logger.info("Removed knowledge base component from metadata")
            except Exception as e:
                self.logger.warning(f"Could not update metadata: {e}")

            self.logger.success(
                f"Framework docs component uninstalled ({removed_count} files removed)"
            )
            return True

        except Exception as e:
            self.logger.exception(f"Unexpected error during knowledge base uninstallation: {e}")
            return False

    def get_dependencies(self) -> List[str]:
        """Get component dependencies (knowledge base has none)"""
        return []

    def update(self, config: Dict[str, Any]) -> bool:
        """
        Sync knowledge base component (overwrite + delete obsolete files).
        No backup needed - SuperClaude source files are always authoritative.
        """
        try:
            self.logger.info("Syncing SuperClaude knowledge base component...")

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
                file_path = self.install_component_subdir / filename
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
            self.logger.exception(f"Unexpected error during knowledge base sync: {e}")
            return False

    def validate_installation(self) -> Tuple[bool, List[str]]:
        """Validate knowledge base component installation"""
        errors = []

        # Check if all framework files exist
        for filename in self.component_files:
            file_path = self.install_component_subdir / filename
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

    def _get_source_dirs(self):
        """Get source directories for framework documentation files"""
        # Assume we're in superclaude/setup/components/framework_docs.py
        # Framework files are organized in superclaude/{framework,business,research}
        project_root = Path(__file__).parent.parent.parent
        return [
            project_root / "superclaude" / "framework",
            project_root / "superclaude" / "business",
            project_root / "superclaude" / "research",
        ]

    def _get_source_dir(self):
        """Get source directory (compatibility method, returns first directory)"""
        dirs = self._get_source_dirs()
        return dirs[0] if dirs else None

    def _discover_component_files(self) -> List[str]:
        """
        Discover framework .md files across multiple directories

        Returns:
            List of relative paths (e.g., ['framework/flags.md', 'business/examples.md'])
        """
        all_files = []
        project_root = Path(__file__).parent.parent.parent / "superclaude"

        for source_dir in self._get_source_dirs():
            if not source_dir.exists():
                self.logger.warning(f"Source directory not found: {source_dir}")
                continue

            # Get directory name relative to superclaude/
            dir_name = source_dir.relative_to(project_root)

            # Discover .md files in this directory
            files = self._discover_files_in_directory(
                source_dir,
                extension=".md",
                exclude_patterns=["README.md", "CHANGELOG.md", "LICENSE.md"],
            )

            # Add directory prefix to each file
            for file in files:
                all_files.append(str(dir_name / file))

        return all_files

    def get_files_to_install(self) -> List[Tuple[Path, Path]]:
        """
        Return list of files to install from multiple source directories

        Returns:
            List of tuples (source_path, target_path)
        """
        files = []
        project_root = Path(__file__).parent.parent.parent / "superclaude"

        for relative_path in self.component_files:
            source = project_root / relative_path
            # Install to superclaude/ subdirectory structure
            target = self.install_component_subdir / relative_path
            files.append((source, target))

        return files

    def get_size_estimate(self) -> int:
        """Get estimated installation size"""
        total_size = 0

        for source, _ in self.get_files_to_install():
            if source.exists():
                total_size += source.stat().st_size

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
