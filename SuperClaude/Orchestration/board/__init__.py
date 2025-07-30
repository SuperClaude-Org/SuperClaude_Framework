"""
Board-Based Orchestration System - Phase 1 Implementation
Foundation infrastructure for safe multi-agent operations
"""

from .card_model import (
    Card, CardStatus, CardPriority, CardType, CardFactory,
    CardContext, CardResult, CardMetrics
)
from .resource_tracker import (
    ResourceTracker, ResourceLimits, ResourceAlert,
    get_resource_tracker, reset_resource_tracker
)
from .workflow_engine import WorkflowEngine, WorkflowEvent, WorkflowRule
from .board_manager import (
    BoardManager, BoardConfig, BoardState,
    get_board_manager, reset_board_manager
)

__all__ = [
    # Card Model
    'Card', 'CardStatus', 'CardPriority', 'CardType', 'CardFactory',
    'CardContext', 'CardResult', 'CardMetrics',
    
    # Resource Tracker
    'ResourceTracker', 'ResourceLimits', 'ResourceAlert',
    'get_resource_tracker', 'reset_resource_tracker',
    
    # Workflow Engine
    'WorkflowEngine', 'WorkflowEvent', 'WorkflowRule',
    
    # Board Manager
    'BoardManager', 'BoardConfig', 'BoardState',
    'get_board_manager', 'reset_board_manager'
]

__version__ = "2.0.0-phase1"
__status__ = "Foundation Implementation Complete"