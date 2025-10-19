"""Context Contract Validator

Enforces project-specific rules from Context Contract:
- Kong/Traefik routing requirements
- Infisical usage requirements
- .env file prohibitions
- Security policies
"""

from typing import Dict, Any, List
import re
from pathlib import Path

from .base import Validator, ValidationResult


class ContextContractValidator(Validator):
    """Validates against Context Contract rules"""

    def __init__(self):
        super().__init__("Context Contract")

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate changes against Context Contract.

        Context should contain:
        - contract: Context Contract data
        - changes: Dict of file changes (path -> content)
        """
        contract = context.get("contract")
        if not contract:
            return self._skip("No Context Contract available")

        changes = context.get("changes", {})
        if not changes:
            return self._pass("No changes to validate")

        violations = []
        suggestions = []

        # Check principles
        principles = contract.get("principles", {})

        # Check 1: .env file creation prohibition
        if principles.get("no_env_files"):
            for file_path in changes.keys():
                if ".env" in Path(file_path).name:
                    violations.append(f"❌ .env file creation prohibited: {file_path}")
                    suggestions.append("Use Infisical for secret management")

        # Check 2: Hardcoded secrets
        if principles.get("use_infisical_only"):
            secret_patterns = [
                r'INFISICAL_TOKEN\s*=\s*[\'"]st\.',  # Infisical token
                r'SUPABASE_SERVICE_ROLE_KEY\s*=\s*[\'"]eyJ',  # Supabase JWT
                r'OPENAI_API_KEY\s*=\s*[\'"]sk-',  # OpenAI key
                r'DATABASE_URL\s*=\s*[\'"]postgres.*password',  # DB password
            ]

            for file_path, content in changes.items():
                for pattern in secret_patterns:
                    if re.search(pattern, content):
                        violations.append(f"❌ Hardcoded secret detected in {file_path}")
                        suggestions.append("Use Infisical or environment variables")
                        break

        # Check 3: Outbound traffic routing
        outbound_proxy = principles.get("outbound_through")
        if outbound_proxy == "kong":
            # Check if Kong routing is mentioned in docker-compose changes
            for file_path, content in changes.items():
                if "docker-compose" in file_path:
                    if "external" in content and "kong" not in content.lower():
                        violations.append(f"❌ External service without Kong routing in {file_path}")
                        suggestions.append("All external services must route through Kong")

        elif outbound_proxy == "traefik":
            # Check if Traefik labels are present
            for file_path, content in changes.items():
                if "docker-compose" in file_path:
                    if "external" in content and "traefik.enable" not in content:
                        violations.append(f"❌ External service without Traefik labels in {file_path}")
                        suggestions.append("All external services must use Traefik labels")

        # Return result
        if violations:
            return self._fail(
                f"Context Contract violations detected ({len(violations)} issues)",
                details={"violations": violations},
                suggestions=suggestions
            )

        return self._pass("All Context Contract rules satisfied")
