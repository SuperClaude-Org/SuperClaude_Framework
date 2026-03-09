---
spec_source: "spec-cli-portify-workflow-evolution.md"
complexity_score: 0.65
primary_persona: analyzer
---

# Executive Summary

This roadmap covers the portification of the `sc:cli-portify` workflow from a code-generation/integration-oriented Phase 3/4 model to a release-spec-synthesis and panel-review model. The work is moderate in complexity but carries meaningful behavioral and contract risk because it changes orchestration semantics, downstream artifacts, and validation expectations without changing Phases 0-2.

From an analyzer perspective, the highest-priority concerns are:

1. **Behavioral fidelity risk**: embedded `sc:brainstorm` and `sc:spec-panel` patterns must remain aligned with their canonical definitions.
2. **State/contract integrity risk**: convergence loops, resume points, timing fields, and failure contracts must be correct on every path.
3. **Downstream readiness risk**: reviewed specs must be reliably consumable by `sc:roadmap`, with quality thresholds enforced consistently.
4. **Regression containment**: old code-generation/integration behavior must be removed cleanly without destabilizing Phases 0-2.

The recommended implementation strategy is a **controlled phased rollout** that prioritizes artifact correctness, contract completeness, and self-validation before CLI surface exposure.

---

# 1. Phased Implementation Plan with Milestones

## Phase 0 — Baseline Verification and Change Boundary Lock
**Objective**: Confirm scope boundaries and prevent unintended edits outside approved components.

### Actions
1. Verify the canonical inputs and outputs:
   - `src/superclaude/examples/release-spec-template.md`
   - `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`
   - `src/superclaude/commands/cli-portify.md`
   - `src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md`
2. Freeze assumptions:
   - Phases 0-2 remain unchanged.
   - Old Phase 3 code generation behavior is removed.
   - Old Phase 4 integration behavior is removed.
3. Trace all downstream consumers of the return contract and reviewed spec artifact.
4. Confirm sync requirement:
   - `src/superclaude/` changes must be followed by `make sync-dev`.

### Milestone
- **M0**: Scope boundary and dependency map approved.

### Deliverables
- Change inventory
- Dependency trace
- Regression checklist for immutable phases

---

## Phase 1 — Release Spec Template Hardening
**Objective**: Ensure the general-purpose release spec template is complete, reusable, and safe for synthesis.

### Actions
1. Validate `release-spec-template.md` against required sections:
   - frontmatter
   - problem statement
   - solution overview
   - FRs
   - architecture
   - interface contracts
   - NFRs
   - risk assessment
   - test plan
   - migration
   - downstream inputs
   - open items
2. Validate sentinel usage:
   - only `{{SC_PLACEHOLDER:name}}`
   - no collisions with legitimate content
3. Confirm the template supports all intended modes:
   - new feature
   - refactoring
   - portification
   - infrastructure
4. Add a placeholder-completion validation rule to detect unresolved template markers.

### Milestone
- **M1**: Template passes completeness and placeholder validation.

### Deliverables
- Hardened template
- Placeholder validation criteria
- Section-to-source mapping confirmation

---

## Phase 2 — Phase 3 Rewrite: Release Spec Synthesis
**Objective**: Replace old code generation behavior with deterministic release spec synthesis.

### Actions
1. Implement template instantiation behavior:
   - load `src/superclaude/examples/release-spec-template.md`
   - create `{work_dir}/portify-release-spec.md`
2. Populate all mapped sections from Phase 1 and Phase 2 outputs.
3. Enforce FR coverage:
   - every `step_mapping` entry must generate a corresponding FR in Section 3
4. Add brainstorm pass behavior inline:
   - architect + analyzer + backend perspectives
   - non-interactive
   - output schema:
     - `gap_id`
     - `description`
     - `severity`
     - `affected_section`
     - `persona`
5. Append `## Brainstorm Gap Analysis`.
6. Implement zero-gap behavior with explicit summary and contract field.
7. Incorporate actionable gaps into target sections.
8. Route unresolved items to Section 11 Open Items.

### Milestone
- **M2**: Draft release spec is generated deterministically with brainstorm enrichment.

### Deliverables
- Draft release spec
- Brainstorm gap analysis section
- FR traceability from `step_mapping`

---

## Phase 3 — Phase 4 Rewrite: Spec Panel Review and Convergence
**Objective**: Replace old integration behavior with focused review, critique scoring, and bounded convergence.

