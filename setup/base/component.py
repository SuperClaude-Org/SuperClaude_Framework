"""
Abstract base class for installable components
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import json
from ..managers.file_manager import FileManager
from ..managers.settings_manager import SettingsManager
from ..utils.logger import get_logger
from ..utils.security import SecurityValidator


class Component(ABC):
    """Base class for all installable components"""
    
    def __init__(self, install_dir: Optional[Path] = None, component_subdir: Path = Path('')):
        """
        Initialize component with installation directory
        
        Args:
            install_dir: Target installation directory (defaults to ~/.claude)
        """
        from .. import DEFAULT_INSTALL_DIR
        self.install_dir = install_dir or DEFAULT_INSTALL_DIR
        self.settings_manager = SettingsManager(self.install_dir)
        self.logger = get_logger()
        self.component_files = self._discover_component_files()
        self.file_manager = FileManager()
        self.install_component_subdir = self.install_dir / component_subdir
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, str]:
        """
        Return component metadata
        
        Returns:
            Dict containing:
                - name: Component name
                - version: Component version
                - description: Component description
                - category: Component category (core, command, integration, etc.)
        """
        pass
    
    def validate_prerequisites(self, installSubPath: Optional[Path] = None) -> Tuple[bool, List[str]]:
        """
        Check prerequisites for this component
        
        Returns:
            Tuple of (success: bool, error_messages: List[str])
        """
        errors = []

        # Check if we have read access to source files
        source_dir = self._get_source_dir()
        if not source_dir or (source_dir and not source_dir.exists()):
            errors.append(f"Source directory not found: {source_dir}")
            return False, errors

        # Check if all required framework files exist
        missing_files = []
        for filename in self.component_files:
            source_file = source_dir / filename
            if not source_file.exists():
                missing_files.append(filename)

        if missing_files:
            errors.append(f"Missing component files: {missing_files}")

        # Check write permissions to install directory
        has_perms, missing = SecurityValidator.check_permissions(
            self.install_dir, {'write'}
        )
        if not has_perms:
            errors.append(f"No write permissions to {self.install_dir}: {missing}")

        # Validate installation target
        is_safe, validation_errors = SecurityValidator.validate_installation_target(self.install_component_subdir)
        if not is_safe:
            errors.extend(validation_errors)

        # Get files to install
        files_to_install = self.get_files_to_install()

        # Validate all files for security
        is_safe, security_errors = SecurityValidator.validate_component_files(
            files_to_install, source_dir, self.install_component_subdir
        )
        if not is_safe:
            errors.extend(security_errors)

        if not self.file_manager.ensure_directory(self.install_component_subdir):
            errors.append(f"Could not create install directory: {self.install_component_subdir}")

        return len(errors) == 0, errors
    
    def get_files_to_install(self) -> List[Tuple[Path, Path]]:
        """
        Return list of files to install
        
        Returns:
            List of tuples (source_path, target_path)
        """
        source_dir = self._get_source_dir()
        files = []

        if source_dir:
            for filename in self.component_files:
                source = source_dir / filename
                target = self.install_component_subdir / filename
                files.append((source, target))

        return files
    
    def get_settings_modifications(self) -> Dict[str, Any]:
        """
        Return settings.json modifications to apply
        (now only Claude Code compatible settings)

        Returns:
            Dict of settings to merge into settings.json
        """
        # Return empty dict as we don't modify Claude Code settings
        return {}
    
    def install(self, config: Dict[str, Any]) -> bool:
        try:
            return self._install(config)
        except Exception as e:
            self.logger.exception(f"Unexpected error during {repr(self)} installation: {e}")
            return False

    @abstractmethod
    def _install(self, config: Dict[str, Any]) -> bool:
        """
        Perform component-specific installation logic
        
        Args:
            config: Installation configuration
            
        Returns:
            True if successful, False otherwise
        """
        # Validate installation
        success, errors = self.validate_prerequisites()
        if not success:
            for error in errors:
                self.logger.error(error)
            return False

        # Get files to install
        files_to_install = self.get_files_to_install()

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

        self.logger.success(f"{repr(self)} component installed successfully ({success_count} files)")

        return self._post_install()

    
    @abstractmethod
    def _post_install(self) -> bool:
        pass


    @abstractmethod
    def uninstall(self) -> bool:
        """
        Remove component
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        Return list of component dependencies
        
        Returns:
            List of component names this component depends on
        """
        pass

    @abstractmethod
    def _get_source_dir(self) -> Optional[Path]:
        """Get source directory for component files"""
        pass
    
    def update(self, config: Dict[str, Any]) -> bool:
        """
        Update component (default: uninstall then install)
        
        Args:
            config: Installation configuration
            
        Returns:
            True if successful, False otherwise
        """
        # Default implementation: uninstall and reinstall
        if self.uninstall():
            return self.install(config)
        return False
    
    def get_installed_version(self) -> Optional[str]:
        """
        Get currently installed version of component
        
        Returns:
            Version string if installed, None otherwise
        """
        print("GETTING INSTALLED VERSION")
        settings_file = self.install_dir / "settings.json"
        if settings_file.exists():
            print("SETTINGS.JSON EXISTS")
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                component_name = self.get_metadata()['name']
                return settings.get('components', {}).get(component_name, {}).get('version')
            except Exception:
                pass
        print("SETTINGS.JSON DOESNT EXIST RETURNING NONE")
        return None
    
    def is_installed(self) -> bool:
        """
        Check if component is installed
        
        Returns:
            True if installed, False otherwise
        """
        return self.get_installed_version() is not None
    
    def validate_installation(self) -> Tuple[bool, List[str]]:
        """
        Validate that component is correctly installed
        
        Returns:
            Tuple of (success: bool, error_messages: List[str])
        """
        errors = []
        
        # Check if all files exist
        for _, target in self.get_files_to_install():
            if not target.exists():
                errors.append(f"Missing file: {target}")
        
        # Check version in settings
        if not self.get_installed_version():
            errors.append("Component not registered in settings.json")
        
        return len(errors) == 0, errors
    
    def get_size_estimate(self) -> int:
        """
        Estimate installed size in bytes
        
        Returns:
            Estimated size in bytes
        """
        total_size = 0
        for source, _ in self.get_files_to_install():
            if source.exists():
                if source.is_file():
                    total_size += source.stat().st_size
                elif source.is_dir():
                    total_size += sum(f.stat().st_size for f in source.rglob('*') if f.is_file())
        return total_size

    def _discover_component_files(self) -> List[str]:
        """
        Dynamically discover framework .md files in the Core directory

        Returns:
            List of framework filenames (e.g., ['CLAUDE.md', 'COMMANDS.md', ...])
        """
        source_dir = self._get_source_dir()

        if not source_dir:
            return []

        return self._discover_files_in_directory(
            source_dir,
            extension='.md',
            exclude_patterns=['README.md', 'CHANGELOG.md', 'LICENSE.md']
        )

    def _discover_files_in_directory(self, directory: Path, extension: str = '.md',
                                   exclude_patterns: Optional[List[str]] = None) -> List[str]:
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
    
    def __str__(self) -> str:
        """String representation of component"""
        metadata = self.get_metadata()
        return f"{metadata['name']} v{metadata['version']}"
    
    def __repr__(self) -> str:
        """Developer representation of component"""
        return f"<{self.__class__.__name__}({self.get_metadata()['name']})>"
