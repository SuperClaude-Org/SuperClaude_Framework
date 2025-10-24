"""
Token Budget Manager

Manages token allocation based on task complexity.

Token Budget by Complexity:
    - simple: 200 tokens (typo fix, trivial change)
    - medium: 1,000 tokens (bug fix, small feature)
    - complex: 2,500 tokens (large feature, refactoring)
"""

from typing import Literal

ComplexityLevel = Literal["simple", "medium", "complex"]


class TokenBudgetManager:
    """
    Token budget management for tasks

    Usage:
        manager = TokenBudgetManager(complexity="medium")
        print(f"Budget: {manager.limit} tokens")
    """

    # Token limits by complexity
    LIMITS = {
        "simple": 200,
        "medium": 1000,
        "complex": 2500,
    }

    def __init__(self, complexity: ComplexityLevel = "medium"):
        """
        Initialize token budget manager

        Args:
            complexity: Task complexity level (simple, medium, complex)
        """
        self.complexity = complexity
        self.limit = self.LIMITS.get(complexity, 1000)
        self.used = 0

    def allocate(self, amount: int) -> bool:
        """
        Allocate tokens from budget

        Args:
            amount: Number of tokens to allocate

        Returns:
            bool: True if allocation successful, False if budget exceeded
        """
        if self.used + amount <= self.limit:
            self.used += amount
            return True
        return False

    def use(self, amount: int) -> bool:
        """
        Consume tokens from the budget.

        Convenience wrapper around allocate() to match historical CLI usage.
        """
        return self.allocate(amount)

    @property
    def remaining(self) -> int:
        """Number of tokens still available."""
        return self.limit - self.used

    def remaining_tokens(self) -> int:
        """Backward compatible helper that mirrors the remaining property."""
        return self.remaining

    def reset(self) -> None:
        """Reset used tokens counter"""
        self.used = 0

    def __repr__(self) -> str:
        return f"TokenBudgetManager(complexity={self.complexity!r}, limit={self.limit}, used={self.used})"
