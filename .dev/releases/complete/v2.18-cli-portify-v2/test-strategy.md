---
validation_milestones: 16
interleave_ratio: '1:3'
---

# Test Strategy: v2.18 CLI Portify v2

## 1. Validation Milestones Mapped to Roadmap Phases

### Phase 1: Foundation and Prerequisite Remediation

| VM | Milestone | What Is Validated | Pass Criteria |
|----|-----------|-------------------|---------------|
| VM-01 | M1.1 Ref File API Alignment | Ref files match live API | `diff` between ref field names and live `models.py`/`gates.py` signatures produces zero mismatches |
| VM-02 | M1.2 Command/Protocol Split | Directory structure, command shim, YAML frontmatter | `make verify-sync` passes; command shim parses all 5 arguments; `Skill sc:cli-portify-protocol` invocation present |
| VM-03 | M1.3 Open Question Resolution | All 10 OQs documented | `decisions.yaml` contains entries for all 6 blocking OQs (002, 003, 004, 007, 008, 010) |

### Phase 2: Contract Infrastructure, Phase 0, and Phase 1

| VM | Milestone | What Is Validated | Pass Criteria |
|----|-----------|-------------------|---------------|
| VM-04 | M2.1 Contract Infrastructure | Schema definitions, resume protocol | Contract YAML round-trips through validation; synthetic failure produces resumable state with correct null fields |
| VM-05 | M2.2 Phase 0 Prerequisites | Workflow resolution, API snapshot, collision check, unsupported-pattern scan | Valid `portify-prerequisites.yaml` emitted for test workflow; unsupported pattern in test input aborts before Phase 1 |
| VM-06 | M2.3 Phase 1 Analysis | Component inventory, step decomposition, DAG, gate assignment, 7 self-checks | Valid `portify-analysis.yaml` with conservation invariant holding; all 6 blocking checks pass |
| VM-07 | M2.4 TodoWrite Integration | 23 subphase tasks tracked | Task count == 23; checkpoint triggers fire at phase completion and on failure |

### Phase 3: Phase 2 Implementation (Design)

| VM | Milestone | What Is Validated | Pass Criteria |
|----|-----------|-------------------|---------------|
| VM-08 | M3.1 Step Graph Design | Step mapping, coverage invariant | `|source_step_registry| == |mapped_steps| + |elimination_records|`; all elimination records have source_id, reason, approved_by |
| VM-09 | M3.2 Model and Gate Design | Dataclass conformance, gate field names | All gate designs reference correct `GateCriteria` fields from API snapshot; `SemanticCheck` uses `Callable[[str], bool]` |
| VM-10 | M3.3 Prompt and Executor Design | Pattern coverage matrix, executor design | 100% pattern coverage for test workflow; no unsupported patterns |
| VM-11 | M3.4 Phase 2 Output | `portify-spec.yaml`, 8 self-checks | 7 blocking checks pass; spec YAML parseable with all required sections |

### Phase 4: Code Generation and Integration

| VM | Milestone | What Is Validated | Pass Criteria |
|----|-----------|-------------------|---------------|
| VM-12 | M4.1 Code Generation Engine | 12 Python files, AST validity, imports, cross-file checks | All files pass `ast.parse()`; import graph acyclic; `__init__.py` exports match; step count matches spec |
| VM-13 | M4.2 CLI Integration | main.py patch, smoke test, structural test, summary | Module imports; Click command group exists; command name registered; `test_<name>_structure.py` passes |
| VM-14 | M4.3 Name Normalization | Naming conventions, collision policy | kebab/snake/Pascal/UPPER_SNAKE derivations correct; collision on non-portified code aborts |

### Phase 5: Validation, Testing, and Cleanup

| VM | Milestone | What Is Validated | Pass Criteria |
|----|-----------|-------------------|---------------|
| VM-15 | M5.1–M5.3 End-to-End | Golden fixtures, negative paths, MCP degradation, resume | 4 golden + 4 negative fixtures pass; MCP degradation produces warnings not failures; resume works from every phase boundary |
| VM-16 | M5.4 Final Cleanup | Sync, regression, lint | `make verify-sync` passes; `make test` passes; `make lint` clean; old `sc-cli-portify/` removed |

---

## 2. Test Categories

### 2.1 Unit Tests

**Scope**: Individual functions and classes in isolation. No cross-phase dependencies.

