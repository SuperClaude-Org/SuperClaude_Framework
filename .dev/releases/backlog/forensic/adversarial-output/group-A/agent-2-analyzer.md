# Agent 2: Analyzer Assessment -- Group A Schema Integrity

**Perspective**: Evidence quality and proportionality
**Core question**: "Is the proposed change proportional to the identified risk? Is it over-engineering?"
**Date**: 2026-02-26

---

## PROPOSAL-006: Add missing schema for `new-tests-manifest.json`

**Verdict**: ACCEPT

**Rationale**: The evidence is unambiguous. FR-028 mandates the artifact. Section 9 defines schemas for every other mandatory artifact (`changes-manifest.json` has Section 9.7, `progress.json` has Section 9.8, etc.). The omission of `new-tests-manifest.json` is clearly an oversight, not a design choice. The proposed fields (file path, test type, related hypothesis IDs, status, scenario tags) are minimal and directly traceable to Phase 5 consumption needs.

**Proportionality**: HIGH. One missing schema definition is a small spec addition (~20 lines of YAML) that prevents an entire class of integration bugs. Effort-to-risk ratio is excellent.

**Evidence quality**: Strong. The gap is verifiable by inspecting Section 9 (no schema exists) and FR-028 (artifact is mandatory).

---

## PROPOSAL-007: Align Risk Surface schema with prompts and requirements

**Verdict**: MODIFY

**Rationale**: The evidence is mixed. The `overall_risk_score` discrepancy is real and verifiable: Section 9.3 lists it as `required`, but the proposal claims the Agent 0c prompt does not instruct computation. This is a genuine prompt-schema misalignment. However, the `secrets_exposure` claim is weaker -- the proposal says a "panel mentions" it but provides no specific section reference. Searching the expert panel review (Section 17) for the exact mention would be needed to validate this claim.

The proposed change bundles two distinct issues: (1) a verifiable schema-prompt gap, and (2) a possibly speculative schema expansion. This bundling inflates the scope.

**Proportionality assessment**:
- `overall_risk_score` alignment: PROPORTIONAL. Small prompt update + calculation method spec. Low cost, directly addresses a verified gap.
- `secrets_exposure` addition: DISPROPORTIONATE. Adding a new risk category changes the schema, requires Agent 0c to implement detection logic, and ripples into risk score weighting. The evidence that this is needed is a vague panel reference, not a functional requirement.

**Modification**: Split into two changes. Accept the `overall_risk_score` prompt-schema alignment. Reject `secrets_exposure` until evidence shows it is needed (specific FR, concrete use case, or panel citation with section number).

**Evidence quality**: Strong for `overall_risk_score`, weak for `secrets_exposure`.

---

## PROPOSAL-008: Strengthen `progress.json` for reproducibility and resume safety

**Verdict**: MODIFY

**Rationale**: The proposal identifies a real concern (stale resumes) but the proposed solution is over-engineered for v1.0. Five new required fields is a large schema change. The evidence assessment:

- **`spec_version`**: Defensive engineering for a schema that does not yet exist in production. YAGNI. Proportionality: LOW.
- **`run_id`**: Useful for observability but not for resume correctness. The resume logic (Section 12.3) does not reference run IDs. Proportionality: LOW.
- **`target_paths`**: Directly addresses the stale-resume scenario. Without this, resume cannot detect that the user changed targets. Proportionality: HIGH.
- **`git_head_or_snapshot`**: Addresses codebase-changed-between-runs. Proportionality: HIGH for git repos, but the spec does not mandate git as a target. Should be optional (not required) to support non-git codebases.
- **`phase_status_map`**: Duplicates information already in `completed_phases` + `current_phase`. The proposal does not explain what additional information the map would carry that the array does not. Proportionality: LOW.
- **`flags` as mandatory**: Already used by resume logic (Section 12.3, step 6). Making it mandatory is proportional. Proportionality: HIGH.

**Modification**: Accept `target_paths` (required) and `flags` (promote to required). Add `git_head_or_snapshot` as optional (not required). Reject `spec_version`, `run_id`, and `phase_status_map` as premature. Total schema change: 2 fields promoted/added vs. 5 proposed. This is proportional.

**Evidence quality**: The core concern (stale resume) is valid but the proposal does not provide evidence that all 5 fields are needed. No failure scenario is described that requires `run_id` or `spec_version`.

