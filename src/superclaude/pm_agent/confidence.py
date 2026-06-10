"""
Pre-implementation Confidence Check

Prevents wrong-direction execution by assessing confidence BEFORE starting.

Token Budget: 100-200 tokens
ROI: 25-250x token savings when stopping wrong direction

Confidence Levels:
    - High (≥90%): Root cause identified, solution verified, no duplication, architecture-compliant
    - Medium (70-89%): Multiple approaches possible, trade-offs require consideration
    - Low (<70%): Investigation incomplete, unclear root cause, missing official docs

Required Checks:
    1. No duplicate implementations (check existing code first)
    2. Architecture compliance (use existing tech stack, e.g., Supabase not custom API)
    3. Official documentation verified
    4. Working OSS implementations referenced
    5. Root cause identified with high certainty

Each check supports an explicit context flag override (e.g. ``duplicate_check_complete``)
for testing or pre-checked scenarios; absent the flag, the check inspects the real
project on disk.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfidenceChecker:
    """
    Pre-implementation confidence assessment

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
        """
        Check if official documentation exists

        Looks for:
        - README.md in project
        - CLAUDE.md with relevant patterns
        - docs/ directory with related content
        """
        # Check context flag first (for testing)
        if "official_docs_verified" in context:
            return context.get("official_docs_verified", False)

        # Check for test file path
        test_file = context.get("test_file")
        if not test_file:
            return False

        project_root = Path(test_file).parent
        while project_root.parent != project_root:
            # Check for documentation files
            if (project_root / "README.md").exists():
                return True
            if (project_root / "CLAUDE.md").exists():
                return True
            if (project_root / "docs").exists():
                return True
            project_root = project_root.parent

        return False

    def _no_duplicates(self, context: Dict[str, Any]) -> bool:
        """
        Check for duplicate implementations

        Before implementing, verify:
        - No existing similar functions/modules
        - No helper functions that solve the same problem
        - No libraries that provide this functionality

        Searches the project for files (any of *.py/*.ts/*.js) whose name matches
        the feature, or that define a function/class/const of the same name. Any
        match is recorded in ``context["potential_duplicates"]``.

        Returns True if no duplicates found (investigation complete)
        """
        # Allow explicit override via context flag (for testing or pre-checked scenarios)
        if "duplicate_check_complete" in context:
            return context.get("duplicate_check_complete", False)

        feature_name = (
            context.get("feature_name")
            or context.get("target_name")
            or context.get("test_name", "")
        )
        if not feature_name:
            return False

        project_root = self._find_project_root(context)
        if not project_root:
            return False  # Can't verify without project root

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
        """
        Check architecture compliance

        Reads the project tech stack from CLAUDE.md / package files and verifies the
        proposed approach does not reinvent existing infrastructure (e.g. introducing a
        custom API in a Supabase project). Warnings are stored in
        ``context["architecture_warnings"]``.

        Returns True if solution aligns with project architecture
        """
        # Allow explicit override via context flag
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
            # Tech stack is known and nothing risky proposed -> compliant
            return True

        anti_patterns = self._check_architecture_anti_patterns(
            tech_stack, proposed_tech
        )
        if anti_patterns:
            context["architecture_warnings"] = anti_patterns
            return False

        return True

    def _has_oss_reference(self, context: Dict[str, Any]) -> bool:
        """
        Check if working OSS implementations referenced

        Validates that external references or documentation have been
        consulted before implementation.

        Returns True if OSS reference found and analyzed
        """
        # Allow explicit override via context flag
        if "oss_reference_complete" in context:
            return context.get("oss_reference_complete", False)

        # Explicit references gathered during investigation
        if context.get("oss_references"):
            return True
        if context.get("documentation_urls"):
            return True
        if context.get("references"):
            return True

        research_notes = context.get("research_notes", "")
        if research_notes and len(research_notes) > 50:
            return True

        # Check if docs/research directory has relevant analysis
        project_root = self._find_project_root(context)
        if project_root and (project_root / "docs" / "research").exists():
            research_dir = project_root / "docs" / "research"
            if list(research_dir.glob("*.md")):
                return True

        context["oss_recommendation"] = (
            "Search for OSS implementations using WebSearch or Context7 MCP"
        )
        return False

    def _root_cause_identified(self, context: Dict[str, Any]) -> bool:
        """
        Check if root cause is identified with high certainty

        Verify:
        - Problem source pinpointed (not guessing)
        - Solution addresses root cause (not symptoms)
        - Fix verified against official docs/OSS patterns

        Returns True if root cause clearly identified
        """
        # Allow explicit override via context flag
        if "root_cause_identified" in context:
            return context.get("root_cause_identified", False)

        # Check for root cause analysis in context
        root_cause = context.get("root_cause", "")
        if not root_cause:
            context["root_cause_warning"] = "Root cause not documented in context"
            return False

        # Validate root cause is specific (not hedged with uncertainty language)
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
            r"\bunclear\b",
            r"\bunknown\b",
        ]
        root_cause_lower = root_cause.lower()
        for pattern in uncertainty_patterns:
            if re.search(pattern, root_cause_lower):
                context["root_cause_warning"] = (
                    f"Root cause contains uncertainty language: '{pattern}'"
                )
                return False

        # A credible root cause comes with a concrete proposed solution
        solution = context.get("proposed_solution", "")
        if not solution:
            context["root_cause_warning"] = "No proposed solution documented"
            return False

        if len(solution) < 20:
            context["root_cause_warning"] = "Proposed solution too brief"
            return False

        return True

    def _find_project_root(self, context: Dict[str, Any]) -> Optional[Path]:
        """Find the project root directory from context"""
        # Check explicit project_root in context
        if "project_root" in context:
            return Path(context["project_root"])

        # Traverse up from test_file to find project root
        test_file = context.get("test_file")
        if not test_file:
            return None

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
        """
        Search the codebase for files related to ``search_term``.

        A file matches when its name resembles the search term, or when it defines a
        ``def``/``class``/``function`` with that exact name. Returns project-relative
        paths (capped at 10) and skips ``exclude_dirs``.
        """
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
        """Read tech stack from CLAUDE.md and project files."""
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
        """Check the proposed approach against the detected tech stack."""
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

    def _has_existing_patterns(self, context: Dict[str, Any]) -> bool:
        """
        Check if existing patterns can be followed

        Looks for:
        - Similar test files
        - Common naming conventions
        - Established directory structure
        """
        test_file = context.get("test_file")
        if not test_file:
            return False

        test_path = Path(test_file)
        test_dir = test_path.parent

        # Check for other test files in same directory
        if test_dir.exists():
            test_files = list(test_dir.glob("test_*.py"))
            return len(test_files) > 1

        return False

    def _has_clear_path(self, context: Dict[str, Any]) -> bool:
        """
        Check if implementation path is clear

        Considers:
        - Test name suggests clear purpose
        - Markers indicate test type
        - Context has sufficient information
        """
        # Check test name clarity
        test_name = context.get("test_name", "")
        if not test_name or test_name == "test_example":
            return False

        # Check for markers indicating test type
        markers = context.get("markers", [])
        known_markers = {
            "unit",
            "integration",
            "hallucination",
            "performance",
            "confidence_check",
            "self_check",
        }

        has_markers = bool(set(markers) & known_markers)

        return has_markers or len(test_name) > 10

    def get_recommendation(self, confidence: float) -> str:
        """
        Get recommended action based on confidence level

        Args:
            confidence: Confidence score (0.0 - 1.0)

        Returns:
            str: Recommended action
        """
        if confidence >= 0.9:
            return "✅ High confidence (≥90%) - Proceed with implementation"
        elif confidence >= 0.7:
            return "⚠️ Medium confidence (70-89%) - Continue investigation, DO NOT implement yet"
        else:
            return "❌ Low confidence (<70%) - STOP and continue investigation loop"
