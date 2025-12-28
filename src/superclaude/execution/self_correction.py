"""
Self-Correction Engine - Learn from Mistakes

Detects failures, analyzes root causes, and prevents recurrence
through Reflexion-based learning.

Key features:
- Automatic failure detection
- Root cause analysis
- Pattern recognition across failures
- Prevention rule generation
- Persistent learning memory
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class RootCause:
    """Identified root cause of failure"""

    category: str  # e.g., "validation", "dependency", "logic", "assumption"
    description: str
    evidence: List[str]
    prevention_rule: str
    validation_tests: List[str]

    def __repr__(self) -> str:
        return (
            f"Root Cause: {self.category}\n"
            f"  Description: {self.description}\n"
            f"  Prevention: {self.prevention_rule}\n"
            f"  Tests: {len(self.validation_tests)} validation checks"
        )


@dataclass
class FailureEntry:
    """Single failure entry in Reflexion memory"""

    id: str
    timestamp: str
    task: str
    failure_type: str
    error_message: str
    root_cause: RootCause
    fixed: bool
    fix_description: Optional[str] = None
    recurrence_count: int = 0

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict"""
        d = asdict(self)
        d["root_cause"] = asdict(self.root_cause)
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "FailureEntry":
        """Create from dict"""
        root_cause_data = data.pop("root_cause")
        root_cause = RootCause(**root_cause_data)
        return cls(**data, root_cause=root_cause)


