---
validation_milestones: 24
interleave_ratio: '1:1'
---

# SC:ROADMAP v2.0 — Comprehensive Test Strategy

## 1. Validation Milestones Mapped to Roadmap Phases

Given complexity score 0.82 (complex class), the interleave ratio is **1:1** per FR-029: every implementation milestone gets a paired validation milestone. This produces **24 validation milestones** across 7 phases.

### Phase 0: Contract Freeze & Interface Decisions

| Val ID | Paired Milestone | What to Validate | Test Type |
|--------|-----------------|------------------|-----------|
| V-0.1 | M0.1 Schema Freeze | Frontmatter schemas parseable by standard YAML parser; field-level required/optional annotations complete per mode; `spec_source`/`spec_sources` mutual exclusivity defined | Contract, Unit |
| V-0.2 | M0.2 Wave Architecture Freeze | Wave state transition diagram covers all 5 waves + REVISE loopback; generation routing abstraction interface defined with template and adversarial strategies | Architecture Review |
| V-0.3 | M0.3 Open Question Resolution | All 10 decisions recorded; no ambiguous "TBD" entries remain; each decision traceable to a phase dependency | Document Review |

### Phase 1: Foundation & Core Pipeline

| Val ID | Paired Milestone | What to Validate | Test Type |
|--------|-----------------|------------------|-----------|
| V-1.1 | M1.1 File Structure | `commands/roadmap.md` exists (~80 lines); `SKILL.md` skeleton exists; `refs/` has exactly 5 stub files; WHEN/WHAT vs HOW separation holds | Unit, Contract |
| V-1.2 | M1.2 Wave Orchestrator | Waves execute in order (0→1A/1B→2→3→4); conditional Wave 1A only with `--specs`; REVISE loops back to Wave 3; dry-run stops at Wave 2; state persistence fires at boundaries; progress reporting emits at each boundary | Unit, Integration |
| V-1.3 | M1.3 Wave 0 Prerequisites | Spec existence check; output dir writability; collision detection appends `-N`; flag parsing for all 6 flags; compliance auto-detection returns correct tier | Unit |
| V-1.4 | M1.4 Extraction Pipeline | Single-pass extraction produces valid `extraction.md` with parseable YAML frontmatter; complexity scoring matches expected ranges; domain classification correct; `--persona` override works | Unit, Integration |
| V-1.5 | M1.5 Chunked Extraction | >500-line spec triggers chunking; chunks ~400 lines (max 600); 4-pass verification (coverage ≥95%, anti-hallucination 100%, section 100%, count exact); single retry on failure; STOP on second failure | Unit, Integration |

### Phase 2: Template System & Roadmap Generation

| Val ID | Paired Milestone | What to Validate | Test Type |
|--------|-----------------|------------------|-----------|
| V-2.1 | M2.1 Template Discovery | 4-tier search order (local→user→plugin→inline); scoring weights correct (0.40/0.30/0.20/0.10); ≥0.6 threshold; `--template` flag bypasses scoring; scores logged; deterministic tie-break | Unit, Integration |
| V-2.2 | M2.2 Generation Routing | Strategy pattern interface accepts extraction output, produces roadmap content; template strategy is default; adversarial strategy stub exists but is not callable | Unit |
| V-2.3 | M2.3 Roadmap Generation | `roadmap.md` has valid frontmatter per Phase 0 schema; exactly one of `spec_source`/`spec_sources`; `milestone_index` with all 7 fields; Decision Summary section with 5 evidence-backed rows; roadmap completes before test-strategy starts | Integration, Contract |
| V-2.4 | M2.4 Test Strategy Generation | `test-strategy.md` has `validation_philosophy: continuous-parallel`; `interleave_ratio` matches complexity class; `major_issue_policy: stop-and-fix`; every validation milestone references a real work milestone | Integration, Contract |
| V-2.5 | M2.5 Dry Run Mode | `--dry-run` executes Waves 0-2; outputs structured preview (spec, complexity, persona, template, milestones, domains, counts); zero files written; no validation agents dispatched; persistence hooks still fire | Integration |

### Phase 3: Validation Pipeline

