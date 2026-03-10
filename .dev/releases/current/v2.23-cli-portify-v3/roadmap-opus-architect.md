

---
spec_source: "spec-cli-portify-workflow-evolution.md"
complexity_score: 0.65
primary_persona: architect
phases: 6
estimated_duration_days: 8-12
risk_level: moderate
---

# Roadmap: CLI Portify v3 — Release Spec Synthesis & Panel Review

## 1. Executive Summary

This roadmap covers the evolution of `sc:cli-portify` from a code-generation pipeline into a **release specification synthesis and review pipeline**. The core change replaces Phases 3-4 (code generation + integration) with Phase 3 (spec synthesis with embedded brainstorm) and Phase 4 (spec-panel review with convergence loop).

**Scope**: 26 requirements (17 functional, 9 non-functional) across 5 domains, modifying ~4 files with 1 new template artifact. Phases 0-2 remain untouched.

**Key architectural decision**: Behavioral patterns from `sc:brainstorm` and `sc:spec-panel` are embedded inline rather than invoked as commands, keeping the pipeline non-interactive and automatable.

## 2. Phased Implementation Plan

### Phase 1: Template Foundation
**Duration**: 1-2 days | **Risk**: Low

**Objective**: Create the reusable release spec template that Phase 3 instantiates.

1. Create `src/superclaude/examples/release-spec-template.md` (FR-017)
   - Frontmatter schema with quality score fields
   - All 12 template sections: problem statement, solution overview, FRs, architecture, interface contracts, NFRs, risk assessment, test plan, migration, downstream inputs, open items, brainstorm gap analysis
   - Use `{{SC_PLACEHOLDER:name}}` sentinel format (Constraint 5)
   - Validate template works for: new feature, refactoring, portification, infrastructure specs
2. Validate sentinel format doesn't collide with template content (Open Question 3)
3. Write self-validation check: regex scan for remaining sentinels (SC-003)

**Milestone M1**: Template exists, passes sentinel collision check, covers all required spec types.

**Exit Criteria**:
- Template file at canonical location (Constraint 4)
- Zero sentinel collisions with template prose
- Template sections map 1:1 to the section-to-source mapping table in the spec

---

### Phase 2: Phase 3 Rewrite — Spec Synthesis
**Duration**: 2-3 days | **Risk**: Medium

**Objective**: Replace code generation with spec synthesis including embedded brainstorm.

1. Rewrite Phase 3 in `SKILL.md` (FR-013)
   - **3a** Template instantiation: load template, create working copy at `{work_dir}/portify-release-spec.md` (FR-001)
   - **3b** Content population: map Phase 1 + Phase 2 outputs to template sections per the 10-section mapping table (FR-002, FR-003)
   - **3c** Embedded brainstorm pass (FR-004, FR-005, FR-006):
     - Multi-persona (architect + analyzer + backend) non-interactive analysis
     - Structured output format: `{gap_id, description, severity, affected_section, persona}`
     - Zero-gap handling with explicit "No gaps identified" summary
   - **3d** Gap incorporation: actionable findings into spec body, unresolvable to Section 11 (FR-007)
2. Remove all code generation instructions from SKILL.md (FR-013)
3. Preserve `refs/code-templates.md` as reference-only, ensure no phase loads it (R-006)
4. Add phase timing instrumentation for `phase_3_seconds` (SC-013)

**Milestone M2**: Phase 3 produces a populated spec with brainstorm gap analysis from Phase 1+2 inputs.

**Exit Criteria**:
- Every `step_mapping` entry produces a corresponding FR (SC-004)
- Brainstorm section present in output (SC-005)
- Zero remaining placeholder sentinels (SC-003)
- Phase completes within 10-minute wall clock target (NFR-001)

---

### Phase 3: Phase 4 Rewrite — Spec Panel Review
**Duration**: 2-3 days | **Risk**: Medium-High (convergence loop complexity)

**Objective**: Replace integration phase with two-pass panel review and convergence loop.

