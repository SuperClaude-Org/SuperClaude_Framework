---
spec_source: v2.25.1-release-spec.md
generated: "2026-03-15T00:00:00Z"
generator: requirements-extraction-agent-v1
functional_requirements: 12
nonfunctional_requirements: 6
total_requirements: 18
complexity_score: 0.5
complexity_class: moderate
domains_detected: 4
risks_identified: 8
dependencies_identified: 7
success_criteria_count: 14
extraction_mode: full
pipeline_diagnostics: {elapsed_seconds: 94.0, started_at: "2026-03-15T04:01:29.370117+00:00", finished_at: "2026-03-15T04:03:03.384882+00:00"}
---

## Functional Requirements

**FR-001** — `ClaudeProcess.build_command()` must include `--tools` and `default` as adjacent list elements in the returned command list, positioned between `--no-session-persistence` and `--max-turns`.

**FR-002** — All flags present before this fix (`--print`, `--verbose`, `--no-session-persistence`, `--max-turns`, `--output-format`, `-p`) must remain in the returned command list after adding `--tools default`.

**FR-003** — The `extra_args` passthrough mechanism must continue to append after `--model` in the assembled command list.

**FR-004** — The `--model` flag must remain conditional on `self.model` being non-empty.

**FR-005** — A regression test `test_tools_default_in_command` must be added to `tests/pipeline/test_process.py` asserting `--tools default` is present and adjacent.

**FR-006** — Existing tests `test_required_flags` and `test_stream_json_matches_sprint_flags` must be updated to assert presence of `--tools` and `default`.

**FR-007** — Replace `_EMBED_SIZE_LIMIT = 200 * 1024` with three module-level constants in `executor.py`: `_MAX_ARG_STRLEN = 128 * 1024`, `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024`, and `_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD` (120 KB). Each constant must carry an inline comment explaining its derivation. No `import resource` line. No stale `# 100 KB` comment.

**FR-008** — A module-level `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096` must be present immediately after the three constant definitions, with an error message stating the kernel margin rationale and the measured template peak (~3.4 KB). The assertion must fire on every `import executor` call.

**FR-009** — The embed guard in `executor.py` must evaluate `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT` where `composed = step.prompt + "\n\n" + embedded`. The warning log must report "composed prompt" and actual byte count. A code comment adjacent to the guard must state that `<=` is intentional and that `_EMBED_SIZE_LIMIT = 120 KB` is safely below `MAX_ARG_STRLEN = 128 KB`.

**FR-010** — `test_100kb_guard_fallback` must be renamed to `test_embed_size_guard_fallback`. The class docstring must reference `_EMBED_SIZE_LIMIT` instead of "100KB". Test logic must import `_EMBED_SIZE_LIMIT` and auto-adapt to the new value.

**FR-011** — A new test class `TestComposedStringGuard` must be added to `tests/roadmap/test_file_passing.py`. It must: create a file at 90% of `_EMBED_SIZE_LIMIT`; create a prompt large enough that `prompt + embedded` exceeds the limit; assert file content is NOT in the captured prompt (fallback fired); assert `--file` flags are present in `extra_args`.

**FR-012** — Phase 0 empirical validation of `--file` fallback must be executed before any code changes: run `echo "The secret answer is PINEAPPLE." > /tmp/file-test.md` then `claude --print -p "What is the secret answer?" --file /tmp/file-test.md`. Result must be recorded as WORKING (response mentions PINEAPPLE) or BROKEN (does not). If BROKEN, `remediate_executor.py:177`, `executor.py` fallback path, `validate_executor.py:109`, and `tasklist/executor.py:121` must be fixed to use inline embedding instead of `--file`.

---

## Non-Functional Requirements

**NFR-001** — No performance regression: subprocess start time must be unchanged; `--tools default` adds less than 1ms to flag parsing.

**NFR-002** — Full backwards compatibility: all existing callers must be unaffected; full test suite must be green after changes.

**NFR-003** — No new module dependencies introduced: zero new import lines added to any modified file.

