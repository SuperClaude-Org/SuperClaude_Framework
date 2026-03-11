---
spec_source: portify-release-spec.md
complexity_score: 0.85
adversarial: true
---

# CLI-Portify v4 — Merged Project Roadmap

## Executive Summary

This roadmap delivers `cli-portify`, a 7-step deterministic pipeline that converts inference-based SuperClaude workflows into programmatic CLI runners. The system orchestrates pure-programmatic steps (config validation, component discovery) with Claude-assisted steps (analysis, design, synthesis, brainstorm gap analysis, panel review with convergence) under synchronous Python flow control.

The merged roadmap uses the Opus-Architect variant as its structural foundation — selected for superior actionability (88 vs 70), architectural completeness (86 vs 72), and open question resolution (88 vs 58) — while incorporating the Haiku-Analyzer variant's strengths in test strategy (edge case identification, dependency-ordered validation sequence), failure-path rigor (early failure taxonomy, per-phase analyzer concerns), and project tracking (named checkpoints A-E).

### Key Architectural Constraints

- **Synchronous-only execution**: Zero `async def` or `await` anywhere in `cli_portify/`
- **Zero base-module modification**: No changes to `pipeline/` or `sprint/` modules
- **Runner-authored truth**: Python determines all status; no Claude self-reporting
- **Mandatory skill reuse**: `/sc:brainstorm` and `/sc:spec-panel` invoked, not reimplemented
- **Additive-only review**: Panel review modifies specs additively; no destructive edits

### Scope

- 13 new Python modules under `src/superclaude/cli/cli_portify/`
- 7 gate definitions with semantic checks
- Convergence loop executor with TurnLedger budget guard
- Rich TUI monitoring with dual JSONL+Markdown logging
- 18 total requirements (7 functional, 11 non-functional), 14 success criteria, 9 identified risks

### Estimated Effort

5 phases over 17-22 working days (3-4 weeks), fully sequential critical path with within-phase parallelization opportunities.

---

## Phased Implementation Plan

### Phase 1: Foundation, Contracts & Pure-Programmatic Steps

**Goal**: Establish module structure, domain models, failure taxonomy, gate framework, inter-module contracts, and the two steps requiring zero Claude interaction.

**Milestone**: `superclaude cli-portify --dry-run` executes Steps 1-2 and halts cleanly.

**Checkpoint A**: End of Phase 1 — deterministic foundations proven.

#### Contract Review (Day 1)

Before implementation, complete a focused contract review covering:

- Inter-module data flow contracts (Step 3 output schema consumed by Step 5 via `@path`)
- Failure contract structure: what fields `PortifyResult` encodes for resume decisions
- Resume state requirements: what serialized state enables correct step re-execution
- Gate signature standardization: all gates return `tuple[bool, str]` (NFR-004)

This is a half-day activity within Phase 1, not a separate phase.

#### Tasks

1. **Module scaffolding** — Create `src/superclaude/cli/cli_portify/__init__.py` and the 13 module stubs with docstrings. Register the `cli-portify` Click group in `main.py` via `app.add_command()`.
2. **Domain models** (`models.py`) — Define `PortifyConfig`, `PortifyResult`, `StepStatus`, `PhaseContract`, and gate-related types. All gate functions return `tuple[bool, str]` (NFR-004). Extend from `pipeline.models` primitives (`PipelineConfig`, `Step`, `StepResult`, `GateCriteria`, `GateMode`).
3. **Failure taxonomy** — Define failure classification categories in Phase 1 alongside `StepStatus`: gate failure, subprocess crash, budget exhaustion, timeout, user rejection, malformed artifact. Full diagnostics implementation remains in Phase 5.
4. **Config validation** (`steps/validate_config.py`, FR-001) — Resolve `--workflow` path, derive CLI name, check output directory writability, detect name collisions, validate template existence (fail fast with specific path in error), emit `validate-config-result.json`. Target: <1s, no subprocess.
5. **Component discovery** (`steps/discover_components.py`, FR-002) — `Path.rglob()` inventory of SKILL.md, refs/, rules/, templates/, scripts/. Produce `component-inventory.md` with YAML frontmatter. Target: <5s, no subprocess.
6. **Gate framework** (`gates.py`) — Implement gate definitions for Steps 1-2 (EXEMPT tier). Wire `gate_passed()` from `pipeline.gates`. Unit tests for gate signature compliance.
7. **Return contracts** — Implement `to_contract()` on `PortifyResult` producing YAML conforming to Phase Contracts schema. Cover success, partial, failed, dry_run paths. Unit tests for every failure path (NFR-009).
8. **CLI options** — `--workflow`, `--output-dir`, `--dry-run`, `--skip-review`, `--model`, `--max-convergence`, `--resume-from`. Parse and propagate through `PortifyConfig`.

