"""
Component registry for auto-discovery and dependency resolution
"""

import importlib
import inspect
from typing import Dict, List, Set, Optional, Type
from pathlib import Path
from .base import Component
from ..utils.logger import get_logger


class ComponentRegistry:
    """Auto-discovery and management of installable components"""

    def __init__(self, components_dir: Path):
        """
        Initialize component registry

        Args:
            components_dir: Directory containing component modules
        """
        self.components_dir = components_dir
        self.component_classes: Dict[str, Type[Component]] = {}
        self.component_instances: Dict[str, Component] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self._discovered = False
        self.logger = get_logger()

    def discover_components(self, force_reload: bool = False) -> None:
        """
        Auto-discover all component classes in components directory

        Args:
            force_reload: Force rediscovery even if already done
        """
        if self._discovered and not force_reload:
            return

        self.component_classes.clear()
        self.component_instances.clear()
        self.dependency_graph.clear()

        if not self.components_dir.exists():
            return

        # Add components directory to Python path temporarily
        import sys

        original_path = sys.path.copy()

        try:
            # Add parent directory to path so we can import setup.components
            setup_dir = self.components_dir.parent
            if str(setup_dir) not in sys.path:
                sys.path.insert(0, str(setup_dir))

            # Discover all Python files in components directory
            for py_file in self.components_dir.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                module_name = py_file.stem
                self._load_component_module(module_name)

        finally:
            # Restore original Python path
            sys.path = original_path

        # Build dependency graph
        self._build_dependency_graph()
        self._discovered = True

    def _load_component_module(self, module_name: str) -> None:
        """
        Load component classes from a module

        Args:
            module_name: Name of module to load
        """
        try:
            # Import the module
            full_module_name = f"setup.components.{module_name}"
            module = importlib.import_module(full_module_name)

            # Find all Component subclasses in the module
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Component)
                    and obj is not Component
                ):

                    # Create instance to get metadata
                    try:
                        instance = obj()
                        metadata = instance.get_metadata()
                        component_name = metadata["name"]

                        self.component_classes[component_name] = obj
                        self.component_instances[component_name] = instance

                    except Exception as e:
                        self.logger.warning(
                            f"Could not instantiate component {name}: {e}"
                        )

        except Exception as e:
            self.logger.warning(f"Could not load component module {module_name}: {e}")

    def _build_dependency_graph(self) -> None:
        """Build dependency graph for all discovered components"""
        for name, instance in self.component_instances.items():
            try:
                dependencies = instance.get_dependencies()
                self.dependency_graph[name] = set(dependencies)
            except Exception as e:
                self.logger.warning(f"Could not get dependencies for {name}: {e}")
                self.dependency_graph[name] = set()

    def get_component_class(self, component_name: str) -> Optional[Type[Component]]:
        """
        Get component class by name

        Args:
            component_name: Name of component

        Returns:
            Component class or None if not found
        """
        self.discover_components()
        return self.component_classes.get(component_name)

    def get_component_instance(
        self, component_name: str, install_dir: Optional[Path] = None
    ) -> Optional[Component]:
        """
        Get component instance by name

        Args:
            component_name: Name of component
            install_dir: Installation directory (creates new instance with this dir)

        Returns:
            Component instance or None if not found
        """
        self.discover_components()

        if install_dir is not None:
            # Create new instance with specified install directory
            component_class = self.component_classes.get(component_name)
            if component_class:
                try:
                    return component_class(install_dir)
                except Exception as e:
                    self.logger.error(
                        f"Error creating component instance {component_name}: {e}"
                    )
                    return None

        return self.component_instances.get(component_name)

    def list_components(self) -> List[str]:
        """
        Get list of all discovered component names

        Returns:
            List of component names
        """
        self.discover_components()
        return list(self.component_classes.keys())

    def get_component_metadata(self, component_name: str) -> Optional[Dict[str, str]]:
        """
        Get metadata for a component

        Args:
            component_name: Name of component

        Returns:
            Component metadata dict or None if not found
        """
        self.discover_components()
        instance = self.component_instances.get(component_name)
        if instance:
            try:
                return instance.get_metadata()
            except Exception:
                return None
        return None

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
        self.discover_components()

        resolved = []
        resolving = set()

        def resolve(name: str):
            if name in resolved:
                return

            if name in resolving:
                raise ValueError(f"Circular dependency detected involving {name}")

            if name not in self.dependency_graph:
                raise ValueError(f"Unknown component: {name}")

            resolving.add(name)

            # Resolve dependencies first
            for dep in self.dependency_graph[name]:
                resolve(dep)

            resolving.remove(name)
            resolved.append(name)

        # Resolve each requested component
        for name in component_names:
            resolve(name)

        return resolved

    def get_dependencies(self, component_name: str) -> Set[str]:
        """
        Get direct dependencies for a component

        Args:
            component_name: Name of component

        Returns:
            Set of dependency component names
        """
        self.discover_components()
        return self.dependency_graph.get(component_name, set())

    def get_dependents(self, component_name: str) -> Set[str]:
        """
        Get components that depend on the given component

        Args:
            component_name: Name of component

        Returns:
            Set of component names that depend on this component
        """
        self.discover_components()
        dependents = set()

        for name, deps in self.dependency_graph.items():
            if component_name in deps:
                dependents.add(name)

        return dependents

    def validate_dependency_graph(self) -> List[str]:
        """
        Validate dependency graph for cycles and missing dependencies

        Returns:
            List of validation errors (empty if valid)
        """
        self.discover_components()
        errors = []

        # Check for missing dependencies
        all_components = set(self.dependency_graph.keys())
        for name, deps in self.dependency_graph.items():
            missing_deps = deps - all_components
            if missing_deps:
                errors.append(
                    f"Component {name} has missing dependencies: {missing_deps}"
                )

        # Check for circular dependencies
        for name in all_components:
            try:
                self.resolve_dependencies([name])
            except ValueError as e:
                errors.append(str(e))

        return errors

    def get_components_by_category(self, category: str) -> List[str]:
        """
        Get components filtered by category

        Args:
            category: Component category to filter by

        Returns:
            List of component names in the category
        """
        self.discover_components()
        components = []

        for name, instance in self.component_instances.items():
            try:
                metadata = instance.get_metadata()
                if metadata.get("category") == category:
                    components.append(name)
            except Exception:
                continue

        return components

    def get_installation_order(self, component_names: List[str]) -> List[List[str]]:
        """
        Get installation order grouped by dependency levels

        Args:
            component_names: List of component names to install

        Returns:
            List of lists, where each inner list contains components
            that can be installed in parallel at that dependency level
        """
        self.discover_components()

        # Get all components including dependencies
        all_components = set(self.resolve_dependencies(component_names))

        # Group by dependency level
        levels = []
        remaining = all_components.copy()

        while remaining:
            # Find components with no unresolved dependencies
            current_level = []
            for name in list(remaining):
                deps = self.dependency_graph.get(name, set())
                unresolved_deps = deps & remaining

                if not unresolved_deps:
                    current_level.append(name)

            if not current_level:
                # This shouldn't happen if dependency graph is valid
                raise ValueError(
                    "Circular dependency detected in installation order calculation"
                )

            levels.append(current_level)
            remaining -= set(current_level)

        return levels

    def create_component_instances(
        self, component_names: List[str], install_dir: Optional[Path] = None
    ) -> Dict[str, Component]:
        """
        Create instances for multiple components

        Args:
            component_names: List of component names
            install_dir: Installation directory for instances

        Returns:
            Dict mapping component names to instances
        """
        self.discover_components()
        instances = {}

        for name in component_names:
            instance = self.get_component_instance(name, install_dir)
            if instance:
                instances[name] = instance
            else:
                self.logger.warning(f"Could not create instance for component {name}")

        return instances

    def get_registry_info(self) -> Dict[str, any]:
        """
        Get comprehensive registry information

        Returns:
            Dict with registry statistics and component info
        """
        self.discover_components()

        # Group components by category
        categories = {}
        for name, instance in self.component_instances.items():
            try:
                metadata = instance.get_metadata()
                category = metadata.get("category", "unknown")
                if category not in categories:
                    categories[category] = []
                categories[category].append(name)
            except Exception:
                if "unknown" not in categories:
                    categories["unknown"] = []
                categories["unknown"].append(name)

        return {
            "total_components": len(self.component_classes),
            "categories": categories,
            "dependency_graph": {
                name: list(deps) for name, deps in self.dependency_graph.items()
            },
            "validation_errors": self.validate_dependency_graph(),
        }
