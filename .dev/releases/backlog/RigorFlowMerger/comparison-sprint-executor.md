---
comparison_pair: 2
ic_component: Sprint Executor
lw_component: Automated QA Workflow
ic_source: src/superclaude/cli/sprint/executor.py, src/superclaude/cli/sprint/process.py
lw_source: .gfdoc/scripts/automated_qa_workflow.sh
mapping_type: direct
verdict_class: IC stronger
confidence: 0.85
patterns_not_mass_verified: true
generated: 2026-03-15
---

# Adversarial Comparison: Sprint Executor (IC) vs Automated QA Workflow (LW)

## 1. Debating Positions

### IC Advocate Position
The IronClaude sprint executor is a **Python supervisor** that manages Claude subprocess lifecycle with phase-level checkpointing, TurnLedger budget accounting, shadow gate mode, and tmux integration. Its core value is **language-appropriate implementation**: Python subprocess orchestration, monotonic clock enforcement, injectable `_subprocess_factory` for test-time substitution, and `TrailingGateRunner` as a daemon thread. The system is testable, extensible, and runs on standard infrastructure.

**Key strengths** (`src/superclaude/cli/sprint/executor.py:349`, `src/superclaude/cli/sprint/process.py:88`):
- TurnLedger enforces budget monotonicity with 80% reimbursement for PASS tasks
- `minimum_allocation=5` turns prevents launching underfunded subprocesses
- `_subprocess_factory` injection point enables testing without real Claude processes
- Shadow gate mode: `TrailingGateRunner` daemon thread decouples metrics from blocking
- Tmux integration for SSH-disconnect resilience

### LW Advocate Position
The llm-workflows automated QA workflow is a **6000-line bash orchestrator** implementing PABLOV methodology with immutable batch numbers, UID-based item tracking, and a fail-closed PASS/FAIL verdict. The three-mode prompt selection (normal/incomplete/correction) handles the most common real-world execution scenarios. The batch state machine (`initialized → worker_in_progress → worker_complete → qa_in_progress → qa_complete`) with persisted state JSON is more granular than IC's phase-level checkpointing.

**Key strengths** (`automated_qa_workflow.sh:4972-5322`, `automated_qa_workflow.sh:4391`):
- Batch immutability: Batch 5 always means the same items regardless of task file changes
- UID-based item tracking ensures stable cross-session references
- Fail-closed verdict: mismatch between taskspec checkmarks and programmatic handoff = FAIL
- Batch overrun detection: quarantines unauthorized Worker completions
- Three prompt modes preserve batch composition in correction/incomplete scenarios

## 2. Evidence from Both Repositories

### IC Evidence
| File | Line | Claim |
|---|---|---|
| `src/superclaude/cli/sprint/executor.py` | 490 | `execute_sprint()` main orchestration loop |
| `src/superclaude/cli/sprint/executor.py` | 349 | `execute_phase_tasks()` with TurnLedger |
| `src/superclaude/cli/sprint/models.py` | 466 | `minimum_allocation=5` turns before subprocess launch |
| `src/superclaude/cli/sprint/process.py` | 108 | Timeout = `max_turns * 120 + 300` (linear scaling) |
| `src/superclaude/cli/sprint/executor.py` | 356 | `_subprocess_factory` injectable for test substitution |
| `src/superclaude/cli/pipeline/trailing_gate.py` | — | `TrailingGateRunner` as daemon thread (shadow mode) |
| `src/superclaude/cli/sprint/executor.py` | 74 | SIGINT/SIGTERM → `shutdown_requested = True` |

### LW Evidence
| File | Line | Claim |
|---|---|---|
| `.gfdoc/scripts/automated_qa_workflow.sh` | 4972-5322 | Batch state machine with immutable state transitions |
| `.gfdoc/scripts/automated_qa_workflow.sh` | 4391 | UID-based item tracking |
| `.gfdoc/scripts/automated_qa_workflow.sh` | 3129-3132 | Fail-closed verdict: taskspec checkmarks vs programmatic handoff |
| `.gfdoc/scripts/automated_qa_workflow.sh` | 5302-5303 | Batch overrun detection and quarantine |
| `.gfdoc/scripts/automated_qa_workflow.sh` | 792-798 | Python isolated parser called from bash |
| `.gfdoc/scripts/automated_qa_workflow.sh` | 5427-5431 | Exponential backoff wait for worker_handoff (up to 6 attempts) |
| `.gfdoc/scripts/automated_qa_workflow.sh` | 4252-4297 | Session rollover: proactive + emergency + dead session recovery |

## 3. Adversarial Debate

**IC attacks LW**: LW's orchestrator is 6000+ lines of bash — a language inherently unsuited to complex state management. The evidence of maintenance fragility is not theoretical: multiple backup files (`automated_qa_workflow_backup_*.sh`) exist in the tracked codebase, indicating iterative patching rather than principled refactoring. The Python subprocess call from bash (`parse_checklist.py` in a sterile environment) is a workaround for bash's limitations, not a design feature. IC implemented the same orchestration logic in Python from the start, avoiding this entire class of technical debt.

**LW attacks IC**: IC's phase-level checkpointing is coarse. If Phase 3 has 15 tasks and fails on task 14, all 15 tasks must re-run on `--start 3` restart. LW's batch-level checkpoint (per-batch state JSON with immutable batch numbers) provides finer granularity: a corrected batch resumes exactly where it failed. Additionally, IC's TurnLedger state is NOT persisted — if the supervisor crashes mid-phase, budget tracking is lost. LW's batch state survives any crash because it's written to disk at every state transition.

**IC counter**: LW's finer batch granularity comes at the cost of a 6000-line bash monolith that requires expert bash knowledge to maintain. IC's Python supervisor is readable and testable by any engineer. The `_subprocess_factory` injection point is a direct testability feature LW has no equivalent of. Furthermore, IC's shadow gate mode enables production monitoring without blocking execution — LW has no equivalent decouple mechanism.

**LW counter**: The UID-based item tracking and batch immutability in LW are genuine reliability features absent in IC. IC tasks within a phase are not individually tracked — only the phase-level gate result is recorded. This means IC cannot answer "which specific tasks in Phase 3 completed before the crash?"

**Convergence**: IC is superior in implementation language, testability, and extensibility. LW is superior in batch-level granularity and per-item tracking. Both implement supervisor-style orchestration for LLM task execution. The core divide is maintenance quality vs. execution granularity.

## 4. Verdict

**Verdict class: IC STRONGER**

**Rationale**: IC's Python implementation is objectively more maintainable than LW's 6000-line bash script. The evidence of LW's maintenance fragility (backup files, bash-calling-Python workaround) is empirical, not theoretical. IC's extensibility (injectable factory, shadow gate mode, TrailingGatePolicy) is a design advantage that LW's bash architecture cannot replicate without a complete rewrite.

**Conditions where LW patterns should be adopted into IC**:
- Batch-level checkpoint granularity (per-item state persistence instead of phase-level only)
- UID-based item tracking within a phase's task set
- Immutable batch identity (once a phase starts, task numbering is frozen — no task renaming mid-run)
- Three-mode execution (normal/incomplete/correction) for mid-phase resume

**Confidence: 0.85**

**Adopt patterns, not mass**: From LW: the batch immutability principle (phase task IDs frozen at start), per-item UID tracking (each task gets a stable ID for cross-session reference), the three-mode prompt selection pattern (normal/incomplete/correction), and the fail-closed verdict logic (mismatch = FAIL, not best-effort PASS). Do NOT adopt: the bash implementation, the multiple-backup versioning strategy, the Python subprocess call from bash.
