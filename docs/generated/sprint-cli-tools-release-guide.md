# Sprint CLI Tools — Release Guide

This guide summarizes the sprint CLI tooling completed in this release, including:
- what each tool does,
- when to use it,
- how to run it,
- practical examples,
- and how it fits into the **spec → roadmap → tasklist → execution** workflow.

---

## 1) Release Summary (What was finalized)

### Core command surface
The `superclaude sprint` command group provides 5 subcommands:
1. `run`
2. `attach`
3. `status`
4. `logs`
5. `kill`

Implemented contract and options are defined in `src/superclaude/cli/sprint/commands.py`.

### Reliability and behavior updates included in this release
- **Canonical phase filename discovery** for 4 naming conventions (strict/near-match-safe)
- **Validation buckets** separated into `errors` and `warnings`
- **Executor timeout contract** hardened (`_timed_out` => `exit_code=124`)
- **Logging severity routing** made explicit (DEBUG/INFO/WARN/ERROR behavior)
- **Non-Unix process fallbacks** added (no unconditional `os.setpgrp`/`os.killpg`)
- **tmux graceful handling** improved when tmux is missing
- **tmux non-force kill escalation**: SIGTERM → wait → SIGKILL
- **CLI help contract hardening** (internal hidden options not exposed)
- **E2E brittleness removal** by patching `executor.shutil.which("claude")` in tests

---

## 2) Command Reference — When and How to Use

## `superclaude sprint run`

### What it does
Loads a tasklist index, discovers phases, validates phase files, and executes phases sequentially (usually in tmux unless `--no-tmux`).

Pre-flight behavior: execution fails fast if the `claude` binary is not in `PATH`.

### Use when
- You have a phase-based tasklist release package ready.
- You want deterministic, resumable execution over multiple phase files.
- You want strict task execution posture (`/sc:task-unified ... --compliance strict --strategy systematic`).

### Syntax
```bash
superclaude sprint run <index_path> [options]
```

### Key options
- `--start N` start from phase N
- `--end N` stop at phase N (default: last discovered)
- `--max-turns N` max turns per phase
- `--model MODEL` set Claude model
- `--dry-run` discovery/validation only; no execution
- `--no-tmux` run in foreground even if tmux is available
- `--permission-flag` permission mode passed to Claude CLI

### Examples
```bash
# Full execution (tmux auto if available)
superclaude sprint run .dev/releases/current/tasklist-index.md

# Resume from failed phase 4 through phase 8
superclaude sprint run .dev/releases/current/tasklist-index.md --start 4 --end 8

# Validate discovered phases only
superclaude sprint run .dev/releases/current/tasklist-index.md --dry-run

# Foreground execution for CI/local debugging
superclaude sprint run .dev/releases/current/tasklist-index.md --no-tmux
```

---

## `superclaude sprint attach`

### What it does
Attaches to a running `sc-sprint-*` tmux session.

### Use when
- A sprint is already running in tmux and you want live visibility.

### Example
```bash
superclaude sprint attach
```

---

## `superclaude sprint status`

### What it does
Intended to show current sprint status from execution logs.

### Current release note
`status` is wired but currently emits a placeholder message from `logging_.py` (`read_status_from_log`) and is not yet connected to active sprint state parsing.

### Example
```bash
superclaude sprint status
```

---

## `superclaude sprint logs`

### What it does
Intended to tail sprint log output.

### Current release note
`logs` is wired but currently a stub message in `logging_.py` (`tail_log`).

### Example
```bash
superclaude sprint logs -n 100
superclaude sprint logs -f
```

---

## `superclaude sprint kill`

### What it does
Stops running sprint tmux session.

### Modes
- `kill --force`: immediate tmux kill-session
- `kill` (non-force): escalation path
  1. SIGTERM to pane PID (or Ctrl-C fallback)
  2. wait 10 seconds
  3. SIGKILL if still alive
  4. kill tmux session

### Use when
- A sprint is stalled/hung or needs controlled stop.

### Examples
```bash
# Graceful stop with escalation
superclaude sprint kill

# Immediate stop
superclaude sprint kill --force
```

---

## 3) End-to-End Workflow: Spec → Roadmap → Tasklist → Task Execution