| Test Group | Target | Count Est. | Priority |
|------------|--------|-----------|----------|
| `test_contract_schema.py` | YAML contract validation, schema versioning, null-field policy, common header parsing | 12–15 | P0 |
| `test_name_normalization.py` | kebab-case, snake_case, PascalCase, UPPER_SNAKE derivation; prefix/suffix stripping | 8–10 | P1 |
| `test_collision_policy.py` | portify-summary.md marker detection; overwrite/abort logic for portified vs non-portified | 6–8 | P0 |
| `test_error_codes.py` | 6 input validation error codes (MISSING_WORKFLOW through DERIVATION_FAILED) | 6 | P1 |
| `test_pattern_detection.py` | 4 unsupported patterns (recursive self-orchestration, interactive mid-pipeline, no stable boundaries, dynamic eval) | 8–10 | P0 |
| `test_step_classification.py` | pure_programmatic / claude_assisted / hybrid classification with confidence scoring | 10–12 | P1 |
| `test_conservation_invariant.py` | `|source_step_registry| == |mapped_steps| + |elimination_records|` equation | 5–6 | P0 |
| `test_dag_validation.py` | Dependency DAG acyclicity, trailing gate safety escalation | 6–8 | P1 |
| `test_ast_validation.py` | `ast.parse()` per-file check, import path verification, base class contract check, GateCriteria field matching, SemanticCheck signature | 10–12 | P0 |
| `test_cross_file_validation.py` | Module completeness (12 files), circular import detection, `__init__.py` export matching, step count matching | 8 | P0 |
| `test_resume_protocol.py` | Contract read, phase skip logic, re-validation of completed contracts, resume_command generation | 8–10 | P1 |
| `test_api_snapshot.py` | Signature extraction from models.py/gates.py, hash computation, hash comparison | 5–6 | P0 |

**Total unit tests**: ~92–113

### 2.2 Integration Tests

**Scope**: Cross-component interactions within and between phases.

| Test Group | What It Validates | Priority |
|------------|-------------------|----------|
| `test_phase0_to_phase1.py` | Phase 0 emits valid `portify-prerequisites.yaml` → Phase 1 reads and validates it → proceeds or rejects | P0 |
| `test_phase1_to_phase2.py` | Phase 1 emits `portify-analysis.yaml` → Phase 2 reads, validates, builds step graph | P0 |
| `test_phase2_to_phase3.py` | Phase 2 emits `portify-spec.yaml` → Phase 3 reads and generates code in dependency order | P0 |
| `test_phase3_to_phase4.py` | Phase 3 emits `portify-codegen.yaml` + generated files → Phase 4 patches main.py, runs smoke test | P0 |
| `test_contract_chain.py` | Full contract chain from Phase 0 through return contract; all contracts parseable and cross-referenced | P1 |
| `test_main_py_patching.py` | `app.add_command()` insertion into real main.py; import added; no duplication on re-run | P0 |
| `test_stale_ref_blocking.py` | Deliberately stale ref files block before Phase 1 with actionable error message | P0 |
| `test_api_drift_detection.py` | Modified API signatures between snapshot and generation trigger blocking error at conformance check | P0 |
| `test_sync_layout.py` | `src/superclaude/skills/sc-cli-portify-protocol/` and `.claude/skills/sc-cli-portify-protocol/` match | P1 |

**Total integration tests**: ~9 groups, ~30–40 individual test cases

### 2.3 End-to-End Tests (Golden Fixtures)

**Scope**: Complete pipeline execution against representative workflows.

| Fixture | Workflow Characteristics | Expected Outcome | SC Validated |
|---------|------------------------|------------------|-------------|
| **GF-01**: Simple sequential skill | Linear steps, all pure_programmatic and claude_assisted, no parallel groups | Full pipeline success; 12 Python files generated; CLI command registered | SC-001–010 |
| **GF-02**: Batched audit skill | Parallel step groups, trailing gates, complex DAG, N:1 mappings | Full pipeline success; ThreadPoolExecutor in executor; trailing→blocking escalation exercised | SC-001–010, SC-007 |
| **GF-03**: Adversarial multi-agent | Multi-domain, high step count, N:1 mappings, low-confidence classifications | Success after user overrides; all conservation invariants hold | SC-001–010, SC-007, SC-013 |
| **GF-04**: Intentionally unsupported | Contains dynamic code gen pattern | Abort in Phase 0; return contract with `status: "failed"`, `failure_phase: 0`, `failure_type: "UNSUPPORTED_PATTERN"` | SC-010, SC-011 |

