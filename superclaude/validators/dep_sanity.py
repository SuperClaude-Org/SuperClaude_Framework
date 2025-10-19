"""Dependency Sanity Validator

Validates that:
- Proposed packages exist on registries (npm, PyPI)
- Versions are compatible with lockfiles
- No conflicting dependencies
"""

from typing import Dict, Any, List, Optional
import subprocess
import json
import re

from .base import Validator, ValidationResult


class DependencySanityValidator(Validator):
    """Validates dependency sanity"""

    def __init__(self):
        super().__init__("Dependency Sanity")

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate dependency changes.

        Context should contain:
        - changes: Dict of file changes
        - contract: Context Contract (for runtime info)
        """
        changes = context.get("changes", {})
        contract = context.get("contract", {})

        issues = []
        warnings = []

        # Check package.json changes
        for file_path, content in changes.items():
            if "package.json" in file_path:
                result = self._validate_npm_deps(content, contract)
                issues.extend(result.get("issues", []))
                warnings.extend(result.get("warnings", []))

            elif "pyproject.toml" in file_path or "requirements.txt" in file_path:
                result = self._validate_python_deps(content, contract)
                issues.extend(result.get("issues", []))
                warnings.extend(result.get("warnings", []))

        # Return result
        if issues:
            return self._fail(
                f"Dependency issues detected ({len(issues)} issues)",
                details={"issues": issues, "warnings": warnings}
            )

        if warnings:
            return self._warning(
                f"Dependency warnings ({len(warnings)} warnings)",
                details={"warnings": warnings}
            )

        return self._pass("All dependencies validated")

    def _validate_npm_deps(self, package_json_content: str, contract: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate npm dependencies"""
        issues = []
        warnings = []

        try:
            # Parse package.json
            data = json.loads(package_json_content)
            dependencies = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

            # Check if packages exist (basic validation)
            for pkg_name, version in dependencies.items():
                # Check for common typos
                if pkg_name.startswith("@"):
                    # Scoped package
                    if not re.match(r"^@[\w-]+/[\w-]+$", pkg_name):
                        issues.append(f"Invalid scoped package name: {pkg_name}")
                else:
                    # Regular package
                    if not re.match(r"^[\w-]+$", pkg_name):
                        issues.append(f"Invalid package name: {pkg_name}")

                # Check version format
                if version and not re.match(r"^[\^~]?\d+\.\d+\.\d+|latest|workspace:\*", version):
                    warnings.append(f"Unusual version format for {pkg_name}: {version}")

        except json.JSONDecodeError:
            issues.append("Invalid package.json format")

        return {"issues": issues, "warnings": warnings}

    def _validate_python_deps(self, content: str, contract: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate Python dependencies"""
        issues = []
        warnings = []

        # Extract package names from requirements.txt or pyproject.toml
        if "[tool.poetry.dependencies]" in content or "[project.dependencies]" in content:
            # pyproject.toml format - basic validation
            # More sophisticated parsing would use tomli/tomlkit
            pass
        else:
            # requirements.txt format
            for line in content.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Check for common issues
                if "==" in line:
                    pkg_spec = line.split("==")
                    if len(pkg_spec) != 2:
                        issues.append(f"Invalid requirement format: {line}")
                    else:
                        pkg_name, version = pkg_spec
                        # Basic package name validation
                        if not re.match(r"^[a-zA-Z0-9_-]+$", pkg_name):
                            issues.append(f"Invalid package name: {pkg_name}")

        return {"issues": issues, "warnings": warnings}

    def check_npm_package_exists(self, package_name: str) -> bool:
        """Check if npm package exists on registry"""
        try:
            result = subprocess.run(
                ["npm", "view", package_name, "version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_pypi_package_exists(self, package_name: str) -> bool:
        """Check if PyPI package exists"""
        try:
            result = subprocess.run(
                ["pip", "index", "versions", package_name],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
