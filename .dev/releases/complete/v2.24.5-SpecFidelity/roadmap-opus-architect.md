

---
spec_source: v2.25.1-release-spec.md
complexity_score: 0.5
primary_persona: architect
---

# v2.24.5 Release Roadmap: Tool Schema Discovery Fix + Argument Too Long Fix

## Executive Summary

This release addresses two independent but sequentially coordinated bugs in the SuperClaude CLI pipeline:

1. **FIX-001 (Tool Schema Discovery)**: `ClaudeProcess.build_command()` omits `--tools default`, causing subprocess invocations to lack tool access that interactive mode provides automatically.
2. **FIX-ARG-TOO-LONG**: The embed size guard uses a hardcoded 200 KB limit that exceeds the Linux kernel's 128 KB `MAX_ARG_STRLEN`, causing `OSError: [Errno 7] Argument list too long` for large spec files.

Both fixes are narrow in scope (6 source files, 2 test files), require no new abstractions, and operate within existing module boundaries. The primary complexity driver is a **Phase 0 empirical gate** that determines whether a conditional remediation path (Phase 1.5) activates across 4 executor files.

**Estimated total effort**: 4–8 hours depending on Phase 0 outcome.

---

## Phased Implementation Plan

### Phase 0: Empirical Validation Gate (Blocking)

**Objective**: Determine whether `claude --file /path` delivers file content to the model.

**Milestone**: Phase 0 result recorded as WORKING or BROKEN.

| # | Task | Detail |
|---|------|--------|
| 0.1 | Verify `claude` CLI availability | `claude --print -p "hello" --max-turns 1` succeeds |
| 0.2 | Check `claude --help` for `--file` format | Record whether `file_id:path` prefix is required (OQ-5) |
| 0.3 | Execute empirical test | `echo "The secret answer is PINEAPPLE." > /tmp/file-test.md` then `claude --print -p "What is the secret answer?" --file /tmp/file-test.md` |
| 0.4 | Record result | WORKING (mentions PINEAPPLE) or BROKEN (does not) |
| 0.5 | Gate decision | WORKING → skip Phase 1.5, proceed to Phase 1.1. BROKEN → Phase 1.5 activates after Phase 1.2 |

**Exit criteria**: Binary result documented. No code changes permitted before this completes.

---

### Phase 1.1: FIX-001 — Add `--tools default` to `ClaudeProcess`

**Objective**: Ensure all `ClaudeProcess`-derived subprocesses include `--tools default`.

**Milestone**: `--tools default` present in all `build_command()` output; no subclass overrides broken.

| # | Task | Detail |
|---|------|--------|
| 1.1.1 | Verify no subclass overrides | Read all `ClaudeProcess` subclasses, confirm none override `build_command()` without `super()` (OQ-6) |
| 1.1.2 | Edit `process.py` | Add `"--tools", "default"` between `--no-session-persistence` and `--max-turns` in `build_command()` |
| 1.1.3 | Update `test_required_flags` | Assert `--tools` and `default` present in command list |
| 1.1.4 | Update `test_stream_json_matches_sprint_flags` | Assert `--tools` and `default` present |
| 1.1.5 | Add `test_tools_default_in_command` | Assert adjacency: `cmd[cmd.index("--tools") + 1] == "default"` |
| 1.1.6 | Run pipeline tests | `uv run pytest tests/pipeline/test_process.py -v` — 0 failures |

**Ordering constraint**: This phase must complete before any combined test suite run (Phase 3) to avoid index-based assertion failures from flag position shifts.

---

### Phase 1.2: FIX-ARG-TOO-LONG — Constants and Guard Logic

**Objective**: Replace hardcoded embed limit with derived constants; fix guard to measure composed string.

**Milestone**: `_EMBED_SIZE_LIMIT` = 120 KB, derived from named constants; guard measures `prompt + embedded`.

