# Diff Analysis: Python Runner Task Execution Scope

## Variants Under Comparison

| Variant | Label | Summary |
|---------|-------|---------|
| B1 | Shell-only | Execute shell commands, write stdout/stderr/exit-code. Leave PLANNING, VERIFICATION, COMPLETION to Claude. |
| B2 | Shell + Artifacts | Execute shell commands AND write evidence files with captured output. Leave judgment steps to Claude. |
| B3 | Full mini-executor | Complete Python executor: shell execution, output capture, artifact writing, AND simple conditional logic. |

---

## Structural Differences

### Scope of Python Code Changes

| Concern | B1 | B2 | B3 |
|---------|----|----|-----|
| Shell command parsing | Yes | Yes | Yes |
| subprocess.run invocation | Yes | Yes | Yes |
| stdout/stderr capture | Yes | Yes | Yes |
| Exit code recording | Yes | Yes | Yes |
| Artifact file writing | No | Yes | Yes |
| Evidence template rendering | No | Yes | Yes |
| Conditional logic (pass/fail classification) | No | No | Yes |
| Step-type dispatch (PLANNING/EXECUTION/VERIFICATION/COMPLETION) | No | No | Yes |
| Result status determination | No | No | Yes |

### Integration Points with Existing Code

| Integration | B1 | B2 | B3 |
|-------------|----|----|-----|
| `_run_task_subprocess()` in executor.py | Replace with shell runner | Replace with shell runner + writer | Replace with full executor |
| `TaskResult` in models.py | Populate exit_code only | Populate exit_code + output_path | Populate all fields including status |
| `ClaudeProcess` in process.py | Bypass for EXEMPT tasks | Bypass for EXEMPT tasks | Bypass for EXEMPT tasks |
| `AggregatedPhaseReport` | Needs Claude phase to classify | Needs Claude phase to classify | Self-classifies, no Claude needed |
| New files required | ~1 (shell_runner.py) | ~1-2 (shell_runner.py, artifact_writer.py) | ~2-3 (shell_runner.py, artifact_writer.py, step_dispatcher.py) |

### Lines of Code Estimate

| Variant | New LoC | Modified LoC | Total Delta |
|---------|---------|-------------|-------------|
| B1 | ~60-80 | ~30 | ~90-110 |
| B2 | ~120-160 | ~40 | ~160-200 |
| B3 | ~250-350 | ~60 | ~310-410 |

---

## Content Differences

### What Each Variant Handles in Python vs Claude

**B1 boundary**: Python runs `subprocess.run(["claude", "--print", ...])`, captures stdout/stderr/exit_code, writes raw output to files. A subsequent Claude session reads those files, interprets results, writes `evidence.md`, and determines PASS/FAIL.

**B2 boundary**: Python runs the shell command, captures output, AND writes structured `evidence.md` files using templates (e.g., "Command: X, Exit code: Y, Output: Z"). Claude still decides whether exit_code=0 + non-empty output constitutes WORKING vs BROKEN.

**B3 boundary**: Python runs the shell command, captures output, writes evidence files, AND applies conditional rules like `if exit_code == 0 and len(stdout) > 0: status = "WORKING"`. No Claude session needed for the entire task lifecycle.

---

## Contradictions

1. **B1 vs B3 on token cost**: B1 requires a Claude session per phase to interpret raw results. B3 eliminates that session entirely. B2 reduces the Claude session scope but does not eliminate it.

2. **B1 vs B3 on reliability**: B1 claims reliability through simplicity (less Python code). B3 claims reliability through determinism (no LLM variance in result classification).

3. **B2's middle ground**: B2 occupies ambiguous territory -- it does the hard work of artifact writing but stops before the easy work of conditional classification, which means it still requires Claude for the simplest judgment.

---

## Unique Contributions

- **B1 uniquely preserves**: Maximum flexibility for Claude to reinterpret raw results. Useful if task semantics change frequently.
- **B2 uniquely provides**: Structured artifacts without requiring Claude, while still deferring judgment. A good checkpoint format for debugging.
- **B3 uniquely enables**: Fully autonomous Phase 1 execution with zero Claude API calls. Solves the nested-claude deadlock completely for empirical tasks.

---

## Architectural Context

The existing codebase (`executor.py`, `process.py`, `models.py`) is built around the `ClaudeProcess` abstraction -- every task spawns a `claude --print` subprocess. The deadlock problem occurs because Phase 1 tasks themselves run `claude --print` commands, creating nested Claude processes.

All three variants solve the deadlock by bypassing `ClaudeProcess` for EXEMPT-tier empirical tasks. The question is how much of the task lifecycle Python absorbs.

Key architectural facts:
- `execute_phase_tasks()` already supports `_subprocess_factory` injection (line 356), providing a clean extension point for all three variants
- `TaskResult` already has fields for `status`, `exit_code`, `output_path`, `output_bytes` -- B3 can populate all of these
- `AggregatedPhaseReport` derives status from `TaskResult.status` -- if B3 sets status correctly, the entire reporting chain works without Claude
