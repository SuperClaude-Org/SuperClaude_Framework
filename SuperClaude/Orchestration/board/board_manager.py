"""
Board Manager for Board-Based Orchestration System
Main orchestration component that coordinates all board operations
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
import json
import uuid

from .card_model import (
    Card, CardStatus, CardPriority, CardType, CardFactory, 
    CardContext, CardResult, CardMetrics
)
from .resource_tracker import ResourceTracker, ResourceLimits, get_resource_tracker
from .workflow_engine import WorkflowEngine, WorkflowEvent

# Import persona and prompt generators for sub-agent creation
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'SubAgents'))
from core.persona_parser import PersonaParser, PersonaDefinition
from core.prompt_generator import PromptGenerator, SubAgentConfig

@dataclass
class BoardConfig:
    """Configuration for the board manager with graceful handoff support"""
    max_active_cards: int = 3
    max_token_budget: int = 20000
    auto_assign_agents: bool = True
    enable_automatic_transitions: bool = True
    persist_state: bool = True
    storage_path: str = "SuperClaude/Orchestration/storage"
    fallback_to_personas: bool = True  # Fallback to documentation personas if board fails
    enable_graceful_handoff: bool = True  # Enable graceful handoff protocol
    compression_threshold: float = 0.60  # Auto-enable --uc mode at 60% usage

@dataclass
class BoardState:
    """Current state of the board"""
    cards: Dict[str, Card] = field(default_factory=dict)
    active_agents: Dict[str, str] = field(default_factory=dict)  # agent_id -> card_id
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

class BoardManager:
    """
    Board Manager - Main Orchestration Component
    
    Coordinates card lifecycle, resource management, and sub-agent creation.
    Provides high-level API for the board-based orchestration system.
    """
    
    def __init__(self, 
                 config: Optional[BoardConfig] = None,
                 resource_limits: Optional[ResourceLimits] = None):
        
        self.config = config or BoardConfig()
        
        # Initialize core components
        self.resource_tracker = ResourceTracker(resource_limits)
        self.workflow_engine = WorkflowEngine(self.resource_tracker)
        self.board_state = BoardState()
        
        # Initialize persona system for sub-agent creation
        self.persona_parser = None
        self.prompt_generator = PromptGenerator()
        self.personas: Dict[str, PersonaDefinition] = {}
        
        # Board status
        self.is_active = True
        self.error_count = 0
        self.last_error = None
        
        # Storage paths
        self.storage_path = Path(self.config.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize persona parser
        self._initialize_persona_system()
        
        # Load persisted state if available
        if self.config.persist_state:
            self._load_board_state()
    
    def create_card_from_request(self, 
                                request: str,
                                persona_name: Optional[str] = None,
                                priority: CardPriority = CardPriority.MEDIUM,
                                user_flags: Optional[List[str]] = None,
                                file_paths: Optional[List[str]] = None) -> Tuple[bool, str, Optional[Card]]:
        """
        Create a new card from a user request.
        This is the main entry point for the board system.
        """
        try:
            # Create card using factory
            card = CardFactory.create_from_request(
                request=request,
                persona_name=persona_name,
                priority=priority,
                user_flags=user_flags,
                file_paths=file_paths
            )
            
            # Add to workflow engine
            success, warnings = self.workflow_engine.add_card(card)
            
            if not success:
                return False, f"Cannot create card: {'; '.join(warnings)}", None
            
            # Store in board state
            self.board_state.cards[card.id] = card
            self.board_state.last_activity = datetime.now()
            
            # Auto-assign agent if enabled
            if self.config.auto_assign_agents and persona_name:
                self._assign_agent_to_card(card, persona_name)
            
            # Persist state
            if self.config.persist_state:
                self._save_board_state()
            
            message = f"Card {card.id} created: {card.title}"
            if warnings:
                message += f" (Warnings: {'; '.join(warnings)})"
                
            return True, message, card
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            return False, f"Error creating card: {e}", None
    
    def start_card(self, card_id: str) -> Tuple[bool, str]:
        """Start processing a card"""
        if card_id not in self.board_state.cards:
            return False, f"Card {card_id} not found"
        
        card = self.board_state.cards[card_id]
        
        # Move card to active status
        success, message = self.workflow_engine.move_card(card_id, CardStatus.ACTIVE, "Started by user")
        
        if success:
            self.board_state.last_activity = datetime.now()
            if self.config.persist_state:
                self._save_board_state()
        
        return success, message
    
    def pause_card(self, card_id: str, reason: str = "User requested") -> Tuple[bool, str]:
        """Pause an active card"""
        success, message = self.workflow_engine.pause_card(card_id, reason)
        
        if success:
            self.board_state.last_activity = datetime.now()
            if self.config.persist_state:
                self._save_board_state()
        
        return success, message
    
    def complete_card(self, card_id: str, result: Optional[CardResult] = None) -> Tuple[bool, str]:
        """Complete a card with optional result data"""
        if card_id not in self.board_state.cards:
            return False, f"Card {card_id} not found"
        
        card = self.board_state.cards[card_id]
        
        # Update result if provided
        if result:
            card.result = result
        
        # Move to review status first for validation
        success, message = self.workflow_engine.move_card(card_id, CardStatus.REVIEW, "Completed")
        
        if success:
            # Release agent assignment
            if card.assigned_agent:
                self._release_agent(card.assigned_agent)
            
            self.board_state.last_activity = datetime.now()
            if self.config.persist_state:
                self._save_board_state()
        
        return success, message
    
    def fail_card(self, card_id: str, error: str) -> Tuple[bool, str]:
        """Mark a card as failed"""
        if card_id not in self.board_state.cards:
            return False, f"Card {card_id} not found"
        
        card = self.board_state.cards[card_id]
        card.add_error(error)
        
        success, message = self.workflow_engine.move_card(card_id, CardStatus.FAILED, f"Failed: {error}")
        
        if success:
            # Release agent assignment
            if card.assigned_agent:
                self._release_agent(card.assigned_agent)
            
            self.board_state.last_activity = datetime.now()
            if self.config.persist_state:
                self._save_board_state()
        
        return success, message
    
    def get_next_task(self, agent_name: Optional[str] = None) -> Optional[Card]:
        """Get the next task that should be processed"""
        return self.workflow_engine.get_next_card(agent_name)
    
    def get_board_status(self) -> Dict[str, Any]:
        """Get comprehensive board status"""
        workflow_status = self.workflow_engine.get_workflow_status()
        
        # Add board-specific information
        board_info = {
            "session_id": self.board_state.session_id,
            "session_duration": (datetime.now() - self.board_state.created_at).total_seconds(),
            "last_activity": self.board_state.last_activity.isoformat(),
            "is_active": self.is_active,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "config": {
                "max_active_cards": self.config.max_active_cards,
                "max_token_budget": self.config.max_token_budget,
                "auto_assign_agents": self.config.auto_assign_agents,
                "fallback_enabled": self.config.fallback_to_personas
            },
            "active_agents": dict(self.board_state.active_agents),
            "available_personas": list(self.personas.keys())
        }
        
        return {
            "board": board_info,
            "workflow": workflow_status
        }
    
    def get_card(self, card_id: str) -> Optional[Card]:
        """Get a specific card"""
        return self.board_state.cards.get(card_id)
    
    def get_cards_by_status(self, status: CardStatus) -> List[Card]:
        """Get all cards with specific status"""
        return [card for card in self.board_state.cards.values() if card.status == status]
    
    def create_sub_agent(self, persona_name: str) -> Tuple[bool, str, Optional[SubAgentConfig]]:
        """Create a sub-agent configuration for a persona"""
        try:
            if persona_name not in self.personas:
                return False, f"Persona {persona_name} not found", None
            
            persona = self.personas[persona_name]
            
            # Generate sub-agent configuration
            from core.prompt_generator import SubAgentGenerator
            generator = SubAgentGenerator()
            agent_config = generator.generate_agent_config(persona)
            
            return True, f"Sub-agent {agent_config.name} created", agent_config
            
        except Exception as e:
            return False, f"Error creating sub-agent: {e}", None
    
    def process_automatic_transitions(self) -> List[str]:
        """Process any automatic card transitions"""
        if not self.config.enable_automatic_transitions:
            return []
        
        actions = self.workflow_engine.process_automatic_transitions()
        
        if actions and self.config.persist_state:
            self._save_board_state()
        
        return actions
    
    def check_graceful_handoff(self, card_id: str) -> Tuple[bool, str]:
        """Check if graceful handoff should be triggered for a card"""
        if not self.config.enable_graceful_handoff:
            return False, "Graceful handoff disabled"
        
        if card_id not in self.board_state.cards:
            return False, f"Card {card_id} not found"
        
        # Check with resource tracker
        should_handoff, reason = self.resource_tracker.check_handoff_trigger(card_id)
        
        return should_handoff, reason
    
    def execute_graceful_handoff(self, card_id: str) -> Tuple[bool, str, Optional[Card]]:
        """Execute graceful handoff by compressing context and creating new agent"""
        if not self.config.enable_graceful_handoff:
            return False, "Graceful handoff disabled", None
        
        if card_id not in self.board_state.cards:
            return False, f"Card {card_id} not found", None
        
        try:
            old_card = self.board_state.cards[card_id]
            
            # Prepare handoff operation
            if not self.resource_tracker.prepare_handoff(card_id):
                return False, "Cannot prepare handoff - insufficient buffer or handoff in progress", None
            
            # Compress context
            compressed_context = self._compress_card_context(old_card)
            
            # Create new card with compressed context
            new_card = self._create_handoff_card(old_card, compressed_context)
            
            # Add new card to tracking
            self.board_state.cards[new_card.id] = new_card
            self.workflow_engine.cards[new_card.id] = new_card
            
            # Transfer agent assignment
            if old_card.assigned_agent:
                new_card.assign_agent(old_card.assigned_agent)
                self.board_state.active_agents[old_card.assigned_agent] = new_card.id
            
            # Complete old card with handoff notice
            old_card.result.output = f"Context handed off to card {new_card.id} for resource optimization"
            old_card.add_warning("Card context compressed and handed off due to resource pressure")
            self.workflow_engine.move_card(card_id, CardStatus.DONE, "Graceful handoff completed")
            
            # Complete handoff operation
            self.resource_tracker.complete_handoff(card_id, new_card.id)
            
            # Persist state
            if self.config.persist_state:
                self._save_board_state()
            
            return True, f"Graceful handoff completed: {card_id} → {new_card.id}", new_card
            
        except Exception as e:
            # Reset handoff state on error
            self.resource_tracker.complete_handoff(card_id, "")
            return False, f"Graceful handoff failed: {e}", None
    
    def _compress_card_context(self, card: Card) -> str:
        """Compress card context for handoff using --uc style compression"""
        # Use SuperClaude's symbol system for compression
        compressed = f"""🎯 Task: {card.title}
