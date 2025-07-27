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

from .card_model import TaskCard, CardStatus
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
    cards: Dict[str, TaskCard] = field(default_factory=dict)
    active_agents: Dict[str, str] = field(default_factory=dict)  # agent_id -> card_id
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    columns: List[CardStatus] = field(default_factory=lambda: [
        CardStatus.BACKLOG,
        CardStatus.TODO,
        CardStatus.IN_PROGRESS,
        CardStatus.INTEGRATE,
        CardStatus.REVIEW,
        CardStatus.DONE,
        CardStatus.FAILED,
        CardStatus.BLOCKED
    ])

class BoardManager:
    """
    Board Manager - Main Orchestration Component
    
    Coordinates card lifecycle, resource management, and sub-agent creation.
    Provides high-level API for the board-based orchestration system.
    Integrates with Phase 2 components for visualization and error recovery.
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
        self.columns = self.board_state.columns
        
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
                                priority: str = 'medium',
                                user_flags: Optional[List[str]] = None,
                                file_paths: Optional[List[str]] = None) -> Tuple[bool, str, Optional[TaskCard]]:
        """
        Create a new card from a user request.
        This is the main entry point for the board system.
        """
        try:
            # Create new task card
            card = TaskCard(
                title=request[:100],  # First 100 chars as title
                context=request,
                priority=priority,
                persona_type=persona_name,
                allowed_tools=self._determine_allowed_tools(persona_name),
                scope='task'
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
    
    def transition_card(self, card_id: str, new_status: CardStatus, reason: str = "") -> Tuple[bool, str]:
        """Transition a card to a new status with validation"""
        if card_id not in self.board_state.cards:
            return False, f"Card {card_id} not found"
            
        card = self.board_state.cards[card_id]
        old_status = card.status
        
        # Validate transition
        if not self._is_valid_transition(old_status, new_status):
            return False, f"Invalid transition from {old_status.value} to {new_status.value}"
            
        # Update card status
        card.status = new_status
        card.updated_at = datetime.now()
        
        # Handle status-specific logic
        if new_status == CardStatus.IN_PROGRESS:
            card.started_at = datetime.now()
        elif new_status in [CardStatus.DONE, CardStatus.FAILED]:
            card.completed_at = datetime.now()
            
        # Update workflow engine
        success, message = self.workflow_engine.move_card(card_id, new_status, reason)
        
        if success:
            self.board_state.last_activity = datetime.now()
            if self.config.persist_state:
                self._save_board_state()
                
        return success, message
    
    def move_card(self, card_id: str, target_column: str, force: bool = False) -> Tuple[bool, str]:
        """Move a card to a specific column with optional force flag"""
        # Map column names to CardStatus
        column_map = {
            'backlog': CardStatus.BACKLOG,
            'todo': CardStatus.TODO,
            'in_progress': CardStatus.IN_PROGRESS,
            'integrate': CardStatus.INTEGRATE,
            'review': CardStatus.REVIEW,
            'done': CardStatus.DONE,
            'failed': CardStatus.FAILED,
            'blocked': CardStatus.BLOCKED
        }
        
        target_status = column_map.get(target_column.lower())
        if not target_status:
            return False, f"Invalid column: {target_column}"
            
        if force:
            # Force move without validation
            card = self.board_state.cards.get(card_id)
            if not card:
                return False, f"Card {card_id} not found"
            card.status = target_status
            card.updated_at = datetime.now()
            return True, f"Card {card_id} force-moved to {target_column}"
        else:
            # Use validated transition
            return self.transition_card(card_id, target_status, f"Moved to {target_column}")
    
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
    
    def get_next_task(self, agent_name: Optional[str] = None) -> Optional[TaskCard]:
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
    
    def get_card(self, card_id: str) -> Optional[TaskCard]:
        """Get a specific card"""
        return self.board_state.cards.get(card_id)
    
    def get_cards_by_status(self, status: CardStatus) -> List[TaskCard]:
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
    
    def execute_graceful_handoff(self, card_id: str) -> Tuple[bool, str, Optional[TaskCard]]:
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
    
    def _compress_card_context(self, card: TaskCard) -> str:
        """Compress card context for handoff using --uc style compression"""
        # Use SuperClaude's symbol system for compression
        compressed = f"""🎯 Task: {card.title}