**Negative-path fixtures**:

| Fixture | Scenario | Expected Behavior | Risk Mitigated |
|---------|----------|-------------------|----------------|
| **NF-01**: Stale refs | Ref files with wrong field names | Blocks before Phase 1 with `STALE_REF` error | RISK-002 |
| **NF-02**: API drift | API signatures change post-snapshot | Blocks at conformance check with hash mismatch error | RISK-001 |
| **NF-03**: Name collision | Pre-existing non-portified code at output | Aborts with `NAME_COLLISION` error; no files written | RISK-008 |
| **NF-04**: Non-portified collision | Human-written code at output path without marker | Never overwrites; aborts with `NON_PORTIFIED_COLLISION` | RISK-012 |

**Determinism assertion**: Run GF-01 and GF-02 twice each. Diff `source_step_registry`, `step_mapping`, `module_plan` — must be identical (SC-002).

**Total E2E tests**: 8 fixtures, ~40–50 assertions

### 2.4 Acceptance Tests

Mapped directly to the 14 success criteria. Each acceptance test is a composite assertion across multiple lower-level tests.

| Acceptance Test | SC | Verification Method |
|----------------|-----|---------------------|
| AT-01: Phase halt/resume | SC-001 | Simulate failures at all 4 phase boundaries; verify resumable state and correct `failure_type` |
| AT-02: Deterministic output | SC-002 | Repeat GF-01 and GF-02; diff three enumerated artifacts |
| AT-03: AST validity | SC-003 | `ast.parse()` on every `.py` file generated by GF-01, GF-02, GF-03 |
| AT-04: Acyclic imports | SC-004 | Import graph analysis on generated modules from all successful golden fixtures |
| AT-05: GateCriteria match | SC-005 | Grep generated code for `GateCriteria` instantiations; verify field names against snapshot |
| AT-06: SemanticCheck signature | SC-006 | Grep generated code for `SemanticCheck`; verify `Callable[[str], bool]` |
| AT-07: Step conservation | SC-007 | Assert equation at Phase 1 and Phase 2 outputs for all golden fixtures |
| AT-08: Module import | SC-008 | `import <generated_module>` succeeds in clean Python process |
| AT-09: Click command | SC-009 | `app.commands` contains expected command name after patching |
| AT-10: Return contract always emitted | SC-010 | Verify contract exists after GF-01 (success), GF-04 (failure), NF-01–NF-04 (all failures) |
| AT-11: Unsupported abort | SC-011 | GF-04 aborts in Phase 0, not later |
| AT-12: Non-portified safety | SC-012 | NF-04 never overwrites |
| AT-13: TodoWrite tracking | SC-013 | Count TodoWrite tasks == 23 during GF-01 execution |
| AT-14: Golden fixtures pass | SC-014 | All 8 fixtures (4 positive + 4 negative) produce expected outcomes |

---

## 3. Test-Implementation Interleaving Strategy

### Ratio: 1:3 (1 test task per 3 implementation tasks)

The interleaving follows a **test-alongside** pattern, not test-after. Each milestone produces testable artifacts, and tests are written within the same milestone, not deferred.

### Per-Phase Interleaving Schedule

