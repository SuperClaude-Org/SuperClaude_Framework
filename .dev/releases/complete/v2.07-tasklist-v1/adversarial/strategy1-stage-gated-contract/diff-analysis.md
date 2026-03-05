# Step 1: Diff Analysis — Strategy 1: Stage-Gated Generation Contract

**Date**: 2026-03-04
**Orchestrator**: sc:adversarial pipeline
**Subject**: Strategy 1 — Add a Stage-Gated Generation Contract with ordered stages (ingest, parse/bucket, convert, enrich, emit, self-check)

---

## 1. Current State (Base Spec)

**Source files analyzed**:
- `sc-tasklist-command-spec-v1.0.md` (PRD §4.3, §6.2, §9)
- `tasklist-generation-pipeline-prd.md` (FR-2, FR-3, §6)
- `tasklist-spec-integration-strategies.md` (Strategy 1 proposal)
- `taskbuilder-integration-proposals.md` (cross-reference)

**Current flow in `sc-tasklist-command-spec-v1.0.md` §4.3**:
```
SKILL execution steps (numbered list, §4.3 Invocation Flow):
  1. Read roadmap text (§2 Input Contract)
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

**What the current spec says about stage validation**:
- §6.2 Content: "The SKILL.md body is the full v3.0 generator prompt" — verbatim carryover from v3.0
- §8 Self-Check: runs after generation is already written; validates structure post-hoc
- §9 Acceptance Criteria item 6: "The Sprint Compatibility Self-Check (§8) runs before output is finalized" — weak ordering constraint (before finalize, not before each Write)
- §5.4 Input Validation: validates inputs before skill invocation but no per-stage validation exists
- No explicit statement that stages must complete and validate before advancing
- No halt-on-failure semantics at stage boundaries
- The self-check (§8) is the only validation gate, and it is positioned after all file emission

**Current failure mode**: If the enrichment stage (§5) produces malformed tier classifications, the generator continues into file emission (§6) and writes invalid output. The self-check then reports errors, but files are already written.

---

## 2. Proposed Change (Strategy 1)

**Proposal**: Strengthen §6.2 with a required statement:
> "Each stage must complete and validate before advancing; no stage skipping."

**Add to §9 Acceptance Criteria**:
> "Generation reports completed stages in order and halts on failed stage validation."

**Named stages** (from strategy proposal):
1. Input ingest
2. Parse + phase bucketing
3. Task conversion
4. Enrichment
5. File emission
6. Self-check

---

## 3. Structural Differences

| Dimension | Current Spec | Strategy 1 Proposal |
|-----------|-------------|---------------------|
| Stage progression | Implicit ordering via numbered list | Explicit ordered contract with named stages |
| Validation timing | Post-hoc only (§8 after all writes) | Per-stage before advancement |
| Failure behavior | Generates invalid output, self-check reports errors | Halts at stage boundary, no partial writes |
| Stage boundary | None — continuous pipeline | Explicit validate-before-advance gates |
| Self-check position | "Before finalize" (after all writes) | After dedicated Stage 6, positioned as terminal gate |
| Output on failure | Partial/malformed files written | No output until all stages pass |
| Implementation surface | Zero new spec sections required | Strengthening §6.2 + one acceptance criterion |

---

## 4. Content Differences

**Content added by Strategy 1**:
- Required ordering semantics: "must complete and validate before advancing"
- Prohibition on stage skipping: "no stage skipping"
- Halt-on-failure contract: "halts on failed stage validation"
- Progress reporting: "Generation reports completed stages in order"

**Content NOT changed by Strategy 1**:
- Stage names/sequence (already implicit in §4.3)
- Self-check content (§8 unchanged)
- File emission rules (§6A, §6B unchanged)
- Task format, ID conventions, metadata fields
- Command layer (`tasklist.md`) entirely unchanged
- Installation, dev workflow, lint-architecture checks

---

## 5. Contradictions Identified

**C1 — §9 Criterion 6 vs. Strategy 1 halt semantics**:
Current text: "The Sprint Compatibility Self-Check (§8) runs before output is finalized"
Strategy 1 adds: "halts on failed stage validation"
These do not directly contradict, but §9 Criterion 6 implies the self-check is the only pre-finalize gate. Strategy 1 adds earlier gates. The criterion needs updating to reflect that ALL stage validations run before finalization, not only §8.

**C2 — "Verbatim" carry-forward policy in §6.2 vs. strengthening §6.2**:
§6.2 states: "The SKILL.md body is the full v3.0 generator prompt — sections §0 through §9 plus the Appendix — reformatted into skill convention but functionally identical."
Strategy 1 requires strengthening §6.2 with a new required statement. "Functionally identical" to v3.0 would be violated if v3.0 does not contain stage-gated semantics (it does not — v3.0 has no per-stage validation). This is a meaningful delta from the parity constraint framing.

**C3 — §4.3 Invocation Flow numbering vs. named stage contract**:
The invocation flow uses 8 numbered steps (items 6 and 7 have sub-items). The proposed stage contract uses 6 named stages. These do not map 1:1. Stage 5 "File emission" spans items 6a + 6b in the current flow. Stage 6 "Self-check" maps to item 7. The mismatch creates a maintenance risk: two representations of the same pipeline with different granularity.

---

## 6. Unique Contributions of Strategy 1

- Converts an implicit pipeline into an explicit contract
- Introduces fail-fast semantics at stage level (vs. post-hoc reporting)
- Eliminates partial write scenarios where invalid output is emitted before failure is detected
- Provides a debugging affordance: "reports completed stages in order" enables triage without re-reading full output
- Minimal spec footprint: two targeted changes (one sentence in §6.2, one criterion in §9) with large reliability gain
- Does not add interactive behavior, new UX, or new output formats — pure internal execution semantics

---

## 7. Risk Surface

| Risk | Likelihood | Source |
|------|-----------|--------|
| Over-specification of LLM execution model | Medium | LLM skill execution is not deterministic; "halt" semantics depend on LLM compliance |
| Stage definition drift (6 vs. 8 steps) | Medium | Two representations of pipeline create inconsistency |
| Parity claim conflict ("functionally identical") | Low-Medium | v3.0 has no stage gates; adding them technically breaks verbatim parity |
| Self-check positioning ambiguity | Low | C1 above; easily resolved by updating §9 Criterion 6 |
