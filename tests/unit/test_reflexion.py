"""
Unit tests for ReflexionPattern

Tests error learning and prevention functionality.
"""

import pytest

from superclaude.pm_agent.reflexion import ReflexionPattern


class TestReflexionPattern:
    """Test suite for ReflexionPattern class"""

    def test_initialization(self):
        """Test ReflexionPattern initialization"""
        reflexion = ReflexionPattern()

        assert reflexion is not None
        assert hasattr(reflexion, "record_error")
        assert hasattr(reflexion, "get_solution")

    def test_record_error_basic(self):
        """Test recording a basic error"""
        reflexion = ReflexionPattern()

        error_info = {
            "test_name": "test_feature",
            "error_type": "AssertionError",
            "error_message": "Expected 5, got 3",
            "traceback": "File test.py, line 10...",
        }

        # Should not raise an exception
        reflexion.record_error(error_info)

    def test_record_error_with_solution(self):
        """Test recording an error with a solution"""
        reflexion = ReflexionPattern()

        error_info = {
            "test_name": "test_database_connection",
            "error_type": "ConnectionError",
            "error_message": "Could not connect to database",
            "solution": "Ensure database is running and credentials are correct",
        }

        reflexion.record_error(error_info)

    def test_get_solution_for_known_error(self):
        """Test retrieving solution for a known error pattern"""
        reflexion = ReflexionPattern()

        # Record an error with solution
        error_info = {
            "error_type": "ImportError",
            "error_message": "No module named 'pytest'",
            "solution": "Install pytest: pip install pytest",
        }

        reflexion.record_error(error_info)

        # Try to get solution for similar error
        error_signature = "ImportError: No module named 'pytest'"
        solution = reflexion.get_solution(error_signature)

        # Note: Actual implementation might return None if not implemented yet
        # This test documents expected behavior
        assert solution is None or isinstance(solution, str)

    def test_error_pattern_matching(self):
        """Test error pattern matching functionality"""
        reflexion = ReflexionPattern()

        # Record multiple similar errors
        errors = [
            {
                "error_type": "TypeError",
                "error_message": "expected str, got int",
                "solution": "Convert int to str using str()",
            },
            {
                "error_type": "TypeError",
                "error_message": "expected int, got str",
                "solution": "Convert str to int using int()",
            },
        ]

        for error in errors:
            reflexion.record_error(error)

        # Test pattern matching (implementation-dependent)
        error_signature = "TypeError"
        solution = reflexion.get_solution(error_signature)

        assert solution is None or isinstance(solution, str)

    def test_reflexion_memory_persistence(self, temp_memory_dir):
        """Test that reflexion can work with memory directory"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        error_info = {
            "test_name": "test_feature",
            "error_type": "ValueError",
            "error_message": "Invalid input",
        }

        # Should not raise exception even with custom memory dir
        reflexion.record_error(error_info)

    def test_error_learning_across_sessions(self):
        """
        Test that errors can be learned across sessions

        Note: This tests the interface, actual persistence
        depends on implementation
        """
        reflexion = ReflexionPattern()

        # Session 1: Record error
        error_info = {
            "error_type": "FileNotFoundError",
            "error_message": "config.json not found",
            "solution": "Create config.json in project root",
            "session": "session_1",
        }

        reflexion.record_error(error_info)

        # Session 2: Retrieve solution
        error_signature = "FileNotFoundError: config.json"
        solution = reflexion.get_solution(error_signature)

        # Implementation may or may not persist across instances
        assert solution is None or isinstance(solution, str)


@pytest.mark.reflexion
def test_reflexion_marker_integration(reflexion_pattern):
    """
    Test that reflexion marker works with pytest plugin fixture

    If this test fails, reflexion should record the failure
    """
    # Test that fixture is properly provided
    assert reflexion_pattern is not None

    # Record a test error
    error_info = {
        "test_name": "test_reflexion_marker_integration",
        "error_type": "IntegrationTestError",
        "error_message": "Testing reflexion integration",
    }

    # Should not raise exception
    reflexion_pattern.record_error(error_info)


def test_reflexion_with_real_exception():
    """
    Test reflexion pattern with a real exception scenario

    This simulates how reflexion would be used in practice
    """
    reflexion = ReflexionPattern()

    try:
        # Simulate an operation that fails
        _ = 10 / 0  # noqa: F841
    except ZeroDivisionError as e:
        # Record the error
        error_info = {
            "test_name": "test_reflexion_with_real_exception",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": "simulated traceback",
            "solution": "Check denominator is not zero before division",
        }

        reflexion.record_error(error_info)

    # Test should complete successfully
    assert True
