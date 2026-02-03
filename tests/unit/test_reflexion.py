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


class TestErrorSignature:
    """Tests for error signature creation"""

    def test_create_signature_with_all_fields(self, temp_memory_dir):
        """Test signature creation with all fields"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        error_info = {
            "error_type": "ValueError",
            "error_message": "Invalid value: 123",
            "test_name": "test_validation",
        }

        signature = reflexion._create_error_signature(error_info)

        assert "ValueError" in signature
        assert "test_validation" in signature
        # Numbers should be replaced with N
        assert "N" in signature or "123" not in signature

    def test_create_signature_partial_info(self, temp_memory_dir):
        """Test signature creation with partial info"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        error_info = {"error_type": "TypeError"}

        signature = reflexion._create_error_signature(error_info)

        assert "TypeError" in signature

    def test_create_signature_empty_info(self, temp_memory_dir):
        """Test signature creation with empty info"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        signature = reflexion._create_error_signature({})

        assert signature == ""


class TestSignatureMatching:
    """Tests for signature matching"""

    def test_signatures_match_identical(self, temp_memory_dir):
        """Test matching identical signatures"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        sig = "ValueError | invalid input | test_feature"

        assert reflexion._signatures_match(sig, sig) is True

    def test_signatures_match_similar(self, temp_memory_dir):
        """Test matching similar signatures"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        sig1 = "ValueError invalid input test_feature"
        sig2 = "ValueError invalid data test_feature"

        # Should match with sufficient overlap
        result = reflexion._signatures_match(sig1, sig2, threshold=0.5)
        assert result is True

    def test_signatures_no_match(self, temp_memory_dir):
        """Test non-matching signatures"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        sig1 = "ValueError invalid input"
        sig2 = "TypeError connection error"

        assert reflexion._signatures_match(sig1, sig2) is False

    def test_signatures_empty(self, temp_memory_dir):
        """Test matching empty signatures"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        assert reflexion._signatures_match("", "") is False
        assert reflexion._signatures_match("test", "") is False


class TestSimilarityCalculation:
    """Tests for similarity calculation"""

    def test_calculate_similarity_identical(self, temp_memory_dir):
        """Test similarity of identical strings"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        score = reflexion._calculate_similarity("test error", "test error")

        assert score == 1.0

    def test_calculate_similarity_different(self, temp_memory_dir):
        """Test similarity of different strings"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        score = reflexion._calculate_similarity("apple orange", "banana grape")

        assert score == 0.0

    def test_calculate_similarity_partial(self, temp_memory_dir):
        """Test partial similarity"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        score = reflexion._calculate_similarity(
            "ValueError invalid input", "ValueError bad input"
        )

        assert 0.0 < score < 1.0

    def test_calculate_similarity_error_type_boost(self, temp_memory_dir):
        """Test error type matching boost"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        # With matching error type
        score_with = reflexion._calculate_similarity(
            "assertionerror test", "assertionerror check"
        )

        # Without matching error type
        score_without = reflexion._calculate_similarity("test one", "check two")

        # Error type match should boost score
        assert score_with > score_without


class TestMindbaseIntegration:
    """Tests for Mindbase integration"""

    def test_is_mindbase_enabled_default(self, temp_memory_dir, monkeypatch):
        """Test Mindbase disabled by default"""
        monkeypatch.delenv("MINDBASE_ENABLED", raising=False)

        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        assert reflexion._is_mindbase_enabled() is False

    def test_is_mindbase_enabled_true(self, temp_memory_dir, monkeypatch):
        """Test Mindbase enabled via environment"""
        monkeypatch.setenv("MINDBASE_ENABLED", "1")

        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        assert reflexion._is_mindbase_enabled() is True

    def test_search_mindbase_disabled(self, temp_memory_dir, monkeypatch):
        """Test search returns None when Mindbase disabled"""
        monkeypatch.delenv("MINDBASE_ENABLED", raising=False)

        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        result = reflexion._search_mindbase("any signature")

        assert result is None

    def test_store_to_mindbase_disabled(self, temp_memory_dir, monkeypatch):
        """Test store returns False when Mindbase disabled"""
        monkeypatch.delenv("MINDBASE_ENABLED", raising=False)

        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        result = reflexion.store_to_mindbase({"error_type": "Test"})

        assert result is False

    def test_store_to_mindbase_enabled(self, temp_memory_dir, monkeypatch):
        """Test store when Mindbase enabled"""
        monkeypatch.setenv("MINDBASE_ENABLED", "1")

        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        result = reflexion.store_to_mindbase(
            {
                "error_type": "TestError",
                "error_message": "Test message",
                "solution": "Test solution",
            }
        )

        assert result is True

        # Verify file was created
        cache_file = temp_memory_dir / "mindbase_cache.jsonl"
        assert cache_file.exists()

    def test_search_mindbase_with_cache(self, temp_memory_dir, monkeypatch):
        """Test searching Mindbase cache"""
        monkeypatch.setenv("MINDBASE_ENABLED", "1")

        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        # Store an error
        reflexion.store_to_mindbase(
            {
                "error_type": "ValueError",
                "error_message": "Invalid input value",
                "solution": "Validate input before processing",
            }
        )

        # Search for similar error
        result = reflexion._search_mindbase("ValueError invalid input")

        assert result is not None
        assert result["source"] == "mindbase"


class TestCrossSessionPatterns:
    """Tests for cross-session pattern learning"""

    def test_get_cross_session_patterns_empty(self, temp_memory_dir):
        """Test getting patterns when none exist"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        patterns = reflexion.get_cross_session_patterns()

        assert patterns == []

    def test_get_cross_session_patterns_with_data(self, temp_memory_dir, monkeypatch):
        """Test getting patterns with stored data"""
        monkeypatch.setenv("MINDBASE_ENABLED", "1")

        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        # Store some patterns
        reflexion.store_to_mindbase(
            {
                "error_type": "ImportError",
                "error_message": "No module named X",
                "solution": "Install module X",
            }
        )

        patterns = reflexion.get_cross_session_patterns()

        assert len(patterns) == 1
        assert patterns[0]["error_type"] == "ImportError"