#### Deliverables

- [ ] All 13 module files created under `cli_portify/`
- [ ] Inter-module contract review documented
- [ ] Failure taxonomy defined alongside `StepStatus`
- [ ] `superclaude cli-portify --workflow path --dry-run` runs Steps 1-2, emits contract
- [ ] 6 unit tests passing (validate-config, discover-components, gate signatures, contract emission)
- [ ] Zero imports of `async`/`await` (SC-009 verified by grep)

#### Analyzer Concerns (Review Checklist)

- Name derivation rules can create subtle collisions if normalization is not fully specified.
- Full-file line counting is acceptable initially, but file-size behavior should be bounded (skip files >1MB, log warning).
- This phase is a dependency bottleneck; defects here invalidate all later phases.

#### Exit Criteria

- SC-002: `--dry-run` halts after Phase 2 with valid contract
- SC-008: Pure-programmatic steps complete within time bounds
- SC-011: Zero modifications to `pipeline/` or `sprint/`

#### Timeline: 3-4 days

---

### Phase 2: Subprocess Infrastructure & Claude-Assisted Core

**Goal**: Build the subprocess execution layer and implement Steps 3-4 (workflow analysis, pipeline design).

**Milestone**: Steps 1-4 execute end-to-end, producing `portify-analysis.md` and `portify-spec.md`.

**Checkpoint B**: End of Phase 2 — dry-run and review gate validated.

#### Tasks

1. **PortifyProcess** (`process.py`) — Extend `ClaudeProcess` from `pipeline.process`. Pass `--add-dir` for work directory and workflow path (R-007 mitigation). Configure `extra_args`, `max_turns`, `@path` file references. Synchronous polling via `threading` + `time.sleep()` (NFR-003).
2. **Prompt builders** (`prompts.py`) — Template functions for Steps 3-7 prompts. Use `@path` references for artifact injection (R-001 mitigation). No inline embedding of large artifacts.
3. **Executor core** (`executor.py`) — Sequential step runner with status tracking, timing measurement, and failure classification (using Phase 1 taxonomy). Deterministic flow: Python decides sequencing, Claude handles content only (NFR-006).
4. **Workflow analysis step** (`steps/workflow_analysis.py`, FR-003) — Claude-assisted. Read all discovered components, produce `portify-analysis.md`. STRICT gate with semantic checks (required sections: Source Components, Step Graph, Gates Summary, Data Flow Diagram, Classification Summary). Under 400 lines.
5. **Pipeline design step** (`steps/pipeline_design.py`, FR-004) — Claude-assisted. Convert analysis into `portify-spec.md`. STRICT gate. User review gate (unless `--skip-review`).
6. **Gate definitions for Steps 3-4** — STRICT tier semantic checks. Section presence validation, line count enforcement, sync-only code patterns. Detect missing step classifications, dependency mappings, and gate summaries.
7. **User review gate** (`review.py`) — stderr prompt mechanism (NFR-011). Display step name, artifact path, gate result summary. `y` continues, `n` emits `USER_REJECTED` status. No timeout (user-paced).

#### Deliverables

- [ ] PortifyProcess with `--add-dir` support operational
- [ ] Steps 3-4 produce valid artifacts with all required sections
- [ ] User review gate functional on stderr (accept and reject paths verified)
- [ ] 5 additional unit tests passing

#### Analyzer Concerns (Review Checklist)

