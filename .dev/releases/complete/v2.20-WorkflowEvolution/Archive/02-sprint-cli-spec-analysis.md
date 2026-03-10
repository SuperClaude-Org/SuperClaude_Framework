# 02 — Sprint CLI Specification Analysis

**Scope**: v2.05 Sprint CLI Specification (sprint-cli-specification.md + extraction.md + test-strategy.md + roadmap.md)
**Focus**: Architecture — gaps between design intent and implementation constraints
**Date**: 2026-03-08
**Purpose**: Diagnostic only — no fixes proposed

---

## Spec Overview

The v2.05 spec is a 2,053-line design specification for `superclaude sprint` — the CLI command that executes tasklist phases sequentially using Claude subprocesses. It defines 11 source files, ~2,160 estimated lines, 35 functional requirements, 8 non-functional requirements, and a complete test suite with mock strategies.

---

## Gaps Between Design Intent and Implementation Constraints

### Gap 1: The Spec Designs for Orchestration Success, Not for LLM Output Variability

The spec's architecture is principled: clean module separation (models, config, executor, monitor, process, tui, tmux, logging, notify), each with clear responsibilities. But the entire architecture assumes that Claude's output follows predictable patterns:

- **Signal extraction** (FR-015, `monitor.py`): The monitor extracts task IDs with `re.compile(r'T\d{2}\.\d{2}')`, tool names with pattern matching, and file changes from output text. These patterns assume Claude structures its output consistently. If Claude changes its output format (e.g., uses different task ID syntax), the monitor silently stops extracting signals.

- **Result file parsing** (FR-030, `executor.py`): Phase status determination uses a 7-level priority chain that parses result files for `EXIT_RECOMMENDATION` and `status` fields. This assumes Claude writes result files in the expected format. The v2.07 retrospective found that `EXIT_RECOMMENDATION: CONTINUE` overrides `status: PARTIAL` — a priority chain bug that existed because the spec never specified what happens when these signals *conflict*.

- **Phase timeout** (NFR-003): `max_turns * 120 + 300` seconds. This formula assumes Claude processes at a rate that makes 120 seconds per turn reasonable. No empirical evidence supports this formula — it's a guess.

> Evidence: v2.05 §12.3 test `test_build_command_default()`: Tests only verify the command *structure* (flags present), not the command's *behavior* (what Claude produces).

### Gap 2: The Spec Defers End-to-End Testing to "Manual Validation"

The test architecture (§12.2) explicitly mocks the subprocess:

| Component | Mock Strategy |
|-----------|---------------|
| `process.py` | Mock `subprocess.Popen`, verify command construction |
| `executor.py` | Mock `ClaudeProcess.start/wait`, mock monitor, verify flow |
| `tmux.py` | Mock `subprocess.run`, verify tmux commands |

The spec acknowledges this gap in §12.2: "Full pipeline E2E | Integration (optional) | Requires `claude` binary in PATH. Marked `@pytest.mark.skipif(not shutil.which('claude'))`. Uses a trivial spec file. | Not in v1 scope — AC-02 validated manually."

This means the most important test — does the pipeline actually work end-to-end? — is explicitly deferred. The entire test suite validates that the orchestration code correctly handles *simulated* success and failure, but never tests real interaction with Claude.

> Evidence: v2.05 §14 "Open Design Questions" #2: "Should the monitor track token usage from claude output? Defer to v4.4: requires parsing structured output format." — Even basic output format questions are deferred.

### Gap 3: Architectural Decisions That Are Implicit or Deferred

**Output format choice**: The spec uses `output_format="text"` for subprocess output, redirecting stdout to files. It never discusses why `stream-json` was not used (which would provide structured output). This choice has profound implications — text output requires regex-based parsing of Claude's freeform output, while stream-json provides machine-readable events. The decision is implicit.

**Prompt construction**: The spec defines that the executor builds a prompt from the tasklist phase file, but doesn't specify prompt engineering constraints. How should the prompt be structured to ensure Claude produces parseable output? What format instructions should be included? These questions are left entirely to the implementer.

**Result file path injection**: The spec designs a result file mechanism where Claude writes phase completion reports. But how does Claude know where to write the result file? The prompt must include the path. If the path is wrong or Claude ignores it, the executor waits forever. The spec doesn't address this failure mode.

### Gap 4: Scope Ambition vs Agent Capability

The spec estimates ~2,160 lines across 11 files. For agent-generated code, this is ambitious. The spec includes:

- A full TUI dashboard with Rich Live rendering
- Threading (monitor runs in a background thread)
- Process group management with SIGTERM→SIGKILL escalation
- Tmux integration with pane splitting
- JSONL and Markdown dual logging
- Desktop notifications across platforms
- Phase discovery with flexible naming conventions

Each of these involves platform-specific behavior, edge cases, and failure modes that are hard to test in isolation. The spec specifies them all in a single release, creating a large surface area for bugs. The v2.07 retrospective validated this concern: 7 telemetry bugs found on first real run.

---

## Whether Success Criteria Are Measurable

The extraction document (extraction.md) defines 8 success criteria:

