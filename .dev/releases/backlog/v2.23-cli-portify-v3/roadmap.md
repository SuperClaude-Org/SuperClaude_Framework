---
spec_source: "spec-cli-portify-workflow-evolution.md"
complexity_score: 0.65
adversarial: true
base_variant: "A (Opus-Architect)"
variant_scores: "A:81 B:76"
convergence_score: 0.78
debate_rounds: 3
---

# Merged Roadmap: CLI Portify v3 — Release Spec Synthesis & Panel Review

## Executive Summary

This roadmap defines the evolution of `sc:cli-portify` from a code-generation pipeline into a **release specification synthesis and review pipeline**. The core change replaces Phases 3-4 (code generation + integration) with Phase 3 (spec synthesis with embedded brainstorm) and Phase 4 (spec-panel review with convergence loop). Phases 0-2 remain untouched.

**Scope**: 26 requirements (17 functional, 9 non-functional) across 5 domains, modifying ~4 files with 1 new template artifact. The work is moderate in complexity but carries meaningful behavioral and contract risk because it changes orchestration semantics, downstream artifacts, and validation expectations.

**Key architectural decisions**:
- Behavioral patterns from `sc:brainstorm` and `sc:spec-panel` are embedded inline rather than invoked as commands, keeping the pipeline non-interactive and automatable.
- The convergence loop uses state machine terminology for documentation and edge-case reasoning, implemented as a bounded conditional loop in SKILL.md.
- Failure contracts are first-class artifacts: every execution path emits a complete return contract.

**Planning estimate**: 6-8 working days. Critical path is fully sequential due to dependency chain.

**Adversarial provenance**: This roadmap merges Variant A (Opus-Architect, score 81) as structural backbone with targeted improvements from Variant B (Haiku-Analyzer, score 76) identified through 3-round adversarial debate (convergence 0.78). 10 of 14 diff points fully resolved; 2 partially resolved; 2 resolved by compromise.

## Phased Implementation Plan

### Phase 1: Template Foundation & Pre-Implementation Verification

**Duration**: 1-2 days | **Risk**: Low

**Objective**: Verify scope boundaries, trace downstream dependencies, and create the reusable release spec template.

#### Pre-Implementation Verification Checklist

Before any template work begins, complete the following (incorporated from debate D-01, D-09):

1. **Change inventory**: Confirm the 4 files to be modified and 1 file to be created
2. **Dependency trace**: Trace all downstream consumers of the return contract (specifically `sc:roadmap` and `sc:tasklist`) and the reviewed spec artifact
3. **Regression checklist**: Confirm Phases 0-2 behavior is unchanged and no phase references old Phase 3/4 outputs
4. **Sync requirement**: Confirm `src/superclaude/` changes must be followed by `make sync-dev`

#### Template Creation

1. Create `src/superclaude/examples/release-spec-template.md` (FR-017)
   - Frontmatter schema with quality score fields
   - All 12 template sections: problem statement, solution overview, FRs, architecture, interface contracts, NFRs, risk assessment, test plan, migration, downstream inputs, open items, brainstorm gap analysis
   - Use `{{SC_PLACEHOLDER:name}}` sentinel format (Constraint 5)
   - Validate template works for: new feature, refactoring, portification, infrastructure specs (cross-type validation from debate D-13)
2. Validate sentinel format doesn't collide with template content (Open Question 3)
3. Write self-validation check: regex scan for remaining sentinels (SC-003)
4. Mark conditional sections clearly (FR-060.7) — sections only required for specific spec types (e.g., migration section for portification specs, backward compatibility for refactoring specs) must be marked with conditional indicators

**Gate A** (from debate D-04): Ready to start synthesis rewrite.
- Template file exists at canonical location (Constraint 4)
- Zero sentinel collisions with template prose
- Template sections map 1:1 to the section-to-source mapping table in the spec
- Dependency trace complete; downstream consumers identified
- Cross-type reusability confirmed for all 4 spec types

---

### Phase 2: Phase 3 Rewrite — Spec Synthesis

**Duration**: 2-3 days | **Risk**: Medium

**Objective**: Replace code generation with spec synthesis including embedded brainstorm.

#### Phase 2→3 Entry Gate (FR-060.1 entry criteria)

Before Phase 3 work begins, verify:
- Phase 2 contract `status: completed`
- All blocking checks passed
- `step_mapping` contains ≥1 entry

