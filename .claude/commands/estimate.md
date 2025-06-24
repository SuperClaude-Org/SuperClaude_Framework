# /estimate - Estimate time, complexity and resources

## Legend
| Symbol | Meaning | | Abbrev | Meaning |
|--------|---------|---|--------|---------|
| → | leads to | | cfg | configuration |
| & | and/with | | impl | implementation |
| w/ | with | | perf | performance |
| @ | at/located | | ops | operations |
| > | greater than | | val | validation |
| ∀ | for all/every | | req | requirements |
| ∃ | exists/there is | | deps | dependencies |
| ∴ | therefore | | env | environment |
| ∵ | because | | db | database |
| ≡ | equivalent | | api | interface |
| ≈ | approximately | | docs | documentation |
| 📁 | directory/path | | std | standard |
| 🔢 | number/count | | def | default |
| 📝 | text/string | | ctx | context |
| ⚙ | setting/config | | err | error |
| 🎛 | control/flags | | exec | execution |
| 🔧 | configuration | | qual | quality |
| 📋 | group/category | | rec | recovery |
| 🚨 | critical/urgent | | sev | severity |
| ⚠ | warning/caution | | resp | response |
| 🔄 | retry/recovery | | esc | escalation |
| ✅ | success/fixed | | tok | token |
| ❌ | failure/error | | opt | optimization |
| ℹ | information | | UX | user experience |
| ⚡ | fast/quick | | UI | user interface |
| 🐌 | slow/delayed | | C | critical |
| ✨ | complete/done | | H | high |
| 📖 | read operation | | M | medium |
| ✏ | edit operation | | L | low |
| 🗑 | delete operation | | |

## Purpose
Provide comprehensive time, complexity, and resource estimates for tasks specified in $ARGUMENTS using data-driven analysis.

## Syntax
`/estimate [flags] [task]`

## Universal Flags
--plan: "Show execution plan before running"
--uc: "UltraCompressed mode (~70% token reduction)"
--ultracompressed: "Alias for --uc"
--think: "Multi-file analysis w/ context (4K tokens)"
--think-hard: "Deep architectural analysis (10K tokens)"
--ultrathink: "Critical system redesign (32K tokens)"
--c7: "Enable Context7→library documentation lookup"
--seq: "Enable Sequential→complex analysis & thinking"
--magic: "Enable Magic→UI component generation"
--pup: "Enable Puppeteer→browser automation & testing"
--all-mcp: "Enable all MCP servers"
--no-mcp: "Disable all MCP servers (native tools only)"
--no-c7: "Disable Context7 specifically"
--no-seq: "Disable Sequential thinking specifically"
--no-magic: "Disable Magic UI builder specifically"
--no-pup: "Disable Puppeteer specifically"

## Command-Specific Flags

**Estimation Types:**
- `--detailed`: Comprehensive breakdown with subtask analysis
- `--quick`: High-level estimate for rapid planning
- `--worst-case`: Risk-based estimation with comprehensive scenarios
- `--comparative`: Compare multiple approaches or solutions

**Analysis Depth:**
- `--dependencies`: Include cross-team and technical dependencies
- `--risks`: Detailed risk analysis with mitigation strategies
- `--resources`: Team composition and skill requirements
- `--timeline`: Milestone-based project timeline

**Research Integration:**
- `--c7`: Research similar projects and patterns
- `--seq`: Complex estimation with uncertainty modeling
- `--benchmarks`: Industry benchmark comparison

## Examples
- `/estimate --detailed --dependencies --think` → Detailed breakdown with dependency analysis
- `/estimate --worst-case --risks --think-hard` → Risk-based estimation with scenarios
- `/estimate "migrate to microservices" --comparative --ultrathink` → Complex architectural estimation
- `/estimate --quick --benchmarks --c7` → Rapid estimate with industry data
- `/estimate --timeline --resources --seq` → Resource planning with timeline

## Estimation Framework

**Time Components:**
- **Development**: Implementation, code review, feedback cycles
- **Testing**: Unit, integration, end-to-end testing
- **Documentation**: Technical docs, user guides, API documentation
- **Deployment**: Release preparation, deployment, verification
- **Buffer**: Uncertainty, learning, unexpected issues

