---
spec_source: SC-ROADMAP-V2-SPEC.md
complexity_score: 0.82
primary_persona: analyst
---

# 1. Executive Summary

This roadmap delivers a v2.0 `sc:roadmap` capability that generates a deterministic, schema-stable roadmap pipeline for single-spec, multi-spec, and multi-roadmap workflows. The implementation scope is substantial: 58 total requirements across 7 technical domains, 9 identified risks, 8 dependencies, and 30 measurable success criteria.

From an analyst perspective, the dominant concerns are not basic generation mechanics, but orchestration correctness, schema integrity, failure handling, and controlled degradation under partial or unavailable dependencies. The highest-value outcome is a reliable 5-wave execution pipeline that produces exactly three machine-parseable artifacts, integrates adversarial workflows safely, preserves resumability, and validates output quality without introducing downstream coupling.

## Strategic Recommendations
1. **Prioritize contract stability first**:
   - Frontmatter schemas and artifact sequencing are downstream dependencies.
   - Freeze these early and test them before expanding feature breadth.

2. **Implement wave orchestration before optimization**:
   - Correct sequencing, state persistence, and gate behavior are higher risk than speed.
   - NFR latency goals should be addressed after functional correctness.

3. **Treat adversarial integration as a bounded subsystem**:
   - All `sc:adversarial` interactions should be wrapped in explicit contract handling.
   - Partial results must never silently degrade output quality.

4. **Build validation and resume logic as first-class capabilities**:
   - These are not enhancements; they are core controls against stale, partial, or low-trust outputs.

5. **Resolve open questions early where they affect interfaces**:
   - Model identifier validation, plugin template tier behavior, orchestrator behavior, and chunked extraction edge cases are design blockers.

## Target Outcome
A production-ready roadmap generator with:
- deterministic artifact generation,
- stable YAML contracts,
- conditional adversarial routing,
- compliance-aware behavior,
- resumable multi-wave execution,
- evidence-based validation scoring,
- clear operator feedback at every wave boundary.

---

# 2. Phased Implementation Plan with Milestones

## Phase 0 — Definition, Contract Freeze, and Architecture Baseline
**Goal:** Eliminate ambiguity in interfaces and establish implementation boundaries before coding deeper logic.

### Milestones
1. **M0.1 — Finalize schema contracts**
   - Define final frontmatter schemas for:
     - `roadmap.md`
     - `extraction.md`
     - `test-strategy.md`
   - Validate:
     - exactly-one-of `spec_source` vs `spec_sources`
     - required metadata per artifact
     - version compatibility rules for v2.0+

2. **M0.2 — Freeze wave architecture**
   - Confirm 5-wave execution model:
     - Wave 0: prerequisites
     - Wave 1A: spec consolidation
     - Wave 1B: detection and extraction
     - Wave 2: planning and template selection
     - Wave 3: artifact generation
     - Wave 4: validation
   - Define state transitions and loopback behavior for REVISE.

3. **M0.3 — Resolve design-blocking open questions**
   - Decide behavior for:
     - plugin template tier in v4.x
     - canonical model identifier list
     - orchestrator agent responsibility
     - adversarial return contract fields
     - Serena resume key selection
     - chunked extraction unresolved references
     - low-milestone interleave edge cases
     - dry-run adversarial cost warning behavior

4. **M0.4 — Confirm file layout and ownership**
   - Lock required locations:
     - `src/superclaude/commands/roadmap.md`
     - `src/superclaude/skills/sc-roadmap/SKILL.md`
     - `src/superclaude/skills/sc-roadmap/refs/*`

### Deliverables
- Interface decision record
- Final schema definitions
- Wave state model
- Open-questions resolution log

### Exit Criteria
- No unresolved interface blockers remain.
- Contract tests can be written without speculative assumptions.

---

## Phase 1 — Core Wave Orchestrator and Preconditions
**Goal:** Build the pipeline skeleton that enforces sequencing, prerequisites, collision handling, and state capture.

### Milestones
1. **M1.1 — Wave runner implementation**
   - Implement ordered wave execution engine.
   - Support:
     - conditional Wave 1A
     - mandatory sequencing Wave 3 before test strategy
     - Wave 4 gating
     - REVISE loop control
     - dry-run cutoff at Wave 2

