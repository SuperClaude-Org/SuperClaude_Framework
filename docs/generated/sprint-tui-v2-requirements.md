# Sprint TUI v2 — Requirements Specification

**Status**: Ready for implementation
**Scope**: 5 existing files + 2 new files
**Branch**: Feature branch off `v2.05-sprint-cli-specifications`

---

## Summary

Visual UX refactor of the Sprint TUI to surface richer real-time information from the Claude stream-json output. Seven feature areas: activity stream, enhanced phase table, task-level progress, conditional error panel, LLM context lines, post-phase summaries with tmux integration, and release retrospective. Terminal summary panels enhanced with aggregate stats.

## Current State

The TUI shows: header (name + elapsed), phase table (5 columns), single progress bar (phase-level), active panel (file, status, last task/tool, output size, files changed), and terminal panel (result + resume command).

The stream-json output contains much richer data that is parsed but not displayed: turn counts, token usage, tool call details, assistant text content, error signals, and model metadata.

## Target Layout — Active Sprint (~25 lines)

```
+=========== SUPERCLAUDE SPRINT RUNNER == v2.07-tasklist-v1 ===========+
|                                                                       |
|  Elapsed: 12m 34s    Model: claude-opus-4-6    Turns: 23/50          |
|                                                                       |
|  #  Phase                            Status   Duration  Turns  Output |
|  1  Foundation & Architecture        PASS     16s       7      10 KB  |
|  2  Command & Skill Implementation   RUNNING  2m 34s    23     148 KB |
|  3  Integration & Tooling            pending  -         -      -      |
|  4  Validation & Acceptance          pending  -         -      -      |
|                                                                       |
|  Phases ======-------- 25% 1/4    Tasks ==========------ 51% 20/39   |
|                                                                       |
|  +---- ACTIVE: phase-2-tasklist.md ----------------------------------+|
|  | Status:  RUNNING -- active (+312.5 B/s)                           ||
|  | Task:    T02.08   Tool: Bash   Files: 3                           ||
|  |                                                                    ||
|  | Prompt:  Execute all tasks in phase-2-tasklist.md --compliance...  ||
|  | Agent:   Good -- the directory doesn't exist yet, and there's no...||
|  |                                                                    ||
|  |  02:53:42  Grep  pyproject.toml (packages config)                  ||
|  |  02:53:43  Write sc-tasklist-protocol/SKILL.md                     ||
|  |  02:53:46  Todo  updated 5 tasks                                   ||
|  +--------------------------------------------------------------------+|
|                                                                       |
|  +---- ERRORS (2) ---------------------------------------------------+|
|  |  T02.04  Bash  exit 1 -- "mkdir: permission denied"               ||
|  |  T02.07  STRICT verification failed                               ||
|  +--------------------------------------------------------------------+|
+-----------------------------------------------------------------------+
```

## Target Layout — Sprint Complete

```
+=========== SUPERCLAUDE SPRINT RUNNER == v2.07-tasklist-v1 ===========+
|                                                                       |
|  #  Phase                            Status   Duration  Turns  Output |
|  1  Foundation & Architecture        PASS     16s       7      10 KB  |
|  2  Command & Skill Implementation   PASS     8m 12s    47     312 KB |
|  3  Integration & Tooling            PASS     4m 03s    28     198 KB |
|  4  Validation & Acceptance          PASS     6m 41s    35     267 KB |
|                                                                       |
|  Phases ================ 100% 4/4  Tasks ================ 100% 39/39 |
|                                                                       |
|  +---- SPRINT COMPLETE ----------------------------------------------+|
|  |                                                                    ||
|  |  Result:     ALL PHASES PASSED                                     ||
|  |  Duration:   19m 12s                                               ||
|  |  Turns:      117 total (avg 29/phase)                              ||
|  |  Tokens:     482K in / 38K out                                     ||
|  |  Output:     787 KB across 4 phases                                ||
|  |  Files:      14 created/modified                                   ||
|  |                                                                    ||
|  |  Log:  .dev/releases/.../tasklist/execution-log.md                 ||
|  |                                                                    ||
|  +--------------------------------------------------------------------+|
+-----------------------------------------------------------------------+
```

## Target Layout — Sprint Halted

```
+=========== SUPERCLAUDE SPRINT RUNNER == v2.07-tasklist-v1 ===========+
|                                                                       |
|  #  Phase                            Status   Duration  Turns  Output |
|  1  Foundation & Architecture        PASS     16s       7      10 KB  |
|  2  Command & Skill Implementation   HALT     8m 28s    54     312 KB |
|  3  Integration & Tooling            skipped  -         -      -      |
|  4  Validation & Acceptance          skipped  -         -      -      |
|                                                                       |
|  Phases ========-------- 25% 1/4  Tasks ==========------ 36% 14/39   |
|                                                                       |
|  +---- SPRINT HALTED -- Phase 2 -------------------------------------+|
|  |                                                                    ||
|  |  Result:     HALTED at Phase 2 (STRICT failure)                    ||
|  |  Duration:   8m 28s                                                ||
|  |  Completed:  1/4 phases, 14/39 tasks                               ||
|  |  Turns:      54 total                                              ||
|  |  Tokens:     231K in / 19K out                                     ||
|  |  Last task:  T02.07 -- STRICT tier verification failed             ||
|  |  Files:      6 created/modified                                    ||
|  |                                                                    ||
|  |  Errors:                                                           ||
|  |    T02.04  Bash  exit 1 -- "mkdir: permission denied"              ||
|  |    T02.07  STRICT verification failed                              ||
|  |                                                                    ||
|  |  Resume:  superclaude sprint run .../tasklist-index.md --start 2   ||
|  |  Log:     .dev/releases/.../tasklist/execution-log.md              ||
|  |                                                                    ||
|  +--------------------------------------------------------------------+|
+-----------------------------------------------------------------------+
```

