---
validation_milestones: 10
interleave_ratio: "1:2"
---

# v2.25 Test Strategy: Deviation-Aware Fidelity Pipeline

## 1. Validation Milestones Mapped to Roadmap Phases

| Milestone | Phase | Name | Type | Release Gate |
|-----------|-------|------|------|--------------|
| VM-1 | 0 | Architecture Freeze Verification | Review | ✅ Required |
| VM-2 | 1a | Data Model Validation | Unit | ✅ Required |
| VM-3 | 1b | Gate and Semantic Check Validation | Unit | ✅ Required |
| VM-4 | 2a | Prompt Contract Validation | Static/Golden | ✅ Required |
| VM-5 | 2b | Step Wiring and Artifact Contract | Integration | ✅ Required |
| VM-6 | 3a | Resume Freshness Correctness | Unit | ✅ Required |
| VM-7 | 3b | Remediation Budget Enforcement | Integration | ✅ Required |
| VM-8 | 4 | Negative Validation (5 Refusal Behaviors) | Unit+Integration | 🔴 Release Blocker |
| VM-9 | 5a | Full Unit Test Suite | Unit | ✅ Required |
| VM-10 | 5b | Integration + Manual Evidence Package | Integration+Manual | 🔴 Release Blocker |

---

## 2. Test Categories

### 2.1 Unit Tests

**Target files**: `test_models.py`, `test_gates_data.py`, `test_executor.py`, `test_remediate.py`

#### Data Model Tests (`test_models.py`)
- `Finding(deviation_class="SLIP")` constructs without error
- `Finding(deviation_class="INVALID")` raises `ValueError`
- `Finding("text")` defaults `deviation_class` to `"UNCLASSIFIED"`
- Each valid class in `VALID_DEVIATION_CLASSES` accepted individually
- `VALID_DEVIATION_CLASSES` is a `frozenset` (immutable)
- Existing `Finding` constructors without `deviation_class` remain unaffected

#### Gate/Semantic Check Tests (`test_gates_data.py`)

For each of the 10 semantic check functions, test the following input categories:

| Check Function | Valid | Invalid | Missing Field | Malformed Field |
|---|---|---|---|---|
| `_certified_is_true()` | `certified: true` | `certified: false` | no field | `certified: 42` |
| `_validation_complete_true()` | `validation_complete: true` | `validation_complete: false` | no field | non-bool |
| `_no_ambiguous_deviations()` | `ambiguous_count: 0` | `ambiguous_count: 1` | no field | `ambiguous_count: "x"` |
| `_routing_consistent_with_slip_count()` | slip_count=2, routing non-empty | slip_count=2, routing empty | no routing field | slip_count="abc" |
| `_pre_approved_not_in_fix_roadmap()` | PRE_APPROVED absent from fix_roadmap | PRE_APPROVED in fix_roadmap | no routing fields | garbage IDs |
| `_slip_count_matches_routing()` | len(fix_roadmap) >= slip_count | len(fix_roadmap) < slip_count | no slip_count | slip_count=-1 |
| `_total_annotated_consistent()` | sum matches total_annotated | sum mismatches | no total_annotated | total_annotated="?" |
| `_total_analyzed_consistent()` | sum matches total_analyzed | sum mismatches | no total_analyzed | total_analyzed=null |
| `_routing_ids_valid()` | all DEV-\d+ tokens | mixed valid/invalid | empty routing | spaces in tokens |
| `_routing_ids_valid()` extended | token in fidelity content | token absent from fidelity | fidelity=None (skip) | — |

**Critical**: Each malformed-field case MUST produce a distinct log message from missing-field case (FR-080). Tests MUST capture log output and assert distinct messages.

#### Parsing Tests (`test_remediate.py` or `test_parsing.py`)
- `_parse_routing_list("")` returns `[]`
- `_parse_routing_list(" ")` returns `[]`
- `_parse_routing_list("DEV-001, DEV-002")` returns `["DEV-001", "DEV-002"]` with whitespace stripped
- `_parse_routing_list("DEV-001,INVALID,DEV-003")` returns `["DEV-001", "DEV-003"]` with WARNING logged
- `_parse_routing_list("dev-001")` excludes lowercase; WARNING logged
- Token count cross-check logged when returned tokens < total_analyzed

