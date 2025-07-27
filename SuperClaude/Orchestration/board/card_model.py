"""
Card Data Model for Board-Based Orchestration System
Represents tasks with context preservation and state management
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from enum import Enum
import json
import uuid

class CardStatus(Enum):
    """Card status representing board columns"""
    BACKLOG = "backlog"      # Not yet started
    ACTIVE = "active"        # Currently being worked on by sub-agent
    REVIEW = "review"        # Completed, awaiting validation
    BLOCKED = "blocked"      # Cannot proceed due to dependency/error
    DONE = "done"           # Successfully completed
    FAILED = "failed"       # Failed and cannot be completed

class CardPriority(Enum):
    """Card priority levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class CardType(Enum):
    """Type of task represented by card"""
    ANALYSIS = "analysis"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"

@dataclass
class CardMetrics:
    """Metrics tracking for card performance"""
    token_usage: int = 0
    processing_time: float = 0.0
    tool_calls: int = 0
    mcp_calls: int = 0
    error_count: int = 0
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_usage": self.token_usage,
            "processing_time": self.processing_time,
            "tool_calls": self.tool_calls,
            "mcp_calls": self.mcp_calls,
            "error_count": self.error_count,
            "retry_count": self.retry_count
        }

@dataclass
class CardContext:
    """Context preservation for sub-agent execution"""
    original_request: str
    persona_name: Optional[str] = None
    auto_flags: List[str] = field(default_factory=list)
    user_flags: List[str] = field(default_factory=list)
    mcp_servers: List[str] = field(default_factory=list)
    file_paths: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    parent_card_id: Optional[str] = None
    session_state: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_request": self.original_request,
            "persona_name": self.persona_name,
            "auto_flags": self.auto_flags,
            "user_flags": self.user_flags,
            "mcp_servers": self.mcp_servers,
            "file_paths": self.file_paths,
            "dependencies": self.dependencies,
            "parent_card_id": self.parent_card_id,
            "session_state": self.session_state
        }

@dataclass
class CardResult:
    """Result data from card execution"""
    output: str = ""
    artifacts: List[str] = field(default_factory=list)  # File paths created/modified
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    handoff_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "output": self.output,
            "artifacts": self.artifacts,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "next_steps": self.next_steps,
            "handoff_data": self.handoff_data
        }