---

## Feature Specifications

### F1: Activity Stream (3 lines, scrolling)

**Location**: Bottom of the active phase panel, no sub-border — just indented timestamp lines.

**Behavior**:
- Shows last 3 tool calls with `HH:MM:SS  ToolName  condensed_input`
- Tool names shortened: `TodoWrite` -> `Todo`, `ToolSearch` -> `Search`, `MultiEdit` -> `Multi`
- Tool inputs truncated to fit available width: file paths shortened (basename only for long paths), arguments clipped with `...`
- When no tool call for >2 seconds, insert a `[thinking... Ns]` line that updates in place
- New events push old ones off the top (FIFO ring buffer of 3)

**Data source**: `tool_use` events from stream-json. Extract `event.content[type=tool_use].name` and first argument from `.input`.

**MonitorState additions**:
```python
activity_log: list[tuple[float, str, str]]  # (timestamp, tool_name, description) — max 3
```

### F2: Enhanced Phase Table

**Changes to existing table**:
- Add column: **Turns** (width=6, right-aligned) — count of assistant message events for that phase
- Add column: **Output** (width=8, right-aligned) — human-readable output size
- Keep existing columns: #, Phase, Status, Duration
- Remove: Tasks column (task info moves to active panel)

**Data for completed phases**: Stored in `PhaseResult` (new fields: `turns`, `output_bytes` already exists).

**Data for running phase**: Read from `MonitorState.turns` and `MonitorState.output_size_display`.

### F3: Task-Level Progress Bar (same line as phase bar)

**Layout**: Single line with both bars, compact width:
```
Phases ======-------- 25% 1/4    Tasks ==========------ 51% 20/39
```

**Phase bar**: Uses existing `phases_passed / len(active_phases)`.

**Task bar**:
- Total tasks: Pre-scanned from phase files on sprint start. Count all `T\d{2}\.\d{2}` patterns across all active phase files. Store in `SprintConfig.total_tasks`.
- Completed tasks: Sum of completed tasks from finished phases (count tasks per phase file) + estimate for current phase from `MonitorState.last_task_id` (parse `TT` suffix as ordinal position).
- Stored as `SprintResult.tasks_completed_estimate` (computed property).

**Rich implementation**: Two `Progress` widgets side by side won't work cleanly. Instead, render as a single `Text` line with manual bar characters using Rich markup:
```python
def _build_dual_progress(self) -> Text:
    # Build two compact bars as a single Text line
    phase_bar = self._mini_bar(done_phases, total_phases, width=14, label="Phases")
    task_bar = self._mini_bar(done_tasks, total_tasks, width=14, label="Tasks")
    return Text.from_markup(f"  {phase_bar}    {task_bar}")
```

Use block characters: `\u2588` (full block) for filled, `\u2591` (light shade) for empty.

### F4: Conditional Error Panel

**Visibility**: Hidden when error count is 0. Appears below the active panel.

**Content**: Each line shows `TaskID  ToolName  error_message_truncated`.
- Max 5 errors displayed
- If more than 5, show `(+N more)` on last line
- Task ID extracted from context if available, otherwise `-`

**Data source**: `tool_result` events where content indicates error (`is_error` field in stream-json, or `type: "tool_result"` with error content). Also catch `exit_code != 0` from Bash tool results.

**MonitorState additions**:
```python
errors: list[tuple[str, str, str]]  # (task_id, tool_name, message) — max 10, display 5
```

**Panel styling**: Red border, title includes count: `ERRORS (N)`.

### F5: LLM Context Lines

**Location**: Inside the active panel, between the Task/Tool line and the activity stream.

**Two lines**:
- `Prompt:  <first ~60 chars of the phase prompt>...` — Static per phase, from `ClaudeProcess.build_prompt()`. Truncated to panel width minus label.
- `Agent:   <first ~60 chars of last assistant text>...` — Updates on each `assistant` event with `content[type=text].text`. Truncated to panel width minus label.

**MonitorState additions**:
```python
last_assistant_text: str  # last ~80 chars of assistant text output, truncated
```

**Static prompt**: Stored in `SprintConfig` or passed to TUI on phase start. The TUI already receives the `Phase` object; add a `prompt_preview: str` field to `Phase` or compute from config.

### F6: Enhanced Terminal Summary Panels

**Success panel** — title in border: `SPRINT COMPLETE`
- Result, Duration, Turns (total + avg/phase), Tokens (in/out), Output (total across phases), Files (total changed), Log path

**Halt panel** — title in border: `SPRINT HALTED -- Phase N`
- Result, Duration, Completed (phases + tasks), Turns, Tokens, Last task + failure reason, Files, Errors (folded in, same format as error panel), Resume command, Log path

