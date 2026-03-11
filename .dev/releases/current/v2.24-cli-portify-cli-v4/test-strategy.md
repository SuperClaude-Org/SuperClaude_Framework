

---
validation_milestones: 5
interleave_ratio: '1:3'
---

# CLI-Portify v4 — Test Strategy

## 1. Validation Milestones Mapped to Roadmap Phases

### Milestone A: Foundation Proven (Phase 1, Days 1-4)

**What's validated**: Module structure, domain models, failure taxonomy, gate framework, pure-programmatic steps.

**Tests to run before Phase 2 begins**:

| Test ID | Type | What It Validates | Success Criteria |
|---------|------|-------------------|------------------|
| T-U01 | Unit | `PortifyConfig` construction and defaults | All fields populated, `--dry-run` flag propagated |
| T-U02 | Unit | `PortifyResult.to_contract()` — success path | YAML output matches Phase Contracts schema |
| T-U03 | Unit | `PortifyResult.to_contract()` — failed/partial/dry_run paths | All contract fields populated per NFR-009 |
| T-U04 | Unit | Gate signature compliance (`tuple[bool, str]`) | All gate functions in `gates.py` return correct type |
| T-U05 | Unit | `validate_config` — happy path | `validate-config-result.json` emitted, <1s (SC-008) |
| T-U06 | Unit | `validate_config` — missing SKILL.md, unwritable dir, name collision | Specific error messages per failure type |
| T-U07 | Unit | `discover_components` — happy path | `component-inventory.md` with correct YAML frontmatter, <5s (SC-008) |
| T-U08 | Unit | `discover_components` — empty workflow, file >1MB skipped | Warning logged, inventory still valid |
| T-U09 | Unit | Name derivation edge cases | `sc-cleanup-audit-protocol` → `cleanup_audit`, prefix/suffix stripping, case conversion |
| T-U10 | Unit | `StepStatus` enum covers all taxonomy categories | gate_failure, subprocess_crash, budget_exhaustion, timeout, user_rejected, malformed_artifact |

**Gate**: All 10 tests pass. `grep -r "async def\|await" cli_portify/` returns 0 results.

**Acceptance criteria**: `superclaude cli-portify --workflow <path> --dry-run` executes Steps 1-2 and halts with valid contract YAML (SC-002).

---

### Milestone B: Subprocess & Core Steps Validated (Phase 2, Days 5-9)

**What's validated**: PortifyProcess, prompt builders, executor sequencing, Steps 3-4, user review gate.

**Tests to run before Phase 3 begins**:

| Test ID | Type | What It Validates | Success Criteria |
|---------|------|-------------------|------------------|
| T-U11 | Unit | `PortifyProcess` extends `ClaudeProcess` with `--add-dir` | `extra_args` includes work dir and workflow path |
| T-U12 | Unit | Prompt builder templates contain `@path` references | No inline artifact embedding; all prompts reference files by path |
| T-U13 | Unit | Executor step sequencing — Python controls flow | Steps execute in order 1→2→3→4; no Claude-decided branching (NFR-006) |
| T-U14 | Unit | Gate definitions Steps 3-4 — STRICT tier semantic checks | Section presence validation (Source Components, Step Graph, etc.) |
| T-U15 | Unit | User review gate — accept path | `y` input → continues execution |
| T-U16 | Unit | User review gate — reject path | `n` input → `USER_REJECTED` status emitted |
| T-I01 | Integration | Steps 1-4 end-to-end with mock subprocess | `portify-analysis.md` and `portify-spec.md` produced with required sections |

**Gate**: 6 unit + 1 integration test pass. Executor never reads Claude output to determine next step.

**Acceptance criteria**: Steps 1-4 produce structurally valid artifacts. Review gate pauses on stderr and responds to y/n. `--dry-run` halts after Step 4 with contract.

---

### Milestone C: Synthesis & Skill Integration Stable (Phase 3, Days 10-13)

**What's validated**: Template instantiation, placeholder elimination, brainstorm skill invocation, Section 12 population.

