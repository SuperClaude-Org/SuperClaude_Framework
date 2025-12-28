"""
PM Agent Core Module

Provides core functionality for PM Agent:
- Pre-execution confidence checking
- Post-implementation self-check protocol
- Reflexion error learning pattern
- Token budget management
"""

from .confidence import ConfidenceChecker
from .reflexion import ReflexionPattern
from .self_check import SelfCheckProtocol

__all__ = [
    "ConfidenceChecker",
    "SelfCheckProtocol",
    "ReflexionPattern",
]
