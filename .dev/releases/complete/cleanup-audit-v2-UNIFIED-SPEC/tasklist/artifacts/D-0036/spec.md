# D-0036: Report Depth Specification

**Task**: T04.10 — Report Depth Modes
**Status**: Complete

## Purpose

Support three report depth modes controlled by the `--depth` flag.

## Depth Modes

### Summary (`--depth summary`)

- Tier counts: total per classification tier.
- Top 10 highest-confidence files per tier.
- Budget summary (if budget tracking enabled).
- Consistency rate (single number).
- No per-section or per-file breakdown.

### Standard (`--depth standard`) — Default

- Everything in summary, plus:
- Per-section breakdown: each analysis phase with file counts and key findings.
- Directory assessments (if applicable per D-0031).
- Per-tier consistency rates.
- Conflict resolution summary (count, not per-file).

### Detailed (`--depth detailed`)

- Everything in standard, plus:
- Per-file classification with evidence arrays.
- Full conflict resolution log.
- Mismatch details from spot-check validation.
- Per-file confidence scores.
- Degradation event log (if any).

## Flag Interface

```
--depth summary|standard|detailed
```

Default: `standard` if flag not provided.

## Constraints

- All depth modes include mandated sections from D-0039.
- Budget caveats (D-0035) present at all depths when budget data exists.
- Depth mode recorded in report metadata.
- Invalid depth value rejected with error listing valid options.
