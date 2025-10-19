"""Security Roughcheck Validator

Detects common security anti-patterns:
- Hardcoded secrets (API keys, tokens, passwords)
- .env file creation in commits
- Exposed credentials in code
- Unsafe practices
"""

from typing import Dict, Any, List
import re
from pathlib import Path

from .base import Validator, ValidationResult


class SecurityRoughcheckValidator(Validator):
    """Validates against common security issues"""

    # Secret detection patterns
    SECRET_PATTERNS = [
        (r'sk_live_[a-zA-Z0-9]{24,}', 'Stripe live secret key'),
        (r'pk_live_[a-zA-Z0-9]{24,}', 'Stripe live publishable key'),
        (r'sk_test_[a-zA-Z0-9]{24,}', 'Stripe test secret key'),
        (r'SUPABASE_SERVICE_ROLE_KEY\s*=\s*[\'"]eyJ', 'Supabase service role key'),
        (r'SUPABASE_ANON_KEY\s*=\s*[\'"]eyJ', 'Supabase anon key'),
        (r'OPENAI_API_KEY\s*=\s*[\'"]sk-', 'OpenAI API key'),
        (r'TWILIO_AUTH_TOKEN\s*=\s*[\'"][a-f0-9]{32}', 'Twilio auth token'),
        (r'INFISICAL_TOKEN\s*=\s*[\'"]st\.', 'Infisical token'),
        (r'DATABASE_URL\s*=\s*[\'"]postgres.*password', 'Database password in URL'),
        (r'AWS_SECRET_ACCESS_KEY\s*=\s*[\'"][\w/+=]{40}', 'AWS secret access key'),
        (r'GITHUB_TOKEN\s*=\s*[\'"]gh[ps]_[a-zA-Z0-9]{36}', 'GitHub token'),
    ]

    # Unsafe patterns
    UNSAFE_PATTERNS = [
        (r'eval\s*\(', 'Use of eval() function'),
        (r'exec\s*\(', 'Use of exec() function'),
        (r'__import__\s*\(', 'Dynamic import with __import__'),
        (r'shell=True', 'Shell command execution'),
        (r'pickle\.loads?\s*\(', 'Unsafe pickle deserialization'),
    ]

    def __init__(self):
        super().__init__("Security Roughcheck")

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate security.

        Context should contain:
        - changes: File changes
        """
        changes = context.get("changes", {})
        if not changes:
            return self._pass("No changes to validate")

        critical_issues = []
        warnings = []

        for file_path, content in changes.items():
            # Check 1: .env file creation
            if ".env" in Path(file_path).name:
                critical_issues.append(f"❌ CRITICAL: .env file detected: {file_path}")

            # Check 2: Hardcoded secrets
            for pattern, description in self.SECRET_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    critical_issues.append(
                        f"❌ CRITICAL: {description} detected in {file_path}"
                    )

            # Check 3: Unsafe patterns
            for pattern, description in self.UNSAFE_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    warnings.append(f"⚠️ {description} in {file_path}")

            # Check 4: Exposed API endpoints without auth
            if self._looks_like_api_route(file_path):
                if not self._has_auth_check(content):
                    warnings.append(
                        f"⚠️ Possible unauthenticated API endpoint in {file_path}"
                    )

        # Generate suggestions
        suggestions = []
        if critical_issues:
            suggestions.extend([
                "Remove hardcoded secrets immediately",
                "Use environment variables or secret management (Infisical)",
                "Never commit .env files - add to .gitignore"
            ])

        if warnings:
            suggestions.extend([
                "Review security warnings carefully",
                "Consider safer alternatives where possible"
            ])

        # Return result
        if critical_issues:
            return self._fail(
                f"CRITICAL security issues detected ({len(critical_issues)} issues)",
                details={
                    "critical": critical_issues,
                    "warnings": warnings
                },
                suggestions=suggestions
            )

        if warnings:
            return self._warning(
                f"Security warnings detected ({len(warnings)} warnings)",
                details={"warnings": warnings},
                suggestions=suggestions
            )

        return self._pass("No security issues detected")

    def _looks_like_api_route(self, file_path: str) -> bool:
        """Check if file looks like an API route"""
        api_indicators = [
            "/api/",
            "/routes/",
            "/endpoints/",
            ".route.",
            ".api.",
        ]
        return any(indicator in file_path.lower() for indicator in api_indicators)

    def _has_auth_check(self, content: str) -> bool:
        """Check if content has authentication checks"""
        auth_patterns = [
            r'@auth',  # Decorator
            r'authenticate',
            r'authorize',
            r'requireAuth',
            r'verifyToken',
            r'checkAuth',
            r'isAuthenticated',
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in auth_patterns)