This sprint CLI is the execution layer for your release pipeline.

## Stage A: Spec (requirements source)
Create/maintain release spec with acceptance criteria and expected outputs.

## Stage B: Roadmap (phase planning)
Translate spec into phases (delivery order, dependencies, quality gates).

## Stage C: Tasklist Index + Phase Files (execution plan)
Prepare:
- one `tasklist-index.md`
- one or more canonical phase files

Canonical file name patterns recognized by discovery:
1. `phase-<N>-tasklist.md`
2. `p<N>-tasklist.md`
3. `phase_<N>_tasklist.md`
4. `tasklist-p<N>.md`

Near-match forms are intentionally rejected to avoid accidental pickup.

## Stage D: Sprint execution
Run:
```bash
superclaude sprint run <tasklist-index.md>
```

For each phase, sprint runtime:
1. launches fresh Claude process,
2. monitors output and updates TUI,
3. enforces timeout/interrupt handling,
4. parses phase result (`EXIT_RECOMMENDATION`/status),
5. records dual logs (JSONL + Markdown),
6. continues or halts.

## Stage E: Resume on halt
If halted, use generated resume command from summary (`--start <halt_phase>`).

---

## 4) Behind the Scenes: What the Python sprint runtime actually executes

This section explains what happens inside the Python runtime so users understand exactly what is being launched.

### 4.1 `superclaude sprint run` call path
When you run:

```bash
superclaude sprint run <tasklist-index.md> [flags]
```

the CLI flow is:
1. `commands.py::run()` parses options.
2. `config.py::load_sprint_config()` discovers phases and validates range/files.
3. If `--dry-run`: prints discovered plan and exits.
4. If tmux is available and `--no-tmux` is not set: `tmux.py::launch_in_tmux()`.
5. Otherwise: `executor.py::execute_sprint()` in foreground.

### 4.2 What command is run for each phase
For each phase, the runtime spawns a fresh Claude CLI process from `process.py::build_command()`.

Effective command shape:

```bash
claude \
  --print \
  <permission-flag> \
  --no-session-persistence \
  --max-turns <N> \
  --output-format text \
  -p "<generated /sc:task-unified prompt>" \
  [--model <model-if-provided>]
```

Important details:
- `--no-session-persistence` ensures phase isolation.
- `CLAUDECODE=""` is injected into child env to avoid nested session detection behavior.
- stdout/stderr are redirected to per-phase files in `results/`.

### 4.3 What prompt is sent to Claude
The sprint runtime generates a structured prompt (from `process.py::build_prompt()`) that begins with:

```text
/sc:task-unified Execute all tasks in @<phase-file> --compliance strict --strategy systematic
```

It then includes execution rules and completion protocol (including writing phase result file and explicit `EXIT_RECOMMENDATION`).

### 4.3.1 How the prompt builder works (detailed)
`build_prompt()` is deterministic and phase-aware. It composes a single multiline prompt from runtime config + phase metadata.

Inputs used by the builder:
- `phase.number` for task-ID format expectations (`T{phase}XX.*`)
- `phase.file` for `@<phase-file>` inclusion
- `config.result_file(phase)` for the required completion report destination

Prompt structure emitted by the builder:
1. **Command header**
   - `/sc:task-unified ... --compliance strict --strategy systematic`
2. **Execution Rules** block
   - task ordering expectations
   - tier-specific verification expectations
   - halt/continue behavior semantics
3. **Completion Protocol** block
   - exact report destination path
   - required report schema items (frontmatter, status table, evidence, files changed)
   - explicit required literal token:
     - `EXIT_RECOMMENDATION: CONTINUE` or
     - `EXIT_RECOMMENDATION: HALT`
4. **Important** block
   - phase-context boundaries (do current phase only)
   - no re-execution of prior-phase work

Why this matters:
- Keeps each spawned Claude process aligned to the same contract.
- Produces machine-parseable completion artifacts for `_determine_phase_status()`.
- Reduces ambiguity by embedding both policy and output contract in the prompt itself.

Operational consequence:
- If a phase agent does not emit the required recommendation token or valid status hints, executor falls back to `PASS_NO_SIGNAL`, `PASS_NO_REPORT`, or `ERROR` paths based on available artifacts.

