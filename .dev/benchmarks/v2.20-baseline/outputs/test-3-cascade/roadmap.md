

---
spec_source: SC-ROADMAP-V2-SPEC.md
complexity_score: 0.82
adversarial: true
---

# SC:ROADMAP v2.0 — Final Merged Roadmap

## Executive Summary

This roadmap delivers `sc:roadmap` v2.0: a 5-wave roadmap generation pipeline with adversarial integration, chunked extraction, template discovery, compliance tiering, and session persistence. The system produces 3 artifacts (`roadmap.md`, `extraction.md`, `test-strategy.md`) from specification documents, with optional multi-spec consolidation and multi-roadmap adversarial generation.

**Complexity**: 0.82 (complex) — driven by multi-mode conditional execution, deep adversarial integration, chunked extraction with 4-pass verification, and session persistence with resume protocol.

**Scope**: 58 requirements (46 functional, 12 non-functional), 7 domains, 8 dependencies, 9+ risks, 30 measurable success criteria.

**Key architectural decisions**:
- Lean SKILL.md (≤500 lines) with 5 refs/ files for algorithms
- On-demand ref loading (max 2-3 at any point) to prevent context bloat
- Versioned frontmatter schema as a contract for downstream consumers, frozen before implementation begins
- Circuit breaker fallbacks for all MCP dependencies
- Explicit wave orchestrator component encapsulating sequencing, state, and mode-aware routing
- 4-layer validation model populated with mode-combination test cases

**Adversarial synthesis**: This roadmap uses Variant A (Opus Architect) as its structural foundation for superior requirement traceability and implementation specificity, enhanced with Variant B (Haiku Analyst) contributions in contract discipline, orchestrator design, and validation methodology.

---

## Phase 0: Contract Freeze & Interface Decisions

**Goal**: Eliminate schema ambiguity and resolve interface-affecting open questions before implementation begins. Condensed from Haiku's 2-3 days to a focused 1-2 day sprint.

**Duration estimate**: 1-2 days

**Rationale**: The debate exposed that the spec defines field names but leaves unresolved: optional vs required semantics per mode, behavior when validation is skipped (absent vs null), mutual exclusivity enforcement rules, and orchestrator agent boundaries. Freezing these prevents individual interpretation from becoming architectural debt.

### Milestone 0.1: Schema Freeze
- Define final frontmatter schemas for all 3 artifacts with field-level required/optional annotations per mode
- Resolve: `spec_source` vs `spec_sources` mutual exclusivity enforcement, validation field behavior when `--no-validate` (fields present with value `SKIPPED`/`0.0`, not absent)
- Produce parseable schema definitions that serve as contract test inputs
- **Validates**: SC-028, FR-002, FR-003, FR-004, NFR-003, NFR-008

### Milestone 0.2: Wave Architecture Freeze
- Confirm 5-wave execution model with state transitions and REVISE loopback behavior
- Define the generation routing abstraction point: where template-based and adversarial paths diverge (strategy pattern interface)
- **Validates**: SC-001, FR-001

### Milestone 0.3: Open Question Resolution
- Resolve all 10 open questions from extraction, producing a decision record:
  1. Plugin tier: no-op stub until v5.0
  2. Model identifiers: hardcode initial list (opus, sonnet, haiku); configurable via refs/
  3. Orchestrator agent: coordination prompt in refs/adversarial-integration.md; does not count toward 2-10 limit
  4. Adversarial return contract: block Phase 4 until SC-ADVERSARIAL-SPEC.md finalized
  5. Serena resume keys: most recent session only, no automatic cleanup
  6. Unresolvable cross-references: informational warnings (non-blocking)
  7. Interleave ratio edge case: floor to minimum 1 validation milestone
  8. Adversarial depth independence: document as note in command file
  9. Template discovery in CI: gracefully skip missing tiers, log availability
  10. Dry run + adversarial cost: console warning before execution
- **Validates**: Phase-blocking decisions for Phases 1-6

