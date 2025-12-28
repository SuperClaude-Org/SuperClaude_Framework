---
name: spawn
description: "Meta-system task orchestration with intelligent breakdown and delegation"
category: special
complexity: high
mcp-servers: []
personas: []
---

# /sc:spawn - Meta-System Task Orchestration

## Triggers
- Complex multi-domain operations requiring intelligent task breakdown
- Large-scale system operations spanning multiple technical areas
- Operations requiring parallel coordination and dependency management
- Meta-level orchestration beyond standard command capabilities

## Usage
```
/sc:spawn [complex-task] [--strategy sequential|parallel|adaptive] [--depth normal|deep]
```

## Behavioral Flow
1. **Analyze**: Parse complex operation requirements and assess scope across domains
2. **Decompose**: Break down operation into coordinated subtask hierarchies
3. **Orchestrate**: Execute tasks using optimal coordination strategy (parallel/sequential)
4. **Monitor**: Track progress across task hierarchies with dependency management
5. **Integrate**: Aggregate results and provide comprehensive orchestration summary

Key behaviors:
- Meta-system task decomposition with Epic → Story → Task → Subtask breakdown
- Intelligent coordination strategy selection based on operation characteristics
- Cross-domain operation management with parallel and sequential execution patterns
- Advanced dependency analysis and resource optimization across task hierarchies
## MCP Integration
- **Native Orchestration**: Meta-system command uses native coordination without MCP dependencies
- **Progressive Integration**: Coordination with systematic execution for progressive enhancement
- **Framework Integration**: Advanced integration with SuperClaude orchestration layers

## Tool Coordination
- **TodoWrite**: Hierarchical task breakdown and progress tracking across Epic → Story → Task levels
- **Read/Grep/Glob**: System analysis and dependency mapping for complex operations
- **Edit/MultiEdit/Write**: Coordinated file operations with parallel and sequential execution
- **Bash**: System-level operations coordination with intelligent resource management

## Key Patterns
- **Hierarchical Breakdown**: Epic-level operations → Story coordination → Task execution → Subtask granularity
- **Strategy Selection**: Sequential (dependency-ordered) → Parallel (independent) → Adaptive (dynamic)
- **Meta-System Coordination**: Cross-domain operations → resource optimization → result integration
- **Progressive Enhancement**: Systematic execution → quality gates → comprehensive validation

## Examples

### Complex Feature Implementation
```
/sc:spawn "implement user authentication system"
# Breakdown: Database design → Backend API → Frontend UI → Testing
# Coordinates across multiple domains with dependency management
```

### Large-Scale System Operation
```
/sc:spawn "migrate legacy monolith to microservices" --strategy adaptive --depth deep
# Enterprise-scale operation with sophisticated orchestration
# Adaptive coordination based on operation characteristics
```

### Cross-Domain Infrastructure
```
/sc:spawn "establish CI/CD pipeline with security scanning"
# System-wide infrastructure operation spanning DevOps, Security, Quality domains
# Parallel execution of independent components with validation gates
```

## Boundaries

**Will:**
- Decompose complex multi-domain operations into coordinated task hierarchies
- Provide intelligent orchestration with parallel and sequential coordination strategies
- Execute meta-system operations beyond standard command capabilities

**Will Not:**
- Replace domain-specific commands for simple operations
- Override user coordination preferences or execution strategies
- Execute operations without proper dependency analysis and validation