📋 Status: {card.status.value} → Continue from here
⚡ Progress: {card.metadata.get('artifacts_count', 0)} artifacts created
🔍 Context: {card.context[:200]}...
📊 Metrics: {card.token_usage}t used
"""
        
        # Add key context elements
        if card.error_count > 0:
            compressed += f"⚠️ Errors: {card.error_count} encountered\n"
        
        # Preserve essential flags and persona
        if card.persona_type:
            compressed += f"👤 Persona: {card.persona_type}\n"
        
        return compressed.strip()
    
    def _create_handoff_card(self, old_card: TaskCard, compressed_context: str) -> TaskCard:
        """Create new card for handoff with compressed context"""
        # Create new card maintaining essential context
        new_card = TaskCard(
            title=f"Continue: {old_card.title}",
            context=compressed_context,
            priority=old_card.priority,
            persona_type=old_card.persona_type,
            allowed_tools=old_card.allowed_tools,
            scope=old_card.scope
        )
        
        # Preserve critical context elements
        new_card.context = compressed_context
        new_card.persona_type = old_card.persona_type
        new_card.dependencies = [old_card.id]
        
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
    
    def _is_valid_transition(self, from_status: CardStatus, to_status: CardStatus) -> bool:
        """Check if a status transition is valid"""
        # Define valid transitions
        valid_transitions = {
            CardStatus.BACKLOG: [CardStatus.TODO, CardStatus.BLOCKED],
            CardStatus.TODO: [CardStatus.IN_PROGRESS, CardStatus.BLOCKED],
            CardStatus.IN_PROGRESS: [CardStatus.INTEGRATE, CardStatus.REVIEW, CardStatus.BLOCKED, CardStatus.FAILED],
            CardStatus.INTEGRATE: [CardStatus.REVIEW, CardStatus.IN_PROGRESS, CardStatus.BLOCKED, CardStatus.FAILED],
            CardStatus.REVIEW: [CardStatus.DONE, CardStatus.IN_PROGRESS, CardStatus.FAILED],
            CardStatus.BLOCKED: [CardStatus.TODO, CardStatus.IN_PROGRESS, CardStatus.FAILED],
            CardStatus.DONE: [],  # Terminal state
            CardStatus.FAILED: [CardStatus.TODO, CardStatus.IN_PROGRESS]  # Can retry
        }
        
        return to_status in valid_transitions.get(from_status, [])
    
    def _determine_allowed_tools(self, persona_name: Optional[str]) -> List[str]:
        """Determine allowed tools based on persona type"""
        if not persona_name:
            return []  # All tools allowed
            
        # Tool restrictions by persona
        tool_map = {
            'architect': ['Read', 'Grep', 'Glob', 'Sequential'],
            'frontend': ['Read', 'Write', 'Edit', 'Magic', 'Playwright'],
            'backend': ['Read', 'Write', 'Edit', 'Bash', 'Context7'],
            'security': ['Read', 'Grep', 'Sequential'],
            'qa': ['Read', 'Grep', 'Playwright', 'Sequential'],
            'performance': ['Read', 'Grep', 'Bash', 'Sequential'],
            'mentor': ['Read', 'Context7', 'Sequential'],
            'scribe': ['Read', 'Write', 'Context7'],
            'analyzer': ['Read', 'Grep', 'Glob', 'Sequential'],
            'refactorer': ['Read', 'Edit', 'MultiEdit', 'Sequential'],
            'devops': ['Read', 'Bash', 'Write', 'Edit']
        }
        
        return tool_map.get(persona_name, [])
    
    def _assign_agent_to_card(self, card: TaskCard, persona_name: str) -> bool:
        """Assign an agent to a card"""
        agent_id = f"{persona_name}-agent-{card.id[:4]}"
        
        card.assigned_agent = agent_id
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
                # For now, skip loading cards until we have proper serialization
                pass  # TODO: Implement TaskCard.from_dict()
                
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