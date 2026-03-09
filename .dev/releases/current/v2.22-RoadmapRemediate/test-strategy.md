---
validation_milestones: 7
interleave_ratio: '1:2'
---

# v2.22 RoadmapRemediate — Test Strategy

## 1. Validation Milestones Mapped to Roadmap Phases

### VM-0: Architecture Lock Validation (Phase 0, Day 0.5)
**Gate**: All structural decisions documented and verified

| Check | Method | Acceptance |
|-------|--------|------------|
| `ClaudeProcess` subprocess cleanup behavior under SIGINT | Manual spike: send SIGINT during subprocess, observe cleanup | Documented behavior with decision on signal forwarding vs manual recovery |
| SHA-256 hash compatibility with existing pipeline patterns | Grep existing hash usage in `pipeline/`, confirm no algorithm conflicts | No collisions; consistent algorithm across state files |
| Step wiring confirmation (remediate=direct, certify=pipeline) | Code review of `validate_executor.py` pattern + `execute_pipeline()` contract | Written confirmation with code references |
| `Finding` status lifecycle model (`SKIPPED` → `FIXED` / `FAILED`) | Review against existing `StepStatus` enum patterns in `pipeline.models` | No conflicts with existing status values |

**Exit**: Architecture decision notes committed. No unresolved structural ambiguity.

---

### VM-1: Foundation Validation (Phase 1, Days 1–3)
**Gate**: Parser produces correct output from all known report formats; data model is importable and backward-compatible

**Unit tests** (target: 100% coverage on parser + model):

| Test ID | Component | What It Tests | Priority |
|---------|-----------|---------------|----------|
| T-1.01 | `Finding` dataclass | All 10 fields instantiate correctly; defaults for optional fields | P0 |
| T-1.02 | `Finding` dataclass | Serialization round-trip (dataclass → dict → dataclass) | P0 |
| T-1.03 | `Finding` dataclass | Status transitions: only valid transitions allowed | P1 |
| T-1.04 | `finding_parser.py` | Parse `validate/reflect-merged.md` format → correct `Finding` list | P0 |
| T-1.05 | `finding_parser.py` | Parse `validate/merged-validation-report.md` format → correct `Finding` list | P0 |
| T-1.06 | `finding_parser.py` | Parse individual `reflect-*` reports (fallback path) → correct `Finding` list | P0 |
| T-1.07 | `finding_parser.py` | Deduplication: same file, within 5 lines → higher severity wins | P0 |
| T-1.08 | `finding_parser.py` | Deduplication: same file, >5 lines apart → both kept | P1 |
| T-1.09 | `finding_parser.py` | Malformed report (missing required fields) → raises structured error | P0 |
| T-1.10 | `finding_parser.py` | Empty report → returns empty list, no crash | P1 |
| T-1.11 | `finding_parser.py` | Parser is pure: no I/O calls, takes string input only | P0 |
| T-1.12 | State schema | New fields are additive; existing `.roadmap-state.json` loads without error | P0 |
| T-1.13 | State schema | Old consumers (tasklist gen, status queries) unaffected by new fields | P0 |

**Fixtures required**:
- `reflect-merged-v1.md` — standard merged report with 3+ findings across severities
- `merged-validation-report-v1.md` — alternate format with same content
- `reflect-opus-architect.md`, `reflect-haiku-analyzer.md` — individual reports for fallback
- `malformed-report.md` — missing severity field, truncated YAML
- `empty-report.md` — valid structure, zero findings
- `duplicate-findings-report.md` — same-file findings within and beyond 5-line threshold

**Interleave point**: Tests T-1.01–T-1.13 written and passing before Phase 2 begins.

---

### VM-2: Prompt & Tasklist Validation (Phase 2, Days 3–4.5)
**Gate**: All 4 prompt paths produce correct output; tasklist validates against `REMEDIATE_GATE`

**Unit tests**:

