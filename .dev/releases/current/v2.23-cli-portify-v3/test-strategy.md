---
validation_milestones: 8
interleave_ratio: '1:1'
---

# Test Strategy: CLI Portify v3 — Release Spec Synthesis & Panel Review

## 1. Validation Milestones Mapped to Roadmap Phases

### VM-1: Pre-Implementation Verification (Phase 1 entry)
**Trigger**: Before any code changes  
**Tests**:
- Confirm exactly 4 files to modify + 1 to create exist at expected paths
- Trace downstream consumers: verify `sc:roadmap` and `sc:tasklist` reference return contract fields
- Regression baseline: snapshot Phases 0-2 behavior (capture outputs for diffing later)
- Verify `make sync-dev` and `make verify-sync` run cleanly on current state

**Acceptance**: All 4 existing files readable; dependency trace documented; Phase 0-2 baseline captured.

### VM-2: Template Foundation (Gate A — Phase 1 exit)
**Trigger**: Template created at `src/superclaude/examples/release-spec-template.md`  
**Tests**:
- **Unit**: Template contains all 12 required sections (regex match section headers)
- **Unit**: Frontmatter schema includes quality score fields
- **Unit**: All placeholders use `{{SC_PLACEHOLDER:name}}` format (regex: `\{\{SC_PLACEHOLDER:\w+\}\}`)
- **Unit**: Zero sentinel collisions — search template prose for literal `{{SC_PLACEHOLDER` outside placeholder positions
- **Unit**: Cross-type reusability — instantiate template with mock data for each of 4 spec types (new feature, refactoring, portification, infrastructure) and verify no section is structurally invalid
- **Unit**: SC-003 self-validation regex works correctly (true positive + true negative cases)

**Acceptance**: Template at canonical path; 12 sections present; zero collisions; cross-type instantiation succeeds for all 4 types.

### VM-3: Spec Synthesis Complete (Gate B — Phase 2 exit)
**Trigger**: SKILL.md Phase 3 rewrite complete  
**Tests**:
- **Integration**: Template instantiation creates working copy at `{work_dir}/portify-release-spec.md` (FR-001)
- **Integration**: Content population maps all 10 sections from Phase 1+2 outputs (FR-002)
- **Unit**: SC-004 — count(step_mapping entries) == count(generated FRs); test with 3, 7, and 12 mappings
- **Integration**: Brainstorm pass produces findings in required schema `{gap_id, description, severity, affected_section, persona}` (FR-005)
- **Integration**: Zero-gap path — feed a "perfect" spec and verify "No gaps identified" summary + `gaps_identified: 0` (FR-006)
- **Integration**: Gap incorporation — actionable findings appear in relevant sections; unresolvable items in Section 11 (FR-007)
- **Unit**: SC-003 — zero remaining sentinels in output spec
- **Unit**: SC-005 — brainstorm section exists in output
- **Unit**: Phase timing field `phase_3_seconds` is a positive number (SC-013)
- **Regression**: Phases 0-2 outputs unchanged from VM-1 baseline
- **NFR**: Phase 3 completes in ≤10 minutes wall clock (NFR-001)

**Acceptance**: All Gate B criteria pass; old code generation instructions absent from SKILL.md; `refs/code-templates.md` not loaded by any phase.

### VM-4: Panel Review Complete (Phase 3 exit)
**Trigger**: SKILL.md Phase 4 rewrite complete  
**Tests**:
- **Integration**: Focus pass produces findings with required fields for both correctness and architecture dimensions (FR-008, SC-006)
- **Integration**: Focus incorporation — CRITICAL addressed (incorporated or justified), MAJOR in body, MINOR in Open Items (FR-009)
- **Unit**: Additive-only constraint — diff spec before/after incorporation; verify only appends/extends, no line deletions or rewrites (NFR-008)
- **Integration**: Critique pass produces all 4 quality scores as floats (FR-010, SC-007)
- **Unit**: Quality formula: `overall == mean(clarity, completeness, testability, consistency)` with test vectors (SC-010):
  - `{8.0, 8.0, 8.0, 8.0}` → `8.0`
  - `{6.0, 7.0, 8.0, 9.0}` → `7.5`
  - `{7.0, 7.0, 7.0, 7.0}` → `7.0`
