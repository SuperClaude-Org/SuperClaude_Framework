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


class TestTokenAllocation:
    """Tests for token allocation functionality"""

    def test_allocate_within_budget(self):
        """Test allocating tokens within budget"""
        manager = TokenBudgetManager(complexity="medium")

        result = manager.allocate(500)

        assert result is True
        assert manager.used == 500

    def test_allocate_exact_budget(self):
        """Test allocating exactly the budget limit"""
        manager = TokenBudgetManager(complexity="simple")

        result = manager.allocate(200)

        assert result is True
        assert manager.used == 200

    def test_allocate_exceeds_budget(self):
        """Test allocating more than budget"""
        manager = TokenBudgetManager(complexity="simple")

        result = manager.allocate(250)

        assert result is False
        assert manager.used == 0  # Should not have allocated

    def test_allocate_multiple_times(self):
        """Test multiple allocations"""
        manager = TokenBudgetManager(complexity="medium")

        assert manager.allocate(300) is True
        assert manager.allocate(300) is True
        assert manager.allocate(300) is True
        assert manager.allocate(200) is False  # Would exceed

        assert manager.used == 900

    def test_use_is_alias_for_allocate(self):
        """Test that use() is an alias for allocate()"""
        manager = TokenBudgetManager(complexity="simple")

        result = manager.use(100)

        assert result is True
        assert manager.used == 100


class TestRemainingTokens:
    """Tests for remaining tokens calculation"""

    def test_remaining_property(self):
        """Test remaining property"""
        manager = TokenBudgetManager(complexity="medium")

        assert manager.remaining == 1000

        manager.allocate(300)
        assert manager.remaining == 700

    def test_remaining_tokens_method(self):
        """Test remaining_tokens method"""
        manager = TokenBudgetManager(complexity="complex")

        assert manager.remaining_tokens() == 2500

        manager.use(1000)
        assert manager.remaining_tokens() == 1500

    def test_remaining_equals_remaining_tokens(self):
        """Test that remaining property equals remaining_tokens()"""
        manager = TokenBudgetManager(complexity="medium")

        manager.allocate(500)

        assert manager.remaining == manager.remaining_tokens()


class TestReset:
    """Tests for reset functionality"""

    def test_reset_clears_used(self):
        """Test reset clears used tokens"""
        manager = TokenBudgetManager(complexity="medium")

        manager.allocate(500)
        assert manager.used == 500

        manager.reset()
        assert manager.used == 0

    def test_reset_restores_remaining(self):
        """Test reset restores full budget"""
        manager = TokenBudgetManager(complexity="simple")

        manager.allocate(150)
        assert manager.remaining == 50

        manager.reset()
        assert manager.remaining == 200


class TestRepr:
    """Tests for string representation"""

    def test_repr_simple(self):
        """Test repr for simple complexity"""
        manager = TokenBudgetManager(complexity="simple")

        repr_str = repr(manager)

        assert "TokenBudgetManager" in repr_str
        assert "simple" in repr_str
        assert "200" in repr_str

    def test_repr_medium(self):
        """Test repr for medium complexity"""
        manager = TokenBudgetManager(complexity="medium")

        repr_str = repr(manager)

        assert "medium" in repr_str
        assert "1000" in repr_str

    def test_repr_with_usage(self):
        """Test repr shows used tokens"""
        manager = TokenBudgetManager(complexity="complex")
        manager.allocate(500)

        repr_str = repr(manager)

        assert "used=500" in repr_str


class TestLimitsConstant:
    """Tests for LIMITS constant"""

    def test_limits_is_dict(self):
        """Test LIMITS is a dictionary"""
        assert isinstance(TokenBudgetManager.LIMITS, dict)

    def test_limits_has_all_complexity_levels(self):
        """Test LIMITS has all complexity levels"""
        assert "simple" in TokenBudgetManager.LIMITS
        assert "medium" in TokenBudgetManager.LIMITS
        assert "complex" in TokenBudgetManager.LIMITS

    def test_limits_values_are_integers(self):
        """Test LIMITS values are integers"""
        for value in TokenBudgetManager.LIMITS.values():
            assert isinstance(value, int)


class TestEdgeCases:
    """Edge case tests"""

    def test_allocate_zero(self):
        """Test allocating zero tokens"""
        manager = TokenBudgetManager(complexity="simple")

        result = manager.allocate(0)

        assert result is True
        assert manager.used == 0

    def test_allocate_negative(self):
        """Test allocating negative tokens"""
        manager = TokenBudgetManager(complexity="simple")

        # Behavior for negative is implementation-defined
        # Just verify no crash
        result = manager.allocate(-100)
        assert isinstance(result, bool)

    def test_multiple_resets(self):
        """Test multiple resets"""
        manager = TokenBudgetManager(complexity="medium")

        manager.allocate(500)
        manager.reset()
        manager.allocate(300)
        manager.reset()
        manager.reset()

        assert manager.used == 0
        assert manager.remaining == 1000