2. **M1.2 — Wave 0 prerequisite validation**
   - Validate:
     - spec file readability
     - output directory writability
     - template directory availability
     - adversarial skill availability when required
     - model identifier validity for `--agents`

3. **M1.3 — Output collision management**
   - Detect existing artifacts in output path.
   - Apply consistent `-N` suffixing strategy across all artifacts.

4. **M1.4 — Progress reporting framework**
   - Emit wave boundary events with:
     - wave number
     - completion status
     - key decisions
     - next wave

5. **M1.5 — Session persistence hooks**
   - Store wave-boundary state via Serena memory or fallback path.
   - Persist:
     - spec source
     - output dir
     - flags
     - last completed wave
     - persona
     - complexity
     - template
     - milestone count
     - adversarial state
     - validation state

### Deliverables
- Orchestrator runner
- Wave 0 validator
- Collision manager
- Progress reporter
- Persistence adapter

### Exit Criteria
- Dry-run can execute Waves 0-2 with structured preview.
- Resume metadata is written at each wave boundary.

---

## Phase 2 — Extraction, Complexity Scoring, and Persona Activation
**Goal:** Produce trustworthy `extraction.md` early and use it as the decision substrate for downstream roadmap generation.

### Milestones
1. **M2.1 — Wave 1B extraction pipeline**
   - Load `refs/extraction-pipeline.md` and `refs/scoring.md`.
   - Parse source spec.
   - Generate requirement inventory, domains, risks, dependencies, success criteria.
   - Write `extraction.md` immediately.

2. **M2.2 — Complexity scoring and classification**
   - Implement weighted scoring model.
   - Output:
     - `complexity_score`
     - `complexity_class`
     - rationale summary

3. **M2.3 — Compliance auto-detection**
   - Apply heuristics for:
     - `strict`
     - `standard`
     - `light`
   - Ensure user override remains authoritative.

4. **M2.4 — Persona resolution**
   - Auto-detect primary persona from extracted content.
   - Support `--persona` override.
   - Propagate persona to model-only adversarial agents where required.

5. **M2.5 — Chunked extraction for large specs**
   - Activate when source exceeds 500 lines.
   - Support:
     - section indexing
     - chunk assembly
     - per-chunk extraction
     - structural merge
     - deduplication
     - cross-reference resolution
     - global ID normalization

6. **M2.6 — Completeness verification for chunked mode**
   - Implement 4-pass verification:
     - source coverage ≥95%
     - anti-hallucination 100%
     - section coverage 100%
     - count reconciliation exact match
   - Permit one retry on failing chunks, then stop with error.

### Deliverables
- Extraction engine
- Scoring engine
- Compliance classifier
- Persona detector
- Chunked extraction subsystem

### Exit Criteria
- `extraction.md` is schema-valid and written deterministically.
- Chunked and single-pass outputs are format-compatible.

---

## Phase 3 — Adversarial Integration and Planning Layer
**Goal:** Safely incorporate multi-spec and multi-roadmap adversarial behaviors without compromising determinism.

### Milestones
1. **M3.1 — Wave 1A multi-spec integration**
   - Invoke `sc:adversarial --compare` for `--specs`.
   - Handle statuses:
     - `success`
     - `partial` with convergence ≥60%
     - `partial` with convergence <60%
     - `failed`
   - Apply divergence warning at convergence <50%.

2. **M3.2 — Wave 2 template discovery**
   - Load `refs/templates.md`.
   - Implement 4-tier search:
     - local
     - user
     - plugin
     - inline
   - Apply compatibility scoring:
     - domain 0.40
     - complexity 0.30
     - type 0.20
     - version 0.10
   - Respect `--template` bypass behavior.

3. **M3.3 — Milestone structure synthesis**
   - Build milestone hierarchy with dependency mapping.
   - Populate frontmatter-ready `milestone_index` metadata.

4. **M3.4 — Multi-roadmap adversarial generation**
   - Invoke `sc:adversarial --source --generate roadmap --agents`.
   - Support agent parsing:
     - `model`
     - `model:persona`
     - `model:persona:"instruction"`
   - Enforce 2-10 agent range.
   - Add orchestrator when agent count ≥5.

5. **M3.5 — Combined mode chaining**
   - Sequence:
     - Wave 1A spec consolidation
     - Wave 1B analysis on unified spec
     - Wave 2 adversarial roadmap planning/generation path

