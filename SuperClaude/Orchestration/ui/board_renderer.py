"""
Board Renderer - ASCII visualization with resource indicators

Provides clear visual representation of board state, card positions,
and resource usage for user transparency and control.
"""

from typing import List, Dict, Optional
from datetime import datetime
from ..board.card_model import TaskCard, CardStatus
from ..board.board_manager import BoardManager
from ..board.resource_tracker import ResourceTracker


class BoardRenderer:
    """ASCII board visualization with resource tracking"""
    
    # Board layout constants
    COLUMN_WIDTH = 25
    CARD_HEIGHT = 8
    MAX_CARDS_DISPLAY = 5
    
    # Visual elements
    BOARD_CHARS = {
        'top_left': '┌',
        'top_right': '┐',
        'bottom_left': '└',
        'bottom_right': '┘',
        'horizontal': '─',
        'vertical': '│',
        'cross': '┼',
        'top_join': '┬',
        'bottom_join': '┴',
        'left_join': '├',
        'right_join': '┤'
    }
    
    # Status indicators
    STATUS_ICONS = {
        CardStatus.BACKLOG: '📋',
        CardStatus.TODO: '📝',
        CardStatus.IN_PROGRESS: '🔄',
        CardStatus.INTEGRATE: '🔗',
        CardStatus.REVIEW: '👁️',
        CardStatus.DONE: '✅',
        CardStatus.FAILED: '❌',
        CardStatus.BLOCKED: '🚧'
    }
    
    def __init__(self, board_manager: BoardManager, resource_tracker: ResourceTracker):
        self.board = board_manager
        self.resources = resource_tracker
        
    def render_board(self, show_resources: bool = True) -> str:
        """Render complete board view with optional resource panel"""
        output = []
        
        # Header with timestamp
        output.append(self._render_header())
        
        # Resource panel
        if show_resources:
            output.append(self._render_resource_panel())
            
        # Board columns
        output.append(self._render_columns())
        
        # Cards in each column
        output.append(self._render_cards())
        
        # Footer with controls
        output.append(self._render_footer())
        
        return '\n'.join(output)
    
    def _render_header(self) -> str:
        """Render board header with title and timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = "🎯 SuperClaude Board System"
        
        header_lines = [
            "═" * 120,
            f"{title.center(120)}",
            f"Last Updated: {timestamp}".center(120),
            "═" * 120
        ]
        
        return '\n'.join(header_lines)
    
    def _render_resource_panel(self) -> str:
        """Render resource usage indicators"""
        metrics = self.resources.get_metrics()
        
        # Token usage bar
        token_percent = (metrics['token_usage'] / metrics['token_limit']) * 100
        token_bar = self._create_progress_bar(token_percent, 30)
        
        # Active cards indicator
        card_usage = f"{metrics['active_cards']}/{metrics['max_active_cards']}"
        
        # MCP calls rate
        mcp_rate = f"{metrics['mcp_calls_per_minute']}/{metrics['mcp_rate_limit']}"
        
        panel_lines = [
            "┌─── Resource Usage ─────────────────────────────────────────┐",
            f"│ 📊 Tokens:  {token_bar} {token_percent:.1f}% ({metrics['token_usage']:,}/{metrics['token_limit']:,})",
            f"│ 🎯 Active:  {card_usage} cards (Max: {metrics['max_active_cards']})",
            f"│ ⚡ MCP Rate: {mcp_rate} calls/min",
            f"│ 🔄 Queue:   {metrics['queued_cards']} cards waiting",
            "└────────────────────────────────────────────────────────────┘"
        ]
        
        # Add warnings if approaching limits
        warnings = []
        if token_percent > 80:
            warnings.append("⚠️  Token usage high - consider pausing cards")
        if metrics['active_cards'] >= metrics['max_active_cards']:
            warnings.append("🚨 Max active cards reached - new cards queued")
            
        if warnings:
            panel_lines.extend([
                "",
                "⚠️  Warnings:",
                *[f"   {w}" for w in warnings]
            ])
            
        return '\n'.join(panel_lines)
    
    def _render_columns(self) -> str:
        """Render column headers"""
        columns = self.board.columns
        
        # Column separator line
        separator = '┬'.join(['─' * self.COLUMN_WIDTH for _ in columns])
        separator = f"┌{separator}┐"
        
        # Column names with icons
        header_row = []
        for col in columns:
            icon = self.STATUS_ICONS.get(col, '📋')
            name = f"{icon} {col.value.upper()}"
            header_row.append(name.center(self.COLUMN_WIDTH))
            
        headers = '│'.join(header_row)
        headers = f"│{headers}│"
        
        # Card counts
        count_row = []
        for col in columns:
            count = len(self.board.get_cards_by_status(col))
            count_str = f"({count} cards)"
            count_row.append(count_str.center(self.COLUMN_WIDTH))
            
        counts = '│'.join(count_row)
        counts = f"│{counts}│"
        
        return '\n'.join([separator, headers, counts, separator.replace('┌', '├').replace('┐', '┤')])
    
    def _render_cards(self) -> str:
        """Render cards in each column"""
        output_lines = []
        columns = self.board.columns
        
        # Get cards for each column
        column_cards = {}
        max_cards = 0
        
        for col in columns:
            cards = self.board.get_cards_by_status(col)
            column_cards[col] = cards[:self.MAX_CARDS_DISPLAY]  # Limit display
            max_cards = max(max_cards, len(column_cards[col]))
            
        # Render row by row
        for row_idx in range(max_cards):
            card_row = []
            
            for col in columns:
                if row_idx < len(column_cards[col]):
                    card = column_cards[col][row_idx]
                    card_display = self._render_card_compact(card)
                    card_row.append(card_display)
                else:
                    card_row.append(' ' * (self.COLUMN_WIDTH - 2))
                    
            row_line = ' │ '.join(card_row)
            output_lines.append(f"│ {row_line} │")
            
        # Show overflow indicator if needed
        overflow_row = []
        for col in columns:
            total = len(self.board.get_cards_by_status(col))
            if total > self.MAX_CARDS_DISPLAY:
                overflow = f"... +{total - self.MAX_CARDS_DISPLAY} more"
                overflow_row.append(overflow.center(self.COLUMN_WIDTH - 2))
            else:
                overflow_row.append(' ' * (self.COLUMN_WIDTH - 2))
                
        if any(o.strip() for o in overflow_row):
            overflow_line = ' │ '.join(overflow_row)
            output_lines.append(f"│ {overflow_line} │")
            
        # Bottom border
        bottom = '┴'.join(['─' * self.COLUMN_WIDTH for _ in columns])
        bottom = f"└{bottom}┘"
        output_lines.append(bottom)
        
        return '\n'.join(output_lines)
    
    def _render_card_compact(self, card: TaskCard) -> str:
        """Render a single card in compact format"""
        # Priority indicator
        priority_icon = {
            'critical': '🔴',
            'high': '🟡',
            'medium': '🟢',
            'low': '⚪'
        }.get(card.priority, '⚪')
        
        # Card ID and title (truncated)
        title = card.title[:20] + '...' if len(card.title) > 20 else card.title
        header = f"{priority_icon} {card.id[:8]}"
        
        # Assigned agent
        agent = card.assigned_agent or "Unassigned"
        agent_str = f"👤 {agent[:15]}"
        
        # Progress or status
        if card.error_count > 0:
            status = f"⚠️  {card.error_count} errors"
        elif card.token_usage:
            percent = (card.token_usage / 5000) * 100  # Assume 5K per card budget
            status = f"📊 {percent:.0f}% tokens"
        else:
            status = "⏳ Waiting"
            
        # Format as compact card
        lines = [
            header.ljust(self.COLUMN_WIDTH - 2),
            title.ljust(self.COLUMN_WIDTH - 2),
            agent_str.ljust(self.COLUMN_WIDTH - 2),
            status.ljust(self.COLUMN_WIDTH - 2)
        ]
        
        return '\n'.join(lines)
    
    def _render_footer(self) -> str:
        """Render footer with available commands"""
        commands = [
            "/sc:board show - Display this board",
            "/sc:board status <card_id> - Card details",
            "/sc:board pause <card_id> - Pause card",
            "/sc:board move <card_id> <column> - Move card",
            "/sc:board help - All commands"
        ]
        
        footer_lines = [
            "",
            "─" * 120,
            "Available Commands:",
            *[f"  {cmd}" for cmd in commands],
            "─" * 120
        ]
        
        return '\n'.join(footer_lines)
    
    def _create_progress_bar(self, percent: float, width: int) -> str:
        """Create a visual progress bar"""
        filled = int((percent / 100) * width)
        empty = width - filled
        
        if percent >= 90:
            fill_char = '🟥'
            empty_char = '⬜'
        elif percent >= 70:
            fill_char = '🟨'
            empty_char = '⬜'
        else:
            fill_char = '🟩'
            empty_char = '⬜'
            
        bar = fill_char * filled + empty_char * empty
        return f"[{bar}]"
    
    def render_card_detail(self, card_id: str) -> Optional[str]:
        """Render detailed view of a single card"""
        card = self.board.get_card(card_id)
        if not card:
            return None
            
        status_icon = self.STATUS_ICONS.get(card.status, '❓')
        
        detail_lines = [
            "┌─── Card Details ───────────────────────────────────────────┐",
            f"│ ID:       {card.id}",
            f"│ Title:    {card.title}",
            f"│ Status:   {status_icon} {card.status.value}",
            f"│ Priority: {card.priority}",
            f"│ Agent:    {card.assigned_agent or 'Unassigned'}",
            f"│ Created:  {card.created_at}",
            f"│ Updated:  {card.updated_at}",
            "├────────────────────────────────────────────────────────────┤",
            f"│ Context:  {card.context[:50]}..." if card.context else "│ Context:  None",
            f"│ Tools:    {', '.join(card.allowed_tools[:3])}..." if card.allowed_tools else "│ Tools:    All",
            f"│ Tokens:   {card.token_usage or 0:,} used",
            f"│ Errors:   {card.error_count}",
            "└────────────────────────────────────────────────────────────┘"
        ]
        
        if card.dependencies:
            detail_lines.insert(-1, f"│ Depends:  {', '.join(card.dependencies)}")
            
        if card.error_log:
            detail_lines.extend([
                "",
                "Recent Errors:",
                *[f"  - {err}" for err in card.error_log[-3:]]
            ])
            
        return '\n'.join(detail_lines)
    
    def render_mini_board(self) -> str:
        """Render a compact board summary for quick status checks"""
        columns = self.board.columns
        summary = []
        
        for col in columns:
            cards = self.board.get_cards_by_status(col)
            icon = self.STATUS_ICONS.get(col, '📋')
            summary.append(f"{icon} {col.value}: {len(cards)}")
            
        metrics = self.resources.get_metrics()
        token_percent = (metrics['token_usage'] / metrics['token_limit']) * 100
        
        mini = [
            f"Board: {' | '.join(summary)}",
            f"Resources: {token_percent:.0f}% tokens, {metrics['active_cards']}/{metrics['max_active_cards']} active"
        ]
        
        return ' | '.join(mini)