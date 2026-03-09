

---
spec_source: SC-ROADMAP-V2-SPEC.md
complexity_score: 0.82
primary_persona: architect
---

# SC:ROADMAP v2.0 — Implementation Roadmap

## Executive Summary

This roadmap covers the implementation of `sc:roadmap` v2.0, a 5-wave roadmap generation pipeline with adversarial integration, chunked extraction, template discovery, compliance tiering, and session persistence. The system produces 3 artifacts (`roadmap.md`, `extraction.md`, `test-strategy.md`) from specification documents, with optional multi-spec consolidation and multi-roadmap adversarial generation.

**Complexity**: 0.82 (complex) — driven by multi-mode conditional execution, deep adversarial integration, chunked extraction with 4-pass verification, and session persistence with resume protocol.

**Scope**: 58 requirements (46 functional, 12 non-functional), 7 domains, 8 dependencies, 9 risks.

**Key architectural decisions**:
- Lean SKILL.md (≤500 lines) with 5 refs/ files for algorithms
- On-demand ref loading (max 2-3 at any point) to prevent context bloat
- Versioned frontmatter schema as a contract for downstream consumers
- Circuit breaker fallbacks for all MCP dependencies

---

## Phase 1: Foundation & Core Pipeline (Wave 0 + Wave 1B)

**Goal**: Establish the single-spec happy path — from spec input to extraction output.

**Duration estimate**: 3-5 days

### Milestone 1.1: File Structure & Command Skeleton
- Create `src/superclaude/commands/roadmap.md` (~80 lines) with trigger definitions, flag declarations, and behavioral summary
- Create `src/superclaude/skills/sc-roadmap/SKILL.md` skeleton (behavioral instructions only)
- Create `refs/` directory with 5 empty stub files: `extraction-pipeline.md`, `scoring.md`, `validation.md`, `templates.md`, `adversarial-integration.md`
- Validate SKILL.md/command separation: WHEN/WHAT in command, HOW in SKILL.md
- **Validates**: SC-024, SC-025, FR-043

### Milestone 1.2: Wave 0 — Prerequisites & Validation
- Implement spec file existence/readability check
- Implement output directory writability check with collision detection (append `-N` suffix per FR-015)
- Implement `--dry-run`, `--compliance`, `--depth`, `--persona`, `--output`, `--no-validate` flag parsing
- Implement compliance auto-detection heuristics (FR-039)
- Defer adversarial availability checks and model validation to Phase 4
- **Validates**: SC-011, SC-020, FR-014, FR-015

### Milestone 1.3: Wave 1B — Extraction Pipeline (Single-Pass)
- Author `refs/extraction-pipeline.md` with the full extraction algorithm
- Author `refs/scoring.md` with complexity scoring formula and domain classification
- Implement spec parsing, requirement extraction, complexity scoring, domain classification
- Write `extraction.md` to disk immediately after extraction completes
- Implement `--persona` flag override for auto-detected primary persona
- Emit progress reporting at Wave 0→1B and 1B→2 boundaries
- **Validates**: SC-001 (partial), SC-009, SC-013 (partial), FR-006, FR-018, FR-019, FR-033

### Milestone 1.4: Wave 1B — Chunked Extraction
- Implement 500-line threshold detection and automatic activation
- Implement section indexing, chunk assembly (~400 lines, max 600), per-chunk extraction with global ID counters
- Implement structural merge and deduplication (ID collision, normalized match, substring >0.8)
- Implement cross-reference resolution with warning logging
- Implement 4-pass completeness verification (Source Coverage ≥95%, Anti-Hallucination 100%, Section Coverage 100%, Count Reconciliation exact match)
- Implement single retry on verification failure, then STOP with error
- **Validates**: SC-018, FR-034, FR-035, NFR-012

### Phase 1 Exit Criteria
1. Single-spec invocation produces valid `extraction.md` with parseable YAML frontmatter
2. Chunked extraction activates for specs >500 lines and passes 4-pass verification
3. Output collision detection appends `-N` suffix correctly
4. Compliance auto-detection returns correct tier for keyword-laden specs, large specs, and small specs
5. SKILL.md ≤500 lines, refs/ contains exactly 5 files

---

## Phase 2: Template System & Roadmap Generation (Wave 2 + Wave 3)

**Goal**: Complete the single-spec pipeline end-to-end — from extraction through roadmap and test-strategy generation.

**Duration estimate**: 3-5 days

### Milestone 2.1: Wave 2 — Template Discovery & Selection
- Author `refs/templates.md` with template format specification and compatibility scoring algorithm
- Implement 4-tier template discovery: local (`.dev/templates/roadmap/`) → user (`~/.claude/templates/roadmap/`) → plugin (no-op stub) → inline generation fallback
- Implement compatibility scoring with correct weights: domain (0.40), complexity (0.30), type (0.20), version (0.10)
- Implement ≥0.6 threshold; below threshold triggers inline generation
- Implement `--template` flag to skip scoring
- Create milestone structure and dependency mapping
- **Validates**: SC-022, SC-023, FR-020, FR-040, FR-041, NFR-009

