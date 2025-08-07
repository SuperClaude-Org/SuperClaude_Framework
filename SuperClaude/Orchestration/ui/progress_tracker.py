"""
Progress Tracker for Phase 3: Advanced Orchestration
Provides real-time updates, activity feed, and enhanced visualization
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import time
import threading
import logging

from ..board.card_model import Card, CardStatus
from ..board.board_manager import BoardManager
from ..board.resource_tracker import ResourceTracker
from .board_renderer import BoardRenderer

logger = logging.getLogger(__name__)


class ActivityType(Enum):
    """Types of activities tracked"""
    CARD_CREATED = "card_created"
    CARD_MOVED = "card_moved"
    AGENT_ASSIGNED = "agent_assigned"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    INTEGRATION_STARTED = "integration_started"
    INTEGRATION_COMPLETED = "integration_completed"
    CONFLICT_DETECTED = "conflict_detected"
    RESOURCE_WARNING = "resource_warning"
    HANDOFF_TRIGGERED = "handoff_triggered"


@dataclass
class Activity:
    """Single activity in the feed"""
    timestamp: datetime
    activity_type: ActivityType
    agent_id: Optional[str]
    card_id: Optional[str]
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class AgentProgress:
    """Track progress for a single agent"""
    agent_id: str
    card_id: str
    status: str
    progress_percentage: int = 0
    current_action: str = ""
    eta_seconds: Optional[int] = None
    started_at: Optional[datetime] = None
    tokens_used: int = 0
    

class ProgressTracker:
    """
    Real-time progress tracking and activity monitoring for the board system.
    Provides enhanced visualization with live updates and activity feed.
    """
    
    def __init__(self, board_manager: BoardManager, update_interval: int = 2):
        self.board = board_manager
        self.renderer = BoardRenderer()
        self.update_interval = update_interval
        
        # Activity tracking
        self.activities = deque(maxlen=100)  # Keep last 100 activities
        self.agent_progress: Dict[str, AgentProgress] = {}
        
        # Update thread
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
        
        # Performance metrics
        self.render_times: deque = deque(maxlen=10)
        self.last_render_time = 0.0
        
    def start_tracking(self):
        """Start the progress tracking thread"""
        if self.running:
            return
            
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info("Progress tracking started")
        
    def stop_tracking(self):
        """Stop the progress tracking thread"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        logger.info("Progress tracking stopped")
        
    def add_activity(self, 
                    activity_type: ActivityType,
                    description: str,
                    agent_id: Optional[str] = None,
                    card_id: Optional[str] = None,
                    **details):
        """Add an activity to the feed"""
        activity = Activity(
            timestamp=datetime.now(),
            activity_type=activity_type,
            agent_id=agent_id,
            card_id=card_id,
            description=description,
            details=details
        )
        self.activities.append(activity)
        
    def update_agent_progress(self,
                            agent_id: str,
                            card_id: str,
                            progress: int,
                            current_action: str,
                            eta_seconds: Optional[int] = None):
        """Update progress for a specific agent"""
        if agent_id not in self.agent_progress:
            self.agent_progress[agent_id] = AgentProgress(
                agent_id=agent_id,
                card_id=card_id,
                status="active",
                started_at=datetime.now()
            )
            
        agent_prog = self.agent_progress[agent_id]
        agent_prog.progress_percentage = min(100, max(0, progress))
        agent_prog.current_action = current_action
        agent_prog.eta_seconds = eta_seconds
        
        # Get token usage from card
        card = self.board.get_card(card_id)
        if card:
            agent_prog.tokens_used = card.metrics.token_usage
            
    def render_board_with_progress(self) -> str:
        """Render the board with real-time progress indicators"""
        start_time = time.time()
        
        # Get board state
        board_status = self.board.get_board_status()
        
        # Build enhanced visualization
        output = []
        
        # Header with resource meters
        resource_status = board_status["workflow"]["resource_status"]
        header = self._render_header(resource_status)
        output.append(header)
        
        # Column headers with counts
        column_headers = self._render_column_headers(board_status)
        output.append(column_headers)
        
        # Cards with progress indicators
        cards_display = self._render_cards_with_progress(board_status)
        output.append(cards_display)
        
        # Activity feed
        activity_feed = self._render_activity_feed()
        output.append(activity_feed)
        
        # Performance metrics
        render_time = time.time() - start_time
        self.render_times.append(render_time)
        self.last_render_time = render_time
        
        return "\n".join(output)
        
    def _render_header(self, resource_status: Dict[str, Any]) -> str:
        """Render header with resource information"""
        active_agents = len(self.agent_progress)
        token_usage = resource_status.get("total_token_usage", 0)
        token_limit = resource_status.get("token_limit", 20000)
        token_percentage = (token_usage / token_limit) * 100
        
        # Determine color/alert based on usage
        if token_percentage >= 85:
            alert = "🚨 CRITICAL"
        elif token_percentage >= 70:
            alert = "⚠️  WARNING"
        else:
            alert = "✅ HEALTHY"
            
        header = f"""
Board: Advanced Multi-Agent Orchestration | Agents: {active_agents}/3 | Tokens: {token_usage:,}/{token_limit:,} ({token_percentage:.1f}%) | Status: {alert}
{'━' * 100}
"""
        return header.strip()
        
    def _render_column_headers(self, board_status: Dict[str, Any]) -> str:
        """Render column headers with card counts"""
        columns = ["TODO", "IN_PROGRESS", "REVIEW", "INTEGRATE", "DONE"]
        headers = []
        
        # Map internal status names to display names
        status_map = {
            "BACKLOG": "TODO",
            "TODO": "TODO",
            "ACTIVE": "IN_PROGRESS",
            "IN_PROGRESS": "IN_PROGRESS",
            "REVIEW": "REVIEW",
            "INTEGRATE": "INTEGRATE",
            "DONE": "DONE"
        }
        
        card_counts = board_status["workflow"]["card_counts"]
        
        for col in columns:
            # Get count for this column
            internal_status = {v: k for k, v in status_map.items()}.get(col, col.lower())
            count = card_counts.get(internal_status, 0)
            
            # Format header
            header = f"{col} ({count})"
            headers.append(f"{header:<20}")
            
        return " ".join(headers)
        
    def _render_cards_with_progress(self, board_status: Dict[str, Any]) -> str:
        """Render cards with progress indicators"""
        output = []
        output.append("─" * 20 + " " + "─" * 20 + " " + "─" * 20 + " " + "─" * 20 + " " + "─" * 20)
        
        # Get cards by column
        cards_by_column = {
            "TODO": [],
            "IN_PROGRESS": [],
            "REVIEW": [],
            "INTEGRATE": [],
            "DONE": []
        }
        
        # Map cards to columns
        for card_id, card in self.board.board_state.cards.items():
            if card.status == CardStatus.BACKLOG:
                cards_by_column["TODO"].append(card)
            elif card.status == CardStatus.ACTIVE:
                cards_by_column["IN_PROGRESS"].append(card)
            elif card.status == CardStatus.REVIEW:
                cards_by_column["REVIEW"].append(card)
            elif card.status == CardStatus.INTEGRATE:
                cards_by_column["INTEGRATE"].append(card)
            elif card.status == CardStatus.DONE:
                cards_by_column["DONE"].append(card)
                
        # Find max cards in any column for row alignment
        max_cards = max(len(cards) for cards in cards_by_column.values())
        
        # Render each row
        for i in range(max_cards):
            row = []
            for col in ["TODO", "IN_PROGRESS", "REVIEW", "INTEGRATE", "DONE"]:
                if i < len(cards_by_column[col]):
                    card = cards_by_column[col][i]
                    card_display = self._render_card_with_progress(card, col)
                    row.append(card_display)
                else:
                    row.append(" " * 20)
                    
            output.append(" ".join(row))
            
        return "\n".join(output)
        
    def _render_card_with_progress(self, card: Card, column: str) -> str:
        """Render a single card with progress indicator"""
        # Basic card info
        card_str = f"[{card.id}] {card.title[:12]}"
        
        # Add progress for active cards
        if column == "IN_PROGRESS" and card.assigned_agent in self.agent_progress:
            progress = self.agent_progress[card.assigned_agent]
            
            # Progress bar
            bar_length = 10
            filled = int((progress.progress_percentage / 100) * bar_length)
            bar = "▓" * filled + "░" * (bar_length - filled)
            
            # ETA
            eta_str = ""
            if progress.eta_seconds:
                if progress.eta_seconds < 60:
                    eta_str = f"{progress.eta_seconds}s"
                else:
                    eta_str = f"{progress.eta_seconds // 60}m"
                    
            card_str = f"{card_str[:17]}\n{bar} {progress.progress_percentage}%"
            if eta_str:
                card_str += f" | {eta_str}"
                
        # Add agent info
        elif card.assigned_agent:
            card_str += f"\nAgent: @{card.assigned_agent[:8]}"
            
        # Add status for integration
        elif column == "INTEGRATE" and card.contributing_agents:
            active_count = sum(1 for a in card.contributing_agents if a in self.agent_progress)
            total_count = len(card.contributing_agents)
            card_str += f"\nAgents: {active_count}/{total_count}"
            
        # Ensure fixed width
        lines = card_str.split("\n")
        formatted_lines = [line[:20].ljust(20) for line in lines[:2]]  # Max 2 lines
        
        return "\n".join(formatted_lines)
        
    def _render_activity_feed(self) -> str:
        """Render the activity feed"""
        output = []
        output.append("=" * 100)
        output.append("Activity Feed:")
        
        # Get last 5 activities
        recent_activities = list(self.activities)[-5:]
        
        for activity in recent_activities:
            time_str = activity.timestamp.strftime("%H:%M:%S")
            
            # Format based on activity type
            if activity.agent_id:
                actor = f"@{activity.agent_id}"
            else:
                actor = "System"
                
            line = f"{time_str} {actor}: {activity.description}"
            
            # Add details if available
            if activity.details:
                if "progress" in activity.details:
                    line += f" ({activity.details['progress']}%)"
                if "tokens" in activity.details:
                    line += f" [Tokens: {activity.details['tokens']}]"
                    
            output.append(line)
            
        return "\n".join(output)
        
    def _update_loop(self):
        """Background thread that updates progress"""
        while self.running:
            try:
                # Update agent progress based on card metrics
                for agent_id, card_id in self.board.board_state.active_agents.items():
                    card = self.board.get_card(card_id)
                    if card and card.status == CardStatus.ACTIVE:
                        # Estimate progress based on time elapsed
                        if card.started_at:
                            elapsed = (datetime.now() - card.started_at).total_seconds()
                            estimated_duration = 300  # 5 minutes estimate
                            progress = min(95, int((elapsed / estimated_duration) * 100))
                            
                            self.update_agent_progress(
                                agent_id=agent_id,
                                card_id=card_id,
                                progress=progress,
                                current_action="Processing...",
                                eta_seconds=max(0, int(estimated_duration - elapsed))
                            )
                            
                # Clean up completed agents
                completed_agents = []
                for agent_id, progress in self.agent_progress.items():
                    card = self.board.get_card(progress.card_id)
                    if card and card.status != CardStatus.ACTIVE:
                        completed_agents.append(agent_id)
                        
                for agent_id in completed_agents:
                    del self.agent_progress[agent_id]
                    
            except Exception as e:
                logger.error(f"Error in progress update loop: {e}")
                
            time.sleep(self.update_interval)
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the progress tracker"""
        avg_render_time = sum(self.render_times) / len(self.render_times) if self.render_times else 0
        
        return {
            "avg_render_time_ms": avg_render_time * 1000,
            "last_render_time_ms": self.last_render_time * 1000,
            "active_agents": len(self.agent_progress),
            "activity_count": len(self.activities),
            "update_interval": self.update_interval
        }