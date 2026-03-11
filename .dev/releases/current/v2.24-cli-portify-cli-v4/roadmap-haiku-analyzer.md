---
spec_source: portify-release-spec.md
complexity_score: 0.85
primary_persona: analyzer
---

# Project Roadmap: CLI Portify v4

## 1. Executive Summary

This roadmap delivers a deterministic, synchronous CLI pipeline that ports existing SuperClaude workflows into repeatable programmatic runners. The target outcome is a new `cli-portify` command group that can analyze a workflow, design a pipeline, synthesize a release spec, run gap analysis, and perform convergent panel review without modifying existing `pipeline/` or `sprint/` base modules.

From an analyzer perspective, the main delivery risks are not feature ambiguity but execution correctness, integration fidelity, and failure-path completeness. The roadmap therefore prioritizes:

1. **Deterministic flow control in Python**
2. **Strict gate enforcement and machine-readable artifacts**
3. **Skill reuse without behavioral reimplementation**
4. **Failure-path observability, resume behavior, and review gating**
5. **Verification of boundary conditions and convergence logic**

### Primary Objectives
1. Build a 7-step pipeline across 5 phases.
2. Keep pure-programmatic steps fast and subprocess-free.
3. Ensure all Claude-assisted steps are constrained by runner-authored truth.
4. Reuse `/sc:brainstorm` and `/sc:spec-panel` safely with pre-flight validation and fallback handling.
5. Pass all defined unit and integration success criteria.

### Recommended Delivery Strategy
- Favor **incremental vertical slices** over broad parallel implementation.
- Establish **contracts and gates first**, then implement step logic against those contracts.
- Treat **resume, convergence, and failure contracts** as first-class features, not cleanup work.
- Validate architectural constraints continuously, especially:
  - synchronous-only execution
  - additive-only spec modification during review
  - zero base-module modifications

---

## 2. Phased Implementation Plan with Milestones

## Phase 0: Foundation and Contract Baseline

### Goals
Establish architecture, contracts, module boundaries, and verification scaffolding before implementation begins.

### Key Activities
1. Confirm target module layout under `src/superclaude/cli/cli_portify/`.
2. Define internal architecture for:
   - config handling
   - step execution
   - gate evaluation
   - subprocess orchestration
   - monitoring/logging
   - resume state
   - contract emission
3. Define canonical data contracts for:
   - step outputs
   - phase outputs
   - failure contracts
   - dry-run contracts
   - convergence status blocks
4. Define all gate function signatures as `tuple[bool, str]`.
5. Create initial test matrix covering:
   - positive paths
   - boundary conditions
   - failure defaults
   - skill availability failures
   - review rejection behavior

### Milestones
- **M0.1**: Architecture and module map approved
- **M0.2**: Contract schemas documented
- **M0.3**: Gate interface and test skeletons created

### Analyzer Concerns
- If contracts are deferred, downstream steps will drift and failure handling will fragment.
- Undefined monitoring/event vocabulary will become a late-stage blocker for diagnostics and resume logic.

### Exit Criteria
- All module responsibilities defined
- Gate signatures standardized
- Test plan covers all success criteria and risks

### Timeline Estimate
- **1-2 days**

---

## Phase 1: Pure-Programmatic Core

Covers:
- **FR-001 Config Validation**
- **FR-002 Component Discovery**

### Goals
Deliver fast, deterministic, subprocess-free early steps with reliable artifacts and validation.

### Key Activities
1. Implement config validation:
   - resolve workflow directory containing `SKILL.md`
   - derive CLI name transformation rules
   - validate output directory writability
   - detect naming collisions
   - emit `validate-config-result.json`
2. Implement component discovery:
   - inventory `SKILL.md`, `refs/`, `rules/`, `templates/`, `scripts/`, matching commands
   - count lines per component
   - emit `component-inventory.md` with required frontmatter
3. Add timing instrumentation for both steps.
4. Add unit tests for:
   - invalid workflow path
   - missing `SKILL.md`
   - name collision
   - unwritable output directory
   - empty or sparse workflow structures
   - timing compliance assertions where feasible

