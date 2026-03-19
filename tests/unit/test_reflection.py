"""
Tests for Reflection Engine

Tests 3-stage pre-execution confidence checking.
"""

import json
import tempfile
from pathlib import Path

from superclaude.execution.reflection import (
    ConfidenceScore,
    ReflectionEngine,
    ReflectionResult,
    get_reflection_engine,
    reflect_before_execution,
)


class TestReflectionResult:
    """Tests for ReflectionResult dataclass"""

    def test_creation(self):
        """Test basic creation"""
        result = ReflectionResult(
            stage="Test Stage",
            score=0.8,
            evidence=["Evidence 1"],
            concerns=["Concern 1"],
        )

        assert result.stage == "Test Stage"
        assert result.score == 0.8
        assert len(result.evidence) == 1
        assert len(result.concerns) == 1

    def test_repr_high_score(self):
        """Test repr with high score shows checkmark"""
        result = ReflectionResult(stage="Test", score=0.9, evidence=[], concerns=[])

        repr_str = repr(result)
        assert "✅" in repr_str
        assert "90%" in repr_str

    def test_repr_medium_score(self):
        """Test repr with medium score shows warning"""
        result = ReflectionResult(stage="Test", score=0.5, evidence=[], concerns=[])

        repr_str = repr(result)
        assert "⚠️" in repr_str

    def test_repr_low_score(self):
        """Test repr with low score shows error"""
        result = ReflectionResult(stage="Test", score=0.3, evidence=[], concerns=[])

        repr_str = repr(result)
        assert "❌" in repr_str


class TestConfidenceScore:
    """Tests for ConfidenceScore dataclass"""

    def test_creation(self):
        """Test basic creation"""
        clarity = ReflectionResult("Clarity", 0.8, [], [])
        mistakes = ReflectionResult("Mistakes", 0.9, [], [])
        context = ReflectionResult("Context", 0.7, [], [])

        score = ConfidenceScore(
            requirement_clarity=clarity,
            mistake_check=mistakes,
            context_ready=context,
            confidence=0.8,
            should_proceed=True,
            blockers=[],
            recommendations=[],
        )

        assert score.confidence == 0.8
        assert score.should_proceed is True

    def test_repr_proceed(self):
        """Test repr shows PROCEED when should_proceed is True"""
        clarity = ReflectionResult("Clarity", 0.8, [], [])
        mistakes = ReflectionResult("Mistakes", 0.9, [], [])
        context = ReflectionResult("Context", 0.7, [], [])

        score = ConfidenceScore(
            requirement_clarity=clarity,
            mistake_check=mistakes,
            context_ready=context,
            confidence=0.8,
            should_proceed=True,
            blockers=[],
            recommendations=[],
        )

        repr_str = repr(score)
        assert "PROCEED" in repr_str

    def test_repr_blocked(self):
        """Test repr shows BLOCKED when should_proceed is False"""
        clarity = ReflectionResult("Clarity", 0.5, [], [])
        mistakes = ReflectionResult("Mistakes", 0.5, [], [])
        context = ReflectionResult("Context", 0.5, [], [])

        score = ConfidenceScore(
            requirement_clarity=clarity,
            mistake_check=mistakes,
            context_ready=context,
            confidence=0.5,
            should_proceed=False,
            blockers=["Low clarity"],
            recommendations=["Clarify requirements"],
        )

        repr_str = repr(score)
        assert "BLOCKED" in repr_str


class TestReflectionEngine:
    """Tests for ReflectionEngine"""

    def test_initialization(self):
        """Test engine initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            assert engine.repo_path == Path(tmpdir)
            assert engine.memory_path.exists()
            assert engine.CONFIDENCE_THRESHOLD == 0.7

    def test_weights_sum_to_one(self):
        """Test that weights sum to 1.0"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            total = sum(engine.WEIGHTS.values())
            assert abs(total - 1.0) < 0.001

    def test_reflect_returns_confidence_score(self):
        """Test reflect method returns ConfidenceScore"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            result = engine.reflect("Create a new function for validation")

            assert isinstance(result, ConfidenceScore)

    def test_reflect_with_context(self):
        """Test reflect with context dict"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            context = {
                "project_index": "loaded",
                "current_branch": "main",
                "git_status": "clean",
            }

            result = engine.reflect("Fix the validation bug", context)

            assert isinstance(result, ConfidenceScore)


class TestReflectClarity:
    """Tests for clarity reflection"""

    def test_specific_verb_increases_score(self):
        """Test specific verbs increase clarity score"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            result = engine._reflect_clarity(
                "Create a new function to validate user input"
            )

            assert result.score > 0.5
            assert any("specific" in e.lower() for e in result.evidence)

    def test_vague_verb_decreases_score(self):
        """Test vague verbs decrease clarity score"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            result = engine._reflect_clarity("Improve something")

            assert result.score < 0.5
            assert any("vague" in c.lower() for c in result.concerns)

    def test_technical_terms_increase_score(self):
        """Test technical terms increase clarity"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            result = engine._reflect_clarity(
                "Add new API endpoint for user authentication function"
            )

            assert result.score > 0.5

    def test_short_task_decreases_score(self):
        """Test short task descriptions decrease score"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            result = engine._reflect_clarity("Fix bug")

            assert any("brief" in c.lower() for c in result.concerns)


