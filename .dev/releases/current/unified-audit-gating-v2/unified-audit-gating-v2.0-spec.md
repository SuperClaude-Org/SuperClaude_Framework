# unified-audit-gating v2.0 — Release Specification

**Status**: SPEC — Panel-reviewed configuration change release
**Date**: 2026-03-06
**Supersedes**: unified-spec-v1.0.md §3.4 (reimbursement rate proof), pipeline defaults
**Panel**: Wiegers, Adzic, Cockburn, Fowler, Nygard, Whittaker, Newman, Hohpe, Crispin, Gregory, Hightower
**Source Document**: PipelineConfigAnalysis.md
**Prior Spec**: unified-audit-gating-v1.2.1/unified-spec-v1.0.md

---

## 1. Problem Statement

The sprint pipeline shipped with two default values that diverged from the unified-spec-v1.0 design intent:

| Parameter | Spec v1.0 Design | Shipped Implementation | This Release Target |
|-----------|-------------------|----------------------|---------------------|
| `max_turns` per phase | Not explicitly specified | 50 | **100** |
| `reimbursement_rate` | 0.90 (§3.4) | 0.50 | **0.80** |

### 1.1 Impact of Current Defaults

**reimbursement_rate=0.5** causes budget exhaustion before a standard 46-task sprint completes:

```
net_cost_per_task = actual_turns - floor(actual_turns × rate) + overhead
                  = 8 - floor(8 × 0.5) + 2
                  = 8 - 4 + 2 = 6 turns per task

46 tasks × 6 turns = 276 turns required
Budget available: 200 turns
Deficit: -76 turns → exhaustion at task ~33
```

**max_turns=50** limits phase execution headroom, contributing to `pass_no_report` outcomes when tasks approach the turn ceiling.

### 1.2 Release Classification

This is a **configuration change release** — no structural changes, no new files, no logic changes. All edits are simple value replacements across 7 source locations and 4 test assertions.

---

## 2. Functional Requirements

| ID | Requirement | Rationale | Traceability |
|----|------------|-----------|--------------|
| FR-001 | The default value of `PipelineConfig.max_turns` SHALL be 100 | Doubles phase execution headroom to reduce `pass_no_report` incidence | S1: pipeline/models.py:175 |
| FR-002 | The default value of `SprintConfig.max_turns` SHALL be 100 | Sprint-layer override must match base class | S2: sprint/models.py:285 |
| FR-003 | The CLI `--max-turns` option SHALL default to 100 | CLI entry point must match config defaults | S3: sprint/commands.py:54 |
| FR-004 | The CLI `--max-turns` help text SHALL read "default: 100" | User-facing documentation accuracy | S3.1: sprint/commands.py:55 |
| FR-005 | The default value of `load_sprint_config(max_turns)` SHALL be 100 | Function signature default must match config | S4: sprint/config.py:108 |
| FR-006 | The default value of `ClaudeProcess.__init__(max_turns)` SHALL be 100 | Constructor default must match config | D1: pipeline/process.py:43 |
| FR-007 | The default value of `TurnLedger.reimbursement_rate` SHALL be 0.8 | Corrects budget sustainability for 46-task sprints | S5: sprint/models.py:476 |
| FR-008 | The `execute-sprint.sh` script SHALL set `MAX_TURNS=100` | Shell script default must match Python defaults | **NEW**: .dev/releases/execute-sprint.sh:47 |
| FR-009 | The `execute-sprint.sh` help text SHALL reference "default: 100" | Script documentation accuracy | **NEW**: .dev/releases/execute-sprint.sh:14 |
| FR-010 | The `rerun-incomplete-phases.sh` comment SHALL reference "max_turns (100)" | Historical context comment accuracy | **NEW**: scripts/rerun-incomplete-phases.sh:4 |
| FR-011 | The roadmap CLI `--max-turns` option SHALL default to 100 | Roadmap CLI entry point must match config defaults | **NEW**: roadmap/commands.py:75 |
| FR-012 | The roadmap CLI `--max-turns` help text SHALL read "Default: 100" | User-facing documentation accuracy | **NEW**: roadmap/commands.py:76 |

