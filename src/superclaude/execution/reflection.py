"""
Reflection Engine - 3-Stage Pre-Execution Confidence Check

Implements the "Triple Reflection" pattern:
1. Requirement clarity analysis
2. Past mistake pattern detection
3. Context sufficiency validation

Only proceeds with execution if confidence >70%.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
from datetime import datetime


@dataclass
class ReflectionResult:
    """Single reflection analysis result"""
    stage: str
    score: float  # 0.0 - 1.0
    evidence: List[str]
    concerns: List[str]

    def __repr__(self) -> str:
        emoji = "✅" if self.score > 0.7 else "⚠️" if self.score > 0.4 else "❌"
        return f"{emoji} {self.stage}: {self.score:.0%}"


@dataclass
class ConfidenceScore:
    """Overall pre-execution confidence assessment"""

    # Individual reflection scores
    requirement_clarity: ReflectionResult
    mistake_check: ReflectionResult
    context_ready: ReflectionResult

    # Overall confidence (weighted average)
    confidence: float

    # Decision
    should_proceed: bool
    blockers: List[str]
    recommendations: List[str]

    def __repr__(self) -> str:
        status = "🟢 PROCEED" if self.should_proceed else "🔴 BLOCKED"
        return f"{status} | Confidence: {self.confidence:.0%}\n" + \
               f"  Clarity: {self.requirement_clarity}\n" + \
               f"  Mistakes: {self.mistake_check}\n" + \
               f"  Context: {self.context_ready}"


class ReflectionEngine:
    """
    3-Stage Pre-Execution Reflection System

    Prevents wrong-direction execution by deep reflection
    before committing resources to implementation.

    Workflow:
    1. Reflect on requirement clarity (what to build)
    2. Reflect on past mistakes (what not to do)
    3. Reflect on context readiness (can I do it)
    4. Calculate overall confidence
    5. BLOCK if <70%, PROCEED if ≥70%
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.memory_path = repo_path / "docs" / "memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)

        # Confidence threshold
        self.CONFIDENCE_THRESHOLD = 0.7

        # Weights for confidence calculation
        self.WEIGHTS = {
            "clarity": 0.5,      # Most important
            "mistakes": 0.3,     # Learn from past
            "context": 0.2,      # Least critical (can load more)
        }

    def reflect(self, task: str, context: Optional[Dict[str, Any]] = None) -> ConfidenceScore:
        """
        3-Stage Reflection Process

        Returns confidence score with decision to proceed or block.
        """

        print("🧠 Reflection Engine: 3-Stage Analysis")
        print("=" * 60)

        # Stage 1: Requirement Clarity
        clarity = self._reflect_clarity(task, context)
        print(f"1️⃣ {clarity}")

        # Stage 2: Past Mistakes
        mistakes = self._reflect_mistakes(task, context)
        print(f"2️⃣ {mistakes}")

        # Stage 3: Context Readiness
        context_ready = self._reflect_context(task, context)
        print(f"3️⃣ {context_ready}")

        # Calculate overall confidence
        confidence = (
            clarity.score * self.WEIGHTS["clarity"] +
            mistakes.score * self.WEIGHTS["mistakes"] +
            context_ready.score * self.WEIGHTS["context"]
        )

        # Decision logic
        should_proceed = confidence >= self.CONFIDENCE_THRESHOLD

        # Collect blockers and recommendations
        blockers = []
        recommendations = []

        if clarity.score < 0.7:
            blockers.extend(clarity.concerns)
            recommendations.append("Clarify requirements with user")

        if mistakes.score < 0.7:
            blockers.extend(mistakes.concerns)
            recommendations.append("Review past mistakes before proceeding")

        if context_ready.score < 0.7:
            blockers.extend(context_ready.concerns)
            recommendations.append("Load additional context files")

        result = ConfidenceScore(
            requirement_clarity=clarity,
            mistake_check=mistakes,
            context_ready=context_ready,
            confidence=confidence,
            should_proceed=should_proceed,
            blockers=blockers,
            recommendations=recommendations
        )

        print("=" * 60)
        print(result)
        print("=" * 60)

        return result

    def _reflect_clarity(self, task: str, context: Optional[Dict] = None) -> ReflectionResult:
        """
        Reflection 1: Requirement Clarity

        Analyzes if the task description is specific enough
        to proceed with implementation.
        """

        evidence = []
        concerns = []
        score = 0.5  # Start neutral

        # Check for specificity indicators
        specific_verbs = ["create", "fix", "add", "update", "delete", "refactor", "implement"]
        vague_verbs = ["improve", "optimize", "enhance", "better", "something"]

        task_lower = task.lower()

        # Positive signals (increase score)
        if any(verb in task_lower for verb in specific_verbs):
            score += 0.2
            evidence.append("Contains specific action verb")

        # Technical terms present
        if any(term in task_lower for term in ["function", "class", "file", "api", "endpoint"]):
            score += 0.15
            evidence.append("Includes technical specifics")

        # Has concrete targets
        if any(char in task for char in ["/", ".", "(", ")"]):
            score += 0.15
            evidence.append("References concrete code elements")

        # Negative signals (decrease score)
        if any(verb in task_lower for verb in vague_verbs):
            score -= 0.2
            concerns.append("Contains vague action verbs")

        # Too short (likely unclear)
        if len(task.split()) < 5:
            score -= 0.15
            concerns.append("Task description too brief")

        # Clamp score to [0, 1]
        score = max(0.0, min(1.0, score))

        return ReflectionResult(
            stage="Requirement Clarity",
            score=score,
            evidence=evidence,
            concerns=concerns
        )

    def _reflect_mistakes(self, task: str, context: Optional[Dict] = None) -> ReflectionResult:
        """
        Reflection 2: Past Mistake Check

        Searches for similar past mistakes and warns if detected.
        """

        evidence = []
        concerns = []
        score = 1.0  # Start optimistic (no mistakes known)

        # Load reflexion memory
        reflexion_file = self.memory_path / "reflexion.json"

        if not reflexion_file.exists():
            evidence.append("No past mistakes recorded")
            return ReflectionResult(
                stage="Past Mistakes",
                score=score,
                evidence=evidence,
                concerns=concerns
            )

        try:
            with open(reflexion_file) as f:
                reflexion_data = json.load(f)

            past_mistakes = reflexion_data.get("mistakes", [])

            # Search for similar mistakes
            similar_mistakes = []
            task_keywords = set(task.lower().split())

            for mistake in past_mistakes:
                mistake_keywords = set(mistake.get("task", "").lower().split())
                overlap = task_keywords & mistake_keywords

                if len(overlap) >= 2:  # At least 2 common words
                    similar_mistakes.append(mistake)

            if similar_mistakes:
                score -= 0.3 * min(len(similar_mistakes), 3)  # Max -0.9
                concerns.append(f"Found {len(similar_mistakes)} similar past mistakes")

                for mistake in similar_mistakes[:3]:  # Show max 3
                    concerns.append(f"  ⚠️ {mistake.get('mistake', 'Unknown')}")
            else:
                evidence.append(f"Checked {len(past_mistakes)} past mistakes - none similar")

        except Exception as e:
            concerns.append(f"Could not load reflexion memory: {e}")
            score = 0.7  # Neutral when can't check

        # Clamp score
        score = max(0.0, min(1.0, score))

        return ReflectionResult(
            stage="Past Mistakes",
            score=score,
            evidence=evidence,
            concerns=concerns
        )

    def _reflect_context(self, task: str, context: Optional[Dict] = None) -> ReflectionResult:
        """
        Reflection 3: Context Readiness

        Validates that sufficient context is loaded to proceed.
        """

        evidence = []
        concerns = []
        score = 0.5  # Start neutral

        # Check if context provided
        if not context:
            concerns.append("No context provided")
            score = 0.3
            return ReflectionResult(
                stage="Context Readiness",
                score=score,
                evidence=evidence,
                concerns=concerns
            )

        # Check for essential context elements
        essential_keys = ["project_index", "current_branch", "git_status"]

        loaded_keys = [key for key in essential_keys if key in context]

        if len(loaded_keys) == len(essential_keys):
            score += 0.3
            evidence.append("All essential context loaded")
        else:
            missing = set(essential_keys) - set(loaded_keys)
            score -= 0.2
            concerns.append(f"Missing context: {', '.join(missing)}")

        # Check project index exists and is fresh
        index_path = self.repo_path / "PROJECT_INDEX.md"

        if index_path.exists():
            # Check age
            age_days = (datetime.now().timestamp() - index_path.stat().st_mtime) / 86400

            if age_days < 7:
                score += 0.2
                evidence.append(f"Project index is fresh ({age_days:.1f} days old)")
            else:
                concerns.append(f"Project index is stale ({age_days:.0f} days old)")
        else:
            score -= 0.2
            concerns.append("Project index missing")

        # Clamp score
        score = max(0.0, min(1.0, score))

        return ReflectionResult(
            stage="Context Readiness",
            score=score,
            evidence=evidence,
            concerns=concerns
        )

    def record_reflection(self, task: str, confidence: ConfidenceScore, decision: str):
        """Record reflection results for future learning"""

        reflection_log = self.memory_path / "reflection_log.json"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "confidence": confidence.confidence,
            "decision": decision,
            "blockers": confidence.blockers,
            "recommendations": confidence.recommendations
        }

        # Append to log
        try:
            if reflection_log.exists():
                with open(reflection_log) as f:
                    log_data = json.load(f)
            else:
                log_data = {"reflections": []}

            log_data["reflections"].append(entry)

            with open(reflection_log, 'w') as f:
                json.dump(log_data, f, indent=2)

        except Exception as e:
            print(f"⚠️ Could not record reflection: {e}")


# Singleton instance
_reflection_engine: Optional[ReflectionEngine] = None


def get_reflection_engine(repo_path: Optional[Path] = None) -> ReflectionEngine:
    """Get or create reflection engine singleton"""
    global _reflection_engine

    if _reflection_engine is None:
        if repo_path is None:
            repo_path = Path.cwd()
        _reflection_engine = ReflectionEngine(repo_path)

    return _reflection_engine


# Convenience function
def reflect_before_execution(task: str, context: Optional[Dict] = None) -> ConfidenceScore:
    """
    Perform 3-stage reflection before task execution

    Returns ConfidenceScore with decision to proceed or block.
    """
    engine = get_reflection_engine()
    return engine.reflect(task, context)