| Test ID | Type | What It Validates | Success Criteria |
|---------|------|-------------------|------------------|
| T-U17 | Unit | Template loader — template exists at expected path | Fail fast with specific path in error if missing |
| T-U18 | Unit | Sentinel scanner — detects `{{SC_PLACEHOLDER:*}}` | Returns list of remaining placeholders with names (SC-003) |
| T-U19 | Unit | Sentinel scanner — zero placeholders | Gate passes, empty list returned |
| T-U20 | Unit | Brainstorm findings post-processor | Parses findings into `{gap_id, description, severity, affected_section, persona}` |
| T-U21 | Unit | Section 12 gate — findings table present | STANDARD gate passes |
| T-U22 | Unit | Section 12 gate — heading only, no content | STANDARD gate fails with descriptive message |
| T-U23 | Unit | Section 12 gate — zero-gap summary text | STANDARD gate passes |
| T-I02 | Integration | Brainstorm skill unavailability fallback | Inline fallback activates, Section 12 populated with fallback notice |

**Gate**: 7 unit + 1 integration test pass. `grep "{{SC_PLACEHOLDER" portify-release-spec.md` returns 0.

**Acceptance criteria**: Synthesized spec has zero placeholders. Brainstorm findings incorporated as `[INCORPORATED]` or routed to Section 11 as `[OPEN]`. Phase 3 completes in <10 min (advisory, NFR-001).

---

### Milestone D: Convergence & Panel Review Proven (Phase 4, Days 14-18)

**What's validated**: Convergence loop terminal states, quality score computation, downstream readiness boundary, budget guards.

| Test ID | Type | What It Validates | Success Criteria |
|---------|------|-------------------|------------------|
| T-U24 | Unit | Convergence — CONVERGED terminal state | 0 unaddressed CRITICALs → loop exits with CONVERGED |
| T-U25 | Unit | Convergence — ESCALATED terminal state | max iterations reached → ESCALATED status |
| T-U26 | Unit | Convergence — BUDGET_EXHAUSTED terminal state | TurnLedger pre-launch guard prevents launch |
| T-U27 | Unit | Convergence — TIMEOUT terminal state | Iteration exceeds 300s → TIMEOUT |
| T-U28 | Unit | Quality score computation (SC-010) | `mean(clarity, completeness, testability, consistency)`, `abs(computed - expected) < 0.01` |
| T-U29 | Unit | Downstream readiness boundary (SC-012) | `7.0` → `true`, `6.9` → `false`, `7.01` → `true` |
| T-U30 | Unit | Convergence predicate — exact string match | Parses `CONVERGENCE_STATUS: CONVERGED` correctly |
| T-U31 | Unit | Convergence predicate — regex fallback | Handles `CONVERGENCE_STATUS:\s*CONVERGED` with whitespace variance |
| T-U32 | Unit | Convergence predicate — malformed panel output | Neither match succeeds → failure contract emitted |
| T-U33 | Unit | Additive-only modification check (NFR-008) | Spec content before panel ⊂ spec content after panel |
| T-U34 | Unit | Budget estimation — insufficient for one iteration | Pre-launch guard blocks with clear message |

**Gate**: All 11 unit tests pass. Convergence loop terminates correctly in all 4 terminal states (SC-004).

**Acceptance criteria**: Quality scores match expected formula. Downstream readiness boundary is exact. Budget guards prevent runaway execution. Additive-only constraint verified.

---

### Milestone E: Release Certification (Phase 5, Days 19-22)

**What's validated**: End-to-end pipeline, TUI monitoring, resume, dual logging, all success criteria.

| Test ID | Type | What It Validates | Success Criteria |
|---------|------|-------------------|------------------|
| T-I03 | Integration | End-to-end `sc-cleanup-audit` workflow (SC-001) | `downstream_ready: true` in final contract |
| T-I04 | Integration | `--dry-run` mode (SC-002) | Halts after Step 4, valid `dry_run` contract |
| T-I05 | Integration | Resume from mid-pipeline failure (SC-006) | Resume command generated, continuation from failed step succeeds |
| T-I06 | Integration | Convergence loop — CONVERGED path | Full pipeline with convergence completing normally |
| T-I07 | Integration | Convergence loop — ESCALATED path | Max iterations reached, ESCALATED status, contract valid |
| T-I08 | Integration | Skill unavailability fallback | Both skills unavailable → inline fallbacks activate → pipeline completes |
| T-U35 | Unit | JSONL event extraction — all 5 signal types | `STEP_START`, `STEP_COMPLETE`, `GATE_PASS`, `GATE_FAIL`, `CONVERGENCE_ITERATION` |
| T-U36 | Unit | Resume command generation | Correct `--resume-from` CLI invocation emitted |
| T-U37 | Unit | Diagnostics — structured error output per failure type | Each taxonomy category produces actionable message |

