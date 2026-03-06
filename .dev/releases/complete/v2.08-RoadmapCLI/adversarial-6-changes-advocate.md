# Advocate Brief: 6 Recommended v2.08 Spec Changes

**Role**: ADVOCATE (arguing FOR adoption)
**Date**: 2026-03-05
**Evidence base**: merged-spec.md, roadmap.md, executor.py, models.py, process.py, monitor.py, debug_logger.py, diagnostics.py

---

## CHANGE-4: Add missing modules to Section 3.1 module listing

**Position**: ADOPT
**Strength of case**: 9/10

**Arguments FOR**:

1. **The modules exist and are actively imported.** `debug_logger.py` (138 lines) and `diagnostics.py` (253 lines) are present in `src/superclaude/cli/sprint/` (verified via filesystem listing). The executor imports both at lines 11-12 of `executor.py`: `from .debug_logger import debug_log, setup_debug_logger` and `from .diagnostics import DiagnosticCollector, FailureClassifier, ReportGenerator`. The monitor also imports from debug_logger at line 17: `from .debug_logger import debug_log`. These are not marginal files -- they are load-bearing dependencies of the two most critical sprint modules.

2. **Omission creates extraction ambiguity.** The v2.08 spec's Section 3.1 is the authoritative module listing that drives the M2 migration plan. An implementer reading Section 3.1 sees 10 sprint files, encounters `import .debug_logger` in the actual code, and must resolve the discrepancy mid-implementation. The spec currently lists `monitor.py` as "unchanged" -- but `monitor.py` imports `debug_logger` (monitor.py line 17). If an implementer does not know `debug_logger.py` exists, they cannot correctly reason about the monitor's dependency graph during extraction.

3. **The "(stays in sprint/)" annotation provides critical architectural guidance.** These modules are sprint-specific: `DiagnosticCollector` collects sprint phase failures, `FailureClassifier` categorizes sprint-specific error patterns, `debug_log` is wired to sprint's `setup_debug_logger(config)` call (executor.py line 53). They should NOT be extracted to `pipeline/`. The annotation makes this boundary decision explicit and prevents over-extraction.

**Acknowledged weaknesses**:

1. An implementer running `ls sprint/` would discover these files regardless. The spec omission creates friction, not impossibility.

**Risk if NOT adopted**:

- An implementer extracts `debug_logger.py` to `pipeline/` (it looks generic), breaking the NFR-007 boundary (pipeline has no sprint imports) because `setup_debug_logger` takes a `SprintConfig`. Alternatively, they try to move `DiagnosticCollector` into pipeline, creating an unnecessary coupling.
- The migration step count in Section 12 becomes inaccurate because two files that participate in the import graph are invisible to the plan.

**Proposed wording**:

Add to Section 3.1 sprint/ listing, after `notify.py`:
```
    debug_logger.py          <- stays in sprint/ (sprint-specific debug logging; used by executor, process, monitor)
    diagnostics.py           <- stays in sprint/ (sprint-specific failure classification and diagnostic reports)
```

---

## CHANGE-5: Add computed property chain verification to M2 acceptance criteria

**Position**: ADOPT
**Strength of case**: 8/10

**Arguments FOR**:

1. **SprintConfig has 7 computed properties that depend on `release_dir`.** In `models.py` lines 101-131, `SprintConfig` defines: `debug_log_path` (line 102, returns `self.results_dir / "debug.log"`), `results_dir` (line 107, returns `self.release_dir / "results"`), `execution_log_jsonl` (line 111), `execution_log_md` (line 114), `output_file()` (line 124), `error_file()` (line 127), and `result_file()` (line 130). After M2, `SprintConfig` will inherit from `PipelineConfig`, and `release_dir` will become a property alias for `PipelineConfig.work_dir`. Every one of these 7 computed properties must resolve correctly through this alias chain.

