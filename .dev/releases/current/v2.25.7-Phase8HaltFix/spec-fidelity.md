---
high_severity_count: 4
medium_severity_count: 6
low_severity_count: 3
total_deviations: 13
validation_complete: true
tasklist_ready: false
---
```

## Deviation Report

---

### DEV-001

- **ID**: DEV-001
- **Severity**: HIGH
- **Deviation**: The roadmap maps `build_prompt()` changes to `src/superclaude/cli/sprint/prompt.py` instead of `src/superclaude/cli/sprint/process.py` as specified.
- **Spec Quote**: "S3-R05, S3-R06, S3-R07 | `src/superclaude/cli/sprint/process.py` | Modify — add `## Sprint Context` header to `build_prompt()`, add `env_vars` to `ClaudeProcess.__init__()`"
- **Roadmap Quote**: "| `src/superclaude/cli/sprint/prompt.py` | `## Sprint Context` header in `build_prompt()` | 3 |"
- **Impact**: If `build_prompt()` lives in `process.py` (per spec), implementing it in `prompt.py` will target the wrong file. Conversely, if the roadmap reflects actual repo structure, the spec's file path is wrong. Either way, one document is incorrect and the implementer will modify the wrong file.
- **Recommended Correction**: Verify the actual location of `build_prompt()` in the codebase and align both documents. If it lives in `process.py`, correct the roadmap's resource table. If it lives in `prompt.py`, correct the spec's §7 table.

---

### DEV-002

- **ID**: DEV-002
- **Severity**: HIGH
- **Deviation**: The roadmap maps `SprintLogger.write_phase_result()` changes to `src/superclaude/cli/sprint/logger.py` instead of `src/superclaude/cli/sprint/logging_.py` as specified.
- **Spec Quote**: "| `src/superclaude/cli/sprint/logging_.py` | FIX-1-R01 | Modify — add `PASS_RECOVERED` to screen INFO routing |"
- **Roadmap Quote**: "| `src/superclaude/cli/sprint/logger.py` | `PASS_RECOVERED` routing to INFO branch | 4 |"
- **Impact**: The implementer will edit `logger.py` while the actual module is `logging_.py` (or vice versa), resulting in the fix being applied to the wrong file or causing a `ModuleNotFoundError` if the file doesn't exist.
- **Recommended Correction**: Verify the actual filename in the repository. Align both documents to the correct filename (`logging_.py` per spec, or `logger.py` per roadmap).

---

### DEV-003

- **ID**: DEV-003
- **Severity**: HIGH
- **Deviation**: The roadmap adds a tenth test T04.10 not present in the spec, and correspondingly raises the expected passing test count from 638 to different values throughout (spec says 9 new tests and ≥629+9=638 total; roadmap says 10 tests and "≥638 passed").
- **Spec Quote**: "All new tests go in `tests/sprint/test_phase8_halt_fix.py` (extending the existing 12-test file). ... T04.01–T04.09" and "DoD-1 | All 9 new tests pass (T04.01–T04.09)"
- **Roadmap Quote**: "T04.10 (named, explicit — adopted from Variant A): `_determine_phase_status()` passes `error_file` through to `detect_prompt_too_long()` — covers FR-010–FR-012 which otherwise lack dedicated test coverage" and "`uv run pytest tests/sprint/test_phase8_halt_fix.py -v` — 10 tests pass"
- **Impact**: The DoD commands in the spec (`uv run pytest tests/sprint/test_phase8_halt_fix.py -v`) expect 9 tests. A verification run against the spec's DoD-1 would pass with 9 tests but the roadmap requires 10. The gap in test coverage (FR-010–FR-012) identified in the roadmap is real, but adding T04.10 silently contradicts the spec's acceptance criteria.
- **Recommended Correction**: Either update the spec to include T04.10 with explicit acceptance criteria and adjust DoD-1 to "10 new tests", or remove T04.10 from the roadmap and add a separate deviation note explaining the coverage gap for FR-010–FR-012.

---

### DEV-004