**Data sources**: All aggregate from `SprintResult` properties. New properties needed:
```python
@property
def total_turns(self) -> int
@property
def total_tokens_in(self) -> int
@property
def total_tokens_out(self) -> int
@property
def total_output_bytes(self) -> int
@property
def total_files_changed(self) -> int
```

### F7: Sprint Name in Outer Panel Title

**Current**: `[bold]SUPERCLAUDE SPRINT RUNNER[/]`
**New**: `[bold]SUPERCLAUDE SPRINT RUNNER[/] [dim]== {release_name}[/]`

Where `release_name` = `config.index_path.parent.name` (already computed in `_build_header()`).

Rich `Panel(title=...)` auto-adjusts border padding around the title text.

---

## Feature Specifications — Phase Summary & Retrospective

### F8: Post-Phase Summary (Hybrid: Programmatic + Haiku Narrative)

**Purpose**: After each phase completes, generate a structured summary of what was accomplished, what files were changed, what validations ran, and what the agent's reasoning was. The user should never have to read raw output files to understand what happened.

**Execution model**:
```
Phase 1 completes
  |
  +---> Phase 2 starts immediately (no delay)
  |
  +---> SummaryWorker thread spawns in background
           |
           +---> Step 1: Programmatic parse of phase-N-output.txt (instant)
           |       Extract: tasks, tool calls, files changed, errors,
           |       validation commands, assistant reasoning snippets
           |
           +---> Step 2: Haiku narrative call (10-30s)
           |       claude --print --model claude-haiku-4-5 -p "<structured data + snippets>"
           |       Produces 3-5 sentence narrative summary
           |
           +---> Step 3: Write results/phase-N-summary.md
           |
           +---> Step 4: Update tmux summary pane (or TUI notification)
```

**Summary output format** (`results/phase-N-summary.md`):

```markdown
# Phase 1 Summary -- Foundation & Architecture Setup

**Duration**: 16s | **Turns**: 7 | **Tokens**: 48K in / 3K out | **Status**: PASS

## Tasks

| Task | Tier | Status | Description |
|------|------|--------|-------------|
| T01.01 | STANDARD | DONE | Created sc-tasklist-protocol/ directory tree |
| T01.02 | LIGHT | DONE | Created empty __init__.py |
| T01.03 | STANDARD | DONE | Created placeholder tasklist.md with YAML frontmatter |
| T01.04 | STANDARD | DONE | Created placeholder SKILL.md with valid frontmatter |

## Files Created/Modified

| Action | Path |
|--------|------|
| mkdir | src/superclaude/skills/sc-tasklist-protocol/ |
| mkdir | src/superclaude/skills/sc-tasklist-protocol/rules/ |
| mkdir | src/superclaude/skills/sc-tasklist-protocol/templates/ |
| new | src/superclaude/skills/sc-tasklist-protocol/__init__.py |
| new | src/superclaude/commands/tasklist.md |
| new | src/superclaude/skills/sc-tasklist-protocol/SKILL.md |

## Validation Evidence

| Task | Method | Command / Check | Result |
|------|--------|-----------------|--------|
| T01.01 | Bash | `ls -la src/superclaude/skills/sc-tasklist-protocol/` | Dirs exist |
| T01.03 | Read | Verified YAML frontmatter fields present | 8/8 fields |
| T01.04 | Read | Verified SKILL.md frontmatter matches spec | name ends in -protocol |

## Agent Reasoning (Excerpts)

> "Checked existing skills for frontmatter patterns before creating new files"
> "Used sc-task-unified-protocol/SKILL.md as reference template for format"
> "Verified pyproject.toml package discovery won't be affected by new __init__.py"

## Narrative

Phase 1 scaffolded the sc-tasklist-protocol skill directory and placeholder
files. All 4 tasks completed without errors. The agent followed existing
patterns from sc-task-unified-protocol for frontmatter formatting. No
STRICT-tier tasks in this phase, so no formal verification was required.
All directories and files confirmed to exist via direct filesystem checks.
```

**Programmatic extraction** (Step 1 — the heavy lifting):

The programmatic parser reads `phase-N-output.txt` (NDJSON) and extracts:

1. **Task status table**: Parse TodoWrite events to get task list and status changes. Match `T\d{2}\.\d{2}` patterns in assistant text to track which task is being worked on. Map final TodoWrite state to DONE/FAIL/SKIP.

2. **Files changed**: Extract from Write, Edit, MultiEdit tool_use events (input contains file paths). Extract from Bash events containing `mkdir`, `touch`, `cp`, `mv`. Deduplicate and classify as new/modified/mkdir.

3. **Validation evidence**: Identify tool calls that appear to be verification (Read after Write to the same file, Bash commands containing `ls`, `test`, `diff`, `grep` on recently-created files, assertions in assistant text like "confirmed", "verified", "passes"). Extract the command and a condensed result.

4. **Agent reasoning excerpts**: Collect `assistant` text content blocks that contain reasoning signals: sentences with "because", "decided", "checked", "following", "pattern", "reference", "verified". Take the top 3-5 most informative snippets, each truncated to ~80 chars.

5. **Errors**: Any tool results with `is_error: true`, Bash exit codes != 0, assistant text containing "error", "failed", "issue".

6. **Aggregate stats**: Duration, turns, tokens (already in PhaseResult).

**Haiku narrative** (Step 2 — lightweight synthesis):