2. **The current D2.1 acceptance criteria only tests the alias itself.** The current wording says: "release_dir property aliases work_dir; existing code using config.release_dir works unchanged." This verifies `config.release_dir == config.work_dir` but says nothing about whether `config.results_dir` (which calls `self.release_dir` internally), `config.debug_log_path` (which calls `self.results_dir` which calls `self.release_dir`), or the three file-path methods still resolve correctly. A naive property alias could pass the current criteria while breaking the transitive chain.

3. **These properties are used in production code paths.** `executor.py` line 248 uses `config.results_dir` to write diagnostic reports. Line 299 uses `config.release_dir` directly. `executor.py` line 74 uses `config.output_file(phase)`. `process.py` line 118 uses `config.output_file(self.phase)` and line 119 uses `config.error_file(self.phase)`. If any of these break silently (returning wrong paths rather than raising errors), sprint writes files to wrong locations -- a silent data-loss regression.

4. **This is a high-value, low-cost addition.** The regression tests are trivial to write: instantiate a `SprintConfig` with a known `release_dir`, assert each property returns the expected path. Perhaps 20 lines of test code that prevent a class of silent failures during the most risk-prone milestone (M2, rated Medium risk in the roadmap).

**Acknowledged weaknesses**:

1. Python property aliasing is straightforward (`@property def release_dir: return self.work_dir`), and a competent implementer would likely test this. The explicit acceptance criteria is belt-and-suspenders.
2. The "7 computed properties" framing is slightly misleading -- 3 of them are methods (`output_file`, `error_file`, `result_file`) that take a `phase` argument, not zero-argument properties. The verification approach differs slightly (need a mock Phase).

**Risk if NOT adopted**:

- A subtle property resolution bug (e.g., `super().__init__()` ordering, `@property` vs attribute shadowing) causes `results_dir` to return `None / "results"` instead of the expected path. Sprint tests that don't exercise these specific property chains pass, but production runs write diagnostics to `/results/` (relative to CWD) instead of the release directory. This is the kind of bug that only manifests in real sprint executions, not unit tests, and is painful to debug.

**Proposed wording**:

Add to D2.1 acceptance criteria:
> All 7 computed properties (`debug_log_path`, `results_dir`, `execution_log_jsonl`, `execution_log_md`, `output_file`, `error_file`, `result_file`) resolve correctly through the `release_dir` -> `work_dir` property alias chain. Regression tests verify all property paths against expected values.

---

## CHANGE-6: Update executor line count and sprint_run_step complexity in Section 13.5

**Position**: ADOPT
**Strength of case**: 9/10

**Arguments FOR**:

1. **The "~100 lines" estimate is factually wrong.** The current spec (Section 13.5, line 965) says sprint_run_step contains "the ~100 lines of existing logic, unchanged in behavior." The actual poll loop in `executor.py` spans lines 68-262 (the body of the `for phase in config.active_phases:` loop), which is approximately 195 lines. Even counting only the core poll logic (lines 94-171, the `while proc_manager._process.poll() is None:` loop plus post-poll result determination through line 205), that is ~110 lines. But the sprint_run_step callable must also include monitor setup (lines 73-76), process launch (lines 83-89), debug logging of phase boundaries (lines 90, 183-189, 224-231), diagnostic collection on failure (lines 242-258), and the TUI error-resilience wrapping (lines 166-170). The total is closer to 180 lines.

2. **The spec omits four critical behaviors that sprint_run_step must preserve.** The comment "unchanged in behavior" is insufficient guidance. An implementer reading Section 13.5 would know they need to wrap the subprocess lifecycle, but would not know they must preserve:
   - **(a) debug_logger calls per poll tick and phase boundaries**: `executor.py` lines 90, 112-123, 133-140, 183-189, 224-231, 250-251, 258 -- there are 7 distinct debug_log call sites in the poll loop alone.
   - **(b) DiagnosticCollector/FailureClassifier/ReportGenerator on failure**: lines 243-258 -- a 16-line failure-handling block that writes diagnostic markdown reports per failed phase.
   - **(c) TUI error resilience wrapping**: lines 166-170 -- `try: tui.update(...) except Exception` ensures a display glitch cannot abort the sprint. Without this, a TUI rendering error would propagate and kill the sprint.
   - **(d) Stall watchdog with kill capability**: lines 126-162 -- a 37-line stall detection system with configurable warn/kill actions, single-fire guard, and reset logic.