### Milestones
- **M1.1**: `validate-config` passes all path and naming tests
- **M1.2**: `discover-components` produces stable inventory artifacts
- **M1.3**: Pure-programmatic timing bounds demonstrated

### Analyzer Concerns
- Name derivation rules can create subtle collisions if normalization is not fully specified.
- Full-file line counting is acceptable initially, but file-size behavior should be bounded or documented.
- This phase is a dependency bottleneck; defects here will invalidate all later phases.

### Risk Mitigation in This Phase
- Add explicit normalization test cases for prefix/suffix stripping and case conversion.
- Fail early on collision ambiguity with actionable error messages.
- Record artifact checksums or structured summaries for debugging reproducibility.

### Exit Criteria
- `validate-config-result.json` emitted on success
- `component-inventory.md` emitted with correct frontmatter
- No Claude subprocess invoked
- Performance targets met:
  - validation <1s
  - discovery <5s

### Timeline Estimate
- **2-3 days**

---

## Phase 2: Workflow Interpretation and Pipeline Design

Covers:
- **FR-003 Workflow Analysis**
- **FR-004 Pipeline Design**

### Goals
Transform discovered workflow assets into a code-ready execution design with strict structural validation.

### Key Activities
1. Implement workflow analysis prompt and execution wrapper.
2. Generate `portify-analysis.md` with required sections:
   - Source Components
   - Step Graph
   - Gates Summary
   - Data Flow Diagram
   - Classification Summary
3. Build strict gate validation for output completeness and line-count constraints.
4. Implement pipeline design step producing `portify-spec.md`.
5. Ensure design includes:
   - step graph
   - domain models
   - prompt builder specifications
   - gate criteria with semantic checks
   - synchronous executor loop
   - Click integration plan
6. Implement user review gate after design.
7. Ensure `--dry-run` halts here with valid contract output.

### Milestones
- **M2.1**: Analysis output passes structural gate checks
- **M2.2**: Design spec is implementation-ready and synchronous-only
- **M2.3**: Review gate and `--dry-run` behavior validated

### Analyzer Concerns
- This phase has the highest risk of semantic incompleteness hidden behind structurally valid markdown.
- Overly broad prompts may produce verbose outputs that exceed intended limits or dilute step boundaries.
- If Python is not the sole controller of next-step flow, NFR-006 will be violated early.

### Risk Mitigation in This Phase
1. Keep prompts constrained to required sections and bounded output.
2. Add semantic gate checks beyond heading presence:
   - detect missing step classifications
   - detect missing dependency mapping
   - detect missing gate summaries
3. Explicitly reject async design patterns in generated design content.
4. Validate review-stop behavior with both accept and reject paths.

### Exit Criteria
- `portify-analysis.md` passes STRICT gate
- `portify-spec.md` passes STRICT gate
- `--dry-run` returns correctly after Phase 2
- User review gate behavior verified

### Timeline Estimate
- **3-4 days**

---

## Phase 3: Spec Synthesis and Gap Analysis

Covers:
- **FR-005 Spec Synthesis**
- **FR-006 Brainstorm Gap Analysis**

### Goals
Generate the release-ready spec from prior artifacts, then stress it through gap discovery and controlled incorporation.

### Key Activities
1. Implement release spec synthesis from template.
2. Populate all required frontmatter and sections using referenced artifacts via `@path`.
3. Enforce placeholder elimination:
   - zero `{{SC_PLACEHOLDER:*}}` tokens
4. Enforce FR consolidation mapping and 7 functional requirements.
5. Implement retry behavior that reports exact unresolved placeholders.
6. Implement brainstorm gap analysis step:
   - pre-flight skill availability check
   - invoke `/sc:brainstorm`
   - parse structured findings into `{gap_id, description, severity, affected_section, persona}`
   - incorporate actionable items as `[INCORPORATED]`
   - route unresolved items to Section 11 as `[OPEN]`
   - append Section 12 summary
7. Validate zero-gap path as acceptable.

### Milestones
- **M3.1**: Synthesized release spec contains no placeholders
- **M3.2**: Gap analysis works for both findings-present and zero-gap cases
- **M3.3**: Phase 3 timing observable and within advisory target