### Milestone 2.2: Wave 3 — Roadmap Generation
- Implement `roadmap.md` generation with full YAML frontmatter:
  - `spec_source` (scalar, single-spec mode)
  - `milestone_index` with per-milestone structured metadata
  - `generator`, `generated` (ISO-8601), `complexity_score`, `validation_score`, `validation_status`
- Implement Decision Summary section in roadmap body (Primary Persona, Template, Milestone Count, Adversarial Mode, Base Variant) with evidence citations
- Enforce sequencing: roadmap.md completes before test-strategy.md begins
- **Validates**: SC-001 (partial), SC-028, SC-030, FR-001, FR-002, FR-003, FR-004, FR-022, FR-023, NFR-003, NFR-004, NFR-008

### Milestone 2.3: Wave 3 — Test Strategy Generation
- Implement `test-strategy.md` generation with YAML frontmatter:
  - `validation_philosophy: continuous-parallel`
  - `interleave_ratio` computed from complexity (LOW→1:3, MEDIUM→1:2, HIGH→1:1)
  - `major_issue_policy: stop-and-fix`
- Ensure every validation milestone references a concrete work milestone from roadmap.md
- Encode continuous parallel validation philosophy in body
- **Validates**: SC-001, SC-029, FR-001, FR-007, FR-028, FR-029

### Milestone 2.4: Dry Run Mode
- Implement `--dry-run` flag: execute Waves 0-2, output structured console preview (spec, complexity, persona, template, milestone structure, domain distribution, estimated counts)
- Ensure no files are written and no validation agents dispatched
- **Validates**: SC-019, FR-036

### Phase 2 Exit Criteria
1. Single-spec invocation produces all 3 artifacts with valid YAML frontmatter
2. Template discovery searches all 4 tiers with correct scoring weights
3. Interleave ratio computed correctly for all complexity classes
4. `--dry-run` outputs preview without writing files
5. Decision Summary section present with evidence-backed rows
6. No references to tasklist generation or downstream commands in any output (SC-010, FR-030)

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
- Implement REVISE loop: re-run Wave 3 → Wave 4, up to 2 iterations
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
2. REVISE loop re-runs correctly and terminates after 2 iterations with PASS_WITH_WARNINGS
3. `--no-validate` and `--compliance light` correctly bypass validation
4. `--compliance strict` enforces full pipeline regardless of spec size

---

## Phase 4: Adversarial Integration (Wave 1A + Wave 2 Adversarial)

**Goal**: Enable multi-spec consolidation and multi-roadmap generation via sc:adversarial.

**Duration estimate**: 3-5 days

**Dependency**: sc:adversarial v1.1.0 must be installed and functional (DEP-001).

### Milestone 4.1: Adversarial Availability & Agent Validation
- Complete Wave 0 adversarial checks: if `--specs` or `--multi-roadmap` present but sc:adversarial not installed, abort with actionable error
- Implement model identifier validation in Wave 0 for `--agents` flag
- Implement agent spec parsing: split on `,` for list, then `:` per agent (max 3 segments)
- Enforce 2-10 agent count range
- Add orchestrator agent for ≥5 agents
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
- Implement `--multi-roadmap --agents <agent-spec>[,...]` flag
- Invoke `sc:adversarial --source --generate roadmap --agents` replacing template-based generation
- Implement `roadmap.md` frontmatter `adversarial` block (mode, agents, convergence_score, base_variant, artifacts_dir)
- Implement `--depth` flag mapping to adversarial debate rounds (quick=1, standard=2, deep=3)
- **Validates**: SC-003, SC-005, FR-005, FR-009, FR-021, FR-031

### Milestone 4.4: Combined Mode
- Implement `--specs` + `--multi-roadmap` combined: chain spec consolidation (Wave 1A) then roadmap adversarial generation (Wave 2) sequentially
- Implement `--interactive` propagation to adversarial invocations
- Implement `--dry-run` with adversarial execution (FR-037)
- **Validates**: SC-004, SC-005, FR-010, FR-037

### Milestone 4.5: Adversarial Validation in Wave 4
- Implement adversarial artifact checks: missing artifacts when adversarial mode used → REJECT; missing convergence score → REVISE
- Implement frontmatter `spec_sources` (list) for multi-spec mode, with mutual exclusion against `spec_source`
- **Validates**: SC-028, FR-003, FR-026