- **ID**: DEV-004
- **Severity**: HIGH
- **Deviation**: The roadmap introduces an "OQ-006 Verification Gate" as a blocking Phase 1 prerequisite that can cause a timeline re-estimate and delay Phase 2, but the spec contains no such open question, gate, or contingency mechanism.
- **Spec Quote**: "S3-R02 | Pass the per-phase isolation directory as `scoped_work_dir` to `ClaudeProcess` so the subprocess cannot resolve `tasklist-index.md` or other phase files via `@`" — the mechanism is specified directly without any open question.
- **Roadmap Quote**: "OQ-006 — whether `CLAUDE_WORK_DIR` env var or subprocess `cwd` controls `@` resolution scope — must be answered before Phase 2 isolation code is written. If OQ-006 reveals `cwd` is the correct lever, Phase 2 implementation changes significantly and the timeline must be re-estimated before coding begins."
- **Impact**: The spec designates `scoped_work_dir` as the parameter for passing the isolation directory; the roadmap treats the actual isolation mechanism as unresolved. An implementer following the roadmap will pause Phase 2 for discovery work the spec treats as already resolved. If OQ-006 resolves differently from the spec's implicit assumption, FR-001/FR-002/S3-R02 will be implemented differently than specified.
- **Recommended Correction**: Resolve OQ-006 and encode the answer in the roadmap's implementation steps as a concrete decision (not a gate). If the mechanism differs from `scoped_work_dir`, update the spec's S3-R02 accordingly before roadmap finalization.

---

### DEV-005

- **ID**: DEV-005
- **Severity**: MEDIUM
- **Deviation**: The roadmap references functional requirements using an "FR-NNN" numbering scheme (FR-001 through FR-022) that does not exist in the spec. The spec uses requirement IDs like S3-R01, S2-R08, FIX-1-R01, etc.
- **Spec Quote**: "| S3-R01, S3-R02, S3-R03 | T01.01, T01.02, T01.03 | §3 S3-A |" (Appendix traceability table uses spec IDs throughout)
- **Roadmap Quote**: "**Requirements**: FR-001, FR-002, FR-003, FR-006" and "| FR-001–FR-003 | `executor.py` | Isolation create/copy/gate | 2 |"
- **Impact**: The requirement-to-phase mapping table in the roadmap uses FR-NNN IDs that cannot be traced back to spec requirements without guessing. Reviewers and implementers cannot verify roadmap coverage against the spec. Some FR-NNN IDs may inadvertently collapse or omit spec requirements.
- **Recommended Correction**: Replace all FR-NNN IDs in the roadmap with the spec's native IDs (S3-R01, S2-R08, FIX-1-R01, etc.), or add an explicit FR-NNN → spec-ID mapping table.

---

### DEV-006

- **ID**: DEV-006
- **Severity**: MEDIUM
- **Deviation**: The roadmap adds `DiagnosticBundle.config=None` deprecation warning behavior (FIX-2 extension) that is not present in the spec.
- **Spec Quote**: "FIX-2-R02 | If `bundle` does not carry a `config` reference, add `config: SprintConfig` as a field to `DiagnosticBundle` (or pass it as a parameter to `classify()`) with a `None` default for backward compatibility"
- **Roadmap Quote**: "If `config is None`: use existing hardcoded path as fallback **and** log a deprecation warning (adopted from Variant A — adds long-term migration value at zero cost)"
- **Impact**: The spec requires backward-compatible `None` default but does not require a deprecation warning. Adding an unsolicited warning may affect log output, test assertions, and operator experience in ways not covered by the spec's test requirements (T04.09 only validates path resolution, not warning emission).
- **Recommended Correction**: Either remove the deprecation warning from the roadmap (stay within spec scope), or add a new spec requirement FIX-2-R03 covering the deprecation warning with an associated acceptance criterion.

---

### DEV-007