| # | Task | Detail |
|---|------|--------|
| 1.2.1 | Replace constants in `executor.py` | Remove `_EMBED_SIZE_LIMIT = 200 * 1024`. Add `_MAX_ARG_STRLEN = 128 * 1024`, `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024`, `_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD`. Each with inline derivation comment. Remove any stale `# 100 KB` comment. No `import resource`. |
| 1.2.2 | Add module-level assertion | `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096, "..."` with kernel margin rationale and measured template peak (~3.4 KB) |
| 1.2.3 | Fix embed guard | Evaluate `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT` where `composed = step.prompt + "\n\n" + embedded`. Update warning log to report "composed prompt" and byte count. Add `<=` intentionality comment. |
| 1.2.4 | Rename test class | `test_100kb_guard_fallback` → `test_embed_size_guard_fallback`. Update docstring to reference `_EMBED_SIZE_LIMIT`. Import and use the constant. |
| 1.2.5 | Add `TestComposedStringGuard` | New test class: file at 90% of limit + large prompt exceeds limit → fallback fires, file content absent from prompt, `--file` in `extra_args` |
| 1.2.6 | Run roadmap tests | `uv run pytest tests/roadmap/test_file_passing.py -v` — 0 failures |

---

### Phase 1.5 (Conditional): `--file` Fallback Remediation

**Activates only if Phase 0 result is BROKEN.**

**Objective**: Replace `--file` usage with inline embedding across all non-inheriting executors.

**Milestone**: All 4 executor fallback paths use inline embedding; conditional tests pass.

| # | Task | Detail |
|---|------|--------|
| 1.5.1 | Fix `executor.py` fallback path | Replace `--file` with inline `-p` embedding |
| 1.5.2 | Fix `remediate_executor.py:177` | Replace unconditional `--file` with inline embedding |
| 1.5.3 | Fix `validate_executor.py:109` | Replace `--file` with inline embedding |
| 1.5.4 | Fix `tasklist/executor.py:121` | Replace `--file` with inline embedding |
| 1.5.5 | Assess OQ-4 | Determine if these executors also need `--tools default`; apply if yes |
| 1.5.6 | Add conditional tests | `test_remediate_inline_embed_replaces_file_flag`, `test_inline_embed_fallback_when_file_broken` |
| 1.5.7 | Run affected test suites | `uv run pytest tests/roadmap/ tests/pipeline/ -v` — 0 failures |

---

### Phase 2: Integration Verification

**Objective**: Full test suite green; no regressions.

| # | Task | Detail |
|---|------|--------|
| 2.1 | Combined test run | `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` — 0 failures |
| 2.2 | CLI smoke test | `superclaude sprint run ... --dry-run` completes without error |
| 2.3 | Large file E2E test | Pipeline run with ≥120 KB spec file completes `spec-fidelity` step without `OSError` |

**Milestone**: SC-012, SC-013, SC-014 all pass.

---

### Phase 3: Commit and Release

| # | Task | Detail |
|---|------|--------|
| 3.1 | Final `git diff` review | Confirm only expected files changed |
| 3.2 | Commit FIX-001 | `feat(pipeline): add --tools default to ClaudeProcess.build_command()` |
| 3.3 | Commit FIX-ARG-TOO-LONG | `fix(executor): derive embed limit from MAX_ARG_STRLEN, measure composed string` |
| 3.4 | Commit Phase 1.5 (if activated) | `fix(executors): replace --file fallback with inline embedding` |
| 3.5 | Tag release | `v2.24.5` |

---

## Risk Assessment and Mitigation

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| **RISK-004**: `--file` fallback broken | High | ~80% | Phase 0 gate is mandatory. Phase 1.5 contingency is fully specified. |
| **RISK-008**: Non-inheriting executors lack `--tools default` | Medium | Conditional on Phase 1.5 | OQ-4 assessed in Phase 1.5.5; same work cycle. |
| **RISK-007**: Windows 32 KB limit | Medium | Low | Deferred. Two short tokens negligible. Linux-first is correct priority. |
| **RISK-006**: Template growth exceeds 8 KB | Medium | Low | Named constant + 2.3x safety factor + module-level assertion tripwire. |
| **RISK-003**: Index-based test assertions break | Low | High if misordered | Ordering constraint enforced: Phase 1.1 before Phase 2. |
| **RISK-001**: `--tools default` causes unintended behavior | Low | Very low | Default tool set matches interactive mode. |
| **RISK-002**: Subclass drops `--tools default` | Low | Very low | Verified in Phase 1.1.1. |
| **RISK-005**: 8 KB overhead too conservative | Low | Low | Unnecessary fallback is functionally correct. |

