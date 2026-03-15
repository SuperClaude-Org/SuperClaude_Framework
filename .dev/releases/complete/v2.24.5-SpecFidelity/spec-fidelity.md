---
high_severity_count: 3
medium_severity_count: 8
low_severity_count: 3
total_deviations: 14
validation_complete: true
tasklist_ready: true
fixes_applied: true
fixes_workflow: claudedocs/workflow_spec-fidelity-fixes.md
---

## Deviation Report

---

### DEV-001
- **ID**: DEV-001
- **Severity**: HIGH
- **Deviation**: Spec requires `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096` immediately after the three constant definitions (FR-ATL.1). The roadmap's Task 1.2.2 adds this assertion but places it as a separate task step rather than specifying it must appear "immediately after the three constant definitions" and be triggered "on any `import executor` call." More critically, the roadmap marks this as OQ-4, implying open-question status, when the spec treats it as a hard requirement with no conditionality.
- **Spec Quote**: "A module-level `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096` is present immediately after the three constant definitions, with an error message stating the kernel margin rationale and the measured template peak (~3.4 KB). The assertion must be triggered on any `import executor` call and therefore on every test run."
- **Roadmap Quote**: "1.2.2 | Add module-level assertion | `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096, "..."` with kernel margin rationale and measured template peak (~3.4 KB) | OQ-4"
- **Impact**: The OQ-4 label in the roadmap's Phase 1.2 table is incorrect — OQ-4 in the spec refers to whether non-inheriting executors need `--tools default`, not to the assertion. This mislabeling may cause an implementer to treat the assertion as an open question to defer, rather than a mandatory FR-ATL.1 deliverable, risking omission.
- **Recommended Correction**: Remove the OQ-4 reference from Task 1.2.2. Specify that the assertion must appear immediately after the three constant definitions (not in a later position) and include the required error message text referencing the kernel margin rationale and ~3.4 KB measured peak.

---

### DEV-002
- **ID**: DEV-002
- **Severity**: HIGH
- **Deviation**: The spec's FR-ATL.1 explicitly requires a `_EMBED_SIZE_LIMIT` that "equals `_MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD` (120 KB)" and specifies "No `import resource` line (dead code from brainstorm draft)". The roadmap's Task 1.2.1 does not mention the prohibition on `import resource`. An implementer working only from the roadmap could inadvertently retain this dead import.
- **Spec Quote**: "No `import resource` line (dead code from brainstorm draft)"
- **Roadmap Quote**: "1.2.1 | Replace constants in `executor.py` | Remove `_EMBED_SIZE_LIMIT = 200 * 1024`. Add `_MAX_ARG_STRLEN = 128 * 1024`, `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024`, `_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD`. Each with inline derivation comment. Remove any stale `# 100 KB` comment. No `import resource`."
- **Impact**: On re-reading the roadmap text carefully, "No `import resource`" is present in Task 1.2.1. This deviation is MEDIUM upon close reading. **Re-classified below.**

> *Self-correction: DEV-002 is not HIGH — the text is present. Reclassified. See DEV-002 revised entry at end of report. Proceeding with re-numbered list.*

---

### DEV-002 (revised)
- **ID**: DEV-002
- **Severity**: MEDIUM
- **Deviation**: The spec FR-ATL.1 specifies that each of the three constants must carry specific inline comment content: `_MAX_ARG_STRLEN` notes it is a Linux kernel compile-time constant; `_PROMPT_TEMPLATE_OVERHEAD` notes the 2.3x safety factor and measured peak; `_EMBED_SIZE_LIMIT` notes its derivation and resulting byte value. The roadmap says only "Each with inline derivation comment" without specifying required content per constant.
- **Spec Quote**: "Each of the three constants carries an inline comment: `_MAX_ARG_STRLEN` notes it is a Linux kernel compile-time constant; `_PROMPT_TEMPLATE_OVERHEAD` notes the 2.3x safety factor and the measured peak; `_EMBED_SIZE_LIMIT` notes its derivation and resulting byte value."
- **Roadmap Quote**: "Add `_MAX_ARG_STRLEN = 128 * 1024`, `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024`, `_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD`. Each with inline derivation comment."
- **Impact**: An implementer may write generic comments that omit the 2.3x safety factor note or the kernel compile-time characterization, reducing the self-documenting intent of NFR-ATL.4 ("Zero magic numbers; every constant has derivation comment").
- **Recommended Correction**: Expand Task 1.2.1 to enumerate the required comment content for each constant individually, matching FR-ATL.1.