#### Executor Unit Tests (`test_executor.py`)

**`_check_annotate_deviations_freshness()` — all 9 test cases (SC-8)**:
1. File missing → returns `False`
2. `roadmap_hash` field missing from frontmatter → returns `False`
3. `roadmap_hash` field present but empty → returns `False`
4. Read error (permission denied) → returns `False`, no exception raised
5. Hash matches current `roadmap.md` → returns `True`
6. Hash does not match current `roadmap.md` → returns `False`
7. `spec-deviations.md` is zero bytes → returns `False`
8. `roadmap.md` does not exist at check time → returns `False`
9. Malformed frontmatter in `spec-deviations.md` → returns `False`

**Each `False` return MUST emit a distinct log message stating the specific failure reason** — assert log content, not just return value.

**`_check_remediation_budget()`**:
- `attempts=0, max=2` → returns `True`
- `attempts=1, max=2` → returns `True`
- `attempts=2, max=2` → returns `False`, calls `_print_terminal_halt()`
- `attempts="abc"` → coerced to 0, WARNING logged, returns `True`
- `attempts=None` → coerced to 0, WARNING logged, returns `True`
- Function does NOT call `sys.exit(1)` directly (assert no `SystemExit` raised from function itself)

**`_print_terminal_halt()` stderr assertions** — captured via `capsys` or `stderr` mock:
- Contains attempt count
- Contains remaining failing finding count
- Contains per-finding IDs from `unfixed_details`
- Contains certification report path
- Contains `--resume` command string

### 2.2 Integration Tests

**Target file**: `tests/roadmap/test_integration_v5_pipeline.py`

All integration tests use pre-recorded subprocess outputs (no live Claude calls). Fixtures replicate v2.24 scenario.

| Test ID | Scenario | Asserts |
|---------|----------|---------|
| INT-1 | Full pipeline from extract to certify | Final state shows `certify` PASS; no halt at spec-fidelity |
| INT-2 | `total_annotated: 0` from annotate-deviations | INFO log emitted; pipeline continues to deviation-analysis |
| INT-3 | `routing_update_spec` non-empty | CLI stdout contains spec-update summary |
| INT-4 | Resume with stale `roadmap_hash` | `annotate-deviations` re-runs; `spec-fidelity` + `deviation-analysis` gate-pass reset |
| INT-5 | Resume with matching `roadmap_hash` | `annotate-deviations` skipped correctly |
| INT-6 | Budget=1 after first remediation failure | Second attempt permitted |
| INT-7 | Budget=2 after second remediation failure | `_print_terminal_halt()` called; `sys.exit(1)` raised |
| INT-8 | `deviations_to_findings()` severity mapping | HIGH→BLOCKING, MEDIUM→WARNING, LOW→INFO; `update_spec`/`no_action` excluded |
| INT-9 | Malformed `.roadmap-state.json` on resume | Defaults to 0 attempts; no exception |
| INT-10 | Old state file without `remediation_attempts` | Field defaults to 0; pipeline proceeds normally |
| INT-11 | `ambiguous_count > 0` | STRICT gate failure; pipeline halts with operator instructions |
| INT-12 | Step order verification | `_get_all_step_ids()` returns 13 steps in exact FR-002 order |

### 2.3 End-to-End / Manual Validation Tests

Used to produce the Phase 5 evidence package (required for VM-10).

