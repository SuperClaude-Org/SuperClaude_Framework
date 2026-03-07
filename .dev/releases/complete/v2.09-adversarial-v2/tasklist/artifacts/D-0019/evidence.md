# D-0019: Step 1 Overhead Measurement Report

## Methodology

Measured structural overhead of M3 (shared assumption extraction, AD-2) additions to Step 1 by counting SKILL.md lines and estimating token count using heuristic (~1.3 tokens/word).

## Measurements

| Component | Lines | Words | Est. Tokens |
|-----------|-------|-------|-------------|
| Step 1 baseline (mode detection + diff assembly, excl. M3) | 334 | 1,574 | ~2,046 |
| M3 addition (shared_assumption_extraction + 6_shared_assumptions) | 64 | 376 | ~489 |

## Delta Calculation

```
delta = M3_tokens / baseline_tokens * 100
delta = 489 / 2046 * 100 = 23.9%
```

## NFR-004 Compliance

**Threshold**: <=10%
**Measured**: ~24%
**Status**: EXCEEDS THRESHOLD

## Mitigating Factors

1. The measurement captures specification size, not runtime cost. At runtime, shared_assumption_extraction only activates when a Mode A/B debate reaches Step 1 (not during pipeline parsing, dry-run, or error exits).
2. The extraction engine section (53 lines, 78% of overhead) could be extracted to a reference section, keeping only a compact dispatch pointer inline in Step 1.
3. The convergence formula change (A-NNN in denominator) adds <5 lines — the overhead is dominated by the engine specification.

## Remediation Recommendation

Extract the shared_assumption_extraction engine specification to its own section (parallel to the existing debate_topic_taxonomy section) and replace it with a 3-line dispatch pointer in Step 1. This would reduce Step 1 overhead to ~5-6%.

## Deliverable Status

- **Task**: T03.03
- **Roadmap Item**: R-019
- **Status**: COMPLETE (measurement done; NFR threshold exceeded)
- **Tier**: STANDARD
- **Fallback**: Remediation deferred to Phase 5 optimization pass