---

### DEV-003
- **ID**: DEV-003
- **Severity**: HIGH
- **Deviation**: The spec FR-ATL.2 requires that when `len(composed.encode('utf-8')) == _EMBED_SIZE_LIMIT` exactly (at-limit), inline embedding fires (not fallback), confirming `<=` is the intended operator, and that "Implementation includes a code comment adjacent to the guard explaining: `<= is intentional; _EMBED_SIZE_LIMIT = 120 KB is safely below MAX_ARG_STRLEN = 128 KB`". The roadmap adds a boundary test in Task 1.2.6, but does not specify the required code comment adjacent to the guard expression. This is a spec requirement (FR-ATL.2 acceptance criterion), not merely a test.
- **Spec Quote**: "Implementation includes a code comment adjacent to the guard explaining: `<= is intentional; _EMBED_SIZE_LIMIT = 120 KB is safely below MAX_ARG_STRLEN = 128 KB`"
- **Roadmap Quote**: "1.2.3 | Fix embed guard | Evaluate `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT` where `composed = step.prompt + "\n\n" + embedded`. Update warning log to report "composed prompt" and byte count. Add `<=` intentionality comment."
- **Impact**: The roadmap says "Add `<=` intentionality comment" but does not specify the required comment text. While partial, this is missing the verbatim content required by the spec acceptance criterion. An implementer may write a different comment that satisfies the spirit but not the letter, preventing traceability.
- **Recommended Correction**: Add the verbatim required comment text from FR-ATL.2 to Task 1.2.3.

---

### DEV-004
- **ID**: DEV-004
- **Severity**: MEDIUM
- **Deviation**: The spec's FR-ATL.3 requires the class docstring to be "updated to reference `_EMBED_SIZE_LIMIT` not '100KB'" and the test "logic unchanged (imports `_EMBED_SIZE_LIMIT`, auto-adapts to new value)." The roadmap's Task 1.2.4 renames the method and updates the docstring but does not explicitly state the test must import `_EMBED_SIZE_LIMIT` as a constant (i.e., auto-adapt) rather than hardcode a number.
- **Spec Quote**: "Test logic unchanged (imports `_EMBED_SIZE_LIMIT`, auto-adapts to new value)"
- **Roadmap Quote**: "1.2.4 | Rename test class | `test_100kb_guard_fallback` → `test_embed_size_guard_fallback`. Update docstring to reference `_EMBED_SIZE_LIMIT`. Import and use the constant."
- **Impact**: Minor — "Import and use the constant" is present but placed in a less prominent position than the spec's explicit acceptance criterion. Low risk of omission but insufficient for traceability.
- **Recommended Correction**: Acceptable as-is; consider making the import-and-use requirement a checklist item in Task 1.2.4.

---

### DEV-005
- **ID**: DEV-005
- **Severity**: MEDIUM
- **Deviation**: The spec FR-ATL.4 specifies that `TestComposedStringGuard` must assert that `--file` flags are present in `extra_args` when fallback fires. The roadmap Task 1.2.5 asserts "file content absent from prompt; `--file` in `extra_args`", which matches, but the spec also names the test `test_prompt_plus_embedded_exceeds_limit` (in Section 8.1 test table). The roadmap does not name this test, making traceability ambiguous.
- **Spec Quote**: "`test_prompt_plus_embedded_exceeds_limit` (new) | `tests/roadmap/test_file_passing.py` | FR-ATL.2, FR-ATL.4: Composed-string guard catches template+embedded overflow"
- **Roadmap Quote**: "1.2.5 | Add `TestComposedStringGuard` | File at 90% of `_EMBED_SIZE_LIMIT` + prompt large enough to exceed composed limit → fallback fires; file content absent from prompt; `--file` in `extra_args`"
- **Impact**: Test name is unspecified in the roadmap. A different name may break cross-reference with tasklists or CI test filtering by name.
- **Recommended Correction**: Specify the test method name `test_prompt_plus_embedded_exceeds_limit` in Task 1.2.5 to match Section 8.1 of the spec.

---

