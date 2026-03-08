# D-0020: Analysis Output Specification

**Task**: T02.09
**Roadmap Items**: R-040, R-042
**Date**: 2026-03-08
**Depends On**: D-0017, D-0018

---

## portify-analysis.md Format

Phase 1 produces `portify-analysis.md` following the template from `refs/analysis-protocol.md`. The file must be under 400 lines.

### Structure

```markdown
---
source_skill: <skill-name>
source_command: <command-name>
step_count: <N>
parallel_groups: <N>
gate_count: <N>
agent_count: <N>
complexity: simple|moderate|high
---

# Portification Analysis: {workflow-name}

## Source Components

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
(from component inventory C-NNN)

## Step Graph

### Step S-001: {name}
- **Type**: pure_programmatic | claude_assisted | hybrid
- **Confidence**: 0.XX
- **Inputs**: [list]
- **Output**: artifact-name
- **Gate**: EXEMPT | LIGHT | STANDARD | STRICT
- **Gate Mode**: BLOCKING | TRAILING
- **Agent**: none | agent-name
- **Parallel**: yes (group N) | no
- **Timeout**: Ns
- **Retry**: N
- **Notes**: ...

(repeat for each step)

## Parallel Groups

| Group | Steps | Rationale |
|-------|-------|-----------|
(from DAG analysis)

## Gates Summary

| Step | Tier | Mode | Frontmatter | Min Lines | Semantic Checks |
|------|------|------|-------------|-----------|-----------------|
(from gate assignments)

## Dependency DAG

```
S-001 → S-002 → S-003
                  ↓
              S-004 → S-005 → S-006
```

## Classification Summary

| Category | Count | Steps |
|----------|-------|-------|
| Pure Programmatic | N | S-XXX, ... |
| Claude-Assisted | N | S-XXX, ... |
| Hybrid | N | S-XXX, ... |

## Conservation Invariant

source_steps: N | classified_steps: N | invariant: HOLDS

## Self-Validation Results

| Check | Type | Result | Message |
|-------|------|--------|---------|
(7 checks)

## Recommendations

- (any recommendations for downstream phases)
```

### Line Count Enforcement

The analysis output must be < 400 lines. If the workflow has many steps, compress the step graph section by:
1. Omitting Notes field when null
2. Using shorter single-line format for steps with default values
3. Combining parallel groups into the step graph rather than separate table

---

## portify-analysis.yaml Contract

Emitted per D-0011 schema (Phase 1 contract). Contains all structured data from the analysis:
- Component inventory
- Step graph with classifications
- Dependency DAG
- Gate assignments
- Self-validation results
- Conservation invariant
- User review status