1. Rewrite Phase 3 in `SKILL.md` (FR-013)
   - **3a** Template instantiation: load template, create working copy at `{work_dir}/portify-release-spec.md` (FR-001)
   - **3b** Content population: map Phase 1 + Phase 2 outputs to template sections per the 10-section mapping table (FR-002, FR-003)
   - **3c** Embedded brainstorm pass (FR-004, FR-005, FR-006):
     - Multi-persona (architect + analyzer + backend) non-interactive analysis
     - Structured output format: `{gap_id, description, severity, affected_section, persona}`
     - Zero-gap handling with explicit "No gaps identified" summary and `gaps_identified: 0` contract field
   - **3d** Gap incorporation: actionable findings into spec body, unresolvable to Section 11 (FR-007)
2. Remove all code generation instructions from SKILL.md (FR-013)
3. Preserve `refs/code-templates.md` as reference-only, ensure no phase loads it (R-006)
4. Add phase timing instrumentation for `phase_3_seconds` (SC-013)

**Gate B**: Ready to start panel review rewrite.
- Every `step_mapping` entry produces a corresponding FR (SC-004)
- Brainstorm section present in output (SC-005)
- Zero remaining placeholder sentinels (SC-003)
- Phase completes within 10-minute wall clock target (NFR-001, non-blocking advisory)

---

### Phase 3: Phase 4 Rewrite — Spec Panel Review

**Duration**: 2-3 days | **Risk**: Medium-High (convergence loop complexity)

**Objective**: Replace integration phase with two-pass panel review and convergence loop.

#### Review Passes

1. Rewrite Phase 4 in `SKILL.md` (FR-014)
   - **4a** Focus pass with `--focus correctness,architecture` (FR-008):
     - Embed `sc:spec-panel` behavioral patterns inline (Constraint 1), applying Fowler (architecture), Nygard (reliability/failure modes), Whittaker (adversarial), Crispin (testing) expert analysis
     - Output: `{finding_id, severity(CRITICAL/MAJOR/MINOR), expert, location, issue, recommendation}`
   - **4b** Focus incorporation (FR-009):
     - CRITICAL: address (incorporate or justify dismissal — Constraint 7)
     - MAJOR: incorporate into spec body
     - MINOR: append to Open Items
     - All modifications additive-only (Constraint 2, NFR-008)
   - **4c** Critique pass with `--mode critique` (FR-010):
     - Quality scores: `{clarity, completeness, testability, consistency}` as floats (0-10 range)
     - Prioritized improvement recommendations
   - **4d** Critique incorporation and scoring (FR-011):
     - Record quality scores in spec frontmatter
     - Compute `overall = mean(clarity, completeness, testability, consistency)` (Constraint 6)
     - Append full panel report as `panel-report.md`

#### Convergence Loop

Document using state machine terminology (debate D-03 synthesis); implement as bounded conditional loop:

- **States**: REVIEWING → INCORPORATING → SCORING → {CONVERGED | ESCALATED}
- **Transition logic**: If unaddressed CRITICALs remain after SCORING → return to REVIEWING
- **Bound**: Max 3 iterations (Constraint enforced)
- **Terminal states**:
  - CONVERGED: zero unaddressed CRITICALs, `status: success`
  - ESCALATED: 3 iterations exhausted, `status: partial`, escalate to user

2. Remove old Phase 4 instructions: main.py patching, import verification, structural tests, summary writing (FR-014)
3. Add phase timing instrumentation for `phase_4_seconds` (SC-013)
4. Implement `downstream_ready` gate: `overall >= 7.0` → true, else false (Constraint 8, SC-012)

**Exit Criteria**:
- Focus pass produces findings for both correctness and architecture (SC-006)
- Critique produces all 4 quality dimension scores (SC-007)
- No unaddressed CRITICALs after ≤3 iterations (SC-008)
- Phase completes within 15-minute wall clock target (NFR-002)

---

### Phase 4: Contract & Command Surface Updates

**Duration**: 1-2 days | **Risk**: Low-Medium

**Objective**: Update return contract schema, CLI command flags, and validate failure paths early.

#### Contract Updates