| Test ID | Component | What It Tests | Priority |
|---------|-----------|---------------|----------|
| T-2.01 | Terminal summary | Findings grouped by severity, correct counts, IDs visible | P1 |
| T-2.02 | Scope filter | Option 1 → only BLOCKING findings pass | P0 |
| T-2.03 | Scope filter | Option 2 → BLOCKING + WARNING pass | P0 |
| T-2.04 | Scope filter | Option 3 → all findings with fix_guidance pass | P0 |
| T-2.05 | Scope filter | Filter is pure function: no I/O | P0 |
| T-2.06 | Auto-SKIP | `NO_ACTION_REQUIRED` findings → SKIPPED regardless of scope | P0 |
| T-2.07 | Auto-SKIP | `OUT_OF_SCOPE` findings → SKIPPED regardless of scope | P0 |
| T-2.08 | Zero-findings guard | 0 actionable after filtering → stub tasklist with `actionable: 0` | P0 |
| T-2.09 | Zero-findings guard | 0 BLOCKING + 0 WARNING + 0 INFO → skip prompt, proceed to certify | P1 |
| T-2.10 | Skip path | User selects `n` → state saved as `validated-with-issues` | P0 |
| T-2.11 | Tasklist generation | `remediation-tasklist.md` has correct YAML frontmatter fields | P0 |
| T-2.12 | Tasklist generation | Findings grouped by severity in output | P1 |
| T-2.13 | `REMEDIATE_GATE` | Gate validates well-formed tasklist (pre-execution state) | P0 |
| T-2.14 | `REMEDIATE_GATE` | Gate rejects tasklist missing required frontmatter | P0 |
| T-2.15 | `REMEDIATE_GATE` | Gate rejects tasklist below minimum line count | P1 |
| T-2.16 | Prompt placement | Interactive prompt logic resides in `execute_roadmap()`, NOT `execute_pipeline()` | P0 |

**Contract test**: `REMEDIATE_GATE` schema definition matches pattern in `tests/roadmap/test_gates_data.py`.

**Interleave point**: Tests T-2.01–T-2.16 passing before Phase 3 orchestration begins.

---

### VM-3: Remediation Orchestrator Validation (Phase 3, Days 4.5–10.5)
**Gate**: Parallel agents execute, rollback works deterministically, tasklist updated with outcomes

This is the highest-risk phase. Tests are ordered by the 8-step internal build sequence.

**Unit tests** (pure functions):

| Test ID | Component | What It Tests | Priority |
|---------|-----------|---------------|----------|
| T-3.01 | `remediate_prompts.py` | Prompt builder produces correct structure for single-file findings | P0 |
| T-3.02 | `remediate_prompts.py` | Prompt includes constraints section (allowlist, preservation rules) | P0 |
| T-3.03 | `remediate_prompts.py` | Cross-file finding includes scoped guidance + "other file handled separately" note | P0 |
| T-3.04 | `remediate_prompts.py` | Prompt builder is pure: no I/O, no subprocess | P0 |
| T-3.05 | File grouping | Findings batched by primary target file correctly | P0 |
| T-3.06 | File grouping | Single-file findings all go to one agent | P0 |
| T-3.07 | File grouping | Grouping is pure function | P1 |
| T-3.08 | Allowlist | Only `roadmap.md`, `extraction.md`, `test-strategy.md` in allowed set | P0 |
| T-3.09 | Allowlist | Finding referencing non-allowlist file → SKIPPED with WARNING | P0 |

**Integration tests** (require filesystem, subprocess):

| Test ID | Component | What It Tests | Priority |
|---------|-----------|---------------|----------|
| T-3.10 | Snapshot mechanism | `.pre-remediate` files created before agent spawn | P0 |
| T-3.11 | Snapshot mechanism | Snapshot contents match original file byte-for-byte | P0 |
| T-3.12 | Agent spawning | `ClaudeProcess` invoked with correct args (prompt + `--file`, no `--session`/`--resume`) | P0 |
| T-3.13 | Agent spawning | Model inherited from parent pipeline config | P1 |
| T-3.14 | Parallel execution | Agents targeting different files run concurrently (wall-clock < sum of individual) | P1 |
| T-3.15 | Timeout enforcement | Agent exceeding 300s is terminated | P0 |
| T-3.16 | Single retry | Failed agent retried once before declaring failure | P0 |
| T-3.17 | Failure → rollback | ANY agent failure triggers rollback of ALL files to snapshots | P0 |
| T-3.18 | Failure → rollback | Rollback restores exact original content (diff = 0) | P0 |
| T-3.19 | Failure → halt | Remaining agents halted after first failure | P0 |
| T-3.20 | Failure → status | Failed + cross-file findings marked FAILED | P0 |
| T-3.21 | Success → cleanup | `.pre-remediate` snapshots deleted on full success | P0 |
| T-3.22 | Success → status | All targeted findings marked FIXED | P0 |
| T-3.23 | Tasklist update | `remediation-tasklist.md` updated with FIXED/FAILED/SKIPPED statuses | P0 |
| T-3.24 | Tasklist update | Updated tasklist passes `REMEDIATE_GATE` validation | P0 |
| T-3.25 | Atomic writes | File writes use `tmp + os.replace()` pattern | P1 |
| T-3.26 | YAML preservation | Agent output preserves frontmatter structure and heading hierarchy | P1 |
| T-3.27 | Import direction | `remediate_executor.py` imports only from `pipeline.models`, `roadmap.models`, `pipeline.process` | P0 |

