

---
spec_source: "spec-roadmap-remediate.md"
complexity_score: 0.72
primary_persona: architect
generated: "2026-03-09"
phases: 6
total_requirements: 46
estimated_duration: "3-4 weeks"
---

# v2.22 RoadmapRemediate — Project Roadmap

## 1. Executive Summary

This release adds two new pipeline steps — **remediate** (step 10) and **certify** (step 11) — to the existing `roadmap run` workflow. The feature parses adversarial validation findings, presents an interactive severity-scoped prompt, orchestrates parallel remediation agents with transactional rollback, and runs a certification pass to verify fixes.

**Architectural signature**: Multi-agent orchestration with file-level batching, snapshot-based rollback, and strict import/edit constraints — all integrated into the existing pipeline without breaking backward compatibility.

**Key risks**: Report format fragility (R-002), cross-file coupling (R-003). Both are mitigated by design (fallback parser, batch-by-file strategy).

**Critical path**: Phase 2 (finding parser + data model) → Phase 3 (remediation orchestrator) → Phase 4 (certification) — these are sequential dependencies. Phases 1 and 5 can overlap with adjacent phases.

---

## 2. Phased Implementation Plan

### Phase 1: Foundation — Models, State, and Parsing Infrastructure
**Duration**: 3-4 days | **Milestone**: M1 — Data model and state schema ready

**Deliverables**:
1. `Finding` dataclass with all specified fields (id, severity, dimension, description, location, evidence, fix_guidance, files_affected, status, agreement_category) — FR-007
2. Extended `.roadmap-state.json` schema with `remediate` and `certify` step entries, additive fields only — FR-029, NFR-009
3. Primary report parser for `validate/reflect-merged.md` and `validate/merged-validation-report.md` — FR-001
4. Fallback parser for individual `reflect-*` reports with deduplication (location-match within 5 lines, higher severity wins) — FR-031
5. Unit tests for both parser paths against known report formats — R-002 mitigation

**Architectural constraints enforced**:
- `Finding` lives in `roadmap.models` (importable by downstream modules)
- Parser is a pure function (NFR-004) — takes string input, returns `list[Finding]`
- All file reads use existing I/O patterns, no new abstractions

**Exit criteria**:
- Parser produces correct `Finding` lists from 3+ report format variants
- State schema passes backward-compatibility check (existing consumers unaffected)
- 100% unit test coverage on parser and data model

---

### Phase 2: Interactive Prompt and Filtering Logic
**Duration**: 2-3 days | **Milestone**: M2 — User prompt and finding filter operational

**Deliverables**:
1. Terminal summary printer: findings grouped by severity with IDs and descriptions — FR-002
2. Interactive 4-option prompt in `execute_roadmap()` (NOT in `execute_pipeline()`) — FR-003, FR-032, NFR-014
3. Scope filter: Option 1 → BLOCKING only, Option 2 → BLOCKING+WARNING, Option 3 → all with fix_guidance — FR-008
4. Auto-SKIP logic for NO_ACTION_REQUIRED and OUT_OF_SCOPE findings — FR-010
5. Zero-findings guard: 0 actionable → emit stub tasklist, proceed to certify — FR-006, FR-009
6. Skip-remediation path: user selects `n` → save state as `validated-with-issues` → end — FR-004

**Architectural constraints enforced**:
- Prompt logic lives in `execute_roadmap()`, preserving `execute_pipeline()` non-interactive contract — FR-032
- Filter functions are pure (NFR-004)

**Exit criteria**:
- All 4 prompt paths tested (options 1, 2, 3, n)
- Zero-findings guard produces correct stub output
- No I/O in filter/scope functions

---

### Phase 3: Remediation Orchestrator
**Duration**: 5-7 days | **Milestone**: M3 — Parallel remediation with rollback operational

This is the **highest-complexity phase** (agent orchestration + transactional rollback).

**Deliverables**:
1. File-level grouping: batch actionable findings by primary target file — FR-011
2. Cross-file finding handling: include in both agents' prompts with scoped guidance — FR-013
3. Prompt builder (`remediate_prompts.py`): pure function producing agent prompts with target file, finding details, constraints — FR-014, NFR-004
4. File allowlist enforcement: agents may ONLY edit `roadmap.md`, `extraction.md`, `test-strategy.md` — FR-015
5. Pre-remediate snapshots: `<file>.pre-remediate` before agent spawn — FR-021
6. Parallel agent execution via `ClaudeProcess` (not `execute_pipeline()`) — FR-012, FR-019, NFR-006
7. Timeout enforcement: 300s per agent, single retry — NFR-001, NFR-002
8. Failure handling: halt remaining agents, rollback all files, mark FAILED — FR-022
9. Success handling: delete snapshots, mark FIXED — FR-023
10. `remediation-tasklist.md` emission with full YAML frontmatter and per-finding status — FR-016
11. Step registration: `remediate` step with `REMEDIATE_GATE` — FR-017, FR-020
12. Context isolation: agents receive only prompt + `--file`, no session flags — NFR-003
13. Model inheritance from parent pipeline config — NFR-010
14. YAML frontmatter and heading preservation by agents — NFR-013

