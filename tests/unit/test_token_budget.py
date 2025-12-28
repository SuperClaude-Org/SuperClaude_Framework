"""
Unit tests for TokenBudgetManager

Tests token budget allocation and management functionality.
"""

import pytest

from superclaude.pm_agent.token_budget import TokenBudgetManager


class TestTokenBudgetManager:
    """Test suite for TokenBudgetManager class"""

    def test_simple_complexity(self):
        """Test token budget for simple tasks (typo fixes)"""
        manager = TokenBudgetManager(complexity="simple")

        assert manager.limit == 200
        assert manager.complexity == "simple"

    def test_medium_complexity(self):
        """Test token budget for medium tasks (bug fixes)"""
        manager = TokenBudgetManager(complexity="medium")

        assert manager.limit == 1000
        assert manager.complexity == "medium"

    def test_complex_complexity(self):
        """Test token budget for complex tasks (features)"""
        manager = TokenBudgetManager(complexity="complex")

        assert manager.limit == 2500
        assert manager.complexity == "complex"

    def test_default_complexity(self):
        """Test default complexity is medium"""
        manager = TokenBudgetManager()

        assert manager.limit == 1000
        assert manager.complexity == "medium"

    def test_invalid_complexity_defaults_to_medium(self):
        """Test that invalid complexity defaults to medium"""
        manager = TokenBudgetManager(complexity="invalid")

        assert manager.limit == 1000
        assert manager.complexity == "medium"

    def test_token_usage_tracking(self):
        """Test token usage tracking if implemented"""
        manager = TokenBudgetManager(complexity="simple")

        # Check if usage tracking is available
        if hasattr(manager, "used"):
            assert manager.used == 0

        if hasattr(manager, "remaining"):
            assert manager.remaining == manager.limit

    def test_budget_allocation_strategy(self):
        """Test token budget allocation strategy"""
        # Simple tasks should have smallest budget
        simple = TokenBudgetManager(complexity="simple")

        # Medium tasks should have moderate budget
        medium = TokenBudgetManager(complexity="medium")

        # Complex tasks should have largest budget
        complex_task = TokenBudgetManager(complexity="complex")

        assert simple.limit < medium.limit < complex_task.limit

    def test_complexity_examples(self):
        """Test that complexity levels match documented examples"""
        # Simple: typo fix (200 tokens)
        simple = TokenBudgetManager(complexity="simple")
        assert simple.limit == 200

        # Medium: bug fix, small feature (1,000 tokens)
        medium = TokenBudgetManager(complexity="medium")
        assert medium.limit == 1000

        # Complex: feature implementation (2,500 tokens)
        complex_task = TokenBudgetManager(complexity="complex")
        assert complex_task.limit == 2500


@pytest.mark.complexity("simple")
def test_complexity_marker_simple(token_budget):
    """
    Test that complexity marker works with pytest plugin fixture

    This test should have a simple (200 token) budget
    """
    assert token_budget.limit == 200
    assert token_budget.complexity == "simple"


@pytest.mark.complexity("medium")
def test_complexity_marker_medium(token_budget):
    """
    Test that complexity marker works with medium budget

    This test should have a medium (1000 token) budget
    """
    assert token_budget.limit == 1000
    assert token_budget.complexity == "medium"


@pytest.mark.complexity("complex")
def test_complexity_marker_complex(token_budget):
    """
    Test that complexity marker works with complex budget

    This test should have a complex (2500 token) budget
    """
    assert token_budget.limit == 2500
    assert token_budget.complexity == "complex"


def test_token_budget_no_marker(token_budget):
    """
    Test that token_budget fixture defaults to medium without marker

    Tests without complexity marker should get medium budget
    """
    assert token_budget.limit == 1000
    assert token_budget.complexity == "medium"