- **Integration**: Convergence loop — inject persistent CRITICALs, verify loop runs exactly 3 iterations then escalates with `status: partial` (FR-012, SC-008, NFR-006)
- **Integration**: Convergence happy path — inject resolvable CRITICALs, verify loop converges in ≤2 iterations with `status: complete`
- **Unit**: Phase timing field `phase_4_seconds` is a positive number (SC-013)
- **Unit**: `panel-report.md` artifact exists after Phase 4 (FR-011)
- **NFR**: Phase 4 completes in ≤15 minutes wall clock (NFR-002)

**Acceptance**: All Phase 3 exit criteria from roadmap pass; convergence loop terminates correctly in both paths.

### VM-5: Contract & Command Surface (Gate C — Phase 4 exit)
**Trigger**: Contract schema and CLI flags updated  
**Tests**:
- **Unit**: Return contract contains all required fields: `contract_version`, `spec_file`, `panel_report`, `quality_scores` (5), `convergence_iterations`, `phase_timing`, `resume_substep`, `downstream_ready`, `warnings` (FR-015)
- **Unit**: Contract emitted on success path — all fields populated, scores > 0 (SC-009)
- **Unit**: Contract emitted on failure path — scores = `0.0` (not null), `downstream_ready = false` (NFR-009, SC-009)
- **Unit**: Contract emitted on dry-run path — Phase 0-2 fields only, no Phase 3/4 fields (FR-016, SC-002)
- **Unit**: `resume_substep` populated for resumable failures (NFR-007)
- **Boundary**: `overall = 7.0` → `downstream_ready: true` (SC-012)
- **Boundary**: `overall = 6.9` → `downstream_ready: false` (SC-012)
- **Boundary**: `overall = 0.0` (failure default) → `downstream_ready: false`
- **Unit**: `--skip-integration` flag rejected with error (SC-014)
- **Unit**: `--dry-run` flag accepted and produces correct behavior

**Acceptance**: All Gate C criteria pass; contract schema validated on all 3 paths (success, failure, dry-run).

### VM-6: Full Validation Suite (Phase 5 exit)
**Trigger**: All implementation phases complete  
**Tests**: Execute the full 5-category validation taxonomy from the roadmap:
- **Structural** (4 checks): SC-003, SC-004, SC-005, frontmatter/panel-report presence
- **Behavioral** (5 checks): SC-006, SC-007, brainstorm schema, zero-gap path, additive-only
- **Contract** (5 checks): SC-009, SC-010, SC-013, SC-014, resume substep
- **Boundary** (4 checks): SC-012, SC-008, mid-panel failure scores, iteration limit = 3
- **E2E** (5 checks): SC-001, SC-002, SC-011, convergence forced-CRITICAL, resume mid-Phase-4

**Acceptance**: All 14 success criteria (SC-001 through SC-014) pass with documented evidence.

### VM-7: Downstream Interoperability (Phase 5, E2E focus)
**Trigger**: Reviewed spec artifact produced  
**Tests**:
- **E2E**: Feed generated spec to `sc:roadmap` — verify it parses and produces a roadmap (SC-011)
- **E2E**: Feed generated spec to `sc:tasklist` — verify it parses without errors
- **Integration**: Verify `contract_version: "2.20"` is tolerated by downstream consumers
- **Regression**: Confirm downstream consumers still work with pre-v3 contract format (backward compatibility)

**Acceptance**: Downstream handoff succeeds for both `sc:roadmap` and `sc:tasklist`.

### VM-8: Sync & Release Readiness (Gate D — Phase 6 exit)
**Trigger**: `make sync-dev` completed  
**Tests**:
- **Unit**: `make verify-sync` passes (src/ and .claude/ match)
- **Unit**: `decisions.yaml` contains entries for this release
- **Unit**: `refs/code-templates.md` exists but is not referenced by any phase instruction
- **Regression**: Full E2E re-run after sync to confirm no sync-introduced breakage

