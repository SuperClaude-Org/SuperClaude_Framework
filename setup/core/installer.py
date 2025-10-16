"""
Base installer logic for SuperClaude installation system fixed some issues
"""

from typing import List, Dict, Optional, Set, Tuple, Any
from pathlib import Path
import shutil
import tempfile
from datetime import datetime
from .base import Component
from ..utils.logger import get_logger


class Installer:
    """Main installer orchestrator"""

    def __init__(self, install_dir: Optional[Path] = None, dry_run: bool = False):
        """
        Initialize installer

        Args:
            install_dir: Target installation directory
            dry_run: If True, only simulate installation
        """
        from .. import DEFAULT_INSTALL_DIR

        self.install_dir = install_dir or DEFAULT_INSTALL_DIR
        self.dry_run = dry_run
        self.components: Dict[str, Component] = {}
        from ..services.settings import SettingsService

        settings_manager = SettingsService(self.install_dir)
        self.installed_components: Set[str] = set(
            settings_manager.get_installed_components().keys()
        )
        self.updated_components: Set[str] = set()

        self.failed_components: Set[str] = set()
        self.skipped_components: Set[str] = set()
        self.logger = get_logger()

    def register_component(self, component: Component) -> None:
        """
        Register a component for installation

        Args:
            component: Component instance to register
        """
        metadata = component.get_metadata()
        self.components[metadata["name"]] = component

    def register_components(self, components: List[Component]) -> None:
        """
        Register multiple components

        Args:
            components: List of component instances
        """
        for component in components:
            self.register_component(component)

    def resolve_dependencies(self, component_names: List[str]) -> List[str]:
        """
        Resolve component dependencies in correct installation order

        Args:
            component_names: List of component names to install

        Returns:
            Ordered list of component names including dependencies

        Raises:
            ValueError: If circular dependencies detected or unknown component
        """
        resolved = []
        resolving = set()

        def resolve(name: str) -> None:
            if name in resolved:
                return

            if name in resolving:
                raise ValueError(f"Circular dependency detected involving {name}")

            if name not in self.components:
                raise ValueError(f"Unknown component: {name}")

            resolving.add(name)

            # Resolve dependencies first
            for dep in self.components[name].get_dependencies():
                resolve(dep)

            resolving.remove(name)
            resolved.append(name)

        # Resolve each requested component
        for name in component_names:
            resolve(name)

        return resolved

    def validate_system_requirements(self) -> Tuple[bool, List[str]]:
        """
        Validate system requirements for all registered components

        Returns:
            Tuple of (success: bool, error_messages: List[str])
        """
        errors = []

        # Check disk space (500MB minimum)
        try:
            stat = shutil.disk_usage(self.install_dir.parent)
            free_mb = stat.free / (1024 * 1024)
            if free_mb < 500:
                errors.append(
                    f"Insufficient disk space: {free_mb:.1f}MB free (500MB required)"
                )
        except Exception as e:
            errors.append(f"Could not check disk space: {e}")

        # Check write permissions
        test_file = self.install_dir / ".write_test"
        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            errors.append(f"No write permission to {self.install_dir}: {e}")

        return len(errors) == 0, errors

    def install_component(self, component_name: str, config: Dict[str, Any]) -> bool:
        """
        Install a single component

        Args:
            component_name: Name of component to install
            config: Installation configuration

        Returns:
            True if successful, False otherwise
        """
        if component_name not in self.components:
            raise ValueError(f"Unknown component: {component_name}")

        component = self.components[component_name]

        # Framework components are ALWAYS updated to latest version
        # These are SuperClaude implementation files, not user configurations
        framework_components = {'framework_docs', 'agents', 'commands', 'modes', 'core', 'mcp'}

        if component_name in framework_components:
            # Always update framework components to latest version
            if component_name in self.installed_components:
                self.logger.info(f"Updating framework component to latest version: {component_name}")
            else:
                self.logger.info(f"Installing framework component: {component_name}")
            # Force update for framework components
            config = {**config, 'force_update': True}
        elif (
            not component.is_reinstallable()
            and component_name in self.installed_components
            and not config.get("update_mode")
            and not config.get("force")
        ):
            # Only skip non-framework components that are already installed
            self.skipped_components.add(component_name)
            self.logger.info(f"Skipping already installed component: {component_name}")
            return True

        # Check prerequisites
        success, errors = component.validate_prerequisites()
        if not success:
            self.logger.error(f"Prerequisites failed for {component_name}:")
            for error in errors:
                self.logger.error(f"  - {error}")
            self.failed_components.add(component_name)
            return False

        # Perform installation or update
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would install {component_name}")
                success = True
            else:
                # If component is already installed and this is a framework component, call update() instead of install()
                if component_name in self.installed_components and component_name in framework_components:
                    success = component.update(config)
                else:
                    success = component.install(config)

            if success:
                self.installed_components.add(component_name)
                self.updated_components.add(component_name)
            else:
                self.failed_components.add(component_name)

            return success

        except Exception as e:
            self.logger.error(f"Error installing {component_name}: {e}")
            self.failed_components.add(component_name)
            return False

    def install_components(
        self, component_names: List[str], config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Install multiple components in dependency order

        Args:
            component_names: List of component names to install
            config: Installation configuration

        Returns:
            True if all successful, False if any failed
        """
        config = config or {}

        # Resolve dependencies
        try:
            ordered_names = self.resolve_dependencies(component_names)
        except ValueError as e:
            self.logger.error(f"Dependency resolution error: {e}")
            return False

        # Validate system requirements
        success, errors = self.validate_system_requirements()
        if not success:
            self.logger.error("System requirements not met:")
            for error in errors:
                self.logger.error(f"  - {error}")
            return False

        # Install each component
        all_success = True
        for name in ordered_names:
            self.logger.info(f"Installing {name}...")
            if not self.install_component(name, config):
                all_success = False
                # Continue installing other components even if one fails

        if not self.dry_run:
            self._run_post_install_validation()

        return all_success

    def _run_post_install_validation(self) -> None:
        """Run post-installation validation for all installed components"""
        self.logger.info("Running post-installation validation...")

        all_valid = True
        for name in self.updated_components:
            if name not in self.components:
                self.logger.warning(
                    f"Cannot validate component '{name}' as it was not part of this installation session."
                )
                continue

            component = self.components[name]
            success, errors = component.validate_installation()

            if success:
                self.logger.info(f"  + {name}: Valid")
            else:
                self.logger.error(f"  x {name}: Invalid")
                for error in errors:
                    self.logger.error(f"    - {error}")
                all_valid = False

        if all_valid:
            self.logger.info("All components validated successfully!")
        else:
            self.logger.error("Some components failed validation. Check errors above.")

    def update_components(
        self, component_names: List[str], config: Dict[str, Any]
    ) -> bool:
        """Alias for update operation (uses install logic)"""
        config["update_mode"] = True
        return self.install_components(component_names, config)

    def get_installation_summary(self) -> Dict[str, Any]:
        """
        Get summary of installation results

        Returns:
            Dict with installation statistics and results
        """
        return {
            "installed": list(self.installed_components),
            "failed": list(self.failed_components),
            "skipped": list(self.skipped_components),
            "install_dir": str(self.install_dir),
            "dry_run": self.dry_run,
        }

    def get_update_summary(self) -> Dict[str, Any]:
        return {
            "updated": list(self.updated_components),
            "failed": list(self.failed_components),
        }
