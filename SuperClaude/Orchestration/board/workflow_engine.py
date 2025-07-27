"""
Workflow Engine for Board-Based Orchestration System
Handles column transitions, business logic, and workflow automation
"""

from typing import Dict, List, Optional, Tuple, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

from .card_model import Card, CardStatus, CardPriority, CardType
from .resource_tracker import ResourceTracker, get_resource_tracker

class WorkflowEvent(Enum):
    """Workflow events that can trigger actions"""
    CARD_CREATED = "card_created"
    CARD_STARTED = "card_started"
    CARD_COMPLETED = "card_completed"
    CARD_FAILED = "card_failed"
    CARD_BLOCKED = "card_blocked"
    CARD_MOVED = "card_moved"
    RESOURCE_WARNING = "resource_warning"
    RESOURCE_CRITICAL = "resource_critical"

@dataclass
class WorkflowRule:
    """Rule for automatic workflow actions"""
    event: WorkflowEvent
    condition: Callable[[Card, Dict], bool]
    action: Callable[[Card, Dict], None]
    description: str
    enabled: bool = True

@dataclass
class WorkflowMetrics:
    """Metrics for workflow performance tracking"""
    cards_processed: int = 0
    average_processing_time: float = 0.0
    success_rate: float = 0.0
    blocked_cards: int = 0
    failed_cards: int = 0
    total_transitions: int = 0
    rule_executions: int = 0