### Phase 0 Exit Criteria
1. Interface decision record produced and reviewed
2. Contract tests can be written without speculative assumptions
3. No unresolved interface blockers remain

---

## Phase 1: Foundation & Core Pipeline (Wave 0 + Wave 1B)

**Goal**: Establish the single-spec happy path with an explicit wave orchestrator — from spec input to extraction output.

**Duration estimate**: 3-5 days

### Milestone 1.1: File Structure & Command Skeleton
- Create `src/superclaude/commands/roadmap.md` (~80 lines) with trigger definitions, flag declarations, and behavioral summary
- Create `src/superclaude/skills/sc-roadmap/SKILL.md` skeleton (behavioral instructions only)
- Create `refs/` directory with 5 empty stub files: `extraction-pipeline.md`, `scoring.md`, `validation.md`, `templates.md`, `adversarial-integration.md`
- Validate SKILL.md/command separation: WHEN/WHAT in command, HOW in SKILL.md
- **Validates**: SC-024, SC-025, FR-043

### Milestone 1.2: Wave Orchestrator Component
- Implement ordered wave execution engine as a tightly-scoped, explicit component encapsulating:
  - Conditional Wave 1A activation
  - Mandatory sequencing (roadmap before test-strategy)
  - REVISE loop with iteration counting and termination
  - Dry-run cutoff at Wave 2
  - State persistence hooks at wave boundaries
  - Resume from last completed wave
  - Circuit breaker fallback integration points
  - Mode-aware routing (template vs adversarial generation path)
- Implement progress reporting at wave boundary events (wave number, status, key decisions, next wave)
- **Validates**: SC-001, FR-001, SC-016, SC-017

### Milestone 1.3: Wave 0 — Prerequisites & Validation
- Implement spec file existence/readability check
- Implement output directory writability check with collision detection (append `-N` suffix per FR-015)
- Implement `--dry-run`, `--compliance`, `--depth`, `--persona`, `--output`, `--no-validate` flag parsing
- Implement compliance auto-detection heuristics (FR-039)
- Defer adversarial availability checks and model validation to Phase 4
- **Validates**: SC-011, SC-020, FR-014, FR-015

### Milestone 1.4: Wave 1B — Extraction Pipeline (Single-Pass)
- Author `refs/extraction-pipeline.md` with the full extraction algorithm
- Author `refs/scoring.md` with complexity scoring formula and domain classification
- Implement spec parsing, requirement extraction, complexity scoring, domain classification
- Write `extraction.md` to disk immediately after extraction completes
- Implement `--persona` flag override for auto-detected primary persona
- **Validates**: SC-001 (partial), SC-009, SC-013 (partial), FR-006, FR-018, FR-019, FR-033

### Milestone 1.5: Wave 1B — Chunked Extraction
- Implement 500-line threshold detection and automatic activation
- Implement section indexing, chunk assembly (~400 lines, max 600), per-chunk extraction with global ID counters
- Implement structural merge and deduplication (ID collision, normalized match, substring >0.8)
- Implement cross-reference resolution with warning logging
- Implement 4-pass completeness verification (Source Coverage ≥95%, Anti-Hallucination 100%, Section Coverage 100%, Count Reconciliation exact match)
- Implement single retry on verification failure, then STOP with error
- **Validates**: SC-018, FR-034, FR-035, NFR-012

### Phase 1 Exit Criteria
1. Single-spec invocation produces valid `extraction.md` with parseable YAML frontmatter conforming to Phase 0 schema
2. Chunked extraction activates for specs >500 lines and passes 4-pass verification
3. Output collision detection appends `-N` suffix correctly
4. Compliance auto-detection returns correct tier for keyword-laden specs, large specs, and small specs
5. SKILL.md ≤500 lines, refs/ contains exactly 5 files
6. Wave orchestrator executes Waves 0-1B with progress reporting and state persistence

---

## Phase 2: Template System & Roadmap Generation (Wave 2 + Wave 3)