**Acceptance**: All Gate D criteria pass; release is downstream-ready.

---

## 2. Test Categories

### Unit Tests (22 tests)
Tests that validate individual components in isolation without executing the full pipeline.

| ID | Test | FR/SC | Priority |
|----|------|-------|----------|
| U-01 | Template has 12 sections | FR-017 | HIGH |
| U-02 | Sentinel format regex correctness | NFR-004 | HIGH |
| U-03 | Zero sentinel collisions in template | NFR-004 | HIGH |
| U-04 | SC-003 self-validation regex (positive + negative) | SC-003 | HIGH |
| U-05 | Quality formula: 4 test vectors | SC-010 | HIGH |
| U-06 | Downstream-ready threshold boundary (7.0, 6.9, 0.0) | SC-012 | HIGH |
| U-07 | Contract schema: all fields present on success | FR-015, SC-009 | HIGH |
| U-08 | Contract schema: failure defaults (0.0, not null) | NFR-009 | HIGH |
| U-09 | Contract schema: dry-run fields only | FR-016 | MEDIUM |
| U-10 | `--skip-integration` rejected | SC-014 | MEDIUM |
| U-11 | `--dry-run` accepted | FR-016 | MEDIUM |
| U-12 | Brainstorm finding schema validation | FR-005 | MEDIUM |
| U-13 | Step-mapping → FR count match (3, 7, 12 inputs) | SC-004 | MEDIUM |
| U-14 | Additive-only diff check (no deletions) | NFR-008 | HIGH |
| U-15 | Phase timing fields are positive numbers | SC-013 | LOW |
| U-16 | `resume_substep` populated on resumable failures | NFR-007 | MEDIUM |
| U-17 | Panel report artifact exists after Phase 4 | FR-011 | MEDIUM |
| U-18 | Cross-type template instantiation (4 types) | FR-017 | MEDIUM |
| U-19 | `make verify-sync` passes | Constraint 10 | LOW |
| U-20 | `decisions.yaml` updated | Phase 6 | LOW |
| U-21 | `refs/code-templates.md` not loaded by any phase | FR-013 | MEDIUM |
| U-22 | Convergence iteration counter increments correctly | FR-012 | HIGH |

### Integration Tests (10 tests)
Tests that validate multi-step interactions within or across phases.

| ID | Test | FR/SC | Priority |
|----|------|-------|----------|
| I-01 | Template instantiation → working copy at correct path | FR-001 | HIGH |
| I-02 | Content population fills all 10 mapped sections | FR-002 | HIGH |
| I-03 | Brainstorm pass with multi-persona produces structured findings | FR-004 | HIGH |
| I-04 | Zero-gap brainstorm path: summary + contract field | FR-006 | MEDIUM |
| I-05 | Gap incorporation: actionable → sections, unresolvable → Section 11 | FR-007 | MEDIUM |
| I-06 | Focus pass: findings for both correctness and architecture | FR-008, SC-006 | HIGH |
| I-07 | Focus incorporation: CRITICAL/MAJOR/MINOR routing | FR-009 | HIGH |
| I-08 | Critique pass: 4 quality scores as floats | FR-010, SC-007 | HIGH |
| I-09 | Convergence loop: resolvable CRITICALs → converges in ≤2 | FR-012 | HIGH |
| I-10 | Convergence loop: persistent CRITICALs → 3 iterations → escalate | FR-012, SC-008 | HIGH |

### End-to-End Tests (5 tests)
Full pipeline runs validating complete workflows.

