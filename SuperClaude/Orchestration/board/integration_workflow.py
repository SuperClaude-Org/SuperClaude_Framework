"""
Integration Workflow for Phase 3: Advanced Orchestration
Handles multi-agent coordination, result merging, and conflict resolution
in the INTEGRATE column.
"""

import json
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

from .card_model import Card, CardStatus, CardResult
from .board_manager import BoardManager

logger = logging.getLogger(__name__)


class IntegrationStrategy(Enum):
    """Strategies for integrating multi-agent work"""
    SEQUENTIAL = "sequential"      # Agents work in sequence, each building on previous
    PARALLEL = "parallel"          # Agents work simultaneously, results merged
    HIERARCHICAL = "hierarchical"  # Master agent coordinates sub-agents
    CONSENSUS = "consensus"        # Multiple agents validate each other's work


@dataclass
class AgentContribution:
    """Represents a single agent's contribution to a task"""
    agent_id: str
    card_id: str
    output: str
    artifacts: List[str]
    metrics: Dict[str, Any]
    timestamp: datetime
    status: str = "pending"  # pending, completed, failed
    

@dataclass
class IntegrationConflict:
    """Represents a conflict between agent outputs"""
    conflict_type: str  # file_modification, logic_conflict, resource_conflict
    agents_involved: List[str]
    description: str
    resolution_options: List[str]
    auto_resolvable: bool = False