| E2E Test | Evidence Artifact | SC Covered |
|----------|------------------|------------|
| Full pipeline run on v2.24 spec | Run logs + state file showing `certify` reached | SC-1 |
| Inspect `spec-deviations.md` | D-02, D-04 classified `INTENTIONAL_IMPROVEMENT` | SC-2 |
| Inspect `deviation-analysis.md` | D-02, D-04 routed `no_action`; DEV-002, DEV-003 in `routing_fix_roadmap` | SC-2, SC-3 |
| Roadmap before/after diff | No `INTENTIONAL`/`PRE_APPROVED` content modified | SC-4 |
| Artifact frontmatter inspection | `schema_version: "2.25"` is first field in both artifacts | SC-10 |
| Static diff of generic pipeline layer | Zero modifications in `pipeline/models.py`, `pipeline/executor.py` | SC-7, NFR-009, NFR-010 |

### 2.4 Acceptance Tests

Mapped to SC-1 through SC-10 from the roadmap. See Section 5 (Acceptance Criteria per Milestone).

---

## 3. Test-Implementation Interleaving Strategy

**Ratio: 1:2** — one test authoring session for every two implementation sessions within each phase.

### Interleave Schedule

```
Phase 0 (0.5–1.5 days)
  └─ No code tests; architecture review checklist only (VM-1)

Phase 1 (2–3 days)
  ├─ [Impl 1.1] models.py: Finding.deviation_class + VALID_DEVIATION_CLASSES
  ├─ [Test 1.1] test_models.py: all Finding constructor cases          ← VM-2 gate
  ├─ [Impl 1.2] gates.py: parse_frontmatter() rename + _parse_routing_list()
  ├─ [Impl 1.3] gates.py: 9+ semantic check functions
  ├─ [Test 1.2] test_gates_data.py: all semantic check boundary tests  ← VM-3 gate
  └─ Full suite pass before Phase 2 begins

Phase 2 (3–4 days)
  ├─ [Impl 2.1] prompts.py: build_annotate_deviations_prompt()
  ├─ [Test 2.1] Prompt golden fixtures: anti-laundering wording, schema fields ← VM-4 gate
  ├─ [Impl 2.2] prompts.py: build_deviation_analysis_prompt()
  ├─ [Test 2.2] Prompt golden fixtures: routing table, routing_intent, schema_version
  ├─ [Impl 2.3] executor.py: step wiring, hash injection, FR-087, FR-089
  ├─ [Impl 2.4] remediate.py: deviations_to_findings()
  ├─ [Test 2.3] test_remediate.py: deviations_to_findings() severity + exclusion (scaffold) ← VM-5 gate
  └─ INT-12 (step order) runnable after this phase

Phase 3 (2–4 days)
  ├─ [Impl 3.1] executor.py: _check_annotate_deviations_freshness()
  ├─ [Test 3.1] test_executor.py: all 9 freshness test cases           ← VM-6 gate
  ├─ [Impl 3.2] executor.py: _check_remediation_budget() + _print_terminal_halt()
  ├─ [Test 3.2] test_executor.py: budget enforcement + stderr assertions ← VM-7 gate
  └─ test_remediate.py: complete deviations_to_findings() integration tests

Phase 4 (1.5–3 days)
  ├─ [Test 4.1] Negative validation: 5 refusal behavior tests          ← VM-8 RELEASE BLOCKER
  └─ [Test 4.2] Roadmap diff verification (SC-4 evidence)

Phase 5 (2–3 days)
  ├─ [Test 5.1] All unit tests finalized                               ← VM-9 gate
  └─ [Test 5.2] Integration + manual evidence package                  ← VM-10 RELEASE BLOCKER
```

**Hard rules**:
- No phase begins until all exit criteria tests from the prior phase pass
- Integration test scaffolds are written in the same phase as the implementation they test; final assertions may be completed in the following phase only if the fixture dependency is unresolved
- No test is skipped, disabled, or marked `xfail` to achieve a green suite

---

## 4. Risk-Based Test Prioritization

Tests ordered by risk severity and blocking potential:

