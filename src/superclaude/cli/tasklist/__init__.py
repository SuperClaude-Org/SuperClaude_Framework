"""Tasklist module -- ``superclaude tasklist`` CLI command.

Provides tasklist validation against upstream roadmaps using the shared
``pipeline/`` foundation. Validates deliverable coverage, signature
preservation, traceability ID validity, and dependency chain correctness.
"""

def __getattr__(name: str):
    if name == "tasklist_group":
        from .commands import tasklist_group
        return tasklist_group
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["tasklist_group"]
