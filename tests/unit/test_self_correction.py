"""
Unit tests for SelfCorrectionEngine

Tests failure detection, root cause analysis, prevention rule
generation, and reflexion-based learning.
"""

import json

import pytest

from superclaude.execution.self_correction import (
    FailureEntry,
    RootCause,
    SelfCorrectionEngine,
)


@pytest.fixture
def correction_engine(tmp_path):
    """Create a SelfCorrectionEngine with temporary repo path"""
    return SelfCorrectionEngine(tmp_path)


@pytest.fixture
def engine_with_history(tmp_path):
    """Create engine with existing failure history"""
    engine = SelfCorrectionEngine(tmp_path)

    # Add a past failure
    root_cause = RootCause(
        category="validation",
        description="Missing input validation",
        evidence=["No null check"],
        prevention_rule="ALWAYS validate inputs before processing",
        validation_tests=["Check input is not None"],
    )

    entry = FailureEntry(
        id="abc12345",
        timestamp="2026-01-01T00:00:00",
        task="create user registration form",
        failure_type="validation",
        error_message="TypeError: cannot read property of null",
        root_cause=root_cause,
        fixed=True,
        fix_description="Added null check",
    )

    with open(engine.reflexion_file) as f:
        data = json.load(f)

    data["mistakes"].append(entry.to_dict())
    data["prevention_rules"].append(root_cause.prevention_rule)

    with open(engine.reflexion_file, "w") as f:
        json.dump(data, f, indent=2)

    return engine


class TestRootCause:
    """Test RootCause dataclass"""

    def test_root_cause_creation(self):
        """Test basic RootCause creation"""
        rc = RootCause(
            category="logic",
            description="Off-by-one error",
            evidence=["Loop bound incorrect"],
            prevention_rule="ALWAYS verify loop boundaries",
            validation_tests=["Test boundary conditions"],
        )
        assert rc.category == "logic"
        assert "logic" in repr(rc).lower() or "Logic" in repr(rc)

    def test_root_cause_repr(self):
        """RootCause repr should show key info"""
        rc = RootCause(
            category="type",
            description="Wrong type passed",
            evidence=["Expected int, got str"],
            prevention_rule="Add type hints",
            validation_tests=["test1", "test2"],
        )
        text = repr(rc)
        assert "type" in text.lower()
        assert "2 validation" in text


class TestFailureEntry:
    """Test FailureEntry dataclass"""

    def test_to_dict_roundtrip(self):
        """FailureEntry should survive dict serialization roundtrip"""
        rc = RootCause(
            category="dependency",
            description="Missing module",
            evidence=["ImportError"],
            prevention_rule="Check deps",
            validation_tests=["Verify import"],
        )
        entry = FailureEntry(
            id="test123",
            timestamp="2026-01-01T00:00:00",
            task="install package",
            failure_type="dependency",
            error_message="ModuleNotFoundError",
            root_cause=rc,
            fixed=False,
        )

        d = entry.to_dict()
        restored = FailureEntry.from_dict(d)

        assert restored.id == entry.id
        assert restored.task == entry.task
        assert restored.root_cause.category == "dependency"