| ID | Test | SC | Priority |
|----|------|-----|----------|
| E-01 | Full portify run → reviewed spec + panel report + contract | SC-001 | CRITICAL |
| E-02 | Dry run → stops after Phase 2, no Phase 3/4 artifacts | SC-002 | HIGH |
| E-03 | Downstream handoff: spec → `sc:roadmap` succeeds | SC-011 | HIGH |
| E-04 | Resume: interrupt mid-Phase 4, resume from `resume_substep` | NFR-007 | MEDIUM |
| E-05 | Full run after `make sync-dev` — no sync-introduced breakage | Constraint 10 | MEDIUM |

### Acceptance Tests (4 tests)
User-facing validation of high-level requirements.

| ID | Test | Validates | Priority |
|----|------|-----------|----------|
| A-01 | Generated spec is meaningful and non-generic for a real workflow | R-004 mitigation | HIGH |
| A-02 | Quality scores discriminate between good and poor specs | OQ-5 calibration | MEDIUM |
| A-03 | Escalation path is usable when convergence exhausts 3 iterations | OQ-7 | MEDIUM |
| A-04 | Old code generation behavior is fully removed (no residual instructions) | FR-013, FR-014 | HIGH |

---

## 3. Test-Implementation Interleaving Strategy

**Ratio**: 1:1 — every implementation step has a corresponding validation step executed immediately after, not deferred to Phase 5.

### Interleaving Schedule

```
Phase 1 Implementation: Template creation
  ├─ TEST: VM-2 unit tests (U-01 through U-04, U-18)
  ├─ TEST: VM-1 pre-verification checks
  └─ GATE A verification

Phase 2 Implementation: Phase 3 rewrite (spec synthesis)
  ├─ TEST: I-01 (template instantiation) — after step 3a
  ├─ TEST: I-02, U-13 (content population) — after step 3b
  ├─ TEST: I-03, I-04, U-12 (brainstorm) — after step 3c
  ├─ TEST: I-05 (gap incorporation) — after step 3d
  ├─ TEST: U-21 (code-templates not loaded) — after removal step
  ├─ TEST: U-15 (phase timing) — after instrumentation
  └─ GATE B verification

Phase 3 Implementation: Phase 4 rewrite (panel review)
  ├─ TEST: I-06 (focus pass) — after step 4a
  ├─ TEST: I-07, U-14 (focus incorporation + additive check) — after step 4b
  ├─ TEST: I-08, U-05 (critique pass + formula) — after step 4c
  ├─ TEST: U-17 (panel report exists) — after step 4d
  ├─ TEST: I-09, I-10, U-22 (convergence loop) — after loop impl
  ├─ TEST: U-06 (boundary threshold) — after downstream_ready impl
  └─ Exit criteria verification

Phase 4 Implementation: Contract & command surface
  ├─ TEST: U-07, U-08, U-09 (contract schemas) — after contract update
  ├─ TEST: U-10, U-11 (flag behavior) — after command update
  ├─ TEST: U-16 (resume substep) — after resume impl
  ├─ TEST: U-06 boundary re-run — after early failure validation
  └─ GATE C verification

Phase 5: Dedicated validation
  ├─ Full 5-category taxonomy execution (VM-6)
  ├─ E-01 through E-05 (all E2E tests)
  ├─ A-01 through A-04 (all acceptance tests)
  └─ Evidence collection for all SC-001 through SC-014

Phase 6: Sync validation
  ├─ TEST: U-19, U-20 (sync + decisions.yaml)
  ├─ TEST: E-05 (post-sync regression)
  └─ GATE D verification
```

**Rationale for 1:1**: The sequential dependency chain means a defect discovered in Phase 5 could require unwinding multiple phases. Testing after each sub-step catches issues at minimum cost. The 1:1 ratio is feasible because most tests are fast self-validation checks (regex, schema, count comparisons).

---

## 4. Risk-Based Test Prioritization

### Priority Tiers

**Tier 1 — CRITICAL (test first, block on failure)**
These cover the highest-risk areas identified in the roadmap risk assessment.