| Priority | Risk ID | Test Focus | Failure Mode Prevented |
|----------|---------|-----------|----------------------|
| P0 | R-1 | Negative validation: bogus citation rejection | Deviation laundering silently passes |
| P0 | R-2 | Resume freshness: all 9 test cases (SC-8) | Stale `spec-deviations.md` reused |
| P0 | — | Budget exhaustion: stderr assertion coverage | Infinite remediation loop |
| P1 | R-9 | Routing parsing: malformed tokens, empty routing with slips | Broken frontmatter halts pipeline |
| P1 | R-6 | Backward compat: Finding default field, old state files | Existing consumers broken |
| P1 | R-7 | STANDARD gate downgrade: full suite after Phase 1 gate changes | Regression from relaxed gating |
| P2 | R-4 | Ambiguity enforcement: STRICT gate on ambiguous_count > 0 | Ambiguous deviations pass silently |
| P2 | R-5 | Certify block: _certified_is_true() with false/missing/malformed | False certification advances pipeline |
| P3 | R-8 | Context window on annotate-deviations | N/A — monitored during manual validation only |
| P3 | R-10 | OQ-A resolution: GateCriteria.aux_inputs inspection | Mid-Phase-2 refactor risk |

### P0 Tests Must Pass Before Any Phase 2 Code Ships

Specifically:
- `test_gates_data.py::test_no_ambiguous_deviations_*` (boundary variants)
- `test_executor.py::test_check_annotate_deviations_freshness_*` (all 9)
- `test_executor.py::test_print_terminal_halt_stderr_*` (finding IDs + resume cmd)

---

## 5. Acceptance Criteria Per Milestone

### VM-1: Architecture Freeze Verification (Phase 0)
- [ ] All 8 OQs resolved or deferred with documented fallback
- [ ] `fidelity.py` inspection complete; modification scope documented
- [ ] `_parse_routing_list()` module placement decided (no circular imports)
- [ ] Module dependency DAG verified: `models.py ← gates.py ← fidelity.py ← remediate.py ← executor.py`
- [ ] FR-079 Option A vs. Option B explicitly selected and recorded

### VM-2: Data Model Validation (Phase 1a)
- [ ] All `Finding` constructor tests pass (valid classes, invalid class, default)
- [ ] `VALID_DEVIATION_CLASSES` is a `frozenset` containing exactly 5 members
- [ ] `ValueError` raised for any value not in the frozenset
- [ ] No existing test regressions

### VM-3: Gate and Semantic Check Validation (Phase 1b)
- [ ] All 10 semantic check functions have passing boundary tests
- [ ] Each malformed-field case has a distinct log message from missing-field (captured and asserted)
- [ ] `parse_frontmatter()` is public; grep confirms zero remaining `_parse_frontmatter` references
- [ ] `SPEC_FIDELITY_GATE` verified as STANDARD tier in gate definition
- [ ] `CERTIFY_GATE` includes `certified_true` check in check list
- [ ] `DEVIATION_ANALYSIS_GATE` semantic check order verified (not just presence): `no_ambiguous`, `validation_complete`, `routing_consistent`, `pre_approved_not_in_fix`, `slip_count_matches`, `total_analyzed`
- [ ] `ALL_GATES` registry contains both new gate entries

### VM-4: Prompt Contract Validation (Phase 2a)
- [ ] `build_annotate_deviations_prompt()` golden fixture asserts: classification taxonomy present (all 4 classes), anti-laundering wording requiring D-XX + round citation, `schema_version: "2.25"` as first frontmatter field in output spec
- [ ] `build_deviation_analysis_prompt()` golden fixture asserts: classification taxonomy (all 4 analysis classes), normative mapping table reference, `routing_intent` sub-field present, `## Spec Update Recommendations` section present, flat routing fields with DEV-\d+ format
- [ ] `build_spec_fidelity_prompt()` accepts `spec_deviations_path=None` without error; with path, prompt includes all 5 behaviors (a–e from FR-017)