Prompt template for the Haiku call:
```
Summarize this phase execution in 3-5 sentences. Focus on: what was built,
key decisions made, validation coverage, and any concerns.

Phase: {phase_name}
Tasks: {task_count} total, {passed} passed, {failed} failed
Files: {file_list}
Validation: {validation_summary}
Agent excerpts: {reasoning_excerpts}
Errors: {error_list or "None"}
```

The Haiku call uses the same `build_env()` from ClaudeProcess (strips CLAUDECODE) and runs via subprocess with `--model claude-haiku-4-5 --max-turns 1`.

**Failure mode**: If the Haiku call fails or times out (15s timeout), the summary is written without the narrative section. The structured data is always available.

### F9: Tmux Summary Pane

**Layout change**: When running in tmux, the session now has 3 panes:

```
+---------------------------------------------------+
|  SUPERCLAUDE SPRINT RUNNER (Rich TUI dashboard)   |  <-- 50%
|  Phase table, progress bars, active panel...      |
+---------------------------------------------------+
|  Phase 1 Summary                                  |  <-- 25% (summary pane)
|  Tasks: 4/4 DONE | Files: 5 new                  |
|  Validation: 3 checks passed                      |
|  "Scaffolded directory tree using existing..."    |
+---------------------------------------------------+
|  tail -f phase-2-output.txt                       |  <-- 25% (output tail)
+---------------------------------------------------+
```

**Pane management**:
- On sprint start: create 3-pane layout (top 50% TUI, middle 25% summary, bottom 25% tail)
- Summary pane initially shows `Waiting for first phase to complete...`
- When `phase-N-summary.md` is written, pipe its content to the summary pane via `tmux send-keys` or by running `cat results/phase-N-summary.md` in that pane
- User can zoom the summary pane with `Ctrl-B z` for full-screen reading, then `Ctrl-B z` to return

**Pane update mechanism**:
```python
def update_summary_pane(tmux_session_name: str, summary_path: Path):
    """Replace summary pane content with latest phase summary."""
    quoted = shlex.quote(str(summary_path))
    # Kill current content in summary pane, display new summary
    subprocess.run(
        ["tmux", "send-keys", "-t", f"{tmux_session_name}:0.1", "C-c"],
        check=False,
    )
    subprocess.run(
        ["tmux", "send-keys", "-t", f"{tmux_session_name}:0.1",
         f"clear && cat {quoted} && echo '\\n--- Press Ctrl-B z to zoom ---'\n"],
        check=False,
    )
```

**--no-tmux fallback**: Summary is still written to `results/phase-N-summary.md`. The TUI shows a notification line in the header area:
```
Phase 1 summary ready: results/phase-1-summary.md
```
This notification persists until the next phase completes (then replaced by the new notification).

### F10: Release Retrospective

**Trigger**: After the final phase completes (or after halt), before the terminal panel is displayed.

**Execution model**:
```
Final phase completes
  |
  +---> Retrospective generator runs (not in parallel -- blocking before terminal display)
           |
           +---> Step 1: Read all phase-N-summary.md files (instant)
           |
           +---> Step 2: Programmatic aggregation
           |       Total stats, combined file list, combined validation matrix,
           |       combined error list, cross-phase patterns
           |
           +---> Step 3: Haiku narrative call (10-30s)
           |       Synthesize phase summaries into release-level narrative
           |
           +---> Step 4: Write results/release-retrospective.md
           |
           +---> Step 5: Display in terminal panel and/or summary pane
```

**Retrospective output format** (`results/release-retrospective.md`):

```markdown
# Release Retrospective -- /sc:tasklist Command + Skill v1.0

**Duration**: 19m 12s | **Phases**: 4/4 passed | **Tasks**: 39/39 completed
**Turns**: 117 total | **Tokens**: 482K in / 38K out | **Files**: 14 created/modified

## Phase Progression

| Phase | Name | Duration | Tasks | Status | Key Outcome |
|-------|------|----------|-------|--------|-------------|
| 1 | Foundation & Architecture | 16s | 4/4 | PASS | Directory tree + placeholders |
| 2 | Command & Skill Implementation | 8m 12s | 16/16 | PASS | Full command + skill content |
| 3 | Integration & Tooling | 4m 03s | 9/9 | PASS | Lint checks + sync verified |
| 4 | Validation & Acceptance | 6m 41s | 10/10 | PASS | All SC criteria passed |

## All Files Created/Modified

| Phase | Action | Path |
|-------|--------|------|
| 1 | new | src/superclaude/skills/sc-tasklist-protocol/__init__.py |
| 1 | new | src/superclaude/commands/tasklist.md |
| 1 | new | src/superclaude/skills/sc-tasklist-protocol/SKILL.md |
| 2 | modified | src/superclaude/commands/tasklist.md |
| 2 | modified | src/superclaude/skills/sc-tasklist-protocol/SKILL.md |
| 2 | new | src/superclaude/skills/sc-tasklist-protocol/rules/tier-classification.md |
| ... | ... | ... |

## Validation Evidence Matrix

| Task | Tier | Method | Validation Command | Result |
|------|------|--------|--------------------|--------|
| T01.01 | STANDARD | Direct test | `ls -la .../sc-tasklist-protocol/` | PASS |
| T01.03 | STANDARD | Direct test | Read + YAML parse | PASS |
| T02.04 | STRICT | Sub-agent | Quality-engineer verification | PASS |
| T02.10 | STRICT | Sub-agent | v3.0 content parity check | PASS |
| T03.06 | STRICT | Sub-agent | 6 lint checks, zero errors | PASS |
| T04.01 | STRICT | Sub-agent | Output bundle validation | PASS |
| ... | ... | ... | ... | ... |

**Validation Coverage**: 39/39 tasks verified (6 STRICT with sub-agent, 28 STANDARD with direct test, 4 LIGHT with sanity check, 1 EXEMPT skipped)

## Errors Encountered

None.

## Release Narrative

This sprint packaged the existing Tasklist Generator v3.0 as a proper SuperClaude
command/skill pair (tasklist.md + sc-tasklist-protocol/). All 39 tasks across 4
phases completed without errors. Phase 1 scaffolded the directory structure. Phase 2
was the heaviest phase (8m) implementing the full command frontmatter, SKILL.md body,
rule files, and templates. Phase 3 verified integration with the build system (sync,
lint, install). Phase 4 ran acceptance tests confirming functional parity with v3.0
and Sprint CLI compatibility. All 6 STRICT-tier tasks passed sub-agent verification.
The release is ready for merge.
```

