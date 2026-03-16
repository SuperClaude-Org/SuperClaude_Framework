# TASKLIST INDEX -- Sprint Context Resilience (v2.25.7-Phase8)

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | Sprint Context Resilience (v2.25.7-Phase8) |
| Generator Version | Roadmap->Tasklist Generator v4.0 |
| Generated | 2026-03-16 |
| TASKLIST_ROOT | .dev/releases/current/v2.25.7-Phase8HaltFix/ |
| Total Phases | 6 |
| Total Tasks | 21 |
| Total Deliverables | 23 |
| Complexity Class | MEDIUM |
| Primary Persona | backend |
| Consulting Personas | analyzer, architect |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | TASKLIST_ROOT/tasklist-index.md |
| Phase 1 Tasklist | TASKLIST_ROOT/phase-1-tasklist.md |
| Phase 2 Tasklist | TASKLIST_ROOT/phase-2-tasklist.md |
| Phase 3 Tasklist | TASKLIST_ROOT/phase-3-tasklist.md |
| Phase 4 Tasklist | TASKLIST_ROOT/phase-4-tasklist.md |
| Phase 5 Tasklist | TASKLIST_ROOT/phase-5-tasklist.md |
| Phase 6 Tasklist | TASKLIST_ROOT/phase-6-tasklist.md |
| Execution Log | TASKLIST_ROOT/execution-log.md |
| Checkpoint Reports | TASKLIST_ROOT/checkpoints/ |
| Evidence Directory | TASKLIST_ROOT/evidence/ |
| Artifacts Directory | TASKLIST_ROOT/artifacts/ |
| Validation Reports | TASKLIST_ROOT/validation/ |
| Feedback Log | TASKLIST_ROOT/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | OQ-006 Gate and Env Plumbing | T01.01-T01.04 | STRICT: 2, STANDARD: 1, EXEMPT: 1 |
| 2 | phase-2-tasklist.md | Isolation Lifecycle | T02.01-T02.04 | STRICT: 2, STANDARD: 2 |
| 3 | phase-3-tasklist.md | Prompt Resilience and Context Header | T03.01-T03.03 | STANDARD: 3 |
| 4 | phase-4-tasklist.md | Diagnostics and Status Fixes | T04.01-T04.03 | STRICT: 1, STANDARD: 1, EXEMPT: 1 |
| 5 | phase-5-tasklist.md | Test Suite and Quality Gates | T05.01-T05.04 | STANDARD: 4 |
| 6 | phase-6-tasklist.md | Smoke Validation and Release Gate | T06.01-T06.03 | STRICT: 1, STANDARD: 1, EXEMPT: 1 |

## Source Snapshot

- Phase 8 sprint context resilience through controlled, moderate-complexity change set (complexity score: 0.62)
- 27 requirements (22 functional, 5 non-functional) across 7 modified files with 9+ new tests
- Core problem: phase subprocesses resolve tasklist-index.md via @ references, wasting ~14K tokens per phase
- Solution: per-phase filesystem isolation, env var propagation, sprint context header, PASS_RECOVERED routing fix, FailureClassifier path resolution
- Adversarial debate synthesis: Variant B (Haiku) selected as base with 5 improvements from Variant A (Opus)
- Phase 6 smoke validation is a hard blocking gate — not deferrable under schedule pressure

## Deterministic Rules Applied

