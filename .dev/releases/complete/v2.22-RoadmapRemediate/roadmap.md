

---
spec_source: "spec-roadmap-remediate.md"
complexity_score: 0.72
adversarial: true
---

# v2.22 RoadmapRemediate — Merged Project Roadmap

## 1. Executive Summary

This release extends the `roadmap run` pipeline with two new post-validation steps — **remediate** (step 10) and **certify** (step 11). The feature parses adversarial validation findings, presents an interactive severity-scoped prompt, orchestrates parallel remediation agents with transactional rollback, and runs a single-pass certification to verify fixes.

**Architectural signature**: Multi-agent orchestration with file-level batching, snapshot-based rollback, and strict import/edit constraints — integrated into the existing pipeline without breaking backward compatibility.

**Key risks**: Report format fragility (R-002), rollback failure during multi-agent remediation (R-003), stale resume causing invalid certification (R-005), certification false passes (R-006). All are mitigated by design with dedicated test investment.

**Critical path**: P0 → P1 → P3 → P4 → P6 (11–15 days minimum). Phases 2 and 5 overlap with adjacent phases.

**Implementation posture**: Build in layers — parsing → filtering/tasklist → orchestration → certification → resume/state. Treat rollback, hashing, and gate validation as first-class features. Optimize for correctness before speed.

---

## 2. Phased Implementation Plan

### Phase 0: Discovery and Architecture Lock
**Duration**: 0.5 days | **Milestone**: M0 — Architecture decisions locked

Scoped discovery phase resolving only structurally-impactful open questions. Behavioral defaults are deferred to implementation phases per recommended defaults.

**Key Actions**:
1. Review existing pipeline foundation: `execute_pipeline()`, `execute_roadmap()`, `validate_executor.py`, step/gate/state models, resume flow, hash usage patterns
2. Confirm current state schema version and additive-extension strategy
3. Resolve structural open questions:
   - SIGINT behavior during remediation — determine whether `ClaudeProcess` subprocess cleanup requires signal forwarding code or if snapshot-based manual recovery suffices
   - Hash algorithm standardization — confirm SHA-256 and validate no conflicts with existing hash patterns
   - Step wiring confirmation — verify `remediate` uses `ClaudeProcess` directly while `certify` uses `execute_pipeline()`
4. Define canonical finding lifecycle: `PENDING` → `FIXED` / `FAILED` / `SKIPPED`

**Deliverables**:
- Architecture decision notes (inline comments or brief doc)
- Final finding status model
- Confirmed step wiring design

**Exit criteria**:
- SIGINT strategy validated against `ClaudeProcess` behavior
- Hash algorithm confirmed
- No structural ambiguity remains for Phases 1–3

---

### Phase 1: Foundation — Models, State Shape, and Parsing Infrastructure
**Duration**: 2–3 days | **Milestone**: M1 — Data model, parser, and state shape ready

**Deliverables**:
1. `Finding` dataclass with all specified fields (id, severity, dimension, description, location, evidence, fix_guidance, files_affected, status, agreement_category) — FR-007
2. State schema shape definition: `.roadmap-state.json` extended with `remediate` and `certify` step entry structures, additive fields only — FR-029, NFR-009. Field details finalized in Phase 5 based on implementation evidence.
3. Primary report parser (`remediate_parser.py`) for `validate/reflect-merged.md` and `validate/merged-validation-report.md` — FR-001
4. Fallback parser for individual `reflect-*` reports with deduplication (same file, within 5 lines, higher severity wins) — FR-031
5. Unit tests for both parser paths against 3+ known report format variants — R-002 mitigation

**Analyzer Priority**: Parser resilience is a critical dependency for every downstream phase. Use fixture-based tests for known report variants. Fail loudly when required structured fields are absent.

**Architectural constraints enforced**:
- `Finding` lives in `roadmap.models` (importable by downstream modules)
- Parser is a pure function (NFR-004) — takes string input, returns `list[Finding]`
- All file reads use existing I/O patterns

**New modules created**:

| Module | Imports From | Imported By |
|--------|-------------|-------------|
| `roadmap/models.py` (extend `Finding`) | `pipeline.models` | `remediate_*`, `certify_*`, `remediate_parser` |
| `remediate_parser.py` | `roadmap.models` | `remediate_executor.py` |