```
Phase 1 (2-3 sessions):
  Session 1:
    [IMPL] M1.1 — Update ref files against live API
    [IMPL] M1.2 — Create protocol directory, command shim
    [TEST] Write test_contract_schema.py stubs + test_collision_policy.py
  Session 2:
    [IMPL] M1.2 — YAML frontmatter, verify-sync coverage
    [IMPL] M1.3 — Resolve OQs, write decisions.yaml
    [TEST] Write test_name_normalization.py, test_error_codes.py
  Session 3 (if needed):
    [TEST] VM-01 through VM-03 validation pass

Phase 2 (3-4 sessions):
  Session 1:
    [IMPL] M2.1 — Contract schemas, versioning policy
    [IMPL] M2.1 — Resume protocol implementation
    [TEST] Write test_resume_protocol.py, test_contract_schema.py (full)
  Session 2:
    [IMPL] M2.2 — Phase 0 prerequisite scanning
    [TEST] Write test_api_snapshot.py, test_pattern_detection.py
    [TEST] Write test_phase0_to_phase1.py (integration)
  Session 3:
    [IMPL] M2.3 — Phase 1 workflow analysis
    [IMPL] M2.4 — TodoWrite integration
    [TEST] Write test_step_classification.py, test_dag_validation.py, test_conservation_invariant.py
  Session 4:
    [TEST] VM-04 through VM-07 validation pass
    [TEST] Write test_stale_ref_blocking.py (integration)

Phase 3 (3-4 sessions):
  Session 1:
    [IMPL] M3.1 — Step graph design
    [IMPL] M3.2 — Model and gate design
    [TEST] Extend test_conservation_invariant.py for Phase 2 coverage invariant
  Session 2:
    [IMPL] M3.3 — Prompt and executor design
    [IMPL] M3.4 — Self-validation and output
    [TEST] Write test_phase1_to_phase2.py, test_phase2_to_phase3.py (integration)
  Session 3:
    [PREP] Define golden fixture input workflows (GF-01 through GF-04, NF-01 through NF-04)
    [TEST] VM-08 through VM-11 validation pass

Phase 4 (4-5 sessions):
  Session 1:
    [IMPL] M4.1 — Code generation engine (models, gates, prompts, config)
    [TEST] Write test_ast_validation.py (incremental, per-file)
  Session 2:
    [IMPL] M4.1 — Code generation (monitor, process, executor, tui, logging_, diagnostics, commands, __init__)
    [TEST] Write test_cross_file_validation.py
  Session 3:
    [IMPL] M4.2 — CLI integration, smoke test, structural test generation
    [TEST] Write test_main_py_patching.py, test_phase3_to_phase4.py
  Session 4:
    [IMPL] M4.3 — Name normalization, collision policy enforcement
    [TEST] VM-12 through VM-14 validation pass
  Session 5 (if needed):
    [TEST] Fix failures from VM-12–14; finalize integration tests

Phase 5 (2-3 sessions):
  Session 1:
    [TEST] Execute GF-01 through GF-04 (golden fixtures)
    [TEST] Execute NF-01 through NF-04 (negative-path fixtures)
    [TEST] MCP degradation testing (M5.2, parallel)
  Session 2:
    [TEST] Resume protocol validation (M5.3, parallel)
    [TEST] Determinism check (run GF-01, GF-02 twice, diff)
    [TEST] Acceptance tests AT-01 through AT-14
  Session 3:
    [IMPL] M5.4 — Cleanup old directory, final sync/test/lint
    [TEST] VM-15, VM-16 final validation pass
```

### Interleaving Rules

1. **No phase exit without its tests passing** — VM checks are mandatory gates.
2. **Unit tests written in same session as implementation** — never deferred to next session.
3. **Integration tests written one session after both connected phases exist** — e.g., `test_phase0_to_phase1.py` written in Phase 2 Session 2, after Phase 0 implementation completes.
4. **Golden fixtures defined in Phase 3** (input data and expected outputs), **executed in Phase 5** (after code generation exists).
5. **Negative-path fixtures run alongside golden fixtures** — same session, parallel execution where possible.

---

## 4. Risk-Based Test Prioritization

### P0 — Must-Have (Block Release)

These tests address high-severity risks and core correctness invariants.

| Test | Risk/SC | Rationale |
|------|---------|-----------|
| `test_ast_validation.py` | RISK-005, SC-003 | Broken Python = unusable output |
| `test_cross_file_validation.py` | RISK-005, SC-004 | Circular imports = import failure at runtime |
| `test_api_snapshot.py` + `test_api_drift_detection.py` | RISK-001, SC-005 | API drift = wrong field names in all generated code |
| `test_stale_ref_blocking.py` | RISK-002, NFR-018 | Stale refs = wrong templates used throughout |
| `test_collision_policy.py` | RISK-008, RISK-012, SC-012, NFR-013 | Data loss if non-portified code overwritten |
| `test_conservation_invariant.py` | RISK-004, SC-007 | Steps lost or duplicated = incorrect pipeline |
| `test_pattern_detection.py` | RISK-003, SC-011 | Unsupported pattern not caught = wasted work + broken output |
| `test_contract_schema.py` | NFR-009, NFR-015, SC-010 | Invalid contracts = broken resume, broken phase transitions |
| Phase-to-phase integration tests | SC-001 | Contract chain is the backbone of the entire system |
| Golden fixtures GF-01, GF-04 | SC-014 | Minimum viable end-to-end proof |

### P1 — Should-Have (High Confidence)