**Final verification sweep**:

| Check | Command | Expected |
|-------|---------|----------|
| SC-009 | `grep -r "async def\|await" src/superclaude/cli/cli_portify/` | 0 results |
| SC-011 | `git diff pipeline/ sprint/` | Empty |
| NFR-004 | Gate signature audit | All `tuple[bool, str]` |
| SC-013 | `uv run pytest tests/cli_portify/ -v` | 37 unit tests pass |
| SC-014 | `uv run pytest tests/cli_portify/integration/ -v` | 6 integration tests pass |

**Acceptance criteria**: All 14 success criteria (SC-001 through SC-014) verified with evidence.

---

## 2. Test Categories

### Unit Tests (37 total)

**Scope**: Individual functions, models, gate logic, convergence predicates, score computation.

**Characteristics**:
- No subprocess invocation
- No file system side effects (use `tmp_path` fixture)
- No Claude CLI dependency
- Execute in <1s each

**Organization**:
```
tests/cli_portify/
├── test_models.py           # T-U01–U03, T-U10
├── test_gates.py            # T-U04, T-U14, T-U18–U19, T-U21–U23
├── test_validate_config.py  # T-U05–U06, T-U09
├── test_discover.py         # T-U07–U08
├── test_process.py          # T-U11–U12
├── test_executor.py         # T-U13
├── test_review.py           # T-U15–U16
├── test_template.py         # T-U17
├── test_brainstorm.py       # T-U20
├── test_convergence.py      # T-U24–U28, T-U30–U32, T-U34
├── test_panel_review.py     # T-U29, T-U33
├── test_monitor.py          # T-U35
├── test_resume.py           # T-U36
├── test_diagnostics.py      # T-U37
└── integration/
    ├── test_e2e.py           # T-I01, T-I03–T-I04
    ├── test_convergence.py   # T-I06–T-I07
    ├── test_resume.py        # T-I05
    └── test_fallback.py      # T-I02, T-I08
```

### Integration Tests (6 total, per SC-014 + skill unavailability)

**Scope**: Multi-step pipeline execution with real or mock subprocess invocation.

**Characteristics**:
- May invoke `claude` CLI (or mock it)
- Create real files in temp directories
- Test cross-module data flow
- Execute in <5 min each (convergence tests may take longer)

**Fixtures needed**:
- `sample_workflow` — minimal workflow directory with SKILL.md and refs/
- `mock_claude_process` — subprocess mock returning controlled artifacts
- `portify_output_dir` — temporary output directory with cleanup

### E2E Tests (1 primary)

**Scope**: Full pipeline against `sc-cleanup-audit` workflow (SC-001).

**Characteristics**:
- Requires `claude` CLI in PATH
- Requires `/sc:brainstorm` and `/sc:spec-panel` installed
- Wall-clock: 15-30 min
- Run manually or in CI with extended timeout

### Acceptance Tests (per milestone)

**Scope**: Verification of success criteria with evidence collection.

**Characteristics**:
- Mix of automated checks and manual verification
- Evidence captured as test artifacts
- Blocking for phase transitions

---

## 3. Test-Implementation Interleaving Strategy

**Ratio**: 1:3 (one test cycle per three implementation tasks)

### Per-Phase Interleaving Pattern

```
Phase N:
  ├── Implement Task 1 (models/scaffolding)
  ├── Implement Task 2 (core logic)
  ├── Implement Task 3 (integration wiring)
  ├── TEST CYCLE: Run all Phase N unit tests
  ├── Fix failures
  ├── Run milestone gate checks
  └── Phase N complete ✓
```

### Specific Interleaving Schedule

**Phase 1** (3-4 days):
- Day 1: Module scaffolding + domain models + contract review → write T-U01–U03, T-U10
- Day 2: Config validation + component discovery → write T-U05–U09
- Day 3: Gate framework + return contracts → write T-U04, run all Phase 1 tests
- Day 3-4: Fix failures, verify Milestone A gate

**Phase 2** (4-5 days):
- Day 5-6: PortifyProcess + prompt builders → write T-U11–U12
- Day 7: Executor core + Steps 3-4 → write T-U13–U14
- Day 8: User review gate → write T-U15–U16, T-I01
- Day 9: Run all Phase 2 tests, fix failures, verify Milestone B gate