### Actions
1. Implement focused review pass inline using `sc:spec-panel` behavior:
   - focus: correctness, architecture
   - output schema:
     - `finding_id`
     - `severity`
     - `expert`
     - `location`
     - `issue`
     - `recommendation`
2. Apply additive-only incorporation rules:
   - CRITICAL: must be incorporated or justified-dismissed
   - MAJOR: incorporated into spec body
   - MINOR: added to Open Items
3. Implement critique pass:
   - `clarity`
   - `completeness`
   - `testability`
   - `consistency`
4. Compute overall quality:
   - `mean(clarity, completeness, testability, consistency)`
5. Write quality scores into spec frontmatter.
6. Emit `panel-report.md`.
7. Implement convergence loop:
   - rerun if unaddressed CRITICAL findings remain
   - maximum 3 iterations
   - escalate with `status: partial` if unresolved after limit

### Milestone
- **M3**: Panel review and convergence loop complete with bounded termination.

### Deliverables
- Reviewed spec
- Panel report
- Quality scores
- Convergence iteration record

---

## Phase 4 — Return Contract and Resume Semantics
**Objective**: Make all execution paths contract-complete and resumable.

### Actions
1. Update return contract to include:
   - `contract_version`
   - `spec_file`
   - `panel_report`
   - `quality_scores`
   - `convergence_iterations`
   - `phase_timing`
   - `resume_substep`
   - `downstream_ready`
   - `warnings`
   - failure-path fields
2. Guarantee contract emission on:
   - success
   - partial success
   - resumable failure
   - non-resumable failure
3. Enforce failure defaults:
   - quality scores = `0.0`
   - `downstream_ready = false`
4. Define substep resume behavior:
   - examples: `3c`, `4a`
5. Validate that prior phase artifacts are preserved across resume.

### Milestone
- **M4**: Contract schema is stable across all control-flow paths.

### Deliverables
- Updated return contract
- Resume semantics matrix
- Failure behavior matrix

---

## Phase 5 — CLI Surface and Protocol Alignment
**Objective**: Align command behavior and protocol references with the new workflow.

### Actions
1. Update `SKILL.md` to reflect:
   - new Phase 3 Release Spec Synthesis
   - new Phase 4 Spec Panel Review
2. Remove old instructions for:
   - code generation
   - main.py patching
   - import verification
   - structural test generation
   - summary writing
3. Preserve `refs/code-templates.md` as reference-only and ensure it is no longer loaded.
4. Update `src/superclaude/commands/cli-portify.md`:
   - support `--dry-run` stopping after Phase 2
   - remove `--skip-integration`
5. Update reference docs/addenda and `decisions.yaml` if required.
6. Sync dev copies:
   - run `make sync-dev`

### Milestone
- **M5**: CLI and protocol documentation reflect only the new behavioral model.

### Deliverables
- Updated command surface
- Updated skill protocol
- Synced `.claude/` copies

---

## Phase 6 — Validation, Boundary Testing, and Downstream Handoff
**Objective**: Prove the workflow is correct, bounded, and consumable.

### Actions
1. Implement self-validation checks for:
   - zero placeholders
   - step_mapping → FR parity
   - brainstorm section presence
   - focus pass findings
   - critique score population
   - no unaddressed CRITICAL findings
   - contract presence on failure
   - score formula correctness
   - threshold boundary at 7.0
   - timing field population
   - `--skip-integration` removal
2. Execute E2E scenarios:
   - full run
   - dry run
   - convergence loop
   - boundary quality cases
   - failure/resume cases
3. Validate `sc:roadmap` downstream consumption of reviewed spec.
4. Capture regressions and perform focused remediation.

### Milestone
- **M6**: Workflow validated as downstream-ready.

### Deliverables
- Validation results
- E2E evidence
- Downstream handoff evidence

---

# 2. Risk Assessment and Mitigation Strategies

## High-Priority Risks

### R1. Behavioral pattern drift
**Why it matters**: Embedded brainstorm/spec-panel logic may silently diverge from canonical command behavior.

**Mitigation**
1. Create a behavioral contract checklist for both embedded passes.
2. Add regression tests that compare expected output schemas and decision rules.
3. Require explicit review whenever canonical `brainstorm.md` or `spec-panel.md` changes.