**Exit criteria**:
- Parser produces correct `Finding` lists from 3+ report format variants
- State schema shape passes backward-compatibility check (existing consumers unaffected)
- 100% unit test coverage on parser and data model

---

### Phase 2: Interactive Prompt, Filtering, and Remediation Tasklist Plan
**Duration**: 1–1.5 days | **Milestone**: M2 — User prompt, filter, and tasklist plan artifact operational

This phase produces the remediation tasklist as a **planning artifact** before agents execute. The tasklist is updated with outcomes post-execution in Phase 3.

**Deliverables**:
1. Terminal summary printer: findings grouped by severity with IDs and descriptions — FR-002
2. Interactive 4-option prompt in `execute_roadmap()` (NOT in `execute_pipeline()`) — FR-003, FR-032, NFR-014
3. Scope filter: Option 1 → BLOCKING only, Option 2 → BLOCKING+WARNING, Option 3 → all with fix_guidance — FR-008
4. Auto-SKIP logic for NO_ACTION_REQUIRED and OUT_OF_SCOPE findings — FR-010
5. Zero-findings guard: 0 actionable → emit stub tasklist (`actionable: 0`, all findings SKIPPED), proceed to certify — FR-006, FR-009
6. Skip-remediation path: user selects `n` → save state as `validated-with-issues` → end — FR-004
7. `remediation-tasklist.md` generation with full YAML frontmatter and grouped entries — FR-016
8. `REMEDIATE_GATE` definition with required fields, minimum line count, semantic validation — FR-017, FR-020

**Analyzer Priority**: This phase defines the control surface users see; behavior must be deterministic. Prompt handling must stay outside `execute_pipeline()` to preserve architecture. Tasklist output becomes the audit trail for remediation, so schema rigor matters.

**Architectural constraints enforced**:
- Prompt logic lives in `execute_roadmap()`, preserving `execute_pipeline()` non-interactive contract — FR-032
- Filter functions are pure (NFR-004)
- Tasklist is a planning record; outcomes (FIXED/FAILED) are written by Phase 3

**Exit criteria**:
- All 4 prompt paths tested (options 1, 2, 3, n)
- Zero-findings guard produces correct stub output
- No I/O in filter/scope functions
- `remediation-tasklist.md` validates against `REMEDIATE_GATE` schema (pre-execution state)

---

### Phase 3: Remediation Orchestrator
**Duration**: 4–6 days | **Milestone**: M3 — Parallel remediation with rollback operational

This is the **highest-complexity phase** (agent orchestration + transactional rollback). Follow the 8-step internal build order to manage dependencies.