**Phase 3** (3-4 days):
- Day 10: Template loader + spec synthesis → write T-U17–U19
- Day 11: Brainstorm gap analysis → write T-U20–U23
- Day 12-13: Run Phase 3 tests + T-I02, fix failures, verify Milestone C gate

**Phase 4** (4-5 days):
- Day 14-15: Convergence executor → write T-U24–U28, T-U30–U32, T-U34
- Day 16-17: Panel review step → write T-U29, T-U33
- Day 18: Run all Phase 4 tests, fix failures, verify Milestone D gate

**Phase 5** (3-4 days):
- Day 19: TUI monitor + dual logging + resume → write T-U35–U37
- Day 20: Integration tests T-I03–T-I08
- Day 21-22: NFR verification sweep, fix failures, verify Milestone E gate

---

## 4. Risk-Based Test Prioritization

### Priority 1 — Must Test First (Blocks Everything)

| Risk | Tests | Rationale |
|------|-------|-----------|
| Phase 1 is dependency bottleneck | T-U01–U10 | Defects here invalidate all later phases |
| Gate signature non-compliance (NFR-004) | T-U04 | Wrong signatures cascade to all gate consumers |
| Contract schema violations (SC-007) | T-U02–U03 | Resume and diagnostics depend on correct contracts |

### Priority 2 — Must Test Before Integration (High Risk)

| Risk | Tests | Rationale |
|------|-------|-----------|
| R-009: Wrong mode mapping in convergence | T-U24–U25, T-U32 | Highest logic-risk phase per roadmap |
| R-003: Non-machine-readable markers | T-U30–U32 | Convergence depends on parsing; failure = stuck loop |
| SC-003: Placeholder leakage | T-U18–U19 | Hard stop if sentinels survive synthesis |
| NFR-006: Claude controls sequencing | T-U13 | Architectural invariant violation |

### Priority 3 — Must Test Before Release (Medium Risk)

| Risk | Tests | Rationale |
|------|-------|-----------|
| R-002: Budget exhaustion | T-U26, T-U34 | Runaway cost if guards fail |
| R-001: Output truncation | T-I03 (with large workflow) | Only detectable in integration |
| R-007: `@path` scope failures | T-U11, T-I01 | Subprocess file access |
| SC-012: Readiness boundary | T-U29 | Off-by-one affects release decisions |

### Priority 4 — Should Test (Lower Risk)

| Risk | Tests | Rationale |
|------|-------|-----------|
| R-004: Long wall-clock time | Timing assertions in T-U05, T-U07 | Advisory only |
| R-008: Review gate UX | T-U15–U16 | Has `--skip-review` escape hatch |
| R-005: Self-portification | Manual verification | Low probability |

---

## 5. Acceptance Criteria Per Milestone

### Milestone A (Phase 1 Exit)

- [ ] 10 unit tests pass (T-U01–U10)
- [ ] `superclaude cli-portify --workflow <path> --dry-run` runs Steps 1-2
- [ ] `validate-config-result.json` and `component-inventory.md` produced
- [ ] `grep -r "async def\|await" cli_portify/` → 0 results
- [ ] All gate functions return `tuple[bool, str]`
- [ ] Contract YAML emitted on success, partial, failed, dry_run paths

### Milestone B (Phase 2 Exit)

- [ ] 16 unit tests + 1 integration test pass (cumulative)
- [ ] Steps 3-4 produce artifacts with all required sections
- [ ] User review gate works on stderr (both accept and reject)
- [ ] `--dry-run` halts after Step 4 with valid contract
- [ ] Python controls all step sequencing (no Claude-decided flow)
- [ ] `PortifyProcess` passes `--add-dir` correctly

### Milestone C (Phase 3 Exit)

- [ ] 23 unit tests + 2 integration tests pass (cumulative)
- [ ] Zero `{{SC_PLACEHOLDER:*}}` sentinels in synthesized spec
- [ ] Section 12 populated (findings table or zero-gap summary)
- [ ] Brainstorm skill invoked (or fallback activated if unavailable)
- [ ] Phase 3 wall-clock < 10 min (advisory)

### Milestone D (Phase 4 Exit)

- [ ] 34 unit tests + 2 integration tests pass (cumulative)
- [ ] Convergence terminates correctly in all 4 states: CONVERGED, ESCALATED, BUDGET_EXHAUSTED, TIMEOUT
- [ ] Quality score = `mean(clarity, completeness, testability, consistency)` with `<0.01` tolerance
- [ ] Downstream readiness: `7.0` → true, `6.9` → false
- [ ] Additive-only modification verified
- [ ] Budget pre-launch guard blocks insufficient budgets