### R2. Convergence loop fails to terminate cleanly
**Why it matters**: Unbounded or ambiguous convergence undermines automation.

**Mitigation**
1. Enforce hard cap of 3 iterations.
2. Record iteration count in contract every time.
3. Escalate deterministically with `status: partial`.
4. Preserve prior artifacts to support manual review/resume.

### R3. Contract inconsistency on failure paths
**Why it matters**: Downstream consumers break if failure contracts are incomplete or shape-shift.

**Mitigation**
1. Treat contract emission as mandatory infrastructure.
2. Add failure-path tests before shipping.
3. Set numeric defaults rather than nulls for quality scores.
4. Validate schema completeness on every invocation.

## Medium-Priority Risks

### R4. Spec too generic to be useful downstream
**Mitigation**
1. Enforce concrete section-to-source mapping.
2. Reject template output containing unresolved placeholders.
3. Validate that Phase 2 `step_mapping` produces concrete FRs.

### R5. Additive incorporation introduces clutter or contradictions
**Mitigation**
1. Constrain additions to section-specific appendices/extensions.
2. Track each incorporated finding by ID.
3. Use critique pass to detect contradictions created by additive content.

### R6. Time-budget overrun in Phase 3 or 4
**Mitigation**
1. Keep review passes scoped and structured.
2. Capture phase timings in contract.
3. Flag overruns as warnings even if output succeeds.

### R7. Downstream consumer incompatibility
**Mitigation**
1. Validate `sc:roadmap` against new reviewed spec format before release.
2. Confirm tolerance for new contract version.
3. Document compatibility expectations explicitly.

## Lower-Priority Risks

### R8. Zero-gap brainstorm outcome causes reviewer confusion
**Mitigation**
1. Emit explicit zero-gap summary.
2. Record `gaps_identified: 0` for auditability.

### R9. Orphaned reference artifacts become misleading
**Mitigation**
1. Mark `refs/code-templates.md` as inactive reference-only.
2. Ensure no workflow phase loads it.

---

# 3. Resource Requirements and Dependencies

## People / Capability Requirements
1. **Analyzer lead**
   - owns traceability, risks, validation, regression detection
2. **Architect reviewer**
   - validates structure, section mapping, convergence implications
3. **Backend/protocol maintainer**
   - updates SKILL.md, command behavior, contract emission
4. **QA/quality engineer**
   - validates self-checks, E2E flows, boundary cases

## Technical Dependencies
1. `src/superclaude/examples/release-spec-template.md`
2. Phase 1 workflow analysis output
3. Phase 2 pipeline specification contract
4. Canonical `sc:brainstorm` behavior definition
5. Canonical `sc:spec-panel` behavior definition
6. `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`
7. `src/superclaude/commands/cli-portify.md`
8. `src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md`

## Environment / Process Requirements
1. UV-based project workflow for any Python/test execution
2. `make sync-dev` after source changes
3. Test environment capable of:
   - self-validation checks
   - E2E workflow execution
   - contract inspection

## Recommended Dependency Order
1. Template validation
2. Phase 3 rewrite
3. Phase 4 rewrite
4. Contract update
5. CLI command update
6. Reference/addendum updates
7. Sync
8. Validation and downstream handoff

---

# 4. Success Criteria and Validation Approach

## Primary Success Criteria
1. Full run produces:
   - reviewed spec
   - `panel-report.md`
   - populated quality scores
   - complete return contract
2. Dry run stops after Phase 2 with no Phase 3/4 artifacts.
3. Generated spec contains zero unresolved placeholders.
4. Every Phase 2 `step_mapping` entry maps to a generated FR.
5. Final output has zero unaddressed CRITICAL findings.
6. `downstream_ready` is true only when `overall >= 7.0`.
7. Failure paths still emit complete contract objects.
8. `sc:roadmap` can consume the reviewed spec successfully.

## Validation Strategy

### A. Structural Validation
- frontmatter fields present
- required sections present
- placeholder regex returns zero matches
- panel report exists when Phase 4 runs

### B. Behavioral Validation
- brainstorm findings follow required schema
- zero-gap path produces correct summary
- focus pass returns categorized findings
- critique pass returns all four score dimensions
- additive-only incorporation is respected

### C. Contract Validation
- all mandatory fields always emitted
- failure defaults correct
- phase timing populated for completed phases
- resume substep populated on resumable failures

