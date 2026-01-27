# Tasklist: Milestone 5 - Enhancements & Polish

> **Source Roadmap**: `.dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/roadmap.md`
> **Milestone**: M5 - Enhancements & Polish
> **Generated**: 2026-01-06
> **Generator Version**: Tasklist-Generator v2.1

---

## Milestone Overview

| Attribute | Value |
|-----------|-------|
| **Objective** | Implement optional flags and multi-iteration support |
| **Dependencies** | M4 (crossLLM integration complete) |
| **Complexity** | Low |
| **Total Deliverables** | 5 |
| **Total Tasks** | 12 |

---

## Deliverable Mapping

| Roadmap ID | Description | Tasks | Est. Effort |
|------------|-------------|-------|-------------|
| REQ-019 | Multi-iteration upgrade support | T05.01-T05.03 | M |
| IMP-001 | --chain flag | T05.04-T05.05 | S |
| IMP-002 | --upgrade-threshold flag | T05.06-T05.07 | S |
| IMP-003 | --upgrade-only flag | T05.08-T05.09 | S |
| IMP-004 | --sequential-upgrades flag | T05.10-T05.12 | S |

---

## Task List

### Multi-Iteration Support

#### T05.01 - Implement multi-iteration upgrade support
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-001 (REQ-019) |
| **Type** | Implementation |
| **Effort** | M |
| **Risk** | Medium |
| **Dependencies** | M4 complete |

**Description**: Implement multi-iteration upgrade support for `--version N` where N>2. Implement chain cycling: iteration 1 uses `claude>gpt`, iteration 2 uses `gpt>gemini`, iteration 3 uses `gemini>claude`, then repeats.

**Acceptance Criteria**:
- [ ] --version 3 executes 2 upgrade iterations (v1=draft, v2=iter1, v3=iter2)
- [ ] Chain cycling follows pattern: claude>gpt → gpt>gemini → gemini>claude
- [ ] Each iteration uses previous iteration output as input
- [ ] Version folders created correctly per iteration
- [ ] Iteration count logged in upgrade-log.md

**Artifacts**:
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (multi-iteration section)

---

#### T05.02 - QA: Verify chain cycling logic
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-001 (REQ-019) |
| **Type** | QA/Verification |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | T05.01 |

**Description**: Verify chain cycling follows correct sequence across iterations.

**Verification Checklist**:
- [ ] Iteration 1: claude>gpt (or --chain override)
- [ ] Iteration 2: gpt>gemini
- [ ] Iteration 3: gemini>claude
- [ ] Iteration 4: claude>gpt (cycle repeats)
- [ ] Chain logged per iteration

---

#### T05.03 - Integration test: Multi-iteration
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-001 (REQ-019) |
| **Type** | Integration Test |
| **Effort** | M |
| **Risk** | Low |
| **Dependencies** | T05.02 |

**Description**: Test multi-iteration with various --version values.

**Test Scenarios**:
- [ ] IT-M5-01: --version 3 creates 2 upgrade iterations
- [ ] Chain sequence verified across iterations
- [ ] Version folders contain correct iteration results

---

### Flag Implementations

#### T05.04 - Implement --chain flag
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-002 (IMP-001) |
| **Type** | Implementation |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | T05.01 |

**Description**: Add `--chain` flag to override the first iteration's chain. Default remains `claude>gpt`. Subsequent iterations follow normal cycling.

**Acceptance Criteria**:
- [ ] --chain gpt>claude overrides iteration 1 only
- [ ] Chain format validated (model>model)
- [ ] Invalid chain format produces clear error
- [ ] Override logged in upgrade-log.md
- [ ] Subsequent iterations unaffected

**Artifacts**:
- `.opencode/command/rf:roadmap-gen.md` (flag definition)
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (flag handling)

---

#### T05.05 - QA: Verify --chain flag behavior
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-002 (IMP-001) |
| **Type** | QA/Verification |
| **Effort** | XS |
| **Risk** | Low |
| **Dependencies** | T05.04 |

**Description**: Verify --chain flag works correctly.

**Verification Checklist**:
- [ ] IT-M5-02: --chain custom overrides iteration 1 only
- [ ] Invalid chain rejected with helpful error
- [ ] Iteration 2+ use standard cycling regardless of --chain
- [ ] Flag documented in command help

---

### Checkpoint: T05.01-T05.05
**Status**: [ ] Complete
**Blockers**: ___
**Notes**: ___

---

#### T05.06 - Implement --upgrade-threshold flag
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-003 (IMP-002) |
| **Type** | Implementation |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | M4 complete |

**Description**: Add `--upgrade-threshold` flag to configure minimum improvement percentage required to accept upgrade. Default is 25%.

**Acceptance Criteria**:
- [ ] --upgrade-threshold 15 accepts 15%+ improvements
- [ ] Threshold validated (1-100 range)
- [ ] Invalid threshold produces clear error
- [ ] Threshold applied per artifact
- [ ] Threshold logged in upgrade-log.md

**Artifacts**:
- `.opencode/command/rf:roadmap-gen.md` (flag definition)
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (flag handling)

---

#### T05.07 - QA: Verify --upgrade-threshold flag behavior
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-003 (IMP-002) |
| **Type** | QA/Verification |
| **Effort** | XS |
| **Risk** | Low |
| **Dependencies** | T05.06 |

**Description**: Verify threshold filtering works correctly.

