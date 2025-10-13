---
name: workflow
description: "Generate structured implementation workflows from PRDs and feature requirements"
category: orchestration
complexity: advanced
mcp-servers: [sequential, context7, magic, playwright, morphllm, serena]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
---

# /sc:workflow - Implementation Workflow Generator

## Triggers
- PRD and feature specification analysis for implementation planning
- Structured workflow generation for development projects
- Multi-persona coordination for complex implementation strategies
- Cross-session workflow management and dependency mapping

## Usage
```
/sc:workflow [prd-file|feature-description] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```

## Behavioral Flow
1. **Analyze**: Parse PRD and feature specifications to understand implementation requirements
2. **Plan**: Generate comprehensive workflow structure with dependency mapping and task orchestration
3. **Coordinate**: Activate multiple personas for domain expertise and implementation strategy
4. **Execute**: Create structured step-by-step workflows with automated task coordination
5. **Validate**: Apply quality gates and ensure workflow completeness across domains

Key behaviors:
- Multi-persona orchestration across architecture, frontend, backend, security, and devops domains
- Advanced MCP coordination with intelligent routing for specialized workflow analysis
- Systematic execution with progressive workflow enhancement and parallel processing
- Cross-session workflow management with comprehensive dependency tracking

## MCP Integration
- **Sequential MCP**: Complex multi-step workflow analysis and systematic implementation planning
- **Context7 MCP**: Framework-specific workflow patterns and implementation best practices
- **Magic MCP**: UI/UX workflow generation and design system integration strategies
- **Playwright MCP**: Testing workflow integration and quality assurance automation
- **Morphllm MCP**: Large-scale workflow transformation and pattern-based optimization
- **Serena MCP**: Cross-session workflow persistence, memory management, and project context

## Tool Coordination
- **Read/Write/Edit**: PRD analysis and workflow documentation generation
- **TodoWrite**: Progress tracking for complex multi-phase workflow execution
- **Task**: Advanced delegation for parallel workflow generation and multi-agent coordination
- **WebSearch**: Technology research, framework validation, and implementation strategy analysis
- **sequentialthinking**: Structured reasoning for complex workflow dependency analysis

## Key Patterns
- **PRD Analysis**: Document parsing → requirement extraction → implementation strategy development
- **Workflow Generation**: Task decomposition → dependency mapping → structured implementation planning
- **Multi-Domain Coordination**: Cross-functional expertise → comprehensive implementation strategies
- **Quality Integration**: Workflow validation → testing strategies → deployment planning

## Examples

### Systematic PRD Workflow
```
/sc:workflow ClaudeDocs/PRD/feature-spec.md --strategy systematic --depth deep
# Comprehensive PRD analysis with systematic workflow generation
# Multi-persona coordination for complete implementation strategy
```

### Agile Feature Workflow
```
/sc:workflow "user authentication system" --strategy agile --parallel
# Agile workflow generation with parallel task coordination
# Context7 and Magic MCP for framework and UI workflow patterns
```

### Enterprise Implementation Planning
```
/sc:workflow enterprise-prd.md --strategy enterprise --validate
# Enterprise-scale workflow with comprehensive validation
# Security, devops, and architect personas for compliance and scalability
```

### Cross-Session Workflow Management
```
/sc:workflow project-brief.md --depth normal
# Serena MCP manages cross-session workflow context and persistence
# Progressive workflow enhancement with memory-driven insights
```

## Boundaries

**Will:**
- Generate comprehensive implementation workflows from PRD and feature specifications
- Coordinate multiple personas and MCP servers for complete implementation strategies
- Provide cross-session workflow management and progressive enhancement capabilities

**Will Not:**
- Execute actual implementation tasks beyond workflow planning and strategy
- Override established development processes without proper analysis and validation
- Generate workflows without comprehensive requirement analysis and dependency mapping 