**Panel Finding (Wiegers, Round 1)**: The original analysis identified 7 source edits. The panel identified **5 additional locations** — 3 in shell scripts and 2 in the roadmap CLI (FR-008 through FR-012). These are hidden coupling points that would have caused configuration drift between the sprint layer, roadmap layer, and shell-based execution.

---

## 3. Non-Functional Requirements

| ID | Requirement | Verification Method |
|----|------------|-------------------|
| NFR-001 | Budget decay: At `reimbursement_rate=0.8` with `initial_budget=200`, a passing task consuming 8 turns with 2 overhead turns SHALL have net cost ≥ 4 turns | Unit test: `test_budget_decay_rate_08` |
| NFR-002 | No infinite run: For any `reimbursement_rate < 1.0`, the geometric series `Σ(rate^n)` converges, bounding total reimbursement | Mathematical proof (§4) |
| NFR-003 | Sprint sustainability: A 46-task sprint (avg 8 turns/task, 2 overhead) at `rate=0.8`, `budget=200` SHALL complete without exhaustion | Integration test: `test_46_task_sprint_completes` |
| NFR-004 | Phase timeout: At `max_turns=100`, phase timeout SHALL be `100 × 120 + 300 = 12,300s (3.4 hours)` | Unit test: timeout computation verification |
| NFR-005 | Sprint timeout bound: A 9-phase sprint at `max_turns=100` SHALL have maximum wall-clock time of `9 × 12,300s = 30.75 hours` | Documentation: acknowledged, no enforcement change |
| NFR-006 | Backward compatibility: Existing sprints with explicit `--max-turns=50` or explicit `reimbursement_rate=0.5` SHALL behave identically | Regression test: explicit override preserved |
| NFR-007 | Gate evaluation performance: Unchanged from v1.2.1 — `gate_passed()` SHALL complete within 50ms for output files up to 100KB | Existing test (no change required) |
| NFR-008 | Budget monotonic decay: `TurnLedger.available()` SHALL be monotonically non-increasing over the lifetime of a sprint (credits never exceed debits due to rate < 1.0) | Property-based test (new) |

### NFR-008 Update: Budget Decay Proof at rate=0.8

**Previous (v1.0 spec, §3.4)**: Proof written for rate=0.90
**This release**: Proof updated for rate=0.80 (implemented value)

The proof structure is identical — any `rate < 1.0` guarantees convergence. However, the **numerical examples** in the spec were incorrect relative to both the original implementation (0.5) and this target (0.8). This release corrects them.

---

## 4. Mathematical Proof: Budget Decay at rate=0.8

### 4.1 Per-Task Net Cost (Floor Model)

```
Given:
  actual_turns = 8 (average for a passing task)
  overhead_turns = 2 (subprocess startup/isolation)
  rate = 0.80

credit = floor(actual_turns × rate) = floor(8 × 0.80) = floor(6.4) = 6
debit  = actual_turns = 8
net_cost = debit - credit + overhead = 8 - 6 + 2 = 4 turns per passing task
```

### 4.2 Sprint Sustainability Analysis

| Metric | rate=0.50 | rate=0.80 | rate=0.90 |
|--------|-----------|-----------|-----------|
| credit per task (floor) | floor(4.0) = 4 | floor(6.4) = 6 | floor(7.2) = 7 |
| net cost per task | 6 | 4 | 3 |
| 46-task total drain | 276 | 184 | 138 |
| Budget remaining (of 200) | **-76 (EXHAUSTED)** | **16** | **62** |
| Max tasks sustainable | **33** | **50** | **66** |

### 4.3 Infinite Run Prevention

For a perpetual task chain where each task consumes `T` turns:

```
Total turns consumed = T + T×rate + T×rate² + T×rate³ + ...
                     = T × Σ(rate^n) for n=0..∞
                     = T / (1 - rate)

At rate=0.80: T/(1-0.80) = T/0.20 = 5T
At rate=0.50: T/(1-0.50) = T/0.50 = 2T
At rate=0.90: T/(1-0.90) = T/0.10 = 10T
```

