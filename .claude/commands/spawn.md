# /spawn - Spawn focused agent for specialized tasks

## Legend
@include shared/universal-constants.yml#Universal_Legend

## Purpose
Spawn specialized sub-agents to handle specific tasks in $ARGUMENTS with focused expertise and parallel execution capabilities.

## Syntax
`/spawn [flags] [task-description]`

@include shared/flag-inheritance.yml#Universal_Always

## Core Flags

--agent flag:
- researcher: Deep research & analysis
- builder: Code generation
- reviewer: Code review & QA
- optimizer: Performance tuning
- documenter: Documentation expert

--mode flag:
- sequential: One agent at a time
- parallel: Multiple agents
- collaborative: Agents work together
- supervisor: Oversee sub-agents

--scope flag:
- focused: Single specific task
- broad: Multiple related tasks
- exploratory: Open-ended research
- iterative: Refine through cycles

## Agent Types

Researcher Agent:
- Deep dive into topics
- Compare solutions
- Analyze trade-offs
- Find best practices
- Document findings

Builder Agent:
- Generate code
- Implement features
- Create tests
- Build prototypes
- Integrate systems

Reviewer Agent:
- Code quality checks
- Security analysis
- Performance review
- Best practice validation
- Suggest improvements

Optimizer Agent:
- Performance profiling
- Resource optimization
- Algorithm improvements
- Database tuning
- Cache strategies

Documenter Agent:
- API documentation
- User guides
- Code comments
- Architecture docs
- README files

## Execution Modes

Sequential Mode:
```yaml
Flow: Agent1 → Agent2 → Agent3
Use: When tasks depend on each other
Example: Research → Build → Review
```

Parallel Mode:
```yaml
Flow: Agent1 | Agent2 | Agent3
Use: For independent tasks
Example: Multiple feature builds
```

Collaborative Mode:
```yaml
Flow: Agents work together
Use: Complex problems
Example: System design session
```

## Best Practices

Task Definition:
- Clear objectives
- Specific deliverables
- Success criteria
- Resource limits
- Time constraints

Agent Selection:
- Match expertise to task
- Consider dependencies
- Plan coordination
- Set boundaries
- Define handoffs

Coordination:
- Clear communication
- Shared context
- Progress tracking
- Result integration
- Quality control

## Examples

```bash
# Research then implement
/spawn --agent researcher "OAuth 2.0 best practices"
/spawn --agent builder "Implement OAuth based on research"

# Parallel feature development
/spawn --mode parallel --agent builder "User auth, Profile API, Settings UI"

# Full cycle with review
/spawn --mode sequential "Research → Build → Review payment integration"

# Collaborative system design
/spawn --mode collaborative --ultrathink "Design microservices architecture"
```

## Integration

Works with:
- All command flags pass through
- Inherits persona preferences
- Shares project context
- Accumulates findings
- Coordinates outputs

## Deliverables

- Agent execution logs
- Task completion reports
- Integrated results
- Performance metrics
- Lessons learned
- Handoff documentation