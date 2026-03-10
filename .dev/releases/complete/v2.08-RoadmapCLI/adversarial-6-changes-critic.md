# Adversarial Critic Brief: 6 Proposed v2.08 Spec Changes

**Role**: CRITIC (arguing against adoption or for scope reduction)
**Date**: 2026-03-05
**Evidence base**: merged-spec.md, roadmap.md, executor.py, models.py, process.py, monitor.py, debug_logger.py, diagnostics.py

---

## CHANGE-4: Add missing modules to Section 3.1 module listing

**Position**: REDUCE
**Strength of counter-case**: 6/10

**Arguments AGAINST**:

1. **Section 3.1 is an architectural diagram, not an inventory manifest.** Its purpose is to show the *extraction boundary* between pipeline/, sprint/, and roadmap/. The key annotations are "extracted from sprint/process.py", "re-exports ClaudeProcess", "unchanged external API" -- they communicate *what moves where*. `debug_logger.py` and `diagnostics.py` do not move anywhere. Listing them with "(stays in sprint/)" adds noise to a diagram whose entire information architecture is about *what changes*.

2. **Implementers will discover these files immediately.** `executor.py` imports both modules at lines 11-12: `from .debug_logger import debug_log, setup_debug_logger` and `from .diagnostics import DiagnosticCollector, FailureClassifier, ReportGenerator`. Any implementer working on the executor extraction will see these imports within the first 15 lines of the file. There is zero risk of someone missing them.

3. **Precedent problem.** If we list every sprint file that "stays in sprint/", we should also list `__init__.py` explicitly, and potentially any future files. The current listing is intentionally selective -- it shows files that *change role* (re-export, extend, wrap). Adding files that do not change role breaks this convention and invites further inventory-style additions.

**Acknowledged strengths of the proposal**:
1. The current listing of 10 files could be misread as exhaustive by someone who has never looked at the actual sprint directory, leading to confusion when they encounter files not in the list.
2. `diagnostics.py` (253 lines) and `debug_logger.py` (138 lines) are non-trivial modules that the extraction must be aware of.

**Risk if adopted unnecessarily**:
- Section 3.1 grows from a focused extraction diagram into a full directory listing, diluting its purpose. Future additions to sprint/ would need to be reflected here to maintain the "complete listing" expectation, creating a maintenance burden.

**Counter-proposal**:
- Add a single line comment below the sprint/ block: `# Also: debug_logger.py, diagnostics.py (sprint-only, not extracted)`. This acknowledges their existence without giving them the visual weight of annotated entries, and clearly communicates they are not part of the extraction.

---

## CHANGE-5: Add computed property chain verification to M2 acceptance criteria

**Position**: REJECT
**Strength of counter-case**: 8/10

**Arguments AGAINST**:

1. **Premature specificity that over-constrains the implementation.** The proposal names exactly 7 computed properties (`debug_log_path`, `results_dir`, `execution_log_jsonl`, `execution_log_md`, `output_file`, `error_file`, `result_file`) and mandates they "resolve correctly through the release_dir->work_dir property alias chain." But the spec has already decided the design (D2.1: "`release_dir` property aliases `work_dir`"). If the alias works, all properties that use `release_dir` or `self.results_dir` (which derives from `release_dir`) work automatically. Testing 7 individual properties is testing Python's `@property` decorator, not testing your extraction logic.

2. **The existing D2.4 acceptance criterion already catches this.** D2.4 states: "uv run pytest tests/sprint/ exits 0 with all sprint test files passing." If any computed property chain breaks, existing tests that use `config.results_dir`, `config.output_file()`, etc. will fail. The current sprint test suite exercises these paths. If it does not, that is a gap in the *test suite*, not a gap in the *spec*.

3. **This is an implementation detail disguised as an acceptance criterion.** Acceptance criteria should describe *observable behavior*, not *internal property resolution mechanics*. "Sprint CLI behavior is identical before and after migration" is the real criterion. D2.4 already captures this.