**Critical rollback test scenario** (R-003 mitigation):
- Agent-A succeeds (edits `roadmap.md`), Agent-B times out → verify `roadmap.md` rolled back to pre-remediate snapshot, Agent-B's target also rolled back, all findings marked FAILED.

**Interleave point**: T-3.01–T-3.09 (pure functions) passing before T-3.10+ (integration). T-3.17–T-3.20 (rollback) passing before parallel execution is considered complete.

---

### VM-4: Certification Validation (Phase 4, Days 8.5–13.5)
**Gate**: Certification correctly identifies fixed and unfixed findings; no false passes

**Unit tests**:

| Test ID | Component | What It Tests | Priority |
|---------|-----------|---------------|----------|
| T-4.01 | `certify_prompts.py` | Prompt scoped to relevant sections only (not full file) | P0 |
| T-4.02 | `certify_prompts.py` | Each finding's location context included | P0 |
| T-4.03 | `certify_prompts.py` | Prompt builder is pure function | P0 |
| T-4.04 | Context extractor | Extracts correct line ranges around finding locations | P0 |
| T-4.05 | Context extractor | Handles edge cases: finding at file start/end | P1 |

**Integration tests**:

| Test ID | Component | What It Tests | Priority |
|---------|-----------|---------------|----------|
| T-4.06 | Certification report | `certification-report.md` has required YAML frontmatter fields | P0 |
| T-4.07 | Certification report | Per-finding PASS/FAIL table present with justifications | P0 |
| T-4.08 | Outcome routing | All findings PASS → `certified: true`, `tasklist_ready: true` | P0 |
| T-4.09 | Outcome routing | Some findings FAIL → `certified-with-caveats` | P0 |
| T-4.10 | `CERTIFY_GATE` | Gate validates well-formed certification report | P0 |
| T-4.11 | `CERTIFY_GATE` | Gate rejects report missing per-finding table | P0 |
| T-4.12 | `CERTIFY_GATE` | Gate rejects report below 15-line minimum | P1 |
| T-4.13 | False pass detection | Deliberately unfixed finding → FAIL in certification (SC-003) | P0 |
| T-4.14 | False pass detection | Partially fixed finding (incomplete remediation) → FAIL | P0 |
| T-4.15 | Single pass | No automatic loop — certify runs once then stops | P0 |
| T-4.16 | Step registration | Certify runs via `execute_pipeline([certify_step])` | P0 |
| T-4.17 | Import direction | `certify_executor.py` imports only from `pipeline.models`, `roadmap.models` | P1 |

**Negative test corpus** (R-006 mitigation):
- Fixture with 3 findings: 1 properly fixed, 1 partially fixed (heading changed but content wrong), 1 untouched → expect 1 PASS, 2 FAIL.

---

### VM-5: Resume & State Validation (Phase 5, Days 11.5–15.5)
**Gate**: Resume works correctly from every pipeline state; stale detection prevents invalid certification

| Test ID | Component | What It Tests | Priority |
|---------|-----------|---------------|----------|
| T-5.01 | Resume skip | Post-validate state + gate passes → skip to remediate | P0 |
| T-5.02 | Resume skip | Post-remediate state + gate passes → skip to certify | P0 |
| T-5.03 | Resume skip | Post-certify state → no-op | P0 |
| T-5.04 | Stale detection | `source_report_hash` mismatch → re-execution triggered | P0 |
| T-5.05 | Stale detection | `source_report_hash` match → resume proceeds normally | P0 |
| T-5.06 | Stale detection | Missing hash field in old state → fail closed (re-execute) | P0 |
| T-5.07 | Backward compat | Old state file (no `remediate`/`certify` fields) loads without crash | P0 |
| T-5.08 | Backward compat | Existing consumers (tasklist gen, status queries) function with new fields | P0 |
| T-5.09 | State transitions | Correct metadata written at validate→remediate boundary | P1 |
| T-5.10 | State transitions | Correct metadata written at remediate→certify boundary | P1 |
| T-5.11 | State finalization | All state schema fields populated after full run | P1 |