| Test | Risk/SC | Rationale |
|------|---------|-----------|
| `test_resume_protocol.py` | RISK-009, SC-001 | Resume is a key differentiator but secondary to correctness |
| `test_step_classification.py` | RISK-007, FR-017 | Low-confidence flagging is safety net, not critical path |
| `test_dag_validation.py` | FR-018, FR-020 | DAG acyclicity and trailing gate escalation |
| `test_name_normalization.py` | NFR-012, FR-046 | Naming bugs are visible but not data-loss risks |
| `test_error_codes.py` | FR-045 | Input validation is important but straightforward |
| Golden fixtures GF-02, GF-03 | SC-014 | Complex scenarios; GF-01 covers basic correctness |
| Negative fixtures NF-01 through NF-04 | Various | Validate failure paths |
| `test_sync_layout.py` | FR-006 | Sync is enforced by `make verify-sync`; test is belt-and-suspenders |

### P2 — Nice-to-Have (Confidence Boost)

| Test | Rationale |
|------|-----------|
| MCP degradation tests (M5.2) | Soft dependencies; advisory only |
| Determinism repeated-run tests | Validated implicitly by golden fixtures; explicit diff is extra assurance |
| TodoWrite task count assertion (AT-13) | Operational tracking, not correctness |
| `test_contract_chain.py` (full chain) | Covered implicitly by phase-to-phase integration tests |

---

## 5. Acceptance Criteria Per Milestone

### Phase 1 Milestones

**M1.1 — Ref File API Alignment**
- [ ] `refs/pipeline-spec.md` tier casing uses `enforcement_tier="STRICT"` (not `tier="strict"`)
- [ ] `refs/pipeline-spec.md` GateCriteria fields match live `gates.py` dataclass
- [ ] `refs/code-templates.md` import paths reference `superclaude.cli.pipeline.models` / `.gates`
- [ ] `refs/code-templates.md` gate template uses actual `GateCriteria` constructor fields
- [ ] Automated diff script: zero field name mismatches between refs and live API
- [ ] Stale-ref detector script exists and passes

**M1.2 — Command/Protocol Split**
- [ ] `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` exists with migrated content
- [ ] `src/superclaude/skills/sc-cli-portify-protocol/refs/` contains updated ref files
- [ ] `src/superclaude/commands/cli-portify.md` parses: `--workflow`, `--name`, `--output`, `--dry-run`, `--skip-integration`
- [ ] Command shim validates with 6 error codes
- [ ] `make verify-sync` covers `sc-cli-portify-protocol/`
- [ ] YAML frontmatter in `SKILL.md` has: name, description, category, complexity, allowed-tools, mcp-servers, personas, argument-hint

**M1.3 — Open Question Resolution**
- [ ] `decisions.yaml` contains entries for OQ-001 through OQ-010
- [ ] All 6 blocking OQs (002, 003, 004, 007, 008, 010) have implementation decisions
- [ ] OQ-002 (TurnLedger): codebase inspected, decision recorded
- [ ] OQ-003 (dry-run/skip-integration): behavioral specification written
- [ ] OQ-004 (integration schema): YAML schema defined with fields
- [ ] OQ-007 (approval gate): mechanism specified (TodoWrite checkpoint)
- [ ] OQ-008 (default output): path convention defined
- [ ] OQ-010 (step boundary algorithm): extracted and documented in `refs/analysis-protocol.md`

### Phase 2 Milestones

**M2.1 — Contract Infrastructure**
- [ ] Schema version field present in all contract schemas (`schema_version: "1.0"`)
- [ ] Backward-compatibility rules documented
- [ ] 6 per-phase contract schemas defined (prerequisites, analysis, spec, codegen, integration, return)
- [ ] Contract validation logic rejects incompatible versions with actionable error
- [ ] Resume protocol handles synthetic failure: reads contract → skips completed phases → resumes correctly
- [ ] Null-field policy: unreached fields set to `null`
- [ ] Return contract contains: status, failure_phase, failure_type, generated_files, counts, api_snapshot_hash, resume_command, warnings, phase_contracts

**M2.2 — Phase 0**
- [ ] Resolves workflow path from `--workflow`; locates command .md, skill SKILL.md, all refs
- [ ] Aborts with `AMBIGUOUS_PATH` on multiple candidates
- [ ] API snapshot captures 7 signatures from models.py and gates.py
- [ ] `api-snapshot.yaml` includes content hash
- [ ] Output directory collision check detects `portify-summary.md` marker
- [ ] Unsupported-pattern scan detects all 4 unsupported patterns
- [ ] `portify-prerequisites.yaml` emitted with all required fields