### Phase 4 Exit Criteria
1. `--specs` invokes sc:adversarial and produces unified spec with correct convergence routing
2. `--multi-roadmap --agents` produces adversarial roadmap with correct frontmatter
3. Combined mode chains both adversarial passes correctly
4. Wave 4 detects missing adversarial artifacts
5. Agent count enforcement (2-10) and model validation work correctly
6. `--dry-run` still executes adversarial invocations

---

## Phase 5: Session Persistence & Resumability

**Goal**: Enable cross-session persistence and resume from interrupted runs.

**Duration estimate**: 1-2 days

**Dependency**: Serena MCP server (DEP-003), sc:save/sc:load (DEP-002).

### Milestone 5.1: Session Save Protocol
- Implement sc:save trigger at each wave boundary
- Store: spec_source, output_dir, flags, last_completed_wave, extraction state, complexity, persona, template, milestone count, adversarial results, validation score
- **Validates**: SC-016, FR-045

### Milestone 5.2: Resume Protocol
- Detect matching Serena memory session (same spec path + output dir)
- Prompt user to resume from last completed wave
- Implement spec file hash comparison; warn if spec changed since last session
- Implement circuit breaker fallback: Serena unavailable → proceed without persistence with user warning
- **Validates**: SC-017, FR-046, NFR-011

### Phase 5 Exit Criteria
1. Session state saved at each wave boundary
2. Resume correctly offered and restores state from the last completed wave
3. Spec hash mismatch produces clear warning
4. Graceful degradation when Serena is unavailable

---

## Phase 6: Hardening & Edge Cases

**Goal**: Address remaining NFRs, edge cases, MCP fallbacks, and ref loading discipline.

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
- Validate all frontmatter parseable by standard YAML parsers (NFR-008)
- Validate frontmatter schema stability: no removed/renamed fields from v2.0 baseline (NFR-003)
- Validate single-spec completion <2 minutes (NFR-001)
- **Validates**: SC-024, NFR-001, NFR-002, NFR-003, NFR-007, NFR-008

### Milestone 6.4: Edge Case Handling
- Interleave ratio edge case: when milestone count is too low for the ratio, floor to minimum 1 validation milestone
- Agent persona inheritance: model-only agents inherit auto-detected primary persona from Wave 1B
- `--persona` propagation to model-only agents in `--agents`
- Empty or near-empty specs: compliance auto-detection routes to LIGHT
- **Validates**: SC-013, FR-011, FR-029, FR-039

### Phase 6 Exit Criteria
1. All NFRs verified
2. Circuit breaker fallbacks tested for all 3 MCP servers
3. Ref loading discipline verified per wave
4. Edge cases handled without errors

---

## Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation | Phase |
|------|------------|--------|------------|-------|
| RISK-001: Claude misses ref files due to SKILL.md split | Medium | High | SKILL.md explicitly names each ref; on-demand loading protocol enforced in Phase 6 | 1, 6 |
| RISK-002: sc:adversarial unavailable | Low | High | Wave 0 detection with actionable install instructions; abort early | 4 |
| RISK-003: Frontmatter schema breaks tasklist generator | Medium | Medium | Versioned contract; additions-only policy after v2.0; documented in NFR-003 | 2, 6 |
| RISK-004: Multi-spec produces incoherent unified spec | Medium | Medium | Convergence-based routing (<60% abort/prompt); divergent-specs heuristic at <50% | 4 |
| RISK-005: Combined mode too slow | Medium | Low | Progress reporting at wave boundaries; no hard time constraints for adversarial modes | 4 |
| RISK-006: Adversarial partial status causes silent degradation | Medium | Medium | Explicit convergence thresholds with routing decisions (≥60%/<60%) | 4 |
| RISK-007: Large specs overwhelm context | Medium | High | Chunked extraction with 4-pass verification; implemented in Phase 1 | 1 |
| RISK-008: Interrupted session produces stale artifacts | Low | Medium | sc:save at wave boundaries; resume protocol with hash-based staleness detection | 5 |
| RISK-009: Unrecognized model in --agents | Low | Medium | Wave 0 validates all model identifiers before execution starts | 4 |

### Additional Architectural Risks Identified

| Risk | Probability | Impact | Mitigation | Phase |
|------|------------|--------|------------|-------|
| RISK-010: SKILL.md exceeds 500 lines during implementation | Medium | Medium | Track line count during each phase; refactor aggressively into refs/ | All |
| RISK-011: Template scoring produces unexpected inline fallback too frequently | Medium | Low | Provide well-scored default templates; log scoring decisions for debugging | 2 |
| RISK-012: REVISE loop creates infinite-feeling UX | Low | Low | Hard cap at 2 iterations with PASS_WITH_WARNINGS; progress reporting during loop | 3 |

---

## Resource Requirements & Dependencies

