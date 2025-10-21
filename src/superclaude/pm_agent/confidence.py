"""
Pre-execution Confidence Check

Prevents wrong-direction execution by assessing confidence BEFORE starting.

Token Budget: 100-200 tokens
ROI: 25-250x token savings when stopping wrong direction

Confidence Levels:
    - High (90-100%): Official docs verified, patterns identified, path clear
    - Medium (70-89%): Multiple approaches possible, trade-offs require consideration
    - Low (<70%): Requirements unclear, no patterns, domain knowledge insufficient
"""

from typing import Dict, Any, Optional
from pathlib import Path


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

        Checks:
        1. Official documentation verified? (40%)
        2. Existing patterns identified? (30%)
        3. Implementation path clear? (30%)

        Args:
            context: Context dict with test/implementation details

        Returns:
            float: Confidence score (0.0 = no confidence, 1.0 = absolute)
        """
        score = 0.0
        checks = []

        # Check 1: Documentation verified (40%)
        if self._has_official_docs(context):
            score += 0.4
            checks.append("✅ Official documentation")
        else:
            checks.append("❌ Missing documentation")

        # Check 2: Existing patterns (30%)
        if self._has_existing_patterns(context):
            score += 0.3
            checks.append("✅ Existing patterns found")
        else:
            checks.append("❌ No existing patterns")

        # Check 3: Clear implementation path (30%)
        if self._has_clear_path(context):
            score += 0.3
            checks.append("✅ Implementation path clear")
        else:
            checks.append("❌ Implementation unclear")

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
            "unit", "integration", "hallucination",
            "performance", "confidence_check", "self_check"
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
            return "✅ High confidence - Proceed immediately"
        elif confidence >= 0.7:
            return "⚠️ Medium confidence - Present options to user"
        else:
            return "❌ Low confidence - STOP and request clarification"