**Programmatic aggregation** (Step 2):

Reads each `phase-N-summary.md`, extracts the structured sections (tasks table, files table, validation table, errors), and combines them. Cross-phase analysis:
- Files modified in multiple phases (track evolution)
- Error patterns across phases
- Validation coverage gaps (tasks with no validation evidence)
- Phase-over-phase timing trends

**Haiku narrative** (Step 3):

Prompt template:
```
Write a 4-8 sentence release retrospective based on these phase summaries.
Cover: what was built overall, heaviest phase and why, validation coverage,
errors encountered (if any), and release readiness assessment.

Sprint: {sprint_name}
Outcome: {outcome}
Phase summaries:
{concatenated_phase_narrative_sections}
Stats: {aggregate_stats}
Errors: {all_errors or "None"}
```

**Integration with terminal panel**: The retrospective file path is shown in the terminal summary panel. In tmux mode, the summary pane displays the retrospective after the final phase summary.

---

## Summary Worker Architecture

### New module: `summarizer.py`

```python
"""Phase summarizer -- structured extraction + Haiku narrative generation."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .models import MonitorState, Phase, PhaseResult, SprintConfig


@dataclass
class PhaseSummary:
    """Structured summary of a completed phase."""

    phase: Phase
    phase_result: PhaseResult

    # Structured extraction (programmatic)
    tasks: list[dict] = field(default_factory=list)         # [{id, tier, status, description}]
    files_changed: list[dict] = field(default_factory=list) # [{action, path}]
    validations: list[dict] = field(default_factory=list)   # [{task, method, command, result}]
    reasoning_excerpts: list[str] = field(default_factory=list)  # top 3-5 snippets
    errors: list[dict] = field(default_factory=list)        # [{task, tool, message}]

    # Narrative (Haiku-generated, may be empty if call fails)
    narrative: str = ""

    @property
    def summary_path(self) -> Path:
        """Where this summary will be written."""
        return self.phase_result.phase.file.parent / "results" / f"phase-{self.phase.number}-summary.md"


class PhaseSummarizer:
    """Extracts structured data from phase output and generates narrative."""

    def __init__(self, config: SprintConfig):
        self.config = config

    def summarize(self, phase: Phase, phase_result: PhaseResult) -> PhaseSummary:
        """Full summarization pipeline: parse + narrate + write."""
        summary = PhaseSummary(phase=phase, phase_result=phase_result)

        # Step 1: Programmatic extraction
        output_file = self.config.output_file(phase)
        if output_file.exists():
            self._extract_structured(output_file, summary)

        # Step 2: Haiku narrative (best-effort)
        self._generate_narrative(summary)

        # Step 3: Write to file
        self._write_summary(summary)

        return summary

    def _extract_structured(self, output_file: Path, summary: PhaseSummary):
        """Parse NDJSON output for tasks, files, validations, reasoning."""
        # ... extraction logic ...

    def _generate_narrative(self, summary: PhaseSummary):
        """Call Haiku for 3-5 sentence narrative summary."""
        if shutil.which("claude") is None:
            return

        prompt = self._build_narrative_prompt(summary)
        env = os.environ.copy()
        env.pop("CLAUDECODE", None)
        env.pop("CLAUDE_CODE_ENTRYPOINT", None)

        try:
            result = subprocess.run(
                [
                    "claude", "--print",
                    "--model", "claude-haiku-4-5",
                    "--max-turns", "1",
                    "--dangerously-skip-permissions",
                    "-p", prompt,
                ],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
                stdin=subprocess.DEVNULL,
            )
            if result.returncode == 0 and result.stdout.strip():
                summary.narrative = result.stdout.strip()
        except (subprocess.TimeoutExpired, OSError):
            pass  # Summary written without narrative

    def _build_narrative_prompt(self, summary: PhaseSummary) -> str:
        """Build the prompt for Haiku narrative generation."""
        # ... template with structured data ...

    def _write_summary(self, summary: PhaseSummary):
        """Write phase-N-summary.md."""
        # ... markdown generation from PhaseSummary fields ...
```

### New module: `retrospective.py`