### VM-5: Step Wiring and Artifact Contract (Phase 2b)
- [ ] `_get_all_step_ids()` returns exactly 13 steps in FR-002 order (asserted as ordered list equality)
- [ ] `annotate-deviations` position: after `merge`, before `test-strategy`
- [ ] `deviation-analysis` position: after `spec-fidelity`, before `remediate`
- [ ] `roadmap_hash` injection uses `.tmp` + `os.replace()` pattern (confirmed by code review + atomic write test)
- [ ] `deviations_to_findings()`: severity mapping correct; `update_spec`/`no_action` excluded; `ValueError` raised when routing empty but `slip_count > 0`; WARNING logged for unknown routing ID
- [ ] INT-2 (total_annotated=0 → INFO log, no halt) passes
- [ ] INT-3 (routing_update_spec non-empty → CLI summary) passes

### VM-6: Resume Freshness Correctness (Phase 3a)
- [ ] All 9 `_check_annotate_deviations_freshness()` test cases pass
- [ ] Each `False` return emits a distinct, specific log message (asserted per test case)
- [ ] Freshness `False` → `annotate-deviations` re-added to queue
- [ ] Freshness `False` → gate-pass state reset for both `spec-fidelity` and `deviation-analysis`
- [ ] No exception propagates out of the function under any input condition

### VM-7: Remediation Budget Enforcement (Phase 3b)
- [ ] Budget cap at 2 attempts verified (attempts=2 → `_print_terminal_halt()` called, returns `False`)
- [ ] Non-integer `remediation_attempts` coerced to 0 with WARNING (not exception)
- [ ] `_print_terminal_halt()` stderr output asserts: attempt count, finding count, per-finding IDs, certification path, resume command
- [ ] `_check_remediation_budget()` does NOT raise `SystemExit` directly
- [ ] Old `.roadmap-state.json` without `remediation_attempts` → defaults to 0
- [ ] INT-6 and INT-7 pass
- [ ] `_apply_resume_after_spec_patch()` code present but unreachable from normal execution (verified by grep/call-graph check)

### VM-8: Negative Validation — Release Blocker (Phase 4)

All 5 refusal behaviors must have explicit test or artifact evidence:

1. **Bogus citation rejection**: Test fixture with `INTENTIONAL_IMPROVEMENT` annotation lacking D-XX + round number → `spec-fidelity` agent reports as HIGH severity. Assert via integration test with mock fidelity agent returning HIGH for invalid annotation.

2. **Stale artifact rejection**: `spec-deviations.md` with mismatched `roadmap_hash` → `annotate-deviations` reruns. Verified by INT-4.

3. **Ambiguous continuation refused**: `ambiguous_count > 0` in `deviation-analysis.md` → STRICT gate failure, pipeline halts. Verified by INT-11 + unit test `_no_ambiguous_deviations(content_with_ambiguous=1)` returns `False`.

4. **False certification refused**: `certified: false` → `CERTIFY_GATE` blocks. Verified by unit test `_certified_is_true(false_content)` returns `False` + integration test with mock certify producing `certified: false`.

5. **Third attempt refused**: `remediation_attempts=2` on `--resume` → `_print_terminal_halt()` + `sys.exit(1)`. Verified by INT-7 with stderr content assertions.

- [ ] SC-4 verified with explicit before/after roadmap diff (not just test pass; diff saved as evidence artifact)
- [ ] Each of the 5 refusal behaviors has an identified test ID or artifact reference in the evidence package

### VM-9: Full Unit Test Suite (Phase 5a)
- [ ] `uv run pytest tests/roadmap/ -v` passes with zero failures, zero skips
- [ ] `test_models.py`: all `Finding` + `VALID_DEVIATION_CLASSES` tests
- [ ] `test_gates_data.py`: all 10 semantic check functions, boundary coverage per matrix in Section 2.1
- [ ] `test_executor.py`: 9 freshness cases, budget cases, stderr assertions
- [ ] `test_remediate.py`: `deviations_to_findings()` all severity mappings + exclusions + ValueError + WARNING log
- [ ] No regressions in pre-existing test suite

