"""PM Mode Initialization Hook

Runs automatically at session start to:
1. Detect repository root and structure
2. Generate Context Contract
3. Load Reflexion Memory
4. Set up PM Mode as default
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from .context_contract import ContextContract
from .reflexion_memory import ReflexionMemory


class PMInitializer:
    """Initializes PM Mode with project context"""

    def __init__(self, cwd: Optional[Path] = None):
        self.cwd = cwd or Path.cwd()
        self.git_root: Optional[Path] = None
        self.config: Dict[str, Any] = {}

    def detect_git_root(self) -> Optional[Path]:
        """Detect Git repository root"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass
        return None

    def scan_project_structure(self) -> Dict[str, Any]:
        """Lightweight scan of project structure (paths only, no content)"""
        if not self.git_root:
            return {}

        structure = {
            "docker_compose": [],
            "infrastructure": {
                "traefik": [],
                "kong": [],
                "supabase": [],
                "infisical": []
            },
            "package_managers": {
                "node": [],
                "python": []
            },
            "config_files": []
        }

        # Docker Compose files
        for pattern in ["docker-compose*.yml", "docker-compose*.yaml"]:
            structure["docker_compose"].extend([
                str(p.relative_to(self.git_root))
                for p in self.git_root.glob(pattern)
            ])

        # Infrastructure directories
        for infra_type in ["traefik", "kong", "supabase", "infisical"]:
            infra_path = self.git_root / "infra" / infra_type
            if infra_path.exists():
                structure["infrastructure"][infra_type].append(str(infra_path.relative_to(self.git_root)))

        # Package managers
        if (self.git_root / "package.json").exists():
            structure["package_managers"]["node"].append("package.json")
        if (self.git_root / "pnpm-lock.yaml").exists():
            structure["package_managers"]["node"].append("pnpm-lock.yaml")
        if (self.git_root / "pyproject.toml").exists():
            structure["package_managers"]["python"].append("pyproject.toml")
        if (self.git_root / "uv.lock").exists():
            structure["package_managers"]["python"].append("uv.lock")

        return structure

    def initialize(self) -> Dict[str, Any]:
        """Main initialization routine"""
        # Step 1: Detect Git root
        self.git_root = self.detect_git_root()
        if not self.git_root:
            return {
                "status": "not_git_repo",
                "message": "Not a Git repository - PM Mode running in standalone mode"
            }

        # Step 2: Scan project structure (lightweight)
        structure = self.scan_project_structure()

        # Step 3: Generate or load Context Contract
        contract = ContextContract(self.git_root, structure)
        contract_data = contract.generate_or_load()

        # Step 4: Load Reflexion Memory
        memory = ReflexionMemory(self.git_root)
        memory_data = memory.load()

        # Step 5: Return initialization data
        return {
            "status": "initialized",
            "git_root": str(self.git_root),
            "structure": structure,
            "context_contract": contract_data,
            "reflexion_memory": memory_data,
            "message": "PM Mode initialized successfully"
        }


def initialize_pm_mode(cwd: Optional[Path] = None) -> Dict[str, Any]:
    """
    Initialize PM Mode as default.

    This function runs automatically at session start.

    Args:
        cwd: Current working directory (defaults to os.getcwd())

    Returns:
        Initialization status and configuration
    """
    initializer = PMInitializer(cwd)
    return initializer.initialize()
