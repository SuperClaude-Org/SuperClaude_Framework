# Base Selection

## Quantitative Scoring (50%)

| Variant | RC | IC | SR | DC | SC | Quant Score |
|---|---:|---:|---:|---:|---:|---:|
| Variant 1 (opus:backend) | 0.86 | 0.96 | 0.77 | 0.78 | 0.90 | 0.853 |
| Variant 2 (sonnet:backend) | 0.92 | 0.97 | 0.86 | 0.88 | 0.93 | 0.916 |
| Variant 3 (haiku:backend) | 0.72 | 0.95 | 0.64 | 0.66 | 0.82 | 0.772 |

## Qualitative Scoring (50%)

| Variant | Completeness (5) | Correctness (5) | Structure (5) | Clarity (5) | Risk (5) | Total/25 | Qual Score |
|---|---:|---:|---:|---:|---:|---:|---:|
| Variant 1 | 4 | 4 | 4 | 4 | 5 | 21 | 0.84 |
| Variant 2 | 5 | 5 | 5 | 4 | 4 | 23 | 0.92 |
| Variant 3 | 3 | 4 | 3 | 4 | 3 | 17 | 0.68 |

## Combined Scoring

Formula: `score = 0.50*quant + 0.50*qual`

| Variant | Quant | Qual | Final |
|---|---:|---:|---:|
| Variant 1 | 0.853 | 0.840 | 0.847 |
| Variant 2 | 0.916 | 0.920 | 0.918 |
| Variant 3 | 0.772 | 0.680 | 0.726 |

## Selected Base

**Base Variant:** Variant 2 (`sonnet:backend`)
**Rationale:** Highest combined score, strongest traceability, clearest implementation mapping, and best alignment with acceptance criteria matrix.

## Incorporations from Non-Base Variants
- From Variant 1: preserve explicit context-window pressure and budget arithmetic caveats for Phase 3/4.
- From Variant 3: keep concise section headings where possible for scanability.