4. **Maintenance cost.** If any property is renamed, added, or removed, this acceptance criterion text becomes stale. It hardcodes the current count (7) and current names of internal properties into the roadmap document.

**Acknowledged strengths of the proposal**:
1. The `release_dir -> work_dir` alias is a genuine risk point in the extraction. If someone introduces `PipelineConfig` with `work_dir` and `SprintConfig.release_dir` does not properly alias it, 7 downstream properties break silently.
2. Making this risk explicit could help a less experienced implementer.

**Risk if adopted unnecessarily**:
- Sets a precedent of listing internal property names in roadmap acceptance criteria. Future specs would need similar granular property enumerations for any refactoring milestone, inflating roadmap documents with implementation details.

---

## CHANGE-6: Update executor line count and sprint_run_step complexity in Section 13.5

**Position**: REDUCE
**Strength of counter-case**: 7/10

**Arguments AGAINST**:

1. **Line counts in specs are inherently fragile.** The current spec says "~100 lines." The proposal says "~180 lines." The actual file is 353 lines total. The `execute_sprint` function itself runs from line 32 to line 304 (272 lines including the finally block). The poll loop proper (lines 99-171) is ~72 lines. None of these numbers match either the current spec or the proposal. Putting any specific line count in the spec is a losing game -- it will be wrong by the time someone reads it.

2. **The four preservation requirements (a-d) are discoverable by reading executor.py.** The proposal wants to mandate that `sprint_run_step` must preserve: (a) debug_logger calls, (b) DiagnosticCollector/FailureClassifier/ReportGenerator, (c) TUI error resilience wrapping, (d) stall watchdog. All four are visible in the first read of `executor.py`. An implementer who is refactoring this function will necessarily read it line by line. These are not hidden or subtle behaviors.