### DEV-006
- **ID**: DEV-006
- **Severity**: MEDIUM
- **Deviation**: The spec Section 4.6 Phase 1 ordering states "1.3 Rename test in test_file_passing.py — FR-ATL.3 [parallel with 1.2]" as a separate explicit step. The roadmap collapses this into Task 1.2.4 under Phase 1.2. The spec's parallelization note (`[parallel with 1.2]`) means this task can run concurrently with Phase 1.2, not that it is part of Phase 1.2.
- **Spec Quote**: "1.3 Rename test in test_file_passing.py -- FR-ATL.3 [parallel with 1.2]"
- **Roadmap Quote**: "1.2.4 | Rename test class | `test_100kb_guard_fallback` → `test_embed_size_guard_fallback`..."
- **Impact**: Merging the rename into Phase 1.2 is harmless functionally but obscures the parallelization opportunity identified by the spec. Teams would not know to split this work across engineers.
- **Recommended Correction**: Surface the rename as a parallel task (Phase 1.3) rather than embedding it in Phase 1.2's task list.

---

### DEV-007
- **ID**: DEV-007
- **Severity**: MEDIUM
- **Deviation**: The spec's Phase 0 specifies a CLI prerequisite verification step before the PINEAPPLE test: "CLI must be installed, authenticated, and able to complete a basic `--print` request. Verify with: `claude --print -p "hello" --max-turns 1`." The roadmap's Task 0.1 covers this, but the spec also defines a third named outcome: "CLI FAILURE: exit non-zero for any reason — Resolve CLI issue and re-run Task 0.1. Do not record WORKING or BROKEN until exit code is 0." The roadmap does not name or document this third outcome — it only documents WORKING and BROKEN.
- **Spec Quote**: "Three named outcomes (exit code 0 only): → WORKING... → BROKEN... → CLI FAILURE: exit non-zero for any reason. Resolve CLI issue and re-run Task 0.1. Do NOT record WORKING or BROKEN."
- **Roadmap Quote**: "0.4 | Record result | WORKING (response mentions PINEAPPLE) or BROKEN (does not) | —"
- **Impact**: Without the CLI FAILURE outcome documented, an implementer may record BROKEN from a failed subprocess (exit non-zero), incorrectly triggering Phase 1.5 when the real problem is CLI configuration.
- **Recommended Correction**: Add CLI FAILURE as a third named outcome in Task 0.4 with the prescribed resolution path.

---

### DEV-008
- **ID**: DEV-008
- **Severity**: HIGH
- **Deviation**: The spec lists a required acceptance criterion for FR-ATL.2: "When `len(composed.encode('utf-8')) == _EMBED_SIZE_LIMIT` exactly (at-limit), inline embedding fires (not fallback)." The roadmap adds Task 1.2.6 ("Add exact-limit boundary test") which validates this behavior as a test. However, the spec places this as a FR-ATL.2 acceptance criterion (implementation requirement), not just a test requirement. The distinction matters: the guard logic must be implemented with `<=` (not `<`) as a verified design decision, and the roadmap does not make this explicit in the implementation task (1.2.3).
- **Spec Quote**: "When `len(composed.encode('utf-8')) == _EMBED_SIZE_LIMIT` exactly (at-limit), inline embedding fires (not fallback) — confirming `<=` is the intended operator" [as an FR-ATL.2 acceptance criterion]
- **Roadmap Quote**: "1.2.6 | Add exact-limit boundary test | Verify composed length exactly equal to `_EMBED_SIZE_LIMIT` still embeds inline (boundary inclusion — `<=` is intentional)"
- **Impact**: The boundary semantics (`<=` vs `<`) are captured only in the test, not reinforced in Task 1.2.3's implementation description. A reviewer of 1.2.3 in isolation would not see the operator requirement.
- **Recommended Correction**: Add to Task 1.2.3: "Use `<=` operator — boundary semantics require at-limit inputs to embed inline."

---