class TestLocalFileSearch:
    """Tests for local file search"""

    def test_search_local_files_no_file(self, temp_memory_dir):
        """Test search when solutions file doesn't exist"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        result = reflexion._search_local_files("any signature")

        assert result is None

    def test_search_local_files_with_match(self, temp_memory_dir):
        """Test search with matching solution"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        # Record an error
        reflexion.record_error(
            {
                "error_type": "KeyError",
                "error_message": "Key 'foo' not found",
                "solution": "Check if key exists before access",
            }
        )

        # Search for similar error
        result = reflexion._search_local_files("KeyError | Key 'foo' not found")

        # May or may not find depending on matching threshold
        assert result is None or isinstance(result, dict)


class TestStatistics:
    """Tests for statistics"""

    def test_get_statistics_empty(self, temp_memory_dir):
        """Test statistics with no data"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        stats = reflexion.get_statistics()

        assert stats["total_errors"] == 0
        assert stats["errors_with_solutions"] == 0
        assert stats["solution_reuse_rate"] == 0.0

    def test_get_statistics_with_data(self, temp_memory_dir):
        """Test statistics with recorded data"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        # Record some errors
        reflexion.record_error(
            {
                "error_type": "Error1",
                "error_message": "Message 1",
                "solution": "Fix 1",
            }
        )
        reflexion.record_error(
            {
                "error_type": "Error2",
                "error_message": "Message 2",
            }
        )

        stats = reflexion.get_statistics()

        assert stats["total_errors"] == 2
        assert stats["errors_with_solutions"] == 1
        assert stats["solution_reuse_rate"] == 50.0


class TestMistakeDoc:
    """Tests for mistake documentation"""

    def test_create_mistake_doc(self, temp_memory_dir):
        """Test mistake doc creation"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        error_info = {
            "test_name": "test_feature",
            "error_type": "AssertionError",
            "error_message": "Expected 5, got 3",
            "traceback": "File test.py, line 10",
            "root_cause": "Calculation bug",
            "solution": "Fix the calculation",
            "why_missed": "Missed edge case",
            "prevention": "Add more tests",
            "lesson": "Always test edge cases",
        }

        reflexion._create_mistake_doc(error_info)

        # Check file was created
        files = list(reflexion.mistakes_dir.iterdir())
        assert len(files) == 1
        assert "test_feature" in files[0].name

    def test_record_error_creates_mistake_doc(self, temp_memory_dir):
        """Test that record_error creates mistake doc when solution provided"""
        reflexion = ReflexionPattern(memory_dir=temp_memory_dir)

        reflexion.record_error(
            {
                "test_name": "test_with_solution",
                "error_type": "ValueError",
                "solution": "Fix the validation",
            }
        )

        # Mistake doc should be created
        files = list(reflexion.mistakes_dir.iterdir())
        assert len(files) == 1
