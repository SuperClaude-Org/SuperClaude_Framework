"""
Recovery Manager - Error handling and recovery strategies

Provides intelligent error recovery with clear visibility:
- Error classification and severity assessment
- Recovery strategy selection
- Fallback mechanisms
- User notification and intervention
"""

from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import traceback
import json

from ..board.card_model import TaskCard, CardStatus
from ..board.board_manager import BoardManager
from .agent_coordinator import AgentCoordinator, AgentStatus
from ...SubAgents.core.delegation_engine import DelegationEngine


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"          # Can be retried automatically
    MEDIUM = "medium"    # Needs strategy adjustment
    HIGH = "high"        # Requires user intervention
    CRITICAL = "critical" # System-level failure


class RecoveryStrategy(Enum):
    """Available recovery strategies"""
    RETRY = "retry"                    # Simple retry with same config
    RETRY_WITH_BACKOFF = "backoff"     # Exponential backoff retry
    REASSIGN = "reassign"              # Assign to different agent
    FALLBACK_PERSONA = "fallback"      # Use different persona type
    PAUSE_FOR_USER = "pause"           # Pause and wait for user
    FAIL_CARD = "fail"                 # Mark card as failed
    SYSTEM_FALLBACK = "system"         # Use main Claude system


@dataclass
class ErrorContext:
    """Context for an error occurrence"""
    card_id: str
    agent_id: Optional[str]
    error_type: str
    error_message: str
    severity: ErrorSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    stack_trace: Optional[str] = None
    recovery_attempts: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecoveryManager:
    """Manages error recovery strategies and fallback mechanisms with automatic reassignment"""
    
    def __init__(self, board_manager: BoardManager, agent_coordinator: AgentCoordinator, 
                 delegation_engine: Optional[DelegationEngine] = None):
        self.board = board_manager
        self.coordinator = agent_coordinator
        self.delegation_engine = delegation_engine
        
        # Error history for pattern detection
        self.error_history: List[ErrorContext] = []
        self.recovery_history: Dict[str, List[Tuple[RecoveryStrategy, bool]]] = {}
        
        # Configuration
        self.max_retry_attempts = 3
        self.backoff_base = 2  # seconds
        self.error_window = timedelta(minutes=15)  # For pattern detection
        self.auto_reassignment_enabled = True
        
        # Error patterns and strategies
        self.error_strategies = self._initialize_error_strategies()
        
    def handle_error(self, error: Exception, card: TaskCard, 
                    agent_id: Optional[str] = None) -> Tuple[RecoveryStrategy, str]:
        """Main error handling entry point"""
        # Create error context
        context = self._create_error_context(error, card, agent_id)
        self.error_history.append(context)
        
        # Classify error severity
        severity = self._classify_error_severity(context)
        context.severity = severity
        
        # Select recovery strategy
        strategy = self._select_recovery_strategy(context)
        
        # Execute recovery
        success, message = self._execute_recovery(strategy, context)
        
        # Track recovery attempt
        card_recovery = self.recovery_history.setdefault(card.id, [])
        card_recovery.append((strategy, success))
        
        # Update card with error info
        self._update_card_error_info(card, context, strategy, message)
        
        return strategy, message
    
    async def execute_retry(self, context: ErrorContext) -> bool:
        """Execute a retry attempt"""
        card = self.board.get_card(context.card_id)
        if not card:
            return False
            
        # Check retry limit
        if context.recovery_attempts >= self.max_retry_attempts:
            return False
            
        # If using backoff, wait
        if context.metadata.get('use_backoff'):
            wait_time = self.backoff_base ** context.recovery_attempts
            await asyncio.sleep(wait_time)
            
        # Increment attempt counter
        context.recovery_attempts += 1
        
        # Resume agent if paused
        if context.agent_id:
            await self.coordinator.resume_agent(context.agent_id)
            
        return True
    
    async def execute_reassignment(self, context: ErrorContext) -> Tuple[bool, str]:
        """Reassign card to a different agent using intelligent delegation"""
        card = self.board.get_card(context.card_id)
        if not card:
            return False, "Card not found"
            
        # Use delegation engine for intelligent reassignment
        if self.delegation_engine and self.auto_reassignment_enabled:
            # Get alternative agent, excluding the failed one
            exclude_agents = [context.agent_id] if context.agent_id else []
            new_agent_id = self.delegation_engine.find_alternative_agent(card, exclude_agents)
            
            if new_agent_id:
                # Release the failed agent
                if context.agent_id:
                    self.delegation_engine.release_agent(context.agent_id)
                    await self.coordinator.terminate_agent(context.agent_id, 
                                                         reason="Failed and reassigned")
                
                # Assign to new agent
                card.assign_agent(new_agent_id)
                
                # Add context preservation for the new agent
                card.context.session_state["previous_attempt"] = {
                    "failed_agent": context.agent_id,
                    "error_type": context.error_type,
                    "error_message": context.error_message,
                    "recovery_strategy": "reassignment"
                }
                
                return True, f"Intelligently reassigned to {new_agent_id}"
            else:
                return False, "No suitable alternative agent found"
        
        # Fallback to basic reassignment
        return await self._basic_reassignment(context)
        
    async def _basic_reassignment(self, context: ErrorContext) -> Tuple[bool, str]:
        """Basic reassignment without delegation engine"""
        card = self.board.get_card(context.card_id)
        if not card:
            return False, "Card not found"
            
        # Get current persona type
        current_agent = None
        if context.agent_id:
            current_agent = self.coordinator.agents.get(context.agent_id)
            
        # Find alternative agent
        if current_agent:
            # Try same persona type first
            alt_agent = await self.coordinator.get_agent_for_persona(current_agent.persona_type)
            if alt_agent:
                success = await self.coordinator.assign_agent_to_card(alt_agent.id, card)
                if success:
                    return True, f"Reassigned to agent {alt_agent.id}"
                    
        # No alternative found
        return False, "No alternative agent available"
    
    async def execute_fallback_persona(self, context: ErrorContext) -> Tuple[bool, str]:
        """Try a different persona type"""
        card = self.board.get_card(context.card_id)
        if not card:
            return False, "Card not found"
            
        # Determine fallback persona based on error type
        fallback_persona = self._select_fallback_persona(context)
        if not fallback_persona:
            return False, "No suitable fallback persona"
            
        # Create new agent with fallback persona
        new_agent = await self.coordinator.create_agent(fallback_persona, card)
        if new_agent:
            return True, f"Created {fallback_persona} agent as fallback"
            
        return False, "Failed to create fallback agent"
    
    def analyze_error_patterns(self) -> Dict[str, Any]:
        """Analyze recent errors for patterns"""
        recent_errors = self._get_recent_errors()
        
        analysis = {
            'total_errors': len(recent_errors),
            'by_severity': self._count_by_severity(recent_errors),
            'by_type': self._count_by_type(recent_errors),
            'frequent_cards': self._identify_problematic_cards(recent_errors),
            'frequent_agents': self._identify_problematic_agents(recent_errors),
            'recovery_success_rate': self._calculate_recovery_success_rate()
        }
        
        # Identify patterns
        patterns = []
        
        # Pattern: Repeated failures on same card
        problem_cards = [card_id for card_id, count in analysis['frequent_cards'] if count >= 3]
        if problem_cards:
            patterns.append({
                'type': 'repeated_card_failure',
                'cards': problem_cards,
                'recommendation': 'Consider failing these cards or manual intervention'
            })
            
        # Pattern: Agent-specific failures
        problem_agents = [agent_id for agent_id, count in analysis['frequent_agents'] if count >= 3]
        if problem_agents:
            patterns.append({
                'type': 'agent_failures',
                'agents': problem_agents,
                'recommendation': 'Terminate and recreate these agents'
            })
            
        # Pattern: Low recovery success
        if analysis['recovery_success_rate'] < 0.5:
            patterns.append({
                'type': 'low_recovery_success',
                'rate': analysis['recovery_success_rate'],
                'recommendation': 'Review recovery strategies, consider manual intervention'
            })
            
        analysis['patterns'] = patterns
        return analysis
    
    def get_recovery_recommendations(self, card_id: str) -> List[str]:
        """Get recovery recommendations for a specific card"""
        recommendations = []
        
        # Check card's error history
        card_errors = [e for e in self.error_history if e.card_id == card_id]
        if not card_errors:
            return ["No errors recorded for this card"]
            
        # Analyze recent errors
        recent_errors = card_errors[-5:]  # Last 5 errors
        
        # Check severity trend
        severities = [e.severity for e in recent_errors]
        if all(s in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] for s in severities):
            recommendations.append("🚨 Multiple high-severity errors - consider manual intervention")
            
        # Check recovery attempts
        recovery_attempts = self.recovery_history.get(card_id, [])
        failed_recoveries = sum(1 for _, success in recovery_attempts if not success)
        if failed_recoveries >= 3:
            recommendations.append("⚠️  Multiple failed recovery attempts - consider failing the card")
            
        # Check error types
        error_types = set(e.error_type for e in recent_errors)
        if 'ResourceExhausted' in error_types:
            recommendations.append("💡 Resource errors - try reducing scope or pausing other cards")
        if 'APIError' in error_types:
            recommendations.append("💡 API errors - check service status and rate limits")
        if 'ToolError' in error_types:
            recommendations.append("💡 Tool errors - verify tool permissions and availability")
            
        # Suggest strategies based on history
        if not recovery_attempts:
            recommendations.append("✅ Try automatic retry with backoff")
        elif len(recovery_attempts) < 3:
            recommendations.append("✅ Try reassigning to a different agent")
        else:
            recommendations.append("✅ Consider using fallback persona or system fallback")
            
        return recommendations
    
    # Private helper methods
    
    def _create_error_context(self, error: Exception, card: TaskCard, 
                             agent_id: Optional[str]) -> ErrorContext:
        """Create error context from exception"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Capture stack trace for detailed errors
        stack_trace = None
        if isinstance(error, (RuntimeError, ValueError, KeyError)):
            stack_trace = traceback.format_exc()
            
        return ErrorContext(
            card_id=card.id,
            agent_id=agent_id,
            error_type=error_type,
            error_message=error_message,
            severity=ErrorSeverity.MEDIUM,  # Will be updated
            stack_trace=stack_trace,
            metadata={
                'card_title': card.title,
                'card_status': card.status.value
            }
        )
    
    def _classify_error_severity(self, context: ErrorContext) -> ErrorSeverity:
        """Classify error severity based on type and context"""
        error_type = context.error_type
        
        # Critical errors
        if error_type in ['SystemExit', 'MemoryError', 'ResourceExhausted']:
            return ErrorSeverity.CRITICAL
            
        # High severity
        if error_type in ['APIError', 'AuthenticationError', 'PermissionError']:
            return ErrorSeverity.HIGH
            
        # Low severity
        if error_type in ['TimeoutError', 'ConnectionError']:
            return ErrorSeverity.LOW
            
        # Check error message for patterns
        message_lower = context.error_message.lower()
        if any(word in message_lower for word in ['fatal', 'critical', 'emergency']):
            return ErrorSeverity.CRITICAL
        elif any(word in message_lower for word in ['failed', 'error', 'invalid']):
            return ErrorSeverity.MEDIUM
            
        # Default to medium
        return ErrorSeverity.MEDIUM
    
    def _select_recovery_strategy(self, context: ErrorContext) -> RecoveryStrategy:
        """Select appropriate recovery strategy"""
        # Check if we have a specific strategy for this error type
        if context.error_type in self.error_strategies:
            return self.error_strategies[context.error_type]
            
        # Check previous recovery attempts
        card_recovery = self.recovery_history.get(context.card_id, [])
        
        # First attempt - simple retry
        if not card_recovery:
            return RecoveryStrategy.RETRY
            
        # Check last strategy
        last_strategy, last_success = card_recovery[-1] if card_recovery else (None, False)
        
        # If last retry failed, try with backoff
        if last_strategy == RecoveryStrategy.RETRY and not last_success:
            return RecoveryStrategy.RETRY_WITH_BACKOFF
            
        # If retries failed, try reassignment
        if len(card_recovery) >= 2 and not any(success for _, success in card_recovery[-2:]):
            return RecoveryStrategy.REASSIGN
            
        # High severity - pause for user
        if context.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            return RecoveryStrategy.PAUSE_FOR_USER
            
        # Multiple failures - consider failing the card
        if len(card_recovery) >= 5:
            return RecoveryStrategy.FAIL_CARD
            
        # Default to retry with backoff
        return RecoveryStrategy.RETRY_WITH_BACKOFF
    
    def _execute_recovery(self, strategy: RecoveryStrategy, 
                         context: ErrorContext) -> Tuple[bool, str]:
        """Execute the selected recovery strategy"""
        if strategy == RecoveryStrategy.RETRY:
            return True, "Retrying operation"
            
        elif strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
            context.metadata['use_backoff'] = True
            wait_time = self.backoff_base ** context.recovery_attempts
            return True, f"Retrying with {wait_time}s backoff"
            
        elif strategy == RecoveryStrategy.REASSIGN:
            # Will be handled asynchronously
            return True, "Reassigning to different agent"
            
        elif strategy == RecoveryStrategy.FALLBACK_PERSONA:
            # Will be handled asynchronously
            return True, "Trying fallback persona"
            
        elif strategy == RecoveryStrategy.PAUSE_FOR_USER:
            if context.card_id:
                self.board.transition_card(context.card_id, CardStatus.BLOCKED, 
                                         f"Paused due to error: {context.error_message}")
            return True, "Paused for user intervention"
            
        elif strategy == RecoveryStrategy.FAIL_CARD:
            if context.card_id:
                self.board.transition_card(context.card_id, CardStatus.FAILED,
                                         f"Failed after multiple errors")
            return True, "Card marked as failed"
            
        elif strategy == RecoveryStrategy.SYSTEM_FALLBACK:
            return True, "Falling back to main system"
            
        return False, "Unknown strategy"
    
    def enable_auto_reassignment(self, enabled: bool = True):
        """Enable or disable automatic reassignment"""
        self.auto_reassignment_enabled = enabled
        
    def get_failure_analysis(self, agent_id: str) -> Dict[str, Any]:
        """Analyze failure patterns for a specific agent"""
        agent_errors = [e for e in self.error_history if e.agent_id == agent_id]
        
        if not agent_errors:
            return {"agent_id": agent_id, "status": "no_errors"}
            
        # Calculate failure rate
        recent_errors = agent_errors[-10:]  # Last 10 errors
        error_types = {}
        for error in recent_errors:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            
        # Check if agent should be terminated
        critical_errors = sum(1 for e in recent_errors if e.severity == ErrorSeverity.CRITICAL)
        high_errors = sum(1 for e in recent_errors if e.severity == ErrorSeverity.HIGH)
        
        should_terminate = (
            critical_errors >= 2 or  # 2+ critical errors
            high_errors >= 5 or     # 5+ high errors
            len(recent_errors) >= 8  # 8+ total errors
        )
        
        return {
            "agent_id": agent_id,
            "total_errors": len(agent_errors),
            "recent_errors": len(recent_errors),
            "error_types": error_types,
            "should_terminate": should_terminate,
            "recommendation": self._get_agent_recommendation(agent_id, recent_errors)
        }
        
    def _get_agent_recommendation(self, agent_id: str, recent_errors: List[ErrorContext]) -> str:
        """Get recommendation for handling a problematic agent"""
        if not recent_errors:
            return "Agent performing well"
            
        critical_count = sum(1 for e in recent_errors if e.severity == ErrorSeverity.CRITICAL)
        high_count = sum(1 for e in recent_errors if e.severity == ErrorSeverity.HIGH)
        
        if critical_count >= 2:
            return "🚨 Terminate agent immediately - multiple critical errors"
        elif high_count >= 5:
            return "⚠️  Consider terminating agent - high error rate"
        elif len(recent_errors) >= 6:
            return "💡 Monitor closely - frequent errors detected"
        else:
            return "✅ Continue monitoring - acceptable error rate"
    
    def _update_card_error_info(self, card: TaskCard, context: ErrorContext,
                               strategy: RecoveryStrategy, message: str) -> None:
        """Update card with error information"""
        card.error_count += 1
        error_entry = f"[{context.timestamp:%H:%M:%S}] {context.error_type}: {message}"
        card.error_log.append(error_entry)
        
        # Add recovery info to metadata
        card.metadata.setdefault('recovery_attempts', []).append({
            'timestamp': context.timestamp.isoformat(),
            'error_type': context.error_type,
            'severity': context.severity.value,
            'strategy': strategy.value,
            'message': message
        })
        
        self.board.update_card(card)
    
    def _initialize_error_strategies(self) -> Dict[str, RecoveryStrategy]:
        """Initialize error type to strategy mapping"""
        return {
            'TimeoutError': RecoveryStrategy.RETRY_WITH_BACKOFF,
            'ConnectionError': RecoveryStrategy.RETRY_WITH_BACKOFF,
            'RateLimitError': RecoveryStrategy.RETRY_WITH_BACKOFF,
            'ResourceExhausted': RecoveryStrategy.PAUSE_FOR_USER,
            'APIError': RecoveryStrategy.FALLBACK_PERSONA,
            'ToolError': RecoveryStrategy.REASSIGN,
            'ValidationError': RecoveryStrategy.PAUSE_FOR_USER,
            'PermissionError': RecoveryStrategy.SYSTEM_FALLBACK
        }
    
    def _select_fallback_persona(self, context: ErrorContext) -> Optional[str]:
        """Select appropriate fallback persona based on error"""
        # Map error types to fallback personas
        fallback_map = {
            'ToolError': 'analyzer',        # Analyzer can work with limited tools
            'ComplexityError': 'architect', # Architect can handle complex tasks
            'ValidationError': 'qa',        # QA can identify issues
            'APIError': 'mentor'           # Mentor can explain without tools
        }
        
        return fallback_map.get(context.error_type)
    
    def _get_recent_errors(self) -> List[ErrorContext]:
        """Get errors within the time window"""
        cutoff = datetime.now() - self.error_window
        return [e for e in self.error_history if e.timestamp > cutoff]
    
    def _count_by_severity(self, errors: List[ErrorContext]) -> Dict[str, int]:
        """Count errors by severity"""
        counts = {}
        for error in errors:
            severity = error.severity.value
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _count_by_type(self, errors: List[ErrorContext]) -> Dict[str, int]:
        """Count errors by type"""
        counts = {}
        for error in errors:
            counts[error.error_type] = counts.get(error.error_type, 0) + 1
        return counts
    
    def _identify_problematic_cards(self, errors: List[ErrorContext]) -> List[Tuple[str, int]]:
        """Identify cards with frequent errors"""
        card_counts = {}
        for error in errors:
            card_counts[error.card_id] = card_counts.get(error.card_id, 0) + 1
        return sorted(card_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _identify_problematic_agents(self, errors: List[ErrorContext]) -> List[Tuple[str, int]]:
        """Identify agents with frequent errors"""
        agent_counts = {}
        for error in errors:
            if error.agent_id:
                agent_counts[error.agent_id] = agent_counts.get(error.agent_id, 0) + 1
        return sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _calculate_recovery_success_rate(self) -> float:
        """Calculate overall recovery success rate"""
        total_attempts = 0
        successful_attempts = 0
        
        for attempts in self.recovery_history.values():
            for _, success in attempts:
                total_attempts += 1
                if success:
                    successful_attempts += 1
                    
        if total_attempts == 0:
            return 1.0
            
        return successful_attempts / total_attempts


# Add missing import
import asyncio