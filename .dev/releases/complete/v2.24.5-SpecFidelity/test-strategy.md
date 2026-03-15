---
validation_milestones: 5
interleave_ratio: "1:2"
---

## Test Strategy: v2.24.5 Release

### Overview

Two independent bug fixes (FIX-001 tool schema discovery, FIX-ARG-TOO-LONG embed guard) with a conditional Phase 1.5 branch. Testing must be interleaved with implementation because Phase 0 is a blocking gate, Phase 1.1 must land before combined suite runs, and the conditional branch requires test decisions before coding begins.

---

## 1. Validation Milestones Mapped to Roadmap Phases

### M0 — CLI Empirical Gate (Phase 0)
**What**: Verify `--file` behavior before any code changes.

Tests:
- Manual: `echo "The secret answer is PINEAPPLE." > /tmp/file-test.md && claude --print -p "What is the secret answer?" --file /tmp/file-test.md`
- Manual: `claude --print -p "hello" --max-turns 1` (confirm CLI health)
- Manual: `claude --help | grep -A3 '\-\-file'` (capture format requirements per OQ-5)

Acceptance: Binary result (WORKING/BROKEN) recorded in writing before any code change. Drives Phase 1.5 activation decision.

---

### M1 — FIX-001 Command Assembly Verified (Phase 1.1)
**What**: `--tools default` present, adjacent, and non-regressive in `ClaudeProcess.build_command()`.

Tests:
- Manual pre-check: grep all `ClaudeProcess` subclasses for `build_command` without `super()` (OQ-6)
- `uv run pytest tests/pipeline/test_process.py::test_tools_default_in_command -v`
- `uv run pytest tests/pipeline/test_process.py::TestRequiredFlags -v`
- `uv run pytest tests/pipeline/test_process.py::test_stream_json_matches_sprint_flags -v`
- `uv run pytest tests/pipeline/test_process.py -v` (full file, 0 failures)

Acceptance: All `test_process.py` tests pass. Flag adjacency assertion confirmed (`cmd[cmd.index("--tools") + 1] == "default"`). Legacy flags (`--print`, `--verbose`, `--no-session-persistence`, `--max-turns`, `--output-format`, `-p`) all present.

---

### M2 — FIX-ARG-TOO-LONG Constants and Guard Verified (Phase 1.2)
**What**: Constants derived correctly, assertion fires on import, guard measures composed string.

Tests:
- Unit: `python -c "from superclaude.cli.roadmap.executor import _EMBED_SIZE_LIMIT, _MAX_ARG_STRLEN, _PROMPT_TEMPLATE_OVERHEAD; assert _EMBED_SIZE_LIMIT == 122880"` (import-time assertion tripwire)
- `uv run pytest tests/roadmap/test_file_passing.py::test_embed_size_guard_fallback -v` (renamed test)
- `uv run pytest tests/roadmap/test_file_passing.py::TestComposedStringGuard -v` (new class)
- Boundary test: file at exactly `_EMBED_SIZE_LIMIT` bytes → inline embedding fires (SC-007)
- `uv run pytest tests/roadmap/test_file_passing.py -v` (full file, 0 failures)

Acceptance: `_EMBED_SIZE_LIMIT == 122880`. No `200 * 1024` literal remains. No stale `# 100 KB` comment. Guard uses `composed.encode("utf-8")`. `len(composed) == _EMBED_SIZE_LIMIT` embeds inline. Overflow triggers fallback with `--file` in `extra_args`.

---

### M1.5 — Conditional Fallback Remediation Verified (Phase 1.5, if Phase 0 = BROKEN)
**What**: All non-inheriting executors use inline embedding instead of broken `--file`.

Tests:
- `uv run pytest tests/roadmap/test_file_passing.py::test_inline_embed_fallback_when_file_broken -v`
- `uv run pytest tests/roadmap/test_file_passing.py::test_remediate_inline_embed_replaces_file_flag -v`
- Manual: grep `remediate_executor.py`, `validate_executor.py`, `tasklist/executor.py` for remaining `--file` usage (must be zero after fix)
- If OQ-4 answered yes: verify `--tools default` present in each non-inheriting executor's command construction