**Goal**: Complete the single-spec pipeline end-to-end with an explicit generation routing abstraction point.

**Duration estimate**: 3-5 days

### Milestone 2.1: Wave 2 — Template Discovery & Selection
- Author `refs/templates.md` with template format specification and compatibility scoring algorithm
- Implement 4-tier template discovery: local (`.dev/templates/roadmap/`) → user (`~/.claude/templates/roadmap/`) → plugin (no-op stub) → inline generation fallback
- Implement compatibility scoring with correct weights: domain (0.40), complexity (0.30), type (0.20), version (0.10)
- Implement ≥0.6 threshold; below threshold triggers inline generation
- Implement `--template` flag to skip scoring
- Log candidate scores for traceability; implement deterministic tie-break rules
- **Validates**: SC-022, SC-023, FR-020, FR-040, FR-041, NFR-009

### Milestone 2.2: Generation Routing Abstraction
- Implement the strategy pattern interface defined in Phase 0 M0.2: generation path accepts extraction output and produces roadmap content
- Template-based generation is the default strategy; adversarial generation strategy is a stub interface prepared for Phase 4
- Create milestone structure and dependency mapping
- This prevents the retrofit identified in the debate ("replacing" language in Opus M4.3)
- **Validates**: Architectural soundness for SC-003, SC-005

### Milestone 2.3: Wave 3 — Roadmap Generation
- Implement `roadmap.md` generation with full YAML frontmatter per Phase 0 schema:
  - `spec_source` (scalar, single-spec mode)
  - `milestone_index` with per-milestone structured metadata
  - `generator`, `generated` (ISO-8601), `complexity_score`, `validation_score`, `validation_status`
- Implement Decision Summary section in roadmap body (Primary Persona, Template, Milestone Count, Adversarial Mode, Base Variant) with evidence citations
- Enforce sequencing: roadmap.md completes before test-strategy.md begins (via wave orchestrator)
- **Validates**: SC-001 (partial), SC-028, SC-030, FR-001, FR-002, FR-003, FR-004, FR-022, FR-023, NFR-003, NFR-004, NFR-008

### Milestone 2.4: Wave 3 — Test Strategy Generation
- Implement `test-strategy.md` generation with YAML frontmatter:
  - `validation_philosophy: continuous-parallel`
  - `interleave_ratio` computed from complexity (LOW→1:3, MEDIUM→1:2, HIGH→1:1)
  - `major_issue_policy: stop-and-fix`
- Ensure every validation milestone references a concrete work milestone from roadmap.md
- Encode continuous parallel validation philosophy in body
- **Validates**: SC-001, SC-029, FR-001, FR-007, FR-028, FR-029

### Milestone 2.5: Dry Run Mode
- Implement `--dry-run` flag: execute Waves 0-2, output structured console preview (spec, complexity, persona, template, milestone structure, domain distribution, estimated counts)
- Ensure no files are written and no validation agents dispatched
- Persistence hooks still fire so resume knows where dry-run stopped
- **Validates**: SC-019, FR-036

### Phase 2 Exit Criteria
1. Single-spec invocation produces all 3 artifacts with valid YAML frontmatter per Phase 0 schema
2. Template discovery searches all 4 tiers with correct scoring weights; scores logged
3. Generation routing abstraction point exists with template strategy active and adversarial stub prepared
4. Interleave ratio computed correctly for all complexity classes, including edge case (minimum 1 validation milestone)
5. `--dry-run` outputs preview without writing files
6. Decision Summary section present with evidence-backed rows
7. No references to tasklist generation or downstream commands in any output (SC-010, FR-030)

---

## Phase 3: Validation Pipeline (Wave 4)

**Goal**: Implement quality gates, REVISE loop, and compliance tier enforcement.

**Duration estimate**: 2-3 days