```python
"""Release retrospective -- aggregates phase summaries into release-level synthesis."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .models import SprintConfig, SprintResult


@dataclass
class ReleaseRetrospective:
    """Aggregated release-level summary."""

    sprint_result: SprintResult

    # Aggregated from phase summaries
    phase_outcomes: list[dict] = field(default_factory=list)  # [{phase, name, duration, tasks, status, key_outcome}]
    all_files: list[dict] = field(default_factory=list)       # [{phase, action, path}]
    validation_matrix: list[dict] = field(default_factory=list)  # [{task, tier, method, command, result}]
    all_errors: list[dict] = field(default_factory=list)
    validation_coverage: str = ""  # e.g. "39/39 verified (6 STRICT, 28 STANDARD, ...)"

    # Narrative
    narrative: str = ""


class RetrospectiveGenerator:
    """Generates release-level retrospective from phase summaries."""

    def __init__(self, config: SprintConfig):
        self.config = config

    def generate(self, sprint_result: SprintResult) -> ReleaseRetrospective:
        """Full retrospective pipeline: aggregate + narrate + write."""
        retro = ReleaseRetrospective(sprint_result=sprint_result)

        # Step 1: Read all phase summaries
        phase_summaries = self._read_phase_summaries()

        # Step 2: Programmatic aggregation
        self._aggregate(phase_summaries, retro)

        # Step 3: Haiku narrative
        self._generate_narrative(retro)

        # Step 4: Write
        self._write_retrospective(retro)

        return retro

    def _read_phase_summaries(self) -> list[str]:
        """Read all phase-N-summary.md files."""
        # ...

    def _aggregate(self, summaries: list[str], retro: ReleaseRetrospective):
        """Combine phase summaries into release-level data."""
        # ...

    def _generate_narrative(self, retro: ReleaseRetrospective):
        """Call Haiku for 4-8 sentence release narrative."""
        # Same pattern as PhaseSummarizer._generate_narrative()

    def _write_retrospective(self, retro: ReleaseRetrospective):
        """Write results/release-retrospective.md."""
        output_path = self.config.results_dir / "release-retrospective.md"
        # ... markdown generation ...
```

### SummaryWorker in `executor.py`

```python
import threading
from .summarizer import PhaseSummarizer

class SummaryWorker:
    """Background thread pool for phase summary generation."""

    def __init__(self, config: SprintConfig):
        self.config = config
        self.summarizer = PhaseSummarizer(config)
        self._threads: list[threading.Thread] = []
        self._summaries: dict[int, PhaseSummary] = {}  # phase_number -> summary

    def submit(self, phase: Phase, phase_result: PhaseResult):
        """Submit a phase for background summarization."""
        t = threading.Thread(
            target=self._run,
            args=(phase, phase_result),
            daemon=True,
            name=f"summary-phase-{phase.number}",
        )
        t.start()
        self._threads.append(t)

    def _run(self, phase: Phase, phase_result: PhaseResult):
        """Run summarization in background thread."""
        try:
            summary = self.summarizer.summarize(phase, phase_result)
            self._summaries[phase.number] = summary
            # Notify tmux pane if applicable
            if self.config.tmux_session_name:
                update_summary_pane(self.config.tmux_session_name, summary.summary_path)
        except Exception:
            pass  # Summary failure must never affect sprint execution

    def wait_all(self, timeout: float = 60):
        """Wait for all pending summaries to complete."""
        for t in self._threads:
            t.join(timeout=timeout)

    @property
    def latest_summary_path(self) -> Path | None:
        """Path to the most recently completed summary, for TUI notification."""
        if self._summaries:
            latest = max(self._summaries.keys())
            return self._summaries[latest].summary_path
        return None
```

Integration in `execute_sprint()`:
```python
summary_worker = SummaryWorker(config)

# After each phase completes:
summary_worker.submit(phase, phase_result)

# After all phases:
summary_worker.wait_all(timeout=60)  # wait for last summary before retrospective

# Generate retrospective
from .retrospective import RetrospectiveGenerator
retro_gen = RetrospectiveGenerator(config)
retro = retro_gen.generate(sprint_result)
```

---

## Tmux Layout Changes (`tmux.py`)

### 3-pane layout on sprint start

```python
def launch_in_tmux(config: SprintConfig):
    name = session_name(config.release_dir)
    config.tmux_session_name = name
    sprint_cmd = _build_foreground_command(config)

    # Create session with sprint TUI as main command
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", name, "-x", "120", "-y", "40",
         *sprint_cmd],
        check=True,
    )

    try:
        # Middle pane: summary display (25%)
        subprocess.run(
            ["tmux", "split-window", "-t", name, "-v", "-p", "50",
             "bash", "-c",
             "echo 'Waiting for first phase to complete...'; read"],
            check=True,
        )

        # Bottom pane: output tail (25% of remaining = 25% total)
        if config.active_phases:
            output_file = config.output_file(config.active_phases[0])
            quoted = shlex.quote(str(output_file))
            subprocess.run(
                ["tmux", "split-window", "-t", f"{name}:0.1", "-v", "-p", "50",
                 "bash", "-c",
                 f"touch {quoted} && tail -f {quoted}; read"],
                check=True,
            )

        # Focus on TUI pane
        subprocess.run(["tmux", "select-pane", "-t", f"{name}:0.0"], check=True)
    except Exception:
        subprocess.run(["tmux", "kill-session", "-t", name], check=False)
        raise

    subprocess.run(["tmux", "attach-session", "-t", name])
    # ... existing exit code handling ...
```