### Analyzer Concerns
- Placeholder leakage is a high-signal failure and must remain a hard stop.
- Brainstorm output variability can break post-processing unless structural fallback logic is defined.
- Incorporation rules must be additive and traceable, or review quality will degrade in Phase 4.

### Risk Mitigation in This Phase
1. Make placeholder detection exact and comprehensive.
2. Use structural parsing with fallback heuristics for brainstorm output.
3. Log raw and normalized findings separately for auditability.
4. Validate that Section 12 contains content, not only a heading.
5. Preserve provenance of incorporated changes.

### Exit Criteria
- `portify-release-spec.md` passes STRICT gate
- Brainstorm findings are normalized or zero-gap is declared correctly
- Section 11/12 semantics validated
- Phase 3 timing captured

### Timeline Estimate
- **3-4 days**

---

## Phase 4: Panel Review and Convergence Control

Covers:
- **FR-007 Panel Review with Convergence**

### Goals
Run spec-panel review iteratively under Python control until convergence or escalation, with robust boundary handling and review gating.

### Key Activities
1. Implement panel review subprocess orchestration.
2. Add pre-flight skill availability checks.
3. Implement convergence loop with:
   - max iterations default 3
   - per-iteration timeout default 300s
   - TurnLedger budget guard
4. Parse and validate machine-readable convergence block in `panel-report.md`.
5. Calculate quality scores:
   - clarity
   - completeness
   - testability
   - consistency
   - overall = arithmetic mean
6. Implement downstream readiness rule:
   - `overall >= 7.0` is true
   - `6.9` is false
7. Ensure each iteration runs focus and critique in one subprocess.
8. Enforce additive-only changes to the spec.
9. Add final user review gate.

### Milestones
- **M4.1**: Convergence logic terminates correctly for CONVERGED and ESCALATED paths
- **M4.2**: Quality score arithmetic and readiness threshold validated
- **M4.3**: Final review gate behavior verified

### Analyzer Concerns
- This is the highest logic-risk phase due to loop control, parsing ambiguity, and multiple terminal states.
- Marker-format variability from `/sc:spec-panel` is a known fragility.
- Incorrect mode mapping across iterations is a critical regression risk.

### Risk Mitigation in This Phase
1. Treat convergence parsing as defensive but deterministic:
   - exact marker parsing first
   - structural fallback second
   - failure contract if neither succeeds
2. Add tests for:
   - converged first iteration
   - converged later iteration
   - escalated after max iterations
   - timeout per iteration
   - malformed panel output
3. Validate additive-only mutations by comparing pre/post content segments.
4. Test readiness threshold at 7.0 and 6.9 explicitly.

### Exit Criteria
- `panel-report.md` includes machine-readable convergence block
- Convergence loop produces valid terminal state
- Overall score math passes tolerance constraint
- User review gate works for continue/reject flows
- Phase 4 timing captured

### Timeline Estimate
- **4-5 days**

---

## Phase 5: Integration, Resume, Diagnostics, and Hardening

### Goals
Stabilize cross-phase behavior, ensure resumability and observability, and prove compliance against success criteria.

### Key Activities
1. Implement or finalize:
   - resume command generation
   - resumable failure contracts
   - monitor/diagnostic output
   - JSONL + Markdown dual logging
2. Define NDJSON/domain signal vocabulary for monitor behavior.
3. Finalize failure classification for:
   - config failures
   - missing skills
   - timeout
   - gate failure
   - user rejection
   - malformed artifact
4. Add integration tests for:
   - end-to-end non-trivial workflow
   - dry-run path
   - skill unavailability fallback
   - review rejection
   - resume from halted step
5. Verify architectural constraints:
   - no `async def`
   - no `await`
   - no `pipeline/` or `sprint/` modifications
6. Run full unit and integration suites.

### Milestones
- **M5.1**: Resume and failure contracts validated
- **M5.2**: Diagnostics and logging complete
- **M5.3**: Full test suite passes
- **M5.4**: Release readiness confirmed