---

### VM-6: Integration & Release Hardening (Phase 6, Days 13.5–19)
**Gate**: All SC-001 through SC-008 pass; no regressions in steps 1–9

**End-to-end tests**:

| Test ID | Success Criterion | What It Tests | Priority |
|---------|-------------------|---------------|----------|
| T-6.01 | SC-001 | Full 12-step pipeline run completes (extract → certify) | P0 |
| T-6.02 | SC-002 | ≥90% BLOCKING findings receive PASS on controlled corpus | P0 |
| T-6.03 | SC-003 | Deliberately unfixed findings → FAIL with justification | P0 |
| T-6.04 | SC-004 | Resume from post-validate, post-remediate, post-certify | P0 |
| T-6.05 | SC-005 | No files outside allowlist modified (workspace diff check) | P0 |
| T-6.06 | SC-006 | Steps 10–11 ≤30% wall-clock overhead vs steps 1–9 | P1 |
| T-6.07 | SC-007 | Tasklist round-trip: parse → emit → re-parse matches | P0 |
| T-6.08 | SC-008 | Old consumers + new state schema → no regressions | P0 |

**Edge case tests**:

| Test ID | Scenario | Expected Behavior | Priority |
|---------|----------|-------------------|----------|
| T-6.09 | SIGINT during remediation | Snapshots remain for manual recovery; no partial writes | P1 |
| T-6.10 | Out-of-allowlist findings | SKIPPED with WARNING log | P1 |
| T-6.11 | Zero findings path | Stub tasklist, vacuous certification | P0 |
| T-6.12 | Fallback parser path | Individual reports parsed when merged unavailable | P0 |
| T-6.13 | `CONFLICT` agreement findings | Included with both perspectives in fix_guidance | P1 |
| T-6.14 | All findings `NO_ACTION_REQUIRED` | All SKIPPED, vacuous certification | P1 |

**Regression tests**:

| Test ID | What It Tests | Priority |
|---------|---------------|----------|
| T-6.15 | Steps 1–9 produce identical output with new code present | P0 |
| T-6.16 | Existing gate definitions unchanged | P0 |
| T-6.17 | `execute_pipeline()` non-interactive contract preserved | P0 |

---

### VM-R: Release Readiness (Post-Phase 6)
**Gate**: Release checklist complete

| Check | Method |
|-------|--------|
| All SC-001–SC-008 passing | CI green |
| Performance benchmark report produced | T-6.06 output archived |
| Architectural constraints verified (code review) | Pure prompts, unidirectional imports, atomic writes, ClaudeProcess reuse |
| No TODO/FIXME in new code | `grep -r "TODO\|FIXME" src/superclaude/cli/roadmap/remediate_* certify_*` |
| Test coverage ≥90% on new modules | `uv run pytest --cov` on new files |

---

## 2. Test Categories

### Unit Tests (58 tests)
**Scope**: Pure functions, dataclasses, filters, prompt builders, gate definitions
**Location**: `tests/roadmap/test_remediate_*.py`, `tests/roadmap/test_certify_*.py`
**Runner**: `uv run pytest tests/roadmap/ -m unit`
**Fixtures**: String-based report fixtures, `Finding` factory helpers, `GATE` constant imports
**Characteristics**: No I/O, no subprocess, no filesystem — fast, deterministic, parallelizable

### Integration Tests (27 tests)
**Scope**: Orchestration flows, snapshot/rollback, `ClaudeProcess` spawning, state persistence, gate evaluation against real files
**Location**: `tests/roadmap/test_remediate_integration.py`, `tests/roadmap/test_certify_integration.py`
**Runner**: `uv run pytest tests/roadmap/ -m integration`
**Fixtures**: `tmp_dir`, `make_file`, mock `ClaudeProcess` with controlled exit codes (NOT mocked in E2E — real subprocess in T-6.*)
**Characteristics**: Filesystem I/O, controlled subprocess behavior, moderate execution time

### End-to-End Tests (8 tests)
**Scope**: Full 12-step pipeline, real `ClaudeProcess` execution, real file modifications
**Location**: `tests/sc-roadmap/integration/test_remediate_e2e.py`
**Runner**: `uv run pytest tests/sc-roadmap/integration/test_remediate_e2e.py -v`
**Characteristics**: Slow (minutes), real subprocess, full state lifecycle. Run in CI but not on every commit.

