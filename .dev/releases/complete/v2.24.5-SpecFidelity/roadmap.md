---
spec_source: v2.25.1-release-spec.md
complexity_score: 0.5
adversarial: true
---

## Executive Summary

This release addresses two independent but sequentially coordinated bugs in the SuperClaude CLI pipeline:

1. **FIX-001 (Tool Schema Discovery)**: `ClaudeProcess.build_command()` omits `--tools default`, causing subprocess invocations to lack tool access that interactive mode provides automatically.
2. **FIX-ARG-TOO-LONG**: The embed size guard uses a hardcoded 200 KB limit that exceeds the Linux kernel's 128 KB `MAX_ARG_STRLEN`, causing `OSError: [Errno 7] Argument list too long` for large spec files.

**Scope**: 18 total requirements across 4 technical domains (CLI process construction, roadmap executor behavior, test coverage, release validation), 8 identified risks, 7 dependencies, 14 success criteria. Both fixes are narrow in scope (6–7 source files, 2 test files), require no new abstractions, and operate within existing module boundaries.

**Primary delivery risk** is not coding complexity — it is incorrect assumptions about CLI behavior, particularly the Phase 0 `--file` gate. The embed guard fix (FIX-ARG-TOO-LONG) is the **primary critical path** as it addresses an active hard-crash `OSError`. FIX-001 is the parallel secondary track.

**Estimated total effort**: 3–4 hours without Phase 1.5; 5–7 hours with Phase 1.5 (conditional on Phase 0 outcome). These are estimates with explicit conditional branching — not delivery commitments.

**Version note**: Both variants' `spec_source` fields reference `v2.25.1-release-spec.md` while the base variant titles the release `v2.24.5`. This discrepancy requires external resolution against the project's version history before tagging. The merged roadmap uses `v2.24.5` as the working title pending confirmation.

---

## Phased Implementation Plan

### Phase 0: Empirical Validation Gate (Blocking)

**Objective**: Determine whether `claude --file /path` delivers file content to the model before any code changes proceed.

**Milestone M0**: CLI fallback behavior verified and documented. Phase 0 result recorded as WORKING or BROKEN.

#### Phase 0 Tasks

| # | Task | Detail | OQ |
|---|------|--------|-----|
| 0.1 | Verify `claude` CLI availability | `claude --print -p "hello" --max-turns 1` succeeds | — |
| 0.2 | Check `claude --help` for `--file` format | Record whether `file_id:path` prefix is required | OQ-5 (roadmap addition — not in spec Section 11; related to OQ-1 `--file` behavior) |
| 0.3 | Execute empirical test | `echo "The secret answer is PINEAPPLE." > /tmp/file-test.md` then `claude --print -p "What is the secret answer?" --file /tmp/file-test.md` | — |
| 0.4 | Record result | Three named outcomes (exit code 0 only): **WORKING** (response mentions PINEAPPLE); **BROKEN** (response does not mention PINEAPPLE, but exit code is 0); **CLI FAILURE** (subprocess exits non-zero for any reason — do NOT record WORKING or BROKEN; resolve CLI configuration issue and re-run Task 0.1 before proceeding) | — |
| 0.5 | Gate decision | WORKING → skip Phase 1.5, proceed to Phase 1.1. BROKEN → Phase 1.5 activates after Phase 1.2 | — |

**Exit criteria**: Binary result documented. No code changes permitted before this completes. Team knows whether Phase 1.5 is activated.

> This is the highest-risk uncertainty in the release. Do not treat it as optional or informal. The ~80% probability of BROKEN means Phase 1.5 should be treated as likely, not exceptional.

---

### Phase 1.1: FIX-001 — Add `--tools default` to `ClaudeProcess`

**Objective**: Ensure all `ClaudeProcess`-derived subprocesses include `--tools default` without breaking existing flag behavior.

**Milestone M1**: All inherited process-based commands include `--tools default` with no assembly regressions.

#### Phase 1.1 Tasks