class WorkflowEngine:
    """
    Workflow Engine for Board-Based Orchestration
    
    Manages card transitions, enforces business rules, and provides automation.
    Integrates with ResourceTracker for safety and capacity management.
    """
    
    def __init__(self, resource_tracker: Optional[ResourceTracker] = None):
        self.resource_tracker = resource_tracker or get_resource_tracker()
        self.cards: Dict[str, Card] = {}
        self.workflow_rules: List[WorkflowRule] = []
        self.metrics = WorkflowMetrics()
        self.event_handlers: Dict[WorkflowEvent, List[Callable]] = {}
        
        # Initialize default workflow rules
        self._initialize_default_rules()
    
    def add_card(self, card: Card) -> Tuple[bool, List[str]]:
        """Add a new card to the workflow"""
        # Check resource availability
        estimated_tokens = card.get_estimated_tokens()
        can_proceed, warnings = self.resource_tracker.check_resource_availability(
            card.id, estimated_tokens
        )
        
        if not can_proceed:
            return False, warnings
        
        # Add card to tracking
        self.cards[card.id] = card
        self.metrics.cards_processed += 1
        
        # Trigger workflow event
        self._trigger_event(WorkflowEvent.CARD_CREATED, card)
        
        return True, warnings
    
    def move_card(self, card_id: str, new_status: CardStatus, reason: str = "") -> Tuple[bool, str]:
        """Move card to new status with validation"""
        if card_id not in self.cards:
            return False, f"Card {card_id} not found"
        
        card = self.cards[card_id]
        old_status = card.status
        
        # Validate transition
        if not card.can_transition_to(new_status):
            return False, f"Invalid transition from {old_status.value} to {new_status.value}"
        
        # Handle resource allocation/deallocation
        success, message = self._handle_resource_transition(card, old_status, new_status)
        if not success:
            return False, message
        
        # Update card status
        card.update_status(new_status, reason)
        self.metrics.total_transitions += 1
        
        # Trigger appropriate workflow events
        if new_status == CardStatus.ACTIVE:
            self._trigger_event(WorkflowEvent.CARD_STARTED, card)
        elif new_status == CardStatus.DONE:
            self._trigger_event(WorkflowEvent.CARD_COMPLETED, card)
        elif new_status == CardStatus.FAILED:
            self._trigger_event(WorkflowEvent.CARD_FAILED, card)
        elif new_status == CardStatus.BLOCKED:
            self._trigger_event(WorkflowEvent.CARD_BLOCKED, card)
        
        self._trigger_event(WorkflowEvent.CARD_MOVED, card)
        
        return True, f"Card moved from {old_status.value} to {new_status.value}"
    
    def get_next_card(self, agent_name: Optional[str] = None) -> Optional[Card]:
        """Get the next card that should be processed"""
        available_cards = [
            card for card in self.cards.values()
            if card.status == CardStatus.BACKLOG
        ]
        
        if not available_cards:
            return None
        
        # Check resource capacity
        capacity = self.resource_tracker.get_available_capacity()
        if capacity["active_cards"] <= 0:
            return None
        
        # Sort by priority and creation time
        available_cards.sort(
            key=lambda c: (
                c.priority.value,  # Higher priority first (enum ordering)
                c.created_at       # Older cards first
            ),
            reverse=True
        )
        
        # Filter by agent capability if specified
        if agent_name:
            suitable_cards = [
                card for card in available_cards
                if self._is_card_suitable_for_agent(card, agent_name)
            ]
            if suitable_cards:
                available_cards = suitable_cards
        
        return available_cards[0] if available_cards else None
    
    def get_cards_by_status(self, status: CardStatus) -> List[Card]:
        """Get all cards with specific status"""
        return [card for card in self.cards.values() if card.status == status]
    
    def get_active_cards(self) -> List[Card]:
        """Get all currently active cards"""
        return self.get_cards_by_status(CardStatus.ACTIVE)
    
    def get_blocked_cards(self) -> List[Card]:
        """Get all blocked cards"""
        return self.get_cards_by_status(CardStatus.BLOCKED)
    
    def process_automatic_transitions(self) -> List[str]:
        """Process any automatic card transitions based on rules and resource management"""
        actions_taken = []
        
        for card in self.cards.values():
            # Check for graceful handoff triggers first
            if card.status == CardStatus.ACTIVE:
                handoff_action = self._check_graceful_handoff(card)
                if handoff_action:
                    actions_taken.append(handoff_action)
                    continue  # Skip other checks if handoff triggered
            
            # Check for automatic transitions
            action = self._check_automatic_transitions(card)
            if action:
                actions_taken.append(action)
        
        return actions_taken
    
    def update_card_metrics(self, card_id: str, **metrics) -> bool:
        """Update metrics for a specific card"""
        if card_id not in self.cards:
            return False
        
        card = self.cards[card_id]
        card.update_metrics(**metrics)
        
        # Check for resource violations
        if 'token_usage' in metrics:
            self.resource_tracker.check_token_usage(metrics['token_usage'], card_id)
        
        return True
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get comprehensive workflow status"""
        status_counts = {}
        for status in CardStatus:
            status_counts[status.value] = len(self.get_cards_by_status(status))
        
        resource_status = self.resource_tracker.get_resource_status()
        
        # Calculate processing times
        active_cards = self.get_active_cards()
        processing_times = []
        for card in active_cards:
            if card.started_at:
                elapsed = (datetime.now() - card.started_at).total_seconds()
                processing_times.append(elapsed)
        
        return {
            "card_counts": status_counts,
            "total_cards": len(self.cards),
            "resource_status": resource_status,
            "metrics": {
                "cards_processed": self.metrics.cards_processed,
                "average_processing_time": self.metrics.average_processing_time,
                "success_rate": self.metrics.success_rate,
                "total_transitions": self.metrics.total_transitions,
                "rule_executions": self.metrics.rule_executions
            },
            "active_processing_times": processing_times,
            "recommendations": self.resource_tracker.get_recommendations()
        }
    
    def add_workflow_rule(self, rule: WorkflowRule) -> None:
        """Add a custom workflow rule"""
        self.workflow_rules.append(rule)
    
    def remove_workflow_rule(self, description: str) -> bool:
        """Remove a workflow rule by description"""
        original_length = len(self.workflow_rules)
        self.workflow_rules = [r for r in self.workflow_rules if r.description != description]
        return len(self.workflow_rules) < original_length
    
    def pause_card(self, card_id: str, reason: str = "User requested") -> Tuple[bool, str]:
        """Pause an active card"""
        if card_id not in self.cards:
            return False, f"Card {card_id} not found"
        
        card = self.cards[card_id]
        if card.status != CardStatus.ACTIVE:
            return False, f"Card {card_id} is not active"
        
        # Move to blocked status
        return self.move_card(card_id, CardStatus.BLOCKED, f"Paused: {reason}")
    
    def resume_card(self, card_id: str, reason: str = "User requested") -> Tuple[bool, str]:
        """Resume a blocked card"""
        if card_id not in self.cards:
            return False, f"Card {card_id} not found"
        
        card = self.cards[card_id]
        if card.status != CardStatus.BLOCKED:
            return False, f"Card {card_id} is not blocked"
        
        # Check if we can resume (resource availability)
        estimated_tokens = card.get_estimated_tokens() - card.metrics.token_usage
        can_proceed, warnings = self.resource_tracker.check_resource_availability(
            card_id, estimated_tokens
        )
        
        if not can_proceed:
            return False, f"Cannot resume: {'; '.join(warnings)}"
        
        # Move back to active
        return self.move_card(card_id, CardStatus.ACTIVE, f"Resumed: {reason}")
    
    def force_complete_card(self, card_id: str, reason: str = "Force completed") -> Tuple[bool, str]:
        """Force complete a card regardless of status"""
        if card_id not in self.cards:
            return False, f"Card {card_id} not found"
        
        card = self.cards[card_id]
        old_status = card.status
        
        # Release resources if active
        if old_status == CardStatus.ACTIVE:
            self.resource_tracker.release_card_resources(card_id)
        
        # Force to done status
        card.update_status(CardStatus.DONE, f"Force completed: {reason}")
        self._trigger_event(WorkflowEvent.CARD_COMPLETED, card)
        
        return True, f"Card force completed from {old_status.value}"
    
    def _handle_resource_transition(self, card: Card, old_status: CardStatus, 
                                  new_status: CardStatus) -> Tuple[bool, str]:
        """Handle resource allocation/deallocation during transitions"""
        
        # Allocate resources when moving to ACTIVE
        if new_status == CardStatus.ACTIVE and old_status != CardStatus.ACTIVE:
            if not self.resource_tracker.allocate_card_resources(card.id):
                return False, "Cannot allocate resources for active card"
        
        # Release resources when leaving ACTIVE
        elif old_status == CardStatus.ACTIVE and new_status != CardStatus.ACTIVE:
            final_metrics = {
                'token_usage': card.metrics.token_usage,
                'tool_calls': card.metrics.tool_calls
            }
            self.resource_tracker.release_card_resources(card.id, final_metrics)
        
        return True, "Resource transition successful"
    
    def _is_card_suitable_for_agent(self, card: Card, agent_name: str) -> bool:
        """Check if a card is suitable for a specific agent"""
        # If card has persona preference, match it
        if card.context.persona_name:
            return agent_name.startswith(card.context.persona_name)
        
        # Otherwise, match based on card type and agent capabilities
        agent_card_type_map = {
            "architect": [CardType.ANALYSIS, CardType.IMPLEMENTATION],
            "security": [CardType.ANALYSIS, CardType.IMPLEMENTATION],
            "frontend": [CardType.IMPLEMENTATION, CardType.TESTING],
            "backend": [CardType.IMPLEMENTATION, CardType.TESTING],
            "analyzer": [CardType.ANALYSIS, CardType.DEBUGGING],
            "qa": [CardType.TESTING, CardType.ANALYSIS],
            "performance": [CardType.ANALYSIS, CardType.IMPLEMENTATION],
            "refactorer": [CardType.REFACTORING, CardType.IMPLEMENTATION]
        }
        
        for agent_type, suitable_types in agent_card_type_map.items():
            if agent_name.startswith(agent_type) and card.card_type in suitable_types:
                return True
        
        return True  # Default: any agent can handle any card
    
    def _check_automatic_transitions(self, card: Card) -> Optional[str]:
        """Check if card should automatically transition"""
        
        # Check for stuck active cards (timeout)
        if card.status == CardStatus.ACTIVE and card.started_at:
            elapsed = (datetime.now() - card.started_at).total_seconds()
            if elapsed > 600:  # 10 minutes timeout
                self.move_card(card.id, CardStatus.BLOCKED, "Processing timeout")
                return f"Card {card.id} blocked due to timeout"
        
        # Check for resource violations
        if card.status == CardStatus.ACTIVE:
            if card.metrics.error_count > 5:
                self.move_card(card.id, CardStatus.FAILED, "Too many errors")
                return f"Card {card.id} failed due to repeated errors"
        
        return None
    
    def _check_graceful_handoff(self, card: Card) -> Optional[str]:
        """Check if graceful handoff should be triggered for active card"""
        try:
            # Check with resource tracker if handoff is needed
            should_handoff, reason = self.resource_tracker.check_handoff_trigger(card.id)
            
            if should_handoff:
                # Trigger graceful handoff event for board manager to handle
                self._trigger_event(WorkflowEvent.RESOURCE_CRITICAL, card)
                card.add_warning(f"Graceful handoff triggered: {reason}")
                return f"Card {card.id} triggered graceful handoff: {reason}"
            
        except Exception as e:
            card.add_error(f"Error checking handoff trigger: {e}")
        
        return None
    
    def _trigger_event(self, event: WorkflowEvent, card: Card) -> None:
        """Trigger workflow event and execute applicable rules"""
        # Execute workflow rules
        for rule in self.workflow_rules:
            if rule.enabled and rule.event == event:
                try:
                    context = {"workflow": self, "resource_tracker": self.resource_tracker}
                    if rule.condition(card, context):
                        rule.action(card, context)
                        self.metrics.rule_executions += 1
                except Exception as e:
                    # Log rule execution error
                    card.add_error(f"Workflow rule error: {e}")
        
        # Trigger event handlers
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(card, self)
                except Exception as e:
                    card.add_error(f"Event handler error: {e}")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default workflow rules"""
        
        # Auto-assign high priority cards
        def assign_high_priority_condition(card: Card, context: Dict) -> bool:
            return card.priority == CardPriority.CRITICAL and not card.assigned_agent
        
        def assign_high_priority_action(card: Card, context: Dict) -> None:
            # Auto-assign to appropriate agent based on card type
            if card.context.persona_name:
                card.assign_agent(f"{card.context.persona_name}-agent")
        
        self.add_workflow_rule(WorkflowRule(
            event=WorkflowEvent.CARD_CREATED,
            condition=assign_high_priority_condition,
            action=assign_high_priority_action,
            description="Auto-assign critical priority cards"
        ))
        
        # Resource warning rule
        def resource_warning_condition(card: Card, context: Dict) -> bool:
            status = context["resource_tracker"].get_resource_status()
            return status["alert_level"] in ["orange", "red", "critical"]
        
        def resource_warning_action(card: Card, context: Dict) -> None:
            status = context["resource_tracker"].get_resource_status()
            card.add_warning(f"Resource alert: {status['alert_level']}")
        
        self.add_workflow_rule(WorkflowRule(
            event=WorkflowEvent.CARD_STARTED,
            condition=resource_warning_condition,
            action=resource_warning_action,
            description="Warn about resource pressure on card start"
        ))
        
        # Auto-complete review cards
        def auto_complete_condition(card: Card, context: Dict) -> bool:
            return (card.status == CardStatus.REVIEW and 
                   len(card.result.errors) == 0 and
                   card.result.output)
        
        def auto_complete_action(card: Card, context: Dict) -> None:
            context["workflow"].move_card(card.id, CardStatus.DONE, "Auto-completed: no errors found")
        
        self.add_workflow_rule(WorkflowRule(
            event=WorkflowEvent.CARD_MOVED,
            condition=auto_complete_condition,
            action=auto_complete_action,
            description="Auto-complete review cards with no errors"
        ))
    
    def add_event_handler(self, event: WorkflowEvent, handler: Callable) -> None:
        """Add an event handler for workflow events"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def remove_event_handler(self, event: WorkflowEvent, handler: Callable) -> bool:
        """Remove an event handler"""
        if event in self.event_handlers and handler in self.event_handlers[event]:
            self.event_handlers[event].remove(handler)
            return True
        return False