3. **Over-constraining the extraction approach.** Section 13.5 describes the *pattern* (composition via callable injection) and the *rationale* (sprint's orchestration is too coupled for hooks). Adding a checklist of 4 specific behaviors that must survive the extraction shifts the section from "design decision documentation" to "implementation checklist." Those belong in the tasklist, not the spec.

4. **Some of these items may not survive the extraction as described.** For example, the stall watchdog (d) depends on `monitor.state.stall_seconds`, which depends on `MonitorState.last_event_time`, which depends on NDJSON parsing. If the extraction separates the poll loop from the monitor, the watchdog's integration point may change form. Specifying "stall watchdog with kill capability" in the spec implies a specific implementation that the extraction might legitimately restructure.

**Acknowledged strengths of the proposal**:
1. The line count being off by 80% is genuinely misleading. "~100 lines" suggests a simple function; the reality is much more complex.
2. The four named behaviors are the most likely regression points during extraction. Making them explicit reduces the chance of an implementer accidentally dropping one.

**Risk if adopted unnecessarily**:
- Section 13.5 becomes an implementation checklist rather than a design rationale section. Line counts go stale immediately.

**Counter-proposal**:
- Replace "~100 lines" with "~150 lines" (round number, closer to the poll-loop-plus-diagnostics reality without pretending precision). Do NOT add the (a)-(d) checklist to the spec. Instead, note: "sprint_run_step must preserve all existing executor behavior; see executor.py for the full orchestration surface." This defers to the code as the source of truth.

---

## CHANGE-7: Add debug_log() removal note to migration strategy

**Position**: ACCEPT RELUCTANTLY
**Strength of counter-case**: 4/10

**Arguments AGAINST**:

1. **This is an implementation decision, not a strategy note.** The migration strategy (Section 12) describes the *sequence of operations* (create pipeline/models.py, move ClaudeProcess, create executor, etc.). Inserting a note about how to handle `debug_log()` calls in a specific file (`process.py`) is mixing granularity levels. The strategy is at the "create module, move class, re-export" level; this note is at the "handle 6 specific function calls in one file" level.

2. **The NFR-07 reference is self-evident.** NFR-07 says pipeline/ must not import from sprint/. If `ClaudeProcess` moves to `pipeline/process.py` and still calls `from .debug_logger import debug_log`, that is a sprint/ import. Any competent implementer will hit this as a compile-time error the moment they try to import `pipeline.process` without sprint dependencies. This is not a subtle risk.

3. **The proposed solution text is prescriptive about an implementation choice.** "sprint adds debug logging via wrapper or accepts process-level logging as sprint-only from sprint/executor.py" -- this describes two possible approaches. The spec should not enumerate implementation alternatives for trivial decisions. The implementer will see the import error and solve it.

**Acknowledged strengths of the proposal**:
1. `process.py` has 6 `debug_log()` calls (lines 139, 146, 181, 196, 202, plus the import at line 11). This is the single densest sprint-specific coupling in the file being extracted. Failing to note it means the implementer discovers it only at extraction time, which is fine for a solo developer but potentially confusing in a tasklist-driven sprint.
2. The note correctly identifies a real NFR-07 violation that MUST be resolved.

**Risk if adopted unnecessarily**:
- Minor spec bloat. The migration strategy section grows with per-file implementation notes that are better captured in tasklist task descriptions.

---

## CHANGE-8: Add monitor coupling annotation

**Position**: REJECT
**Strength of counter-case**: 8/10

**Arguments AGAINST**:

1. **The information is already captured.** Section 3.1 lists `monitor.py` as "unchanged" in sprint/. The module's docstring (line 1-6 of monitor.py) explicitly states: "Parses stream-json (NDJSON) output from `claude --print --output-format stream-json`." The annotation would duplicate information that lives in the code.

2. **"roadmap v1 does not use monitoring" is obvious from the spec.** The roadmap pipeline has no monitor, no TUI, no stall detection -- none of the sprint-specific orchestration. The entire spec design makes this clear. Adding "roadmap v1 does not use monitoring" to a module listing is stating the obvious for documentation completeness, not for implementer guidance.

3. **This is YAGNI documentation.** The proposed annotation describes *why* monitor.py cannot be extracted. But nobody proposed extracting it. It stays in sprint/, marked "unchanged." Explaining why a file that is not moving is not moving is defensive documentation that adds bulk without value.

4. **Scope creep into implementation archaeology.** Annotating one sprint module's internal implementation details (NDJSON parsing, `last_event_time`, `events_received`) in the spec creates an expectation that all sprint modules deserve similar annotations. The spec would balloon with implementation notes about files it explicitly says are "unchanged."

**Acknowledged strengths of the proposal**:
1. If a future implementer considers extracting monitor.py into pipeline/, this annotation would save them time understanding why it cannot be generalized.
2. The coupling between monitor.py's NDJSON parsing and sprint's `--output-format stream-json` choice is a genuine architectural dependency worth documenting *somewhere*.

**Risk if adopted unnecessarily**:
- Precedent for annotating every "unchanged" module with its internal coupling details. Would need similar annotations for tui.py (coupled to MonitorState shape), tmux.py (coupled to session naming), logging_.py (coupled to PhaseResult format), etc. The module listing becomes a mini-architecture-decision-record for each file.

---

## CHANGE-9: Add stall watchdog regression test to M2 acceptance criteria

**Position**: REDUCE
**Strength of counter-case**: 7/10

**Arguments AGAINST**:

1. **D2.4 already covers this.** The current acceptance criterion states: "uv run pytest tests/sprint/ exits 0 with all sprint test files passing at extraction start; no sprint test modifications during pipeline/ migration." If stall watchdog tests exist in `tests/sprint/`, they will run and must pass. If they do not exist, that is a test coverage gap in the *current* sprint test suite, not something to address via the v2.08 roadmap's M2 acceptance criteria.

2. **Adding specific feature-level test requirements to M2 inflates scope.** M2's purpose is to migrate sprint to pipeline/ *without regression*. If we add "stall watchdog verified in at least one test case," we should also add: "TUI error resilience verified in at least one test case," "diagnostic report generation verified in at least one test case," "signal handler graceful shutdown verified in at least one test case," etc. Each sprint behavior could justify its own acceptance criterion. The correct boundary is: "all existing tests pass."

3. **This may require writing NEW tests, expanding M2 scope.** The current test suite may or may not have stall watchdog test coverage. If it does not, this acceptance criterion forces the implementer to write new tests during M2 -- tests for pre-existing functionality, not for the migration itself. This is scope creep: M2 is a migration milestone, not a "improve sprint test coverage" milestone.

4. **Premature specificity.** The criterion names specific behaviors (`--stall-timeout with warn and kill actions`) that the implementer must verify. But the extraction may restructure how the watchdog integrates with the poll loop. Mandating a test for the pre-extraction API shape in a post-extraction context is potentially contradictory.

**Acknowledged strengths of the proposal**:
1. The stall watchdog is the most complex sprint behavior that interacts with `ClaudeProcess` (which is being extracted). It is a genuine regression risk point.
2. If the existing test suite lacks watchdog coverage, requiring at least one test is a reasonable safety net.

**Risk if adopted unnecessarily**:
- M2 scope expands from "zero-regression migration" to "zero-regression migration plus targeted test coverage improvements." This increases M2 effort and potentially delays M3/M4 work.

**Counter-proposal**:
- Add to D2.4: "If stall watchdog behavior is exercised by existing sprint tests, those tests pass unchanged." This makes the criterion conditional on existing coverage rather than mandating new test creation.

---

## Triage Assessment

### Genuinely Needed (adopt with modifications)

**CHANGE-7** (debug_log removal note): This is the only change that addresses a *compile-time blocker*. When `ClaudeProcess` moves to `pipeline/process.py`, the `from .debug_logger import debug_log` import will fail because `debug_logger` is a sprint-only module. An implementer WILL discover this, but noting it in the migration strategy costs one line and prevents confusion during tasklist execution. Accept with tighter wording: "Step 2: When moving ClaudeProcess, remove or replace debug_log() calls (sprint-only dependency; NFR-07)."

### Adopt in Reduced Form

**CHANGE-4** (missing modules): Add a comment, not full entries. One line acknowledging their existence is sufficient.

**CHANGE-6** (executor line count): Fix the line count from ~100 to ~150. Do NOT add the (a)-(d) preservation checklist -- that belongs in tasklist task descriptions, not the spec.

**CHANGE-9** (stall watchdog test): Reword as conditional on existing test coverage, not as a mandate to write new tests.

### Reject

**CHANGE-5** (computed property chain): Pure implementation detail. D2.4 already catches property chain breakage via existing tests. Adding 7 named properties to acceptance criteria is over-engineering the spec.

**CHANGE-8** (monitor coupling annotation): YAGNI documentation. Nobody is proposing to extract monitor.py. Annotating why an unchanged file is unchanged is defensive spec-writing that adds bulk without value. If this coupling needs documenting, it belongs in monitor.py's docstring (where it already lives).

### Summary Table

| Change | Verdict | Spec Impact | Implementation Risk Mitigated | Cost/Benefit |
|--------|---------|-------------|-------------------------------|--------------|
| 4 | REDUCE | +1 line | Low (discoverable) | Marginal positive |
| 5 | REJECT | +3 lines + property list | None (D2.4 covers) | Net negative |
| 6 | REDUCE | +0 net (fix number) | Low (discoverable) | Marginal positive |
| 7 | ACCEPT | +1 line | Medium (compile-time blocker) | Positive |
| 8 | REJECT | +2 lines | None (YAGNI) | Net negative |
| 9 | REDUCE | +1 line (conditional) | Low (D2.4 covers base case) | Marginal positive |

**Net assessment**: Of the 6 proposed changes, only CHANGE-7 addresses a risk that an implementer would not naturally discover within the first 5 minutes of working on the affected file. The remaining 5 are defensive documentation that trades spec readability for marginal risk reduction. The spec is already 960+ lines; every addition must earn its place.
