"""
Tests for Self-Correction Engine

Tests failure detection, root cause analysis, and learning.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from superclaude.execution.self_correction import (
    FailureEntry,
    RootCause,
    SelfCorrectionEngine,
    get_self_correction_engine,
    learn_from_failure,
)


class TestRootCause:
    """Tests for RootCause dataclass"""

    def test_creation(self):
        """Test basic creation"""
        cause = RootCause(
            category="validation",
            description="Invalid input",
            evidence=["Error message"],
            prevention_rule="Always validate",
            validation_tests=["Check not None"],
        )

        assert cause.category == "validation"
        assert cause.description == "Invalid input"

    def test_repr(self):
        """Test string representation"""
        cause = RootCause(
            category="logic",
            description="Off by one error",
            evidence=["Assertion failed"],
            prevention_rule="Check boundaries",
            validation_tests=["Test edge cases"],
        )

        repr_str = repr(cause)
        assert "Root Cause" in repr_str
        assert "logic" in repr_str


class TestFailureEntry:
    """Tests for FailureEntry dataclass"""

    def test_creation(self):
        """Test basic creation"""
        cause = RootCause(
            category="validation",
            description="Test",
            evidence=[],
            prevention_rule="Test rule",
            validation_tests=[],
        )

        entry = FailureEntry(
            id="abc123",
            timestamp="2024-01-01T00:00:00",
            task="Test task",
            failure_type="error",
            error_message="Test error",
            root_cause=cause,
            fixed=False,
        )

        assert entry.id == "abc123"
        assert entry.recurrence_count == 0

    def test_to_dict(self):
        """Test conversion to dict"""
        cause = RootCause(
            category="validation",
            description="Test",
            evidence=[],
            prevention_rule="Test rule",
            validation_tests=[],
        )

        entry = FailureEntry(
            id="abc123",
            timestamp="2024-01-01T00:00:00",
            task="Test task",
            failure_type="error",
            error_message="Test error",
            root_cause=cause,
            fixed=False,
        )

        d = entry.to_dict()

        assert isinstance(d, dict)
        assert d["id"] == "abc123"
        assert isinstance(d["root_cause"], dict)

    def test_from_dict(self):
        """Test creation from dict"""
        data = {
            "id": "abc123",
            "timestamp": "2024-01-01T00:00:00",
            "task": "Test task",
            "failure_type": "error",
            "error_message": "Test error",
            "root_cause": {
                "category": "validation",
                "description": "Test",
                "evidence": [],
                "prevention_rule": "Test rule",
                "validation_tests": [],
            },
            "fixed": False,
            "fix_description": None,
            "recurrence_count": 0,
        }

        entry = FailureEntry.from_dict(data)

        assert entry.id == "abc123"
        assert entry.root_cause.category == "validation"


class TestSelfCorrectionEngine:
    """Tests for SelfCorrectionEngine"""

    def test_initialization(self):
        """Test engine initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            assert engine.repo_path == Path(tmpdir)
            assert engine.reflexion_file.exists()

    def test_init_creates_reflexion_memory(self):
        """Test initialization creates reflexion.json"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            with open(engine.reflexion_file) as f:
                data = json.load(f)

            assert "version" in data
            assert "mistakes" in data
            assert "prevention_rules" in data


class TestDetectFailure:
    """Tests for failure detection"""

    def test_detect_failed_status(self):
        """Test detection of failed status"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            result = {"status": "failed", "error": "Test error"}

            assert engine.detect_failure(result) is True

    def test_detect_error_status(self):
        """Test detection of error status"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            result = {"status": "error", "error": "Test error"}

            assert engine.detect_failure(result) is True

    def test_detect_success_no_failure(self):
        """Test success status is not failure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            result = {"status": "success"}

            assert engine.detect_failure(result) is False


class TestCategorizeFailure:
    """Tests for failure categorization"""

    def test_categorize_validation(self):
        """Test validation category detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            category = engine._categorize_failure("Invalid input provided", "")

            assert category == "validation"

    def test_categorize_dependency(self):
        """Test dependency category detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            category = engine._categorize_failure("Module not found: foo", "")

            assert category == "dependency"

    def test_categorize_logic(self):
        """Test logic category detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            category = engine._categorize_failure(
                "AssertionError: expected 5, actual 3", ""
            )

            assert category == "logic"

    def test_categorize_type(self):
        """Test type category detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            # "type" keyword triggers type category, but "expected" may trigger logic
            # The actual implementation checks for "type" in error
            category = engine._categorize_failure("type mismatch in function", "")

            assert category == "type"

    def test_categorize_unknown(self):
        """Test unknown category for unrecognized errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            category = engine._categorize_failure("Some random error", "")

            assert category == "unknown"


class TestGeneratePreventionRule:
    """Tests for prevention rule generation"""

    def test_validation_rule(self):
        """Test validation prevention rule"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            rule = engine._generate_prevention_rule("validation", "Invalid", [])

            assert "validate" in rule.lower()

    def test_dependency_rule(self):
        """Test dependency prevention rule"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            rule = engine._generate_prevention_rule("dependency", "Not found", [])

            assert "dependencies" in rule.lower() or "check" in rule.lower()

    def test_rule_includes_recurrence_info(self):
        """Test rule includes recurrence info when similar failures exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            # Create mock similar failures
            similar = [MagicMock(), MagicMock()]

            rule = engine._generate_prevention_rule("validation", "Invalid", similar)

            assert "2 times" in rule


