# Time & Complexity Estimation

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Universal_Flags

Provide comprehensive time & complexity estimates for task in $ARGUMENTS.

Thinking flags (optional):
- --think→multi-component estimation w/ deps
- --think-hard→complex project estimation w/ risk analysis
- --ultrathink→enterprise-scale estimation w/ full uncertainty modeling

Examples:
- `/user:estimate --detailed --think` - Detailed breakdown w/ dependency analysis
- `/user:estimate --worst-case --think-hard` - Risk-based estimation w/ comprehensive scenarios
- `/user:estimate "migrate to microservices" --ultrathink` - Complex architectural estimation

Relevant factors:

Time components:
- Dev time→impl | Code review & feedback cycles | Testing (unit, integration, E2E)
- Deployment & verification | Docs updates

Complexity multipliers:
- New feature from scratch: 1x baseline | Refactoring existing: 1.5x (understanding + changing)
- Working w/ legacy: 2x (constraints + unknowns) | Cross-team deps: 1.5x (coordination overhead)

Uncertainty factors:
- Clear requirements, known tech: ±10%
- Some unknowns, new patterns: ±25%
- Significant unknowns, research needed: ±50%
- Completely new territory: ±100%

Estimation workflow:
1. Break down task into subtasks
2. Estimate each subtask individually
3. Apply complexity multipliers
4. Add appropriate uncertainty buffer
5. Provide a realistic range, not a single number

Formula: Base time × Complexity × Uncertainty = Time range

Include in estimates:
- Best case scenario (everything goes smoothly)
- Realistic case (normal friction and discoveries)
- Worst case scenario (significant obstacles)

## Additional Considerations

Context factors:
- Developer experience level with the codebase
- Availability of documentation and examples
- Required coordination with other teams
- Potential blockers or dependencies

Research requirements for estimation:
- Technology patterns → Research implementation complexity via C7 and official docs
- Architecture patterns → WebSearch for similar project timelines and case studies
- Team velocity → Check historical data and industry benchmarks
- Risk assessment → Must verify common pitfalls and mitigation strategies
- Never estimate based on gut feeling - always research comparable scenarios
- All estimates must cite sources: // Source: [estimation data reference]

Report Output:
- Estimate summaries: `.claudedocs/summaries/estimate-<timestamp>.md`
- Risk assessments: `.claudedocs/reports/risk-analysis-<timestamp>.md`
- Ensure directory exists: `mkdir -p .claudedocs/summaries/ .claudedocs/reports/`
- Include report location in output: "📄 Estimate saved to: [path]"

Deliverables: Time estimate range (min-max), complexity assessment, required resources, key assumptions, risk analysis, and potential blockers that could affect the estimate.