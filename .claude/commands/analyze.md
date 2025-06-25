# Multi-dimensional Analysis & Debugging

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Command_Header

Multi-dimensional analysis on code, arch, or problem in $ARGUMENTS.

@include shared/command-templates.yml#Universal_Flags
@see shared/thinking-modes.yml ∀ thinking flags
@see shared/mcp-flags.yml ∀ MCP controls

Examples:
- `/user:analyze --code --think` - Code review w/ context
- `/user:analyze --arch --think-hard` - Deep arch analysis
- `/user:analyze --security --ultrathink` - Comprehensive security audit

Analysis modes:

**--code:** Quality review→naming, structure, DRY, complexity | Bugs→null checks, boundaries, types | Security→injection, auth, validation | Perf→O(n²), N+1, memory

**--arch:** System design & patterns | Layer coupling | Scalability bottlenecks | Maintainability assessment | Improvement suggestions

**--profile:** CPU, memory, execution time | Network latency, DB queries | Frontend metrics | Bottleneck identification | Optimization recommendations

**--security:** OWASP top 10 | Auth & authorization | Data handling & encryption | Attack vector identification

**--perf:** Bottleneck analysis | Algorithm complexity | DB queries & indexes | Caching strategies | Resource utilization

**--watch:** Continuous file monitoring | Real-time quality tracking | Auto re-analysis | Live metrics

**--interactive:** Guided exploration | Step-by-step fixes | Live improvement

@include shared/command-templates.yml#Research_Requirements

@include shared/command-templates.yml#Report_Output

Deliverables: @include shared/constants.yml#Success_Messages