| Risk | Tests | Rationale |
|------|-------|-----------|
| R-001: Behavioral pattern drift | I-03, I-06, I-08, A-04 | Embedded patterns are the core behavioral change; schema tests catch drift early |
| R-002: Convergence non-convergence | I-09, I-10, U-22 | State machine correctness is the highest-complexity component (0.7 state management score) |
| R-008: Contract inconsistency on failure | U-07, U-08, SC-009 | Failure contracts are first-class; inconsistency breaks downstream consumers |
| R-005: Additive incorporation contradictions | U-14, I-07 | Additive-only is a mechanical constraint; violation would trigger convergence spirals |

**Tier 2 — HIGH (test during implementation, review at gates)**

| Risk | Tests | Rationale |
|------|-------|-----------|
| R-007: Downstream incompatibility | E-03, VM-7 | Medium probability, medium impact; caught by E2E but not blocking until Phase 5 |
| R-004: Generic spec output | A-01, I-02 | Low probability but high impact; content population test catches early |
| R-003: Token/time overconsumption | NFR-001, NFR-002 timing checks | Medium probability; timing instrumentation provides data |

**Tier 3 — MEDIUM (test at Phase 5, accept risk)**

| Risk | Tests | Rationale |
|------|-------|-----------|
| R-006: Orphaned reference artifacts | U-21 | Low severity; grep check is sufficient |
| R-009: Silent behavioral contract changes | A-04, regression baseline | Documentation-based mitigation; no mechanical enforcement possible now |
| OQ-5: Quality score calibration | A-02 | Post-implementation empirical validation; cannot test until real data exists |

### Test Execution Order (within each phase)