### Summary pane update function

```python
def update_summary_pane(tmux_session_name: str, summary_path: Path):
    """Display phase summary in the middle tmux pane."""
    quoted = shlex.quote(str(summary_path))
    # Interrupt current content
    subprocess.run(
        ["tmux", "send-keys", "-t", f"{tmux_session_name}:0.1", "C-c"],
        check=False,
    )
    # Clear and display summary
    subprocess.run(
        ["tmux", "send-keys", "-t", f"{tmux_session_name}:0.1",
         f"clear && cat {quoted} && echo '' && echo '--- Ctrl-B z to zoom/unzoom ---'\n"],
        check=False,
    )
```

### Tail pane index shifts

With 3 panes, the tail pane moves from `:0.1` to `:0.2`. The `update_tail_pane()` function needs its pane index updated.

---

## --no-tmux Fallback

When tmux is unavailable:
- Summary files are still written to `results/phase-N-summary.md`
- TUI shows a notification line below the header:
  ```
  Phase 1 summary ready: results/phase-1-summary.md
  ```
- Notification stored in `SprintTUI.latest_summary_notification: str | None`
- Updated by the executor when `SummaryWorker.latest_summary_path` changes
- Retrospective still generated and path shown in the terminal panel

---

## Model Changes (`models.py`)

### MonitorState — new fields

```python
@dataclass
class MonitorState:
    # ... existing fields ...

    # F1: Activity stream
    activity_log: list = field(default_factory=list)  # list[tuple[float, str, str]], max 3

    # F2: Turn tracking
    turns: int = 0

    # F4: Error tracking
    errors: list = field(default_factory=list)  # list[tuple[str, str, str]], max 10

    # F5: LLM context
    last_assistant_text: str = ""

    # F3: Task counting
    total_tasks_in_phase: int = 0
    completed_task_estimate: int = 0

    # F6: Token tracking (accumulated across events in current phase)
    tokens_in: int = 0
    tokens_out: int = 0
```

### PhaseResult — new fields

```python
@dataclass
class PhaseResult:
    # ... existing fields ...
    turns: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
```

### SprintResult — new aggregate properties

```python
@property
def total_turns(self) -> int:
    return sum(r.turns for r in self.phase_results)

@property
def total_tokens_in(self) -> int:
    return sum(r.tokens_in for r in self.phase_results)

@property
def total_tokens_out(self) -> int:
    return sum(r.tokens_out for r in self.phase_results)

@property
def total_output_bytes(self) -> int:
    return sum(r.output_bytes for r in self.phase_results)

@property
def total_files_changed(self) -> int:
    return sum(r.files_changed for r in self.phase_results)
```

### SprintConfig — new field

```python
total_tasks: int = 0  # pre-scanned from all phase files
```

---

## Monitor Changes (`monitor.py`)

### New extraction in `_extract_signals_from_event()`

```python
def _extract_signals_from_event(self, event: dict):
    event_type = event.get("type", "")

    # F2: Count assistant turns
    if event_type == "assistant":
        message = event.get("message", {})
        content = message.get("content", [])
        # Only count if this has actual content (not empty delta)
        if content:
            self.state.turns += 1

        # F5: Extract last assistant text
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "").strip()
                if text:
                    self.state.last_assistant_text = text[:80]

        # F6: Token tracking
        usage = message.get("usage", {})
        if usage:
            self.state.tokens_in += usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
            self.state.tokens_out += usage.get("output_tokens", 0)

    # F1: Activity log from tool_use
    if event_type == "tool_use" or (event_type == "assistant" and ...tool_use in content...):
        # Extract tool name and condensed input
        ...append to activity_log ring buffer (max 3)...

    # F4: Error detection from tool results
    if event_type == "user":
        # Check for is_error or error indicators in tool_result content
        ...append to errors list (max 10)...

    # ... existing extraction ...
```

### New method: `_count_tasks_in_file()`

```python
@staticmethod
def count_tasks_in_file(phase_file: Path) -> int:
    """Count T<PP>.<TT> task IDs in a phase file."""
    text = phase_file.read_text(errors="replace")
    return len(set(TASK_ID_PATTERN.findall(text)))
```

Called during `reset()` to set `self.state.total_tasks_in_phase`.

### Pre-scan on sprint start

In `config.py` `load_sprint_config()`, after discovering phases, scan all phase files to compute `total_tasks`:
```python
config.total_tasks = sum(OutputMonitor.count_tasks_in_file(p.file) for p in config.active_phases)
```

---

## TUI Changes (`tui.py`)

### `_render()` — new layout

```python
def _render(self) -> Panel:
    header = self._build_header()           # Elapsed + Model + Turns
    table = self._build_phase_table()       # Enhanced with Turns + Output columns
    progress = self._build_dual_progress()  # Two bars on one line
    detail = self._build_active_panel()     # Enhanced with activity + LLM context
    errors = self._build_error_panel()      # Conditional — None if no errors

    parts = [header, "", table, "", progress, "", detail]
    if errors:
        parts.extend(["", errors])

    body = RichGroup(*parts)
    release_name = self.config.index_path.parent.name
    return Panel(
        body,
        title=f"[bold]SUPERCLAUDE SPRINT RUNNER[/] [dim]== {release_name}[/]",
        border_style="blue",
        padding=(1, 2),
    )
```

