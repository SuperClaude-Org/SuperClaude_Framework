---
name: sc-validate-tests
description: Validate tier classification behavior against YAML test specifications. Self-validation skill for /sc-task-unified command testing.
allowed-tools: Read, Glob, Grep, TodoWrite
---

# /sc:validate-tests - Behavioral Test Validation Skill

## Purpose

Self-validation skill that enables Claude to test its own tier classification and behavioral compliance against YAML specification files.

```
/sc:validate-tests [test-file|test-directory] [flags]
```

---

## Triggers

### Explicit Invocation
```bash
/sc:validate-tests tests/sc-task-unified/
/sc:validate-tests tests/sc-task-unified/test_tier_classification.yaml
/sc:validate-tests --all
```

### Auto-Suggest
- After modifying tier classification configs
- After updating `/sc:task` skill definition
- When user asks "do the tests pass?"

---

## Usage

```bash
/sc:validate-tests [target] [flags]
```

### Flags

| Flag | Description |
|------|-------------|
| `--all` | Run all test files in `tests/sc-task-unified/` |
| `--verbose` | Show detailed results for each test case |
| `--summary` | Show only pass/fail counts (default) |
| `--category [name]` | Run specific test category only |
| `--stop-on-fail` | Stop at first failure |
| `--report [path]` | Save detailed report to file |

### Test Categories

| Category | File | Description |
|----------|------|-------------|
| `classification` | `test_tier_classification.yaml` | Golden dataset tier tests |
| `routing` | `test_verification_routing.yaml` | Verification method selection |
| `compound` | `test_compound_phrases.yaml` | Compound phrase overrides |
| `boosters` | `test_context_boosters.yaml` | Context-based score adjustments |
| `comparison` | `test_command_comparison.yaml` | Unified vs dual-command |
| `edge` | `test_edge_cases.yaml` | Boundary and unusual inputs |
| `integration` | `test_integration_scenarios.yaml` | End-to-end workflows |

---

## Behavioral Flow

### 1. Load Test Specifications
```yaml
actions:
  - Read target YAML file(s)
  - Parse test cases with expected outcomes
  - Group by category for organized execution
```

### 2. Execute Classification Logic
For each test case:
```yaml
actions:
  - Extract input text
  - Apply tier classification algorithm:
      1. Check compound phrases first (highest specificity)
      2. Match keywords against tier definitions
      3. Apply context boosters if context provided
      4. Calculate confidence score
      5. Apply priority rules (STRICT > EXEMPT > LIGHT > STANDARD)
      6. Handle ambiguity (escalate when scores within 0.1)
  - Record actual tier and confidence
```

### 3. Compare Results
```yaml
actions:
  - Compare actual_tier vs expected_tier
  - Check confidence within expected range
  - Verify requires_confirmation flag accuracy
  - Record pass/fail with details
```

### 4. Generate Report
```yaml
report_sections:
  - Summary: Total pass/fail/skip counts
  - By Category: Results grouped by test category
  - Failures: Detailed failure analysis
  - Recommendations: Suggested config adjustments
```

---

## Tier Classification Reference

### Priority Order
```
STRICT (1) > EXEMPT (2) > LIGHT (3) > STANDARD (4)
```

### Keyword Matching

#### STRICT Keywords (Priority 1)
```yaml
security_domain:
  - security, auth, authentication, authorization
  - password, credential, token, secret, encrypt
  - permission, access control, session, oauth, jwt

data_integrity:
  - database, migration, schema, model
  - transaction, query, sql, orm

scope_indicators:
  - refactor, remediate, restructure, overhaul
  - multi-file, system-wide, cross-module
  - breaking change, api contract

patterns:
  - path contains: auth/, security/, crypto/, models/, migrations/
  - file count > 2
```

#### EXEMPT Keywords (Priority 2)
```yaml
questions:
  - what, how, why, explain, understand
  - describe, clarify, tell me about

exploration:
  - explore, investigate, analyze (read-only)
  - review, check, look at, show me

planning:
  - plan, design, brainstorm, consider
  - think about, evaluate options

git_operations:
  - commit, push, pull, merge, rebase
  - git status, git diff, git log
```

#### LIGHT Keywords (Priority 3)
```yaml
trivial_changes:
  - typo, spelling, grammar
  - format, formatting, whitespace, indent
  - comment, documentation (inline)
  - rename (simple), lint, style

modifiers:
  - minor, small, quick, trivial, simple
  - tiny, brief, slight
```

#### STANDARD Keywords (Priority 4)
```yaml
code_modifications:
  - add, create, implement, build
  - update, modify, change, edit
  - fix, repair, correct, resolve
  - remove, delete, deprecate
```

### Compound Phrase Rules

**LIGHT Overrides** (check first):
```yaml
- "quick fix" → LIGHT
- "minor change" → LIGHT
- "fix typo" → LIGHT
- "small update" → LIGHT
- "update comment" → LIGHT
- "refactor comment" → LIGHT
- "fix spacing" → LIGHT
- "fix lint" → LIGHT
- "rename variable" → LIGHT
```

**STRICT Overrides** (security always wins):
```yaml
- "fix security" → STRICT
- "add authentication" → STRICT
- "update database" → STRICT
- "change api" → STRICT
- "modify schema" → STRICT
- Any LIGHT modifier + security keyword → STRICT
```

### Context Boosters

```yaml
file_count_boosters:
  - files > 2: STRICT +0.3
  - files == 1: LIGHT +0.1

path_pattern_boosters:
  - auth/, security/, crypto/: STRICT +0.4
  - tests/, __tests__/: STANDARD +0.2
  - docs/, *.md, *.txt: EXEMPT +0.5

operation_type_boosters:
  - is_read_only: EXEMPT +0.4
  - is_git_operation: EXEMPT +0.5
```