### Milestone 3.1: Wave 4 — Quality Validation
- Author `refs/validation.md` with validation algorithms, scoring formulas, and agent prompts
- Implement quality-engineer agent dispatch: completeness, consistency, traceability checks
- Implement test-strategy validation: interleave ratio matches complexity class, validation milestones reference real work milestones, continuous parallel philosophy encoded, stop-and-fix thresholds defined
- Implement self-review agent dispatch (4-question protocol)
- Aggregate scores and produce PASS (≥85%) / REVISE (70-84%) / REJECT (<70%)
- **Validates**: SC-006, FR-024, FR-025

### Milestone 3.2: REVISE Loop
- Implement REVISE loop via wave orchestrator: re-run Wave 3 → Wave 4, up to 2 iterations
- REVISE loop respects mode-aware routing (re-runs template or adversarial generation as appropriate)
- After 2 failed iterations, accept with `validation_status: PASS_WITH_WARNINGS`
- Store `validation_score` and `validation_status` in frontmatter
- **Validates**: SC-007, FR-027

### Milestone 3.3: Validation Bypass & Compliance Tiers
- Implement `--no-validate`: skip Wave 4, set `validation_score: 0.0`, `validation_status: SKIPPED`
- Implement `--compliance light`: reduced extraction, inline templates only, skip Wave 4, set `validation_status: LIGHT`
- Implement `--compliance strict`: full extraction + 4-pass verification even <500 lines, all template tiers, full Wave 4
- **Validates**: SC-012, SC-021, FR-038, FR-042

### Phase 3 Exit Criteria
1. Wave 4 produces correct PASS/REVISE/REJECT classification
2. REVISE loop re-runs correctly via orchestrator and terminates after 2 iterations with PASS_WITH_WARNINGS
3. `--no-validate` and `--compliance light` correctly bypass validation
4. `--compliance strict` enforces full pipeline regardless of spec size

---

## Phase 4: Adversarial Integration (Wave 1A + Wave 2 Adversarial)

**Goal**: Enable multi-spec consolidation and multi-roadmap generation via sc:adversarial, plugging into the generation routing abstraction from Phase 2.

**Duration estimate**: 3-5 days

**Dependency**: sc:adversarial v1.1.0 must be installed and functional (DEP-001).

