"""
Card Formatter - Helper for consistent card visualization

Provides formatting utilities for cards in different contexts:
- Compact view for board display
- Detailed view for inspection
- Status updates and notifications
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..board.card_model import TaskCard, CardStatus


class CardFormatter:
    """Formatting utilities for task card display"""
    
    # Formatting constants
    MAX_TITLE_LENGTH = 50
    MAX_CONTEXT_LENGTH = 100
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Visual indicators
    PRIORITY_COLORS = {
        'critical': '🔴',
        'high': '🟡', 
        'medium': '🟢',
        'low': '⚪'
    }
    
    STATUS_COLORS = {
        CardStatus.BACKLOG: '📋',
        CardStatus.TODO: '📝',
        CardStatus.IN_PROGRESS: '🔄',
        CardStatus.INTEGRATE: '🔗',
        CardStatus.REVIEW: '👁️',
        CardStatus.DONE: '✅',
        CardStatus.FAILED: '❌',
        CardStatus.BLOCKED: '🚧'
    }
    
    AGENT_TYPES = {
        'architect': '🏗️',
        'frontend': '🎨',
        'backend': '⚙️',
        'security': '🛡️',
        'qa': '🧪',
        'analyzer': '🔍',
        'performance': '⚡',
        'refactorer': '🔧',
        'devops': '🚀',
        'mentor': '📚',
        'scribe': '✍️'
    }
    
    @classmethod
    def format_compact(cls, card: TaskCard, width: int = 25) -> List[str]:
        """Format card for compact board display"""
        lines = []
        
        # Header with priority and ID
        priority_icon = cls.PRIORITY_COLORS.get(card.priority, '⚪')
        header = f"{priority_icon} {card.id[:8]}"
        lines.append(header.ljust(width))
        
        # Title (truncated if needed)
        title = cls._truncate(card.title, width - 2)
        lines.append(title.ljust(width))
        
        # Agent assignment
        if card.assigned_agent:
            agent_type = cls._detect_agent_type(card.assigned_agent)
            agent_icon = cls.AGENT_TYPES.get(agent_type, '👤')
            agent_name = cls._truncate(card.assigned_agent, width - 4)
            lines.append(f"{agent_icon} {agent_name}".ljust(width))
        else:
            lines.append("👤 Unassigned".ljust(width))
            
        # Status indicator
        status_line = cls._format_status_line(card, width)
        lines.append(status_line.ljust(width))
        
        return lines
    
    @classmethod
    def format_detailed(cls, card: TaskCard) -> str:
        """Format card for detailed inspection"""
        status_icon = cls.STATUS_COLORS.get(card.status, '❓')
        priority_icon = cls.PRIORITY_COLORS.get(card.priority, '⚪')
        
        sections = []
        
        # Basic information
        sections.append(cls._format_section("Basic Information", [
            f"ID:         {card.id}",
            f"Title:      {card.title}",
            f"Status:     {status_icon} {card.status.value}",
            f"Priority:   {priority_icon} {card.priority}",
            f"Created:    {card.created_at}",
            f"Updated:    {card.updated_at}"
        ]))
        
        # Assignment and context
        agent_info = "Unassigned"
        if card.assigned_agent:
            agent_type = cls._detect_agent_type(card.assigned_agent)
            agent_icon = cls.AGENT_TYPES.get(agent_type, '👤')
            agent_info = f"{agent_icon} {card.assigned_agent}"
            
        sections.append(cls._format_section("Assignment & Context", [
            f"Agent:      {agent_info}",
            f"Context:    {cls._wrap_text(card.context or 'No context', 60, 12)}"
        ]))
        
        # Resource usage
        resource_lines = [
            f"Tokens:     {card.token_usage or 0:,} used"
        ]
        
        if card.allowed_tools:
            tools_str = ', '.join(card.allowed_tools[:5])
            if len(card.allowed_tools) > 5:
                tools_str += f" (+{len(card.allowed_tools) - 5} more)"
            resource_lines.append(f"Tools:      {tools_str}")
        else:
            resource_lines.append("Tools:      All available")
            
        sections.append(cls._format_section("Resources", resource_lines))
        
        # Dependencies and blocks
        if card.dependencies or card.blocked_by:
            dep_lines = []
            if card.dependencies:
                dep_lines.append(f"Depends on: {', '.join(card.dependencies)}")
            if card.blocked_by:
                dep_lines.append(f"Blocked by: {', '.join(card.blocked_by)}")
            sections.append(cls._format_section("Dependencies", dep_lines))
            
        # Errors
        if card.error_count > 0:
            error_lines = [f"Error count: {card.error_count}"]
            if card.error_log:
                error_lines.append("Recent errors:")
                for error in card.error_log[-5:]:  # Last 5 errors
                    error_lines.append(f"  • {cls._truncate(error, 70)}")
            sections.append(cls._format_section("Errors", error_lines))
            
        # Metadata
        if card.metadata:
            meta_lines = []
            for key, value in card.metadata.items():
                meta_lines.append(f"{key}: {value}")
            sections.append(cls._format_section("Metadata", meta_lines))
            
        return '\n\n'.join(sections)
    
    @classmethod
    def format_status_update(cls, card: TaskCard, old_status: CardStatus, 
                           new_status: CardStatus, reason: Optional[str] = None) -> str:
        """Format a status change notification"""
        old_icon = cls.STATUS_COLORS.get(old_status, '❓')
        new_icon = cls.STATUS_COLORS.get(new_status, '❓')
        
        lines = [
            f"📢 Card Status Update",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Card: {card.id[:8]} - {card.title}",
            f"Status: {old_icon} {old_status.value} → {new_icon} {new_status.value}"
        ]
        
        if card.assigned_agent:
            agent_type = cls._detect_agent_type(card.assigned_agent)
            agent_icon = cls.AGENT_TYPES.get(agent_type, '👤')
            lines.append(f"Agent: {agent_icon} {card.assigned_agent}")
            
        if reason:
            lines.append(f"Reason: {reason}")
            
        lines.append(f"Time: {datetime.now().strftime(cls.TIME_FORMAT)}")
        
        return '\n'.join(lines)
    
    @classmethod
    def format_error_notification(cls, card: TaskCard, error: str) -> str:
        """Format an error notification"""
        lines = [
            f"⚠️  Error on Card {card.id[:8]}",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"Card: {card.title}",
            f"Error: {error}",
            f"Error Count: {card.error_count}",
            f"Status: {cls.STATUS_COLORS.get(card.status, '❓')} {card.status.value}"
        ]
        
        if card.assigned_agent:
            lines.append(f"Agent: {card.assigned_agent}")
            
        return '\n'.join(lines)
    
    @classmethod
    def format_queue_position(cls, position: int, total: int) -> str:
        """Format queue position indicator"""
        if position == 1:
            return f"🎯 Next in queue (1/{total})"
        else:
            return f"⏳ Queue position: {position}/{total}"
    
    @classmethod
    def format_progress_bar(cls, current: int, total: int, width: int = 20) -> str:
        """Format a progress bar"""
        if total == 0:
            return "[" + "━" * width + "]"
            
        percent = current / total
        filled = int(percent * width)
        
        if percent >= 1.0:
            bar = "█" * width
            color = "🟢"
        elif percent >= 0.7:
            bar = "█" * filled + "▒" * (width - filled)
            color = "🟡"
        else:
            bar = "█" * filled + "░" * (width - filled)
            color = "🔵"
            
        return f"{color} [{bar}] {percent*100:.0f}%"
    
    @classmethod
    def _truncate(cls, text: str, max_length: int) -> str:
        """Truncate text with ellipsis if needed"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @classmethod
    def _wrap_text(cls, text: str, width: int, indent: int = 0) -> str:
        """Wrap text to specified width with indentation"""
        if not text:
            return ""
            
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > width:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    # Word is too long, truncate it
                    lines.append(word[:width-3] + "...")
                    current_line = []
                    current_length = 0
            else:
                current_line.append(word)
                current_length += len(word) + 1
                
        if current_line:
            lines.append(' '.join(current_line))
            
        # Add indentation to wrapped lines
        if indent > 0 and len(lines) > 1:
            lines = [lines[0]] + [' ' * indent + line for line in lines[1:]]
            
        return '\n'.join(lines)
    
    @classmethod
    def _detect_agent_type(cls, agent_name: str) -> Optional[str]:
        """Detect agent type from name"""
        agent_lower = agent_name.lower()
        for agent_type in cls.AGENT_TYPES:
            if agent_type in agent_lower:
                return agent_type
        return None
    
    @classmethod
    def _format_status_line(cls, card: TaskCard, width: int) -> str:
        """Format the status line for a card"""
        if card.error_count > 0:
            return f"⚠️  {card.error_count} error{'s' if card.error_count > 1 else ''}"
        elif card.blocked_by:
            return "🚧 Blocked"
        elif card.status == CardStatus.IN_PROGRESS and card.token_usage:
            # Assume 5K token budget per card
            percent = min((card.token_usage / 5000) * 100, 100)
            return f"📊 {percent:.0f}% tokens"
        elif card.status == CardStatus.DONE:
            return "✅ Complete"
        elif card.status == CardStatus.FAILED:
            return "❌ Failed"
        else:
            return "⏳ Waiting"
    
    @classmethod
    def _format_section(cls, title: str, lines: List[str]) -> str:
        """Format a section with title and content"""
        section = [
            f"── {title} {'─' * (60 - len(title) - 4)}",
            *lines
        ]
        return '\n'.join(section)