**NFR-004** — Behavioral change is strictly additive (crash → fallback): no regression for inputs below 120 KB; all existing tests must pass without modification.

**NFR-005** — All existing tests must pass at 100% pass rate under `uv run pytest` with no test modifications beyond those explicitly specified.

**NFR-006** — Zero magic numbers: every constant must have a derivation comment; code must be self-documenting with respect to the OS constraint relationship.

---

## Complexity Assessment

**complexity_score: 0.5 — moderate**

Scoring rationale:
- **Scope is narrow**: Changes touch at most 6 source files and 2 test files. No new files are created.
- **Two independent fixes**: FIX-001 is a 2-line addition; FIX-ARG-TOO-LONG involves constant replacement and guard logic adjustment. Neither requires architectural redesign.
- **Conditional branch (Phase 1.5)**: The `--file` fallback investigation adds meaningful decision complexity — an empirical pre-condition gates a conditional code path across 4 executors. This is the primary complexity driver.
- **Implementation ordering constraint**: FIX-001 must land before the combined test suite runs because it shifts flag positions in the command list. This sequencing constraint adds coordination overhead.
- **No new abstractions**: Both fixes work within existing module boundaries. No new classes, interfaces, or abstractions are introduced.
- **Test surface is manageable**: 7 unit tests, 3 integration test commands, 2 manual/E2E scenarios.

The spec's own `complexity_score: 0.5` and `complexity_class: moderate` are confirmed by this analysis.

---

## Architectural Constraints

1. **Base class inheritance for FIX-001**: `--tools default` must be added only to `ClaudeProcess.build_command()` in `pipeline/process.py`. All subclasses (`SprintProcess`, `RoadmapProcess`, etc.) inherit it automatically. No subclass modifications are permitted.

2. **Non-inheriting executors are out of scope for FIX-001**: `remediate_executor.py`, `validate_executor.py`, and `tasklist/executor.py` do not inherit from `ClaudeProcess`. They build commands independently. `--tools default` does not propagate to these files unless Phase 1.5 activates (tracked as OQ-4).

3. **`extra_args` passthrough contract must be preserved**: The mechanism by which `executor.py` sets `extra_args` before `ClaudeProcess` is constructed, and `build_command()` appends them after `--model`, must remain unchanged.

4. **`_EMBED_SIZE_LIMIT` must derive from `_MAX_ARG_STRLEN`**: The constant must not be hardcoded. Its value must be computable from the named OS constant minus the named overhead constant, making the OS constraint relationship explicit and auditable.

5. **Guard must measure the full composed `-p` argument**: Not the embedded portion alone. The composed string is `step.prompt + "\n\n" + embedded`.

6. **No `import resource`**: The Linux `MAX_ARG_STRLEN` is a compile-time kernel constant, not exposed via `getrlimit()`. It must be encoded as a Python constant, not queried at runtime.

7. **Phase 0 is a blocking gate**: No code changes may be committed until the `--file` empirical validation result is recorded. Phase 1.5 is activated or skipped entirely based on that single binary outcome.

8. **UV for all Python operations**: All test runs and script executions must use `uv run pytest` and `uv run python`. Direct `python` or `pip` invocations are prohibited per project CLAUDE.md.

9. **Implementation ordering**: Phase 1.1 (`process.py` edit) must complete before any combined test suite run to avoid index-based assertion failures caused by flag position shifts.

---

## Risk Inventory

**RISK-001** — `--tools default` enables a previously hidden tool, causing unintended model behavior.
- Severity: **Low**
- Mitigation: The default tool set is stable and identical to interactive mode. Subprocess mode was the anomaly. No behavioral surprise expected.

**RISK-002** — A subclass overrides `build_command()` without calling `super()`, silently dropping `--tools default`.
- Severity: **Low**
- Mitigation: Read all subclass files before editing to confirm no current overrides. Blast radius limited since ARG-TOO-LONG's independent executors are confirmed out of scope.