| SC | Measurability |
|----|---------------|
| SC-001: Sprint executes multi-phase sequentially | Measurable — but only tested with mocks |
| SC-002: Phase lifecycle tracked | Measurable via JSONL log — but JSONL had inaccuracies (v2.07) |
| SC-003: TUI renders phase progress | Measurable via snapshot tests — but snapshots test rendering, not correctness |
| SC-004: Tmux integration works | Measurable — but mocked in tests |
| SC-005: Signal handler graceful shutdown | Measurable — but v2.13 identifies signal handling as untested subsystem |
| SC-006: Resume from failed phase | Measurable — but requires prior failure to test |
| SC-007: All test assertions pass | Meta-circular: tests pass means tests pass |
| SC-008: End-to-end execution | "Validated manually" — not automated |

SC-007 is particularly revealing: "All test assertions pass" is a success criterion. But if the tests use mocks that don't capture real behavior, passing tests prove nothing about production quality.

---

## Error Handling and Edge Cases: Specified or Left to Implementer?

**Specified error handling**:
- SIGTERM → 10s grace → SIGKILL escalation (FR-029)
- Phase timeout computation (NFR-003)
- Stall detection thresholds (FR-021: 60s)
- EXIT_RECOMMENDATION parsing for halt decision

**Unspecified error handling**:
- What happens if Claude's stdout is binary/corrupted?
- What happens if the result file is partially written (crash during write)?
- What happens if two phases write to the same output file?
- What happens if the tmux session dies mid-sprint?
- What happens if disk space runs out during logging?
- What happens if the monitor thread crashes?
- What happens if Rich Live rendering fails (v2.03 identifies this: "TUI silently dies after first render exception")

The TUI failure mode is particularly telling: it's identified as a root cause in v2.03, but the v2.05 spec doesn't address it. The spec designs the TUI (FR-016 through FR-021) without discussing error resilience. The v2.13 spec later identifies "TUI error resilience" as an untested subsystem.

---

## Synthesis

### Top 3 Theories

**Theory 1: The Spec Optimizes for Architectural Correctness, Not Operational Reality**
The spec is architecturally sound: clean module boundaries, well-defined interfaces, principled separation of concerns. But it designs for the happy path of "Claude produces expected output, the executor processes it, the monitor extracts signals, the TUI renders progress." Every architectural decision assumes the parts work correctly in isolation. The operational reality — LLM output variability, subprocess timing, threading races, platform differences — is addressed through mock-based tests that simulate the happy path.

**Theory 2: Scope Ambition Creates Untestable Surface Area**
2,160 lines across 11 files with threading, subprocess management, TUI rendering, tmux integration, and structured logging is too much to validate in a single release with mock-based tests. Each component works in isolation (proven by unit tests) but the interaction between components under real conditions is where bugs emerge. The v2.13 spec found 6 untested subsystems at ~45% coverage, confirming this theory.

**Theory 3: Deferred End-to-End Testing Is the Root Failure Mode**
The spec explicitly defers end-to-end testing ("Not in v1 scope — AC-02 validated manually"). This means the most important validation — does the complete pipeline work? — is a manual, optional step. In practice, "validated manually" means "validated once by the developer, never again by CI." Every subsequent change to any component can silently break the end-to-end flow without detection.

### Blind Spots

1. **LLM output format**: The spec never discusses how Claude's freeform text output interacts with the regex-based signal extraction, result file parsing, or frontmatter checking. This is the interface between the system and its primary dependency, and it's entirely unspecified.
2. **Threading failure modes**: The monitor runs in a background thread. The spec doesn't discuss what happens if the thread crashes, raises an exception, or falls behind in processing. The v2.13 spec identifies "monitor thread lifecycle" as untested.
3. **Platform-specific behavior**: Tmux integration, desktop notifications, and process group management are platform-specific. The spec doesn't discuss cross-platform testing or CI environments where tmux/notify-send may not be available.
4. **Prompt engineering**: The spec designs the orchestration (how to call Claude) but not the prompts (what to tell Claude). Prompt quality determines output quality, and output quality determines whether gates pass.

### Confidence vs Reality Gaps

| Confidence Signal | Source | Reality |
|-------------------|--------|---------|
| "Total: ~2,160 lines estimated across 11 files" | v2.05 §1 | Implies the scope is well-understood and bounded |
| Test strategy: "Testability: 9.0/10" | v2.03 Panel Assessment | Tests use mocks; 6 subsystems remained untested (v2.13) |
| "Mock strategy: subprocess.Popen mocked via unittest.mock.patch" | v2.05 §12.2 | Mocks simulate expected behavior, not real LLM output |
| "Sprint test stability guarantee" | v2.08 §13.6 | "If any sprint test imports break, the migration has a bug — this is the canary" — but canary tests only catch import breaks, not behavioral bugs |
| Extraction extraction_mode: "chunked (4 chunks)" | extraction.md | Implies thorough analysis; but extraction is also agent-generated |

### Evidence Citations

1. v2.05 §12.2: "Full pipeline E2E | Integration (optional) | Not in v1 scope — AC-02 validated manually."
2. v2.05 §12.2: "Mock strategy: subprocess.Popen mocked via unittest.mock.patch for all subprocess tests."
3. v2.05 §14 Q2: "Should the monitor track token usage from claude output? Defer to v4.4."
4. v2.05 §1: Module architecture estimates ~2,160 lines — ambitious scope for agent-generated code.
5. v2.03 §Problem Statement: "TUI silently dies after first render exception" — known failure mode not addressed in v2.05 TUI design.
6. v2.13 §D4: "6 subsystems remain untested... Coverage is approximately 45%."

---

*Analysis complete. Diagnostic only — no fixes proposed.*