### `_build_header()` — simplified

Remove release name (now in panel title). Show: Elapsed, Model, Turns/MaxTurns.

### `_build_phase_table()` — add columns

Add Turns and Output columns. Remove old Tasks column.

### `_build_dual_progress()` — new method

Render two compact progress bars as a single `Text` line using block characters.

### `_build_active_panel()` — enhanced

- Title becomes `f"ACTIVE: {phase.basename}"` (filename in border)
- Content: Status line, Task/Tool/Files line, blank, Prompt line, Agent line, blank, 3 activity lines
- Activity lines: formatted from `MonitorState.activity_log`

### `_build_error_panel()` — new method

Returns `Panel` with red border if `MonitorState.errors` is non-empty, else `None`.

### `_build_terminal_panel()` — enhanced

Two variants:
- Success: aggregate stats (duration, turns, tokens, output, files, log path)
- Halt: aggregate stats + completed count + last task + errors folded in + resume command + log path

---

## Executor Changes (`executor.py`)

Integration of SummaryWorker and RetrospectiveGenerator:

```python
# At start of execute_sprint():
summary_worker = SummaryWorker(config)

# After each phase result is recorded:
phase_result = PhaseResult(
    # ... existing fields ...
    turns=monitor.state.turns,
    tokens_in=monitor.state.tokens_in,
    tokens_out=monitor.state.tokens_out,
)
sprint_result.phase_results.append(phase_result)
summary_worker.submit(phase, phase_result)  # <-- NEW: background summary

# After sprint loop exits (before terminal panel):
summary_worker.wait_all(timeout=60)  # wait for last summary

# Generate retrospective (blocking -- runs before terminal display)
from .retrospective import RetrospectiveGenerator
retro_gen = RetrospectiveGenerator(config)
retro = retro_gen.generate(sprint_result)
# retro.path available for terminal panel display

# TUI notification for --no-tmux mode:
if summary_worker.latest_summary_path:
    tui.latest_summary_notification = f"Summary: {summary_worker.latest_summary_path}"
```

---

## Tmux Changes (`tmux.py`)

- 3-pane layout: TUI (50%) + summary (25%) + output tail (25%)
- `update_summary_pane()` function to pipe summary content to middle pane
- Tail pane index shifts from `:0.1` to `:0.2`
- `update_tail_pane()` pane index updated accordingly
- `_build_foreground_command()` unchanged

---

## Token display format helper

```python
def _format_tokens(n: int) -> str:
    if n < 1000:
        return f"{n}"
    if n < 1_000_000:
        return f"{n / 1000:.1f}K"
    return f"{n / 1_000_000:.1f}M"
```

---

## Out of Scope (Future PRs)

- `--compact` CLI flag to show current minimal layout
- Cost tracking / cache hit ratio display
- MCP server health indicators
- ETA estimation
- `sprint status` and `sprint logs` command implementations (currently stubs)
- Modal overlay for summary viewing in `--no-tmux` mode (keyboard input)
- Configurable summary model (currently hardcoded to Haiku)
- Interactive summary navigation (viewing older phase summaries)

---

## File Inventory

### Modified files (5)
| File | Changes |
|------|---------|
| `models.py` | New fields on MonitorState, PhaseResult, SprintResult, SprintConfig |
| `monitor.py` | Turn counting, token tracking, activity log, error detection, task counting |
| `tui.py` | New layout, dual progress bars, activity stream, error panel, LLM context, enhanced terminal panels, summary notification |
| `executor.py` | SummaryWorker integration, RetrospectiveGenerator call, summary notification to TUI |
| `tmux.py` | 3-pane layout, summary pane management, pane index update |

### New files (2)
| File | Purpose |
|------|---------|
| `summarizer.py` | PhaseSummary dataclass, PhaseSummarizer (programmatic extraction + Haiku narrative), SummaryWorker (background thread) |
| `retrospective.py` | ReleaseRetrospective dataclass, RetrospectiveGenerator (aggregation + Haiku narrative) |

### Output artifacts (per sprint)
| File | When Written |
|------|-------------|
| `results/phase-N-summary.md` | After each phase completes (background) |
| `results/release-retrospective.md` | After all phases complete (blocking) |

---

## Test Impact

### Existing test updates
- `test_tui.py`: New columns in phase table assertions, new MonitorState fields in fixtures, new terminal panel content, new `_build_dual_progress()` and `_build_error_panel()` methods, summary notification display
- `test_models.py`: New fields on MonitorState, PhaseResult, SprintResult aggregate properties, SprintConfig.total_tasks

### New tests needed
- `test_summarizer.py`: PhaseSummarizer programmatic extraction from NDJSON fixtures, narrative prompt building, summary markdown generation, SummaryWorker background execution and thread safety
- `test_retrospective.py`: RetrospectiveGenerator aggregation from phase summaries, narrative prompt building, retrospective markdown generation
- `test_tmux.py` (if exists): 3-pane layout creation, summary pane updates, pane index handling

### No changes needed
- `test_cli_contract.py`, `test_config.py` (beyond total_tasks), `test_process.py`, `test_e2e_*.py`