| # | Task | Detail | OQ |
|---|------|--------|-----|
| 1.1.1 | Verify no subclass overrides | Read all `ClaudeProcess` subclasses; confirm none override `build_command()` without `super()` | OQ-6 (roadmap addition — implements RISK-002 mitigation from spec Section 7; not in spec Section 11 Open Items) |
| 1.1.2 | Edit `process.py` | Add `"--tools", "default"` after `--no-session-persistence` and before `--max-turns` in `build_command()` | — |
| 1.1.3 | Update `test_required_flags` | Assert `--tools` and `default` present in command list | — |
| 1.1.4 | Update `test_stream_json_matches_sprint_flags` | Assert `--tools` and `default` present | — |
| 1.1.5 | Add `test_tools_default_in_command` | Assert adjacency: `cmd[cmd.index("--tools") + 1] == "default"` | — |
| 1.1.6 | Run pipeline tests | `uv run pytest tests/pipeline/test_process.py -v` — 0 failures | — |

**Ordering constraint**: This phase must complete before any combined test suite run (Phase 2) to avoid index-based assertion failures from flag position shifts.

**Parallelization**: Phases 1.1 and 1.2 are architecturally independent — different source files, different test files, no shared intermediate state. They **can execute in parallel** after Phase 0 completes on a multi-person team.

> **Solo-engineer wave cadence alternative**: Wave 1 (design verification for both tracks: confirm subclass behavior, confirm constant derivation) → Wave 2 (implementation of both tracks) → Wave 3 (combined test + validation). This reduces context-switching cost on a single-engineer team.

---

### Phase 1.2: FIX-ARG-TOO-LONG — Constants and Guard Logic

**Objective**: Replace hardcoded embed limit with derived constants; fix guard to measure composed string. This is the **primary critical path** fix addressing an active hard-crash failure mode.

**Milestone M2**: `_EMBED_SIZE_LIMIT` = 120 KB, derived from named constants; guard measures `prompt + embedded` composed byte length.

#### Phase 1.2 Tasks

| # | Task | Detail | OQ |
|---|------|--------|-----|
| 1.2.1 | Replace constants in `executor.py` | Remove `_EMBED_SIZE_LIMIT = 200 * 1024`. Add the following three constants with their required per-constant inline comments: (1) `_MAX_ARG_STRLEN = 128 * 1024` — comment must state this is the Linux kernel compile-time constant; (2) `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024` — comment must note the 2.3x safety factor and the measured template peak (~3.4 KB); (3) `_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD` — comment must note its derivation (MAX_ARG_STRLEN minus overhead) and the resulting byte value (120 KB = 122,880 bytes). Remove any stale `# 100 KB` comment. No `import resource`. | — |
| 1.2.2 | Add module-level assertion | `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096, "<error message>"` — this is a mandatory FR-ATL.1 deliverable, not an open question. The assertion must appear **immediately after the three constant definitions** (not elsewhere in the module). The error message must state the kernel margin rationale and the measured template peak (~3.4 KB). The assertion fires on every `import executor` call and therefore on every test run. | — |
| 1.2.3 | Fix embed guard | Evaluate `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT` where `composed = step.prompt + "\n\n" + embedded`. Use `<=` operator (not `<`) — boundary semantics require that at-limit inputs embed inline, not trigger fallback. Add the following verbatim code comment adjacent to the guard expression: `# <= is intentional; _EMBED_SIZE_LIMIT = 120 KB is safely below MAX_ARG_STRLEN = 128 KB`. Update warning log to report "composed prompt" and byte count. | — |
| 1.2.4 | Update renamed test class | In `tests/roadmap/test_file_passing.py`, update the renamed class `test_embed_size_guard_fallback` (formerly `test_100kb_guard_fallback`): update docstring to reference `_EMBED_SIZE_LIMIT`. The test must import `_EMBED_SIZE_LIMIT` from `executor` and use it in assertions (auto-adapts to new value — no hardcoded byte counts). | — |
| 1.2.5 | Add `TestComposedStringGuard` | In `tests/roadmap/test_file_passing.py`, add class `TestComposedStringGuard` (per spec Section 4.2) with test method named `test_prompt_plus_embedded_exceeds_limit` (per spec Section 8.1 test inventory). Scenario: file at 90% of `_EMBED_SIZE_LIMIT` + prompt large enough to exceed composed limit → fallback fires; file content absent from prompt; `--file` in `extra_args`. | — |
| 1.2.6 | Add exact-limit boundary test | Verify composed length exactly equal to `_EMBED_SIZE_LIMIT` still embeds inline (boundary inclusion — `<=` is intentional, as specified in Task 1.2.3 implementation) | — |
| 1.2.7 | Run roadmap tests | `uv run pytest tests/roadmap/test_file_passing.py -v` — 0 failures | — |

