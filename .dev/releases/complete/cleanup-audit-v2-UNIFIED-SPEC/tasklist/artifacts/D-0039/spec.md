# D-0039: Report Completeness Specification

**Task**: T04.13 — Report Completeness Validation
**Status**: Complete

## Purpose

Ensure every generated report contains all mandated sections and directory assessments.

## Mandated Sections (per AC1)

Every report, regardless of depth mode, must contain these 6 sections:

| # | Section | Content |
|---|---------|---------|
| 1 | Executive Summary | Tier counts, total files, consistency rate |
| 2 | Classification Breakdown | Per-tier file lists or counts (depth-dependent) |
| 3 | Validation Results | Spot-check consistency rate, per-tier rates |
| 4 | Budget Report | Consumption summary, caveats (if budget enabled) |
| 5 | Methodology Notes | Phases run, capabilities used, degradation events |
| 6 | Recommendations | Prioritized action items based on findings |

## Directory Assessment Check (per AC16)

- For every directory that exceeds the threshold (D-0031), a directory assessment block must be present.
- Completeness validator checks: `assessed_directories` count matches `directories_above_threshold` count.

## Validation Process

1. After report generation, run completeness check.
2. Verify each of the 6 mandated sections exists and is non-empty.
3. Verify directory assessments match threshold-exceeding directories.
4. Missing sections cause a validation failure with specific section named.

## Failure Behavior

- Completeness failure blocks report finalization.
- Error message identifies exactly which sections are missing.
- Report is written to a `.draft` file until completeness passes.

## Constraints

- Completeness check runs at all depth levels.
- Degraded reports (L4-L5) still require all 6 sections (content may note degradation).
- Check is non-bypassable; no flag to skip it.
