# Agent 1: Architect Assessment -- Group A Schema Integrity

**Perspective**: Structural necessity for implementation
**Core question**: "Would an implementer get stuck without this change?"
**Date**: 2026-02-26

---

## PROPOSAL-006: Add missing schema for `new-tests-manifest.json`

**Verdict**: ACCEPT

**Rationale**: This is a clear implementation blocker. FR-028 mandates that Agent 4b produces `new-tests-manifest.json`, and Phase 5 (Agent 5b) must consume it to correlate test results with fix proposals. Without a schema, the implementer of Agent 4b has no contract to emit against, and the implementer of Agent 5b has no contract to parse against. Two independent agents with no shared schema definition is a guaranteed interop failure.

**Necessity score**: 0.95 -- An implementer would have to invent a schema ad-hoc, creating a fragile implicit contract that would break on first cross-agent integration.

**Risk of not implementing**: High. Two agents (4b, 5b) independently guess at field names and structure. Integration fails at runtime.

---

## PROPOSAL-007: Align Risk Surface schema with prompts and requirements

**Verdict**: MODIFY

**Rationale**: The `overall_risk_score` alignment is necessary -- it is already listed as `required` in the schema (Section 9.3, line 986 of the spec) but the Agent 0c prompt does not instruct the agent to compute it. An implementer writing the Agent 0c prompt would notice this gap and be forced to improvise. However, the `secrets_exposure` addition is less clearly justified. The proposal references a "panel mention" but does not cite a specific FR or schema requirement. Adding a new risk category should be driven by a functional requirement, not a side comment in a review panel.

**Modification**: Accept the `overall_risk_score` alignment (prompt-to-schema sync) and the calculation method specification. Defer `secrets_exposure` until a formal FR is written that requires it. Without an FR, adding it is speculative schema expansion.

**Necessity score**: 0.75 -- The `overall_risk_score` gap is a real implementer blocker; `secrets_exposure` is not.

**Risk of not implementing**: Medium. The risk score drives model-tier selection (FR-010), so the calculation gap is a real dependency chain issue.

---

## PROPOSAL-008: Strengthen `progress.json` for reproducibility and resume safety

**Verdict**: MODIFY

**Rationale**: The resume logic (Section 12.3) already works with the current schema for the basic case: it reads `completed_phases`, determines next phase, and validates artifact existence. An implementer CAN build a working resume system without these additions. However, the additions address a real edge case: resuming against a different codebase state (e.g., someone does `git pull` between runs). The question is whether this is a Phase 1 implementation concern or a hardening concern.

- `run_id`: Useful for log correlation but not structurally required for resume.
- `spec_version`: Defensive. Useful if the schema evolves but YAGNI for v1.0.
- `target_paths`: Genuinely useful. Without this, resume cannot validate it is resuming against the same target.
- `git_head_or_snapshot`: Genuinely useful for the same reason.
- `phase_status_map`: The current `completed_phases` array already covers this. A map adds expressiveness (per-phase metadata) but is not blocking.
- `flags` as mandatory: Already in the schema as optional. Making it mandatory is reasonable since resume logic depends on it (Section 12.3, step 6).

**Modification**: Accept `target_paths`, `git_head_or_snapshot`, and making `flags` mandatory. Defer `run_id`, `spec_version`, and `phase_status_map` to post-v1.0 hardening. Keep the schema minimal for first implementation.

**Necessity score**: 0.60 -- An implementer can build resume without these fields; they prevent edge-case corruption but are not structural blockers.

---

## PROPOSAL-009: Make domain IDs stable across retries/resume

**Verdict**: ACCEPT

**Rationale**: This is a genuine structural defect. The current hypothesis ID format `H-{domain_index}-{sequence}` uses positional indexing, but domain discovery (Phase 0) is non-deterministic -- three parallel Haiku agents may produce domains in different order on retry. If a run resumes at Phase 3 but Phase 0 was re-run (per Section 12.4), all hypothesis IDs from Phase 1 become invalid because domain indices shifted. Every downstream schema that references hypothesis IDs (fix proposals, changes manifest, test manifest, final report) would contain stale references.

An implementer building the resume system would hit this bug on the first retry that re-runs Phase 0. The fix is straightforward: use a deterministic hash of domain name + files_in_scope as the domain_id, and derive hypothesis IDs from that.

**Necessity score**: 0.90 -- This is a latent bug that manifests on any resume that re-executes Phase 0. The implementer would discover it through testing but would then need to refactor multiple schemas.

**Risk of not implementing**: High. Cross-phase reference integrity is broken on resume.

---

## PROPOSAL-010: Enforce exactly three fix tiers with uniqueness constraints

**Verdict**: MODIFY

**Rationale**: FR-018 says "containing three fix tiers" but the schema says `minItems: 1, maxItems: 3`. This is a real inconsistency. The `--fix-tier` flag (FR-042) assumes the selected tier exists in every proposal. If a proposal only emits `minimal` and `moderate`, selecting `--fix-tier robust` produces a lookup failure.

However, forcing exactly 3 tiers may be overly rigid. Some hypotheses legitimately have only one viable fix approach (e.g., a missing null check has only one reasonable fix). Forcing the agent to invent artificial tiers wastes tokens and produces low-quality filler.

**Modification**: Require that all emitted tiers are unique (no duplicates -- this is clearly a bug to allow). Change the `--fix-tier` logic to fall back gracefully: if the requested tier does not exist, select the next-lower tier with a warning. Keep `minItems: 1, maxItems: 3`. Update FR-018 language to say "up to three fix tiers" to match the schema.

**Necessity score**: 0.70 -- The uniqueness constraint is necessary (duplicate tiers are nonsensical). The "exactly 3" constraint is over-specified.

---

## PROPOSAL-021: Add multi-root path provenance to schemas

**Verdict**: ACCEPT

**Rationale**: FR-036 explicitly allows multiple target paths as positional arguments. Every path-bearing record in every schema uses relative paths with no indication of which root they are relative to. An implementer building the Phase 4 implementation agent would have no way to resolve `src/main.py` when the user passed two target roots that both contain `src/main.py`.

This is not a theoretical concern -- monorepo usage is the primary use case for multi-path invocation, and monorepos frequently have overlapping relative paths.

**Necessity score**: 0.85 -- Multi-root is a first-class feature (FR-036 is MUST priority). Without path provenance, the feature is broken for any non-trivial multi-root case.

**Risk of not implementing**: High for multi-root invocations. Low if single-root is the only tested path.

---

## Summary Table

| Proposal | Verdict | Necessity | Key Argument |
|----------|---------|-----------|--------------|
| P-006 | ACCEPT | 0.95 | No contract between Agent 4b and Agent 5b without schema |
| P-007 | MODIFY | 0.75 | Accept risk_score alignment, defer secrets_exposure (no FR) |
| P-008 | MODIFY | 0.60 | Accept target_paths + git_head + flags-mandatory; defer rest |
| P-009 | ACCEPT | 0.90 | Index-based IDs break on resume; deterministic hash is required |
| P-010 | MODIFY | 0.70 | Accept uniqueness, reject "exactly 3" (too rigid) |
| P-021 | ACCEPT | 0.85 | Multi-root is a MUST FR; paths are ambiguous without provenance |
