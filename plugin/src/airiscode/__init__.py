"""
SuperClaude Framework

AI-enhanced development framework for Claude Code.
Provides pytest plugin for enhanced testing and optional skills system.
"""

__version__ = "0.4.0"
__author__ = "Kazuki Nakai"

# Expose main components
from .pm_agent.confidence import ConfidenceChecker
from .pm_agent.self_check import SelfCheckProtocol
from .pm_agent.reflexion import ReflexionPattern

__all__ = [
    "ConfidenceChecker",
    "SelfCheckProtocol",
    "ReflexionPattern",
    "__version__",
]