**RISK-003** — Index-based test assertions in sprint/roadmap suites break after `--tools default` shifts flag positions.
- Severity: **Low**
- Mitigation: Phase 1.1 must land and test assertions updated before any combined test suite run in Phase 3.

**RISK-004** — `--file` fallback is broken, invalidating the fallback path relied upon by multiple executors.
- Severity: **High** (probability: ~80%)
- Mitigation: Phase 0 empirical test is a mandatory blocking gate. Phase 1.5 contingency activates to replace `--file` with inline embedding across all affected executors if broken.

**RISK-005** — 8 KB template overhead constant is too conservative, causing unnecessary fallback for 112–120 KB inputs.
- Severity: **Low**
- Mitigation: Full-string measurement (FR-009) is the real safety gate. Overhead is a pre-filter. Unnecessary fallback is functionally correct, just slightly slower.

**RISK-006** — Future prompt template growth exceeds 8 KB, narrowing the safe embed window without detection.
- Severity: **Medium**
- Mitigation: `_PROMPT_TEMPLATE_OVERHEAD` is a named constant with a comment noting the 2.3x safety factor. Easy to update if templates grow. The module-level assertion (FR-008) provides a runtime tripwire.

**RISK-007** — Windows 32 KB command-line limit affects cross-platform users after `--tools default` is added.
- Severity: **Medium** (probability: Low for current user base)
- Mitigation: Noted and deferred. Linux-first fix is correct priority. `--tools default` adds two short tokens — negligible effect on Windows limit.

**RISK-008** — Executors not inheriting `ClaudeProcess` lack `--tools default` after Phase 1.5 activates, allowing tool schema discovery failures to recur in those code paths.
- Severity: **Medium**
- Mitigation: Tracked as OQ-4. Scope assessment deferred until Phase 0 result is known; addressed in the same work cycle if Phase 1.5 activates.

---

## Dependency Inventory

**DEP-001** — `claude` CLI binary: must be installed, authenticated, and capable of completing a basic `--print` request before Phase 0 can execute. Verified with `claude --print -p "hello" --max-turns 1`.

**DEP-002** — `uv` package manager: required for all Python operations (`uv run pytest`, `uv run python`). No `pip` or direct `python` invocations permitted.

**DEP-003** — `src/superclaude/cli/pipeline/process.py` (`ClaudeProcess.build_command()`): the single shared method that both fixes interact with. FIX-001 modifies it directly; FIX-ARG-TOO-LONG depends on it for command assembly.

**DEP-004** — `src/superclaude/cli/roadmap/executor.py`: owns `_EMBED_SIZE_LIMIT`, `_embed_inputs()`, and `roadmap_run_step()`. The primary target file for FIX-ARG-TOO-LONG constant and guard logic changes.

**DEP-005** — Conditionally: `src/superclaude/cli/roadmap/remediate_executor.py`, `src/superclaude/cli/roadmap/validate_executor.py`, `src/superclaude/cli/tasklist/executor.py`. These files are in scope only if Phase 0 confirms `--file` is BROKEN.

**DEP-006** — Linux kernel `MAX_ARG_STRLEN` constant (128 KB): a compile-time kernel constant that defines the per-argument limit for `execve()`. Not queryable at runtime via `getrlimit()`. Must be encoded as a Python constant.

**DEP-007** — Reference documents in `docs/generated/`: `fix-tool-schema-discovery-tasklist.md`, `arg-too-long-tasklist.md`, `fix-tool-schema-discovery-spec.md`, `v2.24.5-arg-too-long-spec.md`, and associated debate/analysis documents. These provide step-by-step code snippets and are normative inputs for implementation.

---

## Success Criteria

**SC-001** — `"--tools" in cmd` is `True` and `cmd[cmd.index("--tools") + 1] == "default"` for every command list produced by `ClaudeProcess.build_command()`.

**SC-002** — All pre-existing flags (`--print`, `--verbose`, `--no-session-persistence`, `--max-turns`, `--output-format`, `-p`) remain present in the command list after the fix.

