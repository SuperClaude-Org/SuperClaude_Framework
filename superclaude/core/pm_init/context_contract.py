"""Context Contract System

Auto-generates project-specific rules that must be enforced:
- Infrastructure patterns (Kong, Traefik, Infisical)
- Security policies (.env禁止, 秘密値管理)
- Runtime requirements
- Validation requirements
"""

from pathlib import Path
from typing import Dict, Any, List
import yaml


class ContextContract:
    """Manages project-specific Context Contract"""

    def __init__(self, git_root: Path, structure: Dict[str, Any]):
        self.git_root = git_root
        self.structure = structure
        self.contract_path = git_root / "docs" / "memory" / "context-contract.yaml"

    def detect_principles(self) -> Dict[str, Any]:
        """Detect project-specific principles from structure"""
        principles = {}

        # Infisical detection
        if self.structure.get("infrastructure", {}).get("infisical"):
            principles["use_infisical_only"] = True
            principles["no_env_files"] = True
        else:
            principles["use_infisical_only"] = False
            principles["no_env_files"] = False

        # Kong detection
        if self.structure.get("infrastructure", {}).get("kong"):
            principles["outbound_through"] = "kong"
        # Traefik detection
        elif self.structure.get("infrastructure", {}).get("traefik"):
            principles["outbound_through"] = "traefik"
        else:
            principles["outbound_through"] = None

        # Supabase detection
        if self.structure.get("infrastructure", {}).get("supabase"):
            principles["supabase_integration"] = True
        else:
            principles["supabase_integration"] = False

        return principles

    def detect_runtime(self) -> Dict[str, Any]:
        """Detect runtime requirements"""
        runtime = {}

        # Node.js
        if "package.json" in self.structure.get("package_managers", {}).get("node", []):
            if "pnpm-lock.yaml" in self.structure.get("package_managers", {}).get("node", []):
                runtime["node"] = {
                    "manager": "pnpm",
                    "source": "lockfile-defined"
                }
            else:
                runtime["node"] = {
                    "manager": "npm",
                    "source": "package-json-defined"
                }

        # Python
        if "pyproject.toml" in self.structure.get("package_managers", {}).get("python", []):
            if "uv.lock" in self.structure.get("package_managers", {}).get("python", []):
                runtime["python"] = {
                    "manager": "uv",
                    "source": "lockfile-defined"
                }
            else:
                runtime["python"] = {
                    "manager": "pip",
                    "source": "pyproject-defined"
                }

        return runtime

    def detect_validators(self) -> List[str]:
        """Detect required validators"""
        validators = [
            "deps_exist_on_registry",
            "tests_must_run"
        ]

        principles = self.detect_principles()

        if principles.get("use_infisical_only"):
            validators.append("no_env_file_creation")
            validators.append("no_hardcoded_secrets")

        if principles.get("outbound_through"):
            validators.append("outbound_through_proxy")

        return validators

    def generate_contract(self) -> Dict[str, Any]:
        """Generate Context Contract from detected structure"""
        return {
            "version": "1.0.0",
            "generated_at": "auto",
            "principles": self.detect_principles(),
            "runtime": self.detect_runtime(),
            "validators": self.detect_validators(),
            "structure_snapshot": self.structure
        }

    def load_contract(self) -> Dict[str, Any]:
        """Load existing Context Contract"""
        if not self.contract_path.exists():
            return {}

        with open(self.contract_path, "r") as f:
            return yaml.safe_load(f)

    def save_contract(self, contract: Dict[str, Any]) -> None:
        """Save Context Contract to disk"""
        self.contract_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.contract_path, "w") as f:
            yaml.dump(contract, f, default_flow_style=False, sort_keys=False)

    def generate_or_load(self) -> Dict[str, Any]:
        """Generate or load Context Contract"""
        # Try to load existing
        existing = self.load_contract()

        # If exists and version matches, return it
        if existing and existing.get("version") == "1.0.0":
            return existing

        # Otherwise, generate new contract
        contract = self.generate_contract()
        self.save_contract(contract)
        return contract