> Senior review attention should concentrate on embed guard constants, composed-size measurement, and large-input boundary tests.

---

### Phase 1.3: FR-ATL.3 — Rename Test (Parallel with Phase 1.2)

**Objective**: Rename `test_100kb_guard_fallback` to `test_embed_size_guard_fallback` in `tests/roadmap/test_file_passing.py`.

**Parallelization note**: This phase can execute concurrently with Phase 1.2 on a multi-person team. It is a distinct parallel track per spec Section 4.6 `[parallel with 1.2]` — not a sub-task of Phase 1.2.

#### Phase 1.3 Tasks

| # | Task | Detail | OQ |
|---|------|--------|-----|
| 1.3.1 | Rename test class | `test_100kb_guard_fallback` → `test_embed_size_guard_fallback` in `tests/roadmap/test_file_passing.py` | — |

---

### Phase 1.5: Conditional — `--file` Fallback Remediation

**Activates only if Phase 0 result is BROKEN.**

**Objective**: Replace broken `--file`-based fallback paths with inline embedding across all affected non-inheriting executors.

**Milestone M1.5**: Fallback path no longer depends on a broken CLI mechanism.

#### Phase 1.5 Tasks

| # | Task | Detail | OQ |
|---|------|--------|-----|
| 1.5.1 | Fix `executor.py` fallback path | Replace `--file` with inline `-p` embedding | — |
| 1.5.2 | Fix `remediate_executor.py:177` | Replace unconditional `--file` with inline embedding | — |
| 1.5.3 | Fix `validate_executor.py:109` | Replace `--file` with inline embedding | — |
| 1.5.4 | Fix `tasklist/executor.py:121` | Replace `--file` with inline embedding | — |
| 1.5.5 | Assess OQ-4 for non-inheriting executors | Determine if these executors also need `--tools default`; apply if yes | OQ-4 |
| 1.5.6 | Add conditional tests | `test_remediate_inline_embed_replaces_file_flag`, `test_inline_embed_fallback_when_file_broken` — note: `test_inline_embed_fallback_when_file_broken` must be parameterized over each of the three affected conditional executors (`remediate_executor`, `validate_executor`, `tasklist/executor`) using their respective `_EMBED_SIZE_LIMIT` values (per spec Section 8.1) | — |
| 1.5.7 | Run affected test suites | `uv run pytest tests/roadmap/ tests/pipeline/ -v` — 0 failures | — |

**Exit criteria**: BROKEN outcome has a forward-path remediation in all relevant executors. Conditional success criteria SC-011 met. If Phase 0 is BROKEN, this phase becomes release-blocking.

---

### Phase 2: Integration Verification

> **Cross-reference note**: The validation tasks in this phase correspond to spec Section 4.6 Phase 3 (Full Validation). Phase numbering differs from the spec — spec Phase 3 tasks 3.1, 3.4, and 3.5 appear here as roadmap Tasks 2.1, 2.2, and 2.3 respectively.

**Objective**: Full test suite green; no regressions. Empirical, unit, boundary, and workflow validation layers all have evidence.

**Milestone M3**: Release candidate validated across all four validation layers.

#### Phase 2 Tasks

| # | Task | Detail |
|---|------|--------|
| 2.1 | Combined test run | `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` — 0 failures. Note: `test_remediate_executor.py` and `test_inline_fallback.py` within `tests/roadmap/` only exist if Phase 1.5 was activated (Phase 0 = BROKEN). Their absence when Phase 0 = WORKING is expected and not a failure. |
| 2.2 | CLI smoke test | `superclaude sprint run ... --dry-run` completes without error |
| 2.3 | Large file E2E test | Pipeline run with ≥120 KB spec file completes `spec-fidelity` step without `OSError` |

> **Do not mark the release complete until all four validation layers have evidence. Passing only unit tests is insufficient for this change set.**

#### Four-Layer Validation Model

1. **Empirical CLI validation** — Phase 0 `--file` proof
2. **Unit-level command validation** — command list structure and invariants
3. **Boundary-condition validation** — exact limit, near limit, composed overflow
4. **Workflow-level validation** — sprint dry-run and large spec execution path

#### Evidence Collection Checklist