### Milestone 4.1: Adversarial Availability & Agent Validation
- Complete Wave 0 adversarial checks: if `--specs` or `--multi-roadmap` present but sc:adversarial not installed, abort with actionable error
- Implement model identifier validation in Wave 0 for `--agents` flag against frozen model list (Phase 0 decision #2)
- Implement agent spec parsing: split on `,` for list, then `:` per agent (max 3 segments)
- Enforce 2-10 agent count range
- Add orchestrator agent for ≥5 agents (per Phase 0 decision #3: does not count toward limit)
- **Validates**: SC-014, SC-015, FR-011, FR-012, FR-032

### Milestone 4.2: Wave 1A — Multi-Spec Consolidation
- Author `refs/adversarial-integration.md` with adversarial return contract handling and convergence routing
- Implement `--specs spec1.md,spec2.md[,...,specN.md]` flag
- Invoke `sc:adversarial --compare` and handle return contract:
  - `success` → proceed
  - `partial` with convergence ≥60% → proceed with warning
  - `partial` with convergence <60% → prompt user (if `--interactive`) or abort
  - `failed` → abort
- Implement divergent-specs heuristic: warn if convergence <50%
- **Validates**: SC-002, SC-008, FR-008, FR-016, FR-017

### Milestone 4.3: Wave 2 — Multi-Roadmap Adversarial Generation
- Implement the adversarial generation strategy for the routing abstraction defined in Phase 2 M2.2
- Implement `--multi-roadmap --agents <agent-spec>[,...]` flag
- Invoke `sc:adversarial --source --generate roadmap --agents` through the generation strategy interface
- Implement `roadmap.md` frontmatter `adversarial` block (mode, agents, convergence_score, base_variant, artifacts_dir)
- Implement `--depth` flag mapping to adversarial debate rounds (quick=1, standard=2, deep=3)
- Implement `--persona` propagation to model-only agents
- **Validates**: SC-003, SC-005, FR-005, FR-009, FR-021, FR-031

### Milestone 4.4: Combined Mode
- Implement `--specs` + `--multi-roadmap` combined: chain spec consolidation (Wave 1A) then roadmap adversarial generation (Wave 2) sequentially
- Implement `--interactive` propagation to adversarial invocations
- Implement `--dry-run` with adversarial execution and cost warning (Phase 0 decision #10)
- **Validates**: SC-004, SC-005, FR-010, FR-037

### Milestone 4.5: Adversarial Validation in Wave 4
- Implement adversarial artifact checks: missing artifacts when adversarial mode used → REJECT; missing convergence score → REVISE
- Implement frontmatter `spec_sources` (list) for multi-spec mode, with mutual exclusion against `spec_source` per Phase 0 schema
- **Validates**: SC-028, FR-003, FR-026

### Phase 4 Exit Criteria
1. `--specs` invokes sc:adversarial and produces unified spec with correct convergence routing
2. `--multi-roadmap --agents` produces adversarial roadmap with correct frontmatter via generation strategy interface (no template code refactored)
3. Combined mode chains both adversarial passes correctly
4. Wave 4 detects missing adversarial artifacts
5. Agent count enforcement (2-10) and model validation work correctly
6. `--dry-run` executes adversarial invocations with cost warning

---

## Phase 5: Session Persistence & Resumability

**Goal**: Enable cross-session persistence and resume from interrupted runs.

**Duration estimate**: 1-2 days

**Dependency**: Serena MCP server (DEP-003), sc:save/sc:load (DEP-002).

### Milestone 5.1: Session Save Protocol
- Implement sc:save trigger at each wave boundary (integrated with wave orchestrator)
- Store: spec_source, output_dir, flags, last_completed_wave, extraction state, complexity, persona, template, milestone count, adversarial results, validation score
- Implement spec file hash capture for staleness detection
- **Validates**: SC-016, FR-045

### Milestone 5.2: Resume Protocol
- Detect matching Serena memory session (same spec path + output dir)
- Prompt user to resume from last completed wave
- Implement spec file hash comparison; warn if spec changed since last session and require explicit confirmation
- Implement circuit breaker fallback: Serena unavailable → proceed without persistence with user warning
- **Validates**: SC-017, FR-046, NFR-011

### Phase 5 Exit Criteria
1. Session state saved at each wave boundary
2. Resume correctly offered and restores state from the last completed wave
3. Spec hash mismatch produces clear warning with confirmation requirement
4. Graceful degradation when Serena is unavailable

---

## Phase 6: Hardening, Verification & Release Readiness

**Goal**: Address remaining NFRs, edge cases, MCP fallbacks, ref loading discipline, and prove compliance against all success criteria.

**Duration estimate**: 2-3 days

### Milestone 6.1: On-Demand Ref Loading Enforcement
- Verify wave-to-ref mapping matches FR-044 exactly:
  - Wave 0: none
  - Wave 1A: adversarial-integration (if --specs)
  - Wave 1B: extraction-pipeline + scoring
  - Wave 2: templates (+ adversarial-integration if --multi-roadmap)
  - Wave 3: none (uses loaded context)
  - Wave 4: validation
- Verify max 2-3 refs loaded at any point
- Verify every algorithm in refs/ is referenced by name from SKILL.md with no duplication
- **Validates**: SC-026, SC-027, FR-044, NFR-006

### Milestone 6.2: MCP Circuit Breakers
- Implement Sequential fallback: unavailable → native Claude reasoning with reduced depth
- Implement Context7 fallback: unavailable → WebSearch
- Implement Serena fallback: unavailable → proceed without persistence with user warning
- **Validates**: NFR-011

### Milestone 6.3: Schema Stability & NFR Compliance
- Validate SKILL.md ≤500 lines (NFR-002)
- Validate no YAML pseudocode in SKILL.md (NFR-002)
- Validate command file ~80 lines (NFR-007)
- Validate all frontmatter parseable by standard YAML parsers against Phase 0 schema (NFR-008)
- Validate frontmatter schema stability: no removed/renamed fields from v2.0 baseline (NFR-003)
- Validate single-spec completion <2 minutes (NFR-001)
- **Validates**: SC-024, NFR-001, NFR-002, NFR-003, NFR-007, NFR-008

### Milestone 6.4: Edge Case Handling
- Interleave ratio edge case: floor to minimum 1 validation milestone (per Phase 0 decision #7)
- Agent persona inheritance: model-only agents inherit auto-detected primary persona from Wave 1B
- `--persona` propagation to model-only agents in `--agents`
- Empty or near-empty specs: compliance auto-detection routes to LIGHT
- **Validates**: SC-013, FR-011, FR-029, FR-039

### Milestone 6.5: Success Criteria Verification Matrix
- Map each SC-001 through SC-030 to one or more tests organized by validation layer (see Validation Approach below)
- Execute negative-path tests: missing skill, invalid model identifiers, output collisions, convergence below threshold, stale resume state, malformed templates, dependency unavailability
- **Validates**: All SC-* criteria

### Milestone 6.6: Release Readiness Gate
- All release thresholds must pass (see Success Criteria below)
- Confirm all Phase 0 decisions are reflected in implementation
- Confirm documentation conforms to architectural constraints
- **Validates**: Release confidence

### Phase 6 Exit Criteria
1. All NFRs verified
2. Circuit breaker fallbacks tested for all 3 MCP servers
3. Ref loading discipline verified per wave
4. Edge cases handled without errors
5. 100% of SC-* criteria mapped to passing tests
6. Release readiness gate passed

---

## Risk Assessment & Mitigation

### High-Priority Risks

**RISK-001: Schema contract breakage** (Probability: Medium, Impact: High)
Downstream consumers depend on frontmatter stability. Frontmatter field semantics (optional vs required per mode, null vs absent) can drift if not frozen early.
- **Mitigation**: Freeze schemas in Phase 0. Add parser-level contract tests as Phase 0 deliverables. Block release on frontmatter drift. Enforce additions-only policy after v2.0 (NFR-003).
- **Phase**: 0, 6

**RISK-002: sc:adversarial unavailable** (Probability: Low, Impact: High)
External dependency blocks all adversarial functionality.
- **Mitigation**: Wave 0 detection with actionable install instructions; abort early. Phases 1-3 and 5-6 deliver a fully functional single-spec pipeline without adversarial.
- **Phase**: 4

**RISK-003: Large-spec extraction failure or hallucinated coverage** (Probability: Medium, Impact: High)
Extraction is the basis for roadmap quality. Chunked extraction introduces merge complexity.
- **Mitigation**: 4-pass completeness verification with strict thresholds. Retry failing chunks once only. STOP with error on unresolved completeness failure rather than continue with low trust.
- **Phase**: 1

**RISK-004: Resume from stale or changed spec** (Probability: Low, Impact: Medium)
Resuming against changed inputs can corrupt traceability.
- **Mitigation**: Hash source spec at each wave boundary. Warn on mismatch. Require explicit user confirmation on stale resume paths.
- **Phase**: 5

### Medium-Priority Risks

| Risk | Probability | Impact | Mitigation | Phase |
|------|------------|--------|------------|-------|
| RISK-005: Multi-spec produces incoherent unified spec | Medium | Medium | Convergence-based routing (<60% abort/prompt); divergent-specs heuristic at <50% | 4 |
| RISK-006: Adversarial partial status causes silent degradation | Medium | Medium | Explicit convergence thresholds with routing decisions (≥60%/<60%); validation rejects missing artifacts | 4 |
| RISK-007: Combined mode too slow | Medium | Low | Progress reporting at wave boundaries; no hard time constraints for adversarial modes; dry-run cost warning | 4 |
| RISK-008: Interrupted session produces stale artifacts | Low | Medium | sc:save at wave boundaries; resume protocol with hash-based staleness detection | 5 |
| RISK-009: Unrecognized model in --agents | Low | Medium | Wave 0 validates all model identifiers against frozen list before execution starts | 4 |
| RISK-010: SKILL.md exceeds 500 lines during implementation | Medium | Medium | Track line count during each phase; refactor aggressively into refs/ | All |
| RISK-011: Template scoring produces unexpected inline fallback too frequently | Medium | Low | Provide well-scored default templates; log scoring decisions for debugging; deterministic tie-break | 2 |
| RISK-012: REVISE loop creates infinite-feeling UX | Low | Low | Hard cap at 2 iterations with PASS_WITH_WARNINGS; progress reporting during loop | 3 |
| RISK-013: Wave orchestrator interaction complexity | Medium | Medium | 7 behavioral concerns (conditional activation, sequencing, REVISE, dry-run, persistence, resume, circuit breakers) interact non-trivially; explicit component with isolated tests prevents implicit ordering bugs | 1 |

---

## Resource Requirements & Dependencies

### Engineering Roles
1. **Primary implementation owner** — Orchestrator, state management, artifact generation
2. **Validation/test owner** — SC-001 to SC-030 verification matrix, negative-path and contract tests
3. **Architecture reviewer** — Schema decisions, wave boundaries, SKILL/refs separation, generation routing abstraction
4. **Documentation owner** (optional) — Command file, SKILL.md, refs separation-of-concerns compliance

### Internal Dependencies
1. **sc:adversarial v1.1.0** (DEP-001) — Required for Phase 4. Must support `--compare`, `--source --generate roadmap --agents`, return contract with status/convergence_score/artifacts_dir. **Risk**: If not finalized, Phase 4 is blocked; Phases 1-3, 5, and 6 (excluding M4.5) deliver a functional single-spec pipeline.
2. **sc:save / sc:load** (DEP-002) — Required for Phase 5. Must support key-value persistence and retrieval.
3. **Downstream tasklist generator** (DEP-007) — Not a blocker. sc:roadmap defines the frontmatter contract; the consumer builds against it later.
4. **v5.0 plugin marketplace** (DEP-008) — Not a blocker. Template discovery tier 3 is a no-op stub.

### External Dependencies
1. **Serena MCP** (DEP-003) — Phase 5. Circuit breaker fallback available.
2. **Sequential MCP** (DEP-004) — Phases 1-3. Circuit breaker fallback to native reasoning.
3. **Context7 MCP** (DEP-005) — Phases 1-2. Circuit breaker fallback to WebSearch.
4. **Standard YAML parser** (DEP-006) — All phases. No risk; widely available.

### Critical Path
```
Phase 0 (Contracts) → Phase 1 (Foundation) → Phase 2 (Generation) → Phase 3 (Validation) → Phase 6 (Hardening)
                                                                                            ↗
                                                              Phase 4 (Adversarial) --------
                                                              Phase 5 (Persistence) --------
```

Phases 4 and 5 can proceed in parallel with each other after Phase 2, with Phase 4's adversarial validation milestone (4.5) depending on Phase 3. Phase 6 is the final integration and hardening phase requiring all prior phases.

---

## Success Criteria & Validation Approach

### 4-Layer Validation Model

Validation is organized in progressive layers to ensure coverage completeness. Each layer builds confidence before the next is meaningful.

#### Layer A — Contract Validation
- Artifact count = exactly 3
- Frontmatter parseability by standard YAML parser
- Required field presence per Phase 0 schema
- Mutual exclusivity of `spec_source` / `spec_sources`
- Validation metadata behavior per mode (`SKIPPED`/`0.0` when bypassed, not absent)
- **Validates**: SC-028, FR-002, FR-003, FR-004, NFR-008

#### Layer B — Flow Validation
- Correct wave sequencing (0 → 1A/1B → 2 → 3 → 4)
- Conditional Wave 1A activation only when `--specs` present
- Roadmap-before-test-strategy ordering enforced
- REVISE loop behavior (2 iterations max, then PASS_WITH_WARNINGS)
- Dry-run cutoff at Wave 2 with no file writes
- No downstream handoff language in outputs
- **Validates**: SC-001, SC-007, SC-010, SC-019, FR-001, FR-027, FR-030, FR-036

#### Layer C — Dependency & Failure Validation
- Missing `sc:adversarial` → actionable abort
- Invalid model identifiers → Wave 0 rejection
- Missing artifacts in adversarial modes → REJECT
- Fallback behavior under MCP degradation (Sequential, Context7, Serena)
- Output collision suffixing
- Stale resume detection and warning
- **Validates**: SC-014, SC-017, FR-012, FR-015, FR-046, NFR-011

#### Layer D — Quality & Mode-Combination Validation
End-to-end test matrix covering all user-facing modes:
- Single-spec (simple, medium, complex specs)
- Single-spec with `--dry-run`
- Single-spec with `--compliance light` and `--compliance strict`
- Multi-spec with 2-3 specs at varying convergence levels
- Multi-roadmap with 2, 5, and 10 agents
- Combined mode (`--specs` + `--multi-roadmap`)
- Resume from interrupted session
- Chunked extraction with >500-line spec

Additional quality checks:
- Milestone references exist in test strategy
- Interleave ratio matches complexity class
- Decision Summary is evidence-backed
- Warnings surfaced when proceeding under partial convergence
- **Validates**: SC-002, SC-003, SC-004, SC-006, SC-012, SC-018, SC-021, FR-008, FR-009, FR-010, FR-024, FR-025, FR-034, FR-038, FR-042

### Release Readiness Gate
- 100% pass on Layer A (schema contract tests)
- 100% pass on Layer B (critical flow tests)
- 100% pass on Layer C (adversarial routing and failure tests)
- 100% pass on Layer D critical paths (single-spec all compliance tiers, chunked extraction, resume/collision safety)
- Single-spec standard mode within NFR target (<2 minutes)
- SKILL.md ≤500 lines, command file ~80 lines, refs/ exactly 5 files
- No unresolved blocker among Phase 0 interface decisions

---

## Timeline Summary

| Phase | Duration | Dependencies | Parallelizable |
|-------|----------|-------------|----------------|
| Phase 0: Contracts | 1-2 days | None | No (baseline) |
| Phase 1: Foundation | 3-5 days | Phase 0 | No (sequential) |
| Phase 2: Generation | 3-5 days | Phase 1 | No (sequential) |
| Phase 3: Validation | 2-3 days | Phase 2 | No (sequential) |
| Phase 4: Adversarial | 3-5 days | Phase 2 + sc:adversarial v1.1.0 | Yes (parallel with Phase 5) |
| Phase 5: Persistence | 1-2 days | Phase 2 + Serena MCP | Yes (parallel with Phase 4) |
| Phase 6: Hardening | 2-3 days | Phases 3, 4, 5 | No (final integration) |

**Critical path (single-spec only)**: Phase 0 → 1 → 2 → 3 → 6 = **11-18 days**

**Full feature set (single engineer, sequential)**: Phase 0 → 1 → 2 → 3 → 4 → 5 → 6 = **15-25 days**

**Full feature set (parallel Phases 4+5)**: **13-22 days**

If Phase 4 is blocked by sc:adversarial v1.1.0 unavailability, Phases 0-3 and 5-6 deliver a fully functional single-spec pipeline in **12-20 days**.

### Schedule Risk Adjustments
Add contingency if any of the following remain unresolved past Phase 0:
1. Adversarial return contract not finalized
2. Model validation list remains ambiguous
3. Plugin tier behavior remains unspecified
4. Chunked extraction edge-case semantics remain open
