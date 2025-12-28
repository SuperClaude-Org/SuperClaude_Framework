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

from pathlib import Path
from typing import Any, Dict


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
        - No existing similar functions/modules (Glob/Grep)
        - No helper functions that solve the same problem
        - No libraries that provide this functionality

        Returns True if no duplicates found (investigation complete)
        """
        # This is a placeholder - actual implementation should:
        # 1. Search codebase with Glob/Grep for similar patterns
        # 2. Check project dependencies for existing solutions
        # 3. Verify no helper modules provide this functionality
        duplicate_check = context.get("duplicate_check_complete", False)
        return duplicate_check

    def _architecture_compliant(self, context: Dict[str, Any]) -> bool:
        """
        Check architecture compliance

        Verify solution uses existing tech stack:
        - Supabase project → Use Supabase APIs (not custom API)
        - Next.js project → Use Next.js patterns (not custom routing)
        - Turborepo → Use workspace patterns (not manual scripts)

        Returns True if solution aligns with project architecture
        """
        # This is a placeholder - actual implementation should:
        # 1. Read CLAUDE.md for project tech stack
        # 2. Verify solution uses existing infrastructure
        # 3. Check not reinventing provided functionality
        architecture_check = context.get("architecture_check_complete", False)
        return architecture_check

    def _has_oss_reference(self, context: Dict[str, Any]) -> bool:
        """
        Check if working OSS implementations referenced

        Search for:
        - Similar open-source solutions
        - Reference implementations in popular projects
        - Community best practices

        Returns True if OSS reference found and analyzed
        """
        # This is a placeholder - actual implementation should:
        # 1. Search GitHub for similar implementations
        # 2. Read popular OSS projects solving same problem
        # 3. Verify approach matches community patterns
        oss_check = context.get("oss_reference_complete", False)
        return oss_check

    def _root_cause_identified(self, context: Dict[str, Any]) -> bool:
        """
        Check if root cause is identified with high certainty

        Verify:
        - Problem source pinpointed (not guessing)
        - Solution addresses root cause (not symptoms)
        - Fix verified against official docs/OSS patterns

        Returns True if root cause clearly identified
        """
        # This is a placeholder - actual implementation should:
        # 1. Verify problem analysis complete
        # 2. Check solution addresses root cause
        # 3. Confirm fix aligns with best practices
        root_cause_check = context.get("root_cause_identified", False)
        return root_cause_check

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