### Analyzer Concerns
- Resume semantics are currently under-specified for partial artifact writes.
- Failure path completeness is a common source of latent defects.
- Monitoring without a defined event schema reduces debugging value.

### Risk Mitigation in This Phase
1. Choose and document explicit resume semantics:
   - recommended: re-run the failed step if output integrity is uncertain
2. Standardize event types and payload schemas.
3. Add contract validation on every terminal path.
4. Use `git diff` checks to enforce base-module immutability.

### Exit Criteria
- All success criteria validated
- 17 unit tests passing
- 5 integration tests passing
- No async usage
- No forbidden module modifications

### Timeline Estimate
- **3-4 days**

---

## 3. Risk Assessment and Mitigation Strategies

## High-Priority Risks

### 1. Output truncation in Claude-assisted steps
- **Severity**: High
- **Affected phases**: 2, 3, 4
- **Impact**: Incomplete artifacts, false gate outcomes, malformed downstream inputs
- **Mitigation**:
  1. Use `@path` references instead of large inline context.
  2. Constrain prompts to required sections.
  3. Add artifact completeness gates before downstream execution.

### 2. Panel convergence misbehavior
- **Severity**: High
- **Affected phases**: 4
- **Impact**: incorrect readiness state, infinite/incorrect looping, false escalation
- **Mitigation**:
  1. Python-controlled convergence only.
  2. Explicit iteration limits and timeout handling.
  3. Boundary tests for marker parsing and score thresholding.

### 3. Skill invocation failure
- **Severity**: High
- **Affected phases**: 3, 4
- **Impact**: blocked pipeline, inconsistent fallback behavior
- **Mitigation**:
  1. Pre-flight checks for `claude` binary and skill availability.
  2. Inline fallback strategy with explicit terminal contracts.
  3. Integration tests simulating unavailable skills.

### 4. Architectural drift from synchronous-only design
- **Severity**: High
- **Affected phases**: all
- **Impact**: NFR violation, inconsistent executor behavior
- **Mitigation**:
  1. Code review rule: no `async def`, no `await`.
  2. Static search enforced in validation.
  3. Design-phase rejection of async patterns.

## Medium-Priority Risks

### 5. Incomplete machine-readable output from reused skills
- **Severity**: Medium-High
- **Mitigation**:
  - post-process structurally
  - define fallback parsing rules
  - fail explicitly when structural minimums are unmet

### 6. User review gate UX ambiguity
- **Severity**: Medium
- **Mitigation**:
  - standardize prompt content
  - show summary + artifact path + expected response
  - define reject behavior clearly

### 7. Resume behavior ambiguity after partial writes
- **Severity**: Medium
- **Mitigation**:
  - define idempotency rules per step
  - prefer re-running failed synthesis/review steps when artifact trust is uncertain

### 8. File access scope issues for `@path`
- **Severity**: Medium
- **Mitigation**:
  - always pass `--add-dir` for work and workflow directories
  - integration test for out-of-scope path failures

## Low-Priority Risks

### 9. Self-portification circularity
- **Severity**: Low
- **Mitigation**:
  - keep source workflow read-only during execution
  - isolate generated outputs

---

## 4. Resource Requirements and Dependencies

## Engineering Resources

### Recommended Roles
1. **Lead backend/CLI engineer**
   - executor, contracts, Click integration, file/process orchestration
2. **QA/validation engineer**
   - gate tests, boundary tests, integration coverage, resume/failure matrices
3. **Documentation/release engineer**
   - artifact schema review, template validation, user review flow clarity

### Estimated Effort Profile
- **High effort areas**:
  - convergence loop
  - gate semantics
  - failure/resume contracts
  - subprocess integration
- **Moderate effort areas**:
  - pure-programmatic steps
  - logging/monitoring
  - Click command registration

## Technical Dependencies

### Internal
1. `pipeline.models`
2. `pipeline.gates`
3. `pipeline.process`
4. `sprint.models`
5. `sprint.process`
6. release spec template

