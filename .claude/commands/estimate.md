**Purpose**: Project complexity and time estimation

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Provide comprehensive time, complexity, and resource estimates for tasks specified in $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/estimate "Add user authentication"` - Quick feature estimate
- `/estimate --scope project --detail high --team medium` - Detailed project estimation
- `/estimate --scope migration --team large --ultrathink` - Migration project estimation

Estimation modes:

**--scope:** Estimation scope
- feature: Single feature estimation | epic: Multi-feature epic
- project: Full project scope | refactor: Code refactoring effort | migration: Data/system migration

**--team:** Team size  
- solo: Single developer | small: 2-3 developers
- medium: 4-8 developers | large: 9+ developers

**--detail:** Estimation detail level
- high: Detailed breakdown | medium: Standard estimates | low: Quick rough estimates

## Estimation Framework

@include shared/execution-patterns.yml#Estimation_Methodology

@include shared/docs-patterns.yml#Standard_Notifications

@include shared/universal-constants.yml#Standard_Messages_Templates