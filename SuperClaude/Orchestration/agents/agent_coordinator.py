"""
Agent Coordinator - Sub-agent lifecycle management

Manages the complete lifecycle of sub-agents:
- Creation from personas
- Assignment to cards
- Monitoring and health checks
- Cleanup and resource recovery
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ...SubAgents.core.persona_parser import PersonaParser
from ...SubAgents.core.prompt_generator import PromptGenerator
from ..board.card_model import TaskCard, CardStatus
from ..board.board_manager import BoardManager
from ..board.resource_tracker import ResourceTracker


class AgentStatus(Enum):
    """Sub-agent lifecycle states"""
    INITIALIZING = "initializing"
    READY = "ready"
    WORKING = "working"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


@dataclass
class SubAgent:
    """Sub-agent instance with state tracking"""
    id: str
    persona_type: str
    card_id: Optional[str] = None
    status: AgentStatus = AgentStatus.INITIALIZING
    created_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    token_usage: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_healthy(self) -> bool:
        """Check if agent is responsive"""
        if self.status in [AgentStatus.FAILED, AgentStatus.TERMINATED]:
            return False
        # Consider unhealthy if no heartbeat for 5 minutes
        return (datetime.now() - self.last_heartbeat) < timedelta(minutes=5)


class AgentCoordinator:
    """Manages sub-agent lifecycle and coordination"""
    
    def __init__(self, board_manager: BoardManager, resource_tracker: ResourceTracker,
                 persona_parser: PersonaParser, prompt_generator: PromptGenerator):
        self.board = board_manager
        self.resources = resource_tracker
        self.persona_parser = persona_parser
        self.prompt_generator = prompt_generator
        
        # Agent registry
        self.agents: Dict[str, SubAgent] = {}
        self.agent_cards: Dict[str, str] = {}  # agent_id -> card_id mapping
        
        # Configuration
        self.max_agents = 3  # Max concurrent agents
        self.heartbeat_interval = 60  # seconds
        self.cleanup_interval = 300  # 5 minutes
        
        # API placeholders (to be implemented with actual API)
        self._api_client = None
        
    async def create_agent(self, persona_type: str, card: TaskCard) -> Optional[SubAgent]:
        """Create a new sub-agent for a task card"""
        # Check resource limits
        if not self._can_create_agent():
            return None
            
        # Get persona definition
        persona = self.persona_parser.get_persona(persona_type)
        if not persona:
            return None
            
        # Generate system prompt
        prompt_config = {
            'persona': persona,
            'context': card.context,
            'tools': card.allowed_tools,
            'restrictions': {
                'token_limit': 5000,  # Per-card token budget
                'time_limit': 300,    # 5 minute timeout
                'scope': card.scope
            }
        }
        
        system_prompt = self.prompt_generator.generate_prompt(
            persona_type=persona_type,
            task_context=card.context,
            config=prompt_config
        )
        
        # Create agent instance
        agent_id = f"agent_{persona_type}_{card.id[:8]}_{datetime.now().timestamp():.0f}"
        agent = SubAgent(
            id=agent_id,
            persona_type=persona_type,
            card_id=card.id,
            metadata={
                'system_prompt': system_prompt,
                'allowed_tools': card.allowed_tools,
                'card_title': card.title
            }
        )
        
        # Initialize agent via API (placeholder)
        success = await self._initialize_agent_api(agent, system_prompt)
        
        if success:
            agent.status = AgentStatus.READY
            self.agents[agent_id] = agent
            self.agent_cards[agent_id] = card.id
            
            # Update card assignment
            card.assigned_agent = agent_id
            self.board.update_card(card)
            
            # Track resource allocation
            self.resources.allocate_agent(agent_id, estimated_tokens=5000)
            
            return agent
        else:
            return None
    
    async def assign_agent_to_card(self, agent_id: str, card: TaskCard) -> bool:
        """Assign an existing agent to a new card"""
        agent = self.agents.get(agent_id)
        if not agent or agent.status != AgentStatus.READY:
            return False
            
        # Check if agent is compatible with card
        if not self._is_agent_compatible(agent, card):
            return False
            
        # Update assignments
        agent.card_id = card.id
        agent.status = AgentStatus.WORKING
        self.agent_cards[agent_id] = card.id
        
        card.assigned_agent = agent_id
        self.board.update_card(card)
        
        return True
    
    async def pause_agent(self, agent_id: str, reason: str = "User requested") -> bool:
        """Pause an agent's execution"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False
            
        if agent.status == AgentStatus.WORKING:
            agent.status = AgentStatus.PAUSED
            agent.metadata['pause_reason'] = reason
            agent.metadata['paused_at'] = datetime.now().isoformat()
            
            # Update associated card
            if agent.card_id:
                card = self.board.get_card(agent.card_id)
                if card and card.status == CardStatus.IN_PROGRESS:
                    self.board.transition_card(card.id, CardStatus.BLOCKED, reason)
                    
            return True
        return False
    
    async def resume_agent(self, agent_id: str) -> bool:
        """Resume a paused agent"""
        agent = self.agents.get(agent_id)
        if not agent or agent.status != AgentStatus.PAUSED:
            return False
            
        agent.status = AgentStatus.WORKING
        agent.metadata.pop('pause_reason', None)
        agent.metadata.pop('paused_at', None)
        
        # Update associated card
        if agent.card_id:
            card = self.board.get_card(agent.card_id)
            if card and card.status == CardStatus.BLOCKED:
                self.board.transition_card(card.id, CardStatus.IN_PROGRESS, "Agent resumed")
                
        return True
    
    async def terminate_agent(self, agent_id: str, reason: str = "Task completed") -> bool:
        """Terminate an agent and clean up resources"""
        agent = self.agents.get(agent_id)
        if not agent:
            return False
            
        # Mark as terminated
        agent.status = AgentStatus.TERMINATED
        agent.metadata['termination_reason'] = reason
        agent.metadata['terminated_at'] = datetime.now().isoformat()
        
        # Clean up API resources (placeholder)
        await self._cleanup_agent_api(agent)
        
        # Release resources
        self.resources.release_agent(agent_id)
        
        # Remove from active registries
        del self.agents[agent_id]
        self.agent_cards.pop(agent_id, None)
        
        return True
    
    async def monitor_agents(self) -> Dict[str, Any]:
        """Monitor all active agents and return health status"""
        health_report = {
            'total_agents': len(self.agents),
            'healthy': 0,
            'unhealthy': 0,
            'working': 0,
            'paused': 0,
            'agents': []
        }
        
        for agent_id, agent in self.agents.items():
            is_healthy = agent.is_healthy()
            
            agent_info = {
                'id': agent_id,
                'persona': agent.persona_type,
                'status': agent.status.value,
                'healthy': is_healthy,
                'card_id': agent.card_id,
                'token_usage': agent.token_usage,
                'error_count': agent.error_count,
                'uptime': (datetime.now() - agent.created_at).total_seconds()
            }
            
            health_report['agents'].append(agent_info)
            
            if is_healthy:
                health_report['healthy'] += 1
            else:
                health_report['unhealthy'] += 1
                
            if agent.status == AgentStatus.WORKING:
                health_report['working'] += 1
            elif agent.status == AgentStatus.PAUSED:
                health_report['paused'] += 1
                
        return health_report
    
    async def handle_agent_error(self, agent_id: str, error: str) -> None:
        """Handle agent error and decide on recovery strategy"""
        agent = self.agents.get(agent_id)
        if not agent:
            return
            
        agent.error_count += 1
        agent.metadata.setdefault('error_log', []).append({
            'timestamp': datetime.now().isoformat(),
            'error': error
        })
        
        # Update card error info
        if agent.card_id:
            card = self.board.get_card(agent.card_id)
            if card:
                card.error_count += 1
                card.error_log.append(f"Agent error: {error}")
                self.board.update_card(card)
        
        # Decide on recovery strategy
        if agent.error_count >= 3:
            # Too many errors, fail the agent
            agent.status = AgentStatus.FAILED
            if agent.card_id:
                self.board.transition_card(agent.card_id, CardStatus.FAILED, 
                                         f"Agent failed after {agent.error_count} errors")
        elif agent.error_count >= 2:
            # Pause for investigation
            await self.pause_agent(agent_id, f"Paused after {agent.error_count} errors")
    
    async def get_agent_for_persona(self, persona_type: str) -> Optional[SubAgent]:
        """Find an available agent of the specified persona type"""
        for agent in self.agents.values():
            if (agent.persona_type == persona_type and 
                agent.status == AgentStatus.READY and
                not agent.card_id):
                return agent
        return None
    
    async def cleanup_inactive_agents(self) -> int:
        """Clean up inactive or failed agents"""
        cleaned = 0
        agents_to_remove = []
        
        for agent_id, agent in self.agents.items():
            # Remove failed or terminated agents
            if agent.status in [AgentStatus.FAILED, AgentStatus.TERMINATED]:
                agents_to_remove.append(agent_id)
                
            # Remove agents that haven't been active for too long
            elif not agent.is_healthy() and agent.status != AgentStatus.PAUSED:
                agents_to_remove.append(agent_id)
                
        for agent_id in agents_to_remove:
            if await self.terminate_agent(agent_id, "Cleanup - inactive"):
                cleaned += 1
                
        return cleaned
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of agent coordinator state"""
        return {
            'active_agents': len(self.agents),
            'max_agents': self.max_agents,
            'agents_by_status': self._count_by_status(),
            'agents_by_persona': self._count_by_persona(),
            'total_token_usage': sum(a.token_usage for a in self.agents.values()),
            'total_errors': sum(a.error_count for a in self.agents.values())
        }
    
    # Private helper methods
    
    def _can_create_agent(self) -> bool:
        """Check if we can create a new agent"""
        active_count = sum(1 for a in self.agents.values() 
                          if a.status in [AgentStatus.READY, AgentStatus.WORKING])
        return active_count < self.max_agents
    
    def _is_agent_compatible(self, agent: SubAgent, card: TaskCard) -> bool:
        """Check if agent can handle the card's requirements"""
        # Check tool compatibility
        if card.allowed_tools:
            agent_tools = agent.metadata.get('allowed_tools', [])
            if not all(tool in agent_tools for tool in card.allowed_tools):
                return False
                
        # Check scope compatibility (could be expanded)
        return True
    
    def _count_by_status(self) -> Dict[str, int]:
        """Count agents by status"""
        counts = {}
        for agent in self.agents.values():
            status = agent.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts
    
    def _count_by_persona(self) -> Dict[str, int]:
        """Count agents by persona type"""
        counts = {}
        for agent in self.agents.values():
            counts[agent.persona_type] = counts.get(agent.persona_type, 0) + 1
        return counts
    
    # API placeholder methods (to be implemented with actual Claude Code API)
    
    async def _initialize_agent_api(self, agent: SubAgent, system_prompt: str) -> bool:
        """Initialize agent via API"""
        # TODO: Implement actual API call to create sub-agent
        # For now, simulate success
        await asyncio.sleep(0.1)  # Simulate API delay
        return True
    
    async def _cleanup_agent_api(self, agent: SubAgent) -> bool:
        """Clean up agent API resources"""
        # TODO: Implement actual API cleanup
        await asyncio.sleep(0.1)  # Simulate API delay
        return True
    
    async def _send_heartbeat(self, agent_id: str) -> bool:
        """Send heartbeat to agent"""
        agent = self.agents.get(agent_id)
        if agent:
            agent.last_heartbeat = datetime.now()
            return True
        return False