**Deliverables**:
1. File-level grouping: batch actionable findings by primary target file — FR-011
2. Cross-file finding handling: include in both agents' prompts with scoped guidance — FR-013. Cross-file prompt structure follows spec §2.3.4 examples (including 'Fix Guidance (YOUR FILE):' and 'Note:' fields).
3. Prompt builder (`remediate_prompts.py`): pure function producing agent prompts with target file, finding details, constraints — FR-014, NFR-004. Prompt template per spec §2.3.4.
4. File allowlist enforcement: agents may ONLY edit `roadmap.md`, `extraction.md`, `test-strategy.md` — FR-015
5. Pre-remediate snapshots: `<file>.pre-remediate` before agent spawn — FR-021
6. Parallel agent execution via `ClaudeProcess` (not `execute_pipeline()`) — FR-012, FR-019, NFR-006
7. Timeout enforcement: 300s per agent, single retry — NFR-001, NFR-002
8. Failure handling: halt remaining agents, rollback all files, mark FAILED — FR-022
9. Success handling: delete snapshots, mark FIXED — FR-023
10. Tasklist update: write outcomes (FIXED/FAILED/SKIPPED) to existing `remediation-tasklist.md` — second write of two-write model
11. Step registration: `remediate` step with `REMEDIATE_GATE` — FR-017, FR-020. Note: step registration exposes remediate as a single step to the outer `execute_pipeline()` while internal orchestration uses `ClaudeProcess` directly (see deliverable #6).
12. Context isolation: agents receive only prompt + `--file`, no session flags — NFR-003
13. Model inheritance from parent pipeline config — NFR-010
14. YAML frontmatter and heading preservation by agents — NFR-013

**Implementation sequence** (internal dependencies):
1. Prompt builder (pure, testable in isolation)
2. Grouping + filtering logic (pure)
3. Snapshot mechanism
4. Agent spawning with `ClaudeProcess`
5. Parallel execution coordinator
6. Rollback/success handlers
7. Tasklist updater
8. Gate definition and step registration

**Analyzer Priority**: Rollback logic must be tested before parallel agent execution is considered complete. Parallelism is valuable, but only after same-file conflict elimination is proven.

**New modules created**:

| Module | Imports From | Imported By |
|--------|-------------|-------------|
| `remediate_prompts.py` | `roadmap.models` | `remediate_executor.py` |
| `remediate_executor.py` | `pipeline.models`, `roadmap.models`, `pipeline.process` | `executor.py` |

**Architectural constraints enforced**:
- `remediate_executor.py` uses `ClaudeProcess` directly, matching `validate_executor.py` pattern — FR-018, FR-019
- Unidirectional imports: `remediate_*` → `pipeline.models` / `roadmap.models` only — NFR-007
- Atomic writes via tmp + `os.replace()` — NFR-005

**Exit criteria**:
- Parallel agents execute against different files concurrently
- Agent failure triggers full rollback (verified by checking file contents match snapshots)
- No files outside allowlist are modified
- Updated `remediation-tasklist.md` passes `REMEDIATE_GATE` validation with outcome statuses
- ≤30% wall-clock overhead vs steps 1–9 (NFR-008)

---

### Phase 4: Certification Step
**Duration**: 2–3 days | **Milestone**: M4 — Certification agent and report operational

**Deliverables**:
1. Certification prompt builder (`certify_prompts.py`): pure function, scoped sections only (not full file) — FR-024, NFR-004, NFR-011
2. Certification context extractor: assembles only relevant sections around finding locations to control token scope
3. `certification-report.md` with YAML frontmatter (findings_verified, findings_passed, findings_failed, certified, certification_date) and per-finding PASS/FAIL table with justifications — FR-025
4. Outcome routing: all pass → `certified: true`, `tasklist_ready: true`; some fail → `certified-with-caveats` — FR-026, FR-027
5. `CERTIFY_GATE` with required frontmatter, min 15 lines, semantic checks, per-finding table presence — FR-028
6. Step registration via `execute_pipeline([certify_step])` — per §2.5
7. No automatic loop — single pass only — NFR-012

**Analyzer Priority**: Keep certification narrow enough to control token cost but broad enough to avoid false passes. Certification must be skeptical by design; justification quality matters as much as PASS/FAIL labels.

**New modules created**:

| Module | Imports From | Imported By |
|--------|-------------|-------------|
| `certify_prompts.py` | `roadmap.models` | certify step |
| `certify_gates.py` | `pipeline.models`, `roadmap.models` | `certify_executor.py` |
| `certify_executor.py` | `pipeline.models`, `roadmap.models`, `certify_gates` | `execute_pipeline()` |

**Architectural constraints enforced**:
- Certify runs as standard Step via `execute_pipeline()` (unlike remediate) — §2.5
- Unidirectional imports — NFR-007
- Pure prompt builder — NFR-004

**Exit criteria**:
- Certification correctly identifies unfixed findings as FAIL (SC-003)
- ≥90% BLOCKING findings receive PASS when properly remediated (SC-002)
- Gate validation passes on well-formed reports
- Negative tests with intentionally unfixed findings confirm skeptical behavior

---

### Phase 5: Resume Support, State Finalization, and Backward Compatibility
**Duration**: 1.5–2 days | **Milestone**: M5 — Full resume support with stale detection

**Deliverables**:
1. State schema field finalization: complete metadata fields for `remediate` and `certify` entries based on Phases 2–4 implementation evidence — FR-029
2. `--resume` skip logic for remediate step (gate check) — FR-030
3. `--resume` skip logic for certify step (gate check) — FR-030
4. Stale hash detection: `source_report_hash` (SHA-256) comparison on resume — FR-030
5. Resume from each state: post-validate, post-remediate, post-certify — SC-004
6. State transitions: correct metadata fields written at each step boundary — FR-029
7. Backward-compatibility validation: old state files without new fields don't crash — SC-008

**Analyzer Priority**: Resume correctness is a high-leverage risk reducer. Stale detection is essential; otherwise resume may certify against outdated findings. Backward compatibility should be tested explicitly, not assumed.

**Exit criteria**:
- Resume from post-validate skips to remediate correctly
- Stale hash triggers re-execution (fail closed on mismatch)
- Resume from post-certify is a no-op
- Old state files without new fields handled gracefully
- Resume decisions are gate- and hash-based, not timestamp-only

---

### Phase 6: Integration Testing, Performance, and Release Hardening
**Duration**: 2–3 days | **Milestone**: M6 — Release-ready

**Deliverables**:
1. End-to-end integration test: full 12-step pipeline run — SC-001
2. Allowlist enforcement test: verify no files outside set are modified — SC-005
3. Performance test: ≤30% overhead for steps 10–11 — SC-006
4. Tasklist round-trip test: parse → emit → re-parse validates format — SC-007
5. Backward-compatibility test: old consumers + new state schema — SC-008
6. Deliberate-failure test: unfixed findings correctly reported as FAIL — SC-003
7. Edge case coverage: SIGINT during remediation, out-of-allowlist findings, zero-findings path, fallback parser path
8. Regression validation on pre-existing roadmap flows (steps 1–9)
9. Code review against architectural constraints: pure prompts, unidirectional imports, atomic writes, `ClaudeProcess` reuse

**Exit criteria**:
- All 8 success criteria (SC-001 through SC-008) pass
- No regressions in existing pipeline steps 1–9
- Performance benchmark report produced
- Release-readiness checklist complete

---

## 3. Risk Assessment and Mitigation

### High-Priority Risks

| ID | Risk | Severity | Probability | Mitigation | Phase |
|----|------|----------|-------------|------------|-------|
| R-001 | Remediation agent introduces new issues | Medium | Medium | Certification step catches regressions; full re-validation available | P4 |
| R-002 | Report format changes break parser | High | Low | Multi-format parser tests; fallback parsing path; graceful degradation; fixture-based coverage | P1 |
| R-003 | Rollback failure during multi-agent remediation | High | Medium | Snapshot every target before any agent starts; centralize rollback orchestration; test failure after first-agent-success + second-agent-timeout | P3 |
| R-004 | Cross-file findings cause conflicting edits | Medium | Low | Batch-by-file eliminates concurrent same-file edits; scoped guidance per agent; mark coupled failures on any agent failure | P3 |
| R-005 | Stale resume causing invalid certification | High | Medium | Require `source_report_hash` validation; fail closed on hash mismatch; gate- and hash-based resume decisions | P5 |
| R-006 | Certification false passes | Medium-High | Medium | Finding-scoped evidence windows; require explicit justification per finding; negative tests with intentionally unfixed findings; skeptical single-pass design | P4 |

### Secondary Risks

| ID | Risk | Severity | Probability | Mitigation | Phase |
|----|------|----------|-------------|------------|-------|
| R-007 | Atomic write race during rollback | Medium | Low | Use `os.replace()` for atomicity; test rollback under concurrent conditions | P3 |
| R-008 | `ClaudeProcess` behavior drift | Medium | Low | Pin to existing API; integration test validates matching behavior with `validate_executor` | P3 |
| R-009 | Allowlist mismatch with out-of-scope findings | Low | Medium | Deterministic SKIP + WARNING emission; covered in parser/filter tests | P2 |
| R-010 | Performance overhead exceeds SC-006 | Medium | Low | Minimal certification context; parallelism across disjoint files only; reuse existing process abstractions | P3, P4 |
| R-011 | State schema breaks existing consumers | Medium | Low | Additive fields only; regression test existing status and tasklist consumers | P1, P5 |

**Risk reduction strategy**: Phase 1 parser tests and Phase 3 rollback tests are the two highest-value test investments. Prioritize these if time-constrained.

---

## 4. Resource Requirements and Dependencies

### External Dependencies

| Dependency | Required By | Status Check |
|------------|-------------|-------------|
| v2.20-WorkflowEvolution pipeline infrastructure | All phases | Must be merged to working branch |
| `ClaudeProcess` API stability | Phase 3 | Verify no breaking changes planned |
| `GateCriteria` / `SemanticCheck` API | Phases 2–4 | Verify supports new gate definitions |
| `pipeline.models` / `roadmap.models` | Phase 1 | Verify import paths and available types |
| `validate_executor.py` pattern | Phase 0, 3 | Read and understand before implementing |
| `execute_roadmap()` in `executor.py` | Phase 2 | Verify extension points exist |

### New Module Summary

| Module | Phase | Imports From | Imported By |
|--------|-------|-------------|-------------|
| `remediate_parser.py` | P1 | `roadmap.models` | `remediate_executor.py` |
| `roadmap/models.py` (extend) | P1 | `pipeline.models` | all `remediate_*`, `certify_*` |
| `remediate_prompts.py` | P3 | `roadmap.models` | `remediate_executor.py` |
| `remediate_executor.py` | P3 | `pipeline.models`, `roadmap.models`, `pipeline.process` | `executor.py` |
| `certify_prompts.py` | P4 | `roadmap.models` | certify step |
| `certify_gates.py` | P4 | `pipeline.models`, `roadmap.models` | `certify_executor.py` |
| `certify_executor.py` | P4 | `pipeline.models`, `roadmap.models`, `certify_gates` | `execute_pipeline()` |

### Test File Inventory

| Test File | Coverage | Phase |
|-----------|----------|-------|
| `tests/roadmap/test_remediate_parser.py` | Finding extraction from various report formats | P1 |
| `tests/roadmap/test_remediate_prompts.py` | Prompt construction, file grouping, constraint injection | P3 |
| `tests/roadmap/test_remediate_executor.py` | Orchestration flow, agent batching, status collection | P3 |
| `tests/roadmap/test_certify_prompts.py` | Certification prompt with finding checklist | P4 |
| `tests/roadmap/test_certify_gates.py` | Gate criteria validation | P4 |
| `tests/roadmap/test_pipeline_integration.py` | End-to-end: validate → prompt → remediate → certify | P6 |

### Token and Cost Estimates

- Remediation agents: ~2–4K tokens per agent prompt × N files (typically 2–3 files) = ~6–12K total
- Certification agent: ~2–3K tokens (scoped sections only, per NFR-011)
- Overhead target: ≤30% wall-clock vs steps 1–9 (NFR-008)

### Engineering Resources

1. **Primary backend/pipeline engineer**: Pipeline orchestration, state/resume logic, rollback semantics
2. **QA/test support**: Parser fixtures, integration tests, performance validation
3. **Reviewer**: Architecture verification, failure-mode review, acceptance criteria traceability

---

## 5. Success Criteria and Validation Approach

### Success Criteria Mapping

| Criterion | Measurement | Phase |
|-----------|-------------|-------|
| SC-001: Full 12-step completion | End-to-end run succeeds through certify | P6 |
| SC-002: ≥90% BLOCKING findings pass certification | `findings_passed / findings_verified` ≥ 0.90 on controlled corpus | P6 |
| SC-003: No false passes on unfixed findings | Deliberate-failure test with unresolved findings → FAIL with justification | P6 |
| SC-004: Correct `--resume` behavior | Resume from post-validate, post-remediate, post-certify; stale-hash mismatch | P5 |
| SC-005: No out-of-scope file edits | Workspace diff before/after restricted to allowlist | P6 |
| SC-006: ≤30% wall-clock overhead | Benchmark steps 10–11 vs steps 1–9 baseline | P6 |
| SC-007: Accurate tasklist status reporting | Round-trip parse/render verification | P3 |
| SC-008: Backward-compatible state schema | Regression tests against pre-existing consumers | P1, P5 |

### Validation Layers

1. **Unit tests**: Parsing, deduplication, filtering, prompt builders, hash validation — per phase for all pure functions
2. **Integration tests**: Prompt flow, remediation orchestration, rollback, certification, end-to-end pipeline — Phase 6
3. **Contract tests**: Gate outputs, state schema, output frontmatter — Phases 2–4
4. **Performance tests**: Timing overhead, token-scope control for certification — Phase 6
5. **Failure-path tests**: Timeout, retry exhaustion, stale resume, interruption handling, deliberate unfixed findings — Phases 3–6

No mocking of `ClaudeProcess` in integration tests — use real subprocess execution.

---

## 6. Timeline Estimates

**Sprint assumption**: 1 sprint ≈ 3–5 working days. The spec's 3–5 sprint estimate (15–25 days) aligns with this roadmap's 13.5–19 day estimate accounting for parallel phase overlap.

| Phase | Duration | Depends On | Can Overlap With |
|-------|----------|-----------|-----------------|
| P0: Discovery | 0.5 days | v2.20 merged | — |
| P1: Foundation | 2–3 days | P0 | — |
| P2: Prompt & Tasklist | 1–1.5 days | P1 (Finding model) | P1 tail end |
| P3: Remediation Orchestrator | 4–6 days | P1, P2 | — |
| P4: Certification | 2–3 days | P3 (tasklist output) | P3 tail end (prompt builder only) |
| P5: Resume & State | 1.5–2 days | P3, P4 | P4 tail end |
| P6: Integration & Hardening | 2–3 days | P3, P4, P5 | — |
| **Total** | **13.5–19 days** | | **~11–15 with overlap** |

**Critical path**: P0 → P1 → P3 → P4 → P6 (11–15.5 days minimum)

**Parallel opportunities**:
- P2 can start once `Finding` dataclass is defined (P1 day 2)
- P4 prompt builder can start during P3 (needs only `Finding` model, not full orchestrator)
- P5 can start once remediate step is functional (P3 end)

### Phase Mapping — Spec to Roadmap

| Spec Phase | Spec Scope | Roadmap Phase(s) |
|------------|-----------|-----------------|
| Phase 1: Parser + Models (1 sprint) | Finding dataclass, parser, tests | P0 (Discovery) + P1 (Foundation) |
| Phase 2: Remediation Executor (1-2 sprints) | Prompt builders, executor, tasklist | P2 (Prompt & Tasklist) + P3 (Orchestrator) |
| Phase 3: Certification (1 sprint) | Certify prompts, gates, report | P4 (Certification) |
| Phase 4: Pipeline Integration (0.5-1 sprint) | Wiring, state, resume, E2E tests | P5 (Resume & State) + P6 (Integration) |

---

## 7. Open Questions — Resolutions and Defaults

### Resolved in Phase 0 (structural impact)

| OQ | Question | Resolution |
|----|----------|------------|
| OQ-001 | SIGINT during remediation | Validate `ClaudeProcess` subprocess cleanup behavior. If signal forwarding not needed: leave `.pre-remediate` files for manual recovery, document in user guide. If signal forwarding required: implement in Phase 3 snapshot mechanism. |
| OQ-002 | Hash algorithm for `source_report_hash` | SHA-256. Validate against existing hash patterns in pipeline. |
| OQ-003 | Step wiring design | `remediate` uses `ClaudeProcess` directly (like `validate_executor`); `certify` uses `execute_pipeline()` (standard step). |

### Deferred with defaults (behavioral impact only)

| OQ | Question | Default |
|----|----------|---------|
| OQ-004 | Findings referencing non-allowlist files | SKIP with WARNING log message; include in tasklist as SKIPPED with reason |
| OQ-005 | Section-to-line resolution for deduplication | Line-number based only; section references treated as approximate |
| OQ-006 | Certify gate when `certification-report.md` doesn't exist | Gate fails (file missing = step not run); resume logic handles this |
| OQ-007 | CONFLICT agreement findings | Include in remediation with both perspectives in fix_guidance; flag in prompt |
| OQ-008 | Schema version bump | Keep `schema_version: 2` if current; if bumping, add migration guard reading both versions |

---

## 8. Implementation Checklist

Summary checklist synthesized from both variant perspectives:

1. **Do not start with agent orchestration** — build parser, tasklist, and state contracts first
2. **Treat rollback as a release gate** — if rollback is not deterministic, the feature is not ready
3. **Resolve structural questions before Phase 1** — SIGINT handling, hash algorithm, step wiring
4. **Optimize for correctness before speed** — stale resume and false certification are more damaging than slower execution
5. **Use SC-001 through SC-008 as an implementation checklist** — every phase should map to specific criteria with explicit evidence
6. **Tasklist is a two-write artifact** — create as plan (Phase 2), update with outcomes (Phase 3)
7. **State schema is a two-stage design** — define shape (Phase 1), finalize fields (Phase 5)

---

## 9. Requirements Traceability Matrix

Mapping of requirement IDs referenced throughout this roadmap to their spec source sections.

### Functional Requirements (FR)

| ID | Description | Spec Reference |
|----|-------------|---------------|
| FR-001 | Parse merged validation report | §2.3.1 |
| FR-002 | Terminal summary of findings by severity | §2.3.2 |
| FR-003 | Context isolation for interactive prompt | §2.3.3 |
| FR-004 | Skip-remediation path | §2.3.3 |
| FR-006 | Zero-findings guard | §2.3.3 |
| FR-007 | Finding dataclass fields | §2.3.1 |
| FR-008 | Scope filter by severity | §2.3.3 |
| FR-009 | Stub tasklist on zero findings | §2.3.3 |
| FR-010 | Auto-SKIP for NO_ACTION_REQUIRED / OUT_OF_SCOPE | §2.3.3 |
| FR-011 | File-level grouping of findings | §2.3.4 |
| FR-012 | Parallel agent execution | §2.3.4 |
| FR-013 | Cross-file finding handling | §2.3.4 |
| FR-014 | Agent prompt structure | §2.3.4 |
| FR-015 | File allowlist enforcement | §2.3.5 |
| FR-016 | Remediation tasklist generation | §2.3.6 |
| FR-017 | REMEDIATE_GATE definition | §2.3.7 |
| FR-018 | Remediate step uses ClaudeProcess pattern | §2.3.4 |
| FR-019 | Agent spawning via ClaudeProcess | §2.3.4 |
| FR-020 | Gate semantic checks | §2.3.7 |
| FR-021 | Pre-remediate snapshots | §2.3.5 |
| FR-022 | Failure handling with rollback | §2.3.5 |
| FR-023 | Success handling with snapshot cleanup | §2.3.5 |
| FR-024 | Certification prompt builder | §2.4.2 |
| FR-025 | Certification report format | §2.4.3 |
| FR-026 | Outcome routing (all pass) | §2.4.4 |
| FR-027 | Outcome routing (partial fail) | §2.4.4 |
| FR-028 | CERTIFY_GATE definition | §2.4.5 |
| FR-029 | State schema extensions | §3.1 |
| FR-030 | Resume behavior | §3.2 |
| FR-031 | Fallback parser with dedup | §8/OQ-003 |
| FR-032 | Non-interactive pipeline contract | §2.5 |

### Non-Functional Requirements (NFR)

| ID | Description | Spec Reference |
|----|-------------|---------------|
| NFR-001 | 300s timeout per agent | §2.3.4 |
| NFR-002 | Single retry on failure | §2.3.4 |
| NFR-003 | Context isolation (no session flags) | §5.1 |
| NFR-004 | Pure prompt functions | §5.1 |
| NFR-005 | Atomic writes (tmp + os.replace) | §5.1 |
| NFR-006 | ClaudeProcess reuse | §5.1 |
| NFR-007 | Unidirectional imports | §5.1 |
| NFR-008 | ≤30% wall-clock overhead | §7/SC-006 |
| NFR-009 | Backward-compatible state schema | §7/SC-008 |
| NFR-010 | Model inheritance from config | §2.3.4 |
| NFR-011 | Scoped certification context | §2.4.2/OQ-002 |
| NFR-012 | No automatic loop | §2.4.4 |
| NFR-013 | Preserve YAML/heading structure | §2.3.4 |
| NFR-014 | Prompt outside execute_pipeline | §2.5 |