1. Schema/format tests (catch structural issues immediately)
2. Behavioral tests (verify logic correctness)
3. Boundary tests (catch off-by-one and threshold errors)
4. Integration tests (verify cross-step interactions)
5. NFR tests (timing, performance — run last as they're least likely to block)

---

## 5. Acceptance Criteria per Milestone

| Milestone | Must Pass | Evidence Required | Blocker If Failed |
|-----------|-----------|-------------------|-------------------|
| **VM-1** | Pre-verification checklist complete | Dependency trace document, Phase 0-2 baseline snapshot | Cannot start Phase 1 |
| **VM-2 (Gate A)** | U-01–U-04, U-18 | Template file, collision scan log, cross-type instantiation output | Cannot start Phase 2 |
| **VM-3 (Gate B)** | I-01–I-05, U-12–U-13, U-15, U-21, SC-003–SC-005 | Generated spec sample, brainstorm output sample, timing log | Cannot start Phase 3 |
| **VM-4** | I-06–I-10, U-05–U-06, U-14, U-17, U-22, SC-006–SC-008 | Panel report sample, convergence loop trace, additive diff | Cannot start Phase 4 |
| **VM-5 (Gate C)** | U-07–U-11, U-16, SC-009–SC-010, SC-012, SC-014 | Contract snapshots (success/failure/dry-run), boundary test results | Cannot start Phase 5 |
| **VM-6** | All SC-001 through SC-014 | Full test suite output, evidence artifacts per roadmap spec | Cannot start Phase 6 |
| **VM-7** | E-03 + downstream consumer tests | `sc:roadmap` output from generated spec, `sc:tasklist` parse log | Blocks release |
| **VM-8 (Gate D)** | U-19–U-20, E-05 | `make verify-sync` output, post-sync E2E run | Blocks release |

---

## 6. Quality Gates Between Phases

### Gate A (Phase 1 → Phase 2)
| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Template exists at canonical path | `test -f src/superclaude/examples/release-spec-template.md` | File exists |
| 12 sections present | Regex count of `## ` headers | Count = 12 |
| Zero sentinel collisions | Grep for `{{SC_PLACEHOLDER` in non-placeholder context | 0 matches |
| Cross-type reusability | Instantiate with 4 mock datasets | All 4 succeed |
| Dependency trace documented | Trace document exists | Exists with ≥2 consumers listed |

### Gate B (Phase 2 → Phase 3)
| Check | Method | Pass Criteria |
|-------|--------|---------------|
| step_mapping → FR count | Count comparison | Exact match |
| Brainstorm section present | Section header search | `## Brainstorm Gap Analysis` exists |
| Zero remaining sentinels | Regex `\{\{SC_PLACEHOLDER:.*?\}\}` | 0 matches |
| Old code gen removed | Grep SKILL.md for code generation keywords | 0 matches for removed instructions |
| Phase 3 timing ≤10 min | `phase_3_seconds` field | ≤ 600 |
| Phase 0-2 regression | Diff against VM-1 baseline | No changes |

### Gate C (Phase 4 → Phase 5)
| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Contract emitted: success path | Schema validation | All fields present, scores > 0 |
| Contract emitted: failure path | Schema validation | All fields present, scores = 0.0 |
| Contract emitted: dry-run path | Schema validation | Phase 0-2 fields only |
| `--skip-integration` rejected | CLI invocation | Non-zero exit / error message |
| Quality formula correct | Arithmetic check | `overall == mean(4 scores)` for 3 test vectors |
| Boundary: 7.0 → ready | Threshold check | `downstream_ready: true` |
| Boundary: 6.9 → not ready | Threshold check | `downstream_ready: false` |

### Gate D (Phase 6 → Release)
| Check | Method | Pass Criteria |
|-------|--------|---------------|
| `make verify-sync` | CLI | Exit code 0 |
| `decisions.yaml` updated | Content check | Contains v2.23 entries |
| `refs/code-templates.md` inactive | Grep all phase instructions | 0 references |
| Post-sync E2E | Full pipeline re-run | SC-001 passes |
| Downstream handoff | Feed spec to `sc:roadmap` | Produces valid roadmap |

---

## 7. Risk-Specific Test Scenarios

### Convergence Loop Edge Cases (R-002, highest complexity)
1. **Happy path**: 0 CRITICALs on first pass → no loop iterations, `convergence_iterations: 1`
2. **Single retry**: 1 CRITICAL on first pass, resolved on second → `convergence_iterations: 2`
3. **Max iterations**: Persistent CRITICAL through 3 passes → `status: partial`, `convergence_iterations: 3`, user escalation triggered
4. **Boundary**: Exactly at iteration 3, CRITICAL resolved → `status: complete`, `convergence_iterations: 3`
5. **Mid-loop failure**: Error during iteration 2 incorporation → `resume_substep` populated, scores = 0.0

### Contract Failure Path Coverage (R-008)
1. **Phase 3 failure** (e.g., template load error): Contract with `spec_file: null`, `quality_scores: {all 0.0}`, `downstream_ready: false`
2. **Phase 4a failure** (focus pass error): Contract with `spec_file` populated but `panel_report: null`, scores = 0.0
3. **Phase 4c failure** (critique pass error): Contract with partial findings but `quality_scores: {all 0.0}`
4. **Timeout failure**: Phase exceeds NFR time cap → Contract with timing populated, scores = 0.0

### Behavioral Pattern Fidelity (R-001)
1. **Brainstorm output schema**: Verify every finding has all 5 required fields
2. **Focus pass output schema**: Verify every finding has all 6 required fields
3. **Critique output schema**: Verify all 4 quality dimensions present as floats in range [0.0, 10.0]
4. **Multi-persona verification**: Brainstorm findings attributed to at least 2 distinct personas

---

## 8. Evidence Collection Requirements

Each milestone must produce the following artifacts for audit trail:

| Milestone | Required Evidence |
|-----------|-------------------|
| VM-2 | Template file content, collision scan log |
| VM-3 | Generated spec sample, brainstorm output JSON, timing measurement |
| VM-4 | Panel report sample, convergence loop trace (iteration count + CRITICAL count per iteration), additive-only diff |
| VM-5 | Contract JSON snapshots: {success, failure, dry-run}, boundary test results |
| VM-6 | SC-001 through SC-014 pass/fail report with evidence links |
| VM-7 | Downstream `sc:roadmap` output from generated spec |
| VM-8 | `make verify-sync` output, post-sync E2E log |