### Internal Dependencies (Must exist before implementation)
1. **sc:adversarial v1.1.0** (DEP-001) — Required for Phase 4. Must support `--compare`, `--source --generate roadmap --agents`, return contract with status/convergence_score/artifacts_dir. **Risk**: If not finalized, Phase 4 is blocked.
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
Phase 1 (Foundation) → Phase 2 (Generation) → Phase 3 (Validation) → Phase 6 (Hardening)
                                                                    ↗
                                              Phase 4 (Adversarial) 
                                              Phase 5 (Persistence)
```

Phases 4 and 5 can proceed in parallel after Phase 2, with Phase 4's adversarial validation milestone (4.5) depending on Phase 3. Phase 6 is the final integration and hardening phase.

---

## Success Criteria & Validation Approach

### Validation Strategy

Each phase has explicit exit criteria (listed above). The overall validation approach is:

1. **Unit-level**: Each milestone validates specific SC-* criteria with concrete assertions
2. **Integration-level**: Phase exit criteria verify cross-milestone interactions
3. **End-to-end**: Final validation runs the full pipeline in all modes:
   - Single-spec (simple, medium, complex specs)
   - Single-spec with `--dry-run`
   - Single-spec with `--compliance light` and `--compliance strict`
   - Multi-spec with 2-3 specs at varying convergence levels
   - Multi-roadmap with 2, 5, and 10 agents
   - Combined mode
   - Resume from interrupted session
   - Chunked extraction with >500-line spec

### Key Validation Checkpoints

| Checkpoint | Criteria | Method |
|-----------|----------|--------|
| 3-artifact production | SC-001 | Run pipeline, verify 3 files exist with valid YAML |
| Frontmatter schema | SC-028, FR-002-005 | Parse frontmatter with YAML parser, assert required fields |
| No downstream handoff | SC-010, FR-030 | Grep outputs for "tasklist", "execute", "proceed to" |
| SKILL.md constraints | SC-024-027 | `wc -l SKILL.md`, grep for YAML pseudocode, verify refs/ count |
| Adversarial integration | SC-002-004, SC-008 | Mock sc:adversarial responses at each status level |
| REVISE loop termination | SC-007 | Force REVISE score, verify 2 iterations then PASS_WITH_WARNINGS |
| Chunked extraction | SC-018 | Feed >500-line spec, verify 4-pass verification passes |
| Performance | NFR-001 | Time single-spec execution, assert <2 minutes |

---

## Open Questions Requiring Resolution

The following open questions from the extraction should be resolved before or during implementation:

| # | Question | Recommended Resolution | Blocking Phase |
|---|----------|----------------------|----------------|
| 1 | Plugin tier template discovery interface | Implement no-op stub with TODO comment; skip tier 3 until v5.0 | 2 |
| 2 | Canonical model identifier list | Hardcode initial list (opus, sonnet, haiku); make configurable via refs/ | 4 |
| 3 | Orchestrator agent for ≥5 agents | Define as a coordination prompt within `refs/adversarial-integration.md`; sc:roadmap injects it | 4 |
| 4 | sc:adversarial return contract finalization | Block Phase 4 until SC-ADVERSARIAL-SPEC.md is finalized | 4 |
| 5 | Serena memory key cleanup | Implement "most recent session only" for resume; no automatic cleanup | 5 |
| 6 | Unresolvable cross-references in chunked extraction | Treat as informational warnings (non-blocking) | 1 |
| 7 | Interleave ratio edge case (too few milestones) | Floor to minimum 1 validation milestone | 6 |
| 8 | Adversarial depth independence documentation | Document as a note in command file; not a prominent feature | 4 |
| 9 | Template discovery in CI/containers | Gracefully skip missing tiers; log which tiers were available | 6 |
| 10 | Dry run + adversarial cost | Add console warning about adversarial cost before execution | 4 |

---

## Timeline Summary

| Phase | Duration | Dependencies | Parallelizable |
|-------|----------|-------------|----------------|
| Phase 1: Foundation | 3-5 days | None | No (baseline) |
| Phase 2: Generation | 3-5 days | Phase 1 | No (sequential) |
| Phase 3: Validation | 2-3 days | Phase 2 | No (sequential) |
| Phase 4: Adversarial | 3-5 days | Phase 2 + sc:adversarial v1.1.0 | Yes (parallel with Phase 5) |
| Phase 5: Persistence | 1-2 days | Phase 2 + Serena MCP | Yes (parallel with Phase 4) |
| Phase 6: Hardening | 2-3 days | Phases 3, 4, 5 | No (final integration) |
| **Total** | **14-23 days** | | |

**Critical path**: Phase 1 → Phase 2 → Phase 3 → Phase 6 = 10-16 days minimum.

Phase 4 is the highest-risk phase due to external dependency on sc:adversarial v1.1.0 finalization. If blocked, Phases 1-3 and 5-6 (excluding adversarial validation in 4.5) can still deliver a fully functional single-spec pipeline.
