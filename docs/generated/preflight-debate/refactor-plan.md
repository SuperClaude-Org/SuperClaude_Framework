# Refactor Plan: Implement 2a (Skip Entirely) with Mitigations

## Overview

Implement the preflight phase-skip mechanism: phases annotated with `execution_mode: python` whose tasks all pass are skipped in the main sprint loop, with Python writing the result contract directly.

---

## Integration Points

### 1. New `PhaseStatus.PREFLIGHT_PASS` enum value
**File**: `src/superclaude/cli/sprint/models.py`
**Risk**: Low
**Action**: Add `PREFLIGHT_PASS = "preflight_pass"` to `PhaseStatus`. Update `is_success` property to include it. Update `is_terminal` property to include it.

### 2. New `execution_mode` field on `TaskEntry` or `Phase`
**File**: `src/superclaude/cli/sprint/models.py`
**Risk**: Low
**Action**: Add `execution_mode: str = "claude"` to `Phase` dataclass. Valid values: `"claude"` (default), `"python"`. Parsed from phase file YAML frontmatter during `discover_phases()`.

### 3. Preflight executor function
**File**: `src/superclaude/cli/sprint/executor.py` (new section)
**Risk**: Medium
**Action**: Create `run_preflight(config: SprintConfig) -> dict[int, AggregatedPhaseReport]`. For each phase where all tasks have `execution_mode: python`, execute shell commands via `subprocess.run()`, collect exit codes/stdout/stderr, build `AggregatedPhaseReport`. Return a mapping of `{phase_number: report}` for phases that fully passed.

Key behaviors:
- If ANY task in a phase fails, the phase is NOT added to the result dict (falls back to Claude)
- Captures stdout/stderr to `artifacts/D-NNNN/` directories
- Respects existing `TaskEntry` structure for task identification

### 4. Result file writer
**File**: `src/superclaude/cli/sprint/executor.py`
**Risk**: Low
**Action**: Reuse `AggregatedPhaseReport.to_markdown()` to write `results/phase-N-result.md`. Add `source: preflight` to YAML frontmatter. This is a 3-line addition to the existing `to_markdown()` method.

### 5. Main loop skip logic
**File**: `src/superclaude/cli/sprint/executor.py`, function `execute_sprint()`
**Risk**: Low
**Action**: Before the `for phase in config.active_phases` loop, call `run_preflight(config)`. Inside the loop, check `if phase.number in preflight_results: continue` with appropriate logging and PhaseResult creation.

```
# Insert after line 523 (before tui.start())
preflight_results = run_preflight(config) if not config.dry_run else {}

# Insert at line 526 (start of phase loop)
if phase.number in preflight_results:
    report = preflight_results[phase.number]
    # Write result file
    result_path = config.result_file(phase)
    result_path.write_text(report.to_markdown())
    # Create PhaseResult for sprint tracking
    phase_result = PhaseResult(
        phase=phase,
        status=PhaseStatus.PREFLIGHT_PASS,
        exit_code=0,
        started_at=datetime.now(timezone.utc),
        finished_at=datetime.now(timezone.utc),
    )
    sprint_result.phase_results.append(phase_result)
    logger.write_phase_result(phase_result)
    notify_phase_complete(phase_result)
    continue
```

### 6. TUI differentiation
**File**: `src/superclaude/cli/sprint/tui.py`
**Risk**: Low
**Action**: Add display handling for `PhaseStatus.PREFLIGHT_PASS` -- distinct color (e.g., cyan) and icon to visually distinguish preflight-passed phases from Claude-passed phases.

### 7. Execution log entry
**File**: `src/superclaude/cli/sprint/logging_.py`
**Risk**: Low
**Action**: Log `"Phase {n} passed preflight -- skipping Claude subprocess"` at INFO level. Include task count, total duration, and evidence artifact paths.

### 8. Shared test fixture for contract consistency
**File**: `tests/sprint/test_preflight_contract.py` (new)
**Risk**: Low
**Action**: Test that `AggregatedPhaseReport.to_markdown()` output is correctly parsed by `_determine_phase_status()`. This is the key regression test that prevents contract drift.

---

## Execution Order

| Step | Task | Depends On | Risk |
|------|------|------------|------|
| 1 | Add `PhaseStatus.PREFLIGHT_PASS` | None | Low |
| 2 | Add `execution_mode` to `Phase` model | None | Low |
| 3 | Parse `execution_mode` from phase file frontmatter | Step 2 | Low |
| 4 | Implement `run_preflight()` | Steps 2, 3 | Medium |
| 5 | Add `source: preflight` to `to_markdown()` | None | Low |
| 6 | Add skip logic to `execute_sprint()` | Steps 1, 4, 5 | Low |
| 7 | TUI differentiation for `PREFLIGHT_PASS` | Step 1 | Low |
| 8 | Logging for preflight outcomes | Step 6 | Low |
| 9 | Contract consistency test | Steps 4, 5 | Low |
| 10 | Integration test: full sprint with preflight phases | All | Medium |

---

## What NOT to Build

- No `--verify-preflight` flag (2c rejected)
- No Claude context injection (2b rejected)
- No dual code paths
- No new CLI flags

## Future Escape Hatch

If empirical evidence shows preflight-passed phases need AI verification, the migration path to 2c is:
1. Add `--verify-preflight` flag to `SprintConfig`
2. In `execute_sprint()`, when `config.verify_preflight and phase.number in preflight_results`, spawn Claude with context injection instead of skipping
3. This is an additive change that does not break the 2a path
