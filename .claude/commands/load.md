**Purpose**: Project context loading and analysis

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Load and analyze project context in $ARGUMENTS.

## Purpose
Load and analyze project context in $ARGUMENTS to build comprehensive understanding of codebase structure, architecture, and patterns.

## Syntax
`/load [flags] [path]`

@include shared/flag-inheritance.yml#Universal_Always

## Core Flags

--scope flag:
- minimal: Core files only
- standard: Main source & config
- comprehensive: All relevant files
- full: Complete project analysis

--focus flag:
- architecture: System design
- api: API endpoints & contracts
- database: Schema & queries
- frontend: UI components
- testing: Test coverage

--format flag:
- summary: High-level overview
- detailed: Comprehensive analysis
- visual: Include diagrams
- structured: YAML/JSON output

## Loading Strategy

Progressive Loading:
1. Core files (package.json, config)
2. Entry points (main, index)
3. Key modules & components
4. Tests & documentation
5. Supporting files

Smart Selection:
- Prioritize by importance
- Skip generated files
- Focus on active code
- Include critical configs
- Respect .gitignore

## Analysis Components

Structure Analysis:
- Directory organization
- Module dependencies
- Component hierarchy
- API surface area
- Database schema

Pattern Detection:
- Design patterns used
- Coding conventions
- Architecture style
- Technology stack
- Best practices

Quality Metrics:
- Code complexity
- Test coverage
- Documentation level
- Technical debt
- Security concerns

## Output Format

Standard Report:
```yaml
Project: [Name]
Type: [Web App/API/Library]
Stack:
  Frontend: [Technologies]
  Backend: [Technologies]
  Database: [Type]
Architecture:
  Style: [Monolith/Microservices]
  Patterns: [List]
Key_Components:
  - [Component]: [Purpose]
Quality:
  Test_Coverage: X%
  Documentation: [Level]
  Complexity: [Score]
```

## Best Practices

Efficiency:
- Load incrementally
- Cache analysis results
- Focus on changes
- Skip redundant files
- Optimize memory usage

Accuracy:
- Verify assumptions
- Cross-reference files
- Check documentation
- Validate patterns
- Update regularly

## Examples

```bash
# Quick project overview
/load --scope minimal

# Full architecture analysis
/load --scope comprehensive --focus architecture

# API documentation generation
/load --focus api --format detailed

# Complete project understanding
/load --scope full --think-hard
```

## Integration

@include shared/loading-config.yml#Loading_Strategies

Works with:
- /analyze for deep inspection
- /document for documentation
- /improve for enhancements
- /estimate for planning

## Deliverables

- Project structure map
- Architecture diagram
- Component inventory
- Dependency graph
- Quality metrics report
- Pattern analysis