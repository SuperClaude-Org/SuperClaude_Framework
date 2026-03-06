# D-0002: Mode A/B Backward Compatibility Regression Baseline

## Overview

This document records the canonical Mode A and Mode B invocation patterns with their expected return contract values. Any change to SKILL.md that causes these invocations to produce different behavior constitutes a regression.

## Baseline Invocations

| # | Mode | Invocation | Expected Routing | Expected Return Contract Fields |
|---|------|------------|------------------|-------------------------------|
| 1 | A (basic) | `/sc:adversarial --compare file1.md,file2.md` | step_0: pipeline_mode=false, step_1: Mode A | `status: success\|partial\|failed`, `merged_output_path: <output>/adversarial/merged-*.md`, `convergence_score: float`, `artifacts_dir: <output>/adversarial/` |
| 2 | A (with flags) | `/sc:adversarial --compare file1.md,file2.md,file3.md --depth deep --convergence 0.90 --focus architecture` | step_0: pipeline_mode=false, step_1: Mode A | Same as #1; depth=deep triggers Round 2+3; convergence=0.90 raises threshold; focus filters debate topics |
| 3 | A (with interactive) | `/sc:adversarial --compare file1.md,file2.md --depth standard --interactive` | step_0: pipeline_mode=false, step_1: Mode A | Same as #1; interactive=true pauses at checkpoints for user input |
| 4 | B (basic) | `/sc:adversarial --source spec.md --generate roadmap --agents opus:architect,haiku:architect` | step_0: pipeline_mode=false, step_1: Mode B | `status: success\|partial\|failed`, `base_variant: <winner>`, `invocation_method: skill-direct` |
| 5 | B (with flags) | `/sc:adversarial --source spec.md --generate roadmap --agents opus:architect,sonnet:security,haiku:analyzer --depth deep --convergence 0.85` | step_0: pipeline_mode=false, step_1: Mode B | Same as #4; 3 agents produce 3 variants; depth=deep triggers all rounds |
| 6 | B (with persona instruction) | `/sc:adversarial --source spec.md --generate design --agents 'opus:architect:"Focus on scalability"',haiku:frontend` | step_0: pipeline_mode=false, step_1: Mode B | Same as #4; agent instruction passed to variant generation prompt |
| 7 | Error: conflict | `/sc:adversarial --compare file1.md,file2.md --source spec.md --generate roadmap --agents opus:architect,haiku:architect` | step_0: pipeline_mode=false, step_1: STOP with error | Error: `Cannot use --compare with --source/--generate/--agents` |
| 8 | Error: neither mode | `/sc:adversarial --depth deep` | step_0: pipeline_mode=false, step_1: STOP with error | Error: `Must provide --compare (Mode A), --source + --generate + --agents (Mode B), or --pipeline (Pipeline Mode)` |

## Return Contract Invariants

The following return contract fields must be present on **every** invocation, regardless of outcome:

| Field | Always Present | Notes |
|-------|---------------|-------|
| `merged_output_path` | Yes | `null` if merge not reached |
| `convergence_score` | Yes | `null` if debate not reached |
| `artifacts_dir` | Yes | Always set (directory created at pipeline start) |
| `status` | Yes | `success`, `partial`, or `failed` |
| `base_variant` | Yes | `null` if debate not reached |
| `unresolved_conflicts` | Yes | Integer, `0` on full success |
| `fallback_mode` | Yes | Boolean |
| `failure_stage` | Yes | `null` on success |
| `invocation_method` | Yes | `skill-direct`, `task-agent`, or `manual` |

## Behavioral Invariants

1. **Mode A with `--compare`**: Files are copied to `<output>/adversarial/variant-N-original.md`. No generation occurs.
2. **Mode B with `--source`+`--generate`+`--agents`**: Variants generated in parallel, one per agent spec.
3. **Depth controls**: `quick` = 1 round, `standard` = 2 rounds, `deep` = 3 rounds.
4. **Convergence threshold**: Default `0.80`, range `0.50-0.99`.
5. **Error on conflict**: Both Mode A and Mode B flags present = immediate STOP.
6. **Error on missing**: Neither Mode A nor Mode B flags = immediate STOP.
7. **Minimum variants**: Adversarial comparison requires at least 2 variants/files.
8. **Maximum variants**: Maximum 10 files (Mode A) or 10 agents (Mode B).

## Regression Testing Protocol

To verify backward compatibility after any SKILL.md modification:

1. Execute invocations #1-#6 above
2. Verify return contract contains all 9 mandatory fields
3. Verify invocations #7-#8 produce the expected error messages
4. Verify no new fields are required that break existing callers
5. Verify `artifacts_dir` structure matches expected layout

## Deliverable Status

- **Task**: T01.02
- **Roadmap Item**: R-002
- **Status**: COMPLETE
- **Tier**: EXEMPT (documentation-only, no code changes)