| Val ID | Paired Milestone | What to Validate | Test Type |
|--------|-----------------|------------------|-----------|
| V-3.1 | M3.1 Quality Validation | quality-engineer agent dispatched; self-review agent dispatched with 4-question protocol; scores aggregated; correct PASS/REVISE/REJECT classification at thresholds (85/70/70) | Unit, Integration |
| V-3.2 | M3.2 REVISE Loop | Score 70-84% triggers re-run Wave 3→4; max 2 iterations; after 2 failures → `PASS_WITH_WARNINGS`; REVISE respects mode-aware routing (template vs adversarial) | Integration |
| V-3.3 | M3.3 Validation Bypass | `--no-validate`: Wave 4 skipped, `validation_score: 0.0`, `validation_status: SKIPPED`; `--compliance light`: skip Wave 4, `validation_status: LIGHT`; `--compliance strict`: full pipeline even <500 lines | Integration |

### Phase 4: Adversarial Integration

| Val ID | Paired Milestone | What to Validate | Test Type |
|--------|-----------------|------------------|-----------|
| V-4.1 | M4.1 Adversarial Availability | Missing sc:adversarial with `--specs`/`--multi-roadmap` → abort with actionable error; model identifier validation rejects unknown models; agent spec parsing (`,` then `:`, max 3 segments); 2-10 count enforcement; orchestrator added at ≥5 | Unit, Integration |
| V-4.2 | M4.2 Multi-Spec Consolidation | `--specs` invokes `sc:adversarial --compare`; return contract routing: success→proceed, partial≥60%→warn+proceed, partial<60%→prompt/abort, failed→abort; divergent-specs warning at <50% | Integration, E2E |
| V-4.3 | M4.3 Multi-Roadmap Generation | Adversarial generation strategy activated via routing abstraction (no template refactoring); frontmatter `adversarial` block present with all 5 fields; `--depth` maps to debate rounds (1/2/3); `--persona` propagates to model-only agents | Integration, E2E |
| V-4.4 | M4.4 Combined Mode | `--specs` + `--multi-roadmap` chains Wave 1A then Wave 2 adversarial; `--interactive` propagates; `--dry-run` with adversarial still executes invocations + emits cost warning | E2E |
| V-4.5 | M4.5 Adversarial Validation | Missing artifacts when adversarial mode → REJECT; missing convergence score → REVISE; `spec_sources` (list) for multi-spec with mutual exclusion against `spec_source` | Integration |

### Phase 5: Session Persistence & Resumability

| Val ID | Paired Milestone | What to Validate | Test Type |
|--------|-----------------|------------------|-----------|
| V-5.1 | M5.1 Session Save | sc:save fires at each wave boundary; all 12 state fields stored; spec file hash captured | Integration |
| V-5.2 | M5.2 Resume Protocol | Matching session detected (same spec+output); user prompted; resume starts from last completed wave; hash mismatch warns + requires confirmation; Serena unavailable → proceed without persistence with warning | Integration, E2E |

### Phase 6: Hardening & Release

| Val ID | Paired Milestone | What to Validate | Test Type |
|--------|-----------------|------------------|-----------|
| V-6.1 | M6.1-6.6 (Consolidated) | Ref loading per-wave matches FR-044 mapping; circuit breakers for Sequential/Context7/Serena; SKILL.md ≤500 lines; command file ~80 lines; all NFRs pass; edge cases (min 1 validation milestone, empty specs, persona inheritance); 100% SC-* mapped to passing tests; release gate thresholds met | Unit, Integration, E2E, Acceptance |

---

## 2. Test Categories

### 2.1 Unit Tests

**Scope**: Individual functions, parsers, scoring algorithms, validators in isolation.