All values are finite. No reimbursement rate < 1.0 can produce an infinite run. The budget is bounded by `initial_budget / (1 - rate)` in the absolute theoretical maximum, but in practice is bounded by `initial_budget` since `available()` cannot exceed `initial_budget` (credits only recover a fraction of debits).

### 4.4 Correction to v1.0 Spec Prose

The v1.0 spec (§3.4, lines 225–235) states:

```
net_cost_per_task = (actual_turns × 0.10) + overhead_turns
                  = (8 × 0.10) + 2 = 2.8 turns per passing task
For a 46-task sprint: ~129 turns of net drain. 200-turn budget sustains with ~71 turns of margin.
```

This is replaced by:

```
net_cost_per_task = actual_turns - floor(actual_turns × 0.80) + overhead_turns
                  = 8 - 6 + 2 = 4 turns per passing task
For a 46-task sprint: 184 turns of net drain. 200-turn budget sustains with 16 turns of margin.
```

**Panel Finding (Nygard, Round 2)**: The 16-turn margin at rate=0.8 is tight. If any task consumes more than average (e.g., 15 turns instead of 8), the margin erodes quickly. The spec SHOULD recommend `initial_budget ≥ 250` for sprints with >40 tasks at rate=0.8. This is a **guidance recommendation**, not a code change — `initial_budget` is already a required positional argument set by callers.

---

## 5. Safety Constraints

| ID | Constraint | Enforcement |
|----|-----------|-------------|
| SC-001 | `reimbursement_rate` MUST be in range `(0.0, 1.0)` exclusive | Runtime validation in TurnLedger (existing) |
| SC-002 | `max_turns` MUST be ≥ 1 | Click `type=int` with implicit positivity (existing) |
| SC-003 | `initial_budget` MUST be ≥ `minimum_allocation` | `can_launch()` guard (existing) |
| SC-004 | Explicit CLI overrides MUST take precedence over defaults | Click option processing (existing) |
| SC-005 | Phase timeout MUST NOT exceed system-configured maximum | **NEW RECOMMENDATION**: Add documentation noting 3.4hr max per phase |

---

## 6. Traceability Matrix

### 6.1 Source Edits (Tier 1: MUST change)

| Edit # | File | Line | Current | Target | FR |
|--------|------|------|---------|--------|----|
| 1 | `src/superclaude/cli/pipeline/models.py` | 175 | `max_turns: int = 50` | `max_turns: int = 100` | FR-001 |
| 2 | `src/superclaude/cli/sprint/models.py` | 285 | `max_turns: int = 50` | `max_turns: int = 100` | FR-002 |
| 3 | `src/superclaude/cli/sprint/commands.py` | 54 | `default=50` | `default=100` | FR-003 |
| 4 | `src/superclaude/cli/sprint/commands.py` | 55 | `help="...default: 50"` | `help="...default: 100"` | FR-004 |
| 5 | `src/superclaude/cli/sprint/config.py` | 108 | `max_turns: int = 50` | `max_turns: int = 100` | FR-005 |
| 6 | `src/superclaude/cli/pipeline/process.py` | 43 | `max_turns: int = 50` | `max_turns: int = 100` | FR-006 |
| 7 | `src/superclaude/cli/sprint/models.py` | 476 | `reimbursement_rate: float = 0.5` | `reimbursement_rate: float = 0.8` | FR-007 |

### 6.2 Additional Source Edits (Tier 1.5: MUST change — panel-identified)

| Edit # | File | Line | Current | Target | FR |
|--------|------|------|---------|--------|----|
| 8 | `.dev/releases/execute-sprint.sh` | 47 | `MAX_TURNS=50` | `MAX_TURNS=100` | FR-008 |
| 9 | `.dev/releases/execute-sprint.sh` | 14 | `default: 50` | `default: 100` | FR-009 |
| 10 | `scripts/rerun-incomplete-phases.sh` | 4 | `max_turns (50)` | `max_turns (100)` | FR-010 |
| 11 | `src/superclaude/cli/roadmap/commands.py` | 75 | `default=50` | `default=100` | FR-011 |
| 12 | `src/superclaude/cli/roadmap/commands.py` | 76 | `help="...Default: 50."` | `help="...Default: 100."` | FR-012 |

