"""Reflexion Memory System

Manages long-term learning from mistakes:
- Loads past failures and solutions
- Prevents recurrence of known errors
- Enables systematic improvement
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class ReflexionEntry:
    """Single reflexion (learning) entry"""

    def __init__(
        self,
        task: str,
        mistake: str,
        evidence: str,
        rule: str,
        fix: str,
        tests: List[str],
        status: str = "adopted",
        timestamp: Optional[str] = None
    ):
        self.task = task
        self.mistake = mistake
        self.evidence = evidence
        self.rule = rule
        self.fix = fix
        self.tests = tests
        self.status = status
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "ts": self.timestamp,
            "task": self.task,
            "mistake": self.mistake,
            "evidence": self.evidence,
            "rule": self.rule,
            "fix": self.fix,
            "tests": self.tests,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReflexionEntry":
        """Create from dictionary"""
        return cls(
            task=data["task"],
            mistake=data["mistake"],
            evidence=data["evidence"],
            rule=data["rule"],
            fix=data["fix"],
            tests=data["tests"],
            status=data.get("status", "adopted"),
            timestamp=data.get("ts")
        )


class ReflexionMemory:
    """Manages Reflexion Memory (learning from mistakes)"""

    def __init__(self, git_root: Path):
        self.git_root = git_root
        self.memory_path = git_root / "docs" / "memory" / "reflexion.jsonl"
        self.entries: List[ReflexionEntry] = []

    def load(self) -> Dict[str, Any]:
        """Load Reflexion Memory from disk"""
        if not self.memory_path.exists():
            # Create empty memory file
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            self.memory_path.touch()
            return {
                "total_entries": 0,
                "rules": [],
                "recent_mistakes": []
            }

        # Load entries
        self.entries = []
        with open(self.memory_path, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        self.entries.append(ReflexionEntry.from_dict(data))
                    except json.JSONDecodeError:
                        continue

        # Extract rules and recent mistakes
        rules = list(set(entry.rule for entry in self.entries if entry.status == "adopted"))
        recent_mistakes = [
            {
                "task": entry.task,
                "mistake": entry.mistake,
                "fix": entry.fix
            }
            for entry in sorted(self.entries, key=lambda e: e.timestamp, reverse=True)[:5]
        ]

        return {
            "total_entries": len(self.entries),
            "rules": rules,
            "recent_mistakes": recent_mistakes
        }

    def add_entry(self, entry: ReflexionEntry) -> None:
        """Add new reflexion entry"""
        self.entries.append(entry)

        # Append to JSONL file
        with open(self.memory_path, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def search_similar_mistakes(self, error_message: str) -> List[ReflexionEntry]:
        """Search for similar past mistakes"""
        # Simple keyword-based search (can be enhanced with semantic search)
        keywords = set(error_message.lower().split())
        similar = []

        for entry in self.entries:
            entry_keywords = set(entry.mistake.lower().split())
            # If >50% keyword overlap, consider similar
            overlap = len(keywords & entry_keywords) / len(keywords | entry_keywords)
            if overlap > 0.5:
                similar.append(entry)

        return sorted(similar, key=lambda e: e.timestamp, reverse=True)

    def get_rules(self) -> List[str]:
        """Get all adopted rules"""
        return list(set(
            entry.rule
            for entry in self.entries
            if entry.status == "adopted"
        ))

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_entries": len(self.entries),
            "adopted_rules": len(self.get_rules()),
            "total_tasks": len(set(entry.task for entry in self.entries))
        }
