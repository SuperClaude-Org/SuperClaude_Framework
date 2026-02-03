"""
Pre-implementation Confidence Check

ARCHITECTURE NOTE:
    superclaude = client only. Core logic lives in airis-agent.
    This module provides a thin wrapper that delegates to airis-agent
    when available, with local fallback for testing/offline use.

Token Budget: 100-200 tokens
ROI: 25-250x token savings when stopping wrong direction

Confidence Levels:
    - High (>=90%): Root cause identified, solution verified, no duplication, architecture-compliant
    - Medium (70-89%): Multiple approaches possible, trade-offs require consideration
    - Low (<70%): Investigation incomplete, unclear root cause, missing official docs
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to import airis-agent integration (preferred)
_airis_available = False
_airis_plugin = None

try:
    from airis_agent.integrations.superclaude import (  # noqa: F401
        ConfidenceResult as AirisConfidenceResult,
    )
    from airis_agent.integrations.superclaude import (  # noqa: F401
        get_plugin,
    )

    _airis_available = True
except ImportError:
    pass


class ConfidenceChecker:
    """
    Pre-implementation confidence assessment

    Delegates to airis-agent when available, falls back to local implementation.

    Usage:
        checker = ConfidenceChecker()
        confidence = checker.assess(context)

        if confidence >= 0.9:
            # High confidence - proceed immediately
        elif confidence >= 0.7:
            # Medium confidence - present options to user
        else:
            # Low confidence - STOP and request clarification
    """

    def __init__(self, use_airis: bool = True):
        """
        Initialize ConfidenceChecker.

        Args:
            use_airis: Whether to use airis-agent if available (default: True)
        """
        self._use_airis = use_airis and _airis_available
        self._local_checker = _LocalConfidenceChecker()

    def assess(self, context: Dict[str, Any]) -> float:
        """
        Assess confidence level (0.0 - 1.0)

        Investigation Phase Checks:
        1. No duplicate implementations? (25%)
        2. Architecture compliance? (25%)
        3. Official documentation verified? (20%)
        4. Working OSS implementations referenced? (15%)
        5. Root cause identified? (15%)

        Args:
            context: Context dict with task details

        Returns:
            float: Confidence score (0.0 = no confidence, 1.0 = absolute certainty)
        """
        # Use local implementation (airis-agent async API not compatible with sync assess)
        return self._local_checker.assess(context)

    def get_recommendation(self, confidence: float) -> str:
        """
        Get recommended action based on confidence level

        Args:
            confidence: Confidence score (0.0 - 1.0)

        Returns:
            str: Recommended action
        """
        return self._local_checker.get_recommendation(confidence)

    # Expose internal methods for testing
    def _no_duplicates(self, context: Dict[str, Any]) -> bool:
        return self._local_checker._no_duplicates(context)

    def _architecture_compliant(self, context: Dict[str, Any]) -> bool:
        return self._local_checker._architecture_compliant(context)

    def _has_official_docs(self, context: Dict[str, Any]) -> bool:
        return self._local_checker._has_official_docs(context)

    def _has_oss_reference(self, context: Dict[str, Any]) -> bool:
        return self._local_checker._has_oss_reference(context)

    def _root_cause_identified(self, context: Dict[str, Any]) -> bool:
        return self._local_checker._root_cause_identified(context)

    def _find_project_root(self, context: Dict[str, Any]) -> Optional[Path]:
        return self._local_checker._find_project_root(context)

    def _search_codebase(
        self,
        root: Path,
        search_term: str,
        patterns: List[str],
        exclude_dirs: List[str],
    ) -> List[str]:
        return self._local_checker._search_codebase(
            root, search_term, patterns, exclude_dirs
        )

    def _read_tech_stack(self, project_root: Path) -> Dict[str, Any]:
        return self._local_checker._read_tech_stack(project_root)

    def _check_architecture_anti_patterns(
        self, tech_stack: Dict[str, Any], proposed_tech: str
    ) -> List[str]:
        return self._local_checker._check_architecture_anti_patterns(
            tech_stack, proposed_tech
        )


class _LocalConfidenceChecker:
    """
    Local fallback implementation of confidence checking.

    Used when airis-agent is not available or for testing.
    """

    def assess(self, context: Dict[str, Any]) -> float:
        """
        Assess confidence level (0.0 - 1.0)

        Investigation Phase Checks:
        1. No duplicate implementations? (25%)
        2. Architecture compliance? (25%)
        3. Official documentation verified? (20%)
        4. Working OSS implementations referenced? (15%)
        5. Root cause identified? (15%)

        Args:
            context: Context dict with task details

        Returns:
            float: Confidence score (0.0 = no confidence, 1.0 = absolute certainty)
        """
        score = 0.0
        checks = []

        # Check 1: No duplicate implementations (25%)
        if self._no_duplicates(context):
            score += 0.25
            checks.append("✅ No duplicate implementations found")
        else:
            checks.append("❌ Check for existing implementations first")

        # Check 2: Architecture compliance (25%)
        if self._architecture_compliant(context):
            score += 0.25
            checks.append("✅ Uses existing tech stack (e.g., Supabase)")
        else:
            checks.append("❌ Verify architecture compliance (avoid reinventing)")

        # Check 3: Official documentation verified (20%)
        if self._has_official_docs(context):
            score += 0.2
            checks.append("✅ Official documentation verified")
        else:
            checks.append("❌ Read official docs first")

        # Check 4: Working OSS implementations referenced (15%)
        if self._has_oss_reference(context):
            score += 0.15
            checks.append("✅ Working OSS implementation found")
        else:
            checks.append("❌ Search for OSS implementations")

        # Check 5: Root cause identified (15%)
        if self._root_cause_identified(context):
            score += 0.15
            checks.append("✅ Root cause identified")
        else:
            checks.append("❌ Continue investigation to identify root cause")

        # Store check results for reporting
        context["confidence_checks"] = checks

        return score

    def _has_official_docs(self, context: Dict[str, Any]) -> bool:
        """Check if official documentation exists."""
        if "official_docs_verified" in context:
            return context.get("official_docs_verified", False)

        test_file = context.get("test_file")
        if not test_file:
            return False

        project_root = Path(test_file).parent
        while project_root.parent != project_root:
            if (project_root / "README.md").exists():
                return True
            if (project_root / "CLAUDE.md").exists():
                return True
            if (project_root / "docs").exists():
                return True
            project_root = project_root.parent

        return False

    def _no_duplicates(self, context: Dict[str, Any]) -> bool:
        """Check for duplicate implementations."""
        if "duplicate_check_complete" in context:
            return context.get("duplicate_check_complete", False)

        feature_name = context.get("feature_name") or context.get("test_name", "")
        if not feature_name:
            return False

        project_root = self._find_project_root(context)
        if not project_root:
            return False

        similar_files = self._search_codebase(
            project_root,
            feature_name,
            patterns=["**/*.py", "**/*.ts", "**/*.js"],
            exclude_dirs=["node_modules", ".venv", "venv", "__pycache__", ".git"],
        )

        if similar_files:
            context["potential_duplicates"] = similar_files[:5]
            return False

        return True

    def _architecture_compliant(self, context: Dict[str, Any]) -> bool:
        """Check architecture compliance."""
        if "architecture_check_complete" in context:
            return context.get("architecture_check_complete", False)

        project_root = self._find_project_root(context)
        if not project_root:
            return False

        tech_stack = self._read_tech_stack(project_root)
        if not tech_stack:
            return False

        context["detected_tech_stack"] = tech_stack

        proposed_tech = context.get("proposed_technology", "")
        if not proposed_tech:
            return True

        anti_patterns = self._check_architecture_anti_patterns(
            tech_stack, proposed_tech
        )
        if anti_patterns:
            context["architecture_warnings"] = anti_patterns
            return False

        return True

    def _has_oss_reference(self, context: Dict[str, Any]) -> bool:
        """Check if working OSS implementations referenced."""
        if "oss_reference_complete" in context:
            return context.get("oss_reference_complete", False)

        oss_refs = context.get("oss_references", [])
        if oss_refs:
            return True

        doc_urls = context.get("documentation_urls", [])
        if doc_urls:
            return True

        research_notes = context.get("research_notes", "")
        if research_notes and len(research_notes) > 50:
            return True

        context["oss_recommendation"] = (
            "Search for OSS implementations using WebSearch or Context7 MCP"
        )
        return False

    def _root_cause_identified(self, context: Dict[str, Any]) -> bool:
        """Check if root cause is identified with high certainty."""
        if "root_cause_identified" in context:
            return context.get("root_cause_identified", False)

        root_cause = context.get("root_cause", "")
        if not root_cause:
            context["root_cause_warning"] = "Root cause not documented in context"
            return False

        uncertainty_patterns = [
            r"\bprobably\b",
            r"\bmaybe\b",
            r"\bmight\b",
            r"\bcould be\b",
            r"\bpossibly\b",
            r"\bnot sure\b",
            r"\bguess\b",
            r"\bthink\b",
            r"\bassume\b",
        ]

        root_cause_lower = root_cause.lower()
        for pattern in uncertainty_patterns:
            if re.search(pattern, root_cause_lower):
                context["root_cause_warning"] = (
                    f"Root cause contains uncertainty language: '{pattern}'"
                )
                return False

        solution = context.get("proposed_solution", "")
        if not solution:
            context["root_cause_warning"] = "No proposed solution documented"
            return False

        if len(solution) < 20:
            context["root_cause_warning"] = "Proposed solution too brief"
            return False

        return True

    def get_recommendation(self, confidence: float) -> str:
        """Get recommended action based on confidence level."""
        if confidence >= 0.9:
            return "✅ High confidence (>=90%) - Proceed with implementation"
        elif confidence >= 0.7:
            return "⚠️ Medium confidence (70-89%) - Continue investigation, DO NOT implement yet"
        else:
            return "❌ Low confidence (<70%) - STOP and continue investigation loop"

    def _find_project_root(self, context: Dict[str, Any]) -> Optional[Path]:
        """Find the project root directory from context."""
        if "project_root" in context:
            return Path(context["project_root"])

        test_file = context.get("test_file")
        if test_file:
            path = Path(test_file)
            current = path.parent if path.is_file() else path
            while current.parent != current:
                if (current / "pyproject.toml").exists():
                    return current
                if (current / "CLAUDE.md").exists():
                    return current
                if (current / ".git").exists():
                    return current
                if (current / "package.json").exists():
                    return current
                current = current.parent

        return None

    def _search_codebase(
        self,
        root: Path,
        search_term: str,
        patterns: List[str],
        exclude_dirs: List[str],
    ) -> List[str]:
        """Search codebase for files matching search term."""
        results = []
        search_lower = search_term.lower().replace("_", "").replace("-", "")

        for pattern in patterns:
            for file_path in root.glob(pattern):
                if any(excluded in str(file_path) for excluded in exclude_dirs):
                    continue

                filename = file_path.stem.lower().replace("_", "").replace("-", "")
                if search_lower in filename or filename in search_lower:
                    results.append(str(file_path.relative_to(root)))
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if len(content) < 100000:
                        if re.search(
                            rf"\b(def|class|function)\s+{re.escape(search_term)}\b",
                            content,
                            re.IGNORECASE,
                        ):
                            results.append(str(file_path.relative_to(root)))
                except (OSError, PermissionError):
                    pass

        return results[:10]

    def _read_tech_stack(self, project_root: Path) -> Dict[str, Any]:
        """Read tech stack from CLAUDE.md or project files."""
        tech_stack: Dict[str, Any] = {}

        claude_md = project_root / "CLAUDE.md"
        if claude_md.exists():
            try:
                content = claude_md.read_text(encoding="utf-8")
                tech_stack["has_claude_md"] = True

                tech_patterns = {
                    "supabase": r"\bsupabase\b",
                    "nextjs": r"\bnext\.?js\b",
                    "react": r"\breact\b",
                    "python": r"\bpython\b",
                    "typescript": r"\btypescript\b",
                    "turborepo": r"\bturborepo\b",
                    "uv": r"\buv\b",
                    "pytest": r"\bpytest\b",
                }

                for tech, pattern in tech_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        tech_stack[tech] = True
            except (OSError, PermissionError):
                pass

        if (project_root / "pyproject.toml").exists():
            tech_stack["python_project"] = True
        if (project_root / "package.json").exists():
            tech_stack["node_project"] = True
        if (project_root / "turbo.json").exists():
            tech_stack["turborepo"] = True

        return tech_stack

    def _check_architecture_anti_patterns(
        self, tech_stack: Dict[str, Any], proposed_tech: str
    ) -> List[str]:
        """Check for architecture anti-patterns."""
        warnings = []
        proposed_lower = proposed_tech.lower()

        if tech_stack.get("supabase"):
            if "custom api" in proposed_lower or "express" in proposed_lower:
                warnings.append(
                    "Supabase project detected - consider using Supabase APIs "
                    "instead of custom API"
                )
            if "custom auth" in proposed_lower:
                warnings.append(
                    "Supabase project detected - consider using Supabase Auth "
                    "instead of custom authentication"
                )

        if tech_stack.get("nextjs"):
            if "custom routing" in proposed_lower:
                warnings.append(
                    "Next.js project detected - use Next.js App Router "
                    "instead of custom routing"
                )

        if tech_stack.get("uv"):
            if "pip install" in proposed_lower:
                warnings.append(
                    "UV project detected - use 'uv pip install' instead of 'pip install'"
                )

        return warnings