Acceptance: No `--file` flag in fallback paths across the four affected files. Conditional test classes pass. OQ-4 resolved and acted upon within this phase.

---

### M3 — Integration and Release Candidate (Phase 2 + Phase 3)
**What**: Full suite regression-free; E2E and smoke tests pass; release artifact ready.

Tests:
- `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` (0 failures, 0 regressions)
- CLI smoke: `superclaude sprint run ... --dry-run` (no error)
- E2E large-input: pipeline run with ≥120 KB spec file through `spec-fidelity` step (no `OSError: [Errno 7]`)
- `git diff --stat` review: only expected files modified
- Manual: confirm no `200 * 1024` literal, no `import resource`, no TODO/placeholder remains

Acceptance: All 14 SC codes verified. Evidence checklist fully checked. Version number confirmed before tagging.

---

## 2. Test Categories

### Unit Tests
**Location**: `tests/pipeline/test_process.py`, `tests/roadmap/test_file_passing.py`

| Test | File | Validates |
|------|------|-----------|
| `test_tools_default_in_command` | `test_process.py` | SC-001: adjacency of `--tools default` |
| `test_required_flags` (updated) | `test_process.py` | SC-002: legacy flags preserved |
| `test_stream_json_matches_sprint_flags` (updated) | `test_process.py` | SC-002: flag set stable |
| `test_embed_size_guard_fallback` (renamed) | `test_file_passing.py` | SC-008: renamed class, constant import |
| `TestComposedStringGuard` (new) | `test_file_passing.py` | SC-009: composed overflow triggers fallback |
| Boundary exact-limit test (new) | `test_file_passing.py` | SC-007: `<=` operator, inline at limit |
| Import-time assertion test | inline `python -c` | SC-005: assert fires on import |

### Integration Tests
**Location**: `tests/sprint/`, `tests/roadmap/`, `tests/pipeline/`

| Test | Command | Validates |
|------|---------|-----------|
| Combined sprint suite | `uv run pytest tests/sprint/ -v` | SC-012: no sprint regressions |
| Combined roadmap suite | `uv run pytest tests/roadmap/ -v` | SC-012: no roadmap regressions |
| Combined pipeline suite | `uv run pytest tests/pipeline/ -v` | SC-012: no pipeline regressions |
| Conditional executor tests (Phase 1.5) | `uv run pytest tests/roadmap/ tests/pipeline/ -v` | SC-011 |

### E2E Tests
**What**: Real process execution with actual file sizes.

| Scenario | Input | Expected |
|----------|-------|----------|
| Large spec file pipeline | ≥120 KB spec | No `OSError`; `spec-fidelity` step completes |
| Inline embed under limit | <120 KB file + small prompt | Content embedded in `-p`, no `--file` in `extra_args` |
| Composed overflow (file + prompt) | File at 90% limit + large prompt | Fallback fires; `--file` in `extra_args`; content absent from `-p` |

### Acceptance Tests
**Manual, evidence-based.**

| Test | Method | Evidence |
|------|--------|----------|
| Phase 0 `--file` gate | Run PINEAPPLE test | Text "WORKING" or "BROKEN" recorded |
| CLI smoke test | `superclaude sprint run ... --dry-run` | Zero error output, exit code 0 |
| `git diff` review | `git diff --stat` before commit | Only 4–7 expected files changed |
| Constant audit | grep for `200 * 1024` | Zero matches |
| No new imports | grep for `import resource` | Zero matches in modified files |

---

## 3. Test-Implementation Interleaving Strategy

Ratio **1:2**: one test-authoring/verification step for every two implementation steps. Justified by the ordering constraint (Phase 1.1 tests must update before combined suite runs) and the conditional branch (Phase 1.5 tests must be designed after Phase 0 result).