### 6.3 Test Edits (Tier 2: MUST update to match)

| Edit # | File | Line | Current | Target |
|--------|------|------|---------|--------|
| 13 | `tests/pipeline/test_models.py` | 54 | `assert cfg.max_turns == 50` | `assert cfg.max_turns == 100` |
| 14 | `tests/sprint/test_models.py` | 188 | `assert cfg.max_turns == 50` | `assert cfg.max_turns == 100` |
| 15 | `tests/sprint/test_config.py` | 215 | `assert config.max_turns == 50` | `assert config.max_turns == 100` |
| 16 | `tests/sprint/test_models.py` | 527 | `assert ledger.reimbursement_rate == 0.5` | `assert ledger.reimbursement_rate == 0.8` |

### 6.4 No Changes Required (Tier 3)

| File | Lines | Reason |
|------|-------|--------|
| `tests/sprint/test_e2e_trailing.py` | 88 | Explicit `max_turns=50` in fixture — intentional test parameter |
| `tests/sprint/test_process.py` | 31, 92 | Explicit `max_turns=50` in fixture |
| `tests/pipeline/test_process.py` | 116 | Explicit `max_turns=50` in fixture |
| `tests/pipeline/test_full_flow.py` | 97, 309 | Computes from `ledger.reimbursement_rate` — auto-adjusts |
| `scripts/rerun-incomplete-phases.sh` | 32 | `MAX_TURNS=200` — explicit override, not default-dependent |
| All `TurnLedger(initial_budget=N)` calls | Various | `initial_budget` is independent of both changes |
| Derived timeout computations | executor.py:77, process.py:108, executor.py:478 | Correctly derived from `config.max_turns` — auto-adjust |

### 6.5 Spec Documentation Edits (Tier 4: SHOULD update)

| File | Section | Current | Target |
|------|---------|---------|--------|
| `unified-spec-v1.0.md` | §3.1 (line 178) | `reimbursement_rate: float = 0.90` | `reimbursement_rate: float = 0.80` |
| `unified-spec-v1.0.md` | §3.4 (lines 225–235) | Proof at 90%: 2.8 turns/task, ~129 drain, ~71 margin | Proof at 80%: 4 turns/task, 184 drain, 16 margin |
| `unified-spec-v1.0.md` | §3.4 title | "The 90% Reimbursement Rate" | "The 80% Reimbursement Rate" |

---

## 7. Risk Register

| ID | Risk | Severity | Probability | Impact | Mitigation |
|----|------|----------|-------------|--------|------------|
| R-001 | 16-turn margin at rate=0.8 is tight for 46-task sprints | Medium | Medium | Budget exhaustion on above-average sprints | Recommend `initial_budget ≥ 250` for >40 tasks; document in spec |
| R-002 | Phase timeout at 3.4 hours may surprise users | Low | Low | Long-running sprints block terminal | Document timeout in help text and release notes |
| R-003 | Shell scripts use hardcoded MAX_TURNS (missed by initial analysis) | High | High (certain) | Python/shell configuration drift | FR-008, FR-009, FR-010 added to edit list |
| R-004 | Existing sprints with implicit defaults silently get new behavior | Medium | Medium | Users who tuned around old defaults may see different budget patterns | CHANGELOG entry mandatory; release notes |
| R-005 | Spec-implementation drift recurrence | Medium | Low | Future confusion about intended values | Update spec prose to reflect 0.8 (Tier 4 edits) |
| R-006 | No environment variable override path exists | Low | Low | Users cannot override defaults without code changes | Accept for v2.0; consider env var support in v2.1 |
| R-007 | 9-phase sprint at max_turns=100 could run 30+ hours | Low | Low | Resource consumption | Document; no enforcement change needed |

---

## 8. Expert Panel Review — Round-by-Round

### Round 1: Structural Analysis