class IntegrationWorkflow:
    """
    Manages multi-agent coordination in the INTEGRATE column.
    Handles merging strategies, conflict resolution, and validation.
    """
    
    def __init__(self, board_manager: BoardManager):
        self.board = board_manager
        self.contributions: Dict[str, List[AgentContribution]] = {}
        self.conflicts: Dict[str, List[IntegrationConflict]] = {}
        self.integration_strategies = {
            IntegrationStrategy.SEQUENTIAL: self._sequential_integration,
            IntegrationStrategy.PARALLEL: self._parallel_integration,
            IntegrationStrategy.HIERARCHICAL: self._hierarchical_integration,
            IntegrationStrategy.CONSENSUS: self._consensus_integration
        }
        
    def coordinate_agents(self, cards: List[Card], strategy: IntegrationStrategy) -> Tuple[bool, str]:
        """
        Coordinate multiple agents based on selected strategy.
        
        Returns: (success, message)
        """
        if not cards:
            return False, "No cards provided for integration"
            
        # Validate all cards are ready for integration
        for card in cards:
            if card.status not in [CardStatus.REVIEW, CardStatus.INTEGRATE]:
                return False, f"Card {card.id} not ready for integration (status: {card.status.value})"
                
        # Execute integration strategy
        try:
            integration_func = self.integration_strategies.get(strategy)
            if not integration_func:
                return False, f"Unknown integration strategy: {strategy}"
                
            result = integration_func(cards)
            return result
            
        except Exception as e:
            logger.error(f"Integration failed: {e}")
            return False, f"Integration error: {str(e)}"
            
    def _sequential_integration(self, cards: List[Card]) -> Tuple[bool, str]:
        """
        Sequential integration: Each agent builds on the previous agent's work.
        Order matters - cards are processed in sequence.
        """
        if not cards:
            return True, "No cards to integrate"
            
        logger.info(f"Starting sequential integration for {len(cards)} cards")
        
        # Sort cards by creation time to maintain order
        cards.sort(key=lambda c: c.created_at)
        
        # Process each card in sequence
        combined_output = []
        combined_artifacts = []
        
        for i, card in enumerate(cards):
            # Each card builds on previous results
            if i > 0:
                # Pass previous output as context to current card
                card.context.session_state["previous_output"] = combined_output[-1]
                card.context.session_state["previous_artifacts"] = combined_artifacts
                
            # Collect outputs
            combined_output.append(card.result.output)
            combined_artifacts.extend(card.result.artifacts)
            
            # Mark card as integrated
            card.update_status(CardStatus.INTEGRATE, f"Sequential integration step {i+1}/{len(cards)}")
            
        # Create merged result
        merged_card = self._create_merged_card(cards, IntegrationStrategy.SEQUENTIAL)
        merged_card.result.output = "\n\n".join(combined_output)
        merged_card.result.artifacts = list(set(combined_artifacts))  # Remove duplicates
        
        return True, f"Sequential integration completed for {len(cards)} cards"
        
    def _parallel_integration(self, cards: List[Card]) -> Tuple[bool, str]:
        """
        Parallel integration: Multiple agents work independently, results are merged.
        Conflicts need to be resolved.
        """
        logger.info(f"Starting parallel integration for {len(cards)} cards")
        
        # Collect all agent contributions
        contributions = []
        for card in cards:
            contribution = AgentContribution(
                agent_id=card.assigned_agent or "unknown",
                card_id=card.id,
                output=card.result.output,
                artifacts=card.result.artifacts,
                metrics=card.metrics.to_dict(),
                timestamp=card.completed_at or datetime.now(),
                status="completed"
            )
            contributions.append(contribution)
            
        # Check for conflicts
        conflicts = self._detect_conflicts(contributions)
        
        if conflicts:
            # Try to auto-resolve conflicts
            resolved_conflicts = []
            unresolved_conflicts = []
            
            for conflict in conflicts:
                if conflict.auto_resolvable:
                    resolved_conflicts.append(conflict)
                else:
                    unresolved_conflicts.append(conflict)
                    
            if unresolved_conflicts:
                # Store conflicts for manual resolution
                merged_card_id = f"merged_{cards[0].id}"
                self.conflicts[merged_card_id] = unresolved_conflicts
                return False, f"Found {len(unresolved_conflicts)} conflicts requiring manual resolution"
                
        # Merge outputs
        merged_output = self._merge_outputs(contributions)
        merged_artifacts = self._merge_artifacts(contributions)
        
        # Create merged card
        merged_card = self._create_merged_card(cards, IntegrationStrategy.PARALLEL)
        merged_card.result.output = merged_output
        merged_card.result.artifacts = merged_artifacts
        
        # Update card statuses
        for card in cards:
            card.update_status(CardStatus.INTEGRATE, "Parallel integration completed")
            
        return True, f"Parallel integration completed for {len(cards)} cards"
        
    def _hierarchical_integration(self, cards: List[Card]) -> Tuple[bool, str]:
        """
        Hierarchical integration: A master agent coordinates sub-agents.
        The first card is treated as the master.
        """
        if len(cards) < 2:
            return False, "Hierarchical integration requires at least 2 cards"
            
        logger.info(f"Starting hierarchical integration with {len(cards)} cards")
        
        master_card = cards[0]
        sub_cards = cards[1:]
        
        # Master reviews and integrates sub-agent work
        sub_outputs = []
        sub_artifacts = []
        
        for sub_card in sub_cards:
            sub_outputs.append({
                "agent": sub_card.assigned_agent,
                "output": sub_card.result.output,
                "metrics": sub_card.metrics.to_dict()
            })
            sub_artifacts.extend(sub_card.result.artifacts)
            
        # Create integration summary for master
        integration_summary = {
            "master_agent": master_card.assigned_agent,
            "sub_agents": [c.assigned_agent for c in sub_cards],
            "sub_outputs": sub_outputs,
            "integration_time": datetime.now().isoformat()
        }
        
        # Master's output takes precedence, with sub-agent work as supporting data
        merged_card = self._create_merged_card(cards, IntegrationStrategy.HIERARCHICAL)
        merged_card.result.output = master_card.result.output
        merged_card.result.artifacts = list(set(master_card.result.artifacts + sub_artifacts))
        merged_card.metadata["integration_summary"] = integration_summary
        
        # Update statuses
        master_card.update_status(CardStatus.INTEGRATE, "Master in hierarchical integration")
        for sub_card in sub_cards:
            sub_card.update_status(CardStatus.INTEGRATE, "Sub-agent in hierarchical integration")
            
        return True, f"Hierarchical integration completed with {len(sub_cards)} sub-agents"
        
    def _consensus_integration(self, cards: List[Card]) -> Tuple[bool, str]:
        """
        Consensus integration: Multiple agents validate each other's work.
        Requires agreement or voting mechanism.
        """
        logger.info(f"Starting consensus integration for {len(cards)} cards")
        
        # Collect all outputs for comparison
        agent_outputs = {}
        for card in cards:
            agent_outputs[card.assigned_agent or card.id] = {
                "output": card.result.output,
                "artifacts": card.result.artifacts,
                "confidence": card.metadata.get("confidence", 0.8)
            }
            
        # Compare outputs for consensus
        consensus_results = self._find_consensus(agent_outputs)
        
        if consensus_results["consensus_reached"]:
            # Use consensus output
            merged_card = self._create_merged_card(cards, IntegrationStrategy.CONSENSUS)
            merged_card.result.output = consensus_results["consensus_output"]
            merged_card.result.artifacts = consensus_results["consensus_artifacts"]
            merged_card.metadata["consensus_details"] = consensus_results
            
            # Update statuses
            for card in cards:
                card.update_status(CardStatus.INTEGRATE, "Consensus reached")
                
            return True, f"Consensus integration completed with {consensus_results['agreement_level']}% agreement"
            
        else:
            # No consensus - need escalation
            return False, f"Consensus not reached (agreement: {consensus_results['agreement_level']}%)"
            
    def _detect_conflicts(self, contributions: List[AgentContribution]) -> List[IntegrationConflict]:
        """Detect conflicts between agent contributions"""
        conflicts = []
        
        # Check for file modification conflicts
        file_modifications = {}
        for contrib in contributions:
            for artifact in contrib.artifacts:
                if artifact in file_modifications:
                    # Multiple agents modified same file
                    conflicts.append(IntegrationConflict(
                        conflict_type="file_modification",
                        agents_involved=[file_modifications[artifact], contrib.agent_id],
                        description=f"Multiple agents modified {artifact}",
                        resolution_options=["merge_changes", "use_latest", "manual_merge"],
                        auto_resolvable=False
                    ))
                else:
                    file_modifications[artifact] = contrib.agent_id
                    
        # Could add more conflict detection logic here
        # - Logic conflicts in code
        # - Resource allocation conflicts
        # - Dependency conflicts
        
        return conflicts
        
    def _merge_outputs(self, contributions: List[AgentContribution]) -> str:
        """Merge outputs from multiple agents"""
        # Simple concatenation for now, could be more sophisticated
        merged_parts = []
        
        for contrib in contributions:
            merged_parts.append(f"=== Output from {contrib.agent_id} ===")
            merged_parts.append(contrib.output)
            merged_parts.append("")
            
        return "\n".join(merged_parts)
        
    def _merge_artifacts(self, contributions: List[AgentContribution]) -> List[str]:
        """Merge artifacts from multiple agents"""
        all_artifacts = []
        for contrib in contributions:
            all_artifacts.extend(contrib.artifacts)
            
        # Remove duplicates while preserving order
        seen = set()
        unique_artifacts = []
        for artifact in all_artifacts:
            if artifact not in seen:
                seen.add(artifact)
                unique_artifacts.append(artifact)
                
        return unique_artifacts
        
    def _find_consensus(self, agent_outputs: Dict[str, Dict]) -> Dict[str, Any]:
        """Find consensus among agent outputs"""
        # Simple voting mechanism - could be enhanced
        output_votes = {}
        total_agents = len(agent_outputs)
        
        # Count similar outputs (simplified - real implementation would be more sophisticated)
        for agent, data in agent_outputs.items():
            output_hash = hash(data["output"][:100])  # Simple hash of first 100 chars
            if output_hash not in output_votes:
                output_votes[output_hash] = {
                    "agents": [],
                    "output": data["output"],
                    "artifacts": data["artifacts"]
                }
            output_votes[output_hash]["agents"].append(agent)
            
        # Find majority
        best_consensus = None
        best_count = 0
        
        for vote_data in output_votes.values():
            if len(vote_data["agents"]) > best_count:
                best_count = len(vote_data["agents"])
                best_consensus = vote_data
                
        agreement_level = (best_count / total_agents) * 100
        consensus_reached = agreement_level >= 60  # 60% threshold
        
        return {
            "consensus_reached": consensus_reached,
            "agreement_level": agreement_level,
            "consensus_output": best_consensus["output"] if best_consensus else "",
            "consensus_artifacts": best_consensus["artifacts"] if best_consensus else [],
            "agreeing_agents": best_consensus["agents"] if best_consensus else [],
            "total_agents": total_agents
        }
        
    def _create_merged_card(self, source_cards: List[Card], strategy: IntegrationStrategy) -> Card:
        """Create a new card representing the merged work"""
        # Use the first card as template
        template_card = source_cards[0]
        
        merged_card = Card(
            id=f"merged_{template_card.id}",
            title=f"Integrated: {template_card.title}",
            description=f"Multi-agent integration of {len(source_cards)} tasks",
            status=CardStatus.INTEGRATE,
            priority=template_card.priority,
            card_type=template_card.card_type,
            context=template_card.context,
            created_by="integration_workflow"
        )
        
        # Track contributing agents
        merged_card.contributing_agents = [card.assigned_agent or card.id for card in source_cards]
        merged_card.integration_strategy = strategy.value
        
        # Aggregate metrics
        total_tokens = sum(card.metrics.token_usage for card in source_cards)
        total_time = sum(card.metrics.processing_time for card in source_cards)
        
        merged_card.metrics.token_usage = total_tokens
        merged_card.metrics.processing_time = total_time
        
        return merged_card
        
    def resolve_conflicts(self, card_id: str, resolutions: Dict[str, str]) -> Tuple[bool, str]:
        """Manually resolve conflicts for a card"""
        if card_id not in self.conflicts:
            return False, f"No conflicts found for card {card_id}"
            
        conflicts = self.conflicts[card_id]
        
        # Apply resolutions
        for i, conflict in enumerate(conflicts):
            if str(i) in resolutions:
                resolution = resolutions[str(i)]
                logger.info(f"Resolving conflict {i} with strategy: {resolution}")
                # Apply resolution logic here
                
        # Clear resolved conflicts
        del self.conflicts[card_id]
        
        return True, f"Resolved {len(conflicts)} conflicts"
        
    def get_integration_status(self, card_id: str) -> Dict[str, Any]:
        """Get detailed integration status for a card"""
        # Find card in INTEGRATE status
        integrate_cards = self.board.get_cards_by_column("INTEGRATE")
        
        for card in integrate_cards:
            if card.id == card_id or card.id.startswith(f"merged_{card_id}"):
                return {
                    "card_id": card.id,
                    "status": card.status.value,
                    "contributing_agents": card.contributing_agents,
                    "integration_strategy": card.integration_strategy,
                    "has_conflicts": card.id in self.conflicts,
                    "conflict_count": len(self.conflicts.get(card.id, [])),
                    "metrics": card.metrics.to_dict()
                }
                
        return {"error": f"Card {card_id} not found in integration"}