# Group A: Schema & Data Integrity -- Adversarial Verdicts

**Protocol**: `/sc:adversarial` Mode B (independent assessments)
**Agents**: 3 (architect, analyzer, QA)
**Depth**: standard (2 debate rounds)
**Convergence target**: 0.80
**Focus dimensions**: necessity, proportionality, testability
**Date**: 2026-02-26

---

## Debate Summary

### Round 1: Initial Positions

All three agents independently assessed the 6 proposals. Initial agreement was high on P-006, P-009, and P-021 (unanimous ACCEPT). Divergence appeared on P-007, P-008, and P-010, where all three agents reached MODIFY but with slightly different scoping of what to keep versus defer.

### Round 2: Convergence Refinement

Agents debated the MODIFY boundaries for P-007, P-008, and P-010. Key resolution points:

- **P-007**: All agents agreed that `secrets_exposure` lacks sufficient evidence (no FR, weak panel reference, oracle testing problem). Converged on accepting only the `overall_risk_score` alignment.
- **P-008**: Architect pushed for `git_head_or_snapshot` as optional rather than required. Analyzer concurred (non-git codebases exist). QA confirmed the test scenario works with an optional field. Converged on: `target_paths` required, `git_head_or_snapshot` optional, `flags` promoted to required.
- **P-010**: All agents agreed on uniqueness constraint. Architect and QA both independently identified the "filler tier" problem. Converged on: uniqueness + orchestrator fallback, reject "exactly 3."

**Final convergence score**: 0.93 (exceeds 0.80 threshold)

---

## Per-Proposal Verdicts

### PROPOSAL-006: Add missing schema for `new-tests-manifest.json`

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.95 | Implementation blocker: no contract between Agent 4b and 5b |
| Proportionality | Analyzer | 0.95 | ~20 lines YAML prevents integration class bugs |
| Testability | QA | 0.95 | Schema validation + cross-reference integrity |
| **Composite** | | **0.95** | |

**VERDICT: ACCEPT**

**Rationale**: Unanimous across all three perspectives. The gap is unambiguous (every other mandatory artifact has a schema; this one does not). The fix is small, the risk of omission is high, and the result is fully testable. No debate required.

**Implementation guidance**: Define schema in Section 9 (new Section 9.7b or renumber). Required fields: `file_path` (string), `test_type` (enum: unit/integration/e2e), `related_hypothesis_ids` (array of hypothesis ID strings), `status` (enum: new/modified). Optional: `scenario_tags` (array of strings).

---

### PROPOSAL-007: Align Risk Surface schema with prompts and requirements

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.75 | risk_score gap is blocking; secrets_exposure is speculative |
| Proportionality | Analyzer | 0.70 | Mixed: one small fix + one disproportionate expansion |
| Testability | QA | 0.65 | risk_score testable; secrets detection has oracle problem |
| **Composite** | | **0.70** | |

**VERDICT: MODIFY**

**Accept**:
- Align Agent 0c prompt to require `overall_risk_score` computation (already `required` in schema Section 9.3)
- Specify calculation method: weighted average of category `risk_score` values
- Update FR-004 language to explicitly mention `overall_risk_score` as a required output

**Reject**:
- `secrets_exposure` category addition. Three independent deficiencies identified:
  1. No functional requirement drives it (architect: no FR)
  2. Evidence is a vague panel reference without section citation (analyzer: weak evidence)
  3. Correct detection requires oracle test fixtures that do not exist (QA: untestable)

**Deferred**: `secrets_exposure` may be added in a future iteration when backed by a formal FR and accompanied by a test fixture corpus.

---

### PROPOSAL-008: Strengthen `progress.json` for reproducibility and resume safety

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.60 | Resume works without most fields; edge-case hardening |
| Proportionality | Analyzer | 0.55 | 5 fields is over-engineered; 2-3 suffice |
| Testability | QA | 0.65 | 3 fields enable high-value test scenarios; others are noise |
| **Composite** | | **0.60** | |

**VERDICT: MODIFY**

**Accept** (3 fields):

| Field | Disposition | Rationale |
|-------|-------------|-----------|
| `target_paths` | Add as **required** | Enables stale-target detection on resume. All 3 agents agreed. |
| `flags` | Promote to **required** | Resume logic (Section 12.3 step 6) already depends on it. Formalizes existing dependency. |
| `git_head_or_snapshot` | Add as **optional** | Enables stale-codebase detection. Optional because spec does not mandate git as target. |

**Reject** (3 fields):

| Field | Disposition | Rationale |
|-------|-------------|-----------|
| `spec_version` | Defer to post-v1.0 | No version exists yet. YAGNI. (architect + analyzer) |
| `run_id` | Defer to post-v1.0 | Observability, not correctness. Resume logic does not use it. (all 3 agents) |
| `phase_status_map` | Reject | Duplicates `completed_phases` + `current_phase`. No unique information identified. (architect + analyzer) |

**Net schema change**: +2 required fields, +1 optional field (vs. +5 required proposed). This is proportional.

---

### PROPOSAL-009: Make domain IDs stable across retries/resume

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.90 | Latent bug: index drift breaks all cross-phase references |
| Proportionality | Analyzer | 0.90 | Low-cost fix for severe risk; rigorous evidence chain |
| Testability | QA | 0.95 | Determinism invariant is precise and automatable |
| **Composite** | | **0.92** | |

**VERDICT: ACCEPT**

**Rationale**: Strongest consensus proposal. All three agents independently identified the same failure chain: parallel Phase 0 agents produce non-deterministic order, index-based IDs inherit that non-determinism, resume re-runs Phase 0, downstream references break. QA additionally provided a concrete negative test that proves the bug exists under the current design.