📋 Status: {card.status.value} → Continue from here
⚡ Progress: {len(card.result.artifacts)} artifacts created
🔍 Context: {card.context.original_request[:200]}...
📊 Metrics: {card.metrics.token_usage}t/{card.metrics.tool_calls}c
"""
        
        # Add key context elements
        if card.context.file_paths:
            compressed += f"📁 Files: {', '.join(card.context.file_paths[:5])}\n"
        
        if card.result.errors:
            compressed += f"⚠️ Errors: {len(card.result.errors)} (resolved)\n"
        
        if card.result.next_steps:
            compressed += f"→ Next: {', '.join(card.result.next_steps[:3])}\n"
        
        # Preserve essential flags and persona
        if card.context.persona_name:
            compressed += f"👤 Persona: {card.context.persona_name}\n"
        
        if card.context.user_flags:
            compressed += f"🏃 Flags: {' '.join(card.context.user_flags)}\n"
        
        return compressed.strip()
    
    def _create_handoff_card(self, old_card: Card, compressed_context: str) -> Card:
        """Create new card for handoff with compressed context"""
        # Create new card maintaining essential context
        new_card = Card(
            title=f"Continue: {old_card.title}",
            description=compressed_context,
            priority=old_card.priority,
            card_type=old_card.card_type,
            created_by="handoff_system"
        )
        
        # Preserve critical context elements
        new_card.context.original_request = compressed_context
        new_card.context.persona_name = old_card.context.persona_name
        new_card.context.user_flags = old_card.context.user_flags + ["--uc"]  # Auto-enable compression
        new_card.context.file_paths = old_card.context.file_paths
        new_card.context.parent_card_id = old_card.id
        
        # Mark as handoff continuation
        new_card.metadata["handoff_from"] = old_card.id
        new_card.metadata["handoff_timestamp"] = datetime.now().isoformat()
        new_card.metadata["compression_ratio"] = len(compressed_context) / len(old_card.context.original_request)
        
        # Set status to active to continue work
        new_card.status = CardStatus.ACTIVE
        new_card.started_at = datetime.now()
        
        return new_card
    
    def emergency_shutdown(self, reason: str) -> None:
        """Emergency shutdown of the board system"""
        self.is_active = False
        self.resource_tracker.force_emergency_mode(reason)
        
        # Pause all active cards
        active_cards = self.get_cards_by_status(CardStatus.ACTIVE)
        for card in active_cards:
            self.workflow_engine.pause_card(card.id, f"Emergency shutdown: {reason}")
        
        if self.config.persist_state:
            self._save_board_state()
    
    def recover_from_emergency(self) -> Tuple[bool, str]:
        """Attempt to recover from emergency mode"""
        if not self.is_active:
            return False, "Board is not active"
        
        # Reset resource tracker emergency mode
        self.resource_tracker.reset_emergency_mode()
        
        # Check if it's safe to proceed
        resource_status = self.resource_tracker.get_resource_status()
        if resource_status["emergency_mode"]:
            return False, "Still in emergency mode - resource conditions not safe"
        
        return True, "Recovered from emergency mode"
    
    def fallback_to_personas(self, request: str) -> Tuple[bool, str]:
        """Fallback to using documentation personas if board fails"""
        if not self.config.fallback_to_personas:
            return False, "Fallback to personas is disabled"
        
        try:
            # This would integrate with the existing SuperClaude persona system
            # For now, return a simulation of the fallback
            return True, f"Fallback executed for request: {request[:50]}..."
            
        except Exception as e:
            return False, f"Fallback failed: {e}"
    
    def cleanup_old_cards(self, max_age_hours: int = 24) -> int:
        """Clean up old completed cards"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        cards_to_remove = []
        for card_id, card in self.board_state.cards.items():
            if (card.status in [CardStatus.DONE, CardStatus.FAILED] and 
                card.completed_at and card.completed_at < cutoff):
                cards_to_remove.append(card_id)
        
        for card_id in cards_to_remove:
            del self.board_state.cards[card_id]
        
        if cards_to_remove and self.config.persist_state:
            self._save_board_state()
        
        return len(cards_to_remove)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the board"""
        completed_cards = self.get_cards_by_status(CardStatus.DONE)
        failed_cards = self.get_cards_by_status(CardStatus.FAILED)
        
        if not completed_cards and not failed_cards:
            return {"error": "No completed cards to analyze"}
        
        total_cards = len(completed_cards) + len(failed_cards)
        success_rate = len(completed_cards) / total_cards if total_cards > 0 else 0
        
        # Calculate average processing time
        processing_times = []
        for card in completed_cards:
            if card.started_at and card.completed_at:
                duration = (card.completed_at - card.started_at).total_seconds()
                processing_times.append(duration)
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Token usage statistics
        token_usage = [card.metrics.token_usage for card in completed_cards if card.metrics.token_usage > 0]
        avg_token_usage = sum(token_usage) / len(token_usage) if token_usage else 0
        
        return {
            "total_cards_processed": total_cards,
            "success_rate": success_rate,
            "average_processing_time": avg_processing_time,
            "average_token_usage": avg_token_usage,
            "current_session_duration": (datetime.now() - self.board_state.created_at).total_seconds(),
            "resource_utilization": self.resource_tracker.get_resource_status()
        }
    
    def _initialize_persona_system(self) -> None:
        """Initialize the persona parsing system"""
        try:
            # Find PERSONAS.md file
            personas_path = None
            search_paths = [
                Path(__file__).parent.parent.parent / "Core" / "PERSONAS.md",
                Path.home() / ".claude" / "PERSONAS.md"
            ]
            
            for path in search_paths:
                if path.exists():
                    personas_path = path
                    break
            
            if personas_path:
                self.persona_parser = PersonaParser(personas_path)
                self.personas = self.persona_parser.parse_all_personas()
            else:
                # Create minimal fallback personas
                self.personas = self._create_fallback_personas()
                
        except Exception as e:
            self.personas = self._create_fallback_personas()
            self.last_error = f"Persona system initialization error: {e}"
    
    def _create_fallback_personas(self) -> Dict[str, PersonaDefinition]:
        """Create minimal fallback personas if parsing fails"""
        from core.persona_parser import PersonaDefinition
        
        fallback_personas = {
            "general": PersonaDefinition(
                name="general",
                identity="General purpose assistant",
                domain="general development",
                priority_hierarchy=["quality", "speed"],
                core_principles=["Help the user effectively"],
                mcp_preferences={},
                quality_standards={},
                auto_triggers=[],
                optimized_commands=[]
            )
        }
        
        return fallback_personas
    
    def _assign_agent_to_card(self, card: Card, persona_name: str) -> bool:
        """Assign an agent to a card"""
        agent_id = f"{persona_name}-agent-{card.id[:4]}"
        
        card.assign_agent(agent_id)
        self.board_state.active_agents[agent_id] = card.id
        
        return True
    
    def _release_agent(self, agent_id: str) -> None:
        """Release an agent assignment"""
        if agent_id in self.board_state.active_agents:
            del self.board_state.active_agents[agent_id]
    
    def _save_board_state(self) -> None:
        """Save board state to persistent storage"""
        try:
            state_file = self.storage_path / "board_state.json"
            
            # Convert board state to serializable format
            state_data = {
                "session_id": self.board_state.session_id,
                "created_at": self.board_state.created_at.isoformat(),
                "last_activity": self.board_state.last_activity.isoformat(),
                "cards": {card_id: card.to_dict() for card_id, card in self.board_state.cards.items()},
                "active_agents": dict(self.board_state.active_agents)
            }
            
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
                
        except Exception as e:
            self.last_error = f"Error saving board state: {e}"
    
    def _load_board_state(self) -> None:
        """Load board state from persistent storage"""
        try:
            state_file = self.storage_path / "board_state.json"
            
            if not state_file.exists():
                return
            
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            # Restore board state
            self.board_state.session_id = state_data.get("session_id", self.board_state.session_id)
            self.board_state.created_at = datetime.fromisoformat(state_data["created_at"])
            self.board_state.last_activity = datetime.fromisoformat(state_data["last_activity"])
            self.board_state.active_agents = state_data.get("active_agents", {})
            
            # Restore cards
            for card_id, card_data in state_data.get("cards", {}).items():
                card = Card.from_dict(card_data)
                self.board_state.cards[card_id] = card
                self.workflow_engine.cards[card_id] = card
                
        except Exception as e:
            self.last_error = f"Error loading board state: {e}"

# Global board manager instance
_global_board_manager: Optional[BoardManager] = None

def get_board_manager(config: Optional[BoardConfig] = None) -> BoardManager:
    """Get the global board manager instance"""
    global _global_board_manager
    if _global_board_manager is None:
        _global_board_manager = BoardManager(config)
    return _global_board_manager

def reset_board_manager(config: Optional[BoardConfig] = None) -> BoardManager:
    """Reset the global board manager with new configuration"""
    global _global_board_manager
    _global_board_manager = BoardManager(config)
    return _global_board_manager