### Deliverables
- Adversarial adapter
- Template selector
- Milestone planner
- Agent parser
- Combined-mode router

### Exit Criteria
- Planning layer can deterministically choose template-based or adversarial generation path.
- Partial adversarial outcomes are explicitly surfaced and handled.

---

## Phase 4 — Artifact Generation and Cross-Artifact Consistency
**Goal:** Generate all required artifacts with correct ordering, traceability, and evidence-backed summaries.

### Milestones
1. **M4.1 — `roadmap.md` generation**
   - Produce YAML frontmatter with:
     - `spec_source` or `spec_sources`
     - `milestone_index`
     - optional `adversarial` block
     - validation fields where applicable
   - Include body sections required by roadmap spec.

2. **M4.2 — Decision Summary section**
   - Add evidence-backed table/section for:
     - Primary Persona
     - Template
     - Milestone Count
     - Adversarial Mode
     - Adversarial Base Variant

3. **M4.3 — `test-strategy.md` generation**
   - Enforce sequencing after roadmap generation.
   - Encode:
     - `validation_philosophy: continuous-parallel`
     - correct `interleave_ratio`
     - `major_issue_policy: stop-and-fix`
   - Ensure milestone references map to real roadmap milestones.

4. **M4.4 — Dry-run preview output**
   - Emit structured preview only.
   - Confirm no artifact writes occur in dry-run mode.

5. **M4.5 — No downstream handoff enforcement**
   - Ensure output messaging remains bounded.
   - Final output should list artifacts and advise review before tasklist generation, with no triggering or coupling.

### Deliverables
- Roadmap generator
- Test strategy generator
- Decision summary builder
- Dry-run preview renderer

### Exit Criteria
- Exactly three artifacts are produced in normal mode.
- Artifact ordering and cross-references are correct.

---

## Phase 5 — Validation, Revision Loop, and Operational Hardening
**Goal:** Ensure generated outputs are scored, revisable, resumable, and robust under failures or degraded dependencies.

### Milestones
1. **M5.1 — Wave 4 validation pipeline**
   - Dispatch:
     - quality-engineer agent
     - self-review agent
   - Aggregate output into:
     - PASS ≥85
     - REVISE 70-84
     - REJECT <70

2. **M5.2 — Test-strategy-specific validation**
   - Verify:
     - interleave ratio aligns to complexity
     - validation milestones map to work milestones
     - continuous-parallel philosophy is explicit
     - stop-and-fix thresholds are defined

3. **M5.3 — Adversarial artifact validation**
   - Reject if required adversarial artifacts are missing.
   - Revise if convergence score is missing.

4. **M5.4 — REVISE loop implementation**
   - Re-run Wave 3 → Wave 4 up to 2 iterations.
   - If still REVISE after 2 loops:
     - accept as `PASS_WITH_WARNINGS`

5. **M5.5 — Circuit breaker and fallback behavior**
   - Sequential unavailable → native reasoning
   - Context7 unavailable → web fallback
   - Serena unavailable → continue without persistence with warning

6. **M5.6 — Resume protocol**
   - Detect matching interrupted session.
   - Compare spec hash.
   - Offer resume when safe; warn on hash mismatch.

### Deliverables
- Validation orchestrator
- Revision loop controller
- Fallback handlers
- Resume detector

### Exit Criteria
- Validation scoring is deterministic and recorded.
- Interrupted sessions can resume safely.
- Fallback behavior does not corrupt outputs or contracts.

---

## Phase 6 — Verification Matrix, Performance Tuning, and Release Readiness
**Goal:** Prove compliance against the success criteria and ensure release-level confidence.

### Milestones
1. **M6.1 — Success-criteria test matrix**
   - Map each SC-001 to SC-030 to one or more tests.
   - Prioritize:
     - contract tests
     - adversarial routing tests
     - chunked extraction tests
     - validation loop tests
     - dry-run tests
     - resume tests

2. **M6.2 — Performance validation**
   - Measure:
     - single-spec completion time
     - overhead by mode
     - latency introduced by validation and persistence

3. **M6.3 — Negative-path testing**
   - Missing skill
   - invalid model identifiers
   - output collisions
   - convergence below threshold
   - stale resume state
   - malformed templates
   - dependency unavailability