- This phase has the highest risk of semantic incompleteness hidden behind structurally valid markdown.
- Overly broad prompts may produce verbose outputs that exceed intended limits or dilute step boundaries.
- If Python is not the sole controller of next-step flow, NFR-006 will be violated early.

#### Exit Criteria

- SC-005: Gate tiers enforce correctly for Steps 1-4
- NFR-005: All status from exit codes and artifacts, not Claude self-report
- NFR-006: Python controls all sequencing

#### Timeline: 4-5 days

---

### Phase 3: Spec Synthesis & Skill Integration

**Goal**: Implement Steps 5-6 (spec synthesis, brainstorm gap analysis) including skill reuse and template instantiation.

**Milestone**: `portify-release-spec.md` generated with zero placeholders, brainstorm findings incorporated.

**Checkpoint C**: End of Phase 3 — synthesis quality and gap incorporation stable.

#### Tasks

1. **Spec synthesis step** (`steps/synthesize_spec.py`, FR-005) — Instantiate the 9KB release spec template from `src/superclaude/examples/release-spec-template.md`. Populate all sections from Phase 1-2 outputs via `@path`. STRICT gate: zero `{{SC_PLACEHOLDER:*}}` sentinels (SC-003). Retry prompt includes specific remaining placeholder names on failure.
2. **Template loader** — Read and validate template existence. Fail fast with clear error if template path is unstable (validated at config time in Phase 1).
3. **Brainstorm gap analysis step** (`steps/brainstorm_gaps.py`, FR-006) — Pre-flight check for `/sc:brainstorm` skill availability. Invoke via subprocess. Post-process findings into structured format `{gap_id, description, severity, affected_section, persona}`. Incorporate actionable findings as `[INCORPORATED]`, route unresolvable to Section 11 as `[OPEN]`. Append Section 12 summary. STANDARD gate: Section 12 requires findings table or zero-gap summary text, not just heading. Inline fallback if skill unavailable.
4. **Gate definitions for Steps 5-6** — STRICT for synthesis, STANDARD for brainstorm. Sentinel scanner for SC-003. Section 12 content validator.
5. **FR consolidation mapping** — Ensure synthesized spec contains explicit mapping of 7 FRs to pipeline steps.

#### Deliverables

- [ ] Template instantiation with zero remaining placeholders
- [ ] Brainstorm skill invocation with pre-flight check and fallback
- [ ] Section 12 properly populated (findings or zero-gap summary)
- [ ] 3 additional unit tests passing

#### Analyzer Concerns (Review Checklist)

- Placeholder leakage is a high-signal failure and must remain a hard stop.
- Brainstorm output variability can break post-processing unless structural fallback logic is defined.
- Incorporation rules must be additive and traceable, or review quality will degrade in Phase 4.

#### Exit Criteria

- SC-003: Zero `{{SC_PLACEHOLDER:*}}` sentinels
- NFR-010: Brainstorm invokes `/sc:brainstorm` (verified by prompt inspection)

#### Timeline: 3-4 days

---

### Phase 4: Convergence Loop & Panel Review

**Goal**: Implement Step 7 (panel review with convergence), the most architecturally complex component.

**Milestone**: Convergence loop terminates correctly (CONVERGED or ESCALATED), producing quality scores and downstream readiness assessment.

**Checkpoint D**: End of Phase 4 — convergence and readiness logic proven.

#### Tasks

1. **Convergence executor** (`convergence.py`) — Iteration manager with TurnLedger budget guard (R-002 mitigation). Each iteration: invoke `/sc:spec-panel --focus correctness,architecture`, run both focus (discussion) and critique in a single subprocess (R-009/GAP-006). Independent timeout per iteration (default 300s). Parse `panel-report.md` for convergence markers. Terminal states: CONVERGED (0 unaddressed CRITICALs), ESCALATED (max iterations reached), BUDGET_EXHAUSTED, TIMEOUT.
2. **Panel review step** (`steps/panel_review.py`, FR-007) — Pre-flight skill check. Additive-only spec modifications (NFR-008). Quality score computation: overall = mean(clarity, completeness, testability, consistency) with <0.01 tolerance (SC-010). Downstream readiness: `overall >= 7.0` -> true, `6.9` -> false (SC-012).
3. **Convergence predicate** — Parse string literals from panel report. Primary: exact string match. Fallback: regex for `CONVERGENCE_STATUS:\s*CONVERGED` (R-003 mitigation). Failure contract if neither succeeds.
4. **Budget estimation** — Pre-launch guard estimates token cost per iteration. Prevent launch if remaining budget insufficient for even one iteration.
5. **Gate definition for Step 7** — STRICT tier. Machine-readable convergence block validation. Quality score boundary checks. User review gate at end.
6. **Resume support** — On convergence failure, preserve `focus-findings.md` for context injection on resume (F-006). Reset convergence counter to 1.

