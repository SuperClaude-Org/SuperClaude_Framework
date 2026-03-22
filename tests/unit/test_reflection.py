"""
Unit tests for ReflectionEngine

Tests the 3-stage pre-execution confidence assessment:
1. Requirement clarity analysis
2. Past mistake pattern detection
3. Context sufficiency validation
"""

import json

import pytest

from superclaude.execution.reflection import (
    ConfidenceScore,
    ReflectionEngine,
    ReflectionResult,
)


@pytest.fixture
def reflection_engine(tmp_path):
    """Create a ReflectionEngine with temporary repo path"""
    return ReflectionEngine(tmp_path)


@pytest.fixture
def engine_with_mistakes(tmp_path):
    """Create a ReflectionEngine with past mistakes in memory"""
    memory_dir = tmp_path / "docs" / "memory"
    memory_dir.mkdir(parents=True)

    reflexion_data = {
        "mistakes": [
            {
                "task": "fix user authentication login flow",
                "mistake": "Used wrong token validation method",
            },
            {
                "task": "create database migration script",
                "mistake": "Forgot to handle nullable columns",
            },
        ],
        "patterns": [],
        "prevention_rules": [],
    }

    (memory_dir / "reflexion.json").write_text(json.dumps(reflexion_data))
    return ReflectionEngine(tmp_path)


class TestReflectionResult:
    """Test ReflectionResult dataclass"""

    def test_repr_high_score(self):
        """High score should show green checkmark"""
        result = ReflectionResult(
            stage="Test", score=0.9, evidence=["good"], concerns=[]
        )
        assert "✅" in repr(result)

    def test_repr_medium_score(self):
        """Medium score should show warning"""
        result = ReflectionResult(
            stage="Test", score=0.6, evidence=[], concerns=["concern"]
        )
        assert "⚠️" in repr(result)

    def test_repr_low_score(self):
        """Low score should show red X"""
        result = ReflectionResult(
            stage="Test", score=0.2, evidence=[], concerns=["bad"]
        )
        assert "❌" in repr(result)


class TestReflectionEngine:
    """Test suite for ReflectionEngine class"""

    def test_reflect_specific_task(self, reflection_engine):
        """Specific task description should get higher clarity score"""
        result = reflection_engine.reflect(
            "Create a new REST API endpoint for /users/{id} in users.py",
            context={"project_index": True, "current_branch": "main", "git_status": "clean"},
        )

        assert result.requirement_clarity.score > 0.5
        assert result.should_proceed is True or result.confidence > 0.0

    def test_reflect_vague_task(self, reflection_engine):
        """Vague task description should get lower clarity score"""
        result = reflection_engine.reflect("improve something")

        assert result.requirement_clarity.score < 0.7
        assert any("vague" in c.lower() for c in result.requirement_clarity.concerns)

    def test_reflect_short_task(self, reflection_engine):
        """Very short task should be flagged"""
        result = reflection_engine.reflect("fix it")

        assert result.requirement_clarity.score < 0.7
        assert any("brief" in c.lower() for c in result.requirement_clarity.concerns)

    def test_reflect_no_context(self, reflection_engine):
        """Missing context should lower context readiness score"""
        result = reflection_engine.reflect(
            "Create user authentication function in auth.py"
        )

        assert result.context_ready.score < 0.7
        assert any("context" in c.lower() for c in result.context_ready.concerns)

    def test_reflect_full_context(self, reflection_engine):
        """Full context should give high context readiness"""
        # Create PROJECT_INDEX.md to satisfy freshness check
        (reflection_engine.repo_path / "PROJECT_INDEX.md").write_text("# Index")

        result = reflection_engine.reflect(
            "Add validation to user registration",
            context={
                "project_index": "loaded",
                "current_branch": "feature/auth",
                "git_status": "clean",
            },
        )

        assert result.context_ready.score >= 0.7

    def test_reflect_no_past_mistakes(self, reflection_engine):
        """No reflexion file should give high mistake check score"""
        result = reflection_engine.reflect("Create new feature")

        assert result.mistake_check.score == 1.0
        assert any("no past" in e.lower() for e in result.mistake_check.evidence)

    def test_reflect_with_similar_mistakes(self, engine_with_mistakes):
        """Similar past mistakes should lower the score"""
        result = engine_with_mistakes.reflect(
            "fix user authentication token validation"
        )

        assert result.mistake_check.score < 1.0
        assert any("similar" in c.lower() for c in result.mistake_check.concerns)

    def test_confidence_threshold(self, reflection_engine):
        """Confidence below 70% should block execution"""
        result = reflection_engine.reflect("maybe improve something")

        if result.confidence < 0.7:
            assert result.should_proceed is False

    def test_confidence_above_threshold(self, reflection_engine):
        """Confidence above 70% should allow execution"""
        (reflection_engine.repo_path / "PROJECT_INDEX.md").write_text("# Index")

        result = reflection_engine.reflect(
            "Create a new REST API endpoint for /users/{id} in users.py",
            context={
                "project_index": "loaded",
                "current_branch": "main",
                "git_status": "clean",
            },
        )

        if result.confidence >= 0.7:
            assert result.should_proceed is True

    def test_record_reflection(self, reflection_engine):
        """Recording reflection should persist to file"""
        confidence = ConfidenceScore(
            requirement_clarity=ReflectionResult("Clarity", 0.8, ["ok"], []),
            mistake_check=ReflectionResult("Mistakes", 1.0, ["none"], []),
            context_ready=ReflectionResult("Context", 0.7, ["loaded"], []),
            confidence=0.85,
            should_proceed=True,
            blockers=[],
            recommendations=[],
        )

        reflection_engine.record_reflection("test task", confidence, "proceed")

        log_file = reflection_engine.memory_path / "reflection_log.json"
        assert log_file.exists()

        data = json.loads(log_file.read_text())
        assert len(data["reflections"]) == 1
        assert data["reflections"][0]["task"] == "test task"
        assert data["reflections"][0]["confidence"] == 0.85

    def test_weights_sum_to_one(self, reflection_engine):
        """Weight values should sum to 1.0"""
        total = sum(reflection_engine.WEIGHTS.values())
        assert abs(total - 1.0) < 0.001

    def test_clarity_specific_verbs_boost(self, reflection_engine):
        """Specific action verbs should boost clarity score"""
        result_specific = reflection_engine._reflect_clarity(
            "Create user registration endpoint", None
        )
        result_vague = reflection_engine._reflect_clarity(
            "improve the system", None
        )

        assert result_specific.score > result_vague.score