### Acceptance Tests (8 tests — SC-001 through SC-008)
**Scope**: Success criteria verification mapped 1:1 to spec
**Location**: `tests/roadmap/test_remediate_acceptance.py`
**Runner**: `uv run pytest tests/roadmap/test_remediate_acceptance.py -v`
**Characteristics**: Each test directly maps to one SC-* criterion. These are the release gate.

---

## 3. Test-Implementation Interleaving Strategy

**Ratio**: 1:2 (one test cycle for every two implementation tasks)

### Interleaving Schedule

```
P0: Discovery
  └─ No tests — architecture validation only

P1: Foundation (Days 1–3)
  ├─ Day 1: Implement Finding dataclass → Write T-1.01–T-1.03
  ├─ Day 2: Implement primary parser → Write T-1.04–T-1.05, T-1.09–T-1.11
  ├─ Day 2.5: Implement fallback parser + dedup → Write T-1.06–T-1.08
  └─ Day 3: State schema shape → Write T-1.12–T-1.13
  CHECKPOINT: All T-1.* green ✅

P2: Prompt & Tasklist (Days 3–4.5) [overlaps P1 tail]
  ├─ Day 3: Scope filter + auto-SKIP → Write T-2.02–T-2.07
  ├─ Day 3.5: Zero-findings guard → Write T-2.08–T-2.09
  ├─ Day 4: Tasklist generation + REMEDIATE_GATE → Write T-2.11–T-2.16
  └─ Day 4.5: Terminal summary + skip path → Write T-2.01, T-2.10
  CHECKPOINT: All T-2.* green ✅

P3: Remediation Orchestrator (Days 4.5–10.5)
  ├─ Day 4.5–5: Prompt builder (pure) → Write T-3.01–T-3.04
  ├─ Day 5–5.5: Grouping + allowlist → Write T-3.05–T-3.09
  │   CHECKPOINT: All pure-function tests green ✅
  ├─ Day 5.5–6.5: Snapshot mechanism → Write T-3.10–T-3.11
  ├─ Day 6.5–7.5: Agent spawning + ClaudeProcess → Write T-3.12–T-3.13
  ├─ Day 7.5–8.5: Parallel execution + timeout → Write T-3.14–T-3.16
  │   CHECKPOINT: Agent spawning works ✅
  ├─ Day 8.5–9.5: Rollback handlers → Write T-3.17–T-3.22
  │   CHECKPOINT: Rollback deterministic ✅ (RELEASE GATE)
  └─ Day 9.5–10.5: Tasklist updater + step registration → Write T-3.23–T-3.27
  CHECKPOINT: All T-3.* green ✅

P4: Certification (Days 8.5–13.5) [prompt builder overlaps P3]
  ├─ Day 8.5–9.5: Prompt builder + context extractor → Write T-4.01–T-4.05
  ├─ Day 10.5–11.5: Certification report + gates → Write T-4.06–T-4.12
  └─ Day 11.5–12.5: False pass tests + step wiring → Write T-4.13–T-4.17
  CHECKPOINT: All T-4.* green ✅

P5: Resume & State (Days 11.5–15.5) [overlaps P4 tail]
  ├─ Day 12.5–13.5: Resume skip logic → Write T-5.01–T-5.06
  └─ Day 13.5–14.5: Backward compat + state finalization → Write T-5.07–T-5.11
  CHECKPOINT: All T-5.* green ✅

P6: Integration & Hardening (Days 14.5–19)
  ├─ Day 14.5–16: E2E tests → Write T-6.01–T-6.08
  ├─ Day 16–17: Edge cases → Write T-6.09–T-6.14
  └─ Day 17–19: Regression + performance → Write T-6.15–T-6.17, benchmark
  CHECKPOINT: All T-6.* green, SC-001–SC-008 pass ✅
```

### Checkpoint Rules
- **No phase transition without green tests** from the current phase
- **Rollback tests (T-3.17–T-3.22) are a release gate** — if they don't pass, Phase 3 is not complete regardless of other progress
- **False-pass tests (T-4.13–T-4.14) are a release gate** — certification without skepticism is worse than no certification

---

## 4. Risk-Based Test Prioritization

### Tier 1: Must-Pass Before Any Merge (P0)

