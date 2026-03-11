

---
spec_source: portify-release-spec.md
complexity_score: 0.85
primary_persona: architect
---

# CLI-Portify v4 — Project Roadmap

## 1. Executive Summary

This roadmap covers the implementation of `cli-portify`, a 7-step pipeline that converts inference-based SuperClaude workflows into programmatic CLI pipelines. The system orchestrates pure-programmatic steps (config validation, component discovery) with Claude-assisted steps (analysis, design, synthesis, brainstorm gap analysis, panel review with convergence) under deterministic Python flow control.

**Key architectural constraints**: synchronous-only execution, zero modification to existing `pipeline/` and `sprint/` base modules, runner-authored truth (no Claude self-reporting for status), and mandatory reuse of existing `/sc:brainstorm` and `/sc:spec-panel` skills.

**Scope**: 13 new Python modules under `src/superclaude/cli/cli_portify/`, 7 gate definitions with semantic checks, a convergence loop executor, Rich TUI monitoring, and dual JSONL+Markdown logging. 18 total requirements (7 functional, 11 non-functional), 14 success criteria, 9 identified risks.

**Estimated total effort**: 5 phases over approximately 3–4 weeks of focused development.

---

## 2. Phased Implementation Plan

### Phase 1: Foundation & Pure-Programmatic Steps
**Goal**: Establish module structure, domain models, gate framework, and the two steps that require zero Claude interaction.

**Milestone**: `superclaude cli-portify --dry-run` executes Steps 1–2 and halts cleanly.

#### Tasks
1. **Module scaffolding** — Create `src/superclaude/cli/cli_portify/__init__.py` and the 13 module stubs with docstrings. Register the `cli-portify` Click group in `main.py` via `app.add_command()`.
2. **Domain models** (`models.py`) — Define `PortifyConfig`, `PortifyResult`, `StepStatus`, `PhaseContract`, and gate-related types. All gate functions return `tuple[bool, str]` (NFR-004). Extend from `pipeline.models` primitives (`PipelineConfig`, `Step`, `StepResult`, `GateCriteria`, `GateMode`).
3. **Config validation** (`steps/validate_config.py`, FR-001) — Resolve `--workflow` path, derive CLI name, check output directory writability, detect name collisions, emit `validate-config-result.json`. Target: <1s, no subprocess.
4. **Component discovery** (`steps/discover_components.py`, FR-002) — `Path.rglob()` inventory of SKILL.md, refs/, rules/, templates/, scripts/. Produce `component-inventory.md` with YAML frontmatter. Target: <5s, no subprocess.
5. **Gate framework** (`gates.py`) — Implement gate definitions for Steps 1–2 (EXEMPT tier). Wire `gate_passed()` from `pipeline.gates`. Unit tests for gate signature compliance.
6. **Return contracts** — Implement `to_contract()` on `PortifyResult` producing YAML conforming to Phase Contracts schema. Cover success, partial, failed, dry_run paths. Unit tests for every failure path (NFR-009).
7. **CLI options** — `--workflow`, `--output-dir`, `--dry-run`, `--skip-review`, `--model`, `--max-convergence`, `--resume-from`. Parse and propagate through `PortifyConfig`.

#### Deliverables
- [ ] All 13 module files created under `cli_portify/`
- [ ] `superclaude cli-portify --workflow path --dry-run` runs Steps 1–2, emits contract
- [ ] 6 unit tests passing (validate-config, discover-components, gate signatures, contract emission)
- [ ] Zero imports of `async`/`await` (SC-009 verified by grep)

#### Exit Criteria
- SC-002: `--dry-run` halts after Phase 2 with valid contract
- SC-008: Pure-programmatic steps complete within time bounds
- SC-011: Zero modifications to `pipeline/` or `sprint/`

---

### Phase 2: Subprocess Infrastructure & Claude-Assisted Core
**Goal**: Build the subprocess execution layer and implement Steps 3–4 (workflow analysis, pipeline design).

**Milestone**: Steps 1–4 execute end-to-end, producing `portify-analysis.md` and `portify-spec.md`.

