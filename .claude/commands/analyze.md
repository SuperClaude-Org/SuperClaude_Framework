**Purpose**: Multi-dimensional code and system analysis

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Multi-dimensional analysis on code, arch, or problem in $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/analyze --code --think` - Code review w/ context
- `/analyze --arch --think-hard` - Deep arch analysis  
- `/analyze --security --ultrathink` - Comprehensive security audit

Analysis modes:

**--code:** Quality review→naming, structure, DRY, complexity | Bugs→null checks, boundaries, types | Security→injection, auth, validation | Perf→O(n²), N+1, memory

**--arch:** System design & patterns | Layer coupling | Scalability bottlenecks | Maintainability assessment | Improvement suggestions

**--profile:** CPU, memory, execution time | Network latency, DB queries | Frontend metrics | Bottleneck identification | Optimization recommendations  

**--security:** OWASP top 10 | Auth & authorization | Data handling & encryption | Attack vector identification

**--perf:** Bottleneck analysis | Algorithm complexity | DB queries & indexes | Caching strategies | Resource utilization

**--watch:** Continuous file monitoring | Real-time quality tracking | Auto re-analysis | Live metrics

**--interactive:** Guided exploration | Step-by-step fixes | Live improvement

@include shared/research-patterns.yml#Mandatory_Research_Flows

@include shared/docs-patterns.yml#Standard_Notifications

@include shared/universal-constants.yml#Standard_Messages_Templates