@dataclass
class Card:
    """
    Task card representing a unit of work in the board orchestration system.
    Provides context preservation and state management for sub-agent execution.
    """
    
    # Core identification
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    
    # Status and workflow
    status: CardStatus = CardStatus.BACKLOG
    priority: CardPriority = CardPriority.MEDIUM
    card_type: CardType = CardType.IMPLEMENTATION
    
    # Assignment and ownership
    assigned_agent: Optional[str] = None
    created_by: str = "user"
    
    # Context and execution data
    context: CardContext = field(default_factory=CardContext)
    result: CardResult = field(default_factory=CardResult)
    metrics: CardMetrics = field(default_factory=CardMetrics)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_status(self, new_status: CardStatus, reason: str = "") -> None:
        """Update card status with timestamp tracking"""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        # Track status-specific timestamps
        if new_status == CardStatus.ACTIVE and not self.started_at:
            self.started_at = datetime.now()
        elif new_status in [CardStatus.DONE, CardStatus.FAILED] and not self.completed_at:
            self.completed_at = datetime.now()
            
        # Add to metadata for audit trail
        if "status_history" not in self.metadata:
            self.metadata["status_history"] = []
        
        self.metadata["status_history"].append({
            "from": old_status.value,
            "to": new_status.value,
            "timestamp": self.updated_at.isoformat(),
            "reason": reason
        })
    
    def assign_agent(self, agent_name: str) -> None:
        """Assign card to a specific agent"""
        self.assigned_agent = agent_name
        self.updated_at = datetime.now()
        
        # Track assignment history
        if "assignment_history" not in self.metadata:
            self.metadata["assignment_history"] = []
            
        self.metadata["assignment_history"].append({
            "agent": agent_name,
            "timestamp": self.updated_at.isoformat()
        })
    
    def add_error(self, error: str) -> None:
        """Add error to card and update metrics"""
        self.result.errors.append(error)
        self.metrics.error_count += 1
        self.updated_at = datetime.now()
    
    def add_warning(self, warning: str) -> None:
        """Add warning to card"""
        self.result.warnings.append(warning)
        self.updated_at = datetime.now()
    
    def update_metrics(self, **kwargs) -> None:
        """Update card metrics"""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                if key in ['token_usage', 'tool_calls', 'mcp_calls', 'error_count', 'retry_count']:
                    # Accumulate counters
                    setattr(self.metrics, key, getattr(self.metrics, key) + value)
                else:
                    # Direct assignment for other metrics
                    setattr(self.metrics, key, value)
        self.updated_at = datetime.now()
    
    def can_transition_to(self, new_status: CardStatus) -> bool:
        """Check if card can transition to new status"""
        valid_transitions = {
            CardStatus.BACKLOG: [CardStatus.ACTIVE, CardStatus.BLOCKED],
            CardStatus.ACTIVE: [CardStatus.REVIEW, CardStatus.BLOCKED, CardStatus.FAILED],
            CardStatus.REVIEW: [CardStatus.DONE, CardStatus.ACTIVE, CardStatus.FAILED],
            CardStatus.BLOCKED: [CardStatus.ACTIVE, CardStatus.FAILED],
            CardStatus.DONE: [],  # Terminal state
            CardStatus.FAILED: [CardStatus.ACTIVE]  # Allow retry
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
    def is_resource_intensive(self) -> bool:
        """Check if card is likely to consume significant resources"""
        # High token usage or many tool calls indicate resource intensity
        return (
            self.metrics.token_usage > 5000 or
            self.metrics.tool_calls > 20 or
            self.card_type in [CardType.ANALYSIS, CardType.IMPLEMENTATION] and
            self.priority in [CardPriority.HIGH, CardPriority.CRITICAL]
        )
    
    def get_estimated_tokens(self) -> int:
        """Estimate token usage for planning purposes"""
        base_tokens = {
            CardType.ANALYSIS: 3000,
            CardType.IMPLEMENTATION: 5000,
            CardType.TESTING: 2000,
            CardType.DOCUMENTATION: 1500,
            CardType.REFACTORING: 4000,
            CardType.DEBUGGING: 3500
        }
        
        # Adjust based on priority and complexity indicators
        estimate = base_tokens.get(self.card_type, 2000)
        
        if self.priority == CardPriority.CRITICAL:
            estimate *= 1.5
        elif self.priority == CardPriority.HIGH:
            estimate *= 1.2
            
        # Adjust based on context complexity
        if len(self.context.file_paths) > 5:
            estimate *= 1.3
        if len(self.context.dependencies) > 3:
            estimate *= 1.2
            
        return int(estimate)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary for serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "card_type": self.card_type.value,
            "assigned_agent": self.assigned_agent,
            "created_by": self.created_by,
            "context": self.context.to_dict(),
            "result": self.result.to_dict(),
            "metrics": self.metrics.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Card':
        """Create card from dictionary"""
        # Parse timestamps
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"])
        started_at = datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None
        completed_at = datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        
        # Create context
        context_data = data.get("context", {})
        context = CardContext(
            original_request=context_data.get("original_request", ""),
            persona_name=context_data.get("persona_name"),
            auto_flags=context_data.get("auto_flags", []),
            user_flags=context_data.get("user_flags", []),
            mcp_servers=context_data.get("mcp_servers", []),
            file_paths=context_data.get("file_paths", []),
            dependencies=context_data.get("dependencies", []),
            parent_card_id=context_data.get("parent_card_id"),
            session_state=context_data.get("session_state", {})
        )
        
        # Create result
        result_data = data.get("result", {})
        result = CardResult(
            output=result_data.get("output", ""),
            artifacts=result_data.get("artifacts", []),
            errors=result_data.get("errors", []),
            warnings=result_data.get("warnings", []),
            recommendations=result_data.get("recommendations", []),
            next_steps=result_data.get("next_steps", []),
            handoff_data=result_data.get("handoff_data", {})
        )
        
        # Create metrics
        metrics_data = data.get("metrics", {})
        metrics = CardMetrics(
            token_usage=metrics_data.get("token_usage", 0),
            processing_time=metrics_data.get("processing_time", 0.0),
            tool_calls=metrics_data.get("tool_calls", 0),
            mcp_calls=metrics_data.get("mcp_calls", 0),
            error_count=metrics_data.get("error_count", 0),
            retry_count=metrics_data.get("retry_count", 0)
        )
        
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            status=CardStatus(data["status"]),
            priority=CardPriority(data["priority"]),
            card_type=CardType(data["card_type"]),
            assigned_agent=data.get("assigned_agent"),
            created_by=data.get("created_by", "user"),
            context=context,
            result=result,
            metrics=metrics,
            created_at=created_at,
            updated_at=updated_at,
            started_at=started_at,
            completed_at=completed_at,
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )

