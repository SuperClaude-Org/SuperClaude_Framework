# /estimate - Estimate time, complexity and resources

## Legend
@include shared/universal-constants.yml#Universal_Legend

## Purpose
Provide comprehensive time, complexity, and resource estimates for tasks specified in $ARGUMENTS using data-driven analysis.

## Syntax
`/estimate [flags] [task]`

@include shared/flag-inheritance.yml#Universal_Always

## Core Flags

--scope flag:
- feature: Single feature estimation
- epic: Multi-feature epic
- project: Full project scope
- refactor: Code refactoring effort
- migration: Data/system migration

--team flag:
- solo: Single developer
- small: 2-3 developers
- medium: 4-8 developers
- large: 9+ developers

--detail flag:
- high: Detailed breakdown
- medium: Standard estimates
- low: Quick rough estimates

## Estimation Components

Time Estimates:
- Development hours/days
- Testing & QA time
- Code review cycles
- Integration effort
- Buffer for unknowns

Complexity Analysis:
- Technical complexity score
- Integration points
- Dependencies & blockers
- Risk factors
- Learning curve

Resource Requirements:
- Developer skill levels
- Infrastructure needs
- Third-party services
- Testing resources
- Documentation effort

## Methodology

Estimation Factors:
- Historical data from similar tasks
- Code complexity metrics
- Team velocity & capacity
- Technical debt impact
- External dependencies

Risk Assessment:
- Technical risks
- Resource availability
- Timeline constraints
- Scope creep potential
- Integration challenges

## Output Format

Standard Estimate:
```yaml
Task: [Description]
Complexity: [Low/Medium/High]
Time_Estimate:
  Optimistic: X days
  Realistic: Y days
  Pessimistic: Z days
Resources:
  Developers: N
  QA: M hours
  Infrastructure: [Details]
Risks:
  - [Risk 1]: [Mitigation]
  - [Risk 2]: [Mitigation]
Assumptions:
  - [Assumption 1]
  - [Assumption 2]
```

## Best Practices

Accuracy:
- Break down into smaller tasks
- Consider all phases (dev, test, deploy)
- Include communication overhead
- Account for code reviews
- Add appropriate buffers

Communication:
- Provide ranges, not fixed numbers
- Document assumptions clearly
- Highlight major risks
- Update estimates as work progresses
- Track actual vs estimated

## Examples

```bash
# Quick feature estimate
/estimate "Add user authentication"

# Detailed project estimation
/estimate --scope project --detail high --team medium

# Refactoring estimate with risks
/estimate --scope refactor --think "Modernize legacy API"

# Migration project estimation
/estimate --scope migration --team large --ultrathink
```

## Deliverables

- Detailed time estimates with ranges
- Complexity analysis & metrics
- Resource allocation plan
- Risk assessment & mitigation
- Assumptions & dependencies
- Confidence levels