class TestReflectMistakes:
    """Tests for past mistake reflection"""

    def test_no_mistakes_file_high_score(self):
        """Test high score when no mistakes recorded"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            result = engine._reflect_mistakes("Any task")

            assert result.score == 1.0
            assert any("no past mistakes" in e.lower() for e in result.evidence)

    def test_similar_mistakes_decreases_score(self):
        """Test similar past mistakes decrease score"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            # Create reflexion memory with mistakes
            reflexion_file = engine.memory_path / "reflexion.json"
            reflexion_data = {
                "mistakes": [
                    {
                        "task": "validation input checking",
                        "mistake": "Forgot null check",
                    }
                ]
            }
            with open(reflexion_file, "w") as f:
                json.dump(reflexion_data, f)

            result = engine._reflect_mistakes("Check validation input")

            assert result.score < 1.0
            assert any("similar" in c.lower() for c in result.concerns)


class TestReflectContext:
    """Tests for context readiness reflection"""

    def test_no_context_low_score(self):
        """Test low score when no context provided"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            result = engine._reflect_context("Any task", None)

            assert result.score == 0.3
            assert any("no context" in c.lower() for c in result.concerns)

    def test_all_context_high_score(self):
        """Test high score with all essential context"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            # Create PROJECT_INDEX.md
            (Path(tmpdir) / "PROJECT_INDEX.md").write_text("# Index")

            context = {
                "project_index": "loaded",
                "current_branch": "main",
                "git_status": "clean",
            }

            result = engine._reflect_context("Any task", context)

            assert result.score >= 0.7

    def test_missing_context_decreases_score(self):
        """Test missing context keys decrease score"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            context = {"project_index": "loaded"}  # Missing others

            result = engine._reflect_context("Any task", context)

            assert any("missing" in c.lower() for c in result.concerns)


class TestRecordReflection:
    """Tests for recording reflection results"""

    def test_record_creates_log(self):
        """Test record_reflection creates log file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            clarity = ReflectionResult("Clarity", 0.8, [], [])
            mistakes = ReflectionResult("Mistakes", 0.9, [], [])
            context = ReflectionResult("Context", 0.7, [], [])

            score = ConfidenceScore(
                requirement_clarity=clarity,
                mistake_check=mistakes,
                context_ready=context,
                confidence=0.8,
                should_proceed=True,
                blockers=[],
                recommendations=[],
            )

            engine.record_reflection("Test task", score, "proceeded")

            log_file = engine.memory_path / "reflection_log.json"
            assert log_file.exists()

    def test_record_appends_to_log(self):
        """Test multiple records append to log"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            clarity = ReflectionResult("Clarity", 0.8, [], [])
            mistakes = ReflectionResult("Mistakes", 0.9, [], [])
            context = ReflectionResult("Context", 0.7, [], [])

            score = ConfidenceScore(
                requirement_clarity=clarity,
                mistake_check=mistakes,
                context_ready=context,
                confidence=0.8,
                should_proceed=True,
                blockers=[],
                recommendations=[],
            )

            engine.record_reflection("Task 1", score, "proceeded")
            engine.record_reflection("Task 2", score, "proceeded")

            log_file = engine.memory_path / "reflection_log.json"
            with open(log_file) as f:
                data = json.load(f)

            assert len(data["reflections"]) == 2


class TestSingletonAndConvenience:
    """Tests for singleton and convenience functions"""

    def test_get_reflection_engine_creates_singleton(self):
        """Test get_reflection_engine returns engine"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Reset singleton
            import superclaude.execution.reflection as mod

            mod._reflection_engine = None

            engine = get_reflection_engine(Path(tmpdir))

            assert isinstance(engine, ReflectionEngine)

    def test_reflect_before_execution(self):
        """Test convenience function"""
        with tempfile.TemporaryDirectory():
            import superclaude.execution.reflection as mod

            mod._reflection_engine = None

            result = reflect_before_execution(
                "Create validation function",
                {
                    "project_index": "loaded",
                    "current_branch": "main",
                    "git_status": "clean",
                },
            )

            assert isinstance(result, ConfidenceScore)


class TestConfidenceThreshold:
    """Tests for confidence threshold logic"""

    def test_below_threshold_blocks(self):
        """Test confidence below threshold blocks execution"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            # Task designed to score low
            result = engine.reflect("improve")

            if result.confidence < 0.7:
                assert result.should_proceed is False

    def test_above_threshold_proceeds(self):
        """Test confidence above threshold allows execution"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ReflectionEngine(Path(tmpdir))

            # Create good conditions
            (Path(tmpdir) / "PROJECT_INDEX.md").write_text("# Index")

            context = {
                "project_index": "loaded",
                "current_branch": "main",
                "git_status": "clean",
            }

            result = engine.reflect(
                "Create a new function called validate_input in utils.py", context
            )

            if result.confidence >= 0.7:
                assert result.should_proceed is True
