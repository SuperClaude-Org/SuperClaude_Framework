# D-0038: Anti-Lazy Guard Specification

**Task**: T04.12 — Anti-Lazy Classification Guard
**Status**: Complete

## Purpose

Detect and prevent uniform or lazy classification patterns that indicate analysis failure.

## Uniformity Threshold

- If >= 90% of files in any single batch receive the same classification, the guard triggers.
- Threshold applies per-batch, not globally (global skew may be legitimate).

## Guard Rules

1. **Detection**: After each batch, compute the distribution of classifications.
2. **Trigger condition**: `max(tier_counts) / batch_size >= 0.90`.
3. **On trigger**: Log a warning and flag the batch for re-analysis.
4. **Re-analysis**: Re-run the batch with an explicit prompt directive to differentiate files.
5. **Second trigger**: If re-analysis still exceeds 90% uniformity, accept results but flag as `"uniformity_warning": true`.

## Guard Scope

- Applies to batches of size >= 10 (small batches may legitimately be uniform).
- Does not apply to directory assessment summaries.
- Guard state is logged and included in report metadata.

## Configuration

```
--uniformity-threshold 0.90    # Default
--disable-lazy-guard           # Opt-out flag
```

## Constraints

- Guard cannot modify classifications directly; it only triggers re-analysis.
- Re-analysis uses the same capabilities as the original analysis.
- Maximum one re-analysis attempt per batch (no infinite loops).