- **ID**: DEV-007
- **Severity**: MEDIUM
- **Deviation**: The roadmap's SC-001 expects 10 tests to pass while the spec's DoD-1 expects 9 tests to pass.
- **Spec Quote**: "DoD-1 | All 9 new tests pass (T04.01–T04.09) | `uv run pytest tests/sprint/test_phase8_halt_fix.py -v`"
- **Roadmap Quote**: "**SC-001**: 10 new tests pass | `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` | 10 passed, exit 0"
- **Impact**: This is a direct consequence of DEV-003 (T04.10 addition). The DoD verification command will produce different pass counts depending on which document is followed, creating a discrepancy in the definition of "done."
- **Recommended Correction**: Align with resolution of DEV-003. If T04.10 is added to the spec, update DoD-1 to "10 new tests."

---

### DEV-008

- **ID**: DEV-008
- **Severity**: MEDIUM
- **Deviation**: The roadmap's SC-002 expects ≥638 total tests while the spec's DoD-2 expects ≥629 baseline tests (629 pre-existing + 9 new = 638, but the spec states "≥629 tests" for pre-existing, not 638 total).
- **Spec Quote**: "DoD-2 | All pre-existing sprint tests pass (≥629 tests, zero regressions) | `uv run pytest tests/ -v --tb=short`" and "NF-01 | All pre-existing tests must continue to pass (≥629 tests)."
- **Roadmap Quote**: "`uv run pytest tests/ -v --tb=short` — ≥638 passed (629 baseline + 10 new), exit 0"
- **Impact**: The spec's DoD-2 says ≥629 (focusing on regression protection of existing tests), while the roadmap correctly computes 629+10=639 but says ≥638. The arithmetic is inconsistent (629+10=639, not 638), and the spec's DoD-2 focuses only on pre-existing test preservation rather than stating a combined total. Minor but could cause confusion in CI gate thresholds.
- **Recommended Correction**: Clarify DoD-2 to state the expected combined total explicitly: "≥638 total tests pass (629 pre-existing + 9 new)." Correct the roadmap's arithmetic if T04.10 is added (629+10=639).

---

### DEV-009

- **ID**: DEV-009
- **Severity**: MEDIUM
- **Deviation**: The roadmap's test class names differ from the spec's test class names.
- **Spec Quote**: "Class: `TestIsolationLifecycle` (S3-A, S3-C)" and "Class: `TestPromptAndDetection` (S3-D, S2-D)" and "Class: `TestFixesAndDiagnostics` (FIX-1, FIX-2, S2-E)"
- **Roadmap Quote**: "**`TestIsolationWiring`** (T04.01–T04.04)" and "**`TestPromptAndContext`** (T04.05–T04.07)" and "**`TestFixesAndDiagnostics`** (T04.08–T04.10)"
- **Impact**: `TestIsolationLifecycle` vs `TestIsolationWiring` and `TestPromptAndDetection` vs `TestPromptAndContext` are different class names. If any test runner configuration, CI filter, or documentation references the spec's class names, the tests will not be found. Only `TestFixesAndDiagnostics` matches.
- **Recommended Correction**: Align roadmap test class names to match the spec exactly: `TestIsolationLifecycle`, `TestPromptAndDetection`, `TestFixesAndDiagnostics`.

---

### DEV-010

- **ID**: DEV-010
- **Severity**: MEDIUM
- **Deviation**: The roadmap's Phase 5 creates `tests/sprint/test_phase8_halt_fix.py` as a new file, while the spec states it extends an existing 12-test file.
- **Spec Quote**: "All new tests go in `tests/sprint/test_phase8_halt_fix.py` (extending the existing 12-test file)."
- **Roadmap Quote**: "Create `tests/sprint/test_phase8_halt_fix.py` with three test classes"
- **Impact**: If the file already exists with 12 tests, "creating" it would overwrite and lose those 12 tests rather than extending them. The baseline test count (629) likely includes those 12 existing tests; losing them would cause regressions.
- **Recommended Correction**: Change "Create" to "Extend" in the roadmap's Phase 5 instructions and note the 12 pre-existing test cases that must be preserved.