### VM-10: Integration + Manual Evidence Package — Release Blocker (Phase 5b)
- [ ] `tests/roadmap/test_integration_v5_pipeline.py` all 12 INT tests pass
- [ ] SC-1: Run log showing `certify` reached without manual intervention
- [ ] SC-2: `spec-deviations.md` and `deviation-analysis.md` artifacts with D-02, D-04 classified and routed `no_action`
- [ ] SC-3: `deviation-analysis.md` with DEV-002, DEV-003 in `routing_fix_roadmap`, `ambiguous_count == 0`
- [ ] SC-4: Before/after roadmap diff artifact — no `INTENTIONAL`/`PRE_APPROVED` sections changed
- [ ] SC-7: Static diff output confirming zero new classes in generic pipeline layer
- [ ] SC-10: Both artifacts parsed with `schema_version == "2.25"` as first frontmatter field
- [ ] NFR-009/NFR-010: Zero-modification diff of `pipeline/executor.py` and `pipeline/models.py`
- [ ] All evidence artifacts committed to `.dev/releases/backlog/2.25-roadmap-v5/` before release review

---

## 6. Quality Gates Between Phases

Each gate is a hard stop. Phase N+1 cannot begin until all gate criteria are met.

### Gate 0→1: Architecture Freeze
**Criteria**:
- VM-1 checklist complete (all 5 items checked)
- OQ-A resolved with implementation option documented
- `_parse_routing_list()` module placement confirmed
- No unresolved decision that could force rework in gates, parsing, or executor flow

**Blocking issues**: Any unresolved OQ in the set {OQ-A, OQ-E, OQ-F, OQ-G, OQ-H} blocks this gate.

### Gate 1→2: Foundation Complete
**Criteria**:
- VM-2 and VM-3 fully satisfied
- `parse_frontmatter()` is public; grep confirms zero `_parse_frontmatter` calls remaining
- Full existing test suite passes (STANDARD gate downgrade must not cause regressions)
- All deprecated check functions present in `gates.py` with `[DEPRECATED v2.25]` docstrings

**Blocking issues**: Any failing test in `test_models.py` or `test_gates_data.py`; any regression in pre-existing suite.

### Gate 2→3: Step Wiring Complete
**Criteria**:
- VM-4 and VM-5 fully satisfied
- Step order assertion (INT-12) passes
- `deviations_to_findings()` unit tests pass (scaffold complete; final assertions may be deferred only if Phase 3 fixture dependency is genuinely unresolved — document reason)
- Prompt golden fixtures committed and reviewed

**Blocking issues**: Incorrect step order; `roadmap_hash` injection not atomic; `deviations_to_findings()` severity mapping incorrect.

### Gate 3→4: Recovery Mechanisms Complete
**Criteria**:
- VM-6 and VM-7 fully satisfied
- INT-4 through INT-10 all pass
- `_apply_resume_after_spec_patch()` verified unreachable from normal execution
- `.roadmap-state.json` backward compatibility confirmed

**Blocking issues**: Any freshness test case failing; remediation budget not capping at 2; stderr output missing required fields; `sys.exit(1)` raised from inside `_check_remediation_budget()`.

### Gate 4→5: Negative Validation Complete
**Criteria**:
- VM-8 fully satisfied — all 5 refusal behaviors have explicit evidence
- SC-4 roadmap diff artifact exists and is clean
- No prohibited modifications in generic pipeline layer (pre-check before Phase 5 effort begins)

**Blocking issues**: Any refusal behavior not covered by a test or artifact; diff shows `INTENTIONAL`/`PRE_APPROVED` content modified; generic pipeline layer modified.

### Gate 5→Release: Evidence Review
**Criteria**:
- VM-9 and VM-10 fully satisfied
- SC-1 through SC-10 all marked `verified` with test ID or artifact reference in a release checklist document
- Zero unresolved code comments of the form `# TODO`, `# OQ-`, or `# DEFERRED` in modified files
- `schema_version: "2.25"` confirmed as first frontmatter field in both artifact types
- All evidence artifacts present in `.dev/releases/backlog/2.25-roadmap-v5/`

**Blocking issues**: Any SC not verified; any unresolved open question in code; any prohibited file modified. Code-complete status alone does not satisfy this gate.