1. Update return contract (FR-015):
   - Add fields: `contract_version`, `spec_file`, `panel_report`, `quality_scores` (5 fields), `convergence_iterations`, `phase_timing`, `resume_substep`, `downstream_ready`, `warnings`, `output_directory`, `failure_phase`, `failure_type`, `source_step_count`, `spec_fr_count`, `api_snapshot_hash`, `resume_command`, `resume_phase`, `phase_contracts`
   - `failure_type` enumeration: `template_failed | brainstorm_failed | brainstorm_timeout | focus_failed | critique_failed | convergence_exhausted | user_rejected`
   - Emit on every invocation including failures (SC-009)
   - On failure: quality scores = `0.0` (not null), `downstream_ready = false` (NFR-009)
   - Populate `resume_substep` for resumable failures (NFR-007)
   - **Resume behavior semantics**:
     - Phase 3 resume (`resume_substep=3c`): populated spec from 3b preserved; brainstorm re-runs from 3c
     - Phase 4 resume (`resume_substep=4a`): draft spec from Phase 3 preserved; review re-runs from 4a
     - All prior phase artifacts preserved on resume

#### Command Surface

2. Update `--dry-run` behavior (FR-016):
   - Execute Phases 0-2 only
   - Emit Phase 0-2 contracts only
   - No spec synthesis or panel review artifacts
3. Remove `--skip-integration` flag from `cli-portify.md` (SC-014)
4. Update `refs/pipeline-spec.md` for Phase 2→3 bridge (D-008)

#### Early Failure Path Validation (from debate D-06, D-14)

5. Validate contract failure paths immediately:
   - Quality scores default to `0.0` on failure (not null)
   - `downstream_ready = false` on failure
   - Contract schema complete on all paths (success, partial, failure)
   - `resume_substep` populated for resumable failures
   - Boundary test: `overall = 7.0` → ready, `overall = 6.9` → not ready (SC-012)

**Gate C**: Ready to expose CLI behavior.
- Return contract emitted on success, failure, and dry-run (SC-009)
- `--skip-integration` flag rejected by command (SC-014)
- Quality score formula verified: `overall == mean(4 scores)` (SC-010)
- All failure path defaults validated

---

### Phase 5: Validation & Testing

**Duration**: 1-1.5 days | **Risk**: Low-Medium

**Objective**: Verify all success criteria using the 5-category validation taxonomy.

Organized per Haiku's validation taxonomy (debate D-08):

#### Structural Validation
- SC-003: Zero placeholder sentinels in generated spec
- SC-004: Step mapping → FR count match
- SC-005: Brainstorm section exists
- Frontmatter fields present; panel report exists when Phase 4 runs

#### Behavioral Validation
- SC-006: Focus findings per dimension (correctness, architecture)
- SC-007: All 4 quality scores present
- Brainstorm findings follow required schema
- Zero-gap path produces correct summary
- Additive-only incorporation is respected

#### Contract Validation
- SC-009: Contract emitted on all paths (success, partial, failure, dry-run)
- SC-010: Quality formula correctness (`overall == mean(4 scores)`)
- SC-013: Phase timing populated for completed phases
- SC-014: Removed flag rejected
- Resume substep populated on resumable failures

#### Boundary Validation
- SC-012: `overall = 7.0` → downstream-ready true; `overall = 6.9` → false
- SC-008: No unaddressed CRITICALs after ≤3 iterations
- Mid-panel failure sets scores to `0.0`
- Iteration limit reached at 3

#### End-to-End Validation
- SC-001: Full portify run → reviewed spec + panel report
- SC-002: Dry run → stops after Phase 2
- SC-011: Downstream handoff → spec consumed by `sc:roadmap`
- Convergence loop: force CRITICALs, verify ≤3 iteration termination
- Resume: interrupt mid-Phase 4, verify `resume_substep` works
- Low-quality spec recovery: introduce intentional gaps in Phase 2 output → brainstorm catches gaps; panel flags them; spec updated before user review
- Phase 3 brainstorm timeout: simulate brainstorm failure mid-execution → return contract emitted with `failure_type=brainstorm_failed`; `resume_substep=3c`

**Validation evidence required**: Test output logs, contract snapshots for success and failure paths, generated spec sample, panel report sample, downstream consumption proof.

---

### Phase 6: Sync & Documentation

**Duration**: 0.5-1 day | **Risk**: Low

**Objective**: Propagate changes and update documentation.

1. Run `make sync-dev` (Constraint 10)
2. Run `make verify-sync` to confirm src/ and .claude/ match
3. Update `decisions.yaml` with architectural decisions from this work (mandatory)
4. Update SKILL.md internal documentation references
5. Verify `refs/code-templates.md` is preserved but unloaded
6. Mark `refs/code-templates.md` as inactive reference-only (debate R9 mitigation)