class TestGenerateValidationTests:
    """Tests for validation test generation"""

    def test_validation_tests(self):
        """Test validation category tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            tests = engine._generate_validation_tests("validation", "Invalid")

            assert len(tests) >= 1
            assert any("None" in t or "type" in t.lower() for t in tests)

    def test_dependency_tests(self):
        """Test dependency category tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            tests = engine._generate_validation_tests("dependency", "Not found")

            assert len(tests) >= 1

    def test_unknown_has_default_tests(self):
        """Test unknown category has default tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            tests = engine._generate_validation_tests("unknown", "Error")

            assert len(tests) >= 1


class TestAnalyzeRootCause:
    """Tests for root cause analysis"""

    def test_analyze_returns_root_cause(self):
        """Test analyze_root_cause returns RootCause"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            failure = {
                "error": "Invalid input value",
                "stack_trace": "File test.py, line 10",
            }

            result = engine.analyze_root_cause("Test task", failure)

            assert isinstance(result, RootCause)

    def test_analyze_categorizes_correctly(self):
        """Test analysis categorizes error correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            # Use "not found" which triggers dependency category
            failure = {"error": "file not found in path"}

            result = engine.analyze_root_cause("Load config task", failure)

            assert result.category == "dependency"


class TestLearnAndPrevent:
    """Tests for learning from failures"""

    def test_learn_creates_entry(self):
        """Test learn_and_prevent creates failure entry"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            cause = RootCause(
                category="validation",
                description="Invalid input",
                evidence=["Error"],
                prevention_rule="Validate inputs",
                validation_tests=["Check not None"],
            )

            failure = {"error": "Invalid input", "type": "validation"}

            engine.learn_and_prevent("Test task", failure, cause)

            with open(engine.reflexion_file) as f:
                data = json.load(f)

            assert len(data["mistakes"]) == 1

    def test_learn_adds_prevention_rule(self):
        """Test learning adds prevention rule"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            cause = RootCause(
                category="logic",
                description="Off by one",
                evidence=["Assertion"],
                prevention_rule="Check array bounds",
                validation_tests=["Test boundaries"],
            )

            failure = {"error": "Index out of bounds"}

            engine.learn_and_prevent("Array task", failure, cause)

            rules = engine.get_prevention_rules()

            assert "Check array bounds" in rules

    def test_learn_increments_recurrence(self):
        """Test same failure increments recurrence count"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            cause = RootCause(
                category="validation",
                description="Invalid",
                evidence=[],
                prevention_rule="Validate",
                validation_tests=[],
            )

            failure = {"error": "Invalid input"}

            # Record same failure twice
            engine.learn_and_prevent("Same task", failure, cause)
            engine.learn_and_prevent("Same task", failure, cause)

            with open(engine.reflexion_file) as f:
                data = json.load(f)

            # Should still be one entry but with recurrence
            assert len(data["mistakes"]) == 1


class TestGetPreventionRules:
    """Tests for getting prevention rules"""

    def test_get_rules_empty(self):
        """Test getting rules when none exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            rules = engine.get_prevention_rules()

            assert rules == []

    def test_get_rules_with_data(self):
        """Test getting rules after learning"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            cause = RootCause(
                category="validation",
                description="Test",
                evidence=[],
                prevention_rule="Test prevention rule",
                validation_tests=[],
            )

            engine.learn_and_prevent("Task", {"error": "Error"}, cause)

            rules = engine.get_prevention_rules()

            assert "Test prevention rule" in rules


class TestCheckAgainstPastMistakes:
    """Tests for checking against past mistakes"""

    def test_check_no_mistakes(self):
        """Test check with no past mistakes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            relevant = engine.check_against_past_mistakes("Any task")

            assert relevant == []

    def test_check_finds_similar(self):
        """Test check finds similar past mistakes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            # Record a failure
            cause = RootCause(
                category="validation",
                description="Invalid input",
                evidence=[],
                prevention_rule="Validate",
                validation_tests=[],
            )

            engine.learn_and_prevent(
                "Validate user input function",
                {"error": "Invalid"},
                cause,
            )

            # Check for similar task
            relevant = engine.check_against_past_mistakes("Check user input validation")

            assert len(relevant) == 1


class TestSingletonAndConvenience:
    """Tests for singleton and convenience functions"""

    def test_get_engine_creates_singleton(self):
        """Test singleton creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import superclaude.execution.self_correction as mod

            mod._self_correction_engine = None

            engine = get_self_correction_engine(Path(tmpdir))

            assert isinstance(engine, SelfCorrectionEngine)

    def test_learn_from_failure_convenience(self):
        """Test convenience function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import superclaude.execution.self_correction as mod

            mod._self_correction_engine = None

            # Initialize with temp dir
            get_self_correction_engine(Path(tmpdir))

            failure = {"error": "Test validation error", "type": "validation"}

            result = learn_from_failure("Test task", failure)

            assert isinstance(result, RootCause)


class TestFindSimilarFailures:
    """Tests for finding similar failures"""

    def test_find_similar_empty(self):
        """Test finding similar when memory is empty"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            similar = engine._find_similar_failures("Any task", "Any error")

            assert similar == []

    def test_find_similar_with_matches(self):
        """Test finding similar failures with matches"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SelfCorrectionEngine(Path(tmpdir))

            # Add a failure
            cause = RootCause(
                category="validation",
                description="Input validation failed",
                evidence=[],
                prevention_rule="Validate",
                validation_tests=[],
            )

            engine.learn_and_prevent(
                "Input validation check",
                {"error": "Input validation failed"},
                cause,
            )

            # Find similar
            similar = engine._find_similar_failures(
                "Check input validation", "Validation failed"
            )

            assert len(similar) >= 1