1. Rewrite Phase 4 in `SKILL.md` (FR-014)
   - **4a** Focus pass with `--focus correctness,architecture` (FR-008):
     - Embed `sc:spec-panel` behavioral patterns inline (Constraint 1)
     - Output: `{finding_id, severity(CRITICAL/MAJOR/MINOR), expert, location, issue, recommendation}`
   - **4b** Focus incorporation (FR-009):
     - CRITICAL: address (incorporate or justify dismissal — Constraint 7)
     - MAJOR: incorporate into spec body
     - MINOR: append to Open Items
     - All modifications additive-only (Constraint 2, NFR-008)
   - **4c** Critique pass with `--mode critique` (FR-010):
     - Quality scores: `{clarity, completeness, testability, consistency}` as floats
     - Prioritized improvement recommendations
   - **4d** Critique incorporation and scoring (FR-011):
     - Record quality scores in spec frontmatter
     - Compute `overall = mean(clarity, completeness, testability, consistency)` (Constraint 6)
     - Append full panel report as `panel-report.md`
   - **4e** Convergence loop (FR-012, NFR-006):
     - If unaddressed CRITICALs remain → loop to 4a
     - Max 3 iterations (Constraint enforced)
     - After 3 iterations: escalate to user, set `status: partial`
2. Remove old Phase 4 instructions: main.py patching, import verification, structural tests, summary writing (FR-014)
3. Add phase timing instrumentation for `phase_4_seconds` (SC-013)
4. Implement `downstream_ready` gate: `overall >= 7.0` → true, else false (Constraint 8, SC-012)

**Milestone M3**: Phase 4 produces reviewed spec with quality scores and panel report, convergence loop terminates correctly.

**Exit Criteria**:
- Focus pass produces findings for both correctness and architecture (SC-006)
- Critique produces all 4 quality dimension scores (SC-007)
- No unaddressed CRITICALs after ≤3 iterations (SC-008)
- Boundary test: 7.0 → ready, 6.9 → not ready (SC-012)
- Phase completes within 15-minute wall clock target (NFR-002)

---

### Phase 4: Contract & Command Surface Updates
**Duration**: 1-2 days | **Risk**: Low

**Objective**: Update return contract schema and CLI command flags.

1. Update return contract (FR-015):
   - Add fields: `contract_version`, `spec_file`, `panel_report`, `quality_scores` (5 fields), `convergence_iterations`, `phase_timing`, `resume_substep`, `downstream_ready`, `warnings`
   - Emit on every invocation including failures (SC-009)
   - On failure: quality scores = `0.0` (not null), `downstream_ready = false` (NFR-009)
   - Populate `resume_substep` for resumable failures (NFR-007)
2. Update `--dry-run` behavior (FR-016):
   - Execute Phases 0-2 only
   - Emit Phase 0-2 contracts only
   - No spec synthesis or panel review artifacts
3. Remove `--skip-integration` flag from `cli-portify.md` (SC-014)
4. Update `refs/pipeline-spec.md` for Phase 2→3 bridge (D-008)

**Milestone M4**: Contract schema complete, dry-run works, removed flag not recognized.

**Exit Criteria**:
- Return contract emitted on success, failure, and dry-run (SC-009)
- `--skip-integration` flag rejected by command (SC-014)
- Quality score formula verified: `overall == mean(4 scores)` (SC-010)

---

### Phase 5: Validation & Testing
**Duration**: 1-2 days | **Risk**: Low-Medium

**Objective**: Verify all success criteria with self-validation checks and E2E tests.

1. Self-validation checks (11 checks):
   - SC-003: Zero placeholder sentinels
   - SC-004: Step mapping → FR count match
   - SC-005: Brainstorm section exists
   - SC-006: Focus findings per dimension
   - SC-007: All 4 quality scores present
   - SC-008: No unaddressed CRITICALs
   - SC-009: Contract emitted on all paths
   - SC-010: Quality formula correctness
   - SC-012: Boundary test at 7.0
   - SC-013: Phase timing populated
   - SC-014: Removed flag rejected
2. E2E scenarios:
   - SC-001: Full portify run → reviewed spec + panel report
   - SC-002: Dry run → stops after Phase 2
   - SC-011: Downstream handoff → spec consumed by `sc:roadmap`
   - Convergence loop: force CRITICALs, verify ≤3 iteration termination
   - Resume: interrupt mid-Phase 4, verify `resume_substep` works
3. NFR timing validation under realistic conditions

**Milestone M5**: All 14 success criteria pass.

---

### Phase 6: Sync & Documentation
**Duration**: 0.5-1 day | **Risk**: Low

**Objective**: Propagate changes and update documentation.

1. Run `make sync-dev` (Constraint 10)
2. Run `make verify-sync` to confirm src/ and .claude/ match
3. Update `decisions.yaml` with architectural decisions from this work
4. Update SKILL.md internal documentation references
5. Verify `refs/code-templates.md` is preserved but unloaded

**Milestone M6**: All changes synced, verified, documented.