3. **An incorrect line count distorts effort estimation.** If a tasklist generator or implementer reads "~100 lines" and plans accordingly, they will underestimate the M2 migration effort by ~80%. The spec's own roadmap rates M2 as Medium risk with effort "S" (small). If the sprint_run_step is actually 180 lines of interlocked behavior (polling, monitoring, diagnostics, watchdog, TUI resilience), the migration deserves more careful planning.

**Acknowledged weaknesses**:

1. Line counts are inherently imprecise guidance. The exact number matters less than the qualitative complexity. The spec could use "~150-180 lines" as a range.
2. Some of these behaviors (debug_log calls) are straightforward to preserve by copying -- they are not architecturally complex, just numerous.

**Risk if NOT adopted**:

- An implementer creates a sprint_run_step that faithfully wraps the subprocess lifecycle but omits the diagnostic collection block, resulting in sprint failures that produce no diagnostic reports -- a direct regression from v2.03/v2.07 improvements. Or they omit the TUI error resilience, causing intermittent sprint crashes on terminal resize events. These are the kinds of regressions that existing tests may not catch because they depend on runtime conditions (actual failures, actual TUI rendering).

**Proposed wording**:

Replace Section 13.5's sprint_run_step comment (line 965 area) with:
```python
    def sprint_run_step(step, pipeline_config, cancel_check):
        # Sprint's existing poll loop: ~180 lines preserving:
        # (a) debug_logger calls per poll tick and phase boundaries
        # (b) DiagnosticCollector/FailureClassifier/ReportGenerator on failure
        # (c) TUI error resilience wrapping (try/except around tui.update)
        # (d) Stall watchdog with configurable warn/kill actions
        ...
        return StepResult(...)
```

---

## CHANGE-7: Add debug_log() removal note to migration strategy

**Position**: ADOPT WITH MODIFICATIONS
**Strength of case**: 6/10

**Arguments FOR**:

1. **`process.py` currently imports debug_logger.** `sprint/process.py` line 12: `from .debug_logger import debug_log` and line 14: `_dbg = logging.getLogger("superclaude.sprint.debug.process")`. When `ClaudeProcess` is extracted to `pipeline/process.py`, these imports become invalid -- `pipeline/` cannot import from `sprint/` (NFR-007). The implementer must decide: strip the debug_log calls from the pipeline copy, or move debug_logger to pipeline, or use stdlib logging in pipeline.

2. **The migration strategy (Section 12) is silent on this.** Step 2 says "Move ClaudeProcess from sprint/process.py to pipeline/process.py; re-export from sprint/process.py." This reads as a simple move-and-re-export. But the actual `process.py` has 7 `debug_log()` calls (lines 139, 142-145, 147-148, 151, 181, 196, 202-207) wired to the sprint-specific debug logger. The move is not a simple copy -- it requires an active decision about logging.

3. **NFR-007 makes this a hard constraint, not a style preference.** The spec states "pipeline/ has no imports from sprint/ or roadmap/." This is a foundational architectural constraint. If an implementer copies process.py verbatim to pipeline/, the code will fail to import (or worse, create a circular dependency if they try to import debug_logger from sprint).

**Acknowledged weaknesses**:

1. A competent implementer would discover this during the first `import` error and resolve it. The note is helpful but not essential for correctness -- the failure mode is loud (ImportError), not silent.
2. The proposed wording is overly prescriptive ("Remove debug_log() calls"). The implementer might reasonably choose stdlib `logging.getLogger()` in pipeline/process.py instead, which would be equally valid and preserve observability.

**Risk if NOT adopted**:

- Low practical risk. The failure mode is an immediate ImportError, which is self-correcting. The main cost is wasted implementation time as the implementer discovers, diagnoses, and resolves the issue -- perhaps 15-30 minutes.

