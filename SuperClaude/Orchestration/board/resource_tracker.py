"""
Resource Tracker for Board-Based Orchestration System
CRITICAL SAFETY COMPONENT: Prevents resource exhaustion and enforces limits
Addresses the 88K token crisis from P2SA v1.1
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import threading
import time

class ResourceAlert(Enum):
    """Resource alert levels"""
    GREEN = "green"      # 0-60% usage
    YELLOW = "yellow"    # 60-75% usage  
    ORANGE = "orange"    # 75-85% usage
    RED = "red"         # 85-95% usage
    CRITICAL = "critical" # 95%+ usage

class ResourceType(Enum):
    """Types of resources to track"""
    TOKENS = "tokens"
    ACTIVE_CARDS = "active_cards"
    MCP_CALLS = "mcp_calls"
    TOOL_CALLS = "tool_calls"
    PROCESSING_TIME = "processing_time"

@dataclass
class ResourceLimits:
    """Resource limits configuration with graceful handoff protocol"""
    # HARD LIMITS - Absolute maximum (for emergency fallback)
    max_active_cards: int = 3           # Max concurrent sub-agents
    max_token_budget: int = 20000       # Conservative token limit per session
    max_mcp_calls_per_min: int = 30     # Rate limiting for MCP servers
    max_tool_calls_per_card: int = 50   # Prevent infinite loops
    max_processing_time: int = 600      # 10 minutes max per card
    max_session_duration: int = 3600    # 1 hour max session
    
    # EFFECTIVE LIMITS - Reserve buffer for graceful handoff operations
    effective_active_cards: float = 2.5    # Reserve 0.5 for handoff operations
    effective_token_budget: int = 17000     # Reserve 3K for compression/transfer
    handoff_buffer_tokens: int = 3000       # Reserved for context compression and agent spawning
    
    # Graduated thresholds for graceful resource management
    yellow_threshold: float = 0.60      # Start optimization (--uc mode)
    orange_threshold: float = 0.75      # Prepare handoff, compress context  
    red_threshold: float = 0.85         # Execute graceful handoff
    critical_threshold: float = 0.95    # Emergency protocols (last resort)

@dataclass 
class ResourceUsage:
    """Current resource usage tracking"""
    active_cards: int = 0
    token_usage: int = 0
    mcp_calls_last_minute: int = 0
    total_tool_calls: int = 0
    session_start_time: datetime = field(default_factory=datetime.now)
    last_mcp_call_times: List[datetime] = field(default_factory=list)
    card_processing_times: Dict[str, float] = field(default_factory=dict)
    # Graceful handoff tracking
    handoff_in_progress: bool = False
    handoff_operations: List[str] = field(default_factory=list)  # Track active handoffs
    compression_mode: bool = False  # Auto-enable --uc mode
    
    def get_session_duration(self) -> float:
        """Get current session duration in seconds"""
        return (datetime.now() - self.session_start_time).total_seconds()

@dataclass
class ResourceViolation:
    """Resource limit violation record"""
    resource_type: ResourceType
    limit_value: float
    actual_value: float
    timestamp: datetime
    card_id: Optional[str] = None
    action_taken: str = ""
    recovery_successful: bool = False

class ResourceTracker:
    """
    CRITICAL SAFETY COMPONENT
    
    Tracks and enforces resource limits to prevent system overload.
    Implements hard limits, soft warnings, and graceful degradation.
    """
    
    def __init__(self, limits: Optional[ResourceLimits] = None):
        self.limits = limits or ResourceLimits()
        self.usage = ResourceUsage()
        self.violations: List[ResourceViolation] = []
        self.alert_level = ResourceAlert.GREEN
        self.emergency_mode = False
        self.lock = threading.Lock()
        
        # Initialize MCP call tracking
        self._cleanup_old_mcp_calls()
    
    def check_resource_availability(self, card_id: str, estimated_tokens: int = 0) -> Tuple[bool, List[str]]:
        """
        Check if resources are available for a new card using effective limits.
        Returns (can_proceed, warnings)
        """
        with self.lock:
            warnings = []
            
            # Use effective limits (with buffer reserved for handoff operations)
            effective_card_limit = self.limits.effective_active_cards
            effective_token_limit = self.limits.effective_token_budget
            
            # Check active card limit against effective limit
            if self.usage.active_cards >= effective_card_limit:
                # Check if we can use handoff buffer
                if self.usage.active_cards >= self.limits.max_active_cards:
                    return False, [f"Maximum active cards reached ({self.limits.max_active_cards})"]
                else:
                    warnings.append("Approaching card limit - graceful handoff may be triggered")
            
            # Check token budget against effective limit
            projected_usage = self.usage.token_usage + estimated_tokens
            if projected_usage > effective_token_limit:
                # Check if we can use handoff buffer
                if projected_usage > self.limits.max_token_budget:
                    return False, [f"Token budget would be exceeded. Current: {self.usage.token_usage}, Estimated: {estimated_tokens}, Limit: {self.limits.max_token_budget}"]
                else:
                    warnings.append("Approaching token limit - graceful handoff may be triggered")
            
            # Check session duration
            session_duration = self.usage.get_session_duration()
            if session_duration > self.limits.max_session_duration:
                return False, [f"Session duration limit reached ({self.limits.max_session_duration}s)"]
            
            # Check if in emergency mode
            if self.emergency_mode:
                return False, ["System in emergency mode due to resource violations"]
            
            # Auto-enable compression mode if in yellow zone
            self._check_and_enable_compression()
            
            # Generate warnings for approaching limits
            warnings.extend(self._generate_warnings(estimated_tokens))
            
            return True, warnings
    
    def allocate_card_resources(self, card_id: str) -> bool:
        """Allocate resources for a new active card"""
        with self.lock:
            if self.usage.active_cards >= self.limits.max_active_cards:
                self._record_violation(
                    ResourceType.ACTIVE_CARDS,
                    self.limits.max_active_cards,
                    self.usage.active_cards + 1,
                    card_id
                )
                return False
            
            self.usage.active_cards += 1
            self.usage.card_processing_times[card_id] = time.time()
            self._update_alert_level()
            return True
    
    def release_card_resources(self, card_id: str, final_metrics: Optional[Dict] = None) -> None:
        """Release resources when card completes"""
        with self.lock:
            if self.usage.active_cards > 0:
                self.usage.active_cards -= 1
            
            # Record processing time
            if card_id in self.usage.card_processing_times:
                processing_time = time.time() - self.usage.card_processing_times[card_id]
                del self.usage.card_processing_times[card_id]
                
                # Check processing time limit
                if processing_time > self.limits.max_processing_time:
                    self._record_violation(
                        ResourceType.PROCESSING_TIME,
                        self.limits.max_processing_time,
                        processing_time,
                        card_id
                    )
            
            # Update token usage if metrics provided
            if final_metrics and 'token_usage' in final_metrics:
                self.usage.token_usage += final_metrics['token_usage']
                if 'tool_calls' in final_metrics:
                    self.usage.total_tool_calls += final_metrics['tool_calls']
            
            self._update_alert_level()
    
    def track_mcp_call(self) -> bool:
        """Track an MCP call and check rate limits"""
        with self.lock:
            now = datetime.now()
            self.usage.last_mcp_call_times.append(now)
            
            # Clean up old calls
            self._cleanup_old_mcp_calls()
            
            # Check rate limit
            calls_last_minute = len(self.usage.last_mcp_call_times)
            if calls_last_minute > self.limits.max_mcp_calls_per_min:
                self._record_violation(
                    ResourceType.MCP_CALLS,
                    self.limits.max_mcp_calls_per_min,
                    calls_last_minute
                )
                return False
            
            self.usage.mcp_calls_last_minute = calls_last_minute
            return True
    
    def check_token_usage(self, additional_tokens: int, card_id: Optional[str] = None) -> bool:
        """Check if additional token usage is allowed"""
        with self.lock:
            new_total = self.usage.token_usage + additional_tokens
            
            if new_total > self.limits.max_token_budget:
                self._record_violation(
                    ResourceType.TOKENS,
                    self.limits.max_token_budget,
                    new_total,
                    card_id
                )
                return False
            
            return True
    
    def get_resource_status(self) -> Dict[str, any]:
        """Get current resource status and metrics"""
        with self.lock:
            session_duration = self.usage.get_session_duration()
            
            # Calculate usage percentages
            active_cards_pct = (self.usage.active_cards / self.limits.max_active_cards) * 100
            token_usage_pct = (self.usage.token_usage / self.limits.max_token_budget) * 100
            session_duration_pct = (session_duration / self.limits.max_session_duration) * 100
            mcp_calls_pct = (self.usage.mcp_calls_last_minute / self.limits.max_mcp_calls_per_min) * 100
            
            return {
                "alert_level": self.alert_level.value,
                "emergency_mode": self.emergency_mode,
                "usage": {
                    "active_cards": {
                        "current": self.usage.active_cards,
                        "limit": self.limits.max_active_cards,
                        "percentage": active_cards_pct
                    },
                    "tokens": {
                        "current": self.usage.token_usage,
                        "limit": self.limits.max_token_budget,
                        "percentage": token_usage_pct
                    },
                    "session_duration": {
                        "current": session_duration,
                        "limit": self.limits.max_session_duration,
                        "percentage": session_duration_pct
                    },
                    "mcp_calls_per_minute": {
                        "current": self.usage.mcp_calls_last_minute,
                        "limit": self.limits.max_mcp_calls_per_min,
                        "percentage": mcp_calls_pct
                    },
                    "total_tool_calls": self.usage.total_tool_calls
                },
                "violations": len(self.violations),
                "last_violation": self.violations[-1].__dict__ if self.violations else None
            }
    
    def get_available_capacity(self) -> Dict[str, int]:
        """Get remaining capacity for each resource type"""
        with self.lock:
            return {
                "active_cards": max(0, self.limits.max_active_cards - self.usage.active_cards),
                "tokens": max(0, self.limits.max_token_budget - self.usage.token_usage),
                "mcp_calls": max(0, self.limits.max_mcp_calls_per_min - self.usage.mcp_calls_last_minute),
                "session_time": max(0, self.limits.max_session_duration - self.usage.get_session_duration())
            }
    
    def force_emergency_mode(self, reason: str) -> None:
        """Force system into emergency mode"""
        with self.lock:
            self.emergency_mode = True
            self.alert_level = ResourceAlert.CRITICAL
            
            # Record as violation
            violation = ResourceViolation(
                resource_type=ResourceType.TOKENS,  # Generic
                limit_value=0,
                actual_value=0,
                timestamp=datetime.now(),
                action_taken=f"Emergency mode activated: {reason}"
            )
            self.violations.append(violation)
    
    def reset_emergency_mode(self) -> None:
        """Reset emergency mode if conditions are safe"""
        with self.lock:
            if self.emergency_mode:
                # Check if conditions are safe
                if (self.usage.active_cards == 0 and 
                    self.usage.token_usage < self.limits.max_token_budget * 0.5):
                    self.emergency_mode = False
                    self._update_alert_level()
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations based on current resource usage"""
        recommendations = []
        status = self.get_resource_status()
        
        # Active cards recommendations
        if status["usage"]["active_cards"]["percentage"] > 80:
            recommendations.append("Consider reducing concurrent tasks to improve performance")
        
        # Token usage recommendations  
        token_pct = status["usage"]["tokens"]["percentage"]
        if token_pct > 80:
            recommendations.append("Enable --uc flag to reduce token usage")
        elif token_pct > 60:
            recommendations.append("Consider using more efficient personas or tools")
        
        # Session duration recommendations
        if status["usage"]["session_duration"]["percentage"] > 80:
            recommendations.append("Consider breaking work into multiple sessions")
        
        # MCP call rate recommendations
        if status["usage"]["mcp_calls_per_minute"]["percentage"] > 80:
            recommendations.append("Reduce MCP server usage or implement caching")
        
        # Emergency mode recommendations
        if self.emergency_mode:
            recommendations.append("System in emergency mode - complete current tasks and restart session")
        
        return recommendations
    
    def _cleanup_old_mcp_calls(self) -> None:
        """Remove MCP calls older than 1 minute"""
        cutoff = datetime.now() - timedelta(minutes=1)
        self.usage.last_mcp_call_times = [
            call_time for call_time in self.usage.last_mcp_call_times 
            if call_time > cutoff
        ]
        self.usage.mcp_calls_last_minute = len(self.usage.last_mcp_call_times)
    
    def _update_alert_level(self) -> None:
        """Update alert level based on current usage"""
        max_percentage = 0
        
        # Calculate max usage percentage across all resources
        if self.limits.max_active_cards > 0:
            max_percentage = max(max_percentage, 
                               (self.usage.active_cards / self.limits.max_active_cards))
        
        if self.limits.max_token_budget > 0:
            max_percentage = max(max_percentage, 
                               (self.usage.token_usage / self.limits.max_token_budget))
        
        session_duration = self.usage.get_session_duration()
        if self.limits.max_session_duration > 0:
            max_percentage = max(max_percentage, 
                               (session_duration / self.limits.max_session_duration))
        
        if self.limits.max_mcp_calls_per_min > 0:
            max_percentage = max(max_percentage, 
                               (self.usage.mcp_calls_last_minute / self.limits.max_mcp_calls_per_min))
        
        # Determine alert level
        if max_percentage >= self.limits.critical_threshold:
            self.alert_level = ResourceAlert.CRITICAL
            if max_percentage >= 1.0:  # Over 100% usage
                self.emergency_mode = True
        elif max_percentage >= self.limits.red_threshold:
            self.alert_level = ResourceAlert.RED
        elif max_percentage >= self.limits.orange_threshold:
            self.alert_level = ResourceAlert.ORANGE
        elif max_percentage >= self.limits.yellow_threshold:
            self.alert_level = ResourceAlert.YELLOW
        else:
            self.alert_level = ResourceAlert.GREEN
    
    def _generate_warnings(self, estimated_tokens: int = 0) -> List[str]:
        """Generate warnings based on current usage"""
        warnings = []
        
        # Token usage warnings
        projected_tokens = self.usage.token_usage + estimated_tokens
        token_percentage = projected_tokens / self.limits.max_token_budget
        
        if token_percentage > self.limits.orange_threshold:
            warnings.append(f"High token usage projected: {projected_tokens}/{self.limits.max_token_budget} ({token_percentage:.1%})")
        
        # Active cards warnings
        if self.usage.active_cards >= self.limits.max_active_cards - 1:
            warnings.append("Approaching maximum active cards limit")
        
        # Session duration warnings  
        session_duration = self.usage.get_session_duration()
        duration_percentage = session_duration / self.limits.max_session_duration
        
        if duration_percentage > self.limits.orange_threshold:
            warnings.append(f"Long session duration: {session_duration:.0f}s ({duration_percentage:.1%})")
        
        return warnings
    
    def check_handoff_trigger(self, card_id: str) -> Tuple[bool, str]:
        """Check if graceful handoff should be triggered for a card"""
        with self.lock:
            # Calculate current resource usage percentages
            token_percentage = self.usage.token_usage / self.limits.effective_token_budget
            card_percentage = self.usage.active_cards / self.limits.effective_active_cards
            
            # Trigger handoff at red threshold (85%)
            if token_percentage >= self.limits.red_threshold or card_percentage >= self.limits.red_threshold:
                return True, f"Resource usage critical: tokens={token_percentage:.1%}, cards={card_percentage:.1%}"
            
            return False, ""
    
    def prepare_handoff(self, card_id: str) -> bool:
        """Prepare for graceful handoff operation"""
        with self.lock:
            if self.usage.handoff_in_progress:
                return False  # Only one handoff at a time
            
            # Check if we have buffer capacity for handoff
            if self.usage.token_usage + self.limits.handoff_buffer_tokens > self.limits.max_token_budget:
                return False  # Not enough buffer space
            
            self.usage.handoff_in_progress = True
            self.usage.handoff_operations.append(card_id)
            return True
    
    def complete_handoff(self, old_card_id: str, new_card_id: str) -> None:
        """Complete graceful handoff operation"""
        with self.lock:
            # Remove old card from tracking
            if old_card_id in self.usage.handoff_operations:
                self.usage.handoff_operations.remove(old_card_id)
            
            # Reset handoff flag if no more operations
            if not self.usage.handoff_operations:
                self.usage.handoff_in_progress = False
    
    def _check_and_enable_compression(self) -> None:
        """Auto-enable compression mode based on resource usage"""
        # Calculate max usage percentage
        token_percentage = self.usage.token_usage / self.limits.effective_token_budget
        
        # Enable compression in yellow zone (60%)
        if token_percentage >= self.limits.yellow_threshold:
            if not self.usage.compression_mode:
                self.usage.compression_mode = True
        else:
            self.usage.compression_mode = False
    
    def _record_violation(self, resource_type: ResourceType, limit: float, 
                         actual: float, card_id: Optional[str] = None) -> None:
        """Record a resource limit violation"""
        violation = ResourceViolation(
            resource_type=resource_type,
            limit_value=limit,
            actual_value=actual,
            timestamp=datetime.now(),
            card_id=card_id,
            action_taken="Request blocked"
        )
        
        self.violations.append(violation)
        
        # Auto-trigger emergency mode for critical violations
        if actual >= limit * 1.2:  # 20% over limit
            self.emergency_mode = True
            violation.action_taken = "Emergency mode activated"

# Global resource tracker instance
_global_tracker: Optional[ResourceTracker] = None

def get_resource_tracker() -> ResourceTracker:
    """Get the global resource tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ResourceTracker()
    return _global_tracker

def reset_resource_tracker(limits: Optional[ResourceLimits] = None) -> ResourceTracker:
    """Reset the global resource tracker with new limits"""
    global _global_tracker
    _global_tracker = ResourceTracker(limits)
    return _global_tracker