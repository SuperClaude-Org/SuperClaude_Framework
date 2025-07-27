"""
Delegation Engine for Phase 3: Advanced Orchestration
Intelligently assigns tasks to the most suitable agents based on capabilities,
workload, and performance history.
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from Orchestration.board.card_model import TaskCard
from Orchestration.agents.agent_coordinator import AgentCoordinator

logger = logging.getLogger(__name__)


@dataclass
class AgentCapability:
    """Represents an agent's capabilities and strengths"""
    domains: List[str]
    tools: List[str]
    strengths: List[str]
    max_complexity: float
    success_rate: float = 0.9
    avg_completion_time: float = 5.0  # minutes


class DelegationEngine:
    """
    Intelligent task delegation system that assigns tasks to the most suitable agents
    based on multiple factors including capabilities, workload, and performance.
    """
    
    # Agent capability matrix defining what each persona is good at
    CAPABILITY_MATRIX = {
        "frontend": AgentCapability(
            domains=["UI", "component", "responsive", "accessibility", "design"],
            tools=["Read", "Write", "Edit", "Magic", "WebFetch"],
            strengths=["React", "Vue", "CSS", "user experience", "animations"],
            max_complexity=0.8
        ),
        "backend": AgentCapability(
            domains=["API", "database", "server", "authentication", "performance"],
            tools=["Read", "Write", "Bash", "Sequential", "Grep"],
            strengths=["REST", "GraphQL", "SQL", "optimization", "scalability"],
            max_complexity=0.9
        ),
        "security": AgentCapability(
            domains=["vulnerability", "authentication", "encryption", "audit", "compliance"],
            tools=["Grep", "Sequential", "Read", "Bash"],
            strengths=["penetration testing", "OWASP", "threat modeling", "cryptography"],
            max_complexity=0.95
        ),
        "qa": AgentCapability(
            domains=["testing", "quality", "validation", "edge cases", "regression"],
            tools=["Playwright", "Read", "Sequential", "Bash"],
            strengths=["E2E testing", "unit testing", "test automation", "bug detection"],
            max_complexity=0.85
        ),
        "architect": AgentCapability(
            domains=["architecture", "design", "scalability", "patterns", "structure"],
            tools=["Sequential", "Read", "Write", "Glob"],
            strengths=["system design", "microservices", "design patterns", "refactoring"],
            max_complexity=1.0
        ),
        "devops": AgentCapability(
            domains=["deployment", "infrastructure", "CI/CD", "monitoring", "automation"],
            tools=["Bash", "Read", "Write", "Sequential"],
            strengths=["Docker", "Kubernetes", "AWS", "automation", "pipelines"],
            max_complexity=0.9
        )
    }
    
    def __init__(self, agent_coordinator: AgentCoordinator, performance_analytics=None):
        self.coordinator = agent_coordinator
        self.analytics = performance_analytics
        self.agent_workload: Dict[str, int] = {}  # Track active tasks per agent
        
    def assign_task(self, task_card: TaskCard) -> Optional[str]:
        """
        Assign task to the best available agent based on scoring algorithm.
        
        Returns agent_id if successful, None if no suitable agent found.
        """
        # Get available agents
        available_agents = self._get_available_agents()
        if not available_agents:
            logger.warning("No available agents for task assignment")
            return None
            
        # Score each agent
        agent_scores = self._score_agents(task_card, available_agents)
        
        # Select best agent
        best_agent_id = self._select_best_agent(agent_scores)
        
        if best_agent_id:
            logger.info(f"Assigned task {task_card.id} to agent {best_agent_id}")
            self._update_workload(best_agent_id, 1)
            return best_agent_id
            
        logger.warning(f"Could not find suitable agent for task {task_card.id}")
        return None
        
    def _get_available_agents(self) -> List[str]:
        """Get list of available agents with capacity"""
        available = []
        
        # Get active agents from coordinator
        active_agents = self.coordinator.list_agents()
        
        for agent_id in active_agents:
            # Check workload
            current_load = self.agent_workload.get(agent_id, 0)
            if current_load < 2:  # Max 2 concurrent tasks per agent
                available.append(agent_id)
                
        return available
        
    def _score_agents(self, task: TaskCard, agents: List[str]) -> Dict[str, float]:
        """
        Score each agent based on task suitability.
        
        Scoring factors:
        - Capability match (40%)
        - Current workload (20%)
        - Past performance (20%)
        - Resource availability (20%)
        """
        scores = {}
        
        for agent_id in agents:
            # Extract persona type from agent_id (e.g., "agent_frontend_001" -> "frontend")
            persona_type = self._extract_persona_type(agent_id)
            
            if persona_type not in self.CAPABILITY_MATRIX:
                scores[agent_id] = 0.0
                continue
                
            capability = self.CAPABILITY_MATRIX[persona_type]
            
            # Calculate capability match score (0-1)
            capability_score = self._calculate_capability_match(task, capability)
            
            # Calculate workload score (0-1, lower workload = higher score)
            workload_score = 1.0 - (self.agent_workload.get(agent_id, 0) / 2.0)
            
            # Calculate performance score (from analytics if available)
            performance_score = self._get_performance_score(agent_id)
            
            # Calculate resource availability score
            resource_score = self._calculate_resource_availability(agent_id)
            
            # Weighted total score
            total_score = (
                capability_score * 0.4 +
                workload_score * 0.2 +
                performance_score * 0.2 +
                resource_score * 0.2
            )
            
            scores[agent_id] = total_score
            
        return scores
        
    def _calculate_capability_match(self, task: TaskCard, capability: AgentCapability) -> float:
        """Calculate how well agent capabilities match task requirements"""
        score = 0.0
        
        # Check domain match
        task_domains = self._extract_task_domains(task)
        domain_matches = sum(1 for d in task_domains if d in capability.domains)
        if task_domains:
            score += (domain_matches / len(task_domains)) * 0.5
            
        # Check complexity match
        task_complexity = task.metadata.get("complexity", 0.5)
        if task_complexity <= capability.max_complexity:
            score += 0.3
            
        # Check tool requirements
        required_tools = task.metadata.get("required_tools", [])
        if required_tools:
            tool_matches = sum(1 for t in required_tools if t in capability.tools)
            score += (tool_matches / len(required_tools)) * 0.2
        else:
            score += 0.2  # No specific tools required
            
        return min(score, 1.0)
        
    def _extract_task_domains(self, task: TaskCard) -> List[str]:
        """Extract domain keywords from task description and metadata"""
        domains = []
        
        # Check task title and description
        text = f"{task.title} {task.description}".lower()
        
        # Map keywords to domains
        domain_keywords = {
            "UI": ["ui", "interface", "component", "frontend", "react", "vue"],
            "API": ["api", "endpoint", "rest", "graphql", "backend"],
            "database": ["database", "sql", "query", "schema", "migration"],
            "security": ["security", "vulnerability", "auth", "encryption"],
            "testing": ["test", "testing", "qa", "quality", "validation"],
            "deployment": ["deploy", "deployment", "ci/cd", "docker", "kubernetes"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text for keyword in keywords):
                domains.append(domain)
                
        return domains
        
    def _extract_persona_type(self, agent_id: str) -> str:
        """Extract persona type from agent ID"""
        # Format: agent_<persona>_<number>
        parts = agent_id.split('_')
        if len(parts) >= 2:
            return parts[1]
        return "generic"
        
    def _get_performance_score(self, agent_id: str) -> float:
        """Get agent's historical performance score"""
        if self.analytics:
            return self.analytics.get_agent_performance(agent_id)
        return 0.8  # Default score if no analytics available
        
    def _calculate_resource_availability(self, agent_id: str) -> float:
        """Calculate resource availability for agent"""
        # Could check token usage, memory, etc.
        # For now, simple implementation
        return 0.9
        
    def _select_best_agent(self, scores: Dict[str, float]) -> Optional[str]:
        """Select agent with highest score above threshold"""
        if not scores:
            return None
            
        # Sort by score
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Select best agent above threshold
        threshold = 0.5
        for agent_id, score in sorted_agents:
            if score >= threshold:
                return agent_id
                
        return None
        
    def _update_workload(self, agent_id: str, delta: int):
        """Update agent workload tracking"""
        current = self.agent_workload.get(agent_id, 0)
        self.agent_workload[agent_id] = max(0, current + delta)
        
    def release_agent(self, agent_id: str):
        """Release agent after task completion"""
        self._update_workload(agent_id, -1)
        
    def find_alternative_agent(self, task: TaskCard, exclude: List[str]) -> Optional[str]:
        """Find alternative agent for reassignment, excluding certain agents"""
        available = [a for a in self._get_available_agents() if a not in exclude]
        
        if not available:
            return None
            
        scores = self._score_agents(task, available)
        return self._select_best_agent(scores)
        
    def get_delegation_stats(self) -> Dict:
        """Get current delegation statistics"""
        return {
            "total_agents": len(self.CAPABILITY_MATRIX),
            "active_agents": len(self.agent_workload),
            "workload_distribution": dict(self.agent_workload),
            "capability_coverage": list(self.CAPABILITY_MATRIX.keys())
        }