---
deliverable: D-0044
task: T05.08
status: PASS
date: 2026-03-09
---

# Failure-State Semantics for Fidelity Status Values

## Overview

The pipeline produces one of four status values for each step and for the
overall pipeline run. These statuses are mutually exclusive and visually
distinguishable in pipeline output.

## Status Definitions

### PASS

| Property | Value |
|----------|-------|
| **Definition** | Step completed successfully and output passed all gate criteria |
| **Trigger Conditions** | Gate returns `(True, None)` for all checks |
| **Pipeline Output** | `[step-id] PASS` (green in terminal) |
| **User Action** | None required — proceed to next step |
| **Example** | `[extract] PASS — 13 frontmatter fields present, 127 lines` |

### FAIL

| Property | Value |
|----------|-------|
| **Definition** | Step completed but output did not pass gate criteria after all retries |
| **Trigger Conditions** | Gate returns `(False, reason)` and retry_limit exhausted |
| **Pipeline Output** | `[step-id] FAIL: <reason>` (red in terminal) |
| **User Action** | Investigate failure reason; fix upstream input; re-run with `--resume` |
| **Example** | `[merge] FAIL: Missing required frontmatter field 'adversarial'` |

### SKIPPED

| Property | Value |
|----------|-------|
| **Definition** | Step was not executed because its output already passes the gate |
| **Trigger Conditions** | `--resume` mode and existing output passes gate; OR `--no-validate` for post-pipeline validation |
| **Pipeline Output** | `[step-id] SKIP (output already passes gate)` |
| **User Action** | None required — previous output is still valid |
| **Example** | `[extract] SKIP (output already passes gate)` |

### DEGRADED

| Property | Value |
|----------|-------|
| **Definition** | Step produced partial results; some sub-components succeeded but not all |
| **Trigger Conditions** | Multi-agent validation where at least one agent succeeds but another fails or times out |
| **Pipeline Output** | `[validate] DEGRADED: agents failed: [haiku-qa]` |
| **User Action** | Review successful agent results; decide whether to accept partial validation or re-run failed agents |
| **Example** | `[validate] DEGRADED — opus-architect succeeded, haiku-qa timed out` |

## State Distinguishability

| Status | Color | Icon | Frontmatter Field |
|--------|-------|------|-------------------|
| PASS | Green | (none) | `validation_complete: true` |
| FAIL | Red | (none) | `validation_complete: false`, `tasklist_ready: false` |
| SKIPPED | Yellow | (none) | `validation_complete: skipped` |
| DEGRADED | Yellow | (none) | `validation_complete: false` (partial results preserved) |

## Implementation References

- Step status enum: `src/superclaude/cli/pipeline/models.py` (`StepStatus`)
- Gate checking: `src/superclaude/cli/pipeline/gates.py` (`gate_passed()`)
- Degraded report: `src/superclaude/cli/roadmap/validate_executor.py` (`_write_degraded_report()`)
- Skip logic: `src/superclaude/cli/roadmap/executor.py` (resume handling)