**Proposed wording** (modified from original):

Add to Section 12, after step 2:
> Note: `sprint/process.py` contains `debug_log()` calls tied to the sprint-specific debug logger. When extracting `ClaudeProcess` to `pipeline/process.py`, either replace these with stdlib `logging.getLogger()` calls (preserving observability) or remove them (keeping pipeline/ minimal). Sprint can re-add sprint-specific logging via its re-export wrapper or executor-level calls. NFR-007 prohibits pipeline/ from importing sprint modules.

---

## CHANGE-8: Add monitor coupling annotation

**Position**: ADOPT
**Strength of case**: 7/10

**Arguments FOR**:

1. **The coupling is real and architecturally significant.** `monitor.py` (all 199 lines) is built entirely around parsing NDJSON (stream-json) output. The module docstring (line 1-6) explicitly states: "Parses stream-json (NDJSON) output from `claude --print --output-format stream-json`." The `_process_chunk` method (lines 131-162) parses JSON lines. The `_extract_signals_from_event` method (lines 164-178) expects specific event types (`event.get("type", "") == "tool_use"`). This is not a general-purpose monitor -- it is coupled to a specific output format.

2. **The spec says roadmap uses `output_format=text`.** Section 3.1's `pipeline/process.py` annotation says: "output_format parameterized: sprint=stream-json, roadmap=text". The monitor cannot parse plain text output using NDJSON parsing logic. The annotation makes it explicit that `monitor.py` stays in sprint and is not a candidate for extraction to pipeline.

3. **The annotation prevents a subtle extraction mistake.** Without it, an implementer might reasonably think "monitoring is a generic pipeline concern" and try to extract `monitor.py` to `pipeline/`. This would either fail (because roadmap output is not NDJSON) or require building a format-agnostic monitor abstraction -- significant scope creep. The annotation closes this door proactively.

4. **Stall detection uses NDJSON-specific signals.** `MonitorState.last_event_time` (models.py line 214) is updated per NDJSON event (monitor.py line 148). The `stall_status` property (models.py lines 225-238) checks `self.events_received`, which counts parsed NDJSON lines. The stall watchdog in executor.py (lines 126-162) depends on `ms.stall_seconds` and `ms.events_received`. This chain -- monitor parses NDJSON, updates event counters, stall watchdog reads counters -- is the coupling that the annotation documents.

**Acknowledged weaknesses**:

1. The annotation is documentation, not enforcement. It does not prevent extraction; it only advises against it. A determined implementer could ignore it.
2. The current spec already says `monitor.py` is "unchanged," which implicitly means it stays in sprint. The annotation adds clarity but not new information for a careful reader.

**Risk if NOT adopted**:

- An implementer or future spec revision attempts to generalize the monitor for pipeline use, resulting in either scope creep (building a format-agnostic monitor) or a broken monitor (trying to parse text output as NDJSON). Medium-probability, medium-impact.

**Proposed wording**:

Change Section 3.1's `monitor.py` entry from:
```
    monitor.py               <- unchanged
```
to:
```
    monitor.py               <- unchanged; coupled to stream-json output format (parses NDJSON events for stall detection via last_event_time/events_received); roadmap v1 does not use monitoring
```

---

## CHANGE-9: Add stall watchdog regression test to M2 acceptance criteria

**Position**: ADOPT
**Strength of case**: 8/10

**Arguments FOR**:

1. **The stall watchdog is a significant behavioral feature that could regress during M2.** The watchdog (executor.py lines 126-162) is a 37-line system with configurable timeout, two action modes (warn and kill), a single-fire guard with reset logic, and integration with the monitor's event counters. During M2, the executor is being restructured to call `execute_pipeline()` internally. The watchdog must survive this restructuring -- it must remain inside `sprint_run_step`, not in `execute_pipeline` (which is format-agnostic and does not understand NDJSON stall detection).