class SelfCorrectionEngine:
    """
    Self-Correction Engine with Reflexion Learning

    Workflow:
    1. Detect failure
    2. Analyze root cause
    3. Store in Reflexion memory
    4. Generate prevention rules
    5. Apply automatically in future executions
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.memory_path = repo_path / "docs" / "memory"
        self.memory_path.mkdir(parents=True, exist_ok=True)

        self.reflexion_file = self.memory_path / "reflexion.json"

        # Initialize reflexion memory if needed
        if not self.reflexion_file.exists():
            self._init_reflexion_memory()

    def _init_reflexion_memory(self):
        """Initialize empty reflexion memory"""
        initial_data = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "mistakes": [],
            "patterns": [],
            "prevention_rules": [],
        }

        with open(self.reflexion_file, "w") as f:
            json.dump(initial_data, f, indent=2)

    def detect_failure(self, execution_result: Dict[str, Any]) -> bool:
        """
        Detect if execution failed

        Returns True if failure detected.
        """
        status = execution_result.get("status", "unknown")
        return status in ["failed", "error", "exception"]

    def analyze_root_cause(self, task: str, failure: Dict[str, Any]) -> RootCause:
        """
        Analyze root cause of failure

        Uses pattern matching and similarity search to identify
        the fundamental cause.
        """

        print("🔍 Self-Correction: Analyzing root cause")
        print("=" * 60)

        error_msg = failure.get("error", "Unknown error")
        stack_trace = failure.get("stack_trace", "")

        # Pattern recognition
        category = self._categorize_failure(error_msg, stack_trace)

        # Load past similar failures
        similar = self._find_similar_failures(task, error_msg)

        if similar:
            print(f"Found {len(similar)} similar past failures")

        # Generate prevention rule
        prevention_rule = self._generate_prevention_rule(category, error_msg, similar)

        # Generate validation tests
        validation_tests = self._generate_validation_tests(category, error_msg)

        root_cause = RootCause(
            category=category,
            description=error_msg,
            evidence=[error_msg, stack_trace] if stack_trace else [error_msg],
            prevention_rule=prevention_rule,
            validation_tests=validation_tests,
        )

        print(root_cause)
        print("=" * 60)

        return root_cause

    def _categorize_failure(self, error_msg: str, stack_trace: str) -> str:
        """Categorize failure type"""

        error_lower = error_msg.lower()

        # Validation failures
        if any(
            word in error_lower for word in ["invalid", "missing", "required", "must"]
        ):
            return "validation"

        # Dependency failures
        if any(
            word in error_lower for word in ["not found", "missing", "import", "module"]
        ):
            return "dependency"

        # Logic errors
        if any(word in error_lower for word in ["assertion", "expected", "actual"]):
            return "logic"

        # Assumption failures
        if any(word in error_lower for word in ["assume", "should", "expected"]):
            return "assumption"

        # Type errors
        if "type" in error_lower:
            return "type"

        return "unknown"

    def _find_similar_failures(self, task: str, error_msg: str) -> List[FailureEntry]:
        """Find similar past failures"""

        try:
            with open(self.reflexion_file) as f:
                data = json.load(f)

            past_failures = [
                FailureEntry.from_dict(entry) for entry in data.get("mistakes", [])
            ]

            # Simple similarity: keyword overlap
            task_keywords = set(task.lower().split())
            error_keywords = set(error_msg.lower().split())

            similar = []
            for failure in past_failures:
                failure_keywords = set(failure.task.lower().split())
                error_keywords_past = set(failure.error_message.lower().split())

                task_overlap = len(task_keywords & failure_keywords)
                error_overlap = len(error_keywords & error_keywords_past)

                if task_overlap >= 2 or error_overlap >= 2:
                    similar.append(failure)

            return similar

        except Exception as e:
            print(f"⚠️ Could not load reflexion memory: {e}")
            return []

    def _generate_prevention_rule(
        self, category: str, error_msg: str, similar: List[FailureEntry]
    ) -> str:
        """Generate prevention rule based on failure analysis"""

        rules = {
            "validation": "ALWAYS validate inputs before processing",
            "dependency": "ALWAYS check dependencies exist before importing",
            "logic": "ALWAYS verify assumptions with assertions",
            "assumption": "NEVER assume - always verify with checks",
            "type": "ALWAYS use type hints and runtime type checking",
            "unknown": "ALWAYS add error handling for unknown cases",
        }

        base_rule = rules.get(category, "ALWAYS add defensive checks")

        # If similar failures exist, reference them
        if similar:
            base_rule += f" (similar mistake occurred {len(similar)} times before)"

        return base_rule

    def _generate_validation_tests(self, category: str, error_msg: str) -> List[str]:
        """Generate validation tests to prevent recurrence"""

        tests = {
            "validation": [
                "Check input is not None",
                "Verify input type matches expected",
                "Validate input range/constraints",
            ],
            "dependency": [
                "Verify module exists before import",
                "Check file exists before reading",
                "Validate path is accessible",
            ],
            "logic": [
                "Add assertion for pre-conditions",
                "Add assertion for post-conditions",
                "Verify intermediate results",
            ],
            "assumption": [
                "Explicitly check assumed condition",
                "Add logging for assumption verification",
                "Document assumption with test",
            ],
            "type": [
                "Add type hints",
                "Add runtime type checking",
                "Use dataclass with validation",
            ],
        }

        return tests.get(category, ["Add defensive check", "Add error handling"])

    def learn_and_prevent(
        self,
        task: str,
        failure: Dict[str, Any],
        root_cause: RootCause,
        fixed: bool = False,
        fix_description: Optional[str] = None,
    ):
        """
        Learn from failure and store prevention rules

        Updates Reflexion memory with new learning.
        """

        print("📚 Self-Correction: Learning from failure")

        # Generate unique ID for this failure
        failure_id = hashlib.md5(
            f"{task}{failure.get('error', '')}".encode()
        ).hexdigest()[:8]

        # Create failure entry
        entry = FailureEntry(
            id=failure_id,
            timestamp=datetime.now().isoformat(),
            task=task,
            failure_type=failure.get("type", "unknown"),
            error_message=failure.get("error", "Unknown error"),
            root_cause=root_cause,
            fixed=fixed,
            fix_description=fix_description,
            recurrence_count=0,
        )

        # Load current reflexion memory
        with open(self.reflexion_file) as f:
            data = json.load(f)

        # Check if similar failure exists (increment recurrence)
        existing_failures = data.get("mistakes", [])
        updated = False

        for existing in existing_failures:
            if existing.get("id") == failure_id:
                existing["recurrence_count"] += 1
                existing["timestamp"] = entry.timestamp
                updated = True
                print(f"⚠️ Recurring failure (count: {existing['recurrence_count']})")
                break

        if not updated:
            # New failure - add to memory
            data["mistakes"].append(entry.to_dict())
            print(f"✅ New failure recorded: {failure_id}")

        # Add prevention rule if not already present
        if root_cause.prevention_rule not in data.get("prevention_rules", []):
            if "prevention_rules" not in data:
                data["prevention_rules"] = []
            data["prevention_rules"].append(root_cause.prevention_rule)
            print("📝 Prevention rule added")

        # Save updated memory
        with open(self.reflexion_file, "w") as f:
            json.dump(data, f, indent=2)

        print("💾 Reflexion memory updated")

    def get_prevention_rules(self) -> List[str]:
        """Get all active prevention rules"""

        try:
            with open(self.reflexion_file) as f:
                data = json.load(f)

            return data.get("prevention_rules", [])

        except Exception:
            return []

    def check_against_past_mistakes(self, task: str) -> List[FailureEntry]:
        """
        Check if task is similar to past mistakes

        Returns list of relevant past failures to warn about.
        """

        try:
            with open(self.reflexion_file) as f:
                data = json.load(f)

            past_failures = [
                FailureEntry.from_dict(entry) for entry in data.get("mistakes", [])
            ]

            # Find similar tasks
            task_keywords = set(task.lower().split())

            relevant = []
            for failure in past_failures:
                failure_keywords = set(failure.task.lower().split())
                overlap = len(task_keywords & failure_keywords)

                if overlap >= 2:
                    relevant.append(failure)

            return relevant

        except Exception:
            return []


# Singleton instance
_self_correction_engine: Optional[SelfCorrectionEngine] = None


def get_self_correction_engine(
    repo_path: Optional[Path] = None,
) -> SelfCorrectionEngine:
    """Get or create self-correction engine singleton"""
    global _self_correction_engine

    if _self_correction_engine is None:
        if repo_path is None:
            repo_path = Path.cwd()
        _self_correction_engine = SelfCorrectionEngine(repo_path)

    return _self_correction_engine


# Convenience function
def learn_from_failure(
    task: str,
    failure: Dict[str, Any],
    fixed: bool = False,
    fix_description: Optional[str] = None,
):
    """
    Learn from execution failure

    Analyzes root cause and stores prevention rules.
    """
    engine = get_self_correction_engine()

    # Analyze root cause
    root_cause = engine.analyze_root_cause(task, failure)

    # Store learning
    engine.learn_and_prevent(task, failure, root_cause, fixed, fix_description)

    return root_cause