#### Deliverables

- [ ] Convergence loop terminates correctly in all terminal states
- [ ] Quality scores computed per SC-010 formula
- [ ] Downstream readiness boundary verified (SC-012)
- [ ] 4 additional unit tests passing (including malformed panel output edge case)

#### Analyzer Concerns (Review Checklist)

- This is the highest logic-risk phase due to loop control, parsing ambiguity, and multiple terminal states.
- Marker-format variability from `/sc:spec-panel` is a known fragility.
- Incorrect mode mapping across iterations is a critical regression risk.

#### Exit Criteria

- SC-004: CONVERGED when 0 CRITICALs, ESCALATED after max
- SC-010: Overall = mean(4 dimensions), tolerance <0.01
- SC-012: 7.0 -> true, 6.9 -> false
- NFR-008: Additive-only modifications verified

#### Timeline: 4-5 days

---

### Phase 5: Integration, Monitoring & Validation

**Goal**: Wire everything together, add TUI monitoring, implement resume support, run full integration tests.

**Milestone**: SC-001 achieved — end-to-end pipeline completes for `sc-cleanup-audit` workflow producing `downstream_ready: true`.

**Checkpoint E**: End of Phase 5 — release certification against all success criteria.

#### Tasks

1. **Rich TUI monitor** (`monitor.py`) — Live dashboard with step progress, timing, gate status. JSONL event extraction from subprocess output. Signal vocabulary: `STEP_START`, `STEP_COMPLETE`, `GATE_PASS`, `GATE_FAIL`, `CONVERGENCE_ITERATION`.
2. **Dual logging** (`logging.py`) — JSONL machine-readable + Markdown human-readable execution logs.
3. **Resume command** (`resume.py`) — Generate resume CLI invocation on resumable failures (SC-006). Load partial state, skip completed steps, re-execute from failure point. Re-run failed step entirely (don't trust partial artifacts).
4. **Diagnostics** (`diagnostics.py`) — Full implementation of failure classification (taxonomy defined in Phase 1). Structured error output with actionable messages.
5. **Integration testing** — 6 integration tests (SC-014 expanded):
   - End-to-end with `sc-cleanup-audit` workflow
   - `--dry-run` mode
   - Resume from mid-pipeline failure
   - Convergence loop (CONVERGED path)
   - Convergence loop (ESCALATED path)
   - Skill unavailability fallback path
6. **Remaining unit tests** — Bring total to 17 (SC-013). Include edge cases:
   - Malformed panel output parsing
   - Empty or sparse workflow structures
   - Name normalization edge cases (prefix/suffix stripping, case conversion)
   - Review rejection behavior
7. **NFR verification sweep**:
   - `grep -r "async def\|await" src/superclaude/cli/cli_portify/` -> zero results (SC-009)
   - `git diff pipeline/ sprint/` -> zero changes (SC-011)
   - Gate signature audit -> all `tuple[bool, str]` (NFR-004)
8. **Timing validation** — Measure Phase 3 <10min (NFR-001), Phase 4 <15min (NFR-002). Advisory warnings only.
9. **`--model` propagation** — Propagate to all Claude subprocesses uniformly.

#### Deliverables

- [ ] Full pipeline executes end-to-end for `sc-cleanup-audit`
- [ ] TUI monitor renders step progress live
- [ ] Resume from failure works correctly
- [ ] 17 unit tests + 6 integration tests passing
- [ ] All 14 success criteria verified

#### Exit Criteria

- SC-001: End-to-end completion with `downstream_ready: true`
- SC-013: 17 unit tests pass
- SC-014: 6 integration tests pass (5 original + skill unavailability)
- All NFRs verified

#### Timeline: 3-4 days

---

## Risk Assessment

### High-Priority Risks

| ID | Risk | Severity | Likelihood | Mitigation | Phase |
|----|------|----------|------------|------------|-------|
| R-001 | Claude truncates output in large context windows | High | Medium | `@path` references instead of inline; generous `max_turns`; constrain prompts to required sections | P2 |
| R-002 | Budget exhaustion before convergence completes | High | Medium | TurnLedger pre-launch guards; per-iteration budget estimation | P4 |
| R-003 | Skills don't produce machine-readable markers | High | Medium | Exact string match primary, regex fallback, failure contract if neither succeeds | P4 |
| R-006 | Skills not installed, subprocess fails | High | Low | Pre-flight `claude` binary + skill availability checks; inline fallback | P2, P3 |
| R-009 | Wrong mode mapping in convergence iterations | High | Medium | Single subprocess per iteration runs both focus + critique | P4 |

### Medium-Priority Risks

| ID | Risk | Severity | Likelihood | Mitigation | Phase |
|----|------|----------|------------|------------|-------|
| R-007 | Subprocess can't read `@path` outside scope | Medium | Medium | `--add-dir` for work dir and workflow path; integration test for out-of-scope failures | P2 |
| R-008 | User review gate lacks programmatic interaction | Medium | Low | `--skip-review` flag; stderr prompt with step name, artifact path, gate summary | P2 |
| R-010 | Resume behavior ambiguity after partial writes | Medium | Medium | Re-run failed step entirely; define idempotency rules per step; don't trust partial artifacts | P1, P5 |
| R-011 | Template path stability | Medium | Low | Validate template existence at config time (Phase 1); fail fast with specific path in error | P1 |

### Low-Priority Risks

| ID | Risk | Severity | Likelihood | Mitigation | Phase |
|----|------|----------|------------|------------|-------|
| R-004 | Long wall-clock time from sequential execution | Low | High | Advisory timing; 7 steps (reduced from 12); non-blocking | P5 |
| R-005 | Self-portification circularity | Low | Low | Source skills read-only during portification | P1 |

---

## Resource Requirements & Dependencies

### Internal Dependencies (Must Exist Before Phase 1)

| Dependency | Module | Used By | Access |
|------------|--------|---------|--------|
| `PipelineConfig`, `Step`, `StepResult` | `pipeline.models` | Domain models | Read-only |
| `GateCriteria`, `GateMode` | `pipeline.models` | Gate framework | Read-only |
| `gate_passed()` | `pipeline.gates` | Gate enforcement | Read-only |
| `ClaudeProcess` | `pipeline.process` | PortifyProcess base | Read-only |
| `TurnLedger`, `GateDisplayState` | `sprint.models` | Budget tracking, TUI | Read-only |
| `SignalHandler` | `sprint.process` | Subprocess management | Read-only |
| Release spec template | `src/superclaude/examples/` | Spec synthesis | Must exist |

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Click | >=8.0.0 | CLI framework |
| Rich | >=13.0.0 | TUI dashboard |
| PyYAML | any | Frontmatter parsing |
| `claude` CLI | in PATH | Subprocess invocation |
| `/sc:brainstorm` skill | installed | Gap analysis step |
| `/sc:spec-panel` skill | installed | Panel review step |

### Pre-Implementation Verification

Before starting Phase 1:

1. Confirm `pipeline.models` exports all required types — read the module, verify API
2. Confirm `ClaudeProcess` supports `extra_args` — read the class, verify `--add-dir` capability
3. Confirm release spec template exists at expected path
4. Confirm `/sc:brainstorm` and `/sc:spec-panel` skills are installed and invocable

---

## Success Criteria & Validation Approach

### Validation Table

| Criterion | Validation Method | Phase |
|-----------|------------------|-------|
| SC-001 | Integration test: end-to-end `sc-cleanup-audit` | P5 |
| SC-002 | Integration test: `--dry-run` halts after P2 | P1 |
| SC-003 | Gate semantic check: `grep "{{SC_PLACEHOLDER"` -> 0 | P3 |
| SC-004 | Unit test: convergence terminal states | P4 |
| SC-005 | Unit tests: each gate enforces correct tier | P1-P4 |
| SC-006 | Integration test: resume from failure | P5 |
| SC-007 | Unit tests: contract YAML on all paths | P1 |
| SC-008 | Timing assertion in unit tests | P1 |
| SC-009 | `grep -r "async def\|await" cli_portify/` -> 0 | P5 |
| SC-010 | Unit test: mean calculation with tolerance | P4 |
| SC-011 | `git diff pipeline/ sprint/` -> empty | P5 |
| SC-012 | Unit test: boundary 7.0 true, 6.9 false | P4 |
| SC-013 | `uv run pytest tests/cli_portify/ -v` -> 17 pass | P5 |
| SC-014 | `uv run pytest tests/cli_portify/integration/ -v` -> 6 pass | P5 |

### Recommended Validation Sequence

Execute tests in dependency order to catch contract violations before propagation:

1. **Contract and gate unit tests** — verify `tuple[bool, str]` signatures, failure taxonomy, return contracts
2. **Pure-programmatic step tests** — validate config validation, component discovery, timing bounds
3. **Claude-assisted artifact structural validation** — verify section presence, line counts, placeholder elimination
4. **Convergence and failure-path tests** — terminal states, score math, boundary conditions, malformed output
5. **End-to-end workflow certification** — full pipeline, dry-run, resume, skill unavailability

---

## Timeline Estimates

| Phase | Duration | Cumulative | Key Risk | Checkpoint |
|-------|----------|------------|----------|------------|
| **P1**: Foundation & Contracts | 3-4 days | Week 1 | Dependency API verification, contract alignment | A |
| **P2**: Subprocess & Core Steps | 4-5 days | Week 2 | PortifyProcess `--add-dir` integration | B |
| **P3**: Synthesis & Skills | 3-4 days | Week 2-3 | Template stability, skill availability | C |
| **P4**: Convergence Loop | 4-5 days | Week 3 | Budget estimation accuracy, marker parsing | D |
| **P5**: Integration & Validation | 3-4 days | Week 3-4 | End-to-end timing, flaky subprocess behavior | E |

**Total**: 17-22 working days (3-4 weeks)

**Critical path**: P1 -> P2 -> P3 -> P4 -> P5 (fully sequential due to data flow dependencies between steps)

**Within-phase parallelization opportunities**:

- Within P1: Models, CLI options, and gate framework can develop concurrently
- Within P2: Prompt builders and executor core are independent until integration
- Within P5: Unit tests and TUI monitor are independent of each other

---

## Open Questions — Resolved

| Question | Resolution | Rationale |
|----------|-----------|-----------|
| GAP-004: Score rounding | Display 1 decimal, compare with `abs(computed - expected) < 0.01` before rounding | Avoids display/comparison mismatch |
| GAP-005: Resume from partial spec | Re-run failed step entirely | Partial artifacts are untrusted; clean re-execution is safer |
| GAP-007: Inline imports | Hoist to module level | Lazy loading unnecessary for `hashlib`/`yaml`; clarity wins |
| GAP-008: Monitor signals | Define 5 event types: `STEP_START`, `STEP_COMPLETE`, `GATE_PASS`, `GATE_FAIL`, `CONVERGENCE_ITERATION` | Minimal viable vocabulary; failure categories defined separately in Phase 1 taxonomy |
| GAP-009: File size limits | Skip files >1MB for line counting; log warning | Prevents pathological cases without over-engineering |
| Open Q7: Review gate UX | Display: step name, artifact path, gate result summary. No timeout (user-paced). | Minimal, actionable information |
| Open Q8: Template location | Validate at config time (Step 1). Fail with specific path in error message. | Fail fast pattern |
| Open Q9: `--model` scope | Propagate to all Claude subprocesses uniformly | Consistent behavior, no step-specific surprises |
| Open Q10: Marker format | Primary: exact string match. Fallback: regex for `CONVERGENCE_STATUS:\s*CONVERGED` | Handles whitespace/formatting variance |