```
Phase 0     → [TEST: PINEAPPLE empirical] → Record result
Phase 1.1   → [IMPL: edit process.py] → [TEST: update + add test_process.py tests] → [VERIFY: uv run pytest tests/pipeline/test_process.py]
Phase 1.2   → [IMPL: constants + guard] → [TEST: rename + add test_file_passing.py tests] → [VERIFY: uv run pytest tests/roadmap/test_file_passing.py]
Phase 1.5   → (if BROKEN) [IMPL: replace --file in 4 executors] → [TEST: conditional test classes] → [VERIFY: uv run pytest tests/roadmap/ tests/pipeline/]
Phase 2     → [TEST: full suite + E2E + smoke] → [VERIFY: evidence checklist]
Phase 3     → [TEST: git diff review + version confirmation] → Tag
```

**Rule**: No phase marks complete until its targeted tests are green. Implementation and test edits happen in the same commit unit (not split across commits).

---

## 4. Risk-Based Test Prioritization

| Priority | Risk | Test Focus |
|----------|------|------------|
| **P1 — Critical** | RISK-004: `--file` broken (~80%) | Phase 0 empirical gate; execute before all else |
| **P1 — Critical** | Active `OSError` hard crash (FIX-ARG-TOO-LONG) | Composed-size guard tests, large-input E2E (SC-014) |
| **P2 — High** | RISK-003: index-based assertions break after flag insertion | `test_required_flags` and `test_stream_json_matches_sprint_flags` updated before combined suite runs |
| **P2 — High** | RISK-008: non-inheriting executors lack `--tools default` post-Phase 1.5 | OQ-4 resolution + grep check in Phase 1.5 |
| **P3 — Medium** | RISK-006: template growth exceeds 8 KB overhead | Import-time assertion test; `_PROMPT_TEMPLATE_OVERHEAD >= 4096` verified |
| **P3 — Medium** | RISK-007: Windows 32 KB limit | Deferred (noted, not tested in this release) |
| **P4 — Low** | RISK-001: `--tools default` unintended behavior | Smoke test + full suite (covered by M3) |
| **P4 — Low** | RISK-002: subclass override without `super()` | Pre-edit grep of subclasses (OQ-6 manual check) |
| **P4 — Low** | RISK-005: conservative 8 KB overhead triggers unnecessary fallback | Boundary test at `_EMBED_SIZE_LIMIT` (SC-007 confirms `<=`) |

---

## 5. Acceptance Criteria Per Milestone

### M0 Acceptance
- [ ] `claude --print -p "hello" --max-turns 1` exits 0
- [ ] PINEAPPLE test executed; result is WORKING or BROKEN (not skipped)
- [ ] Result recorded in writing (Phase 1.5 activation decision documented)
- [ ] `claude --help` `--file` format captured for OQ-5

### M1 Acceptance (FIX-001)
- [ ] No subclass overrides `build_command()` without `super()` (OQ-6 resolved)
- [ ] `"--tools" in cmd` is `True`
- [ ] `cmd[cmd.index("--tools") + 1] == "default"` is `True`
- [ ] All six legacy flags still present in command list
- [ ] `uv run pytest tests/pipeline/test_process.py -v` → 0 failures
- [ ] `extra_args` still appends after `--model`

### M2 Acceptance (FIX-ARG-TOO-LONG)
- [ ] `_EMBED_SIZE_LIMIT == 122880` (120 KB exactly)
- [ ] No `200 * 1024` literal in `executor.py`
- [ ] No stale `# 100 KB` comment
- [ ] No `import resource` line added
- [ ] `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096` present; fires on import
- [ ] Guard evaluates `len((step.prompt + "\n\n" + embedded).encode("utf-8")) <= _EMBED_SIZE_LIMIT`
- [ ] Exact-limit case (`len == _EMBED_SIZE_LIMIT`) embeds inline
- [ ] Overflow case falls back; `--file` in `extra_args`; file content absent from captured prompt
- [ ] `uv run pytest tests/roadmap/test_file_passing.py -v` → 0 failures

