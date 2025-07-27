"""
Persona Parser for P2SA Framework
Extracts persona definitions from PERSONAS.md and converts to sub-agent configurations
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path

@dataclass
class PersonaDefinition:
    """Data model for a parsed persona"""
    name: str
    identity: str
    domain: str
    priority_hierarchy: List[str]
    core_principles: List[str]
    mcp_preferences: Dict[str, List[str]]
    quality_standards: Dict[str, str]
    auto_triggers: List[str]
    optimized_commands: List[str]
    
class PersonaParser:
    """Parse PERSONAS.md and extract persona definitions"""
    
    def __init__(self, personas_path: Path):
        self.personas_path = personas_path
        self.personas = {}
        
    def parse_all_personas(self) -> Dict[str, PersonaDefinition]:
        """Parse all personas from PERSONAS.md"""
        content = self.personas_path.read_text()
        
        # Extract each persona section
        persona_sections = self._extract_persona_sections(content)
        
        for section in persona_sections:
            persona = self._parse_persona_section(section)
            if persona:
                self.personas[persona.name] = persona
                
        return self.personas
    
    def _extract_persona_sections(self, content: str) -> List[str]:
        """Extract individual persona sections from markdown"""
        # Match ## `--persona-name` sections
        pattern = r'## `--persona-(\w+)`.*?(?=## `--persona-|\Z)'
        sections = re.findall(pattern, content, re.DOTALL)
        return sections
    
    def _parse_persona_section(self, section: str) -> Optional[PersonaDefinition]:
        """Parse a single persona section"""
        # Extract persona name
        name_match = re.search(r'--persona-(\w+)', section)
        if not name_match:
            return None
            
        name = name_match.group(1)
        
        # Extract identity
        identity_match = re.search(r'\*\*Identity\*\*: (.+)', section)
        identity = identity_match.group(1) if identity_match else ""
        
        # Extract priority hierarchy  
        priority_match = re.search(r'\*\*Priority Hierarchy\*\*: (.+)', section)
        priorities = []
        if priority_match:
            priorities = [p.strip() for p in priority_match.group(1).split('>')]
        
        # Extract core principles
        principles = self._extract_list_after_header(section, "Core Principles")
        
        # Extract MCP preferences
        mcp_prefs = self._extract_mcp_preferences(section)
        
        # Extract quality standards
        quality_stds = self._extract_quality_standards(section)
        
        # Extract auto-activation triggers
        triggers = self._extract_list_after_header(section, "Auto-Activation Triggers")
        
        # Extract optimized commands
        commands = self._extract_optimized_commands(section)
        
        # Determine domain from identity
        domain = self._determine_domain(identity, name)
        
        return PersonaDefinition(
            name=name,
            identity=identity,
            domain=domain,
            priority_hierarchy=priorities,
            core_principles=principles,
            mcp_preferences=mcp_prefs,
            quality_standards=quality_stds,
            auto_triggers=triggers,
            optimized_commands=commands
        )
    
    def _extract_list_after_header(self, text: str, header: str) -> List[str]:
        """Extract bullet points after a specific header"""
        pattern = rf'\*\*{header}\*\*:?\s*\n((?:[-\d]+\..*\n)+)'
        match = re.search(pattern, text)
        if match:
            items = re.findall(r'[-\d]+\. (.+)', match.group(1))
            return items
        return []
    
    def _extract_mcp_preferences(self, section: str) -> Dict[str, List[str]]:
        """Extract MCP server preferences"""
        prefs = {}
        
        # Look for Primary, Secondary, Avoided patterns
        for level in ['Primary', 'Secondary', 'Avoided']:
            pattern = rf'\*\*{level}\*\*: (.+)'
            match = re.search(pattern, section)
            if match:
                # Parse server names and reasons
                servers = []
                content = match.group(1)
                # Simple extraction - can be enhanced
                if '-' in content:
                    parts = content.split('-')
                    servers.append(parts[0].strip())
                else:
                    servers.append(content.strip())
                prefs[level.lower()] = servers
                
        return prefs
    
    def _extract_quality_standards(self, section: str) -> Dict[str, str]:
        """Extract quality standards section"""
        standards = {}
        
        # Look for quality standards section
        qs_match = re.search(r'\*\*Quality Standards\*\*:?\s*\n((?:- \*\*.+\*\*:.+\n)+)', section)
        if qs_match:
            # Parse each standard
            for line in qs_match.group(1).split('\n'):
                if line.strip():
                    std_match = re.match(r'- \*\*(.+?)\*\*: (.+)', line)
                    if std_match:
                        standards[std_match.group(1)] = std_match.group(2)
                        
        return standards
    
    def _extract_optimized_commands(self, section: str) -> List[str]:
        """Extract optimized commands for persona"""
        commands = []
        
        # Look for commands section
        cmd_section = re.search(r'\*\*Optimized Commands\*\*:?\s*\n((?:- .+\n)+)', section)
        if cmd_section:
            # Extract command names
            for line in cmd_section.group(1).split('\n'):
                if line.strip():
                    # Extract command from format: - `/command` - description
                    cmd_match = re.match(r'- `(/.+?)`', line)
                    if cmd_match:
                        commands.append(cmd_match.group(1))
                        
        return commands
    
    def _determine_domain(self, identity: str, name: str) -> str:
        """Determine domain from identity and name"""
        domain_mapping = {
            'architect': 'systems architecture',
            'frontend': 'user interface development',
            'backend': 'server-side development',
            'security': 'security and compliance',
            'performance': 'optimization and efficiency',
            'analyzer': 'analysis and investigation',
            'qa': 'quality assurance',
            'refactorer': 'code quality',
            'devops': 'infrastructure and deployment',
            'mentor': 'education and guidance',
            'scribe': 'documentation and communication'
        }
        
        return domain_mapping.get(name, 'general development')