**Verification Checklist**:
- [ ] IT-M5-03: --threshold 15 applies lower threshold
- [ ] 20% improvement accepted with --threshold 15
- [ ] 20% improvement rejected with --threshold 25
- [ ] Threshold logged per artifact result

---

#### T05.08 - Implement --upgrade-only flag
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-004 (IMP-003) |
| **Type** | Implementation |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | M4 complete |

**Description**: Add `--upgrade-only` flag to limit which artifacts are upgraded. Accepts comma-separated list of artifact names.

**Acceptance Criteria**:
- [ ] --upgrade-only roadmap.md upgrades only roadmap.md
- [ ] --upgrade-only roadmap.md,test-strategy.md upgrades both
- [ ] Invalid artifact name produces clear error
- [ ] Non-upgraded artifacts remain unchanged
- [ ] Selective upgrade logged in upgrade-log.md

**Artifacts**:
- `.opencode/command/rf:roadmap-gen.md` (flag definition)
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (flag handling)

---

#### T05.09 - QA: Verify --upgrade-only flag behavior
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-004 (IMP-003) |
| **Type** | QA/Verification |
| **Effort** | XS |
| **Risk** | Low |
| **Dependencies** | T05.08 |

**Description**: Verify selective upgrade works correctly.

**Verification Checklist**:
- [ ] IT-M5-04: --upgrade-only limits upgraded artifacts
- [ ] Only specified artifacts passed to crossLLM
- [ ] Non-specified artifacts unchanged
- [ ] Invalid artifact name caught with helpful error

---

#### T05.10 - Implement --sequential-upgrades flag
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-005 (IMP-004) |
| **Type** | Implementation |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | M4 complete (specifically REQ-013) |

**Description**: Add `--sequential-upgrades` flag to force sequential (non-parallel) upgrade execution. Useful for debugging and resource-constrained environments.

**Acceptance Criteria**:
- [ ] --sequential-upgrades forces one-by-one execution
- [ ] Upgrade order is deterministic (roadmap → test-strategy → execution-prompt)
- [ ] Each upgrade completes before next starts
- [ ] Sequential mode logged in upgrade-log.md
- [ ] Circuit breaker still functional in sequential mode

**Artifacts**:
- `.opencode/command/rf:roadmap-gen.md` (flag definition)
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (flag handling)

---

#### T05.11 - QA: Verify --sequential-upgrades flag behavior
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M5-005 (IMP-004) |
| **Type** | QA/Verification |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | T05.10 |

**Description**: Verify sequential execution mode works correctly.

**Verification Checklist**:
- [ ] IT-M5-05: --sequential-upgrades forces non-parallel
- [ ] Timing confirms sequential (not concurrent)
- [ ] Execution order is deterministic
- [ ] Circuit breaker works in sequential mode

---

#### T05.12 - Integration test: All M5 flags
| Attribute | Value |
|-----------|-------|
| **Deliverable** | All M5 |
| **Type** | Integration Test |
| **Effort** | M |
| **Risk** | Low |
| **Dependencies** | T05.11 |

**Description**: Test flag combinations and interactions.

**Test Scenarios**:
- [ ] --version 3 --chain gpt>claude (custom first iteration)
- [ ] --upgrade-threshold 10 --upgrade-only roadmap.md (combined flags)
- [ ] --sequential-upgrades --version 2 (sequential multi-iteration)
- [ ] All flags work together without conflicts

---

### Checkpoint: T05.06-T05.12 (End of Phase)
**Status**: [ ] Complete
**Blockers**: ___
**Notes**: ___

---

## Verification Checkpoint M5

| Checkpoint Item | Status | Notes |
|-----------------|--------|-------|
| All deliverables code-complete | [ ] | |
| --version 3 creates v1/, v2/, v3/ with correct chain sequence | [ ] | |
| --chain overrides iteration 1 only | [ ] | |
| --upgrade-threshold correctly filters results | [ ] | |
| --upgrade-only limits which artifacts upgrade | [ ] | |
| --sequential-upgrades forces sequential execution | [ ] | |

---

## Traceability Matrix

| Roadmap ID | Task IDs | Deliverable ID | Artifact Path |
|------------|----------|----------------|---------------|
| REQ-019 | T05.01, T05.02, T05.03 | D-M5-001 | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| IMP-001 | T05.04, T05.05 | D-M5-002 | `.opencode/command/rf:roadmap-gen.md`, `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| IMP-002 | T05.06, T05.07 | D-M5-003 | `.opencode/command/rf:roadmap-gen.md`, `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| IMP-003 | T05.08, T05.09 | D-M5-004 | `.opencode/command/rf:roadmap-gen.md`, `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| IMP-004 | T05.10, T05.11, T05.12 | D-M5-005 | `.opencode/command/rf:roadmap-gen.md`, `.opencode/agent/rf-roadmap-gen-orchestrator.md` |

---

## Execution Log Template

| Task ID | Started | Completed | Status | Notes |
|---------|---------|-----------|--------|-------|
| T05.01 | | | ⏳ | |
| T05.02 | | | ⏳ | |
| T05.03 | | | ⏳ | |
| T05.04 | | | ⏳ | |
| T05.05 | | | ⏳ | |
| T05.06 | | | ⏳ | |
| T05.07 | | | ⏳ | |
| T05.08 | | | ⏳ | |
| T05.09 | | | ⏳ | |
| T05.10 | | | ⏳ | |
| T05.11 | | | ⏳ | |
| T05.12 | | | ⏳ | |

---

*Generated by Tasklist-Generator v2.1*