**M2.3 — Phase 1**
- [ ] Component inventory with stable `component_id` (C-NNN format)
- [ ] Step decomposition with stable `source_id` (S-NNN format)
- [ ] Conservation invariant: every source operation → exactly one source_id
- [ ] Classification confidence scoring; flag < 0.7 with justification
- [ ] Dependency DAG is acyclic
- [ ] Gate tier and mode assigned per step
- [ ] Trailing gate → BLOCKING escalation when downstream consumes output as prompt context
- [ ] 7 self-validation checks: 6 blocking pass, 1 advisory reported
- [ ] `portify-analysis.md` under 400 lines
- [ ] `portify-analysis.yaml` with component_inventory, source_step_registry, dependency_graph, parallel_groups, validation_results

**M2.4 — TodoWrite Integration**
- [ ] 23 subphase tasks defined across 5 phases
- [ ] Checkpoint triggers fire after phase completion
- [ ] Checkpoint triggers fire at user review gates
- [ ] Checkpoint triggers fire before write operations
- [ ] Checkpoint triggers fire on failure

### Phase 3 Milestones

**M3.1 — Step Graph Design**
- [ ] Step mapping records 1:1, 1:N, N:1, 1:0 with justification
- [ ] Coverage invariant holds: `|source_step_registry| == |mapped_steps| + |elimination_records|`
- [ ] Elimination records have source_id, reason, approved_by

**M3.2 — Model and Gate Design**
- [ ] Config extends `PipelineConfig`; Result extends `StepResult`
- [ ] Status enum and Monitor state with NDJSON signals designed
- [ ] TurnLedger resolved per OQ-002
- [ ] Gates use correct `GateCriteria` fields: `required_frontmatter_fields`, `min_lines`, `enforcement_tier`, `semantic_checks`
- [ ] Semantic checks use `Callable[[str], bool]` signature
- [ ] API conformance verified against Phase 0 snapshot hash

**M3.3 — Prompt and Executor Design**
- [ ] Prompts specify input strategy, output sections, frontmatter fields, machine-readable markers
- [ ] Prompts split to `portify-prompts.md` if > 300 lines
- [ ] Pure-programmatic steps implemented as full Python code
- [ ] Executor uses sprint-style synchronous supervisor with ThreadPoolExecutor
- [ ] Pattern coverage matrix: 100% coverage for test workflow; abort on unsupported

**M3.4 — Phase 2 Output**
- [ ] 8 self-validation checks: 7 blocking pass, 1 advisory reported
- [ ] `portify-spec.yaml` contains: step_mapping, module_plan, gate_definitions, pattern_coverage, api_conformance
- [ ] User approval gate mechanism functional

### Phase 4 Milestones

**M4.1 — Code Generation**
- [ ] 12 Python files generated in order: models → gates → prompts → config → monitor → process → executor → tui → logging_ → diagnostics → commands → `__init__.py`
- [ ] Atomic generation: partial failure halts entirely, no partial output
- [ ] Per-file: `ast.parse()` succeeds, imports valid, base classes correct, GateCriteria fields match, SemanticCheck signatures correct
- [ ] Cross-file: all 12 present, no circular imports, `__init__.py` exports match, step count matches spec
- [ ] `portify-codegen.yaml` emitted

**M4.2 — CLI Integration**
- [ ] `main.py` patched with import and `app.add_command()`
- [ ] Naming collision aborts cleanly
- [ ] Smoke test: module imports, Click command group exists, name matches
- [ ] `test_<name>_structure.py` generated in `tests/` and passes
- [ ] `portify-summary.md` written with file inventory, CLI usage, step graph, known limitations, resume template
- [ ] `portify-integration.yaml` emitted

**M4.3 — Name Normalization**
- [ ] kebab-case, snake_case, PascalCase, UPPER_SNAKE derivations correct
- [ ] `sc-` prefix and `-protocol` suffix stripped
- [ ] Collision policy: portified code offers overwrite; non-portified always aborts

### Phase 5 Milestones