| Test Group | Target | Count Est. | Priority |
|------------|--------|------------|----------|
| Frontmatter Schema | YAML parse, required/optional per mode, mutual exclusivity | 12 | P0 |
| Complexity Scoring | Formula with 5 weighted factors, boundary values, class thresholds | 8 | P0 |
| Template Scoring | 4-weight compatibility, ≥0.6 threshold, tie-break determinism | 10 | P1 |
| Flag Parsing | All 20+ flags, combinations, conflicts, defaults | 15 | P0 |
| Agent Spec Parsing | `,` split, `:` split, max 3 segments, 2-10 range, model validation | 10 | P1 |
| Compliance Detection | Keyword heuristics, line thresholds, auto-tier classification | 8 | P0 |
| Collision Detection | `-N` suffix incrementing, existing files, race conditions | 5 | P1 |
| Interleave Ratio | LOW→1:3, MEDIUM→1:2, HIGH→1:1, edge case (min 1 milestone) | 6 | P1 |
| Chunked Extraction | Section indexing, chunk assembly, dedup algorithms, ID counters | 12 | P0 |
| 4-Pass Verification | Coverage ≥95%, anti-hallucination 100%, section 100%, count exact | 8 | P0 |

**Total estimated unit tests**: ~94

### 2.2 Integration Tests

**Scope**: Wave-to-wave interactions, MCP server coordination, strategy pattern routing.

| Test Group | Target | Count Est. | Priority |
|------------|--------|------------|----------|
| Wave Sequencing | 0→1B→2→3→4 ordering, conditional 1A, state transitions | 8 | P0 |
| Orchestrator State Machine | All state transitions, edge cases (resume mid-wave, dry-run cutoff) | 10 | P0 |
| Extraction→Generation Pipeline | extraction.md consumed by Wave 2→3 correctly | 5 | P0 |
| Template Discovery→Selection→Generation | 4-tier search produces correct template for generation | 6 | P1 |
| Generation Routing | Template vs adversarial strategy selection and execution | 5 | P1 |
| REVISE Loop | Wave 3→4 re-run, iteration counting, PASS_WITH_WARNINGS termination | 5 | P0 |
| Validation Agent Dispatch | quality-engineer and self-review agent coordination, score aggregation | 5 | P1 |
| Circuit Breaker Fallbacks | Sequential→native, Context7→WebSearch, Serena→no-persistence | 6 | P1 |
| Session Save/Resume | State capture at boundaries, resume from each wave, hash comparison | 8 | P1 |
| Adversarial Return Contract | success/partial/failed routing, convergence thresholds | 6 | P1 |

**Total estimated integration tests**: ~64

### 2.3 End-to-End Tests

**Scope**: Full pipeline invocations from CLI flags to output artifacts on disk.

| Test Scenario | Flags | Expected Output | Priority |
|---------------|-------|-----------------|----------|
| Single-spec simple | `spec.md` | 3 artifacts, LOW complexity, 1:3 ratio | P0 |
| Single-spec complex | `large-spec.md` | 3 artifacts, HIGH complexity, 1:1 ratio, chunked extraction | P0 |
| Single-spec dry run | `--dry-run spec.md` | Console preview, zero files | P0 |
| Single-spec strict | `--compliance strict spec.md` | Full pipeline, 4-pass even <500 lines | P1 |
| Single-spec light | `--compliance light spec.md` | Reduced extraction, `validation_status: LIGHT` | P1 |
| Single-spec no-validate | `--no-validate spec.md` | `validation_score: 0.0`, `validation_status: SKIPPED` | P1 |
| Multi-spec | `--specs a.md,b.md` | Unified spec, single roadmap | P1 |
| Multi-roadmap | `--multi-roadmap --agents opus,sonnet` | Adversarial roadmap with frontmatter block | P1 |
| Combined mode | `--specs a.md,b.md --multi-roadmap --agents opus,sonnet` | Chained adversarial | P2 |
| Resume interrupted | Kill after Wave 2, re-invoke | Resume prompt, continues from Wave 3 | P1 |
| Output collision | Pre-existing artifacts in output dir | `-1` suffix appended | P1 |
| >500-line chunked | `large-spec.md` (600+ lines) | Chunked extraction, 4-pass verification passes | P0 |

**Total estimated E2E tests**: 12

### 2.4 Acceptance Tests

**Scope**: Success criteria (SC-001 through SC-030) mapped to verifiable assertions.

Each SC-* criterion becomes one acceptance test. Organized by the 4-layer validation model from the roadmap:

- **Layer A (Contract)**: SC-028, SC-024, SC-025 — 3 tests
- **Layer B (Flow)**: SC-001, SC-007, SC-009, SC-010, SC-019 — 5 tests
- **Layer C (Dependency/Failure)**: SC-011, SC-014, SC-015, SC-017 — 4 tests
- **Layer D (Quality/Mode)**: SC-002 through SC-006, SC-008, SC-012, SC-013, SC-016, SC-018, SC-020 through SC-023, SC-026, SC-027, SC-029, SC-030 — 18 tests

**Total acceptance tests**: 30

---

## 3. Test-Implementation Interleaving Strategy

### Philosophy: Continuous Parallel Validation

Per FR-028 and the 1:1 interleave ratio, work is **assumed deviated until proven otherwise**. Every implementation milestone gets a validation milestone that runs before the next implementation begins.

### Interleaving Pattern

```
Phase 0:  M0.1 → V-0.1 → M0.2 → V-0.2 → M0.3 → V-0.3 → EXIT GATE 0
Phase 1:  M1.1 → V-1.1 → M1.2 → V-1.2 → M1.3 → V-1.3 → M1.4 → V-1.4 → M1.5 → V-1.5 → EXIT GATE 1
Phase 2:  M2.1 → V-2.1 → M2.2 → V-2.2 → M2.3 → V-2.3 → M2.4 → V-2.4 → M2.5 → V-2.5 → EXIT GATE 2
Phase 3:  M3.1 → V-3.1 → M3.2 → V-3.2 → M3.3 → V-3.3 → EXIT GATE 3
Phase 4:  M4.1 → V-4.1 → M4.2 → V-4.2 → M4.3 → V-4.3 → M4.4 → V-4.4 → M4.5 → V-4.5 → EXIT GATE 4
Phase 5:  M5.1 → V-5.1 → M5.2 → V-5.2 → EXIT GATE 5
Phase 6:  M6.1-6.6 → V-6.1 (consolidated) → EXIT GATE 6 (RELEASE)
```

### Stop-and-Fix Policy

**Major issue** (any of these triggers immediate stop):
- Frontmatter schema violation (Layer A failure)
- Wave sequencing error (Layer B failure)
- Data loss or corruption in extraction output
- Security-sensitive flag bypass (compliance tier violation)

**Minor issue** (log and continue, fix in next cycle):
- Template scoring tie-break inconsistency
- Progress reporting format deviation
- Non-blocking warning message wording

### Test-First vs Test-After by Phase

| Phase | Strategy | Rationale |
|-------|----------|-----------|
| Phase 0 | Test-first (contract tests written before schema is frozen) | Schema is the foundation; contract tests prevent drift |
| Phase 1 | Test-first for orchestrator, test-after for extraction | Orchestrator is architectural; extraction is algorithmic |
| Phase 2 | Test-after | Template scoring and generation need working code to validate against |
| Phase 3 | Test-first | Validation thresholds (85/70/70) and REVISE loop logic are spec-defined contracts |
| Phase 4 | Test-after (mock sc:adversarial) | Adversarial integration requires mocking external dependency |
| Phase 5 | Test-after (mock Serena) | Persistence requires mocking MCP server |
| Phase 6 | Acceptance test execution | All SC-* criteria run as final acceptance suite |

---

## 4. Risk-Based Test Prioritization

### Priority 0 — Must pass before any release (Blocking)

| Risk | Tests | Rationale |
|------|-------|-----------|
| RISK-001: Schema contract breakage | V-0.1, frontmatter unit tests, Layer A acceptance | Downstream consumers depend on schema stability |
| RISK-003: Extraction failure/hallucination | V-1.4, V-1.5, 4-pass verification unit tests | Extraction is the data foundation for everything |
| RISK-013: Orchestrator interaction complexity | V-1.2, wave sequencing integration tests | 7 behavioral concerns interact; bugs here cascade |
| Single-spec happy path | E2E single-spec simple + complex | Core value proposition must work |

### Priority 1 — Must pass before feature release

