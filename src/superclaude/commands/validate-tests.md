---
name: validate-tests
description: "Validate tier classification behavior against YAML test specifications"
category: testing
complexity: moderate
allowed-tools: Read, Glob, Grep, Bash, TodoWrite, Task, Skill
mcp-servers: [sequential]
personas: [qa, analyzer]
---

# /sc:validate-tests - Behavioral Test Validation

Validate tier classification behavior against YAML test specifications.

## Usage

```bash
/sc:validate-tests [target] [flags]
```

## Arguments

- `target`: Test file or directory (default: `tests/sc-task-unified/`)

## Flags

| Flag | Description |
|------|-------------|
| `--all` | Run all test files |
| `--verbose` | Show detailed trace for each test |
| `--summary` | Show only pass/fail counts (default) |
| `--category [name]` | Run specific category: classification, routing, compound, boosters, comparison, edge, integration |
| `--stop-on-fail` | Stop at first failure |
| `--report [path]` | Save report to file |

## Examples

```bash
# Run all tests
/sc:validate-tests --all

# Run specific category
/sc:validate-tests --category classification

# Verbose output for debugging
/sc:validate-tests tests/sc-task-unified/test_compound_phrases.yaml --verbose

# Save report
/sc:validate-tests --all --report claudedocs/validation-report.md
```

## Behavior

1. **Load**: Read YAML test specifications
2. **Execute**: Apply tier classification algorithm to each test input
3. **Compare**: Check actual vs expected tier, confidence, and flags
4. **Report**: Generate summary with pass/fail counts and failure details

## Test Categories

| Category | Tests | Purpose |
|----------|-------|---------|
| `classification` | 100 | Golden dataset for tier assignment |
| `routing` | 40 | Verification method selection |
| `compound` | 30 | Compound phrase overrides |
| `boosters` | 25 | Context-based adjustments |
| `comparison` | 40 | Unified vs dual-command |
| `edge` | 35 | Boundary and unusual inputs |
| `integration` | 30 | End-to-end workflows |

## Classification Algorithm

Reference: `skills/sc-validate-tests-protocol/classification-algorithm.yaml`

### Priority Order
```
STRICT (1) > EXEMPT (2) > LIGHT (3) > STANDARD (4)
```

### Phases
1. **Compound Phrases**: Check multi-word patterns first
2. **Keywords**: Match against tier keyword lists
3. **Context Boosters**: Apply file/path/operation adjustments
4. **Confidence**: Calculate score with ambiguity handling
5. **Resolution**: Apply priority rules for conflicts

## Report Format

```
═══════════════════════════════════════════════════════════
  /sc:validate-tests Report
═══════════════════════════════════════════════════════════

RESULTS
───────────────────────────────────────────────────────────
  Total:    300 tests
  ✅ Pass:   287 (95.7%)
  ❌ Fail:   11  (3.7%)
  ⏭️ Skip:   2   (0.7%)

BY CATEGORY
───────────────────────────────────────────────────────────
  classification    96/100  ████████████████████░  96%
  routing          38/40   ███████████████████░░  95%
  ...
```

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:validate-tests-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.

## Boundaries

**Will:**
- Validate tier classification behavior against YAML test specifications
- Apply the tier classification algorithm to test inputs and compare against expected results
- Generate summary reports with pass/fail counts and failure details

**Will Not:**
- Modify test specification files
- Change the classification algorithm itself
- Skip test categories without explicit user request

## See Also

- `/sc:task` - Unified task command
- `skills/sc-task-unified-protocol/SKILL.md` - Task skill definition
- `skills/sc-validate-tests-protocol/SKILL.md` - Full validation skill spec