---

### DEV-011

- **ID**: DEV-011
- **Severity**: LOW
- **Deviation**: The roadmap uses "FR-007, FR-008, FR-009, FR-010, FR-011, FR-012" as requirement labels for Phase 3 but the spec labels these as S3-R05, S3-R06, S2-R08, S2-R08b, S2-R08c, S2-R08d respectively.
- **Spec Quote**: "S3-R05 | Add a `## Sprint Context` section to `build_prompt()`..." and "S2-R08 | Add keyword-only parameter `error_path: Path | None = None` to `detect_prompt_too_long()`..."
- **Roadmap Quote**: "**Requirements**: FR-007, FR-008, FR-009, FR-010, FR-011, FR-012"
- **Impact**: Traceability gap. This is the FR-NNN aliasing issue from DEV-005 applied specifically to Phase 3. Cross-referencing the spec against the roadmap requires guessing the FR→spec-ID mapping.
- **Recommended Correction**: Use spec-native IDs in all phase requirement references.

---

### DEV-012

- **ID**: DEV-012
- **Severity**: LOW
- **Deviation**: The roadmap's total timeline estimate is stated as "4.25–4.5 days" while the per-phase sum (0.75+1.0+0.5+0.5+1.0+0.5) equals 4.25 days. The spec provides no timeline estimates.
- **Spec Quote**: [No timeline specified in spec]
- **Roadmap Quote**: "**Timeline**: 4.5 working days, contingent on OQ-006 resolution" (Executive Summary) vs. "**Total** | | **4.25–4.5 days**" (Timeline table)
- **Impact**: Minor inconsistency within the roadmap itself. Does not affect spec compliance directly but creates ambiguity for planning.
- **Recommended Correction**: Reconcile the executive summary and timeline table to use a single consistent estimate.

---

### DEV-013

- **ID**: DEV-013
- **Severity**: LOW
- **Deviation**: The roadmap's resource table lists 8 files total (7 modified + 1 new test file) while the spec's §7 lists exactly 7 files to modify (the test file is listed as "Modify" of an existing file, not a new file).
- **Spec Quote**: "| `tests/sprint/test_phase8_halt_fix.py` | T04.01–T04.09 | Modify — add 9 new test cases in 3 test classes |"
- **Roadmap Quote**: "### New Files (1) | `tests/sprint/test_phase8_halt_fix.py` | 10 test cases covering all Phase 8 requirements | 5 |"
- **Impact**: Low organizational impact, but the roadmap's classification of the test file as "new" contradicts the spec's "Modify" classification and masks the pre-existing 12-test content (reinforcing DEV-010).
- **Recommended Correction**: Move `tests/sprint/test_phase8_halt_fix.py` from the "New Files" table to the "Files Modified" table, consistent with the spec's §7 classification.

---

## Summary

**13 total deviations** across 3 severity levels:

| Severity | Count | Key Issues |
|----------|-------|------------|
| HIGH | 4 | Two conflicting file paths for modified modules (`process.py` vs `prompt.py`; `logging_.py` vs `logger.py`); unresolved OQ-006 mechanism gate contradicting spec's specified `scoped_work_dir` approach; extra test T04.10 added without spec authorization |
| MEDIUM | 6 | FR-NNN aliasing obscures spec traceability throughout; deprecation warning added beyond spec scope; test count arithmetic inconsistencies in DoD and SC-001/SC-002; test class name mismatches; "create" vs "extend" for existing test file |
| LOW | 3 | Phase 3 FR-NNN aliases (subset of the medium issue); internal timeline inconsistency within the roadmap; test file misclassified as new vs. modified |

**Blocking issues**: DEV-001 and DEV-002 (file path conflicts) must be resolved by verifying the actual module filenames in the repository before any implementation begins. DEV-004 (OQ-006 gate) should be resolved against the spec's intended `scoped_work_dir` mechanism or the spec updated to reflect the open question. DEV-003 (T04.10 addition) requires a decision on whether to update the spec or remove T04.10.