#### Tasks
1. **PortifyProcess** (`process.py`) — Extend `ClaudeProcess` from `pipeline.process`. Pass `--add-dir` for work directory and workflow path (R-007 mitigation). Configure `extra_args`, `max_turns`, `@path` file references. Synchronous polling via `threading` + `time.sleep()` (NFR-003).
2. **Prompt builders** (`prompts.py`) — Template functions for Steps 3–7 prompts. Use `@path` references for artifact injection (R-001 mitigation). No inline embedding of large artifacts.
3. **Executor core** (`executor.py`) — Sequential step runner with status tracking, timing measurement, and failure classification. Deterministic flow: Python decides sequencing, Claude handles content only (NFR-006).
4. **Workflow analysis step** (`steps/workflow_analysis.py`, FR-003) — Claude-assisted. Read all discovered components, produce `portify-analysis.md`. STRICT gate with semantic checks (required sections: Source Components, Step Graph, Gates Summary, Data Flow Diagram, Classification Summary). Under 400 lines.
5. **Pipeline design step** (`steps/pipeline_design.py`, FR-004) — Claude-assisted. Convert analysis into `portify-spec.md`. STRICT gate. User review gate (unless `--skip-review`).
6. **Gate definitions for Steps 3–4** — STRICT tier semantic checks. Section presence validation, line count enforcement, sync-only code patterns.
7. **User review gate** (`review.py`) — stderr prompt mechanism (NFR-011). Display file path and summary. `y` continues, `n` emits `USER_REJECTED` status.

#### Deliverables
- [ ] PortifyProcess with `--add-dir` support operational
- [ ] Steps 3–4 produce valid artifacts with all required sections
- [ ] User review gate functional on stderr
- [ ] 5 additional unit tests passing

#### Exit Criteria
- SC-005: Gate tiers enforce correctly for Steps 1–4
- NFR-005: All status from exit codes and artifacts, not Claude self-report
- NFR-006: Python controls all sequencing

---

### Phase 3: Spec Synthesis & Skill Integration
**Goal**: Implement Steps 5–6 (spec synthesis, brainstorm gap analysis) including skill reuse and template instantiation.

**Milestone**: `portify-release-spec.md` generated with zero placeholders, brainstorm findings incorporated.

#### Tasks
1. **Spec synthesis step** (`steps/synthesize_spec.py`, FR-005) — Instantiate the 9KB release spec template from `src/superclaude/examples/release-spec-template.md`. Populate all sections from Phase 1–2 outputs via `@path`. STRICT gate: zero `{{SC_PLACEHOLDER:*}}` sentinels (SC-003). Retry prompt includes specific remaining placeholder names on failure.
2. **Template loader** — Read and validate template existence. Fail fast with clear error if template path is unstable (Open Question 8).
3. **Brainstorm gap analysis step** (`steps/brainstorm_gaps.py`, FR-006) — Pre-flight check for `/sc:brainstorm` skill availability. Invoke via subprocess. Post-process findings into structured format `{gap_id, description, severity, affected_section, persona}`. Incorporate actionable findings as `[INCORPORATED]`, route unresolvable to Section 11 as `[OPEN]`. Append Section 12 summary. STANDARD gate: Section 12 requires findings table or zero-gap summary text, not just heading. Inline fallback if skill unavailable.
4. **Gate definitions for Steps 5–6** — STRICT for synthesis, STANDARD for brainstorm. Sentinel scanner for SC-003. Section 12 content validator.
5. **FR consolidation mapping** — Ensure synthesized spec contains explicit mapping of 7 FRs to pipeline steps.

#### Deliverables
- [ ] Template instantiation with zero remaining placeholders
- [ ] Brainstorm skill invocation with pre-flight check and fallback
- [ ] Section 12 properly populated (findings or zero-gap summary)
- [ ] 3 additional unit tests passing

#### Exit Criteria
- SC-003: Zero `{{SC_PLACEHOLDER:*}}` sentinels
- NFR-010: Brainstorm invokes `/sc:brainstorm` (verified by prompt inspection)

---

### Phase 4: Convergence Loop & Panel Review
**Goal**: Implement Step 7 (panel review with convergence), the most architecturally complex component.

**Milestone**: Convergence loop terminates correctly (CONVERGED or ESCALATED), producing quality scores and downstream readiness assessment.

#### Tasks
1. **Convergence executor** (`convergence.py`) — Iteration manager with TurnLedger budget guard (R-002 mitigation). Each iteration: invoke `/sc:spec-panel --focus correctness,architecture`, run both focus (discussion) and critique in a single subprocess (R-009/GAP-006). Independent timeout per iteration (default 300s). Parse `panel-report.md` for convergence markers. Terminal states: CONVERGED (0 unaddressed CRITICALs), ESCALATED (max iterations reached), BUDGET_EXHAUSTED, TIMEOUT.
2. **Panel review step** (`steps/panel_review.py`, FR-007) — Pre-flight skill check. Additive-only spec modifications (NFR-008). Quality score computation: overall = mean(clarity, completeness, testability, consistency) with <0.01 tolerance (SC-010). Downstream readiness: `overall >= 7.0` → true, `6.9` → false (SC-012).
3. **Convergence predicate** — Parse string literals from panel report. Fallback to structural checks if markers in different format (R-003 mitigation).
4. **Budget estimation** — Pre-launch guard estimates token cost per iteration. Prevent launch if remaining budget insufficient for even one iteration.
5. **Gate definition for Step 7** — STRICT tier. Machine-readable convergence block validation. Quality score boundary checks. User review gate at end.
6. **Resume support** — On convergence failure, preserve `focus-findings.md` for context injection on resume (F-006). Reset convergence counter to 1.

