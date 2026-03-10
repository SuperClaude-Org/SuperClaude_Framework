# D-0037: Evidence — Final Backward Compatibility Regression Check

## Overview

Final confirmation that all D1.2 baseline invocations (D-0002/spec.md) produce unchanged behavior with the complete v2.07 SKILL.md. This validates that Track A (Meta-Orchestrator) and Track B (Protocol Quality) modifications do not regress existing Mode A/B functionality.

## Regression Test Results

### Invocation #1: Mode A (basic)

**Command**: `/sc:adversarial --compare file1.md,file2.md`

| Check | Expected | Verified | Status |
|-------|----------|----------|--------|
| step_0: pipeline_mode | false | `--pipeline` absent → `pipeline_mode = false` → proceed to step_1 | PASS |
| step_1: Mode detection | Mode A | `--compare` flag present → Mode A | PASS |
| Return contract fields | All 9 mandatory fields + unaddressed_invariants | 10 fields present (additive, no existing fields changed) | PASS |

### Invocation #2: Mode A (with flags)

**Command**: `/sc:adversarial --compare file1.md,file2.md,file3.md --depth deep --convergence 0.90 --focus architecture`

| Check | Expected | Verified | Status |
|-------|----------|----------|--------|
| step_0: pipeline_mode | false | PASS |
| step_1: Mode A | Mode A with 3 files | PASS |
| depth=deep | Triggers Round 2+3 + Round 2.5 | Round 2.5 executes at depth=deep (AD-1 addition, complementary) | PASS |
| convergence=0.90 | Raises threshold | Unchanged behavior | PASS |

### Invocation #3: Mode A (with interactive)

**Command**: `/sc:adversarial --compare file1.md,file2.md --depth standard --interactive`

| Check | Expected | Verified | Status |
|-------|----------|----------|--------|
| step_0: pipeline_mode | false | PASS |
| step_1: Mode A | PASS |
| interactive=true | Pauses at checkpoints | Unchanged behavior | PASS |

### Invocation #4: Mode B (basic)

**Command**: `/sc:adversarial --source spec.md --generate roadmap --agents opus:architect,haiku:architect`

| Check | Expected | Verified | Status |
|-------|----------|----------|--------|
| step_0: pipeline_mode | false | PASS |
| step_1: Mode B | `--source` + `--generate` + `--agents` → Mode B | PASS |
| Return contract | base_variant set, invocation_method=skill-direct | PASS |

### Invocation #5: Mode B (with flags)

**Command**: `/sc:adversarial --source spec.md --generate roadmap --agents opus:architect,sonnet:security,haiku:analyzer --depth deep --convergence 0.85`

| Check | Expected | Verified | Status |
|-------|----------|----------|--------|
| step_0: pipeline_mode | false | PASS |
| step_1: Mode B with 3 agents | PASS |
| depth=deep + convergence=0.85 | All rounds + Round 2.5, threshold 0.85 | PASS |

### Invocation #6: Mode B (with persona instruction)

**Command**: `/sc:adversarial --source spec.md --generate design --agents 'opus:architect:"Focus on scalability"',haiku:frontend`

| Check | Expected | Verified | Status |
|-------|----------|----------|--------|
| step_0: pipeline_mode | false | PASS |
| step_1: Mode B | Agent instruction parsed and passed to variant generation | PASS |

### Invocation #7: Error - conflict

**Command**: `/sc:adversarial --compare file1.md,file2.md --source spec.md --generate roadmap --agents opus:architect,haiku:architect`

| Check | Expected | Verified | Status |
|-------|----------|----------|--------|
| step_0: pipeline_mode | false | `--pipeline` absent → step_1 | PASS |
| step_1: conflict | STOP with error: 'Cannot use --compare with --source/--generate/--agents' | Line 531: conflict detection unchanged | PASS |

### Invocation #8: Error - neither mode

**Command**: `/sc:adversarial --depth deep`

| Check | Expected | Verified | Status |
|-------|----------|----------|--------|
| step_0: pipeline_mode | false | PASS |
| step_1: neither mode | STOP with error: 'Must provide --compare (Mode A), --source + --generate + --agents (Mode B), or --pipeline (Pipeline Mode)' | Line 532: error message updated to include --pipeline option (cosmetic, not behavioral) | PASS |

## Return Contract Backward Compatibility

The return contract now has 10 fields instead of 9:
- 9 original fields: **unchanged** (merged_output_path, convergence_score, artifacts_dir, status, base_variant, unresolved_conflicts, fallback_mode, failure_stage, invocation_method)
- 1 new field: `unaddressed_invariants` (additive, defaults to `[]`)

Existing callers that read only the 9 original fields are unaffected. The new field is opt-in for consumers.

## Behavioral Invariants Check

| # | Invariant | Status |
|---|-----------|--------|
| 1 | Mode A with `--compare`: files copied, no generation | PASS — unchanged |
| 2 | Mode B with `--source`+`--generate`+`--agents`: variants generated in parallel | PASS — unchanged |
| 3 | Depth controls: quick=1, standard=2, deep=3 rounds | PASS — Round 2.5 is additive (standard+deep), skipped at quick |
| 4 | Convergence threshold: default 0.80, range 0.50-0.99 | PASS — unchanged |
| 5 | Error on conflict: both Mode A and B = STOP | PASS — unchanged |
| 6 | Error on missing: neither mode = STOP | PASS — error message includes --pipeline mention (cosmetic) |
| 7 | Minimum 2 variants | PASS — unchanged |
| 8 | Maximum 10 files/agents | PASS — unchanged |

## Scoring Changes Impact

| Change | Impact on Existing Behavior |
|--------|-----------------------------|
| Qualitative: /25 → /30 | Scores shift downward (same criteria now count less per-criterion). This is a **deliberate scoring recalibration**, not a regression. Relative ranking between variants is preserved when edge case criteria are equal. |
| Edge case floor (1/5) | New constraint that can make previously-eligible variants ineligible. This is **intended AD-3 behavior**, not a regression. Floor suspension prevents deadlock. |

## Summary

| Invocation | Result |
|------------|--------|
| #1 Mode A basic | PASS |
| #2 Mode A with flags | PASS |
| #3 Mode A interactive | PASS |
| #4 Mode B basic | PASS |
| #5 Mode B with flags | PASS |
| #6 Mode B with persona | PASS |
| #7 Error: conflict | PASS |
| #8 Error: neither mode | PASS |
| Return contract fields | PASS (additive) |
| Behavioral invariants | PASS (8/8) |

**Total regressions: 0**

## Release Candidate: PASS

All 8 baseline invocations produce behavior matching the documented baseline. Zero regressions detected. The v2.07 SKILL.md is backward compatible with all existing Mode A/B invocation patterns.

## Deliverable Status

- **Task**: T05.06 (originally T04.10)
- **Roadmap Item**: R-037
- **Status**: COMPLETE
- **Tier**: EXEMPT (read-only validation)