**Complexity Multipliers:**
- **New Feature**: 1.0x baseline (green field development)
- **Refactoring**: 1.5x (understanding existing + changes)
- **Legacy Integration**: 2.0x (constraints + unknowns)
- **Cross-Team Dependencies**: 1.5x (coordination overhead)
- **New Technology**: 1.8x (learning curve + risk)

**Uncertainty Factors:**
- **Clear Requirements + Known Tech**: ±10% variance
- **Some Unknowns + New Patterns**: ±25% variance
- **Significant Research Required**: ±50% variance
- **Completely New Territory**: ±100% variance

## Estimation Process

**1. Task Decomposition:**
- Break down into measurable subtasks
- Identify dependencies and prerequisites
- Map required skills and expertise
- Determine critical path items

**2. Base Estimation:**
- Estimate each subtask individually
- Use historical data where available
- Apply complexity multipliers
- Add uncertainty buffers

**3. Scenario Planning:**
- **Best Case**: Everything goes smoothly (20% probability)
- **Most Likely**: Normal friction and discoveries (60% probability)
- **Worst Case**: Significant obstacles encountered (20% probability)

**4. Validation:**
- Compare with similar projects
- Review with team members
- Validate assumptions
- Document reasoning

## Context Factors

**Team Factors:**
- Developer experience with codebase
- Team familiarity with technology stack
- Available mentorship and support
- Team size and composition

**Project Factors:**
- Quality of existing documentation
- Codebase complexity and technical debt
- Testing and CI/CD maturity
- Deployment and infrastructure complexity

**External Factors:**
- Stakeholder availability for feedback
- Third-party service dependencies
- Regulatory or compliance requirements
- Market or business constraints

## Research Requirements

**Data Sources:**
- Technology patterns → Research via `--c7` and official documentation
- Architecture patterns → Industry case studies and benchmarks
- Team velocity → Historical data and productivity metrics
- Risk assessment → Common pitfalls and mitigation strategies

**Evidence-Based Estimation:**
- Never estimate based on intuition alone
- Always research comparable scenarios
- Cite sources for all estimates
- Validate assumptions with data

## Deliverables
- **Estimate Summary**: Time ranges (min-max) with confidence levels
- **Complexity Assessment**: Technical difficulty and risk factors
- **Resource Requirements**: Team composition and skill needs
- **Risk Analysis**: Potential blockers and mitigation strategies
- **Timeline**: Milestone-based project schedule
- **Assumptions**: Key assumptions and dependencies

## Output Locations
- **Estimates**: `.claudedocs/summaries/estimate-{timestamp}.md`
- **Risk Analysis**: `.claudedocs/reports/risk-analysis-{timestamp}.md`
- **Timelines**: `.claudedocs/summaries/timeline-{timestamp}.md`

## Research Requirements
External_Library_Research:
  - Identify library/framework mentioned
  - Context7 lookup for official documentation
  - Verify API patterns and examples
  - Check version compatibility
  - Document findings in implementation
Pattern_Research:
  - Search existing codebase for similar patterns
  - Magic component search if UI-related
  - WebSearch for official documentation
  - Validate approach with Sequential thinking
  - Document pattern choice rationale
API_Integration_Research:
  - Official documentation lookup
  - Authentication requirements
  - Rate limiting and error handling
  - SDK availability and examples
  - Integration testing approach

## Report Notifications
📄 Analysis report saved to: {path}
📊 Metrics updated: {path}
📋 Summary saved to: {path}
💾 Checkpoint created: {path}
📚 Documentation created: {path}
📁 Created directory: {path}
✅ {operation} completed successfully
❌ {operation} failed: {reason}
⚠ {operation} completed w/ warnings

## Best Practices

**Estimation Guidelines:**
- Provide ranges, not single numbers
- Include confidence levels
- Document all assumptions
- Plan for the unexpected
- Review and refine estimates regularly

**Common Pitfalls to Avoid:**
- Over-optimistic assumptions
- Ignoring integration complexity
- Underestimating testing time
- Forgetting documentation effort
- Missing deployment complexity

## Troubleshooting
- **Complex Projects**: Use `--ultrathink` for comprehensive analysis
- **Unknown Technologies**: Combine `--c7 --seq` for research-based estimates
- **High Uncertainty**: Use `--worst-case --risks` for scenario planning
- **Team Planning**: Include `--resources --timeline` for capacity planning

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