**Gate D**: Ready for downstream use.
- All changes synced and verified
- `decisions.yaml` updated
- Overall quality threshold logic validated
- No unaddressed CRITICAL findings
- Reviewed spec consumed by `sc:roadmap` (downstream interoperability confirmed)

## Risk Assessment

| ID | Risk | Severity | Probability | Mitigation |
|----|------|----------|-------------|------------|
| R-001 | Behavioral pattern drift — embedded brainstorm/spec-panel logic diverges from canonical commands | High | Medium | Create behavioral contract checklist for both passes; add regression tests comparing output schemas; require review on canonical command changes; add version tags to embedded patterns |
| R-002 | Convergence loop doesn't converge | Medium | Low-Medium | Max 3 iterations hard cap; additive-only prevents new issues; user escalation with `status: partial`; preserve prior artifacts for manual review |
| R-003 | Panel passes consume too many tokens/time | Medium | Medium | Two focused passes (not exhaustive); NFR time caps; monitor during Phase 5; flag overruns as warnings |
| R-004 | Generated spec too generic for downstream use | Medium | Low | Template sections map directly to Phase 1+2 concrete outputs; reject output with unresolved placeholders |
| R-005 | Additive incorporation introduces contradictions | Medium | Medium | Constrain additions to section-specific extensions; track each finding by ID; use critique pass to detect contradictions (from debate D-05) |
| R-006 | Focus incorporation introduces structural issues | High impact | Low | Additive-only constraint (Constraint 2) mechanically prevents rewrites |
| R-007 | Downstream consumer incompatibility | Medium | Medium | Validate `sc:roadmap` against new spec format before release; confirm tolerance for `contract_version: "2.20"`; document compatibility expectations (from debate D-09, converted from OQ-8) |
| R-008 | Contract inconsistency on failure paths | High | Low-Medium | Mandatory contract emission; failure-path tests in Phase 4; numeric defaults (not nulls); schema validation on every invocation |
| R-009 | Orphaned reference artifacts become misleading | Low | Medium | Mark `refs/code-templates.md` as inactive; ensure no workflow phase loads it (from debate D-05) |

### Architectural Attention Flags

- **Behavioral pattern fidelity** (Open Question 4): No mechanical enforcement that embedded patterns stay synchronized with canonical command definitions. Recommend adding a version tag to embedded patterns and a sync-check in CI as follow-up work.
- **Quality score calibration** (Open Question 5): The 7.0 threshold is untested empirically. Recommend collecting score distributions during first 5-10 runs and adjusting if non-discriminating.

## Resource Requirements

### Implementation Dependencies (ordered per Constraint 9)