### 4.4 tmux mode: what is launched
If tmux mode is selected, runtime creates a deterministic session name (`sc-sprint-<hash>`) and launches a foreground sprint command inside tmux.

Foreground command built by runtime:

```bash
superclaude sprint run <index> --no-tmux --start <N> --max-turns <N> --permission-flag <flag> [--end <N>] [--model <M>] [--tmux-session-name <name>]
```

Then it:
- splits a bottom pane to tail phase output,
- keeps top pane for TUI,
- attaches user to the tmux session.

### 4.5 Stop/kill behavior internals
`superclaude sprint kill` (non-force) performs escalation:
1. target pane PID lookup,
2. SIGTERM,
3. wait 10s,
4. SIGKILL if still alive,
5. kill tmux session.

If pane PID is unavailable, fallback sends Ctrl-C to pane before cleanup.

---

## 5) Runtime Behavior Details (Important)

## Phase status semantics
Phase statuses include:
- success: `pass`, `pass_no_signal`, `pass_no_report`
- failures: `halt`, `timeout`, `error`

Decision highlights:
- `exit_code == 124` => `timeout`
- non-zero exit (except 124 handling) => `error`
- `EXIT_RECOMMENDATION: HALT` wins over `CONTINUE` if both appear
- `status: PARTIAL` => `halt`

## Logging severity routing
- **DEBUG** (`pass_no_signal`): JSONL only
- **INFO** (`pass`, `pass_no_report`): screen + JSONL (+ markdown row)
- **WARN** (`halt`, `timeout`): highlighted stderr + JSONL (+ markdown row)
- **ERROR** (`error`): highlighted stderr + bell + JSONL (+ markdown row)

## Process portability
- Unix process-group operations are used when available.
- Fallback path uses process-level `terminate()/kill()` on non-Unix environments.

## tmux resilience
- If tmux is not installed, discovery returns no session gracefully.
- Non-force kill follows escalation behavior rather than immediate hard kill.

---

## 6) Practical Use Cases

## Use case 1: Normal release execution
```bash
superclaude sprint run .dev/releases/current/tasklist-index.md
```
Best for long-running multi-phase execution with reconnect support via tmux.

## Use case 2: Safe preflight before execution
```bash
superclaude sprint run .dev/releases/current/tasklist-index.md --dry-run
```
Confirms discovery/range before consuming runtime.

## Use case 3: Recover from mid-release halt
```bash
superclaude sprint run .dev/releases/current/tasklist-index.md --start 5
```
Resume from the halt phase indicated in execution summary.

## Use case 4: CI/ephemeral shell environment
```bash
superclaude sprint run .dev/releases/current/tasklist-index.md --no-tmux
```
Avoids tmux dependency in constrained runners.

---

## 7) Authoring Checklist for Tasklist Packages

Before running sprint:
- [ ] index file exists and is readable
- [ ] phase files follow one of the 4 canonical names
- [ ] start/end range maps to at least one active phase
- [ ] each phase has clear task IDs and acceptance criteria
- [ ] release directory writable (for `results/` and execution logs)

After run:
- [ ] inspect `execution-log.md` summary
- [ ] inspect `execution-log.jsonl` for machine-readable telemetry
- [ ] use generated resume command if outcome halted

---

## 8) Quick Command Cheat Sheet

```bash
# Start sprint
superclaude sprint run <index>

# Start specific range
superclaude sprint run <index> --start 2 --end 6

# Dry-run only
superclaude sprint run <index> --dry-run

# Force foreground
superclaude sprint run <index> --no-tmux

# Attach to running tmux sprint
superclaude sprint attach

# Stop sprint gracefully (with escalation)
superclaude sprint kill

# Stop sprint immediately
superclaude sprint kill --force
```

---

## 9) Notes for the Spec→Roadmap→Tasklist pipeline owners

- Keep roadmap phases aligned to actual canonical file names to guarantee deterministic discovery.
- Treat `status` and `logs` subcommands as placeholders in this release (wired, not fully implemented).
- Prefer explicit acceptance evidence in phase outputs (`EXIT_RECOMMENDATION`, status frontmatter, modified files list) to maximize executor determinism.
- Use `--dry-run` as an automated gate between roadmap generation and execution kickoff.