| Risk | Tests | Rationale |
|------|-------|-----------|
| RISK-002: sc:adversarial unavailable | V-4.1 (availability check + abort) | Must fail gracefully, not crash |
| RISK-004: Stale resume | V-5.2 (hash mismatch warning) | Data integrity on resume |
| RISK-005: Incoherent multi-spec | V-4.2 (convergence routing) | Adversarial quality gate |
| RISK-006: Silent adversarial degradation | V-4.5 (missing artifacts → REJECT) | Prevents undetected quality loss |
| RISK-010: SKILL.md >500 lines | V-6.1 (line count check) | Architectural constraint |
| RISK-011: Excessive inline fallback | V-2.1 (template scoring) | UX quality |
| Circuit breaker fallbacks | V-6.1 (all 3 MCP fallbacks) | Resilience under degradation |

### Priority 2 — Should pass, not blocking

| Risk | Tests | Rationale |
|------|-------|-----------|
| RISK-007: Combined mode too slow | V-4.4 (dry-run cost warning) | UX concern, not correctness |
| RISK-012: REVISE loop UX | V-3.2 (iteration cap) | Already hard-capped at 2 |
| Edge cases | V-6.1 (min 1 milestone, empty specs) | Low probability scenarios |

---

## 5. Acceptance Criteria Per Milestone

### Phase 0 Exit Criteria (Gate 0)

- [ ] YAML schemas for all 3 artifacts written and parseable
- [ ] Required/optional field annotations complete for all modes (single, multi-spec, multi-roadmap, combined, dry-run, no-validate, light, strict)
- [ ] `spec_source`/`spec_sources` mutual exclusivity rule documented and testable
- [ ] Wave state transition diagram reviewed — covers all paths including REVISE and dry-run
- [ ] All 10 open questions resolved with decision record
- [ ] **Quality gate**: Contract test stubs written (can compile, assertions pending implementation)

### Phase 1 Exit Criteria (Gate 1)

- [ ] `commands/roadmap.md` exists, ≤100 lines, contains WHEN/WHAT only
- [ ] `SKILL.md` skeleton exists, ≤500 lines
- [ ] `refs/` has exactly 5 files (may be stubs for unused ones)
- [ ] Wave orchestrator passes all 8 sequencing integration tests
- [ ] Single-spec extraction produces valid `extraction.md` — frontmatter parseable, counts match
- [ ] Chunked extraction triggers for >500-line spec — 4-pass verification passes
- [ ] Collision detection appends `-N` suffix correctly (tested with 0, 1, 3 pre-existing collisions)
- [ ] Compliance auto-detection: security keywords → STRICT, >500 lines → STRICT, <100 lines/<5 reqs → LIGHT, else → STANDARD
- [ ] Progress reporting visible at Wave 0 and Wave 1B boundaries
- [ ] **Quality gate**: All P0 unit tests pass; integration tests for orchestrator pass

### Phase 2 Exit Criteria (Gate 2)

- [ ] Template discovery searches all 4 tiers in order (local→user→plugin stub→inline)
- [ ] Template scoring weights verified: domain 0.40, complexity 0.30, type 0.20, version 0.10
- [ ] Score <0.6 triggers inline generation fallback
- [ ] `--template` flag bypasses scoring entirely
- [ ] Generation routing abstraction: template strategy active, adversarial strategy stub exists
- [ ] `roadmap.md` produced with all required frontmatter fields per Phase 0 schema
- [ ] `test-strategy.md` produced with `validation_philosophy: continuous-parallel`
- [ ] Interleave ratio: LOW→1:3, MEDIUM→1:2, HIGH→1:1 (verified for each)
- [ ] Decision Summary section present with 5 rows, each citing evidence
- [ ] `--dry-run` outputs preview, writes zero files, dispatches no agents
- [ ] No downstream handoff language in any output (grep for "tasklist", "execute", "run next")
- [ ] **Quality gate**: Single-spec E2E test passes end-to-end (all 3 artifacts valid)

### Phase 3 Exit Criteria (Gate 3)