2. **The current D2.4 acceptance criteria is necessary but insufficient.** D2.4 says: "uv run pytest tests/sprint/ exits 0 with all sprint test files passing at extraction start; no sprint test modifications during pipeline/ migration." This verifies that existing tests still pass. But if the existing test suite does not include a stall watchdog test, this criterion provides no protection. The change explicitly requires at least one post-migration test case for the watchdog, closing the coverage gap.

3. **The watchdog has two distinct behaviors that need separate verification.** `config.stall_action == "kill"` (executor.py line 141) terminates the process and sets `_timed_out = True`. `config.stall_action == "warn"` (executor.py line 152) prints a warning but allows the process to continue. Both behaviors interact with the monitor's `stall_seconds` field (which depends on `events_received > 0` -- line 129 -- to avoid triggering during startup). A single test case that only tests the warn path would miss a regression in the kill path.

4. **The watchdog interacts with the monitor coupling (CHANGE-8).** The watchdog reads `ms.stall_seconds` and `ms.events_received` from `MonitorState`, which is populated by the NDJSON-parsing monitor. If M2 accidentally disrupts this data flow (e.g., by changing how the monitor is initialized or how its state object is shared), the watchdog would silently stop working -- `stall_seconds` would always be 0.0, and the watchdog would never trigger. An explicit test catches this.

**Acknowledged weaknesses**:

1. The stall watchdog may already have test coverage in the existing test suite. I did not verify this, and the existing tests may adequately cover this behavior. The change is redundant if so.
2. Adding acceptance criteria to D2.4 increases the M2 definition of done. If the stall watchdog tests are complex to write (requiring mock NDJSON streams with timed pauses), this could slow M2 delivery.

**Risk if NOT adopted**:

- The stall watchdog silently stops functioning after M2 migration. Users running long sprint phases with `--stall-timeout 300 --stall-action kill` would no longer get automatic kill behavior on stalled phases. This is a production regression that would only be discovered during a real stall event -- potentially hours into a sprint run, with no diagnostic output explaining why the watchdog did not fire.

**Proposed wording**:

Add to D2.4 acceptance criteria:
> Stall watchdog behavior (`--stall-timeout` with `warn` and `kill` actions) verified in at least one post-migration test case. Test must confirm: (a) warn action prints warning but does not terminate, (b) kill action terminates the subprocess, (c) watchdog does not trigger during startup when `events_received == 0`.

---

## Priority Ranking

| Priority | Change | Severity | Risk if Omitted | Effort to Add |
|----------|--------|----------|-----------------|---------------|
| 1 | **CHANGE-6**: Update executor line count and sprint_run_step complexity | High | Silent behavioral regressions (diagnostics, TUI resilience, watchdog) | Low (text edit) |
| 2 | **CHANGE-4**: Add missing modules to Section 3.1 | High | Extraction ambiguity, potential NFR-007 violation | Low (text edit) |
| 3 | **CHANGE-5**: Add computed property chain verification to M2 | Medium-High | Silent path resolution bugs in production | Low (text edit) |
| 4 | **CHANGE-9**: Add stall watchdog regression test to M2 | Medium-High | Silent watchdog regression after migration | Low (text edit) |
| 5 | **CHANGE-8**: Add monitor coupling annotation | Medium | Potential scope creep or extraction mistake | Low (text edit) |
| 6 | **CHANGE-7**: Add debug_log() removal note | Low-Medium | Wasted implementation time (self-correcting failure) | Low (text edit) |

**Rationale**: Changes 6 and 4 address factual inaccuracies in the spec that could lead to incorrect implementation decisions. Changes 5 and 9 strengthen acceptance criteria to catch specific regression categories. Change 8 provides architectural guidance that prevents misguided extraction. Change 7 addresses a self-correcting issue (ImportError) and is the most deferrable.

**All 6 changes should be adopted.** They are all text edits to existing spec/roadmap documents with no code impact. The total effort to apply all 6 is under 30 minutes. The risk of applying them is effectively zero (they add precision, not ambiguity). The only question is priority for the adversarial debate itself, not whether any should be rejected outright.