| Risk | Tests | Rationale |
|------|-------|-----------|
| R-002: Report format fragility | T-1.04–T-1.09 | Parser is the single dependency for all downstream phases |
| R-003: Rollback failure | T-3.17–T-3.22 | If rollback doesn't work, the feature is destructive |
| R-006: Certification false passes | T-4.13–T-4.14 | False confidence in certification undermines the entire feature |
| R-005: Stale resume | T-5.04–T-5.06 | Certifying against outdated findings is silently dangerous |
| SC-005: No out-of-scope edits | T-6.05 | File safety is non-negotiable |

### Tier 2: Must-Pass Before Release (P0–P1)

| Risk | Tests | Rationale |
|------|-------|-----------|
| SC-001: Full pipeline completion | T-6.01 | Core happy path |
| SC-008: Backward compatibility | T-1.12–T-1.13, T-5.07–T-5.08, T-6.08 | Existing users must not break |
| NFR-014: Non-interactive contract | T-2.16, T-6.17 | Architectural integrity |
| NFR-007: Import direction | T-3.27, T-4.17 | Prevents dependency cycles |

### Tier 3: Should-Pass (P1)

| Risk | Tests | Rationale |
|------|-------|-----------|
| SC-006: Performance overhead | T-6.06 | Important but not blocking |
| R-004: Cross-file conflicts | T-3.05–T-3.06 | Low probability by design |
| NFR-013: YAML preservation | T-3.26 | Important for output quality |

---

## 5. Acceptance Criteria Per Milestone

### M0 — Architecture Lock
- [ ] SIGINT behavior documented with code evidence
- [ ] SHA-256 confirmed compatible with existing patterns
- [ ] Step wiring design written and reviewed
- [ ] Finding lifecycle model defined

### M1 — Foundation Ready
- [ ] `Finding` dataclass instantiates with all 10 fields (T-1.01)
- [ ] Primary parser handles 2+ merged report formats (T-1.04, T-1.05)
- [ ] Fallback parser deduplicates correctly (T-1.07, T-1.08)
- [ ] Parser rejects malformed input with clear error (T-1.09)
- [ ] State schema additive — old files still load (T-1.12, T-1.13)
- [ ] 100% unit test coverage on `finding_parser.py` and `Finding`

### M2 — Prompt & Tasklist Operational
- [ ] All 4 prompt options produce correct filtering (T-2.02–T-2.05)
- [ ] Auto-SKIP for `NO_ACTION_REQUIRED`/`OUT_OF_SCOPE` (T-2.06, T-2.07)
- [ ] Zero-findings guard emits stub tasklist (T-2.08)
- [ ] Skip path saves `validated-with-issues` state (T-2.10)
- [ ] `remediation-tasklist.md` passes `REMEDIATE_GATE` (T-2.13)
- [ ] Prompt logic in `execute_roadmap()`, not `execute_pipeline()` (T-2.16)

### M3 — Remediation Orchestrator Operational
- [ ] Parallel agents run concurrently on different files (T-3.14)
- [ ] Agent failure → full rollback → files match snapshots exactly (T-3.17, T-3.18)
- [ ] No files outside allowlist modified (T-3.08, T-3.09)
- [ ] Updated tasklist passes `REMEDIATE_GATE` with outcomes (T-3.24)
- [ ] Timeout at 300s, single retry (T-3.15, T-3.16)
- [ ] `ClaudeProcess` used directly, not `execute_pipeline()` (T-3.12)
- [ ] Rollback is deterministic and tested — **release gate**

### M4 — Certification Operational
- [ ] Certification report has required YAML frontmatter (T-4.06)
- [ ] Per-finding PASS/FAIL table with justifications (T-4.07)
- [ ] All pass → `certified: true` (T-4.08)
- [ ] Some fail → `certified-with-caveats` (T-4.09)
- [ ] Unfixed findings → FAIL, not PASS (T-4.13) — **release gate**
- [ ] Single pass only, no loop (T-4.15)

### M5 — Resume & State Complete
- [ ] Resume from every state works correctly (T-5.01–T-5.03)
- [ ] Stale hash → re-execution (T-5.04)
- [ ] Old state files without new fields don't crash (T-5.07)
- [ ] Existing consumers unaffected (T-5.08)