- Phase numbering preserved from roadmap (6 explicit phases, sequential, no gaps)
- Roadmap items assigned R-001 through R-033 in appearance order
- Task IDs use T<PP>.<TT> zero-padded format (T01.01 through T06.03)
- Related sub-steps grouped into single tasks when producing one independently deliverable output
- Checkpoint cadence: end-of-phase checkpoints for all phases (no phases exceed 5 tasks)
- No clarification tasks needed — roadmap provides sufficient specificity for all items
- Deliverable IDs assigned D-0001 through D-0023 in task order
- Effort computed via EFFORT_SCORE keyword matching (Section 5.2.1)
- Risk computed via RISK_SCORE keyword matching (Section 5.2.2)
- Tier classification via compound phrase overrides then keyword matching (Section 5.3)
- Verification routing aligned to computed tier (Section 4.10)
- MCP requirements and sub-agent delegation set per tier (Sections 5.5, 5.6)

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Phase 1 | Trace execute_sprint() -> ClaudeProcess -> subprocess launch boundary |
| R-002 | Phase 1 | Identify where @ reference resolution occurs |
| R-003 | Phase 1 | Test env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)} as the candidate mechanism |
| R-004 | Phase 1 | Confirm or falsify; document subprocess cwd as the explicit fallback if env var is ineffective |
| R-005 | Phase 1 | Validate current interfaces: ClaudeProcess.__init__(), build_env(), execute_sprint() |
| R-006 | Phase 1 | Perform codebase grep for all PhaseStatus.PASS handling sites to identify PASS_RECOVERED parity gaps |
| R-007 | Phase 1 | Add env_vars: dict[str, str] | None = None keyword-only parameter to ClaudeProcess.__init__() |
| R-008 | Phase 1 | Store as self._extra_env_vars, wire through to build_env() call |
| R-009 | Phase 1 | Add env_vars: dict[str, str] | None = None keyword-only parameter to build_env() |
| R-010 | Phase 1 | Implement merge semantics: env.update(env_vars) after os.environ.copy() (override semantics) |
| R-011 | Phase 1 | Verify all existing call sites remain valid (keyword-only with None default = no breakage) |
| R-012 | Phase 2 | Add startup orphan cleanup before the phase loop: shutil.rmtree(config.results_dir / ".isolation", ignore_errors=True) |
| R-013 | Phase 2 | Create config.results_dir / ".isolation" / f"phase-{phase.number}" |
| R-014 | Phase 2 | Copy only phase.file via shutil.copy2(phase.file, isolation_dir / phase.file.name) |
| R-015 | Phase 2 | Pass the isolation path into the subprocess boundary using the mechanism confirmed in M1.0 |
| R-016 | Phase 2 | In per-phase finally block: shutil.rmtree(isolation_dir, ignore_errors=True) |
| R-017 | Phase 3 | Update build_prompt() to add ## Sprint Context section containing sprint name, phase N of M |
| R-018 | Phase 3 | Extend detect_prompt_too_long() with error_path: Path | None = None; scan error_path using same logic |
| R-019 | Phase 3 | Extend _determine_phase_status() with error_file: Path | None = None; forward to detect_prompt_too_long() |
| R-020 | Phase 3 | Update execute_sprint() call site to pass config.error_file(phase) |
| R-021 | Phase 4 | Add PhaseStatus.PASS_RECOVERED to the INFO routing branch in SprintLogger.write_phase_result() |
| R-022 | Phase 4 | Add config: SprintConfig | None = None keyword-only parameter to DiagnosticBundle |
| R-023 | Phase 4 | Replace hardcoded output-file path construction with bundle.config.output_file(bundle.phase_result.phase) in FailureClassifier |
| R-024 | Phase 4 | PASS_RECOVERED grep audit: grep all PhaseStatus.PASS switch sites for PASS_RECOVERED parity |
| R-025 | Phase 5 | Create tests/sprint/test_phase8_halt_fix.py with TestIsolationWiring (T04.01-T04.04): isolation directory lifecycle |
| R-026 | Phase 5 | TestPromptAndContext (T04.05-T04.07): build_prompt() Sprint Context header, detect_prompt_too_long() error_path |
| R-027 | Phase 5 | TestFixesAndDiagnostics (T04.08-T04.10): PASS_RECOVERED routing, FailureClassifier config path, error_file plumbing |
| R-028 | Phase 5 | Run validation: pytest tests/sprint/test_phase8_halt_fix.py -v, pytest tests/ -v --tb=short, ruff check, ruff format --check |
| R-029 | Phase 6 | Manual smoke test: trigger context exhaustion on a phase approaching prompt limits, verify PASS_RECOVERED |
| R-030 | Phase 6 | Verify tasklist-index.md is not resolvable by the isolated subprocess |
| R-031 | Phase 6 | Verify no stale .isolation/phase-* directories remain after execution |
| R-032 | Phase 6 | Final diff review against all 7 modified files |
| R-033 | Phase 6 | Document release-ready conclusion |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001, R-002, R-003, R-004, R-005 | OQ-006 resolution document: confirmed mechanism (env var or cwd) | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0001/spec.md | M | Medium |
| D-0002 | T01.01 | R-006 | PhaseStatus.PASS grep audit inventory for PASS_RECOVERED parity | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0002/notes.md | M | Medium |
| D-0003 | T01.02 | R-007, R-008 | env_vars keyword-only parameter on ClaudeProcess.__init__() with _extra_env_vars storage | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0003/evidence.md | S | Low |
| D-0004 | T01.03 | R-009, R-010 | env_vars keyword-only parameter on build_env() with override merge semantics | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0004/evidence.md | S | Low |
| D-0005 | T01.04 | R-011 | End-to-end propagation trace confirming existing call sites unaffected | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0005/evidence.md | XS | Low |
| D-0006 | T02.01 | R-012 | Startup orphan cleanup in execute_sprint() before phase loop | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0006/evidence.md | S | Low |
| D-0007 | T02.02 | R-013, R-014 | Per-phase isolation directory creation with single-file copy | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0007/evidence.md | M | Medium |
| D-0008 | T02.03 | R-015 | Isolation path passed to subprocess via M1.0-confirmed mechanism | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0008/evidence.md | M | Medium |
| D-0009 | T02.04 | R-016 | Per-phase finally-block cleanup with ignore_errors=True | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0009/evidence.md | S | Low |
| D-0010 | T03.01 | R-017 | build_prompt() emits ## Sprint Context section with sprint name, phase N/M, artifact root, prior-phase dirs | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0010/evidence.md | S | Low |
| D-0011 | T03.02 | R-018 | detect_prompt_too_long() accepts error_path parameter and scans it with same last-10-lines logic | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0011/evidence.md | S | Low |
| D-0012 | T03.03 | R-019, R-020 | _determine_phase_status() accepts error_file and forwards to detect_prompt_too_long(); execute_sprint() passes config.error_file(phase) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0012/evidence.md | S | Low |
| D-0013 | T04.01 | R-021 | PASS_RECOVERED added to INFO routing branch in SprintLogger.write_phase_result() | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0013/evidence.md | XS | Low |
| D-0014 | T04.02 | R-022 | DiagnosticBundle accepts config: SprintConfig | None = None with deprecation warning on None | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0014/evidence.md | M | Low |
| D-0015 | T04.02 | R-023 | FailureClassifier.classify() uses bundle.config.output_file() instead of hardcoded path | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0015/evidence.md | M | Low |
| D-0016 | T04.03 | R-024 | PASS_RECOVERED parity audit document: all PhaseStatus.PASS switch sites checked | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0016/notes.md | S | Low |
| D-0017 | T05.01 | R-025 | TestIsolationWiring class with 4 tests (T04.01-T04.04) in test_phase8_halt_fix.py | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0017/evidence.md | M | Low |
| D-0018 | T05.02 | R-026 | TestPromptAndContext class with 3 tests (T04.05-T04.07) in test_phase8_halt_fix.py | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0018/evidence.md | S | Low |
| D-0019 | T05.03 | R-027 | TestFixesAndDiagnostics class with 3 tests (T04.08-T04.10) in test_phase8_halt_fix.py | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0019/evidence.md | M | Low |
| D-0020 | T05.04 | R-028 | Validation suite passing: 10 new tests + full regression + ruff lint + ruff format | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0020/evidence.md | S | Low |
| D-0021 | T06.01 | R-029 | Smoke test evidence: PASS_RECOVERED visible in operator output during context exhaustion | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0021/evidence.md | S | Medium |
| D-0022 | T06.02 | R-030, R-031 | Isolation enforcement evidence: tasklist-index.md unreachable, no stale .isolation dirs | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0022/evidence.md | S | Medium |
| D-0023 | T06.03 | R-032, R-033 | Release-ready document with diff review across 7 files | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0023/spec.md | S | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001, R-002, R-003, R-004, R-005 | T01.01 | D-0001 | EXEMPT | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0001/spec.md |
| R-006 | T01.01 | D-0002 | EXEMPT | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0002/notes.md |
| R-007, R-008 | T01.02 | D-0003 | STRICT | [█████████░] 90% | TASKLIST_ROOT/artifacts/D-0003/evidence.md |
| R-009, R-010 | T01.03 | D-0004 | STRICT | [█████████░] 90% | TASKLIST_ROOT/artifacts/D-0004/evidence.md |
| R-011 | T01.04 | D-0005 | STANDARD | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0005/evidence.md |
| R-012 | T02.01 | D-0006 | STANDARD | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0006/evidence.md |
| R-013, R-014 | T02.02 | D-0007 | STRICT | [█████████░] 90% | TASKLIST_ROOT/artifacts/D-0007/evidence.md |
| R-015 | T02.03 | D-0008 | STRICT | [█████████░] 90% | TASKLIST_ROOT/artifacts/D-0008/evidence.md |
| R-016 | T02.04 | D-0009 | STANDARD | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0009/evidence.md |
| R-017 | T03.01 | D-0010 | STANDARD | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0010/evidence.md |
| R-018 | T03.02 | D-0011 | STANDARD | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0011/evidence.md |
| R-019, R-020 | T03.03 | D-0012 | STANDARD | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0012/evidence.md |
| R-021 | T04.01 | D-0013 | STANDARD | [█████████░] 90% | TASKLIST_ROOT/artifacts/D-0013/evidence.md |
| R-022 | T04.02 | D-0014 | STRICT | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0014/evidence.md |
| R-023 | T04.02 | D-0015 | STRICT | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0015/evidence.md |
| R-024 | T04.03 | D-0016 | EXEMPT | [████████░░] 80% | TASKLIST_ROOT/artifacts/D-0016/notes.md |
| R-025 | T05.01 | D-0017 | STANDARD | [█████████░] 90% | TASKLIST_ROOT/artifacts/D-0017/evidence.md |
| R-026 | T05.02 | D-0018 | STANDARD | [█████████░] 90% | TASKLIST_ROOT/artifacts/D-0018/evidence.md |
| R-027 | T05.03 | D-0019 | STANDARD | [█████████░] 90% | TASKLIST_ROOT/artifacts/D-0019/evidence.md |
| R-028 | T05.04 | D-0020 | STANDARD | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0020/evidence.md |
| R-029 | T06.01 | D-0021 | STANDARD | [████████░░] 80% | TASKLIST_ROOT/artifacts/D-0021/evidence.md |
| R-030, R-031 | T06.02 | D-0022 | STRICT | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0022/evidence.md |
| R-032, R-033 | T06.03 | D-0023 | EXEMPT | [████████░░] 85% | TASKLIST_ROOT/artifacts/D-0023/spec.md |