## 3. Risk Assessment & Mitigation

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| R-003: Panel passes consume too many tokens/time | Medium | Medium | Two focused passes (not one exhaustive); NFR time caps; monitor during Phase 5 |
| R-007: Convergence loop doesn't converge | Medium | Low-Medium | Max 3 iterations hard cap; additive-only prevents new issues; user escalation path |
| R-008: Focus incorporation introduces new issues | High impact | Low | Additive-only constraint (Constraint 2) mechanically prevents rewrites |
| R-009: Behavioral contract drift over time | Medium | Medium | Document behavioral interface contracts explicitly; flag as tech debt for mechanical enforcement later |
| R-004: Generated spec too generic | Medium impact | Low | Template sections map directly to Phase 1+2 concrete outputs |
| R-005: Users skip Phase 4 review | Medium | Medium | Quality scores in frontmatter; `downstream_ready` gate blocks progression |

**Risks requiring architectural attention**:
- **Behavioral pattern fidelity** (Open Question 4): No mechanical enforcement that embedded patterns stay synchronized with canonical command definitions. Recommend adding a version tag to embedded patterns and a sync-check in CI as follow-up work.
- **Quality score calibration** (Open Question 5): The 7.0 threshold is untested empirically. Recommend collecting score distributions during initial usage and adjusting if non-discriminating.

## 4. Resource Requirements & Dependencies

### Implementation Dependencies (ordered per Constraint 9)

```
Template (FR-017) 
  → Phase 3/4 rewrite (FR-001–FR-012) 
    → Contract update (FR-015) 
      → Command update (FR-016) 
        → refs addendum 
          → decisions.yaml 
            → sync
```

### Files Modified

| File | Changes | Phase |
|------|---------|-------|
| `src/superclaude/examples/release-spec-template.md` | **Created** | 1 |
| `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` | Phase 3+4 rewrite, Phase 3+4 old removal | 2, 3 |
| `src/superclaude/commands/cli-portify.md` | `--skip-integration` removal, contract schema | 4 |
| `src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md` | Phase 2→3 bridge update | 4 |

### External Dependencies

- D-004: `sc:brainstorm` behavioral patterns must be stable in `src/superclaude/commands/brainstorm.md`
- D-005: `sc:spec-panel` behavioral patterns must be stable in `src/superclaude/commands/spec-panel.md`
- D-002/D-003: Phase 1+2 outputs (existing, unchanged)

## 5. Success Criteria & Validation

All 14 success criteria from the extraction are addressed:

- **SC-001 through SC-010**: Covered in Phase 5 validation suite
- **SC-011**: Downstream handoff E2E test (spec → `sc:roadmap`)
- **SC-012**: Boundary test at quality threshold 7.0
- **SC-013**: Phase timing instrumentation (Phases 2-3)
- **SC-014**: Removed flag test (Phase 4)

**Quality gate**: Overall quality score ≥ 7.0 required for `downstream_ready: true` (NFR-003).

## 6. Timeline Estimates

| Phase | Duration | Cumulative | Blocking Dependencies |
|-------|----------|------------|----------------------|
| 1: Template Foundation | 1-2 days | 1-2 days | None |
| 2: Phase 3 Rewrite | 2-3 days | 3-5 days | Phase 1 complete |
| 3: Phase 4 Rewrite | 2-3 days | 5-8 days | Phase 2 complete |
| 4: Contract & Command | 1-2 days | 6-10 days | Phase 3 complete |
| 5: Validation | 1-2 days | 7-12 days | Phase 4 complete |
| 6: Sync & Docs | 0.5-1 day | 8-12 days | Phase 5 complete |

**Critical path**: Phases 1→2→3→4→5→6 (fully sequential due to dependency chain in Constraint 9).

**Parallelization opportunity**: Limited. Phase 4 contract work could begin in parallel with late Phase 3 convergence loop implementation, saving ~0.5 days.

## 7. Open Questions Requiring Resolution

Items that should be resolved before or during implementation:

1. **Convergence loop user actions** (OQ-7): Define available user actions on escalation (force-accept / edit-and-rerun / abandon). Recommend: all three, with force-accept setting `status: forced`.
2. **Downstream contract compatibility** (OQ-8): Verify `sc:roadmap` and `sc:tasklist` handle `contract_version: "2.20"` schema. Recommend: check during Phase 4 implementation.
3. **Panel failure recovery granularity** (OQ-6): Recommend: resume at pass level (4a/4c), not sub-sub-step. Simpler and sufficient.
4. **Progress observability** (OQ-1): Defer to follow-up work. Phase timing in contract provides post-hoc observability; real-time progress is nice-to-have.
5. **Quality score calibration** (OQ-5): Collect empirical data during first 5-10 runs before adjusting threshold. No action needed now.