### Confidence Calculation

```python
def calculate_confidence(scores, context):
    # Base confidence from keyword matching
    max_score = max(scores.values())
    base_confidence = min(0.95, max_score)

    # Reduce for ambiguity
    sorted_scores = sorted(scores.values(), reverse=True)
    if len(sorted_scores) > 1:
        gap = sorted_scores[0] - sorted_scores[1]
        if gap < 0.1:
            base_confidence *= 0.85  # Ambiguous

    # Boost for compound phrases
    if context.get('compound_phrase_matched'):
        base_confidence = min(0.95, base_confidence + 0.15)

    # Reduce for vague input
    if context.get('vague_input') or context.get('no_keywords'):
        base_confidence *= 0.7

    return round(base_confidence, 2)
```

### Ambiguity Handling

```yaml
rules:
  - When top two tier scores within 0.1: escalate to higher priority tier
  - When confidence < 0.7: set requires_confirmation = true
  - When no keywords match: default to STANDARD with confidence 0.5
```

---

## Test Case Format

### Expected YAML Structure
```yaml
- id: TC001
  input: "fix the authentication bug"
  expected_tier: STRICT
  expected_confidence: ">= 0.85"
  keywords_matched: ["fix", "authentication"]
  compound_phrase: null
  requires_confirmation: false
  rationale: "Authentication keyword triggers STRICT"
```

### Validation Rules

| Field | Validation |
|-------|------------|
| `expected_tier` | Exact match required |
| `expected_confidence` | Supports ranges: `>= 0.85`, `0.70-0.80`, `< 0.60` |
| `requires_confirmation` | Boolean match when confidence < 0.7 |
| `keywords_matched` | At least one must be found (if specified) |
| `compound_phrase` | Must be detected if specified |

---

## Report Format

### Summary View (default)
```
═══════════════════════════════════════════════════════════
  /sc:validate-tests Report
═══════════════════════════════════════════════════════════

Test Suite: tests/sc-task-unified/
Timestamp:  2025-01-23 14:30:00

RESULTS
───────────────────────────────────────────────────────────
  Total:    300 tests
  ✅ Pass:   287 (95.7%)
  ❌ Fail:   11  (3.7%)
  ⏭️ Skip:   2   (0.7%)

BY CATEGORY
───────────────────────────────────────────────────────────
  classification    96/100  ████████████████████░░░░  96%
  routing          38/40   ███████████████████░░░░░  95%
  compound         29/30   ████████████████████████  97%
  boosters         24/25   ████████████████████████  96%
  comparison       39/40   ████████████████████████  98%
  edge             33/35   ██████████████████████░░  94%
  integration      28/30   ████████████████████████  93%

STATUS: ⚠️ 11 failures require attention
───────────────────────────────────────────────────────────
```

### Verbose View (--verbose)
```
═══════════════════════════════════════════════════════════
  Test: TC045 - "quick database update"
═══════════════════════════════════════════════════════════

Input:    "quick database update"
Expected: STRICT (confidence >= 0.80)
Actual:   STRICT (confidence: 0.85)

Classification Trace:
  1. Keywords found: ["quick" → LIGHT, "database" → STRICT, "update" → STANDARD]
  2. Compound phrases: None matched
  3. Context boosters: None
  4. Priority resolution: STRICT wins (priority 1 > all)
  5. Confidence: 0.85 (clear winner, no ambiguity)

Result: ✅ PASS
───────────────────────────────────────────────────────────
```

### Failure Detail
```
═══════════════════════════════════════════════════════════
  ❌ FAILURE: TC078
═══════════════════════════════════════════════════════════

Input:    "minor auth change"
Expected: STRICT (confidence >= 0.90)
Actual:   LIGHT (confidence: 0.75)

Analysis:
  - "minor" matched LIGHT tier
  - "auth" should have triggered STRICT override
  - Compound phrase "minor auth" not in override list

Recommendation:
  Add to config/tier-keywords.yaml under strict_wins:
    - "minor auth" → STRICT

───────────────────────────────────────────────────────────
```

---

## Examples

### Run All Tests
```bash
/sc:validate-tests --all

# Output: Summary of all 300 tests
```

### Run Specific Category
```bash
/sc:validate-tests --category classification

# Output: 100 tier classification tests
```

### Verbose Single File
```bash
/sc:validate-tests tests/sc-task-unified/test_compound_phrases.yaml --verbose

# Output: Detailed trace for each of 30 compound phrase tests
```

### Save Report
```bash
/sc:validate-tests --all --report claudedocs/validation-report.md

# Output: Full report saved to file
```

### Stop on First Failure
```bash
/sc:validate-tests --all --stop-on-fail

# Output: Stops and shows detail at first failure
```

---

## Integration with /sc:task

After validation:
```yaml
if all_tests_pass:
  - "Classification logic validated against 300 test cases"
  - "Ready for production use"

if failures_exist:
  - "Review failure details"
  - "Update tier-keywords.yaml or classification logic"
  - "Re-run validation"
```

---

## Boundaries

### Will
- Parse YAML test specifications
- Apply tier classification algorithm to test inputs
- Compare actual vs expected results
- Generate detailed reports with recommendations
- Identify configuration gaps

### Will Not
- Modify test files automatically
- Update configuration without user approval
- Execute actual code changes during validation
- Skip test categories without explicit flag

---

## Version History

- **v1.0.0** - Initial release for /sc:task-unified validation