- [ ] Phase 0 result captured
- [ ] Subclass review completed
- [ ] Constants updated and audited
- [ ] No new imports added
- [ ] Targeted tests green
- [ ] Grouped tests green (`sprint/`, `roadmap/`, `pipeline/`)
- [ ] Dry-run green
- [ ] Large-input scenario green (≥120 KB, no `OSError`)

---

### Phase 3: Commit and Release

**Milestone M4**: Release tagged and committed.

#### Phase 3 Tasks

| # | Task | Detail |
|---|------|--------|
| 3.1 | Final `git diff` review | Confirm only expected files changed |
| 3.2 | Commit FIX-001 | `feat(pipeline): add --tools default to ClaudeProcess.build_command()` |
| 3.3 | Commit FIX-ARG-TOO-LONG | `fix(executor): derive embed limit from MAX_ARG_STRLEN, measure composed string` |
| 3.4 | Commit Phase 1.5 (if activated) | `fix(executors): replace --file fallback with inline embedding` |
| 3.5 | Resolve version number | Confirm v2.24.5 or v2.25.1 against project version history before tagging |
| 3.6 | Tag release | `v2.24.5` (pending version confirmation) |

---

## Risk Assessment

### Risk Table with Contingencies

| Risk ID | Risk | Severity | Probability | Mitigation | Contingency |
|---------|------|----------|-------------|------------|-------------|
| RISK-004 | `--file` fallback broken | High | ~80% | Phase 0 gate is mandatory and blocking | Replace broken fallback path across all affected executors in the same release cycle (Phase 1.5) |
| RISK-008 | Non-inheriting executors lack `--tools default` | Medium | Conditional on Phase 1.5 | OQ-4 assessed in Phase 1.5.5; same work cycle | Apply `--tools default` to affected executors within Phase 1.5 if assessment confirms missing |
| RISK-006 | Template growth exceeds 8 KB overhead | Medium | Low | Named constant + 2.3x safety factor + module-level assertion tripwire | Tighten overhead constant and re-run boundary tests in a maintenance release |
| RISK-007 | Windows 32 KB limit differs from Linux | Medium | Low | Deferred; Linux-first is correct priority | Open separate platform-compatibility task; do not expand this release scope |
| RISK-003 | Index-based test assertions break after flag insertion | Low | High if misordered | Ordering constraint enforced: Phase 1.1 before Phase 2 | Re-run `test_process.py` after Phase 1.1 and fix any positional failures before proceeding |
| RISK-001 | `--tools default` causes unintended subprocess behavior | Low | Very low | Default tool set matches interactive mode baseline | Revert flag insertion and investigate behavioral delta via smoke tests |
| RISK-002 | Subclass drops `--tools default` via override without `super()` | Low | Very low | Verified in Phase 1.1.1 before any modification | Modify affected subclasses to preserve inheritance in Phase 1.1 scope |
| RISK-005 | 8 KB overhead is unnecessarily conservative, triggers premature fallback | Low | Low | Accept conservative behavior as functionally correct | No action required; correct behavior is a functionally acceptable trade-off |

**Primary critical path risk**: RISK-004 at ~80% probability. Treat Phase 1.5 as likely, not exceptional. The embed guard fix is the primary critical path item as it addresses an active hard-crash `OSError`, not a hypothetical risk.

---

## Resource Requirements

### Engineering Resources

- **Primary implementation owner**: Python CLI engineer familiar with command assembly and roadmap executor flow
- **Validation owner**: QA-focused engineer or same owner performing evidence-based verification
- **Review focus**: Embed guard constants and boundary tests (primary); command construction correctness (secondary); conditional path if Phase 1.5 activates

### Prerequisites

All must be available before work begins:

| Dependency | ID | Requirement |
|------------|-----|-------------|
| `claude` CLI | DEP-001 | Installed, authenticated, functional |
| `uv` package manager | DEP-002 | Installed and operational |
| Reference documents | DEP-007 | `docs/generated/` normative specs accessible |
| Linux kernel `MAX_ARG_STRLEN` | DEP-006 | Compile-time constant (128 KB); not runtime-queryable |
| `ClaudeProcess` base class | DEP-003 | Single shared method both fixes interact with |

### Files Modified