class CardFactory:
    """Factory for creating cards from user requests"""
    
    @staticmethod
    def create_from_request(
        request: str,
        persona_name: Optional[str] = None,
        priority: CardPriority = CardPriority.MEDIUM,
        card_type: Optional[CardType] = None,
        user_flags: Optional[List[str]] = None,
        file_paths: Optional[List[str]] = None
    ) -> Card:
        """Create a card from a user request"""
        
        # Auto-detect card type if not specified
        if card_type is None:
            card_type = CardFactory._detect_card_type(request)
        
        # Generate title from request
        title = CardFactory._generate_title(request, card_type)
        
        # Create context
        context = CardContext(
            original_request=request,
            persona_name=persona_name,
            user_flags=user_flags or [],
            file_paths=file_paths or []
        )
        
        return Card(
            title=title,
            description=request[:200] + "..." if len(request) > 200 else request,
            priority=priority,
            card_type=card_type,
            context=context
        )
    
    @staticmethod
    def _detect_card_type(request: str) -> CardType:
        """Auto-detect card type from request text"""
        request_lower = request.lower()
        
        # Keywords for different card types
        type_keywords = {
            CardType.ANALYSIS: ["analyze", "review", "investigate", "examine", "study"],
            CardType.IMPLEMENTATION: ["implement", "create", "build", "develop", "add"],
            CardType.TESTING: ["test", "verify", "validate", "check", "qa"],
            CardType.DOCUMENTATION: ["document", "write", "explain", "guide", "readme"],
            CardType.REFACTORING: ["refactor", "cleanup", "improve", "optimize", "restructure"],
            CardType.DEBUGGING: ["debug", "fix", "resolve", "troubleshoot", "error"]
        }
        
        # Count matches for each type
        type_scores = {}
        for card_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in request_lower)
            if score > 0:
                type_scores[card_type] = score
        
        # Return type with highest score, default to implementation
        return max(type_scores.items(), key=lambda x: x[1])[0] if type_scores else CardType.IMPLEMENTATION
    
    @staticmethod
    def _generate_title(request: str, card_type: CardType) -> str:
        """Generate a concise title for the card"""
        # Take first 50 characters and clean up
        title = request[:50].strip()
        
        # Remove common prefixes
        prefixes_to_remove = ["please", "can you", "help me", "i need to", "i want to"]
        title_lower = title.lower()
        
        for prefix in prefixes_to_remove:
            if title_lower.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        # Add ellipsis if truncated
        if len(request) > 50:
            title += "..."
            
        return title or f"{card_type.value.title()} Task"