**Architectural constraints enforced**:
- `remediate_executor.py` uses `ClaudeProcess` directly, matching `validate_executor.py` pattern — FR-018, FR-019
- Unidirectional imports: `remediate_*` → `pipeline.models` / `roadmap.models` only — NFR-007
- Atomic writes via tmp + `os.replace()` — NFR-005

**Implementation sequence** (internal dependencies):
1. Prompt builder (pure, testable in isolation)
2. Grouping + filtering logic (pure)
3. Snapshot mechanism
4. Agent spawning with `ClaudeProcess`
5. Parallel execution coordinator
6. Rollback/success handlers
7. Tasklist emitter
8. Gate definition and step registration

**Exit criteria**:
- Parallel agents execute against different files concurrently
- Agent failure triggers full rollback (verified by checking file contents match snapshots)
- No files outside allowlist are modified
- `remediation-tasklist.md` passes `REMEDIATE_GATE` validation
- ≤30% wall-clock overhead vs steps 1-9 (NFR-008)

---

### Phase 4: Certification Step
**Duration**: 3-4 days | **Milestone**: M4 — Certification agent and report operational

**Deliverables**:
1. Certification prompt builder (`certify_prompts.py`): pure function, scoped sections only (not full file) — FR-024, NFR-004, NFR-011
2. `certification-report.md` with YAML frontmatter and per-finding PASS/FAIL table — FR-025
3. Outcome routing: all pass → `certified: true`, `tasklist_ready: true`; some fail → `certified-with-caveats` — FR-026, FR-027
4. `CERTIFY_GATE` with required frontmatter, min 15 lines, semantic checks — FR-028
5. Step registration via `execute_pipeline([certify_step])` — per §2.5
6. No automatic loop — single pass only — NFR-012

**Architectural constraints enforced**:
- Certify runs as standard Step via `execute_pipeline()` (unlike remediate) — §2.5
- Unidirectional imports — NFR-007
- Pure prompt builder — NFR-004

**Exit criteria**:
- Certification correctly identifies unfixed findings as FAIL (SC-003)
- ≥90% BLOCKING findings receive PASS when properly remediated (SC-002)
- Gate validation passes on well-formed reports

---

### Phase 5: Resume Support and State Integration
**Duration**: 2-3 days | **Milestone**: M5 — Full resume support for new steps

**Deliverables**:
1. `--resume` skip logic for remediate step (gate check) — FR-030
2. `--resume` skip logic for certify step (gate check) — FR-030
3. Stale hash detection: `source_report_hash` comparison on resume — FR-030
4. Resume from each state: post-validate, post-remediate, post-certify — SC-004
5. State transitions: correct metadata fields written at each step boundary — FR-029

**Exit criteria**:
- Resume from post-validate skips to remediate correctly
- Stale hash triggers re-execution (not skip)
- Resume from post-certify is a no-op
- Backward-compatible: old state files without new fields don't crash (SC-008)

---

### Phase 6: Integration Testing and Hardening
**Duration**: 2-3 days | **Milestone**: M6 — Release-ready

**Deliverables**:
1. End-to-end integration test: full 12-step pipeline run — SC-001
2. Allowlist enforcement test: verify no files outside set are modified — SC-005
3. Performance test: ≤30% overhead for steps 10-11 — SC-006
4. Tasklist round-trip test: parse → emit → re-parse validates format — SC-007
5. Backward-compatibility test: old consumers + new state schema — SC-008
6. Deliberate-failure test: unfixed findings correctly reported as FAIL — SC-003
7. Edge case coverage: SIGINT during remediation (OQ-NEW-001), out-of-allowlist findings (OQ-NEW-002)

**Exit criteria**:
- All 8 success criteria (SC-001 through SC-008) pass
- No regressions in existing pipeline steps 1-9
- Open questions resolved or documented with chosen defaults

---

## 3. Risk Assessment and Mitigation

| ID | Risk | Severity | Probability | Mitigation | Phase Addressed |
|----|------|----------|-------------|------------|-----------------|
| R-001 | Remediation agent introduces new issues | Medium | Medium | Certification step catches regressions; full re-validation available | P4 |
| R-002 | Report format changes break parser | High | Low | Multi-format parser tests; fallback parsing path; graceful degradation | P1 |
| R-003 | Cross-file findings cause conflicting edits | Medium | Low | Batch-by-file eliminates concurrent same-file edits; scoped guidance per agent | P3 |
| R-004 | User interrupts during remediation | Low | Low | `.pre-remediate` snapshots enable manual rollback; resume picks up from last step | P3, P5 |
| R-005 | Certification agent too lenient | Low | Medium | Structured gate criteria; user can re-run full adversarial validation | P4 |
| R-NEW-001 | Rollback mechanism fails on atomic write race | Medium | Low | Use `os.replace()` for atomicity; test rollback under concurrent conditions | P3 |
| R-NEW-002 | `ClaudeProcess` behavior drift from `validate_executor` pattern | Medium | Low | Pin to existing API; integration test validates matching behavior | P3 |

