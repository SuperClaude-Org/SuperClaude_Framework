"""
Token Budget Management

Budget-aware operations with complexity-based allocation.

Budget Levels:
    - Simple (typo fix): 200 tokens
    - Medium (bug fix): 1,000 tokens
    - Complex (feature): 2,500 tokens

Token Efficiency Strategy:
    - Compress trial-and-error history (keep only successful path)
    - Focus on actionable learnings (not full trajectory)
    - Example: "[Summary] 3 failures (details: failures.json) | Success: proper validation"

Expected Reduction:
    - Simple tasks: 80-95% reduction
    - Medium tasks: 60-80% reduction
    - Complex tasks: 40-60% reduction
"""

from typing import Dict, Literal, Optional
from enum import Enum


class ComplexityLevel(str, Enum):
    """Task complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class TokenBudgetManager:
    """
    Token budget management for complexity-aware operations

    Usage:
        # Simple task (typo fix)
        budget = TokenBudgetManager(complexity="simple")
        assert budget.limit == 200

        # Medium task (bug fix)
        budget = TokenBudgetManager(complexity="medium")
        assert budget.limit == 1000

        # Complex task (feature implementation)
        budget = TokenBudgetManager(complexity="complex")
        assert budget.limit == 2500

        # Check budget
        if budget.remaining < 100:
            print("⚠️ Low budget - compress output")
    """

    # Budget allocations by complexity
    BUDGETS = {
        ComplexityLevel.SIMPLE: 200,    # Typo fix, comment update
        ComplexityLevel.MEDIUM: 1000,   # Bug fix, refactoring
        ComplexityLevel.COMPLEX: 2500,  # Feature implementation
    }

    def __init__(
        self,
        complexity: Literal["simple", "medium", "complex"] = "medium",
        custom_limit: Optional[int] = None
    ):
        """
        Initialize token budget manager

        Args:
            complexity: Task complexity level
            custom_limit: Custom token limit (overrides complexity-based)
        """
        self.complexity = ComplexityLevel(complexity)

        if custom_limit is not None:
            self.limit = custom_limit
        else:
            self.limit = self.BUDGETS[self.complexity]

        self.used = 0
        self.operations = []

    def use(self, tokens: int, operation: str = "") -> bool:
        """
        Use tokens for an operation

        Args:
            tokens: Number of tokens to use
            operation: Description of operation

        Returns:
            bool: Whether tokens were successfully allocated
        """
        if self.used + tokens > self.limit:
            return False

        self.used += tokens
        self.operations.append({
            "tokens": tokens,
            "operation": operation,
            "total_used": self.used,
        })

        return True

    @property
    def remaining(self) -> int:
        """Get remaining token budget"""
        return self.limit - self.used

    @property
    def usage_percentage(self) -> float:
        """Get budget usage percentage"""
        return (self.used / self.limit) * 100 if self.limit > 0 else 0.0

    @property
    def is_low(self) -> bool:
        """Check if budget is running low (<20% remaining)"""
        return self.remaining < (self.limit * 0.2)

    @property
    def is_critical(self) -> bool:
        """Check if budget is critical (<10% remaining)"""
        return self.remaining < (self.limit * 0.1)

    def get_status(self) -> Dict[str, any]:
        """
        Get current budget status

        Returns:
            Dict with status information
        """
        return {
            "complexity": self.complexity.value,
            "limit": self.limit,
            "used": self.used,
            "remaining": self.remaining,
            "usage_percentage": round(self.usage_percentage, 1),
            "is_low": self.is_low,
            "is_critical": self.is_critical,
            "operations_count": len(self.operations),
        }

    def get_recommendation(self) -> str:
        """
        Get recommendation based on current budget status

        Returns:
            str: Recommendation message
        """
        if self.is_critical:
            return "🚨 CRITICAL: <10% budget remaining - Use symbols only, compress heavily"
        elif self.is_low:
            return "⚠️ LOW: <20% budget remaining - Compress output, avoid verbose explanations"
        elif self.usage_percentage > 50:
            return "📊 MODERATE: >50% budget used - Start token-efficient communication"
        else:
            return "✅ HEALTHY: Budget sufficient for standard operations"

    def format_usage_report(self) -> str:
        """
        Format budget usage report

        Returns:
            str: Formatted report
        """
        status = self.get_status()

        report = [
            f"🧠 Token Budget Report",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"Complexity: {status['complexity']}",
            f"Limit: {status['limit']} tokens",
            f"Used: {status['used']} tokens ({status['usage_percentage']}%)",
            f"Remaining: {status['remaining']} tokens",
            f"",
            f"Recommendation:",
            f"{self.get_recommendation()}",
        ]

        if self.operations:
            report.append(f"")
            report.append(f"Recent Operations:")
            for op in self.operations[-5:]:  # Last 5 operations
                operation_name = op['operation'] or "unnamed"
                report.append(
                    f"  • {operation_name}: {op['tokens']} tokens "
                    f"(total: {op['total_used']})"
                )

        return "\n".join(report)

    def reset(self) -> None:
        """Reset budget usage (keep limit)"""
        self.used = 0
        self.operations = []

    def set_complexity(self, complexity: Literal["simple", "medium", "complex"]) -> None:
        """
        Update complexity level and reset budget

        Args:
            complexity: New complexity level
        """
        self.complexity = ComplexityLevel(complexity)
        self.limit = self.BUDGETS[self.complexity]
        self.reset()

    @classmethod
    def estimate_complexity(cls, context: Dict[str, any]) -> ComplexityLevel:
        """
        Estimate complexity level from context

        Heuristics:
            - Simple: Single file, <50 lines changed, no new files
            - Medium: Multiple files, <200 lines changed, or refactoring
            - Complex: New features, >200 lines, architectural changes

        Args:
            context: Context dict with task information

        Returns:
            ComplexityLevel: Estimated complexity
        """
        # Check lines changed
        lines_changed = context.get("lines_changed", 0)
        if lines_changed > 200:
            return ComplexityLevel.COMPLEX

        # Check files modified
        files_modified = context.get("files_modified", 0)
        if files_modified > 3:
            return ComplexityLevel.COMPLEX
        elif files_modified > 1:
            return ComplexityLevel.MEDIUM

        # Check task type
        task_type = context.get("task_type", "").lower()
        if any(keyword in task_type for keyword in ["feature", "implement", "add"]):
            return ComplexityLevel.COMPLEX
        elif any(keyword in task_type for keyword in ["fix", "bug", "refactor"]):
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.SIMPLE

    def __str__(self) -> str:
        """String representation"""
        return (
            f"TokenBudget({self.complexity.value}: "
            f"{self.used}/{self.limit} tokens, "
            f"{self.usage_percentage:.1f}% used)"
        )

    def __repr__(self) -> str:
        """Developer representation"""
        return (
            f"TokenBudgetManager(complexity={self.complexity.value!r}, "
            f"limit={self.limit}, used={self.used})"
        )