**Karl Wiegers (Requirements)**:
The analysis document is well-structured with clear traceability. However, FR completeness has gaps:
- The analysis missed shell script defaults (`execute-sprint.sh:47`, `rerun-incomplete-phases.sh:4`). These are functional requirements that must be part of the edit list.
- The help text update (edit #4) is correctly identified but should be a separate FR for traceability.
- **Recommendation**: Add FR-008 through FR-010 for shell script alignment.

**Gojko Adzic (Specification by Example)**:

Given a sprint with 46 tasks, average 8 turns each, 2 overhead, initial_budget=200:
```
Scenario: Budget sustainability at rate=0.8
  Given: TurnLedger(initial_budget=200, reimbursement_rate=0.8)
  When: 46 tasks execute, each consuming 8 turns with PASS gates
  Then: final budget = 200 - 184 = 16 turns remaining
  And: all tasks completed without HALT

Scenario: Budget exhaustion at rate=0.5 (current)
  Given: TurnLedger(initial_budget=200, reimbursement_rate=0.5)
  When: tasks execute sequentially
  Then: budget exhausted at task ~33
  And: tasks 34-46 NOT ATTEMPTED

Scenario: Explicit override preserved
  Given: CLI invocation with --max-turns=50
  When: sprint executes
  Then: max_turns=50 is used (not 100)
  And: behavior identical to v1.2.1
```

**Alistair Cockburn (Use Cases)**:
Primary actor: Sprint runner operator. Goal: complete a multi-phase sprint without budget exhaustion. The configuration change is invisible to the operator — they experience it as "sprints that used to fail now succeed." No use case changes required.

**Martin Fowler (Architecture)**:
The 5-location default pattern for `max_turns` is a code smell — DRY violation. The base class default (S1), subclass override (S2), CLI default (S3), function default (S4), and constructor default (D1) should ideally derive from a single source. However, this is a pre-existing architectural issue and out of scope for this configuration release. **Recommendation**: File a follow-up issue to consolidate defaults into a single constant or config file.

### Round 2: Mathematical Rigor and Correctness

**Michael Nygard (Reliability)**:
The mathematical analysis is correct but the framing needs correction:

1. The analysis claims 0.8 makes NFR-008 "stronger." This is **incorrect framing**. NFR-008 (no infinite run) holds identically for ANY rate < 1.0. The proof is equally "strong" at 0.5, 0.8, and 0.9.

2. What differs is **practical sustainability**: at 0.5, a 46-task sprint is infeasible (exhaustion at task 33). At 0.8, it's feasible but tight (16-turn margin). At 0.9, it's comfortable (62-turn margin).

3. The 16-turn margin concern: If even one task consumes 20 turns instead of 8, the net cost for that task is `20 - floor(20 × 0.8) + 2 = 20 - 16 + 2 = 6` instead of 4. Two such tasks eat the entire margin. **Recommendation**: Spec should include budget adequacy guidance: `initial_budget ≥ 250` for >40 tasks.

**James Whittaker (Adversarial)**:

**Attack 1 — Zero/Empty Attack on reimbursement_rate**:
> I can break this specification by **Zero/Empty Attack**. The invariant at **TurnLedger.credit()** fails when **reimbursement_rate = 0.0**. Concrete attack: `TurnLedger(initial_budget=200, reimbursement_rate=0.0)` → `credit(8)` → `reimbursed += floor(8 × 0.0) = 0`. Budget drain is 100% — every task costs its full turns. This is valid behavior (no reimbursement), but the spec doesn't define the boundary. **Severity: MINOR** — behavior is correct, but the valid range should be documented.

**Attack 2 — Sentinel Collision on rate=1.0**:
> I can break this specification by **Sentinel Collision Attack**. The invariant at **NFR-008** (budget decay) fails when **reimbursement_rate = 1.0**. Concrete attack: `TurnLedger(initial_budget=200, reimbursement_rate=1.0)` → `credit(8)` → `reimbursed += 8` → net cost = 0 + overhead only. With overhead=0 (subprocess re-use), infinite run is possible. **Severity: CRITICAL** — SC-001 must enforce `rate < 1.0` strictly, not `rate <= 1.0`.

**Attack 3 — Accumulation Attack on budget margin**:
> I can break this specification by **Accumulation Attack**. The invariant at **NFR-003** (46-task sprint sustainability) fails when **task variance is high**. Concrete attack: 40 tasks use 8 turns (net cost 4 each = 160), then 6 tasks use 15 turns each (net cost `15 - 12 + 2 = 5` each = 30). Total: 190. Remaining: 10. Now if any of those 6 tasks FAIL their gate (no reimbursement), net cost = 15 + 2 = 17. Budget: 200 - 160 - 17 = 23, but remediation needs `minimum_remediation_budget=3` and the remediation task needs turns too. Tight but survivable. However, 2 gate failures in the final 6 tasks: 200 - 160 - 34 = 6. Can't remediate the second failure. **Severity: MAJOR** — NFR-003 should be conditioned on "all tasks pass gates" or the margin guidance should account for failures.

### Round 3: Test Strategy and Migration

**Lisa Crispin (Testing)**:

**Test updates required** (4 assertion changes): Correct and complete.

**NEW tests recommended**:

| Test | Type | Purpose | Priority |
|------|------|---------|----------|
| `test_budget_decay_rate_08` | Unit | Verify net cost = 4 at rate=0.8, actual=8 | P1 |
| `test_max_sustainable_tasks_rate_08` | Unit | Verify exhaustion at task ~50 with budget=200 | P1 |
| `test_46_task_sprint_completes` | Integration | Full 46-task mock sprint at new defaults | P1 |
| `test_budget_exhaustion_property` | Property-based | For random task counts and turn usage, budget reaches 0 in finite steps at rate=0.8 | P2 |
| `test_explicit_override_preserved` | Regression | `--max-turns=50` overrides new default of 100 | P1 |
| `test_timeout_at_100_turns` | Unit | Verify timeout = 12,300s | P2 |
| `test_rate_boundary_zero` | Boundary | rate=0.0 → zero reimbursement, all tasks cost full turns | P2 |
| `test_rate_boundary_near_one` | Boundary | rate=0.99 → high reimbursement but still decays | P2 |

**Janet Gregory (Quality Practices)**:
The specification workshop identified that the analysis was produced by a single author without cross-team review. The panel review itself serves as the quality checkpoint. **Recommendation**: Include a test matrix in the CHANGELOG showing before/after behavior for the three key scenarios (46-task sprint at 0.5, 0.8, 0.9).

**Sam Newman (Service Boundaries)**:
No service boundary changes. The configuration defaults are internal to the sprint runner. No API contract changes. No backward-incompatible behavioral changes for users who explicitly set values.

**Gregor Hohpe (Integration)**:
No integration pattern changes. The three-channel event flow (§2.4 in v1.0 spec) is unaffected. The TurnLedger economics change in magnitude but not in structure.

**Kelsey Hightower (Operations)**:
The 3.4-hour phase timeout is significant for CI/CD environments. If sprints run in GitHub Actions or similar, the default runner timeout is typically 6 hours. A 9-phase sprint at 30+ hours would exceed this. **Recommendation**: Document the timeout implications in release notes.

---

## 9. Guard Condition Boundary Table

| Guard | Location | Input Condition | Variable Value | Guard Result | Specified Behavior | Status |
|-------|----------|-----------------|----------------|--------------|-------------------|--------|
| `can_launch()` | TurnLedger | Zero budget | `available() = 0` | False | HALT sprint | OK |
| `can_launch()` | TurnLedger | Minimal budget | `available() = 5` | True | Launch with 5 turns | OK |
| `can_launch()` | TurnLedger | Below minimum | `available() = 4` | False | HALT sprint | OK |
| `can_launch()` | TurnLedger | Typical | `available() = 150` | True | Launch normally | OK |
| `can_remediate()` | TurnLedger | Zero budget | `available() = 0` | False | Skip remediation, HALT | OK |
| `can_remediate()` | TurnLedger | At minimum | `available() = 3` | True | Attempt remediation | OK |
| `can_remediate()` | TurnLedger | Below minimum | `available() = 2` | False | Skip remediation, HALT | OK |
| `credit()` | TurnLedger | rate=0.0 | `floor(8 × 0.0) = 0` | N/A | Zero reimbursement | GAP — valid range not documented |
| `credit()` | TurnLedger | rate=0.8 (new default) | `floor(8 × 0.8) = 6` | N/A | Credit 6 turns | OK |
| `credit()` | TurnLedger | rate=1.0 | `floor(8 × 1.0) = 8` | N/A | Full reimbursement — NFR-008 violated | GAP — SC-001 must enforce `< 1.0` strictly |
| `credit()` | TurnLedger | Negative rate | `rate = -0.1` | N/A | Negative credit — ledger corruption | GAP — no validation for negative rate |
| `credit()` | TurnLedger | rate > 1.0 | `rate = 1.5` | N/A | Credit exceeds debit — budget inflation | GAP — no validation for rate > 1.0 |
| `timeout` | process.py | max_turns=0 | `0 × 120 + 300 = 300s` | N/A | 5-minute timeout (minimum) | OK |
| `timeout` | process.py | max_turns=100 (new default) | `100 × 120 + 300 = 12300s` | N/A | 3.4-hour timeout | OK |
| `timeout` | process.py | max_turns=MAX_INT | overflow risk | N/A | Extremely long timeout | GAP — no upper bound validation |

**Findings from Boundary Table**:
- **MAJOR (FR-GAP-001)**: `reimbursement_rate` valid range `(0.0, 1.0)` exclusive should be enforced at construction time. SC-001 states this but enforcement must be verified.
- **MAJOR (FR-GAP-002)**: Negative `reimbursement_rate` and `rate > 1.0` produce incorrect behavior. Validation needed.
- **MINOR (FR-GAP-003)**: `max_turns` has no upper bound. At extreme values, timeout overflows. Low practical risk but should be documented.

---

## 10. Spec-Implementation Alignment Recommendation

**Panel Consensus (Round 3)**: The spec (unified-spec-v1.0.md) MUST be updated to reflect the implemented value of 0.8. Reasons:

1. **Root cause prevention**: Spec-implementation drift caused this release. Keeping the spec at 0.90 while implementing 0.80 perpetuates the exact problem.
2. **Developer trust**: Developers reading the spec should find values that match the code.
3. **Mathematical accuracy**: The worked examples in §3.4 and Appendix A become misleading if they show 0.90 math but the code uses 0.80.

**Recommendation**: Update the spec to reflect 0.8 as the **current implemented value**. Add a note:

```
NOTE: The original design target was 0.90 (v1.0 spec). The implementation shipped at 0.50
due to conservative initial calibration. v2.0 corrects to 0.80 based on empirical sprint
data showing 0.50 causes budget exhaustion on standard workloads. Future releases may
adjust toward 0.90 as the system matures.
```

---

## 11. Migration and Changelog Guidance

### CHANGELOG Entry (Mandatory)

```markdown
## v2.0.0 — Configuration Defaults Update

### Changed
- **max_turns** default: 50 → 100 per phase
  - Doubles execution headroom to reduce `pass_no_report` incidence
  - Phase timeout increases proportionally: 6,300s → 12,300s (3.4 hours)
  - Explicit `--max-turns=N` overrides are preserved
- **reimbursement_rate** default: 0.5 → 0.8
  - Fixes budget exhaustion on 46-task sprints (previously exhausted at task ~33)
  - Aligns implementation closer to spec design intent (0.90)
  - 200-turn budget now sustains 50 passing tasks (was 33)

### Migration Guide
- If you relied on `max_turns=50` implicitly, your sprints will now allow up to 100 turns per phase.
  To preserve old behavior: `superclaude sprint run <index> --max-turns 50`
- If you calibrated `initial_budget` around `reimbursement_rate=0.5`, your budgets will now
  have more margin. No action needed unless you explicitly set `reimbursement_rate=0.5` in code.
- Shell scripts (`execute-sprint.sh`) updated to match. If you copied these scripts, update your copies.

### Budget Guidance
- For sprints with >40 tasks: recommend `initial_budget ≥ 250` at rate=0.8
- For sprints with ≤20 tasks: `initial_budget=200` provides comfortable margin
```

---

## 12. Test Strategy Summary

### Tests to UPDATE (4)

| # | Test File | Line | Change |
|---|-----------|------|--------|
| 1 | `tests/pipeline/test_models.py` | 54 | `== 50` → `== 100` |
| 2 | `tests/sprint/test_models.py` | 188 | `== 50` → `== 100` |
| 3 | `tests/sprint/test_config.py` | 215 | `== 50` → `== 100` |
| 4 | `tests/sprint/test_models.py` | 527 | `== 0.5` → `== 0.8` |

### Tests to ADD (New)

| # | Test Name | Type | File | Description |
|---|-----------|------|------|-------------|
| 1 | `test_budget_decay_rate_08` | Unit | `tests/sprint/test_models.py` | Verify: TurnLedger(initial_budget=200, rate=0.8), debit(8), credit(8) → reimbursed=6, available()=198 |
| 2 | `test_max_sustainable_tasks_at_08` | Unit | `tests/sprint/test_models.py` | Loop debit+credit for N tasks until exhaustion, verify N≈50 at rate=0.8 |
| 3 | `test_46_task_sprint_sustainability` | Integration | `tests/sprint/test_models.py` | 46-task loop at avg=8 turns, rate=0.8, budget=200 → all complete, final budget > 0 |
| 4 | `test_budget_exhaustion_property` | Property | `tests/sprint/test_models.py` | Hypothesis: for random(1,100) tasks with random(1,50) turns each, budget always reaches 0 |
| 5 | `test_explicit_max_turns_override` | Regression | `tests/sprint/test_config.py` | Explicit `--max-turns=50` overrides default of 100 |
| 6 | `test_rate_boundary_validation` | Boundary | `tests/sprint/test_models.py` | rate=0.0, rate=0.99, rate=1.0 (rejected), rate=-0.1 (rejected) |

### Tests NOT Affected (Tier 3 — No Changes)

All explicit-value fixtures (`max_turns=50` in test parameters) and derived-value tests (`int(10 * ledger.reimbursement_rate)`) are correctly isolated and will pass without changes.

---

## 13. Total Edit Count

| Tier | Category | Count | Risk |
|------|----------|-------|------|
| 1 | Source defaults (Python) | 7 | Low |
| 1.5 | Shell script + roadmap CLI defaults (panel-identified) | 5 | Low |
| 2 | Test assertion updates | 4 | None |
| 4 | Spec documentation (recommended) | 3 | None |
| **Total** | | **19** | **Low** |

Plus 6 new tests to add.

---

## Appendix A: Panel Composition and Review Summary

| Expert | Focus | Key Finding | Severity |
|--------|-------|-------------|----------|
| Wiegers | Requirements | 5 missing edits: 3 shell scripts + 2 roadmap CLI | HIGH |
| Adzic | Examples | 3 concrete GWT scenarios produced | — |
| Cockburn | Use Cases | No use case changes needed | — |
| Fowler | Architecture | DRY violation in 5-location defaults (follow-up issue) | MINOR |
| Nygard | Reliability | 16-turn margin is tight; budget guidance needed | MEDIUM |
| Whittaker | Adversarial | rate=1.0 breaks NFR-008; negative rate unhandled | CRITICAL (1), MAJOR (2) |
| Newman | Boundaries | No service boundary changes | — |
| Hohpe | Integration | No integration pattern changes | — |
| Crispin | Testing | 6 new tests recommended | — |
| Gregory | Quality | Test matrix in CHANGELOG recommended | — |
| Hightower | Operations | 3.4hr timeout needs CI/CD documentation | LOW |

### Panel Consensus Items

1. **UNANIMOUS**: Shell script and roadmap CLI defaults MUST be included in edit list (FR-008–FR-012)
2. **UNANIMOUS**: Spec prose MUST be updated to reflect 0.8 (not left at 0.90)
3. **MAJORITY (9/11)**: Budget guidance (`initial_budget ≥ 250` for >40 tasks) should be added
4. **MAJORITY (8/11)**: New integration test for 46-task sprint completion is P1 priority
5. **UNANIMOUS**: CHANGELOG entry is mandatory for this release
6. **MAJORITY (7/11)**: DRY consolidation of defaults is desirable but out of scope

---

*Generated by /sc:spec-panel — 11-expert panel review, 3 rounds, deep analysis mode*
*Source: PipelineConfigAnalysis.md + unified-spec-v1.0.md (v1.2.1)*
