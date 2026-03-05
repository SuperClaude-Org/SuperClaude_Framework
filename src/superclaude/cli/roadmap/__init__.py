"""Roadmap module -- ``superclaude roadmap`` CLI command.

Builds on the shared ``pipeline/`` foundation to orchestrate an 8-step
roadmap generation pipeline with adversarial variant generation, structured
debate, and merge.
"""

from .commands import roadmap_group

__all__ = ["roadmap_group"]