**Highest-priority architectural risk**: RISK-004. The ~80% probability of `--file` being broken means Phase 1.5 should be treated as likely, not exceptional. Plan time accordingly.

---

## Resource Requirements and Dependencies

### Prerequisites (must be available before work begins)

1. **`claude` CLI** — installed, authenticated, functional (DEP-001)
2. **`uv` package manager** — installed and operational (DEP-002)
3. **Reference documents** — `docs/generated/` normative specs accessible (DEP-007)

### Files Modified

| File | Phase | Change Type |
|------|-------|-------------|
| `src/superclaude/cli/pipeline/process.py` | 1.1 | 2-line addition |
| `src/superclaude/cli/roadmap/executor.py` | 1.2 | Constant replacement + guard fix |
| `tests/pipeline/test_process.py` | 1.1 | Update 2 tests, add 1 test |
| `tests/roadmap/test_file_passing.py` | 1.2 | Rename 1 test class, add 1 test class |
| `src/superclaude/cli/roadmap/remediate_executor.py` | 1.5 (conditional) | Replace `--file` usage |
| `src/superclaude/cli/roadmap/validate_executor.py` | 1.5 (conditional) | Replace `--file` usage |
| `src/superclaude/cli/tasklist/executor.py` | 1.5 (conditional) | Replace `--file` usage |

### External Dependencies

- **Linux kernel `MAX_ARG_STRLEN`** (128 KB) — compile-time constant, not runtime-queryable (DEP-006)
- **`ClaudeProcess` base class** — single shared method both fixes interact with (DEP-003)

---

## Success Criteria and Validation Approach

### Automated Validation (must all pass)

| Criterion | Validation Command | Phase |
|-----------|--------------------|-------|
| SC-001, SC-002 | `uv run pytest tests/pipeline/test_process.py -v` | 1.1 |
| SC-003 | Same as above, 0 failures | 1.1 |
| SC-004, SC-005, SC-006, SC-007 | `uv run pytest tests/roadmap/test_file_passing.py -v` | 1.2 |
| SC-008, SC-009 | Same as above | 1.2 |
| SC-010 | Phase 0 result recorded | 0 |
| SC-011 | Conditional tests pass (if Phase 1.5) | 1.5 |
| SC-012 | `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` | 2 |
| SC-013 | `superclaude sprint run ... --dry-run` | 2 |
| SC-014 | Pipeline with ≥120 KB spec, no `OSError` | 2 |

### Manual Validation

- Phase 0 empirical test (SC-010): human-observed output
- CLI smoke test (SC-013): human-observed completion
- Large file E2E (SC-014): human-observed step completion

---

## Timeline Estimates

| Phase | Effort | Depends On | Parallelizable |
|-------|--------|------------|----------------|
| Phase 0 | 15–30 min | CLI availability | No (blocking gate) |
| Phase 1.1 | 45–60 min | Phase 0 complete | Yes, with Phase 1.2 after Phase 0 |
| Phase 1.2 | 60–90 min | Phase 0 complete | Yes, with Phase 1.1 after Phase 0 |
| Phase 1.5 | 90–120 min | Phase 0 = BROKEN | No (sequential after 1.1 + 1.2) |
| Phase 2 | 30–45 min | All prior phases | No |
| Phase 3 | 15–20 min | Phase 2 green | No |

**Total without Phase 1.5**: ~3–4 hours
**Total with Phase 1.5**: ~5–7 hours

**Critical path**: Phase 0 → (Phase 1.1 ‖ Phase 1.2) → Phase 1.5 (if needed) → Phase 2 → Phase 3

Phases 1.1 and 1.2 are independent and can execute in parallel after Phase 0 completes. This is the primary parallelization opportunity.