- [ ] Validation agents dispatched and scores aggregated
- [ ] Score ≥85% → PASS, 70-84% → REVISE, <70% → REJECT (boundary values tested: 84.9→REVISE, 85.0→PASS, 69.9→REJECT, 70.0→REVISE)
- [ ] REVISE loop: re-runs Wave 3→4, max 2 iterations, then PASS_WITH_WARNINGS
- [ ] `--no-validate`: `validation_score: 0.0`, `validation_status: SKIPPED`
- [ ] `--compliance light`: Wave 4 skipped, `validation_status: LIGHT`
- [ ] `--compliance strict`: full pipeline enforced regardless of spec size
- [ ] **Quality gate**: REVISE loop integration test passes with mock scores at each boundary

### Phase 4 Exit Criteria (Gate 4)

- [ ] Missing sc:adversarial + adversarial flags → abort with install instructions
- [ ] Model identifier validation rejects unknown models at Wave 0
- [ ] Agent count <2 or >10 → rejected
- [ ] `--specs` invokes `sc:adversarial --compare`, convergence routing correct at 60% threshold
- [ ] `--multi-roadmap --agents` produces adversarial roadmap via generation strategy (not template refactoring)
- [ ] Frontmatter `adversarial` block has all 5 fields (mode, agents, convergence_score, base_variant, artifacts_dir)
- [ ] Combined mode chains Wave 1A → Wave 2 adversarial sequentially
- [ ] `--interactive` propagates to adversarial invocations
- [ ] `--dry-run` with adversarial emits cost warning
- [ ] Wave 4 detects missing adversarial artifacts → REJECT
- [ ] **Quality gate**: Multi-spec and multi-roadmap E2E tests pass (with mocked sc:adversarial)

### Phase 5 Exit Criteria (Gate 5)

- [ ] sc:save fires at each wave boundary (verified by mock capture)
- [ ] All 12 state fields stored correctly
- [ ] Spec file hash captured and compared on resume
- [ ] Resume detected and offered when matching session exists
- [ ] Hash mismatch produces warning and requires explicit confirmation
- [ ] Serena unavailable → warning + proceed without persistence
- [ ] **Quality gate**: Resume E2E test — kill after Wave 2, re-invoke, confirm resume from Wave 3

### Phase 6 Exit Criteria (Gate 6 — Release)

- [ ] Ref loading per-wave matches FR-044 exactly (max 2-3 at any point)
- [ ] Circuit breakers tested: Sequential fallback, Context7 fallback, Serena fallback
- [ ] SKILL.md ≤500 lines confirmed
- [ ] Command file ~80 lines confirmed
- [ ] No YAML pseudocode in SKILL.md
- [ ] Single-spec completion <2 minutes (timed test)
- [ ] All 30 SC-* acceptance tests pass
- [ ] All Layer A-D tests pass at 100%
- [ ] Edge cases: min 1 validation milestone, empty spec → LIGHT, persona inheritance for model-only agents
- [ ] Negative-path tests pass: missing skill, invalid models, output collisions, convergence <60%, stale resume, malformed templates, MCP unavailability
- [ ] **Release gate**: All criteria in roadmap "Release Readiness Gate" section met

---

## 6. Quality Gates Between Phases

### Gate Structure

Each gate runs automatically after the last validation milestone of a phase. Gates are **blocking** — the next phase cannot begin until the gate passes.

```
┌─────────────────────────────────────────────────────────────┐
│                    GATE EVALUATION                          │
│  1. Run all validation milestone tests for the phase        │
│  2. Check phase exit criteria checklist (all boxes checked) │
│  3. Run regression suite (all prior phase tests still pass) │
│  4. Evaluate stop-and-fix triggers (any major issues?)      │
│  5. PASS → proceed  |  FAIL → stop, fix, re-evaluate       │
└─────────────────────────────────────────────────────────────┘
```

### Gate Definitions