### DEV-009
- **ID**: DEV-009
- **Severity**: MEDIUM
- **Deviation**: The spec Section 8.1 defines two conditional Phase 1.5 tests with specific names and parameterization: `test_remediate_inline_embed_replaces_file_flag` and `test_inline_embed_fallback_when_file_broken` (parameterized over each executor's `_EMBED_SIZE_LIMIT`). The roadmap Task 1.5.6 names both tests but does not specify the parameterization requirement ("parameterized over each executor's `_EMBED_SIZE_LIMIT` value").
- **Spec Quote**: "`test_inline_embed_fallback_when_file_broken` (new, parameterized) | FR-ATL.5: all three conditional executors route oversized inputs via inline embedding; parameterized over each executor's `_EMBED_SIZE_LIMIT` value"
- **Roadmap Quote**: "1.5.6 | Add conditional tests | `test_remediate_inline_embed_replaces_file_flag`, `test_inline_embed_fallback_when_file_broken`"
- **Impact**: Without the parameterization requirement, the test may be written as three separate non-parameterized tests, which would pass CI but obscure which executor is failing if one of the three breaks.
- **Recommended Correction**: Add "parameterized over each of the three affected executors" to Task 1.5.6.

---

### DEV-010
- **ID**: DEV-010
- **Severity**: LOW
- **Deviation**: The spec (Section 4.2, Modified Files table) specifies `tests/roadmap/test_file_passing.py (new class)` for FR-ATL.4. The roadmap describes this as adding `TestComposedStringGuard` in Task 1.2.5. The class name is not mentioned in the spec's Section 8.1 test table (the test method is named `test_prompt_plus_embedded_exceeds_limit`). The roadmap uses the class name but not the method name; the spec uses the method name but not the class name. Minor naming gap.
- **Spec Quote**: "Add `TestComposedStringGuard` to test_file_passing.py — FR-ATL.4" [Section 4.2] vs "`test_prompt_plus_embedded_exceeds_limit` (new)" [Section 8.1]
- **Roadmap Quote**: "1.2.5 | Add `TestComposedStringGuard`..."
- **Impact**: Negligible — both the class and method will exist. Traceability between Section 4.2 and Section 8.1 of the spec is slightly ambiguous, but the roadmap correctly captures the class.
- **Recommended Correction**: Specify both class name (`TestComposedStringGuard`) and method name (`test_prompt_plus_embedded_exceeds_limit`) in Task 1.2.5.

---

### DEV-011
- **ID**: DEV-011
- **Severity**: MEDIUM
- **Deviation**: The spec Section 4.6 names Task 3.4 as "`superclaude sprint run ... --dry-run` — CLI smoke test" and Task 3.5 as "Pipeline run with large spec file — E2E validation." These appear in the roadmap as Phase 2 Tasks 2.2 and 2.3. The roadmap renumbers and reorders the final integration steps into a different phase structure (the spec calls them Phase 3, the roadmap calls them Phase 2 integration). While the tasks themselves are preserved, the version confirmation step (spec Task 3.5 "Resolve version number") is present in the roadmap as Phase 3 Task 3.5 but the spec Task 3.4 (`--dry-run`) maps to roadmap Phase 2 Task 2.2 — causing phase numbering misalignment that could confuse cross-reference between the spec and roadmap.
- **Spec Quote**: "Phase 3 — Full validation (depends on all above): 3.1 uv run pytest tests/pipeline/ -v... 3.4 superclaude sprint run ... --dry-run -- CLI smoke test. 3.5 Pipeline run with large spec file -- E2E validation."
- **Roadmap Quote**: "Phase 2: Integration Verification... 2.2 | CLI smoke test | `superclaude sprint run ... --dry-run` completes without error... 2.3 | Large file E2E test | Pipeline run with ≥120 KB spec file completes `spec-fidelity` step without `OSError`"
- **Impact**: Low functional impact — all tasks are present. Phase numbering mismatch could cause confusion when cross-referencing spec and roadmap during implementation reviews.
- **Recommended Correction**: Align phase numbering or add a cross-reference note in the roadmap that spec Phase 3 validation tasks appear in roadmap Phase 2.

---

### DEV-012
- **ID**: DEV-012
- **Severity**: MEDIUM
- **Deviation**: The spec Section 8.2 Integration Tests includes a conditional integration test command: `uv run pytest tests/roadmap/test_remediate_executor.py tests/roadmap/test_inline_fallback.py -v` (conditional on Phase 1.5 activation). The roadmap Phase 2 Task 2.1 runs `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` which covers this implicitly, but does not explicitly call out the conditional integration test command from Section 8.2.
- **Spec Quote**: "`uv run pytest tests/roadmap/test_remediate_executor.py tests/roadmap/test_inline_fallback.py -v` (conditional on Phase 1.5 activation) | Validates all Phase 1.5 inline embedding paths; conditional on Phase 0 BROKEN result"
- **Roadmap Quote**: "2.1 | Combined test run | `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` — 0 failures"
- **Impact**: The roadmap's broad `tests/roadmap/` sweep covers the files implicitly, but the conditional nature of this specific test command (only required if Phase 0 = BROKEN) is not called out. An implementer may not realize these files only exist in the Phase 1.5 branch.
- **Recommended Correction**: Add a conditional note to Phase 2 Task 2.1 stating the Phase 1.5 specific test files are part of the roadmap suite only if Phase 1.5 activated.

---

### DEV-013
- **ID**: DEV-013
- **Severity**: LOW
- **Deviation**: The roadmap introduces an OQ-5 ("Check `claude --help` for `--file` format — Record whether `file_id:path` prefix is required") in Phase 0 Task 0.2. This open question does not appear in the spec's Section 11 Open Items. The spec's open items are OQ-1 through OQ-4.
- **Spec Quote**: [Section 11 Open Items table — no OQ-5 listed]
- **Roadmap Quote**: "0.2 | Check `claude --help` for `--file` format | Record whether `file_id:path` prefix is required | OQ-5"
- **Impact**: The roadmap adds a discovery task not in the spec. This is additive and beneficial (the spec's Appendix B references `arg-too-long-file-fallback-validation.md` which mentions `file_id:relative_path` format), but introduces an undocumented OQ that could expand scope if acted upon.
- **Recommended Correction**: Either acknowledge OQ-5 as a roadmap addition beyond the spec (note it as such), or fold it into OQ-1 since both concern `--file` behavior.

---

### DEV-014
- **ID**: DEV-014
- **Severity**: LOW
- **Deviation**: The roadmap introduces an OQ-6 ("Verify no subclass overrides — Read all `ClaudeProcess` subclasses; confirm none override `build_command()` without `super()`") in Phase 1.1 Task 1.1.1. The spec's Risk Assessment (Section 7) mentions this as a risk mitigation strategy but does not define it as an open question (OQ-2 in the spec refers to stdin, OQ-3 to remediate_executor, OQ-4 to non-inheriting executors and `--tools default`). OQ-6 is not in the spec's open items.
- **Spec Quote**: "Read subclass files before editing to confirm inheritance chain; none currently override." [Section 7, Risk row for RISK-002]
- **Roadmap Quote**: "1.1.1 | Verify no subclass overrides | Read all `ClaudeProcess` subclasses; confirm none override `build_command()` without `super()` | OQ-6"
- **Impact**: The roadmap elevates a risk mitigation note into a numbered task with an OQ label. Functionally correct and conservative, but introduces numbering not in the spec's open items table.
- **Recommended Correction**: Remove OQ-6 label (or note it as a roadmap-added verification step). The task itself is appropriate.

---

## Summary

**Severity Distribution**:
- HIGH: 3 (DEV-001, DEV-003, DEV-008)
- MEDIUM: 8 (DEV-002, DEV-004, DEV-005, DEV-006, DEV-007, DEV-009, DEV-011, DEV-012)
- LOW: 3 (DEV-010, DEV-013, DEV-014)

**Key Findings**:

The roadmap is structurally sound and covers all major functional requirements. The three HIGH severity deviations share a common pattern: the roadmap captures the *what* but omits or mislabels critical *constraints* from the spec's acceptance criteria:

1. **DEV-001**: The module-level assertion is mislabeled OQ-4 (an unrelated open question), risking deferral of a mandatory deliverable.
2. **DEV-003**: The required verbatim code comment for the `<=` operator is reduced to "Add `<=` intentionality comment" without the mandated text.
3. **DEV-008**: The boundary semantics (`<=` vs `<`) are captured only in the test task, not in the implementation task where the operator must be chosen.

The MEDIUM deviations are primarily specification detail gaps: missing per-constant comment content specifications, absent test method names, undocumented Phase 0 third outcome (CLI FAILURE), missing parameterization requirement for Phase 1.5 tests, and phase numbering misalignment. The LOW deviations are all additive — the roadmap introduces OQ-5 and OQ-6 not in the spec.

**Tasklist readiness**: Not ready (`tasklist_ready: false`) due to 3 HIGH severity deviations. Resolve DEV-001, DEV-003, and DEV-008 before proceeding to tasklist generation.
