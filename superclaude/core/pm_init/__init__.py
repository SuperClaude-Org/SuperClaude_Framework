"""PM Mode Initialization System

Auto-initializes PM Mode as default with:
- Context Contract generation
- Reflexion Memory loading
- Lightweight configuration scanning
"""

from .init_hook import initialize_pm_mode
from .context_contract import ContextContract
from .reflexion_memory import ReflexionMemory

__all__ = ["initialize_pm_mode", "ContextContract", "ReflexionMemory"]