4. **M6.4 — Documentation and release packaging**
   - Confirm:
     - command file remains concise
     - SKILL.md ≤500 lines
     - refs directory exactly 5 focused files
     - no algorithm duplication in SKILL.md

### Deliverables
- Test matrix
- Performance report
- Release-readiness checklist
- Final compliance report

### Exit Criteria
- All critical success criteria are demonstrably satisfied.
- Release artifacts and documentation conform to architectural constraints.

---

# 3. Risk Assessment and Mitigation Strategies

## High-Priority Risks

### 1. Schema contract breakage
**Why it matters:** Downstream consumers depend on frontmatter stability.

**Mitigation**
- Freeze schemas in Phase 0.
- Add parser-level contract tests early.
- Block release on frontmatter drift.
- Version additions only; no rename/remove behavior after v2.0.

### 2. Adversarial integration quality degradation
**Why it matters:** Partial results can appear valid while degrading coherence.

**Mitigation**
- Wrap all adversarial calls in strict status handling.
- Enforce convergence thresholds.
- Require artifact presence in validation.
- Surface warnings directly in roadmap metadata where applicable.

### 3. Large-spec extraction failure or hallucinated coverage
**Why it matters:** Extraction is the basis for roadmap quality.

**Mitigation**
- Use chunked extraction above threshold.
- Apply 4-pass completeness verification.
- Retry failing chunks once only.
- Stop on unresolved completeness failure rather than continue with low trust.

### 4. Resume from stale or changed spec
**Why it matters:** Resuming against changed inputs can corrupt traceability.

**Mitigation**
- Hash the source spec at each wave boundary.
- Warn on mismatch before resume.
- Require explicit user confirmation on stale resume paths.

## Medium-Priority Risks

### 5. Open design ambiguities causing rework
**Mitigation**
- Resolve all interface-affecting open questions in Phase 0.
- Track each decision as a contract, not an implementation note.

### 6. Combined mode latency and operational opacity
**Mitigation**
- Emit explicit wave progress reporting.
- Distinguish slow-but-expected from error states.
- Add dry-run preview for planning transparency.

### 7. Template selection inconsistency
**Mitigation**
- Centralize scoring logic.
- Log candidate scores for traceability.
- Add deterministic tie-break rules.

### 8. Missing or unavailable dependencies
**Mitigation**
- Validate early in Wave 0.
- Provide actionable abort messaging.
- Use bounded circuit-breaker fallbacks where allowed.

### 9. Edge-case mismatch in validation milestone interleaving
**Mitigation**
- Define minimum viable interleave behavior for low-milestone plans.
- Add explicit edge-case tests before release.

---

# 4. Resource Requirements and Dependencies

## Engineering Roles
1. **Primary implementation owner**
   - Responsible for orchestrator, state management, and artifact generation.

2. **Validation/test owner**
   - Builds SC-001 to SC-030 verification matrix.
   - Focuses on negative-path and contract tests.

3. **Architecture reviewer**
   - Reviews schema, wave boundaries, and SKILL/refs separation.

4. **Optional documentation owner**
   - Ensures command file, SKILL.md, and refs maintain separation-of-concerns.

## Technical Dependencies
1. **Internal**
   - `sc:adversarial` v1.1.0
   - `sc:save` / `sc:load`
   - future tasklist consumer compatibility
   - future plugin marketplace placeholder integration

2. **External**
   - Serena MCP
   - Sequential MCP
   - Context7 MCP
   - YAML parser support

## Infrastructure/Tooling Needs
- UV-based Python execution and tests
- automated contract test suite
- fixture set for:
  - single-spec inputs
  - multi-spec inputs
  - large specs >500 lines
  - adversarial partial/failure returns
  - collision scenarios
  - stale resume scenarios

## Dependency Planning Recommendations
1. **Treat `sc:adversarial` as a hard prerequisite only for adversarial modes**.
2. **Treat Serena as optional-but-degrading**, not required for base functionality.
3. **Treat YAML parseability as release-blocking**.
4. **Treat future plugin tier as explicit placeholder behavior**, not unimplemented ambiguity.

---

# 5. Success Criteria and Validation Approach

## Validation Strategy
The validation strategy should align directly with the extracted 30 success criteria and use a layered evidence model:

