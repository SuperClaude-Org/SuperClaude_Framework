# Sprint CLI Output Buffering Fix — Tasklist Index

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | Sprint CLI Output Buffering Fix (v2.05 Diagnostic) |
| Generator Version | sc:workflow v4.2.0 |
| Generated | 2026-03-04 |
| Status | PENDING |
| TASKLIST_ROOT | `.dev/releases/current/v2.03-CLI-Sprint-diag/tasklist-fixes` |
| Source | `TASKLIST_ROOT/../adversarial/debate-verdict.md` |
| Total Phases | 4 |
| Total Tasks | 16 |
| Branch | `v2.05-sprint-cli-specifications` |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | `TASKLIST_ROOT/tasklist-index.md` |
| Phase 1 Tasklist | `TASKLIST_ROOT/phase-1-tasklist.md` |
| Phase 2 Tasklist | `TASKLIST_ROOT/phase-2-tasklist.md` |
| Phase 3 Tasklist | `TASKLIST_ROOT/phase-3-tasklist.md` |
| Phase 4 Tasklist | `TASKLIST_ROOT/phase-4-tasklist.md` |
| Debate Verdict (source) | `TASKLIST_ROOT/../adversarial/debate-verdict.md` |

---

## Root Cause Summary

The sprint CLI subprocess uses `--output-format text` which buffers ALL stdout until session completion. Multi-turn agentic sessions produce 0 bytes for minutes/hours. The TUI monitor classifies 0-byte growth as "STALLED" after 60s. Users kill what appears to be a hung process — but it was working.

**Exit code -9** in the execution log = user-initiated kill (SIGTERM → 10s → SIGKILL), not a crash.

---

## Priority Items from Debate Verdict

| Priority | Fix | File(s) | Risk |
|---|---|---|---|
| P0 | Switch `--output-format text` → `stream-json` | `process.py` | Medium — requires monitor rewrite |
| P1 | Adapt monitor to parse stream-json NDJSON lines | `monitor.py` | Medium — thread safety with partial writes |
| P1 | Adjust TUI stall thresholds for stream-json | `tui.py`, `models.py` | Low |
| P1 | Update `_determine_phase_status` for stream-json output file | `executor.py` | Low — result file is independent |
| P2 | (Deferred) Feature-detect `stream-json` support for backward compat | `process.py` | — |
| P3 | (Deferred) Replace `@{path}` with tool-read directive in prompt | `process.py` | — |

P2 and P3 are deferred — not in this sprint.

---

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome | Tier |
|---|---|---|---|---|
| 1 | Output Format Switch (P0) | T01.01–T01.04 | `process.py` emits stream-json; monitor parses NDJSON | STRICT |
| 2 | TUI & Stall Detection (P1) | T02.01–T02.04 | TUI shows real-time progress; stall detection accurate | STANDARD |
| 3 | Test Updates | T03.01–T03.04 | All existing tests pass; new tests cover stream-json path | STRICT |
| 4 | Integration Validation | T04.01–T04.04 | Manual and automated E2E validation | STANDARD |

---

## Existing Test Assertions That Must Be Updated

These tests will break after the output format change and must be updated in Phase 3:

| Test File | Test | Current Assertion | Required Change |
|---|---|---|---|
| `test_process.py` | `test_build_command_required_flags` | `assert "text" in cmd` | Change to `assert "stream-json" in cmd` |
| `test_process.py` | `test_build_env_claudecode` | `assert env["CLAUDECODE"] == ""` | Change to `assert "CLAUDECODE" not in env` |
| `test_regression_gaps.py` | `test_build_env_preserves_existing_vars` | `assert env["CLAUDECODE"] == ""` | Change to `assert "CLAUDECODE" not in env` |

---

## Files Modified in This Sprint

| File | Changes |
|---|---|
| `src/superclaude/cli/sprint/process.py` | `build_command()`: text→stream-json; `build_env()`: already fixed (env.pop) |
| `src/superclaude/cli/sprint/monitor.py` | Rewrite `_poll_once()` and `_extract_signals()` to parse NDJSON |
| `src/superclaude/cli/sprint/models.py` | Add `last_message_at` field to `MonitorState`; revise stall thresholds |
| `src/superclaude/cli/sprint/tui.py` | Update stall display for stream-json liveness signals |
| `src/superclaude/cli/sprint/executor.py` | Minor: handle stream-json output file in `_determine_phase_status` fallback |
| `tests/sprint/test_process.py` | Update format and env assertions |
| `tests/sprint/test_regression_gaps.py` | Update env assertion |
| `tests/sprint/test_monitor_stream.py` | New file: NDJSON monitor tests |
| `tests/sprint/test_e2e_success.py` | May need stream-json mock output |
| `tests/sprint/test_e2e_halt.py` | May need stream-json mock output |
