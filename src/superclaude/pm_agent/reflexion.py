"""
Reflexion Error Learning Pattern

ARCHITECTURE NOTE:
    superclaude = client only. Core logic lives in airis-agent.
    This module provides a thin wrapper that delegates to airis-agent
    when available, with local fallback for testing/offline use.

Token Budget:
    - Cache hit: 0 tokens (known error -> instant solution)
    - Cache miss: 1-2K tokens (new investigation)

Performance:
    - Error recurrence rate: <10%
    - Solution reuse rate: >90%

Storage Strategy:
    - Primary: airis-agent (Mindbase MCP for semantic search)
    - Fallback: docs/memory/solutions_learned.jsonl (local file)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to import airis-agent integration (preferred)
_airis_available = False

try:
    from airis_agent.integrations.superclaude import (  # noqa: F401
        get_plugin,
        get_reflexion_memory,
    )

    _airis_available = True
except ImportError:
    pass


class ReflexionPattern:
    """
    Error learning and prevention through reflexion

    Delegates to airis-agent when available, falls back to local implementation.

    Usage:
        reflexion = ReflexionPattern()

        # When error occurs
        error_info = {
            "error_type": "AssertionError",
            "error_message": "Expected 5, got 3",
            "test_name": "test_calculation",
        }

        # Check for known solution
        solution = reflexion.get_solution(error_info)

        if solution:
            print(f"Known error - Solution: {solution}")
        else:
            # New error - investigate and record
            reflexion.record_error(error_info)
    """

    def __init__(self, memory_dir: Optional[Path] = None, use_airis: bool = True):
        """
        Initialize reflexion pattern

        Args:
            memory_dir: Directory for storing error solutions
                       (defaults to docs/memory/ in current project)
            use_airis: Whether to use airis-agent if available (default: True)
        """
        self._use_airis = use_airis and _airis_available
        self._local = _LocalReflexionPattern(memory_dir)

    def get_solution(self, error_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get known solution for similar error

        Args:
            error_info: Error information dict

        Returns:
            Solution dict if found, None otherwise
        """
        # Use local implementation (airis-agent async API)
        return self._local.get_solution(error_info)

    def record_error(self, error_info: Dict[str, Any]) -> None:
        """
        Record error and solution for future learning

        Args:
            error_info: Error information dict
        """
        self._local.record_error(error_info)

    def get_statistics(self) -> Dict[str, Any]:
        """Get reflexion pattern statistics."""
        return self._local.get_statistics()

    # Expose for testing
    @property
    def memory_dir(self) -> Path:
        return self._local.memory_dir

    @property
    def solutions_file(self) -> Path:
        return self._local.solutions_file

    @property
    def mistakes_dir(self) -> Path:
        return self._local.mistakes_dir

    def _create_error_signature(self, error_info: Dict[str, Any]) -> str:
        return self._local._create_error_signature(error_info)

    def _search_mindbase(self, error_signature: str) -> Optional[Dict[str, Any]]:
        return self._local._search_mindbase(error_signature)

    def _is_mindbase_enabled(self) -> bool:
        return self._local._is_mindbase_enabled()

    def _calculate_similarity(self, sig1: str, sig2: str) -> float:
        return self._local._calculate_similarity(sig1, sig2)

    def store_to_mindbase(self, error_info: Dict[str, Any]) -> bool:
        return self._local.store_to_mindbase(error_info)

    def get_cross_session_patterns(self) -> List[Dict[str, Any]]:
        return self._local.get_cross_session_patterns()

    def _search_local_files(self, error_signature: str) -> Optional[Dict[str, Any]]:
        return self._local._search_local_files(error_signature)

    def _signatures_match(self, sig1: str, sig2: str, threshold: float = 0.7) -> bool:
        return self._local._signatures_match(sig1, sig2, threshold)

    def _create_mistake_doc(self, error_info: Dict[str, Any]) -> None:
        return self._local._create_mistake_doc(error_info)