### External
1. Click >= 8.0.0
2. Rich >= 13.0.0
3. PyYAML
4. `claude` CLI binary
5. `/sc:brainstorm` skill
6. `/sc:spec-panel` skill

## Dependency Management Recommendations
1. Validate all required internal symbols before implementation lock-in.
2. Confirm template path stability early.
3. Verify subprocess argument propagation, especially `--model` and `--add-dir`.
4. Add smoke tests for skill invocation before full pipeline tests.

---

## 5. Success Criteria and Validation Approach

## Success Criteria Coverage Plan

### Functional Validation
1. Confirm end-to-end completion for a non-trivial workflow.
2. Confirm dry-run halts after Phase 2 with valid contract.
3. Confirm each of the 7 steps emits expected artifacts.
4. Confirm skill reuse instead of behavioral reimplementation.

### Non-Functional Validation
1. Confirm synchronous-only execution.
2. Confirm all gates return `tuple[bool, str]`.
3. Confirm runner-authored truth governs status.
4. Confirm deterministic sequencing in Python.
5. Confirm additive-only review updates.
6. Confirm no modifications to `pipeline/` or `sprint/`.

## Validation Methods

### Automated
1. **Unit tests**
   - target all gate functions
   - validate timing logic
   - validate score math
   - validate name normalization
   - validate failure default population
2. **Integration tests**
   - end-to-end happy path
   - dry-run path
   - convergence/escalation path
   - skill unavailability
   - review rejection/resume path
3. **Static verification**
   - search for `async def` and `await`
   - verify module placement
   - verify forbidden-directory immutability via `git diff`

### Manual/Review Gates
1. Review `portify-spec.md` after Phase 2
2. Review final spec and panel report after Phase 4
3. Confirm artifact readability and traceability for operators

## Recommended Validation Sequence
1. Contract and gate unit tests first
2. Pure-programmatic step tests second
3. Claude-assisted artifact structural validation third
4. Convergence and failure-path tests fourth
5. End-to-end workflow certification last

---

## 6. Timeline Estimates Per Phase

| Phase | Scope | Estimate | Primary Risk Driver |
|---|---|---:|---|
| Phase 0 | Foundation, contracts, test scaffolding | 1-2 days | contract ambiguity |
| Phase 1 | Config validation + component discovery | 2-3 days | path/name edge cases |
| Phase 2 | Workflow analysis + pipeline design | 3-4 days | semantic completeness |
| Phase 3 | Spec synthesis + brainstorm gaps | 3-4 days | placeholder leakage, parsing variability |
| Phase 4 | Panel review + convergence | 4-5 days | loop control, marker parsing |
| Phase 5 | Integration, resume, diagnostics, hardening | 3-4 days | failure-path completeness |

### Total Estimated Delivery Window
- **13-18 working days**

### Recommended Milestone Checkpoints
1. **Checkpoint A**: End of Phase 1
   - deterministic foundations proven
2. **Checkpoint B**: End of Phase 2
   - dry-run and review gate validated
3. **Checkpoint C**: End of Phase 3
   - synthesis quality and gap incorporation stable
4. **Checkpoint D**: End of Phase 4
   - convergence and readiness logic proven
5. **Checkpoint E**: End of Phase 5
   - release certification against all success criteria

---

## Analyzer Recommendations

1. **Do not begin with subprocess orchestration.** Start with contracts, gates, and pure-programmatic steps.
2. **Promote convergence logic to a top-tier test target.** It is the highest systemic risk.
3. **Resolve open questions before late integration**, especially:
   - resume semantics after partial writes
   - monitoring signal vocabulary
   - score display vs comparison precision
   - model override propagation
4. **Treat failure contracts as part of core functionality.** They are required for trustworthy automation.
5. **Use artifact-based truth only.** Never let model narrative determine status.
6. **Keep review modifications auditable and additive.** This preserves traceability and prevents silent regressions.

## Final Readiness Definition

The project should be considered roadmap-complete only when it can:
1. port a non-trivial workflow end-to-end,
2. stop safely at review gates,
3. resume predictably after recoverable failures,
4. converge or escalate deterministically in panel review,
5. pass all explicit success criteria without violating architectural constraints.
