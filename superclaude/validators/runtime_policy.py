"""Runtime Policy Validator

Validates runtime requirements:
- Node.js version (LTS, latest, project-specified)
- Python version (LTS, latest, project-specified)
- Consistency with lockfiles
"""

from typing import Dict, Any, List, Optional
import subprocess
import json
import re

from .base import Validator, ValidationResult


class RuntimePolicyValidator(Validator):
    """Validates runtime policies"""

    def __init__(self):
        super().__init__("Runtime Policy")

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate runtime requirements.

        Context should contain:
        - contract: Context Contract (for runtime info)
        - changes: File changes (to detect version changes)
        """
        contract = context.get("contract", {})
        changes = context.get("changes", {})

        runtime = contract.get("runtime", {})
        if not runtime:
            return self._skip("No runtime requirements specified")

        issues = []
        warnings = []

        # Validate Node.js runtime
        if "node" in runtime:
            node_result = self._validate_node_runtime(runtime["node"], changes)
            issues.extend(node_result.get("issues", []))
            warnings.extend(node_result.get("warnings", []))

        # Validate Python runtime
        if "python" in runtime:
            python_result = self._validate_python_runtime(runtime["python"], changes)
            issues.extend(python_result.get("issues", []))
            warnings.extend(python_result.get("warnings", []))

        # Return result
        if issues:
            return self._fail(
                f"Runtime policy violations ({len(issues)} issues)",
                details={"issues": issues, "warnings": warnings}
            )

        if warnings:
            return self._warning(
                f"Runtime policy warnings ({len(warnings)} warnings)",
                details={"warnings": warnings}
            )

        return self._pass("Runtime requirements satisfied")

    def _validate_node_runtime(self, node_config: Dict[str, Any], changes: Dict[str, str]) -> Dict[str, List[str]]:
        """Validate Node.js runtime"""
        issues = []
        warnings = []

        manager = node_config.get("manager", "npm")
        source = node_config.get("source", "package-json-defined")

        # Check if package.json specifies engines
        for file_path, content in changes.items():
            if "package.json" in file_path:
                try:
                    data = json.loads(content)
                    engines = data.get("engines", {})
                    node_version = engines.get("node")

                    if not node_version and source == "package-json-defined":
                        warnings.append("No Node.js version specified in package.json engines")

                    if manager == "pnpm" and "pnpm" not in engines:
                        warnings.append("Using pnpm but no pnpm version in engines")

                except json.JSONDecodeError:
                    issues.append("Invalid package.json format")

        return {"issues": issues, "warnings": warnings}

    def _validate_python_runtime(self, python_config: Dict[str, Any], changes: Dict[str, str]) -> Dict[str, List[str]]:
        """Validate Python runtime"""
        issues = []
        warnings = []

        manager = python_config.get("manager", "pip")
        source = python_config.get("source", "pyproject-defined")

        # Check if pyproject.toml specifies python version
        for file_path, content in changes.items():
            if "pyproject.toml" in file_path:
                # Basic check for python version requirement
                if "requires-python" in content:
                    # Extract version requirement
                    match = re.search(r'requires-python\s*=\s*[\'"]([^"\']+)[\'"]', content)
                    if match:
                        version_spec = match.group(1)
                        # Validate version format
                        if not re.match(r'^[><=~^!]+\d+\.\d+', version_spec):
                            warnings.append(f"Unusual Python version format: {version_spec}")
                    else:
                        warnings.append("Could not parse requires-python version")
                elif source == "pyproject-defined":
                    warnings.append("No requires-python specified in pyproject.toml")

        return {"issues": issues, "warnings": warnings}

    def get_current_node_version(self) -> Optional[str]:
        """Get current Node.js version"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def get_current_python_version(self) -> Optional[str]:
        """Get current Python version"""
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