**Risk reduction strategy**: Phase 1 parser tests and Phase 3 rollback tests are the two highest-value test investments. Prioritize these if time-constrained.

---

## 4. Resource Requirements and Dependencies

### External Dependencies (must be stable before work begins)

| Dependency | Required By | Status Check |
|------------|-------------|-------------|
| v2.20-WorkflowEvolution pipeline infrastructure | All phases | Must be merged to working branch |
| `ClaudeProcess` API stability | Phase 3 | Verify no breaking changes planned |
| `GateCriteria` / `SemanticCheck` API | Phases 3-4 | Verify supports new gate definitions |
| `pipeline.models` / `roadmap.models` | Phase 1 | Verify import paths and available types |
| `validate_executor.py` pattern | Phase 3 | Read and understand before implementing |
| `execute_roadmap()` in `executor.py` | Phase 2 | Verify extension points exist |

### New Modules to Create

| Module | Phase | Imports From | Imported By |
|--------|-------|-------------|-------------|
| `roadmap/models.py` (extend `Finding`) | P1 | `pipeline.models` | `remediate_*`, `certify_*` |
| `remediate_prompts.py` | P3 | `roadmap.models` | `remediate_executor.py` |
| `remediate_executor.py` | P3 | `pipeline.models`, `roadmap.models`, `pipeline.process` | `executor.py` |
| `certify_prompts.py` | P4 | `roadmap.models` | certify step |
| `certify_executor.py` | P4 | `pipeline.models`, `roadmap.models` | `execute_pipeline()` |
| `finding_parser.py` | P1 | `roadmap.models` | `remediate_executor.py` |

### Token/Cost Estimates

- Remediation agents: ~2-4K tokens per agent prompt × N files (typically 2-3 files) = ~6-12K total
- Certification agent: ~2-3K tokens (scoped sections only, per NFR-011)
- Overhead target: ≤30% wall-clock vs steps 1-9 (NFR-008)

---

## 5. Success Criteria and Validation Approach

| Criterion | Measurement | Test Type | Phase |
|-----------|-------------|-----------|-------|
| SC-001: Full 12-step completion | End-to-end run succeeds | Integration | P6 |
| SC-002: ≥90% BLOCKING findings pass certification | `findings_passed / findings_verified` ≥ 0.90 | Integration | P6 |
| SC-003: Unfixed findings reported as FAIL | Deliberate-failure test | Integration | P6 |
| SC-004: Resume correctness | Resume from 3 states | Integration | P5 |
| SC-005: No out-of-allowlist edits | File modification audit | Integration | P6 |
| SC-006: ≤30% overhead | Timing measurement | Performance | P6 |
| SC-007: Tasklist format accuracy | Round-trip parse test | Unit | P3 |
| SC-008: Backward-compatible state | Old consumer test | Unit | P1, P5 |

**Validation strategy**: Unit tests per phase for pure functions (parsers, filters, prompt builders). Integration tests in Phase 6 for end-to-end flows. No mocking of `ClaudeProcess` in integration tests — use real subprocess execution.

---

## 6. Timeline Estimates

| Phase | Duration | Depends On | Can Overlap With |
|-------|----------|-----------|-----------------|
| P1: Foundation | 3-4 days | v2.20 merged | — |
| P2: Interactive Prompt | 2-3 days | P1 (Finding model) | P1 tail end |
| P3: Remediation Orchestrator | 5-7 days | P1, P2 | — |
| P4: Certification | 3-4 days | P3 (tasklist output) | P3 tail end |
| P5: Resume Support | 2-3 days | P3, P4 | P4 tail end |
| P6: Integration Testing | 2-3 days | P3, P4, P5 | — |
| **Total** | **17-24 days** | | **~15-20 with overlap** |

**Critical path**: P1 → P3 → P4 → P6 (13-18 days minimum)

**Parallel opportunities**:
- P2 can start once `Finding` dataclass is defined (P1 day 2)
- P5 can start once remediate step is functional (P3 end)
- P4 prompt builder can start during P3 (needs only `Finding` model, not full orchestrator)

---

## 7. Open Questions — Recommended Resolutions

| OQ | Question | Recommended Default |
|----|----------|-------------------|
| OQ-NEW-001 | SIGINT during remediation — cleanup snapshots? | Leave `.pre-remediate` files for manual recovery; document in user guide |
| OQ-NEW-002 | Findings referencing non-allowlist files | SKIP with WARNING log message; include in tasklist as SKIPPED with reason |
| OQ-NEW-003 | Hash algorithm for `source_report_hash` | SHA-256; document in state schema |
| OQ-NEW-004 | Section-to-line resolution for deduplication | Line-number based only; section references treated as approximate |
| OQ-NEW-005 | Certify gate when `certification-report.md` doesn't exist | Gate fails (file missing = step not run); resume logic handles this |
| OQ-NEW-006 | CONFLICT agreement findings | Include in remediation with both perspectives in fix_guidance; flag in prompt |
| OQ-NEW-007 | Schema version bump | Keep `schema_version: 2` if already current; if bumping, add migration guard that reads both versions |
