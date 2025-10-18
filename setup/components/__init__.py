"""
Component Directory

Each module defines an installable responsibility unit:
- knowledge_base: Framework knowledge initialization
- behavior_modes: Execution mode definitions
- agent_personas: AI agent personality definitions
- slash_commands: CLI command registration
- mcp_integration: External tool integration via MCP
"""

from .knowledge_base import KnowledgeBaseComponent
from .behavior_modes import BehaviorModesComponent
from .agent_personas import AgentPersonasComponent
from .slash_commands import SlashCommandsComponent
from .mcp_integration import MCPIntegrationComponent

__all__ = [
    "KnowledgeBaseComponent",
    "BehaviorModesComponent",
    "AgentPersonasComponent",
    "SlashCommandsComponent",
    "MCPIntegrationComponent",
]
