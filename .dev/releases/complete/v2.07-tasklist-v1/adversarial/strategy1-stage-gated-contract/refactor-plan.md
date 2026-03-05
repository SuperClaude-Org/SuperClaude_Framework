# Step 4: Refactoring Plan — Strategy 1: Stage-Gated Generation Contract

**Date**: 2026-03-04
**Decision**: ADOPT with modifications M1-M5
**Target spec**: `sc-tasklist-command-spec-v1.0.md`

---

## Modification Inventory

| ID | Modification | Target Section | Risk | Order |
|----|-------------|---------------|------|-------|
| M1 | Reword "halts" to instruction-appropriate language | §9 Acceptance Criteria | Low | 1 |
| M2 | Add per-stage validation criteria table | §6.2 (new subsection) | Low | 2 |
| M3 | Canonicalize 6-stage names in §4.3, retire numbered-step duplication | §4.3 Invocation Flow | Low | 3 |
| M4 | Add parity clarification note | §6.2 Content | Very Low | 4 |
| M5 | Update §9 Criterion 6 to cover all stage gates, not only §8 | §9 Acceptance Criteria | Low | 1 (with M1) |

---

## Integration Point 1: §4.3 Invocation Flow (M3)

### Current text (conceptual — 8-step numbered list)
```
SKILL execution:
  1. Read roadmap text (§2)
  2. Parse roadmap items (§4.1)
  3. Determine phase buckets (§4.2-4.3)
  4. Convert items to tasks (§4.4-4.5)
  5. Enrich: effort/risk/tier/confidence (§5)
  6. Generate multi-file bundle (§6):
     - Write tasklist-index.md (§6A)
     - Write phase-N-tasklist.md per phase (§6B)
  7. Run Sprint Compatibility Self-Check (§8)
  8. Return file paths
```

### Replacement text (M3 applied — named stage contract)
```
SKILL execution — Stage-Gated Contract:

  Stage 1: Input Ingest
    - Read roadmap text (§2 Input Contract)
    - Read spec/context if provided
    Validation: roadmap text is non-empty; required sections present

  Stage 2: Parse + Phase Bucketing
    - Parse roadmap items (§4.1)
    - Assign items to phase buckets (§4.2-4.3)
    Validation: all items assigned to exactly one phase; no items dropped

  Stage 3: Task Conversion
    - Convert phase items to task format (§4.4-4.5)
    Validation: all items produce valid task stubs with T<PP>.<TT> IDs; no ID collisions

  Stage 4: Enrichment
    - Assign effort/risk/tier/confidence to each task (§5)
    Validation: all tasks have non-empty effort, risk, tier, confidence fields

  Stage 5: File Emission
    - Write tasklist-index.md (§6A)
    - Write phase-N-tasklist.md per phase (§6B)
    Validation: all declared phase files exist on disk; index Phase Files table matches actual filenames

  Stage 6: Self-Check
    - Run Sprint Compatibility Self-Check (§8)
    Validation: all §8 checks pass; no check failures

  Stage progression rule: each stage must complete and pass its validation
  before advancing to the next stage. Do not proceed to Stage N+1 if Stage N
  validation criteria are not satisfied. Report completed stages in order
  using TodoWrite as each stage passes.
```

### Risk: Low
No output schema change. No command layer change. Replaces an implicit ordering with an explicit one.

---

## Integration Point 2: §6.2 Content (M2 + M4)

### Current text (relevant sentence)
```
The SKILL.md body is the full v3.0 generator prompt — sections §0 through §9 plus the
Appendix — reformatted into skill convention but functionally identical.
```

### Additional text to append after that sentence (M4 parity note + M2 reference)
```
Note on stage-gated execution (skill packaging addition): The stage-gated
generation contract (§4.3) is a reliability mechanism added during skill
packaging. It constrains execution behavior without altering the generation
algorithm, task schema, or output structure. The v3.0 generator did not
include per-stage validation semantics; this is intentional hardening for
automated sprint execution contexts.

The following per-stage validation criteria govern stage advancement:

| Stage | Name | Validation Criteria |
|-------|------|---------------------|
| 1 | Input Ingest | Roadmap text non-empty; required sections (phases/items) present; file read succeeded |
| 2 | Parse + Phase Bucketing | Every roadmap item assigned to exactly one phase; no ambiguous assignments remain unresolved; phase count ≥ 1 |
| 3 | Task Conversion | All roadmap items converted to task stubs; T<PP>.<TT> IDs assigned with no collisions; task titles non-empty |
| 4 | Enrichment | All tasks have non-empty: Effort (XS/S/M/L/XL), Risk (low/moderate/high), Tier (STANDARD/STRICT/EXEMPT/LIGHT), Confidence score |
| 5 | File Emission | tasklist-index.md written; all phase files referenced in index exist on disk; no extra phase files written |
| 6 | Self-Check | All Sprint Compatibility Self-Check assertions (§8) pass; no blocking failures |

If any stage validation criterion is not satisfied, the skill must not advance
to the next stage. Instead, report the failed criterion and the corrective
action taken (or, if correction is not possible, report the blocking error).
```

### Risk: Low
Additive only. Does not change any existing content.

---

## Integration Point 3: §9 Acceptance Criteria (M1 + M5)

### Current Criterion 6
```
6. The Sprint Compatibility Self-Check (§8) runs before output is finalized
```

### Replacement (M1 + M5 applied)
```
6. Generation executes in stage order (Ingest → Parse/Bucket → Convert → Enrich →
   Emit → Self-Check). Each stage must satisfy its validation criteria before the
   next stage begins. If a stage's validation criteria are not satisfied, the skill
   must not proceed to the next stage. Completed stages are reported in order via
   TodoWrite.
```

### New Criterion 10 (appended after existing criteria)
```
10. No output files are written unless Stage 1 through Stage 4 validations have
    passed. Stage 5 (File Emission) is only entered after all pre-write stages
    are validated.
```

### Risk: Low
Updates one criterion text (does not remove the §8 self-check requirement — it is now Stage 6). Adds one criterion to strengthen the pre-write gate.

---

## Non-Modified Sections

The following sections are explicitly NOT modified by this plan:
- `tasklist.md` command file (command layer entirely unchanged)
- §5.4 Input Validation (command-layer validation; skill-layer validation is separate)
- §8 Sprint Compatibility Self-Check (content unchanged; now positioned as Stage 6)
- §6A Index File Template (output schema unchanged)
- §6B Phase File Template (output schema unchanged)
- §7 Style Rules (unchanged)
- §7.1-§7.3 Lint-architecture checks (unchanged)
- All `rules/` and `templates/` extracted reference files (unchanged)

---

## Implementation Order

1. Apply M1 + M5 simultaneously to §9 (acceptance criteria update — one edit block)
2. Apply M2 + M4 simultaneously to §6.2 (parity note + per-stage criteria table — one edit block)
3. Apply M3 to §4.3 (replace 8-step list with 6-stage named contract)
4. Verify: `make lint-architecture` still passes (no structural changes that would affect checks)
5. Verify: manual read-through of SKILL.md flow confirms stage names align across §4.3 and §6.2

---

## Validation After Implementation

| Check | Method | Pass Criteria |
|-------|--------|--------------|
| Lint-architecture | `make lint-architecture` | No errors |
| §4.3 alignment with §6.2 | Manual review | 6 stage names match in both sections |
| §9 Criterion 6 covers §8 | Manual review | Criterion text references Stage 6 (Self-Check) |
| Parity note clarity | Manual review | Note clearly states "skill packaging addition" |
| Per-stage table completeness | Manual review | All 6 stages have validation criteria |