**M5.1 — Golden Fixtures**
- [ ] GF-01 (simple sequential): full success, 12 files, CLI registered
- [ ] GF-02 (batched audit): success with parallel groups and trailing gates
- [ ] GF-03 (adversarial multi-agent): success after user overrides
- [ ] GF-04 (unsupported): abort in Phase 0, return contract emitted
- [ ] NF-01 (stale refs): blocks before Phase 1
- [ ] NF-02 (API drift): blocks at conformance check
- [ ] NF-03 (name collision): aborts, no files written
- [ ] NF-04 (non-portified collision): never overwrites

**M5.2 — MCP Degradation**
- [ ] Each MCP server (Auggie, Serena, Sequential, Context7) unavailability tested
- [ ] Degradation produces advisory warnings, not hard failures
- [ ] Phase contracts log MCP fallback usage

**M5.3 — Resume Protocol**
- [ ] Failures at boundaries 0→1, 1→2, 2→3, 3→4 all produce resumable state
- [ ] Resume skips completed phases
- [ ] Resume re-validates completed contracts (not blindly trusted)
- [ ] `resume_command` in return contract is correct and executable

**M5.4 — Cleanup**
- [ ] Old `sc-cli-portify/` removed
- [ ] `make verify-sync` passes
- [ ] `make test` passes (no regressions)
- [ ] `make lint` clean on new/modified files

---

## 6. Quality Gates Between Phases

### Gate Structure

Every phase transition enforces a **three-layer gate**:

```
┌─────────────────────────────────────┐
│  Layer 1: Contract Validation       │  Machine-readable YAML contract
│  - Schema version compatible        │  from preceding phase exists
│  - All required fields present      │  and passes validation
│  - Status == "passed"               │
├─────────────────────────────────────┤
│  Layer 2: Test Suite Pass           │  All P0 tests for the completed
│  - Unit tests for phase pass        │  phase pass. P1 tests for the
│  - Integration tests pass           │  phase pass (advisory if not).
│  - No P0 test regressions           │
├─────────────────────────────────────┤
│  Layer 3: Validation Milestone      │  The corresponding VM checkpoint
│  - VM checklist fully satisfied     │  (from Section 1) has all items
│  - Evidence recorded                │  checked off.
│  - No blocking issues open          │
└─────────────────────────────────────┘
```

### Gate Definitions

| Gate | Between | Contract Required | Tests Required | Blocking Conditions |
|------|---------|-------------------|----------------|---------------------|
| **G1** | Phase 1 → Phase 2 | N/A (no contract from Phase 1) | VM-01, VM-02, VM-03 pass | Ref file mismatches > 0; any blocking OQ unresolved; `make verify-sync` fails |
| **G2** | Phase 2 → Phase 3 | `portify-analysis.yaml` with `status: "passed"` | VM-04, VM-05, VM-06, VM-07 pass | Conservation invariant violated; any of 6 blocking self-checks fail; unsupported pattern detected |
| **G3** | Phase 3 → Phase 4 | `portify-spec.yaml` with `status: "passed"` | VM-08, VM-09, VM-10, VM-11 pass | Coverage invariant violated; pattern coverage < 100%; any of 7 blocking self-checks fail; API conformance mismatch |
| **G4** | Phase 4 → Phase 5 | `portify-codegen.yaml` + `portify-integration.yaml` with `status: "passed"` | VM-12, VM-13, VM-14 pass | Any `ast.parse()` failure; circular imports; smoke test failure; `__init__.py` export mismatch |
| **G5** | Phase 5 → Done | Return contract with `status: "passed"` | VM-15, VM-16 pass; AT-01 through AT-14 pass | Any golden fixture failure; `make test` regression; `make lint` violation |

### Gate Failure Protocol

1. **Identify**: Which layer failed (contract / tests / VM checklist)?
2. **Diagnose**: Root cause analysis — is it a code bug, a test bug, or a spec ambiguity?
3. **Fix**: Address in current phase, not the next.
4. **Re-validate**: Re-run the full gate check, not just the failing item.
5. **Document**: Record failure and fix in phase contract `validation_status.advisory` field.

### API Conformance Re-Check

At gates G2, G3, and G4, re-hash the live API (`models.py`, `gates.py`) and compare against Phase 0 snapshot hash. If hashes differ:
- **G2**: Re-run Phase 0 snapshot, update contracts, re-validate Phase 1 output.
- **G3**: Re-run Phase 0 snapshot, cascade re-validation through Phase 1 and Phase 2.
- **G4**: Halt. API changed during code generation — re-run from Phase 2 minimum.

This prevents the highest-severity risk (RISK-001: Live API Drift) from silently corrupting downstream output.