### M6 — Release Ready
- [ ] SC-001 through SC-008 all pass (T-6.01–T-6.08)
- [ ] No regressions in steps 1–9 (T-6.15)
- [ ] Edge cases covered (T-6.09–T-6.14)
- [ ] Performance benchmark ≤30% overhead (T-6.06)
- [ ] Code review confirms architectural constraints

---

## 6. Quality Gates Between Phases

### Gate G0→G1: Discovery → Foundation
| Criterion | Method | Blocker? |
|-----------|--------|----------|
| All structural questions resolved | Architecture notes committed | Yes |
| No ambiguity in Finding lifecycle | Status model reviewed | Yes |
| `validate_executor.py` pattern understood | Code reading complete | Yes |

### Gate G1→G2: Foundation → Prompt & Tasklist
| Criterion | Method | Blocker? |
|-----------|--------|----------|
| T-1.01–T-1.13 all green | `uv run pytest -m "vm1"` | Yes |
| `Finding` importable from `roadmap.models` | Import test | Yes |
| Parser coverage ≥100% on pure function paths | `--cov` report | Yes |

### Gate G2→G3: Prompt & Tasklist → Remediation Orchestrator
| Criterion | Method | Blocker? |
|-----------|--------|----------|
| T-2.01–T-2.16 all green | `uv run pytest -m "vm2"` | Yes |
| `REMEDIATE_GATE` defined and tested | T-2.13, T-2.14 pass | Yes |
| Filter functions verified pure (no I/O) | T-2.05 pass | Yes |

### Gate G3→G4: Remediation Orchestrator → Certification
| Criterion | Method | Blocker? |
|-----------|--------|----------|
| T-3.01–T-3.27 all green | `uv run pytest -m "vm3"` | Yes |
| Rollback deterministic (T-3.17–T-3.22) | Specific test run | **Release gate** |
| No same-file concurrent edits possible | T-3.05–T-3.06 pass | Yes |
| `remediation-tasklist.md` passes gate with outcomes | T-3.24 pass | Yes |

### Gate G4→G5: Certification → Resume & State
| Criterion | Method | Blocker? |
|-----------|--------|----------|
| T-4.01–T-4.17 all green | `uv run pytest -m "vm4"` | Yes |
| False-pass detection proven (T-4.13–T-4.14) | Specific test run | **Release gate** |
| `CERTIFY_GATE` defined and tested | T-4.10, T-4.11 pass | Yes |

### Gate G5→G6: Resume & State → Integration
| Criterion | Method | Blocker? |
|-----------|--------|----------|
| T-5.01–T-5.11 all green | `uv run pytest -m "vm5"` | Yes |
| Backward compatibility proven | T-5.07, T-5.08 pass | Yes |
| Stale detection fail-closed | T-5.04, T-5.06 pass | Yes |

### Gate G6→Release: Integration → Ship
| Criterion | Method | Blocker? |
|-----------|--------|----------|
| SC-001–SC-008 all pass | `uv run pytest -m acceptance` | Yes |
| Steps 1–9 regression free | T-6.15, T-6.16 pass | Yes |
| Performance ≤30% overhead | T-6.06 benchmark | Yes (soft) |
| Test coverage ≥90% on new modules | `--cov` report | Yes |
| Architectural review complete | Manual code review | Yes |

---

## 7. Test Infrastructure Requirements

### New Fixtures Needed
- **Report fixtures**: 6 markdown files covering merged, individual, malformed, empty, and duplicate-finding formats
- **Finding factory**: Helper to create `Finding` instances with sensible defaults for test brevity
- **Pipeline state fixtures**: Pre-built `.roadmap-state.json` files at each pipeline state (post-validate, post-remediate, post-certify, legacy-without-new-fields)
- **Controlled ClaudeProcess**: Test harness that simulates success/failure/timeout without real Claude API calls (for integration tests only — E2E uses real subprocess)

### Test Markers
```python
pytest.mark.vm1      # Foundation tests
pytest.mark.vm2      # Prompt & Tasklist tests
pytest.mark.vm3      # Remediation Orchestrator tests
pytest.mark.vm4      # Certification tests
pytest.mark.vm5      # Resume & State tests
pytest.mark.vm6      # Integration & Hardening tests
pytest.mark.acceptance  # SC-001 through SC-008
```

### CI Configuration
- **On every commit**: Unit tests (vm1–vm5 markers) — target <60s
- **On PR**: Unit + integration tests — target <5min
- **On merge to integration**: Full suite including E2E — target <15min
- **Release gate**: Acceptance tests + performance benchmark — manual trigger