---

## PROPOSAL-009: Make domain IDs stable across retries/resume

**Verdict**: ACCEPT

**Rationale**: The evidence chain is strong and complete:
1. Hypothesis IDs use `H-{domain_index}-{sequence}` (Section 9.5, line 1195-1196)
2. Domain indices come from array position in `investigation-domains.json` (Section 9.4)
3. Phase 0 uses 3 parallel Haiku agents whose output order is non-deterministic
4. Resume can re-run Phase 0 (Section 12.4)
5. Therefore, domain indices can shift on re-run, invalidating all downstream references

This is a rigorous deductive argument. The proposed fix (deterministic hash or UUID) is a well-understood technique with minimal overhead. The alternative (live with index-based IDs) requires constraining resume to never re-run Phase 0, which contradicts the restart semantics table.

**Proportionality**: HIGH. The fix touches ID generation in one place (Phase 0 domain synthesis) and ID format validation in schemas. The risk (broken cross-phase references) is severe and affects every downstream phase.

**Evidence quality**: Strong. Every link in the chain is verifiable from the spec.

---

## PROPOSAL-010: Enforce exactly three fix tiers with uniqueness constraints

**Verdict**: MODIFY

**Rationale**: The evidence is partially strong. The discrepancy between FR-018 ("three fix tiers") and schema Section 9.6 (`minItems: 1, maxItems: 3`) is verifiable. The `--fix-tier` selection logic (FR-042) does assume tier existence. However, the proposal's solution (force exactly 3) is disproportionate to the risk.

**Evidence assessment**:
- Duplicate tier risk: Real but trivially prevented with a uniqueness constraint. Low-cost fix.
- Missing tier risk: Real when `--fix-tier robust` is used but only `minimal` and `moderate` exist. However, the proportional fix is a fallback in the orchestrator selection logic, not a mandate that agents produce filler content.

**Cost analysis of "exactly 3"**:
- Forces agents to generate 3 tiers even when only 1-2 are meaningful
- Adds ~500-1000 tokens per fix proposal for potentially low-quality filler tiers
- Multiplied across N hypotheses, this is significant token waste
- Creates a perverse incentive: agents pad proposals to meet schema requirements

**Modification**: Add uniqueness constraint on tier values (zero-cost, prevents a real bug). Keep `minItems: 1`. Add graceful fallback in `--fix-tier` selection: if requested tier is absent, select closest available tier and emit a warning. Update FR-018 to say "up to three fix tiers."

**Evidence quality**: Strong for the inconsistency, but the proposed solution exceeds what the evidence supports.

---

## PROPOSAL-021: Add multi-root path provenance to schemas

**Verdict**: ACCEPT

**Rationale**: FR-036 (MUST priority) accepts multiple target paths. Every path-bearing schema record uses relative paths without root disambiguation. The proposal identifies a genuine ambiguity that would manifest in any multi-root invocation.

**Proportionality assessment**: The proposed change (add `root_id`/`target_root` fields to path-bearing records) touches multiple schemas, which is non-trivial. However, the alternative is that multi-root support -- a MUST requirement -- is silently broken. The cost of NOT implementing (broken multi-root) exceeds the cost of implementing (schema additions).

**Counter-argument considered**: "Most users will use single-root, so defer multi-root correctness." This fails because FR-036 is MUST priority. A MUST requirement that silently produces incorrect results is worse than a missing feature.

**Evidence quality**: Strong. FR-036 existence + relative path inspection in schemas = verifiable gap.

---

## Summary Table

| Proposal | Verdict | Proportionality | Evidence Quality | Key Concern |
|----------|---------|-----------------|------------------|-------------|
| P-006 | ACCEPT | High | Strong | ~20 lines of schema; prevents integration class bugs |
| P-007 | MODIFY | Mixed | Strong/Weak | Split: accept risk_score fix, reject secrets_exposure |
| P-008 | MODIFY | Low (as proposed) | Partial | 5 fields is over-engineered; 2 fields suffice for v1.0 |
| P-009 | ACCEPT | High | Strong | Rigorous deductive chain; low-cost fix for severe risk |
| P-010 | MODIFY | Low (as proposed) | Mixed | Uniqueness yes; "exactly 3" creates perverse incentives |
| P-021 | ACCEPT | High | Strong | MUST FR is broken without it |
