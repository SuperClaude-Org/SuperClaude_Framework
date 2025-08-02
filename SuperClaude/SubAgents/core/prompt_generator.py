"""
System Prompt Generator for P2SA Framework
Converts PersonaDefinition objects into Claude Code sub-agent system prompts
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json

from .persona_parser import PersonaDefinition

class PromptGenerator:
    """Generate system prompts for sub-agents from persona definitions"""
    
    def __init__(self):
        self.prompt_template = """You are {name}-agent, a specialized sub-agent for {domain}.

IDENTITY: {identity}

CORE MISSION:
{core_mission}

DECISION FRAMEWORK:
Priority order: {priorities}
Always evaluate decisions against these priorities.

SPECIALIZED CAPABILITIES:
{capabilities}

QUALITY STANDARDS:
{quality_standards}

TOOLS:
{tool_preferences}

OUTPUT STYLE:
- Be {communication_style}
- Focus on {focus_areas}
- Always provide {deliverables}

COLLABORATION:
When working with other agents, provide structured handoffs using:
```json
{{
  "analysis": "your findings",
  "recommendations": ["specific", "actionable", "items"],
  "concerns": ["potential issues"],
  "next_steps": ["for other agents"]
}}
```

PROACTIVE ASSISTANCE:
{proactive_guidance}"""

    def generate_prompt(self, persona: PersonaDefinition) -> str:
        """Generate a complete system prompt for a persona"""
        
        # Format core mission from principles
        core_mission = self._format_core_mission(persona.core_principles)
        
        # Format priorities
        priorities = " > ".join(persona.priority_hierarchy)
        
        # Generate capabilities based on domain
        capabilities = self._generate_capabilities(persona)
        
        # Format quality standards
        quality_standards = self._format_quality_standards(persona.quality_standards)
        
        # Format tool preferences
        tool_prefs = self._format_tool_preferences(persona.mcp_preferences)
        
        # Determine communication style
        comm_style = self._determine_communication_style(persona.name)
        
        # Determine focus areas
        focus_areas = self._determine_focus_areas(persona)
        
        # Determine deliverables
        deliverables = self._determine_deliverables(persona.name)
        
        # Generate proactive guidance
        proactive = self._generate_proactive_guidance(persona)
        
        # Fill template
        prompt = self.prompt_template.format(
            name=persona.name,
            domain=persona.domain,
            identity=persona.identity,
            core_mission=core_mission,
            priorities=priorities,
            capabilities=capabilities,
            quality_standards=quality_standards,
            tool_preferences=tool_prefs,
            communication_style=comm_style,
            focus_areas=focus_areas,
            deliverables=deliverables,
            proactive_guidance=proactive
        )
        
        return prompt
    
    def _format_core_mission(self, principles: List[str]) -> str:
        """Format core principles as mission directives"""
        if not principles:
            return "- Provide expert assistance in your domain"
        
        formatted = []
        for principle in principles[:5]:  # Limit to top 5
            # Convert principle to directive
            directive = f"- {principle}"
            formatted.append(directive)
            
        return "\n".join(formatted)
    
    def _generate_capabilities(self, persona: PersonaDefinition) -> str:
        """Generate specialized capabilities based on persona"""
        
        capability_templates = {
            "architect": [
                "- System design using DDD, microservices, and cloud patterns",
                "- Scalability analysis and capacity planning",
                "- Technology selection and architectural decision records",
                "- Cross-cutting concerns (security, monitoring, resilience)"
            ],
            "security": [
                "- Threat modeling using STRIDE methodology",
                "- Vulnerability assessment and penetration testing strategies",
                "- Security pattern implementation (OAuth, JWT, encryption)",
                "- Compliance mapping (OWASP, GDPR, SOC2, PCI-DSS)"
            ],
            "frontend": [
                "- Modern framework expertise (React, Vue, Angular)",
                "- Responsive design and mobile-first development",
                "- Performance optimization (bundle size, lazy loading)",
                "- Accessibility implementation (WCAG 2.1 AA)"
            ],
            "backend": [
                "- RESTful and GraphQL API design",
                "- Database optimization and query performance",
                "- Distributed systems and microservices",
                "- Message queuing and event-driven architecture"
            ],
            "performance": [
                "- Performance profiling and bottleneck analysis",
                "- Caching strategies (CDN, Redis, application-level)",
                "- Database query optimization",
                "- Frontend performance (Core Web Vitals)"
            ],
            "analyzer": [
                "- Root cause analysis methodologies",
                "- Data-driven investigation techniques",
                "- Pattern recognition in complex systems",
                "- Hypothesis testing and validation"
            ]
        }
        
        capabilities = capability_templates.get(persona.name, [
            "- Domain expertise in " + persona.domain,
            "- Best practices and pattern implementation",
            "- Quality-focused development",
            "- Collaborative problem solving"
        ])
        
        return "\n".join(capabilities)
    
    def _format_quality_standards(self, standards: Dict[str, str]) -> str:
        """Format quality standards dictionary"""
        if not standards:
            return "- Maintain high quality standards in all work"
        
        formatted = []
        for key, value in standards.items():
            formatted.append(f"- {key}: {value}")
            
        return "\n".join(formatted)
    
    def _format_tool_preferences(self, prefs: Dict[str, List[str]]) -> str:
        """Format MCP tool preferences"""
        formatted = []
        
        if 'primary' in prefs:
            formatted.append(f"Primary: {', '.join(prefs['primary'])} - Use these for core tasks")
            
        if 'secondary' in prefs:
            formatted.append(f"Secondary: {', '.join(prefs['secondary'])} - Use when primary tools insufficient")
            
        if 'avoided' in prefs:
            formatted.append(f"Restricted: {', '.join(prefs['avoided'])} - Avoid these tools")
            
        if not formatted:
            formatted.append("Use all available tools as appropriate for the task")
            
        return "\n".join(formatted)
    
    def _determine_communication_style(self, persona_name: str) -> str:
        """Determine communication style based on persona"""
        styles = {
            "architect": "systematic and strategic",
            "security": "precise and risk-aware",
            "frontend": "user-focused and visual",
            "backend": "technical and reliability-focused",
            "performance": "metrics-driven and analytical",
            "analyzer": "evidence-based and thorough",
            "qa": "detail-oriented and quality-focused",
            "refactorer": "clean and improvement-oriented",
            "devops": "automation-focused and efficient",
            "mentor": "educational and supportive",
            "scribe": "clear and well-structured"
        }
        
        return styles.get(persona_name, "professional and helpful")
    
    def _determine_focus_areas(self, persona: PersonaDefinition) -> str:
        """Determine key focus areas for persona"""
        focus_map = {
            "architect": "long-term maintainability, scalability, and system coherence",
            "security": "threat mitigation, compliance, and security best practices",
            "frontend": "user experience, accessibility, and performance",
            "backend": "reliability, data integrity, and API design",
            "performance": "bottleneck identification and optimization strategies",
            "analyzer": "root causes and evidence-based solutions"
        }
        
        return focus_map.get(persona.name, "domain expertise and best practices")
    
    def _determine_deliverables(self, persona_name: str) -> str:
        """Determine expected deliverables for persona"""
        deliverables = {
            "architect": "architectural diagrams, decision records, and design documents",
            "security": "threat assessments, vulnerability reports, and remediation plans",
            "frontend": "responsive components, accessibility audits, and performance metrics",
            "backend": "API specifications, database schemas, and reliability reports",
            "performance": "performance profiles, optimization recommendations, and benchmarks",
            "analyzer": "investigation reports, root cause analyses, and solution proposals"
        }
        
        return deliverables.get(persona_name, "high-quality solutions and recommendations")
    
    def _generate_proactive_guidance(self, persona: PersonaDefinition) -> str:
        """Generate proactive assistance guidance"""
        
        # Use auto-triggers to create proactive behavior
        if persona.auto_triggers:
            triggers = ", ".join([f'"{t}"' for t in persona.auto_triggers[:3]])
            return f"When you detect keywords like {triggers}, proactively offer your specialized assistance."
        
        return "Monitor for opportunities to apply your expertise and proactively suggest improvements."

@dataclass 
class SubAgentConfig:
    """Configuration for creating a sub-agent"""
    name: str
    description: str
    system_prompt: str
    tools: Optional[List[str]] = None
    
class SubAgentGenerator:
    """Generate sub-agent configurations from personas"""
    
    def __init__(self):
        self.prompt_generator = PromptGenerator()
        
    def generate_agent_config(self, persona: PersonaDefinition) -> SubAgentConfig:
        """Generate complete sub-agent configuration"""
        
        # Generate system prompt
        system_prompt = self.prompt_generator.generate_prompt(persona)
        
        # Create description
        description = f"{persona.identity}. Specialized in {persona.domain}."
        
        # Determine tools based on MCP preferences
        tools = self._determine_tools(persona.mcp_preferences)
        
        return SubAgentConfig(
            name=f"{persona.name}-agent",
            description=description,
            system_prompt=system_prompt,
            tools=tools
        )
    
    def _determine_tools(self, mcp_prefs: Dict[str, List[str]]) -> Optional[List[str]]:
        """Determine tool restrictions based on preferences"""
        
        # If there are avoided tools, restrict access
        if 'avoided' in mcp_prefs and mcp_prefs['avoided']:
            # Return all tools except avoided ones
            all_tools = ['Read', 'Write', 'Edit', 'MultiEdit', 'Grep', 'Glob', 
                        'Bash', 'Task', 'WebSearch', 'WebFetch']
            
            # Add MCP tools
            mcp_tools = ['mcp__context7__*', 'mcp__sequential__*', 
                        'mcp__magicuidesign__*', 'mcp__playwright__*']
            
            # Filter out avoided
            avoided = mcp_prefs['avoided']
            allowed_tools = []
            
            for tool in all_tools:
                # Check if tool should be avoided
                avoid = False
                for avoided_pattern in avoided:
                    if avoided_pattern.lower() in tool.lower():
                        avoid = True
                        break
                if not avoid:
                    allowed_tools.append(tool)
                    
            return allowed_tools if allowed_tools else None
            
        # No restrictions
        return None