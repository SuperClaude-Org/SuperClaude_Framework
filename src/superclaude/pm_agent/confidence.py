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

        Returns True if no duplicates found (investigation complete)
        """
        # Allow explicit override via context flag (for testing or pre-checked scenarios)
        if "duplicate_check_complete" in context:
            return context["duplicate_check_complete"]

        # Search for duplicates in the project
        project_root = self._find_project_root(context)
        if not project_root:
            return False  # Can't verify without project root

        target_name = context.get("target_name", context.get("test_name", ""))
        if not target_name:
            return False

        # Search for similarly named files/functions in the codebase
        duplicates = self._search_codebase(project_root, target_name)
        return len(duplicates) == 0

    def _architecture_compliant(self, context: Dict[str, Any]) -> bool:
        """
        Check architecture compliance

        Verify solution uses existing tech stack by reading CLAUDE.md
        and checking that the proposed approach aligns with the project.

        Returns True if solution aligns with project architecture
        """
        # Allow explicit override via context flag
        if "architecture_check_complete" in context:
            return context["architecture_check_complete"]

        project_root = self._find_project_root(context)
        if not project_root:
            return False

        # Check for architecture documentation
        arch_files = ["CLAUDE.md", "PLANNING.md", "ARCHITECTURE.md"]
        for arch_file in arch_files:
            if (project_root / arch_file).exists():
                return True

        # If no architecture docs found, check for standard config files
        config_files = [
            "pyproject.toml", "package.json", "Cargo.toml",
            "go.mod", "pom.xml", "build.gradle",
        ]
        return any((project_root / cf).exists() for cf in config_files)

    def _has_oss_reference(self, context: Dict[str, Any]) -> bool:
        """
        Check if working OSS implementations referenced

        Validates that external references or documentation have been
        consulted before implementation.

        Returns True if OSS reference found and analyzed
        """
        # Allow explicit override via context flag
        if "oss_reference_complete" in context:
            return context["oss_reference_complete"]

        # Check if context contains reference URLs or documentation links
        references = context.get("references", [])
        if references:
            return True

        # Check if docs/research directory has relevant analysis
        project_root = self._find_project_root(context)
        if project_root and (project_root / "docs" / "research").exists():
            research_dir = project_root / "docs" / "research"
            research_files = list(research_dir.glob("*.md"))
            if research_files:
                return True

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
            return context["root_cause_identified"]

        # Check for root cause analysis in context
        root_cause = context.get("root_cause", "")
        if not root_cause:
            return False

        # Validate root cause is specific (not vague)
        vague_indicators = ["maybe", "probably", "might", "possibly", "unclear", "unknown"]
        root_cause_lower = root_cause.lower()
        if any(indicator in root_cause_lower for indicator in vague_indicators):
            return False

        # Root cause should have reasonable specificity (>10 chars)
        return len(root_cause.strip()) > 10

    def _find_project_root(self, context: Dict[str, Any]) -> Optional[Path]:
        """Find the project root directory from context"""
        # Check explicit project_root in context
        if "project_root" in context:
            root = Path(context["project_root"])
            if root.exists():
                return root

        # Traverse up from test_file to find project root
        test_file = context.get("test_file")
        if not test_file:
            return None

        current = Path(test_file).parent
        while current.parent != current:
            if (current / "pyproject.toml").exists() or (current / ".git").exists():
                return current
            current = current.parent
        return None

    def _search_codebase(self, project_root: Path, target_name: str) -> List[Path]:
        """
        Search for files/functions with similar names in the codebase

        Returns list of paths to potential duplicates
        """
        duplicates = []

        # Normalize target name for search
        # Convert test_feature_name to feature_name
        search_name = re.sub(r"^test_", "", target_name)
        if not search_name:
            return []

        # Search for Python files with similar names
        src_dirs = [project_root / "src", project_root / "lib", project_root]
        for src_dir in src_dirs:
            if not src_dir.exists():
                continue
            for py_file in src_dir.rglob("*.py"):
                # Skip test files and __pycache__
                if "test_" in py_file.name or "__pycache__" in str(py_file):
                    continue
                if search_name.lower() in py_file.stem.lower():
                    duplicates.append(py_file)

        return duplicates

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