### M1.5 Acceptance (conditional, Phase 0 = BROKEN only)
- [ ] Zero remaining `--file` usage in fallback paths of `remediate_executor.py`, `validate_executor.py`, `tasklist/executor.py`, `executor.py`
- [ ] OQ-4 resolved: `--tools default` added to non-inheriting executors if assessment confirms needed
- [ ] `test_remediate_inline_embed_replaces_file_flag` passes
- [ ] `test_inline_embed_fallback_when_file_broken` passes
- [ ] `uv run pytest tests/roadmap/ tests/pipeline/ -v` → 0 failures

### M3 Acceptance (Release Candidate)
- [ ] `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` → 0 failures, 0 regressions
- [ ] `superclaude sprint run ... --dry-run` → exit 0, no error output
- [ ] ≥120 KB spec file pipeline run → no `OSError: [Errno 7]`
- [ ] `git diff --stat` shows only expected files (4 unconditional + up to 3 conditional)
- [ ] Evidence checklist from roadmap Phase 2 fully checked
- [ ] Version number confirmed (v2.24.5 or v2.25.1) before tagging

---

## 6. Quality Gates Between Phases

### Gate G0 → G1: After Phase 0
**Block condition**: Phase 0 not executed or result not recorded.  
**Check**: Written record of WORKING/BROKEN exists. Phase 1.5 activation decision documented. No code committed before this gate passes.

### Gate G1 → Combined Suite: After Phase 1.1
**Block condition**: `tests/pipeline/test_process.py` has any failure.  
**Check**: `uv run pytest tests/pipeline/test_process.py -v` → 0 failures. Flag adjacency assertion included. This gate must pass before any combined `tests/sprint/ tests/roadmap/ tests/pipeline/` run, because flag position shifts from Phase 1.1 will break index-based assertions in other suites if Phase 1.1 tests aren't updated first.

### Gate G2: After Phase 1.2
**Block condition**: `tests/roadmap/test_file_passing.py` has any failure.  
**Check**: `uv run pytest tests/roadmap/test_file_passing.py -v` → 0 failures. Constants verified by inspection. Import-time assertion verified. Boundary cases covered.

### Gate G1.5 (conditional): After Phase 1.5
**Block condition**: Any `--file` usage remains in fallback paths; conditional tests fail.  
**Check**: grep clean; `uv run pytest tests/roadmap/ tests/pipeline/ -v` → 0 failures. If OQ-4 was answered yes, `--tools default` grep confirms presence.

### Gate G3 → Release: After Phase 2
**Block condition**: Any of the four validation layers missing evidence.  
**Check**: All four evidence categories present:
1. Empirical CLI validation (Phase 0 result)
2. Unit-level command validation (M1 + M2 test runs)
3. Boundary-condition validation (exact-limit, near-limit, composed overflow)
4. Workflow-level validation (dry-run + large-input E2E)

No tagging until all four layers have documented evidence.

---

## Evidence Collection Checklist (from Roadmap Phase 2, expanded)

- [ ] Phase 0 WORKING/BROKEN result recorded
- [ ] OQ-5: `--file` format from `claude --help` captured
- [ ] OQ-6: subclass review completed, no unsupervised overrides found
- [ ] `_EMBED_SIZE_LIMIT == 122880` confirmed by import test
- [ ] No new imports added (grep `import resource` clean)
- [ ] No `200 * 1024` literal remains (grep clean)
- [ ] `tests/pipeline/test_process.py` green before combined run
- [ ] `tests/roadmap/test_file_passing.py` green
- [ ] Full grouped suite (`sprint/`, `roadmap/`, `pipeline/`) green
- [ ] Dry-run smoke test green
- [ ] ≥120 KB large-input E2E green (no `OSError`)
- [ ] (Conditional) Phase 1.5 executor grep clean + conditional tests green
- [ ] `git diff --stat` reviewed; only expected files changed
