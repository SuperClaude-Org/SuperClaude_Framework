# Adversarial Debate Input: 6 Recommended v2.08 Spec Changes

## Context

Three prior analyses (v2.03, v2.05, v2.07 impact on v2.08) identified 9 total editorial changes needed to the v2.08-RoadmapCLI spec. 3 have already been applied. The remaining 6 are the subject of this debate.

The v2.08 spec plans to extract a shared `pipeline/` module from the existing `sprint/` CLI code and build `superclaude roadmap` on top of it. The sprint code has been modified by v2.03 (diagnostic framework) and v2.07 (tasklist packaging + sprint improvements).

## The 6 Proposed Changes

### CHANGE-4: Add missing modules to Section 3.1 module listing
- **Target**: merged-spec.md Section 3.1 (Module Structure)
- **Current**: Sprint module listing shows 10 files (commands, config, executor, models, process, monitor, tui, tmux, logging_, notify)
- **Proposed**: Add `debug_logger.py` and `diagnostics.py` to sprint/ listing with "(stays in sprint/)" annotation
- **Severity**: Medium
- **Source analyses**: v2.05 IMPACT-3, v2.03 REAL IMPACT 2

### CHANGE-5: Add computed property chain verification to M2 acceptance criteria
- **Target**: roadmap.md M2 deliverable D2.1 acceptance criteria
- **Current**: "release_dir property aliases work_dir; existing code using config.release_dir works unchanged"
- **Proposed**: Add: "All 7 computed properties (debug_log_path, results_dir, execution_log_jsonl, execution_log_md, output_file, error_file, result_file) resolve correctly through the release_dir→work_dir property alias chain. Regression tests verify all property paths."
- **Severity**: Medium
- **Source analysis**: v2.05 IMPACT-2

### CHANGE-6: Update executor line count and sprint_run_step complexity in Section 13.5
- **Target**: merged-spec.md Section 13.5 (execute_pipeline Extension Pattern)
- **Current**: References "~100 lines of existing logic" for sprint_run_step callable
- **Proposed**: Update to ~180 lines; note sprint_run_step must preserve: (a) debug_logger calls per poll tick and phase boundaries, (b) DiagnosticCollector/FailureClassifier/ReportGenerator on failure, (c) TUI error resilience wrapping, (d) stall watchdog with kill capability
- **Severity**: Medium
- **Source analyses**: v2.05 IMPACT-3, v2.05 IMPACT-6, v2.03 REAL IMPACT 2

### CHANGE-7: Add debug_log() removal note to migration strategy
- **Target**: merged-spec.md Section 12 (Sprint Migration Strategy)
- **Current**: "Move ClaudeProcess from sprint/process.py to pipeline/process.py; re-export from sprint/process.py"
- **Proposed**: Add note: "Remove debug_log() calls from pipeline/process.py during extraction (NFR-07 violation); sprint adds debug logging via wrapper or accepts process-level logging as sprint-only from sprint/executor.py"
- **Severity**: Low
- **Source analysis**: v2.03 REAL IMPACT 2, v2.03 Recommendation 2

### CHANGE-8: Add monitor coupling annotation
- **Target**: merged-spec.md Section 3.1 sprint/monitor.py entry
- **Current**: monitor.py listed as sprint module with no annotation
- **Proposed**: Add annotation: "coupled to stream-json output format (parses NDJSON events for stall detection via last_event_time/events_received); roadmap v1 does not use monitoring"
- **Severity**: Low
- **Source analyses**: v2.05 IMPACT-4, v2.03 REAL IMPACT 3

### CHANGE-9: Add stall watchdog regression test to M2 acceptance criteria
- **Target**: roadmap.md M2 deliverable D2.4 acceptance criteria
- **Current**: "uv run pytest tests/sprint/ exits 0 with all sprint test files passing at extraction start; no sprint test modifications during pipeline/ migration"
- **Proposed**: Add: "Stall watchdog behavior (--stall-timeout with warn and kill actions) verified in at least one post-migration test case"
- **Severity**: Medium
- **Source analysis**: v2.05 IMPACT-6