### D. Boundary Validation
- `overall = 7.0` → downstream-ready true
- `overall = 6.9` → downstream-ready false
- iteration limit reached at 3
- mid-panel failure sets scores to `0.0`

### E. End-to-End Validation
- full invocation from Phase 0-4
- `--dry-run`
- convergence loop with persistent CRITICAL finding
- downstream `sc:roadmap` handoff

## Validation Evidence Required
1. Test output logs
2. Contract snapshots for success and failure paths
3. Generated spec sample
4. Panel report sample
5. Downstream consumption proof

---

# 5. Timeline Estimates per Phase

## Overall Estimate
Given the **moderate complexity (0.65)** and the concentration of risk in behavioral fidelity and validation, the work should be planned as **6 implementation phases plus validation gates**, not as a single uninterrupted change set.

## Phase Estimates

### Phase 0 — Baseline Verification and Boundary Lock
- **Estimate**: 0.5 day
- **Reasoning**: low implementation effort, high analytical value

### Phase 1 — Template Hardening
- **Estimate**: 0.5 to 1 day
- **Reasoning**: section validation is straightforward, but placeholder safety and generalization need care

### Phase 2 — Phase 3 Rewrite: Release Spec Synthesis
- **Estimate**: 1 to 1.5 days
- **Reasoning**: deterministic mapping, brainstorm enrichment, and FR traceability are the main work items

### Phase 3 — Phase 4 Rewrite: Spec Panel Review and Convergence
- **Estimate**: 1 to 1.5 days
- **Reasoning**: most control-flow and quality-gate complexity resides here

### Phase 4 — Return Contract and Resume Semantics
- **Estimate**: 0.5 to 1 day
- **Reasoning**: contract work is compact but must be exhaustive across failure paths

### Phase 5 — CLI Surface and Protocol Alignment
- **Estimate**: 0.5 day
- **Reasoning**: focused edits, moderate regression sensitivity

### Phase 6 — Validation and Downstream Handoff
- **Estimate**: 1 to 1.5 days
- **Reasoning**: validation breadth is high due to 11 self-checks + 11 E2E scenarios

## Total Roadmap Estimate
- **Implementation + validation**: **4.0 to 6.0 working days**
- **Most schedule-sensitive items**:
  1. convergence loop correctness
  2. failure contract completeness
  3. downstream `sc:roadmap` compatibility

---

# 6. Recommended Milestone Gate Criteria

## Gate A — Ready to start synthesis rewrite
Must have:
1. validated template structure
2. confirmed immutable Phases 0-2
3. dependency map complete

## Gate B — Ready to start panel review rewrite
Must have:
1. deterministic spec generation
2. brainstorm gap analysis appended
3. FR traceability proven

## Gate C — Ready to expose CLI behavior
Must have:
1. panel review functioning
2. convergence bounded
3. return contract complete
4. `--dry-run` behavior verified

## Gate D — Ready for downstream use
Must have:
1. overall quality threshold logic validated
2. no unaddressed CRITICAL findings
3. reviewed spec consumed by `sc:roadmap`
4. sync complete and verified

---

# 7. Analyzer Recommendations

1. **Prioritize contract correctness before polish**. A complete but imperfectly worded reviewed spec is safer than a polished workflow with inconsistent failure contracts.
2. **Treat convergence as a controlled-state machine**, not an informal retry loop.
3. **Make behavioral fidelity explicit**. The biggest latent risk is silent drift between embedded logic and canonical command behavior.
4. **Test failure paths early**. The highest downstream breakage risk is not success behavior; it is partial/failure contract behavior.
5. **Do not collapse validation into a final step only**. Add checkpoints after template hardening, synthesis, and panel review.
6. **Validate downstream consumption before declaring readiness**. `downstream_ready` should reflect actual interoperability, not only score thresholds.

---

# 8. Final Readout

This is a **moderate-complexity protocol refactor** with **high importance on correctness, traceability, and bounded automation**. The work is feasible without major architectural expansion, but only if implemented with disciplined sequencing:

1. lock scope,
2. harden template,
3. rewrite synthesis,
4. rewrite panel review,
5. stabilize contracts,
6. validate full and failure paths,
7. confirm downstream interoperability.

The roadmap should be considered successful only when the reviewed spec is not merely generated, but **reliably scoreable, resumable, auditable, and consumable by downstream planning workflows**.
