"""Project Context Management

Detects and manages project-specific configuration:
- Context Contract (project rules)
- Project structure detection
- Initialization
"""

from .contract import ContextContract
from .init import initialize_context

__all__ = ["ContextContract", "initialize_context"]