#### Deliverables
- [ ] Convergence loop terminates correctly in all terminal states
- [ ] Quality scores computed per SC-010 formula
- [ ] Downstream readiness boundary verified (SC-012)
- [ ] 4 additional unit tests passing

#### Exit Criteria
- SC-004: CONVERGED when 0 CRITICALs, ESCALATED after max
- SC-010: Overall = mean(4 dimensions), tolerance <0.01
- SC-012: 7.0 → true, 6.9 → false
- NFR-008: Additive-only modifications verified

---

### Phase 5: Integration, Monitoring & Validation
**Goal**: Wire everything together, add TUI monitoring, implement resume support, run full integration tests.

**Milestone**: SC-001 achieved — end-to-end pipeline completes for `sc-cleanup-audit` workflow producing `downstream_ready: true`.

#### Tasks
1. **Rich TUI monitor** (`monitor.py`) — Live dashboard with step progress, timing, gate status. JSONL event extraction from subprocess output (Open Question GAP-008 — define minimal signal vocabulary: `STEP_START`, `STEP_COMPLETE`, `GATE_PASS`, `GATE_FAIL`, `CONVERGENCE_ITERATION`).
2. **Dual logging** (`logging.py`) — JSONL machine-readable + Markdown human-readable execution logs.
3. **Resume command** (`resume.py`) — Generate resume CLI invocation on resumable failures (SC-006). Load partial state, skip completed steps, re-execute from failure point. Handle Open Question GAP-005: re-run failed step entirely (don't trust partial artifacts).
4. **Diagnostics** (`diagnostics.py`) — Failure classification (gate failure, subprocess crash, budget exhaustion, timeout, user rejection). Structured error output.
5. **Integration testing** — 5 integration tests (SC-014):
   - End-to-end with `sc-cleanup-audit` workflow
   - `--dry-run` mode
   - Resume from mid-pipeline failure
   - Convergence loop (CONVERGED path)
   - Convergence loop (ESCALATED path)
6. **Remaining unit tests** — Bring total to 17 (SC-013).
7. **NFR verification sweep**:
   - `grep -r "async def\|await" src/superclaude/cli/cli_portify/` → zero results (SC-009)
   - `git diff pipeline/ sprint/` → zero changes (SC-011)
   - Gate signature audit → all `tuple[bool, str]` (NFR-004)
8. **Timing validation** — Measure Phase 3 <10min (NFR-001), Phase 4 <15min (NFR-002). Advisory warnings only.
9. **`--model` propagation** — Resolve Open Question 9: propagate to all Claude subprocesses uniformly.

#### Deliverables
- [ ] Full pipeline executes end-to-end for `sc-cleanup-audit`
- [ ] TUI monitor renders step progress live
- [ ] Resume from failure works correctly
- [ ] 17 unit tests + 5 integration tests passing
- [ ] All 14 success criteria verified

#### Exit Criteria
- SC-001: End-to-end completion with `downstream_ready: true`
- SC-013: 17 unit tests pass
- SC-014: 5 integration tests pass
- All NFRs verified

---

## 3. Risk Assessment & Mitigation

| ID | Risk | Severity | Likelihood | Mitigation | Phase |
|----|------|----------|------------|------------|-------|
| R-001 | Claude truncates output in large context windows | High | Medium | `@path` references instead of inline; generous `max_turns` | P2 |
| R-002 | Budget exhaustion before convergence completes | Medium | Medium | TurnLedger pre-launch guards; per-iteration budget estimation | P4 |
| R-003 | Skills don't produce machine-readable markers | Medium-High | Medium | Post-processing with structural fallback parsing | P4 |
| R-004 | Long wall-clock time from sequential execution | Low-Impact | High | Advisory timing; 7 steps (reduced from 12); non-blocking | P5 |
| R-005 | Self-portification circularity | Low | Low | Source skills read-only during portification | P1 |
| R-006 | Skills not installed, subprocess fails | High-Impact | Low | Pre-flight `claude` binary + skill availability checks | P2, P3 |
| R-007 | Subprocess can't read `@path` outside scope | Medium | Medium | `--add-dir` for work dir and workflow path | P2 |
| R-008 | User review gate lacks programmatic interaction | Medium | Low | `--skip-review` flag; stderr prompt with clear instructions | P2 |
| R-009 | Wrong mode mapping in convergence iterations | High | Medium | Single subprocess per iteration runs both focus + critique | P4 |

**Architectural risk not in inventory**: Template path stability (Open Question 8). Mitigate by validating template existence at config validation time (Phase 1) and failing fast with actionable error.

---

## 4. Resource Requirements & Dependencies

### Internal Dependencies (Must Exist Before Phase 1)
| Dependency | Module | Used By | Verified |
|------------|--------|---------|----------|
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

## 5. Success Criteria Validation Approach

| Criterion | Validation Method | Phase |
|-----------|------------------|-------|
| SC-001 | Integration test: end-to-end `sc-cleanup-audit` | P5 |
| SC-002 | Integration test: `--dry-run` halts after P2 | P1 |
| SC-003 | Gate semantic check: `grep "{{SC_PLACEHOLDER"` → 0 | P3 |
| SC-004 | Unit test: convergence terminal states | P4 |
| SC-005 | Unit tests: each gate enforces correct tier | P1–P4 |
| SC-006 | Integration test: resume from failure | P5 |
| SC-007 | Unit tests: contract YAML on all paths | P1 |
| SC-008 | Timing assertion in unit tests | P1 |
| SC-009 | `grep -r "async def\|await" cli_portify/` → 0 | P5 |
| SC-010 | Unit test: mean calculation with tolerance | P4 |
| SC-011 | `git diff pipeline/ sprint/` → empty | P5 |
| SC-012 | Unit test: boundary 7.0 true, 6.9 false | P4 |
| SC-013 | `uv run pytest tests/cli_portify/ -v` → 17 pass | P5 |
| SC-014 | `uv run pytest tests/cli_portify/integration/ -v` → 5 pass | P5 |

---

## 6. Timeline Estimates

| Phase | Duration | Cumulative | Key Risk |
|-------|----------|------------|----------|
| **P1**: Foundation | 3–4 days | Week 1 | Dependency API verification |
| **P2**: Subprocess & Core Steps | 4–5 days | Week 2 | PortifyProcess `--add-dir` integration |
| **P3**: Synthesis & Skills | 3–4 days | Week 2–3 | Template stability, skill availability |
| **P4**: Convergence Loop | 4–5 days | Week 3 | Budget estimation accuracy, marker parsing |
| **P5**: Integration & Validation | 3–4 days | Week 3–4 | End-to-end timing, flaky subprocess behavior |

**Total**: 17–22 working days (3–4 weeks)

**Critical path**: P1 → P2 → P3 → P4 → P5 (fully sequential due to data flow dependencies between steps)

**Parallelization opportunities**:
- Within P1: Models, CLI options, and gate framework can develop concurrently
- Within P2: Prompt builders and executor core are independent until integration
- Within P5: Unit tests and TUI monitor are independent of each other

---

## 7. Open Questions — Recommended Resolutions

| Question | Recommendation | Rationale |
|----------|---------------|-----------|
| GAP-004: Score rounding | Display 1 decimal, compare with `abs(computed - expected) < 0.01` before rounding | Avoids display/comparison mismatch |
| GAP-005: Resume from partial spec | Re-run failed step entirely | Partial artifacts are untrusted; clean re-execution is safer |
| GAP-007: Inline imports | Hoist to module level | Lazy loading unnecessary for `hashlib`/`yaml`; clarity wins |
| GAP-008: Monitor signals | Define 5 event types: `STEP_START`, `STEP_COMPLETE`, `GATE_PASS`, `GATE_FAIL`, `CONVERGENCE_ITERATION` | Minimal viable vocabulary |
| GAP-009: File size limits | Skip files >1MB for line counting; log warning | Prevents pathological cases without over-engineering |
| Open Q7: Review gate UX | Display: step name, artifact path, gate result summary. No timeout (user-paced). | Minimal, actionable information |
| Open Q8: Template location | Validate at config time (Step 1). Fail with specific path in error message. | Fail fast pattern |
| Open Q9: `--model` scope | Propagate to all Claude subprocesses uniformly | Consistent behavior, no step-specific surprises |
| Open Q10: Marker format | Primary: exact string match. Fallback: regex for `CONVERGENCE_STATUS:\s*CONVERGED` | Handles whitespace/formatting variance |