class TestSelfCorrectionEngine:
    """Test suite for SelfCorrectionEngine"""

    def test_init_creates_reflexion_file(self, correction_engine):
        """Engine should create reflexion.json on init"""
        assert correction_engine.reflexion_file.exists()

        data = json.loads(correction_engine.reflexion_file.read_text())
        assert data["version"] == "1.0"
        assert data["mistakes"] == []
        assert data["prevention_rules"] == []

    def test_detect_failure_failed(self, correction_engine):
        """Should detect 'failed' status"""
        assert correction_engine.detect_failure({"status": "failed"}) is True

    def test_detect_failure_error(self, correction_engine):
        """Should detect 'error' status"""
        assert correction_engine.detect_failure({"status": "error"}) is True

    def test_detect_failure_success(self, correction_engine):
        """Should not detect success as failure"""
        assert correction_engine.detect_failure({"status": "success"}) is False

    def test_detect_failure_unknown(self, correction_engine):
        """Should not detect unknown status as failure"""
        assert correction_engine.detect_failure({"status": "unknown"}) is False

    def test_categorize_validation(self, correction_engine):
        """Validation errors should be categorized correctly"""
        result = correction_engine._categorize_failure("invalid input format", "")
        assert result == "validation"

    def test_categorize_dependency(self, correction_engine):
        """Dependency errors should be categorized correctly"""
        result = correction_engine._categorize_failure(
            "ModuleNotFoundError: No module named 'foo'", ""
        )
        assert result == "dependency"

    def test_categorize_logic(self, correction_engine):
        """Logic errors should be categorized correctly"""
        result = correction_engine._categorize_failure(
            "AssertionError: expected 5, actual 3", ""
        )
        assert result == "logic"

    def test_categorize_type(self, correction_engine):
        """Type errors should be categorized correctly"""
        result = correction_engine._categorize_failure("TypeError: int is not str", "")
        assert result == "type"

    def test_categorize_unknown(self, correction_engine):
        """Uncategorizable errors should be 'unknown'"""
        result = correction_engine._categorize_failure("Something weird happened", "")
        assert result == "unknown"

    def test_analyze_root_cause(self, correction_engine):
        """Should produce a RootCause with all fields populated"""
        failure = {"error": "invalid input: expected integer", "stack_trace": ""}

        root_cause = correction_engine.analyze_root_cause("validate user input", failure)

        assert isinstance(root_cause, RootCause)
        assert root_cause.category == "validation"
        assert root_cause.prevention_rule != ""
        assert len(root_cause.validation_tests) > 0

    def test_learn_and_prevent_new_failure(self, correction_engine):
        """New failure should be stored in reflexion memory"""
        failure = {"type": "logic", "error": "Expected True, got False"}
        root_cause = RootCause(
            category="logic",
            description="Assertion failed",
            evidence=["Wrong return value"],
            prevention_rule="ALWAYS verify return values",
            validation_tests=["Check assertion"],
        )

        correction_engine.learn_and_prevent("test logic check", failure, root_cause)

        data = json.loads(correction_engine.reflexion_file.read_text())
        assert len(data["mistakes"]) == 1
        assert "ALWAYS verify return values" in data["prevention_rules"]

    def test_learn_and_prevent_recurring_failure(self, correction_engine):
        """Same failure twice should increment recurrence count"""
        failure = {"type": "logic", "error": "Same error message"}
        root_cause = RootCause(
            category="logic",
            description="Same error",
            evidence=["Same"],
            prevention_rule="Fix it",
            validation_tests=["Test"],
        )

        # Record twice with same task+error (same hash)
        correction_engine.learn_and_prevent("same task", failure, root_cause)
        correction_engine.learn_and_prevent("same task", failure, root_cause)

        data = json.loads(correction_engine.reflexion_file.read_text())
        assert len(data["mistakes"]) == 1  # Not duplicated
        assert data["mistakes"][0]["recurrence_count"] == 1

    def test_find_similar_failures(self, engine_with_history):
        """Should find past failures with keyword overlap"""
        similar = engine_with_history._find_similar_failures(
            "create user registration endpoint",
            "null pointer error",
        )
        assert len(similar) >= 1

    def test_find_no_similar_failures(self, engine_with_history):
        """Unrelated task should find no similar failures"""
        similar = engine_with_history._find_similar_failures(
            "deploy kubernetes cluster",
            "pod scheduling error",
        )
        assert len(similar) == 0

    def test_get_prevention_rules(self, engine_with_history):
        """Should return stored prevention rules"""
        rules = engine_with_history.get_prevention_rules()
        assert len(rules) >= 1
        assert "validate" in rules[0].lower()

    def test_check_against_past_mistakes(self, engine_with_history):
        """Should find relevant past failures for similar task"""
        relevant = engine_with_history.check_against_past_mistakes(
            "update user registration form"
        )
        assert len(relevant) >= 1

    def test_check_against_past_mistakes_no_match(self, engine_with_history):
        """Unrelated task should have no relevant past failures"""
        relevant = engine_with_history.check_against_past_mistakes(
            "configure nginx reverse proxy"
        )
        assert len(relevant) == 0

    def test_generate_prevention_rule_with_similar(self, correction_engine):
        """Prevention rule should note recurrence when similar failures exist"""
        similar = [
            FailureEntry(
                id="x",
                timestamp="",
                task="t",
                failure_type="v",
                error_message="e",
                root_cause=RootCause("v", "d", [], "r", []),
                fixed=False,
            )
        ]
        rule = correction_engine._generate_prevention_rule("validation", "err", similar)
        assert "1 times before" in rule

    def test_generate_validation_tests_known_category(self, correction_engine):
        """Known categories should return specific tests"""
        tests = correction_engine._generate_validation_tests("validation", "err")
        assert len(tests) == 3
        assert any("None" in t for t in tests)

    def test_generate_validation_tests_unknown_category(self, correction_engine):
        """Unknown category should return generic tests"""
        tests = correction_engine._generate_validation_tests("exotic", "err")
        assert len(tests) >= 1