```
Pre-Implementation Verification
  → Template (FR-017)
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
| `src/superclaude/skills/sc-cli-portify-protocol/decisions.yaml` | Architectural decisions from this work | 6 |

### External Dependencies

- D-004: `sc:brainstorm` behavioral patterns must be stable in `src/superclaude/commands/brainstorm.md`
- D-005: `sc:spec-panel` behavioral patterns must be stable in `src/superclaude/commands/spec-panel.md`
- D-002/D-003: Phase 1+2 outputs (existing, unchanged)

### Capability Requirements

This work is executed by a solo developer with Claude Code. No team role assignments are necessary (debate D-07). Key capability needs:
- Behavioral protocol authoring (SKILL.md rewrite)
- Contract schema design (return contract)
- Validation design (self-checks + E2E)

## Success Criteria and Validation Approach

All 14 success criteria from the extraction are addressed:

| Criterion | Coverage |
|-----------|----------|
| SC-001 through SC-010 | Phase 5 validation suite (5-category taxonomy) |
| SC-011 | Downstream handoff E2E test (spec → `sc:roadmap`) |
| SC-012 | Boundary test at quality threshold 7.0 (Phase 4 early + Phase 5) |
| SC-013 | Phase timing instrumentation (Phases 2-3) |
| SC-014 | Removed flag test (Phase 4) |

**Quality gate**: Overall quality score ≥ 7.0 required for `downstream_ready: true` (NFR-003).

**Validation evidence required**: Test output logs, contract snapshots (success + failure), generated spec sample, panel report sample, downstream consumption proof.

## Timeline Estimates

| Phase | Duration | Cumulative | Blocking Dependencies |
|-------|----------|------------|----------------------|
| 1: Template Foundation & Pre-Verification | 1-2 days | 1-2 days | None |
| 2: Phase 3 Rewrite (Spec Synthesis) | 2-3 days | 3-5 days | Gate A (Phase 1) |
| 3: Phase 4 Rewrite (Panel Review) | 2-3 days | 5-8 days | Gate B (Phase 2) |
| 4: Contract & Command Surface | 1-1.5 days | 6-9 days | Phase 3 complete |
| 5: Validation & Testing | 1-1.5 days | 7-10 days | Gate C (Phase 4) |
| 6: Sync & Documentation | 0.5 day | 6-8 days | Phase 5 complete |

**Planning estimate**: 6-8 working days.

**Critical path**: Phases 1→2→3→4→5→6 (fully sequential due to dependency chain in Constraint 9).

**Parallelization opportunity**: Per spec §4.7, SKILL.md Phase 3 rewrite and Phase 4 rewrite may run in parallel (~1-2 days savings). Additionally, Phase 4 contract schema work could begin in parallel with late Phase 3 convergence loop implementation. Sequential execution chosen for this roadmap due to dependency chain simplicity, but parallel execution is a valid optimization.

## Open Questions Requiring Resolution

Items that remain genuine unresolved decisions (not risk-adjacent — those are embedded in the risk table):

| ID | Question | Recommendation | Resolution Timing |
|----|----------|----------------|-------------------|
| OQ-5 | Quality score calibration — is 7.0 the right threshold? | Collect empirical data during first 5-10 runs before adjusting | Post-implementation |
| OQ-7 | ~~RESOLVED~~ — User rejection options at Phase 4 gate defined per spec §5.2: (1) Edit and re-review: manually edit spec, resume from `resume_substep=4a`; (2) Regenerate: resume from Phase 3; (3) Abandon: `status: failed, failure_type: user_rejected`. Convergence exhaustion (3 iterations) separately escalates with `status: partial`. | N/A — Resolved | N/A |
| OQ-6 | Panel failure recovery granularity | Resume at pass level (4a/4c), not sub-sub-step — simpler and sufficient | During Phase 4 |
| OQ-8 | Progress observability — NFR time targets have no real-time progress indicator mechanism (Spec Open Item 1, Hightower) | Define phase progress events or progress bar in future iteration | Post-implementation |
| OQ-9 | Brainstorm enrichment mapping formalism — `affected_section` field could be more formally defined with section paths or line ranges (Spec Open Item 2, Hohpe) | Evaluate after first 5-10 runs | Post-implementation |

## Requirement Traceability

| Roadmap ID | Spec ID | Description |
|------------|---------|-------------|
| FR-001 | FR-060.1/3a | Template instantiation |
| FR-002 | FR-060.1/3b | Content population |
| FR-003 | FR-060.1/3b | Step mapping → FR correspondence |
| FR-004–007 | FR-060.1/3c-3d | Brainstorm pass and gap incorporation |
| FR-008–012 | FR-060.2/4a-4e | Panel review and convergence |
| FR-013 | FR-060.3 | Remove old Phase 3 |
| FR-014 | FR-060.4 | Remove old Phase 4 |
| FR-015 | FR-060.5 | Return contract update |
| FR-016 | FR-060.6 | Dry-run behavior |
| FR-017 | FR-060.7 | Release spec template |
| NFR-001–006 | NFR-060.1–060.6 | Non-functional requirements |
| NFR-007–009 | Implicit | Resume, additive-only, failure defaults |

## Constraints Reference

| ID | Constraint | Source |
|----|-----------|--------|
| Constraint 1 | No inter-skill command invocation; embed behavioral patterns inline | §2.1 Decision 1 |
| Constraint 2 | Additive-only incorporation (append/extend, no rewrites) | §2.1 Decision 2 |
| Constraint 4 | Template at `src/superclaude/examples/release-spec-template.md` | §2.1 Decision 4 |
| Constraint 5 | Sentinel format `{{SC_PLACEHOLDER:name}}` | §2.1 Decision 5 |
| Constraint 6 | Quality formula: `overall = mean(4 scores)` | §2.1 Decision 6 |
| Constraint 7 | CRITICAL findings: incorporation OR justified-dismissal | §2.1 Decision 7 |
| Constraint 8 | Downstream-ready threshold: `overall >= 7.0` | §2.1 Decision 8 |
| Constraint 9 | Implementation order per dependency chain | §2.1 Decision 9 |
| Constraint 10 | Component sync via `make sync-dev` | §2.1 Decision 10 |