### Layer A — Contract Validation
Validate:
- artifact count = exactly 3
- frontmatter parseability
- required field presence
- mutual exclusivity of `spec_source` / `spec_sources`
- correct validation metadata behavior

### Layer B — Flow Validation
Validate:
- correct wave sequencing
- conditional Wave 1A
- roadmap-before-test-strategy ordering
- REVISE loop behavior
- dry-run cutoff
- no downstream handoff

### Layer C — Dependency and Failure Validation
Validate:
- missing `sc:adversarial`
- invalid model identifiers
- missing artifacts in adversarial modes
- fallback behavior under MCP degradation
- output collision suffixing

### Layer D — Quality Validation
Validate:
- milestone references exist
- interleave ratio matches complexity
- Decision Summary is evidence-backed
- warnings are surfaced when proceeding under partial convergence

## Recommended Success Gate Structure
1. **Gate 1 — Contract complete**
   - All three artifacts parse and match schema.

2. **Gate 2 — Execution correctness**
   - Wave transitions and mode routing are correct.

3. **Gate 3 — Quality trustworthiness**
   - Validation pipeline produces expected status and score behavior.

4. **Gate 4 — Recovery and resilience**
   - Resume, collision, and fallback behaviors function safely.

## Measurable Release Thresholds
- 100% pass on schema contract tests
- 100% pass on critical adversarial routing tests
- 100% pass on chunked extraction verification tests
- 100% pass on resume/collision safety tests
- single-spec standard mode within NFR target
- no unresolved blocker among open interface questions

---

# 6. Timeline Estimates Per Phase

Given the complexity score of **0.82 (complex)** and the number of cross-cutting concerns, implementation should be planned in controlled phases with explicit review gates.

## Estimated Phase Durations

### Phase 0 — Definition, Contract Freeze, and Architecture Baseline
**Estimate:** 2-3 days  
**Rationale:** High leverage; resolves blockers before expensive implementation.

### Phase 1 — Core Wave Orchestrator and Preconditions
**Estimate:** 3-4 days  
**Rationale:** Central execution backbone with persistence and progress reporting.

### Phase 2 — Extraction, Complexity Scoring, and Persona Activation
**Estimate:** 4-6 days  
**Rationale:** Includes chunked extraction and 4-pass verification, one of the higher-risk subsystems.

### Phase 3 — Adversarial Integration and Planning Layer
**Estimate:** 3-5 days  
**Rationale:** Depends on external/internal contracts and has several conditional branches.

### Phase 4 — Artifact Generation and Cross-Artifact Consistency
**Estimate:** 2-4 days  
**Rationale:** Moderate complexity, but must preserve schema integrity and ordering guarantees.

### Phase 5 — Validation, Revision Loop, and Operational Hardening
**Estimate:** 3-4 days  
**Rationale:** Validation logic, loop controls, and fallback handling are reliability-critical.

### Phase 6 — Verification Matrix, Performance Tuning, and Release Readiness
**Estimate:** 3-5 days  
**Rationale:** Needed to prove all 30 success criteria and close NFR gaps.

## Total Estimated Delivery Window
**Estimate:** 20-31 working days**

This range assumes:
- one primary engineer,
- no major redesign after Phase 0,
- stable adversarial contract availability,
- normal debugging overhead for complex orchestration logic.

## Schedule Risk Adjustments
Add contingency if any of the following remain unresolved:
1. adversarial return contract not finalized,
2. model validation list remains ambiguous,
3. plugin tier behavior remains unspecified,
4. chunked extraction edge-case semantics remain open.

---

# Recommended Implementation Order of Operations

1. Finalize schemas and unresolved interfaces.
2. Build wave orchestrator and prerequisite checks.
3. Implement extraction and scoring.
4. Add planning/template selection.
5. Integrate adversarial modes.
6. Generate artifacts.
7. Add Wave 4 validation and REVISE loops.
8. Harden resume/fallback/collision handling.
9. Run full success-criteria verification matrix.
10. Release only after contract and negative-path confidence is high.

---

# Analyst Conclusion

This is a **high-complexity orchestration feature**, not merely a content-generation enhancement. The roadmap should therefore optimize for **correctness, traceability, controlled failure, and schema durability** over raw speed or breadth-first implementation. The most important recommendation is to **front-load contract decisions and validation scaffolding** so that later phases produce predictable, testable outputs rather than compounding ambiguity.