### Milestone E (Phase 5 Exit — Release)

- [ ] 37 unit tests pass (SC-013 satisfied at 37, exceeding the 17 minimum)
- [ ] 6 integration tests pass (SC-014)
- [ ] All 14 success criteria (SC-001 through SC-014) verified with evidence
- [ ] NFR verification sweep: no async, no base module changes, gate signatures compliant
- [ ] TUI monitor renders step progress
- [ ] Resume from failure works correctly
- [ ] Dual JSONL + Markdown logging operational

---

## 6. Quality Gates Between Phases

### Gate Structure

Each phase transition requires:

1. **Test gate**: All milestone tests pass
2. **Structural gate**: Code meets architectural constraints
3. **Coverage gate**: New code has unit test coverage
4. **Contract gate**: Inter-module contracts verified

### Phase 1 → Phase 2 Gate

| Check | Method | Blocker? |
|-------|--------|----------|
| 10 unit tests pass | `uv run pytest tests/cli_portify/ -v` | Yes |
| No async/await | `grep -r "async def\|await" cli_portify/` | Yes |
| Gate signatures | Type check all gate returns | Yes |
| Contract schema | Unit test T-U02–U03 | Yes |
| Module structure | 13 files exist under `cli_portify/` | Yes |
| No base module changes | `git diff pipeline/ sprint/` empty | Yes |

### Phase 2 → Phase 3 Gate

| Check | Method | Blocker? |
|-------|--------|----------|
| 16 unit + 1 integration pass | Test suite | Yes |
| Steps 1-4 produce valid artifacts | Integration test T-I01 | Yes |
| Review gate functional | T-U15–U16 | Yes |
| `--dry-run` contract valid | Manual or T-I04 draft | Yes |
| NFR-006 verified | Code review of executor | Yes |

### Phase 3 → Phase 4 Gate

| Check | Method | Blocker? |
|-------|--------|----------|
| 23 unit + 2 integration pass | Test suite | Yes |
| Zero placeholders | T-U18–U19 + manual grep | Yes |
| Brainstorm fallback works | T-I02 | Yes |
| Section 12 content valid | T-U21–U23 | Yes |
| FR mapping complete | Manual review of synthesized spec | Yes |

### Phase 4 → Phase 5 Gate

| Check | Method | Blocker? |
|-------|--------|----------|
| 34 unit + 2 integration pass | Test suite | Yes |
| All 4 terminal states tested | T-U24–U27 | Yes |
| Score computation exact | T-U28–U29 | Yes |
| Malformed output handled | T-U32 | Yes |
| Budget guard functional | T-U34 | Yes |
| Additive-only verified | T-U33 | Yes |

### Phase 5 → Release Gate

| Check | Method | Blocker? |
|-------|--------|----------|
| 37 unit tests pass | `uv run pytest tests/cli_portify/ -v` | Yes |
| 6 integration tests pass | `uv run pytest tests/cli_portify/integration/ -v` | Yes |
| SC-001 verified | T-I03 (end-to-end) | Yes |
| SC-009 verified | grep sweep | Yes |
| SC-011 verified | git diff | Yes |
| All 14 SC verified | Evidence table | Yes |
| No regressions | Full project test suite | Yes |

---

## Appendix: Test Count Summary

| Phase | New Unit | Cumulative Unit | New Integration | Cumulative Integration | Total |
|-------|----------|-----------------|-----------------|------------------------|-------|
| P1 | 10 | 10 | 0 | 0 | 10 |
| P2 | 6 | 16 | 1 | 1 | 17 |
| P3 | 7 | 23 | 1 | 2 | 25 |
| P4 | 11 | 34 | 0 | 2 | 36 |
| P5 | 3 | 37 | 4 | 6 | 43 |

**Final count**: 37 unit tests + 6 integration tests = 43 total tests.

Note: The roadmap specifies SC-013 as "17 unit tests" and SC-014 as "5 integration tests" (later amended to 6). This strategy defines 37 unit tests and 6 integration tests — exceeding the minimum while maintaining focused coverage. The additional unit tests address edge cases identified in the roadmap's Analyzer Concerns (malformed output, empty workflows, name normalization, boundary conditions) which are essential for a 0.85 complexity project.