| File | Phase | Change Type |
|------|-------|-------------|
| `src/superclaude/cli/pipeline/process.py` | 1.1 | 2-line addition |
| `src/superclaude/cli/roadmap/executor.py` | 1.2 | Constant replacement + guard fix |
| `tests/pipeline/test_process.py` | 1.1 | Update 2 tests, add 1 test |
| `tests/roadmap/test_file_passing.py` | 1.2, 1.3 | Rename 1 test class, add 2 test classes |
| `src/superclaude/cli/roadmap/remediate_executor.py` | 1.5 (conditional) | Replace `--file` usage |
| `src/superclaude/cli/roadmap/validate_executor.py` | 1.5 (conditional) | Replace `--file` usage |
| `src/superclaude/cli/tasklist/executor.py` | 1.5 (conditional) | Replace `--file` usage |

---

## Success Criteria and Validation

### Automated Validation

| Criterion | Validation Command | Phase | SC Codes |
|-----------|-------------------|-------|----------|
| `--tools` and `default` present and adjacent in command | `uv run pytest tests/pipeline/test_process.py -v` | 1.1 | SC-001, SC-002, SC-003 |
| Constants derived, assertion present, guard correct | `uv run pytest tests/roadmap/test_file_passing.py -v` | 1.2 | SC-004–SC-009 |
| Phase 0 result recorded | Human observation | 0 | SC-010 |
| Conditional fallback tests pass (if Phase 1.5) | `uv run pytest tests/roadmap/ tests/pipeline/ -v` | 1.5 | SC-011 |
| Full suite no regressions | `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` | 2 | SC-012 |
| CLI smoke test passes | `superclaude sprint run ... --dry-run` | 2 | SC-013 |
| ≥120 KB spec, no `OSError` | Pipeline with large spec file | 2 | SC-014 |

### Success Criteria Grouping

**A. Command assembly**: `--tools` present; `default` adjacent; legacy flags preserved; `extra_args` ordering preserved; conditional `--model` behavior preserved.

**B. Embed guard**: `_EMBED_SIZE_LIMIT` derived from named constants; import-time assertion present; guard evaluates composed byte length; exact-limit case embeds inline; overflow case falls back correctly.

**C. Test suite**: Pipeline tests pass; renamed guard test passes; `TestComposedStringGuard` passes; grouped sprint/roadmap/pipeline suite passes.

**D. Operational**: Phase 0 result recorded; sprint dry-run passes; large spec file (≥120 KB) completes without `Argument list too long`; fallback remediation tests pass if Phase 0 is BROKEN.

---

## Timeline Estimates

These are conditional estimates — not delivery commitments. Actual time depends on Phase 0 outcome, engineer familiarity with the executor codebase, and state of existing test infrastructure.

| Phase | Effort Estimate | Depends On | Parallelizable |
|-------|----------------|------------|----------------|
| Phase 0 | 15–30 min | CLI availability | No (blocking gate) |
| Phase 1.1 | 45–60 min | Phase 0 complete | Yes, with Phase 1.2 (multi-person) |
| Phase 1.2 | 60–90 min | Phase 0 complete | Yes, with Phase 1.1 (multi-person) |
| Phase 1.3 | 5–10 min | Phase 0 complete | Yes, parallel with Phase 1.2 |
| Phase 1.5 | 90–120 min | Phase 0 = BROKEN | No (sequential after 1.1 + 1.2) |
| Phase 2 | 30–45 min | All prior phases | No |
| Phase 3 | 15–20 min | Phase 2 green | No |

**Total without Phase 1.5**: ~3–4 hours
**Total with Phase 1.5**: ~5–7 hours

### Critical Path

```
Phase 0 → (Phase 1.1 ‖ Phase 1.2 ‖ Phase 1.3) → [Phase 1.5 if BROKEN] → Phase 2 → Phase 3
```

Phases 1.1, 1.2, and 1.3 are independent and can execute in parallel after Phase 0 completes on a multi-person team. The primary parallelization opportunity is these three tracks.

**Primary critical path item**: The embed guard fix (Phase 1.2) — observed hard-crash failure. If Phase 0 returns BROKEN, Phase 1.5 joins the critical path and becomes release-blocking.

**Solo-engineer cadence**: Wave 1 (Phase 0 + design verification for both tracks) → Wave 2 (Phase 1.1 + Phase 1.2 + Phase 1.3 implementation + Phase 1.5 if triggered) → Wave 3 (Phase 2 + Phase 3).