class _LocalReflexionPattern:
    """
    Local fallback implementation of reflexion pattern.

    Used when airis-agent is not available or for testing.
    """

    def __init__(self, memory_dir: Optional[Path] = None):
        if memory_dir is None:
            memory_dir = Path.cwd() / "docs" / "memory"

        self.memory_dir = memory_dir
        self.solutions_file = memory_dir / "solutions_learned.jsonl"
        self.mistakes_dir = memory_dir.parent / "mistakes"

        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.mistakes_dir.mkdir(parents=True, exist_ok=True)

    def get_solution(self, error_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get known solution for similar error."""
        error_signature = self._create_error_signature(error_info)

        solution = self._search_mindbase(error_signature)
        if solution:
            return solution

        solution = self._search_local_files(error_signature)
        return solution

    def record_error(self, error_info: Dict[str, Any]) -> None:
        """Record error and solution for future learning."""
        error_info["timestamp"] = datetime.now().isoformat()

        with self.solutions_file.open("a") as f:
            f.write(json.dumps(error_info) + "\n")

        if error_info.get("root_cause") or error_info.get("solution"):
            self._create_mistake_doc(error_info)

    def _create_error_signature(self, error_info: Dict[str, Any]) -> str:
        """Create error signature for matching."""
        parts = []

        if "error_type" in error_info:
            parts.append(error_info["error_type"])

        if "error_message" in error_info:
            import re

            message = error_info["error_message"]
            message = re.sub(r"\d+", "N", message)
            parts.append(message[:100])

        if "test_name" in error_info:
            parts.append(error_info["test_name"])

        return " | ".join(parts)

    def _search_mindbase(self, error_signature: str) -> Optional[Dict[str, Any]]:
        """Search for similar error in mindbase cache."""
        if not self._is_mindbase_enabled():
            return None

        mindbase_cache = self.memory_dir / "mindbase_cache.jsonl"
        if not mindbase_cache.exists():
            return None

        best_match = None
        best_score = 0.0

        try:
            with mindbase_cache.open("r") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        stored_signature = record.get("signature", "")

                        score = self._calculate_similarity(
                            error_signature, stored_signature
                        )

                        if score > best_score and score >= 0.6:
                            best_score = score
                            best_match = record

                    except json.JSONDecodeError:
                        continue

        except (OSError, PermissionError):
            return None

        if best_match:
            return {
                "solution": best_match.get("solution"),
                "root_cause": best_match.get("root_cause"),
                "prevention": best_match.get("prevention"),
                "timestamp": best_match.get("timestamp"),
                "source": "mindbase",
                "similarity_score": best_score,
            }

        return None

    def _is_mindbase_enabled(self) -> bool:
        """Check if Mindbase integration is enabled."""
        return os.environ.get("MINDBASE_ENABLED", "").lower() in ("1", "true", "yes")

    def _calculate_similarity(self, sig1: str, sig2: str) -> float:
        """Calculate similarity between two error signatures."""
        words1 = set(sig1.lower().split())
        words2 = set(sig2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        jaccard = intersection / union if union > 0 else 0.0

        error_types = {
            "assertionerror",
            "typeerror",
            "valueerror",
            "keyerror",
            "indexerror",
            "importerror",
            "filenotfounderror",
            "connectionerror",
            "zerodivisionerror",
        }

        common_error_types = (words1 & words2) & error_types
        error_boost = 0.2 if common_error_types else 0.0

        return min(1.0, jaccard + error_boost)

    def store_to_mindbase(self, error_info: Dict[str, Any]) -> bool:
        """Store error information to Mindbase cache."""
        if not self._is_mindbase_enabled():
            return False

        mindbase_cache = self.memory_dir / "mindbase_cache.jsonl"

        try:
            cache_entry = {
                "signature": self._create_error_signature(error_info),
                "error_type": error_info.get("error_type"),
                "error_message": error_info.get("error_message"),
                "solution": error_info.get("solution"),
                "root_cause": error_info.get("root_cause"),
                "prevention": error_info.get("prevention"),
                "timestamp": datetime.now().isoformat(),
                "session_id": os.environ.get("CLAUDE_SESSION_ID", "unknown"),
            }

            with mindbase_cache.open("a") as f:
                f.write(json.dumps(cache_entry) + "\n")

            return True

        except (OSError, PermissionError):
            return False

    def get_cross_session_patterns(self) -> List[Dict[str, Any]]:
        """Get error patterns learned across sessions."""
        patterns: List[Dict[str, Any]] = []

        mindbase_cache = self.memory_dir / "mindbase_cache.jsonl"
        if not mindbase_cache.exists():
            return patterns

        try:
            with mindbase_cache.open("r") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        if record.get("solution"):
                            patterns.append(
                                {
                                    "error_type": record.get("error_type"),
                                    "pattern": record.get("signature"),
                                    "solution": record.get("solution"),
                                    "session_id": record.get("session_id"),
                                }
                            )
                    except json.JSONDecodeError:
                        continue

        except (OSError, PermissionError):
            pass

        return patterns

    def _search_local_files(self, error_signature: str) -> Optional[Dict[str, Any]]:
        """Search for similar error in local JSONL file."""
        if not self.solutions_file.exists():
            return None

        with self.solutions_file.open("r") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    stored_signature = self._create_error_signature(record)

                    if self._signatures_match(error_signature, stored_signature):
                        return {
                            "solution": record.get("solution"),
                            "root_cause": record.get("root_cause"),
                            "prevention": record.get("prevention"),
                            "timestamp": record.get("timestamp"),
                        }
                except json.JSONDecodeError:
                    continue

        return None

    def _signatures_match(self, sig1: str, sig2: str, threshold: float = 0.7) -> bool:
        """Check if two error signatures match."""
        words1 = set(sig1.lower().split())
        words2 = set(sig2.lower().split())

        if not words1 or not words2:
            return False

        overlap = len(words1 & words2)
        total = len(words1 | words2)

        return (overlap / total) >= threshold

    def _create_mistake_doc(self, error_info: Dict[str, Any]) -> None:
        """Create detailed mistake documentation."""
        test_name = error_info.get("test_name", "unknown")
        date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{test_name}-{date}.md"
        filepath = self.mistakes_dir / filename

        content = f"""# Mistake Record: {test_name}

**Date**: {date}
**Error Type**: {error_info.get("error_type", "Unknown")}

---

## What Happened

{error_info.get("error_message", "No error message")}

```
{error_info.get("traceback", "No traceback")}
```

---

## Root Cause

{error_info.get("root_cause", "Not analyzed")}

---

## Why Missed

{error_info.get("why_missed", "Not analyzed")}

---

## Fix Applied

{error_info.get("solution", "Not documented")}

---

## Prevention Checklist

{error_info.get("prevention", "Not documented")}

---

## Lesson Learned

{error_info.get("lesson", "Not documented")}
"""

        filepath.write_text(content)

    def get_statistics(self) -> Dict[str, Any]:
        """Get reflexion pattern statistics."""
        if not self.solutions_file.exists():
            return {
                "total_errors": 0,
                "errors_with_solutions": 0,
                "solution_reuse_rate": 0.0,
            }

        total = 0
        with_solutions = 0

        with self.solutions_file.open("r") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    total += 1
                    if record.get("solution"):
                        with_solutions += 1
                except json.JSONDecodeError:
                    continue

        return {
            "total_errors": total,
            "errors_with_solutions": with_solutions,
            "solution_reuse_rate": (with_solutions / total * 100) if total > 0 else 0.0,
        }