## Execution Log Template

**Intended Path:** TASKLIST_ROOT/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run | Result | Evidence Path |
|---|---:|---|---:|---|---|---|---|

## Checkpoint Report Template

- `# Checkpoint Report -- <Checkpoint Title>`
- `**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/<deterministic-name>.md`
- `**Scope:** <tasks covered>`
- `## Status`
  - `Overall: Pass | Fail | TBD`
- `## Verification Results` (exactly 3 bullets)
- `## Exit Criteria Assessment` (exactly 3 bullets)
- `## Issues & Follow-ups`
- `## Evidence`

## Feedback Collection Template

**Intended Path:** TASKLIST_ROOT/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|

## Generation Notes

- No clarification tasks generated — roadmap provides full specificity for all 27 requirements
- Phase numbering preserved as-is (1-6, no gaps)
- T01.01 classified as EXEMPT due to investigation/exploration nature (read-only, analyze, review keywords)
- T04.03 classified as EXEMPT due to grep audit being a read-only analysis operation
- T06.03 classified as EXEMPT due to review/document nature
- Phases 3 and 4 are parallelizable per roadmap (no dependency on Phase 2)
- Roadmap test naming (T04.01-T04.10) refers to test IDs within test_phase8_halt_fix.py, not tasklist task IDs