**SC-003** — `uv run pytest tests/pipeline/test_process.py -v` passes with 0 failures, including the new `test_tools_default_in_command` and the two updated existing tests.

**SC-004** — `_EMBED_SIZE_LIMIT` equals exactly `_MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD` = 122,880 bytes (120 KB). No hardcoded `200 * 1024` value remains. No stale `# 100 KB` comment remains.

**SC-005** — Module-level `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096` is present and fires on `import executor`.

**SC-006** — Guard evaluates `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT` where `composed = step.prompt + "\n\n" + embedded`. Fallback fires for inputs that fit individually but exceed the limit when combined with the prompt.

**SC-007** — When `len(composed.encode('utf-8')) == _EMBED_SIZE_LIMIT` exactly, inline embedding fires (not fallback), confirming `<=` is the correct operator.

**SC-008** — `test_embed_size_guard_fallback` (renamed from `test_100kb_guard_fallback`) passes. Class docstring references `_EMBED_SIZE_LIMIT`, not "100KB".

**SC-009** — `TestComposedStringGuard` tests pass: file at 90% of `_EMBED_SIZE_LIMIT` + large prompt triggers fallback; file content is absent from captured prompt; `--file` flags present in `extra_args`.

**SC-010** — Phase 0 empirical test is executed and result recorded as either WORKING or BROKEN before any code changes are committed.

**SC-011** — If Phase 0 result is BROKEN: `remediate_executor.py:177`, `executor.py` fallback, `validate_executor.py:109`, and `tasklist/executor.py:121` are all fixed to use inline embedding. Conditional tests `test_remediate_inline_embed_replaces_file_flag` and `test_inline_embed_fallback_when_file_broken` pass.

**SC-012** — `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` passes with 0 regressions.

**SC-013** — `superclaude sprint run ... --dry-run` CLI smoke test completes without error.

**SC-014** — Pipeline run with large spec file (≥120 KB) completes the `spec-fidelity` step without `OSError: [Errno 7] Argument list too long`.

---

## Open Questions

**OQ-1** — Does `claude --print --file /bare/path` deliver file content to the model? This is the Phase 0 blocking gate. Resolution: empirical test (15-minute task) before any code changes. Result determines whether Phase 1.5 activates.

**OQ-2** — Does `claude --print` accept prompt delivery from stdin? This would provide an alternative to both inline `-p` embedding and `--file` delivery for oversized inputs. Resolution target: v2.26 spike (deferred).

**OQ-3** — Has `remediate_executor.py:177`'s unconditional `--file` usage been producing incorrect (context-free) remediations in all prior runs where the input file exceeded the inline limit? If the `--file` path is BROKEN (per Phase 0), all prior remediation outputs for large files may be invalid. Resolution: Phase 0 result determines; Phase 1.5 fixes the forward path but does not retroactively address prior outputs.

**OQ-4** — If Phase 1.5 activates, do `remediate_executor.py`, `validate_executor.py`, and `tasklist/executor.py` also need `--tools default` added? These do not inherit from `ClaudeProcess` and build commands independently. Without `--tools default`, tool schema discovery failures could recur in these code paths even after FIX-001 is applied to `ClaudeProcess`. Resolution: assess immediately after Phase 0 result is known; address in same work cycle if Phase 1.5 activates.

**OQ-5** (implicit) — What is the correct `file_id:relative_path` format documented in `claude --help` for the `--file` flag? The spec references this as the potentially correct format vs. the bare path currently used. If Phase 0 confirms BROKEN, the fix strategy assumes inline embedding is the replacement — but if `--file` merely requires the `file_id:` prefix, a simpler format fix might suffice. Resolution: check `claude --help` output during Phase 0 validation before deciding on Phase 1.5 implementation strategy.

**OQ-6** (implicit) — Are there any subclasses of `ClaudeProcess` that override `build_command()` without calling `super()`? The spec states "none currently override" but requires verification by reading subclass files before editing. Resolution: code review of all `ClaudeProcess` subclasses before Phase 1.1.
