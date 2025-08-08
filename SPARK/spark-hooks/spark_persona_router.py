#!/usr/bin/env python3
"""
SPARK Persona Router Hook (UserPromptSubmit)
Intelligently activates personas and MCP servers based on task analysis
"""

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s", 
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


def extract_keywords(text: str) -> list:
    """Extract relevant keywords for persona activation"""
    text_lower = text.lower()
    
    keywords = []
    
    # Backend indicators
    backend_patterns = [
        r'\b(api|endpoint|service|server|database|backend)\b',
        r'\b(rest|graphql|microservice|authentication)\b',
        r'\b(reliability|uptime|performance|scalability)\b'
    ]
    
    # Security indicators  
    security_patterns = [
        r'\b(auth|security|vulnerability|encrypt|compliance)\b',
        r'\b(oauth|jwt|ssl|tls|cors|csrf)\b',
        r'\b(threat|attack|secure|protection)\b'
    ]
    
    # Frontend indicators
    frontend_patterns = [
        r'\b(component|ui|frontend|responsive|accessibility)\b',
        r'\b(react|vue|angular|html|css|javascript)\b',
        r'\b(user experience|ux|interface|dashboard)\b'
    ]
    
    # Architecture indicators
    architecture_patterns = [
        r'\b(architecture|design|system|structure)\b',
        r'\b(pattern|framework|infrastructure|deployment)\b',
        r'\b(scalable|maintainable|modular)\b'
    ]
    
    # Check patterns and add keywords
    for pattern in backend_patterns:
        if re.search(pattern, text_lower):
            keywords.append("backend")
            break
            
    for pattern in security_patterns:
        if re.search(pattern, text_lower):
            keywords.append("security")
            break
            
    for pattern in frontend_patterns:
        if re.search(pattern, text_lower):
            keywords.append("frontend")
            break
            
    for pattern in architecture_patterns:
        if re.search(pattern, text_lower):
            keywords.append("architecture")
            break
    
    return list(set(keywords))


def calculate_complexity(text: str, context: dict = None) -> float:
    """Calculate task complexity score (0.0-1.0)"""
    complexity_indicators = [
        # High complexity indicators (0.3-0.4 each)
        (r'\b(architecture|system|scalable|enterprise|complex)\b', 0.4),
        (r'\b(microservice|distributed|real-time|performance)\b', 0.3),
        (r'\b(security|authentication|authorization|compliance)\b', 0.3),
        
        # Medium complexity indicators (0.2 each)
        (r'\b(api|database|integration|workflow)\b', 0.2),
        (r'\b(responsive|accessibility|optimization)\b', 0.2),
        (r'\b(testing|validation|monitoring)\b', 0.2),
        
        # Low complexity indicators (0.1 each)
        (r'\b(component|function|method|form)\b', 0.1),
        (r'\b(style|format|display|show)\b', 0.1),
    ]
    
    complexity_score = 0.0
    text_lower = text.lower()
    
    for pattern, score in complexity_indicators:
        if re.search(pattern, text_lower):
            complexity_score += score
    
    # Cap at 1.0
    return min(complexity_score, 1.0)


def select_personas_and_mcp(keywords: list, complexity: float) -> dict:
    """Select appropriate personas and MCP servers"""
    
    active_personas = []
    mcp_servers = []
    
    # Persona activation based on keywords
    if "backend" in keywords:
        active_personas.append("backend")
        mcp_servers.extend(["context7", "sequential"])
        
    if "security" in keywords:
        active_personas.append("security") 
        mcp_servers.append("sequential")  # For threat modeling
        
    if "frontend" in keywords:
        active_personas.append("frontend")
        mcp_servers.append("magic")  # For UI generation
        
    if "architecture" in keywords or complexity > 0.7:
        active_personas.append("architect")
        mcp_servers.append("sequential")  # For systematic analysis
        
    # Complexity-based MCP activation
    if complexity > 0.7:
        if "sequential" not in mcp_servers:
            mcp_servers.append("sequential")
            
    # Always include Context7 for pattern lookup if not already included
    if mcp_servers and "context7" not in mcp_servers:
        mcp_servers.append("context7")
    
    # Default fallback
    if not active_personas:
        active_personas = ["backend"]  # Default to backend
        mcp_servers = ["context7"]
    
    return {
        "active_personas": list(set(active_personas)),
        "mcp_servers": list(set(mcp_servers)),
        "complexity_score": complexity,
        "quality_gates_required": 8 if complexity > 0.5 else 6
    }


def update_task_context(activation_result: dict, prompt: str) -> None:
    """Update current_task.json with SPARK activation info"""
    
    task_file = Path(".claude/workflows/current_task.json")
    
    if task_file.exists():
        try:
            with open(task_file, 'r') as f:
                task_data = json.load(f)
        except:
            task_data = {}
    else:
        task_data = {}
    
    # Add SPARK activation metadata
    task_data.update({
        "sparkclaude_activation": {
            **activation_result,
            "activation_timestamp": datetime.now().isoformat(),
            "original_prompt": prompt,
            "routing_strategy": "intelligent_persona_selection"
        },
        "enhanced_workflow": True,
        "token_efficiency_target": "82%",
    })
    
    # Ensure task_file directory exists
    task_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(task_file, 'w') as f:
            json.dump(task_data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to update task context: {e}")


def main():
    """Main hook execution"""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        prompt = input_data.get("prompt", "")
        
        # Skip if not an implementation-related prompt
        if not any(keyword in prompt.lower() for keyword in [
            "implement", "create", "build", "develop", "design", 
            "/implement", "task-", "component", "api", "service"
        ]):
            sys.exit(0)
        
        # Analyze prompt for SPARK activation
        keywords = extract_keywords(prompt)
        complexity = calculate_complexity(prompt)
        
        if not keywords and complexity < 0.3:
            # Simple task, no need for SPARK enhancement
            sys.exit(0)
            
        # Select personas and MCP servers
        activation_result = select_personas_and_mcp(keywords, complexity)
        
        # Update task context
        update_task_context(activation_result, prompt)
        
        # Log activation details
        logger.info("🧠 SPARK Intelligence Activated!")
        logger.info(f"🎭 Personas: {', '.join(activation_result['active_personas'])}")
        logger.info(f"🔧 MCP Servers: {', '.join(activation_result['mcp_servers'])}")
        logger.info(f"📊 Complexity: {activation_result['complexity_score']:.2f}")
        logger.info(f"🛡️ Quality Gates: {activation_result['quality_gates_required']}")
        
        # Generate context for Claude
        context = f"""🧠 SPARK Intelligence System Activated!

**Intelligent Analysis Results:**
- 🎭 **Active Personas**: {', '.join(activation_result['active_personas'])}
- 🔧 **MCP Servers**: {', '.join(activation_result['mcp_servers'])} 
- 📊 **Complexity Score**: {activation_result['complexity_score']:.2f}/1.0
- 🛡️ **Quality Gates**: {activation_result['quality_gates_required']}/10

**Efficiency Achievement**: 82% token reduction vs SuperClaude original (8K vs 44K tokens)

**Important**: Use the **implementer-spark** agent which has been pre-configured with this intelligence for optimal performance."""
        
        # Output context for Claude to see
        print(context)
        
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON input: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Hook execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()