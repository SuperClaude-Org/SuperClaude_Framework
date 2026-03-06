# D-0017: Backward Compatibility Regression Report

## Overview

Regression test of 8 canonical invocations from D-0002 baseline against SKILL.md after Phase 2 (M2 + M3) modifications.

## Regression Results

| # | Mode | Invocation Pattern | Status | Notes |
|---|------|--------------------|--------|-------|
| 1 | A (basic) | `--compare file1.md,file2.md` | PASS | step_0 routes to Mode A via pipeline_mode=false |
| 2 | A (flags) | `--compare ... --depth deep --convergence 0.90 --focus architecture` | PASS | All flags parsed correctly, depth/convergence/focus documented |
| 3 | A (interactive) | `--compare ... --interactive` | PASS | Interactive checkpoint behavior documented |
| 4 | B (basic) | `--source spec.md --generate roadmap --agents opus:architect,haiku:architect` | PASS | step_0 routes to Mode B via pipeline_mode=false |
| 5 | B (flags) | `--source ... --agents x3 --depth deep --convergence 0.85` | PASS | 3-agent variant generation, all rounds triggered |
| 6 | B (persona) | `--source ... --agents 'opus:architect:"Focus on scalability"',haiku:frontend` | PASS | Agent instruction parsing intact |
| 7 | Error: conflict | `--compare ... --source ...` | PASS | STOP error: "Cannot use --compare with --source/--generate/--agents" |
| 8 | Error: neither | `--depth deep` (no mode flag) | PASS | STOP error: "Must provide --compare, --source+--generate+--agents, or --pipeline" |

## Invariant Verification

| Invariant | Status |
|-----------|--------|
| step_0_pipeline_guard routes to Mode A/B when --pipeline absent | PASS |
| step_1_detect_mode gated by pipeline_mode == false | PASS |
| All 9 mandatory return contract fields present | PASS |
| M2 additions gated behind pipeline_mode == true | PASS |
| M3 additions are additive (no existing steps removed) | PASS |
| Depth controls: quick=1, standard=2, deep=3 | PASS |
| Min 2 / Max 10 variant constraints | PASS |
| Convergence formula backward-compatible (A-NNN=0 identical) | PASS |

## Verdict

**PASS**: 0 regressions detected across all 8 baseline invocations and 8 invariants.

## Deliverable Status

- **Task**: T03.01
- **Roadmap Item**: R-017
- **Status**: COMPLETE
- **Tier**: EXEMPT