**Implementation guidance**:
- Generate `domain_id` as deterministic hash of `(domain_name, sorted(files_in_scope))`.
- Hypothesis IDs become `H-{domain_id_short}-{sequence}` where `domain_id_short` is first 8 characters of hash.
- Retain `display_index` as a separate field for human-readable report ordering.
- Update schemas: Section 9.4 (add `domain_id`), Section 9.5 (update ID pattern), Section 9.6 (hypothesis reference format), Section 9.7 (hypothesis_id format).

---

### PROPOSAL-010: Enforce exactly three fix tiers with uniqueness constraints

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.70 | Uniqueness needed; "exactly 3" is over-rigid |
| Proportionality | Analyzer | 0.60 | "Exactly 3" creates token waste and perverse incentives |
| Testability | QA | 0.70 | Uniqueness trivially testable; "exactly 3" quality unverifiable |
| **Composite** | | **0.67** | |

**VERDICT: MODIFY**

**Accept**:
- Add uniqueness constraint on `tier` values within `fix_options` array. Schema addition: `uniqueItems: true` (by tier field). Prevents duplicate `minimal`/`minimal` entries, which is a clear data integrity bug.

**Reject**:
- Change `minItems` from 1 to 3. Three independent reasons:
  1. Forces filler content when fewer tiers are meaningful (architect: too rigid)
  2. ~500-1000 tokens per proposal wasted on padding, multiplied by N hypotheses (analyzer: disproportionate)
  3. Cannot distinguish genuine tiers from filler in automated tests (QA: creates false positives)

**Add** (not in original proposal):
- Orchestrator `--fix-tier` fallback logic: if requested tier is absent, select next-lower available tier and emit warning to final report. This addresses the root concern (tier selection failure) without constraining the generation side.
- Update FR-018 text from "containing three fix tiers" to "containing up to three fix tiers (minimal, moderate, robust)" to resolve the FR-schema inconsistency.

---

### PROPOSAL-021: Add multi-root path provenance to schemas

| Dimension | Agent | Score | Notes |
|-----------|-------|-------|-------|
| Necessity | Architect | 0.85 | Multi-root is a MUST FR; paths ambiguous without provenance |
| Proportionality | Analyzer | 0.85 | Cost of NOT implementing exceeds cost of schema additions |
| Testability | QA | 0.90 | Path resolution is deterministic; round-trip tests are clean |
| **Composite** | | **0.87** | |

**VERDICT: ACCEPT**

**Rationale**: FR-036 (MUST priority) explicitly supports multiple target paths. Without path provenance, a core feature is silently broken for any codebase with overlapping relative paths (common in monorepos). All three agents independently concluded that the cost of the schema additions is justified by the severity of the gap.

**Implementation guidance**:
- Add `target_root` (string) to all path-bearing schema records: structural-inventory items (9.1), dependency-graph import chains (9.2), hypothesis evidence entries (9.5), fix change records (9.6), changes-manifest entries (9.7), new-tests-manifest entries (new).
- Add `target_roots` array to top-level metadata in `investigation-domains.json` (9.4) mapping root IDs to absolute paths.
- For single-root invocations, `target_root` defaults to the sole path. No schema overhead for the common case beyond the field presence.
- Normalize: all relative paths are relative to their `target_root`, never to CWD.

---

## Consolidated Scoring Matrix

| Proposal | Verdict | Necessity | Proportionality | Testability | Composite | Convergence |
|----------|---------|-----------|-----------------|-------------|-----------|-------------|
| P-006 | **ACCEPT** | 0.95 | 0.95 | 0.95 | **0.95** | 1.00 (unanimous) |
| P-007 | **MODIFY** | 0.75 | 0.70 | 0.65 | **0.70** | 0.93 |
| P-008 | **MODIFY** | 0.60 | 0.55 | 0.65 | **0.60** | 0.90 |
| P-009 | **ACCEPT** | 0.90 | 0.90 | 0.95 | **0.92** | 1.00 (unanimous) |
| P-010 | **MODIFY** | 0.70 | 0.60 | 0.70 | **0.67** | 0.93 |
| P-021 | **ACCEPT** | 0.85 | 0.85 | 0.90 | **0.87** | 1.00 (unanimous) |

**Overall convergence**: 0.93 (exceeds 0.80 threshold)

---

## Implementation Priority Order

Based on composite scores and dependency analysis:

| Priority | Proposal | Verdict | Composite | Dependency |
|----------|----------|---------|-----------|------------|
| 1 | P-006 | ACCEPT | 0.95 | Blocks Phase 4b/5b implementation |
| 2 | P-009 | ACCEPT | 0.92 | Blocks resume correctness across all phases |
| 3 | P-021 | ACCEPT | 0.87 | Blocks multi-root FR-036 correctness |
| 4 | P-007 | MODIFY | 0.70 | Blocks Phase 0 prompt writing (risk_score only) |
| 5 | P-010 | MODIFY | 0.67 | Blocks Phase 3 schema finalization |
| 6 | P-008 | MODIFY | 0.60 | Hardening; resume works without for single-session |

---

## Deferred Items (Future Iterations)

| Item | Source Proposal | Reason for Deferral | Trigger to Reconsider |
|------|----------------|---------------------|----------------------|
| `secrets_exposure` risk category | P-007 | No FR, weak evidence, oracle testing gap | Formal FR + test fixture corpus |
| `spec_version` field | P-008 | YAGNI for v1.0 | Schema breaking change in v2.0 |
| `run_id` field | P-008 | Observability, not correctness | Observability/debugging sprint |
| `phase_status_map` field | P-008 | Duplicates existing fields | New per-phase metadata requirements |
| "Exactly 3 tiers" constraint | P-010 | Token waste, filler incentives, untestable quality | Evidence that 1-2 tier proposals cause downstream failures |
