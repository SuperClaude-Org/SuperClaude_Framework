 Sprint Runner Problem Statement: Silent Incomplete Phases                                                                                                                                        
                                                                  
  Problem Summary

  The sprint runner (superclaude sprint) silently classifies incomplete phases as successful. When a Claude Code subprocess exhausts its --max-turns budget mid-phase, the runner cannot
  distinguish this from a phase that completed all work successfully. Incomplete work passes through as PASS_NO_REPORT, the sprint continues, and downstream phases may build on work that was
  never done.

  ---
  Architecture Context

  How the Runner Works

  The sprint runner (src/superclaude/cli/sprint/executor.py) orchestrates multi-phase execution by spawning one Claude Code subprocess per phase:

  For each phase:
    1. Build prompt with task list + completion instructions
    2. Launch: claude --max-turns 50 --output-format stream-json -p <prompt>
    3. Poll subprocess at 0.5s intervals (TUI updates, stall watchdog)
    4. Subprocess exits → read exit code + check for result file
    5. Classify phase status → continue or halt

  The subprocess is an autonomous Claude Code agent given a tasklist file and instructed to:
  - Execute all tasks in order
  - Write a phase-N-result.md file when finished (the Completion Protocol)
  - Include YAML frontmatter (status: PASS|FAIL|PARTIAL) and EXIT_RECOMMENDATION: CONTINUE|HALT

  The Status Classification Chain

  _determine_phase_status() in executor.py:306-351 resolves status using this priority:

  ┌──────────┬───────────────────────────────────────────────┬────────────────┬────────────┬────────────┐
  │ Priority │                   Condition                   │     Status     │ is_success │ is_failure │
  ├──────────┼───────────────────────────────────────────────┼────────────────┼────────────┼────────────┤
  │ 1        │ exit_code == 124                              │ TIMEOUT        │ false      │ true       │
  ├──────────┼───────────────────────────────────────────────┼────────────────┼────────────┼────────────┤
  │ 2        │ exit_code != 0                                │ ERROR          │ false      │ true       │
  ├──────────┼───────────────────────────────────────────────┼────────────────┼────────────┼────────────┤
  │ 3        │ result file has EXIT_RECOMMENDATION: HALT     │ HALT           │ false      │ true       │
  ├──────────┼───────────────────────────────────────────────┼────────────────┼────────────┼────────────┤
  │ 4        │ result file has EXIT_RECOMMENDATION: CONTINUE │ PASS           │ true       │ false      │
  ├──────────┼───────────────────────────────────────────────┼────────────────┼────────────┼────────────┤
  │ 5        │ result file has status: PASS                  │ PASS           │ true       │ false      │
  ├──────────┼───────────────────────────────────────────────┼────────────────┼────────────┼────────────┤
  │ 6        │ result file has status: FAIL                  │ HALT           │ false      │ true       │
  ├──────────┼───────────────────────────────────────────────┼────────────────┼────────────┼────────────┤
  │ 7        │ result file has status: PARTIAL               │ HALT           │ false      │ true       │
  ├──────────┼───────────────────────────────────────────────┼────────────────┼────────────┼────────────┤
  │ 8        │ result file exists, no recognized signal      │ PASS_NO_SIGNAL │ true       │ false      │
  ├──────────┼───────────────────────────────────────────────┼────────────────┼────────────┼────────────┤
  │ 9        │ no result file, output exists                 │ PASS_NO_REPORT │ true       │ false      │
  ├──────────┼───────────────────────────────────────────────┼────────────────┼────────────┼────────────┤
  │ 10       │ no result file, no output                     │ ERROR          │ false      │ true       │
  └──────────┴───────────────────────────────────────────────┴────────────────┴────────────┴────────────┘

  The halt/continue decision in the executor loop is:
  if status.is_failure:
      # collect diagnostics, set outcome HALTED, break
  else:
      # continue to next phase

  How the Agent Prompt Works

  From ClaudeProcess.build_prompt() in process.py:46-88:

  /sc:task-unified Execute all tasks in @{phase_file} --compliance strict --strategy systematic

  ## Completion Protocol
  When ALL tasks in this phase are complete (or halted on STRICT failure):
  1. Write a phase completion report to {result_file} containing:
     - YAML frontmatter with: phase, status (PASS|FAIL|PARTIAL), tasks_total, tasks_passed, tasks_failed
     - Per-task status table
     - Files modified
     - Blockers for next phase
     - EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT

  The report is the last thing the agent is told to do. It is always the first casualty when turns run out.

  ---
  The Failure Mode

  What Happens

  1. Claude Code subprocess receives --max-turns 50
  2. Agent executes tasks, consuming turns (planning + implementation + verification per task)
  3. At turn 51, Claude Code force-stops the session with event error_max_turns
  4. Claude Code exits with code 0 (this is a graceful termination, not a crash)
  5. No phase-N-result.md was written (the agent never reached the Completion Protocol)
  6. The runner sees: exit code 0, no result file, output file is non-empty
  7. Status resolves to PASS_NO_REPORT (priority 9)
  8. PASS_NO_REPORT.is_success == True
  9. Sprint continues to next phase

  What the Runner Cannot See

  - How many tasks were in the phase file (it never parses the tasklist)
  - How many tasks the agent actually completed
  - Whether the agent hit error_max_turns or finished normally (both exit 0)
  - Whether the last task was fully completed or interrupted mid-implementation

  Evidence from the cleanup-audit-v2-UNIFIED-SPEC Sprint

  ┌───────┬───────┬───────────────────┬────────────────┬────────────┬─────────────────────────────────────────────────────────────────┐
  │ Phase │ Tasks │ Last Task Reached │     Status     │ Turns Used │                          What Happened                          │
  ├───────┼───────┼───────────────────┼────────────────┼────────────┼─────────────────────────────────────────────────────────────────┤
  │ 1     │ 8     │ T01.08 (8/8)      │ pass_no_report │ 51 (max)   │ All tasks done but report not written                           │
  ├───────┼───────┼───────────────────┼────────────────┼────────────┼─────────────────────────────────────────────────────────────────┤
  │ 2     │ 6     │ T02.06 (6/6)      │ pass_no_report │ 51 (max)   │ All tasks done, report was in_progress in todo list when killed │
  ├───────┼───────┼───────────────────┼────────────────┼────────────┼─────────────────────────────────────────────────────────────────┤
  │ 3     │ 10    │ T03.10 (10/10)    │ pass           │ <50        │ Completed within budget, report written                         │
  ├───────┼───────┼───────────────────┼────────────────┼────────────┼─────────────────────────────────────────────────────────────────┤
  │ 4     │ 13    │ T04.13 (13/13)    │ pass           │ <50        │ Completed within budget, report written                         │
  ├───────┼───────┼───────────────────┼────────────────┼────────────┼─────────────────────────────────────────────────────────────────┤
  │ 5     │ 9     │ T05.05 (5/9)      │ pass_no_report │ 51 (max)   │ 4 tasks never executed (T05.06-T05.09)                          │
  └───────┴───────┴───────────────────┴────────────────┴────────────┴─────────────────────────────────────────────────────────────────┘

  Phase 5 is the critical case: tasks T05.06 (benchmarking), T05.07 (concurrent-run isolation), T05.08 (non-determinism documentation), and T05.09 (release readiness decision) were never run. The
   sprint reported outcome: success.

  ---
  Why This Is a Problem

  1. Silent Data Loss

  Incomplete work is indistinguishable from complete work at the sprint level. The execution log shows pass_no_report but this is treated identically to pass in all decision logic.

  2. Downstream Phase Corruption

  Later phases may depend on deliverables from earlier phases. If phase N skips tasks, phase N+1 may build on missing foundations. In this sprint, Phase 5's unfinished tasks included the release
  readiness decision — the entire point of the final phase.

  3. False Confidence

  The sprint reports outcome: success with phases_passed: 5, phases_failed: 0. A user reviewing the execution log sees green across the board. The pass_no_report label is the only hint, and it
  doesn't communicate severity.

  4. No Recovery Path

  The runner's resume_command() generates a resume from the halt_phase, but since no phase halted, there's no resume suggestion. The user would need to manually re-run phases 1, 2, and 5, but has
   no tooling to know this is needed.

  ---
  Root Cause Analysis

  The Core Design Gap

  The runner relies entirely on the agent's self-reporting (the result file) to determine phase outcome, but the agent's ability to self-report is constrained by the same turn budget that limits
  its work. The Completion Protocol is the last step, making it the most likely to be cut.

  Contributing Factors

  ┌───────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │          Factor           │                                                                        Detail                                                                        │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Claude Code exit code     │ error_max_turns exits with code 0, indistinguishable from normal completion                                                                          │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ No task inventory         │ The runner never parses the phase tasklist file to know how many tasks exist                                                                         │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Report is last-mile       │ The Completion Protocol is at the end of the prompt, so the report is written after all work                                                         │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Monitor is liveness-only  │ OutputMonitor tracks output growth, stall duration, and last task ID, but doesn't compare against expected tasks                                     │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ PASS_NO_REPORT is success │ The status is classified as is_success, same as PASS                                                                                                 │
  ├───────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ No turn-budget awareness  │ The runner computes timeout_seconds = max_turns * 120 + 300 for wall-clock timeout, but has no visibility into how many turns were actually consumed │
  └───────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  What the Runner Already Has (Underutilized)

  1. MonitorState.last_task_id — regex-extracted from output stream (e.g., T05.05). This tells us where the agent stopped.
  2. Phase file paths — config.phases[i].file points to the tasklist markdown. Parsing task IDs from this would give the expected count.
  3. PhaseStatus.PASS_NO_REPORT — already distinguished from PASS in the enum, but not in the decision logic.
  4. Output stream in NDJSON — the full Claude Code session is captured. The error_max_turns event is in the stream (as the final "subtype":"error_max_turns" JSON line).

  ---
  Constraints for the Solution

  1. Cannot change Claude Code's exit code behavior — error_max_turns returning 0 is a Claude Code CLI design decision outside this project's control
  2. The child agent is untrusted for self-reporting — any solution that depends solely on the agent writing a report has the same failure mode
  3. Must be backward-compatible — existing sprint runs, tasklist formats, and CLI flags should continue to work
  4. Phase timeout already exists — config.phase_timeout is on the SprintConfig model but currently unused; this could be wired in
  5. Performance budget — the monitor already polls at 0.5s; any new logic should fit within that cycle

  ---
  Relevant Source Files

  ┌───────────────────────────────────────────┬────────────────────────────────────────────────────────────────┐
  │                   File                    │                              Role                              │
  ├───────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ src/superclaude/cli/sprint/executor.py    │ Main orchestration loop + _determine_phase_status()            │
  ├───────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ src/superclaude/cli/sprint/process.py     │ ClaudeProcess.build_prompt() — the prompt given to child agent │
  ├───────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ src/superclaude/cli/sprint/models.py      │ PhaseStatus enum, SprintConfig, MonitorState, PhaseResult      │
  ├───────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ src/superclaude/cli/sprint/monitor.py     │ OutputMonitor — NDJSON stream parser with regex extraction     │
  ├───────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ src/superclaude/cli/sprint/config.py      │ load_sprint_config() — phase discovery and validation          │
  ├───────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ src/superclaude/cli/sprint/logging_.py    │ SprintLogger — execution log writing                           │
  ├───────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ src/superclaude/cli/sprint/diagnostics.py │ DiagnosticCollector, FailureClassifier, ReportGenerator        │
  ├───────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ src/superclaude/cli/sprint/tui.py         │ SprintTUI — terminal UI display                                │
  ├───────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ src/superclaude/cli/pipeline/process.py   │ PipelineProcess.build_command() — base CLI arg construction    │
  ├───────────────────────────────────────────┼────────────────────────────────────────────────────────────────┤
  │ src/superclaude/cli/pipeline/models.py    │ PipelineConfig — base config                                   │
  └───────────────────────────────────────────┴────────────────────────────────────────────────────────────────┘

  ---
  What a Solution Should Address

  1. Detect incomplete phases — distinguish "all tasks done, no report" from "ran out of turns mid-phase"
  2. Classify appropriately — a new status or reclassification that triggers halt or user notification
  3. Surface the gap — make it obvious in execution logs which tasks were not reached
  4. Enable recovery — generate actionable resume commands for incomplete phases
  5. Optional: prevent the gap — strategies to ensure the report gets written before turns expire (turn reservation, early scaffolding, progressive reporting)