| Gate | Precondition | Pass Criteria | Regression Scope | Failure Action |
|------|-------------|---------------|-------------------|----------------|
| **Gate 0** | Phase 0 complete | Schemas parseable, decisions recorded, no TBDs | N/A (baseline) | Resolve ambiguity before proceeding |
| **Gate 1** | Phase 1 complete | Orchestrator + extraction working, chunked extraction verified | Gate 0 contract tests | Fix orchestrator or extraction bugs |
| **Gate 2** | Phase 2 complete | 3 artifacts produced end-to-end, template scoring verified | Gates 0-1 | Fix generation or template bugs |
| **Gate 3** | Phase 3 complete | Validation pipeline classifies correctly, REVISE loop works | Gates 0-2 | Fix validation scoring or loop logic |
| **Gate 4** | Phase 4 complete | All adversarial modes functional, return contract routing correct | Gates 0-3 | Fix adversarial integration |
| **Gate 5** | Phase 5 complete | Persistence saves/resumes correctly, degradation graceful | Gates 0-3 (4 if complete) | Fix persistence or fallback |
| **Gate 6 (Release)** | All phases complete | 100% acceptance tests, all NFRs verified, release readiness thresholds | Gates 0-5 (full regression) | Fix remaining failures |

### Regression Strategy

- **Gates 0-2**: Run full test suite (fast, <30s expected)
- **Gates 3-5**: Run full test suite + targeted adversarial/persistence tests
- **Gate 6**: Full test suite + acceptance suite + performance benchmark + NFR compliance check

### Gate Override Policy

- No overrides for Gate 0 (schema contract is non-negotiable)
- No overrides for Gate 1 (orchestrator correctness is foundational)
- Gates 2-5: May proceed with documented known issues if:
  - Issue is not in a P0 test
  - Issue has a mitigation plan with timeline
  - Product owner explicitly approves
- Gate 6: No overrides — all release criteria must pass

---

## Appendix A: SC-* to Test Mapping Matrix

| SC | Layer | Test IDs | Phase Validated |
|----|-------|----------|-----------------|
| SC-001 | B | V-1.2, V-2.3, V-2.4, E2E-single-simple | 1, 2 |
| SC-002 | D | V-4.2, E2E-multi-spec | 4 |
| SC-003 | D | V-4.3, E2E-multi-roadmap | 4 |
| SC-004 | D | V-4.4, E2E-combined | 4 |
| SC-005 | D | V-4.3, V-4.4 | 4 |
| SC-006 | D | V-3.1 | 3 |
| SC-007 | B | V-3.2 | 3 |
| SC-008 | D | V-4.2 | 4 |
| SC-009 | B | V-1.2 (progress reporting) | 1 |
| SC-010 | B | V-2.3 (grep for downstream language) | 2 |
| SC-011 | C | V-1.3 (collision detection) | 1 |
| SC-012 | D | V-3.3 | 3 |
| SC-013 | D | V-4.3 (persona propagation) | 4 |
| SC-014 | C | V-4.1 (model validation) | 4 |
| SC-015 | C | V-4.1 (agent count enforcement) | 4 |
| SC-016 | D | V-5.1 | 5 |
| SC-017 | C | V-5.2 | 5 |
| SC-018 | D | V-1.5 | 1 |
| SC-019 | B | V-2.5 | 2 |
| SC-020 | D | V-1.3 (auto-detection) | 1 |
| SC-021 | D | V-3.3 | 3 |
| SC-022 | D | V-2.1 | 2 |
| SC-023 | D | V-2.1 (weight verification) | 2 |
| SC-024 | A | V-1.1, V-6.1 | 1, 6 |
| SC-025 | A | V-1.1 | 1 |
| SC-026 | A | V-6.1 (ref referencing) | 6 |
| SC-027 | A | V-6.1 (ref loading) | 6 |
| SC-028 | A | V-0.1, V-2.3, V-4.5 | 0, 2, 4 |
| SC-029 | D | V-2.4 | 2 |
| SC-030 | D | V-2.3 (Decision Summary) | 2 |

**Coverage**: 30/30 SC criteria mapped (100%)

## Appendix B: Test Counts Summary

| Category | Count | Priority Distribution |
|----------|-------|-----------------------|
| Unit Tests | ~94 | P0: 51, P1: 38, P2: 5 |
| Integration Tests | ~64 | P0: 23, P1: 36, P2: 5 |
| E2E Tests | 12 | P0: 3, P1: 7, P2: 2 |
| Acceptance Tests | 30 | All P0 (release-blocking) |
| **Total** | **~200** | |
