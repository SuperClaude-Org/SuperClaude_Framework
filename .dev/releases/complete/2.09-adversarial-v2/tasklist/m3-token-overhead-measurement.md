# M3 Token Overhead Measurement: Step 1 shared_assumption_extraction

**Date**: 2026-03-05
**File**: `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`
**NFR**: NFR-004 (token overhead delta <= 10%)

---

## Measurement Scope

**Step 1 Section**: Lines 515-912 of SKILL.md
- From `step_1_detect_mode` through end of `diff_analysis_assembly` (including validation and similarity_check)
- This encompasses: mode detection, mode A/B parsing, common flags, variant loading, structural diff engine, content diff engine, contradiction detection, unique contribution extraction, shared assumption extraction, and diff-analysis.md assembly

---

## Baseline (Step 1 WITHOUT M3 additions)

| Metric | Value |
|--------|-------|
| Lines | 334 |
| Words | 1,574 |
| Characters | 13,928 |
| Est. tokens (1.3 tok/word) | **2,046** |
| Est. tokens (1 tok/4 chars) | **3,482** |

---

## M3 Additions (shared_assumption_extraction in Step 1)

### Block 1: Shared Assumption Extraction Engine (lines 789-841)
- The entire `### Shared Assumption Extraction Engine (AD-2)` section
- Includes: purpose, integration_point, agreement_identification, assumption_enumeration, classification, promotion_to_diff_points, output_format, AC_AD2_1 acceptance criterion
- **53 lines, 297 words, 2,583 chars**

### Block 2: 6_shared_assumptions assembly entry (lines 881-889)
- The `6_shared_assumptions` entry in `diff_analysis_assembly.assembly_order`
- Includes: source, section, format, content, table_columns
- **9 lines, 52 words, 537 chars**

### Block 3: Summary line addition (line 898)
- `- Total shared assumptions surfaced: <N> (UNSTATED: <N>, STATED: <N>, CONTRADICTED: <N>)`
- **1 line, 12 words, 97 chars**

### Inline fragments
- Line 859: `, shared assumptions (<N>)` appended to metadata categories (~4 words, ~30 chars)
- Line 906: `"A-NNN IDs are sequential starting from A-001 with no gaps"` validation rule (~11 words, ~63 chars)

### M3 Total

| Metric | Value |
|--------|-------|
| Lines | ~64 |
| Words | 376 |
| Characters | 3,310 |
| Est. tokens (1.3 tok/word) | **489** |
| Est. tokens (1 tok/4 chars) | **828** |

---

## Delta Calculation

| Method | M3 Tokens | Baseline Tokens | Delta |
|--------|-----------|-----------------|-------|
| Word-based (1.3 tok/word) | 489 | 2,046 | **23.89%** |
| Char-based (1 tok/4 chars) | 828 | 3,482 | **23.77%** |
| **Average** | -- | -- | **23.83%** |

---

## NFR-004 Compliance Verdict

| Criterion | Threshold | Measured | Result |
|-----------|-----------|----------|--------|
| Token overhead delta | <= 10% | 23.83% | **FAIL** |

The M3 shared assumption extraction additions to Step 1 represent approximately **23.8% token overhead** relative to the Step 1 baseline, which is **2.4x the 10% NFR-004 limit**.

---

## Notes

1. **Not counted as M3 Step 1 overhead** (belongs to Step 2): The `shared_assumption_handling` block in the advocate prompt template (lines 946-967, ~20 lines) and the `omission_detection` block (lines 961-967). These are Step 2 additions and would be measured separately.

2. **Not counted as M3 Step 1 overhead** (overview section): Lines 100-107 in the protocol overview summary. This is a top-level summary, not Step 1 implementation.

3. **Not counted as M3 Step 1 overhead** (debate taxonomy): Line 163 (`shared_assumption_rule` in auto_tagging). This is a Step 2 debate taxonomy addition.

4. The shared_assumption_extraction engine (Block 1, 53 lines) is the dominant contributor, accounting for ~78% of the M3 overhead.

---

## Remediation Suggestions

To bring the delta under 10%, the M3 additions would need to be reduced from ~376 words to ~157 words (a ~58% reduction). Possible approaches:

- **Extract to separate file**: Move the detailed shared_assumption_extraction engine specification to a `refs/` template file and reference it inline with a 2-3 line summary
- **Compress classification/enumeration**: The `assumption_enumeration.technique` and `classification` sub-sections could be condensed into a single compact table
- **Remove acceptance criterion from engine spec**: Move `AC_AD2_1` to a test file rather than inline in the protocol
- **Merge with unique_contribution_extraction**: Since shared assumptions run immediately after unique contributions, consider merging into a single "contribution and assumption analysis" section with shared infrastructure
