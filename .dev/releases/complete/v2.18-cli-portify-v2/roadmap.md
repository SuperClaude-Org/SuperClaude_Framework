

---
spec_source: "refactoring-spec-cli-portify.md"
complexity_score: 0.92
adversarial: true
---

## Executive Summary

This roadmap delivers the refactoring of `sc-cli-portify` from a monolithic skill into a command/protocol split architecture with contract-driven phase boundaries, live API conformance checking, deterministic code generation with AST verification, and comprehensive failure routing with resume semantics.

**Scope**: 70 requirements (52 functional, 18 non-functional) across 7 domains at enterprise complexity (0.92). The work produces a 5-phase portification pipeline that transforms SuperClaude skill/command/agent workflows into programmatic CLI pipelines with validated Python code generation.

**Critical path**: Ref file remediation → Command/Protocol split → Contract schema definition → Phase 0-1 implementation → Phase 2 design → Phase 3-4 code generation and integration → Golden fixture validation.

**Key architectural decisions**:
- Contract-driven phase boundaries (YAML with versioned schemas) — phases are independently resumable
- Live API snapshot with hash verification prevents drift-induced generation errors
- Atomic generation with AST validation ensures no partial or broken output
- 7 supported patterns only — explicit boundary prevents aspirational scope creep
- Determinism validated against enumerated artifacts (`source_step_registry`, `step_mapping`, `module_plan`)

**Open questions**: All 10 OQs must be resolved before Phase 2 implementation begins. OQ-002 (TurnLedger), OQ-003 (dry-run behavior), OQ-004 (integration schema), OQ-007 (approval gate mechanism), and OQ-008 (default output path) are blocking for design work.

**Estimated delivery**: 14–19 working sessions (approximately 26–35 working days, assuming 1.5–2 sessions per day with review latency).

---

## Phase 1: Foundation and Prerequisite Remediation

**Duration**: 2–3 sessions (~3–5 days)
**Goal**: Eliminate known drift, establish the split architecture, resolve blocking open questions, define contract schema versioning policy

### Milestone 1.1: Ref File API Alignment

Addresses RISK-002 (ref file staleness) — the highest-priority prerequisite. No downstream work proceeds until refs match the live API.

1. Read live `models.py` and `gates.py` to capture current API signatures
2. Update `refs/pipeline-spec.md`:
   - Fix tier casing: `tier="strict"` → `enforcement_tier="STRICT"`
   - Align `GateCriteria` field names to match live dataclass
   - Correct `SemanticCheck` contract: `Callable[[str], bool]` signature, not `tuple[bool, str]`
3. Update `refs/code-templates.md`:
   - Align all import paths to `superclaude.cli.pipeline.models` / `.gates`
   - Fix gate template to use actual `GateCriteria` constructor fields
   - Verify all 12 file templates reference correct base classes
4. **Validation**: Diff ref files against live API — zero field name mismatches. Add stale-ref detector script that compares ref field names against live API signatures.

**Requirements**: FR-048, NFR-003, NFR-018
**Risks mitigated**: RISK-002

### Milestone 1.2: Command/Protocol Split

Runs in parallel with Milestone 1.1.

1. Create `src/superclaude/skills/sc-cli-portify-protocol/` directory structure:
   - `SKILL.md` (migrated from `sc-cli-portify/SKILL.md`)
   - `__init__.py`
   - `refs/` (moved from `sc-cli-portify/refs/` — updated files from M1.1)
2. Create `src/superclaude/commands/cli-portify.md` (thin command shim):
   - Parse arguments: `--workflow`, `--name`, `--output`, `--dry-run`, `--skip-integration`
   - Input validation with 6 error codes (MISSING_WORKFLOW, INVALID_PATH, AMBIGUOUS_PATH, OUTPUT_NOT_WRITABLE, NAME_COLLISION, DERIVATION_FAILED)
   - Delegate to `Skill sc:cli-portify-protocol`
3. Promote YAML frontmatter in `SKILL.md`: name, description, category, complexity, allowed-tools, mcp-servers, personas, argument-hint
4. Ensure `make verify-sync` covers `sc-cli-portify-protocol/` directory
5. Deprecate `sc-cli-portify/` — mark for removal in Phase 5 after all validation passes

**Requirements**: FR-001 through FR-006, FR-044, FR-045, FR-046

### Milestone 1.3: Open Question Resolution

Resolve before proceeding to Phase 2:

| OQ | Resolution | Blocking? |
|----|-----------|-----------|
| OQ-001 | Confirm spec typo — §5.3 → §11.2. Document in protocol. | No |
| OQ-002 | Inspect codebase for `TurnLedger`. If absent from pipeline API, remove from spec. | **Yes** |
| OQ-003 | `--dry-run` = execute Phases 0-2 only, emit contracts, no code generation. `--skip-integration` = skip Phase 4. | **Yes** |
| OQ-004 | Define `portify-integration.yaml` schema: `main_py_patched`, `command_registered`, `test_file_generated`, `smoke_test_passed`. | **Yes** |
| OQ-005 | Set `batch_dynamic: false` always (dynamic fan-out unsupported). Remove field or make constant. | No |
| OQ-006 | Verify `refs/analysis-protocol.md` exists (confirmed). | No |
| OQ-007 | Approval gates use TodoWrite checkpoint pattern: write contract → mark task "awaiting review" → user resumes. | **Yes** |
| OQ-008 | Default `--output` to `src/superclaude/cli/<derived_name>/`. Blocking: affects contract emission paths. | **Yes** |
| OQ-009 | Structural tests go to `tests/` per project convention. | No |
| OQ-010 | Extract step boundary algorithm from current `SKILL.md` and document explicitly in `refs/analysis-protocol.md`. | **Yes** for Phase 3 |

**Exit criteria**: All 10 OQs have documented resolutions. Blocking OQs (002, 003, 004, 007, 008, 010) have implementation decisions recorded in `decisions.yaml`.

### Phase 1 Exit Criteria

- No legacy structural conflicts remain
- Protocol and command discoverable from both `src/` and `.claude/`
- Ref files verified against live API with zero mismatches
- All 10 OQs resolved and documented
- `make verify-sync` passes for new protocol directory

---

## Phase 2: Protocol Core — Contract Infrastructure, Phase 0, and Phase 1

**Duration**: 3–4 sessions (~5–8 days)
**Goal**: Implement contract infrastructure, prerequisite scanning (Phase 0), and workflow analysis (Phase 1)
**Dependencies**: Phase 1 complete, all blocking OQs resolved

### Milestone 2.1: Contract Infrastructure and Schema Versioning

Contract schemas are defined as a prerequisite sub-task, then validated through real Phase 0 execution.

1. Define contract schema versioning policy:
   - Schema version field in contract header (e.g., `schema_version: "1.0"`)
   - Backward-compatibility rules: additive fields allowed, field removal requires major version bump
   - Version validation on contract read — reject incompatible versions with actionable error
2. Define YAML contract common header schema:
   ```yaml
   schema_version: "1.0"
   phase: <int>
   status: "passed" | "failed" | "skipped"
   timestamp: <ISO8601>
   resume_checkpoint: <string>
   validation_status: {blocking_passed: <int>, blocking_failed: <int>, advisory: [...]}
   ```
3. Define per-phase contract schemas (`portify-prerequisites.yaml`, `portify-analysis.yaml`, `portify-spec.yaml`, `portify-codegen.yaml`, `portify-integration.yaml`, return contract)
4. Implement contract validation logic — next phase reads and validates incoming contract before proceeding
5. Implement return contract structure (FR-043): status, failure_phase, failure_type, generated_files, counts, api_snapshot_hash, resume_command, warnings, phase_contracts
6. Implement resume protocol (FR-052): read latest contract, validate completed phases, resume from failure point
7. Validate resume semantics with a synthetic failure scenario before Phase 0 runs — proves contract mechanics work independently
8. Define null-field policy: unreached fields explicitly set to `null`

**Requirements**: FR-007, FR-008, FR-009, FR-043, FR-052, NFR-009, NFR-015, NFR-016

### Milestone 2.2: Phase 0 — Prerequisites

1. Workflow path resolution from `--workflow` argument (FR-010):
   - Locate command `.md`, skill `SKILL.md`, all refs/rules/templates/scripts
   - Abort with `AMBIGUOUS_PATH` on multiple candidates
2. Live API snapshot (FR-011):
   - Read `models.py` and `gates.py` via Serena/Auggie
   - Extract signatures: `SemanticCheck`, `GateCriteria`, `gate_passed()`, `PipelineConfig`, `Step`, `StepResult`, `GateMode`
   - Store as `api-snapshot.yaml` with content hash
3. Output directory collision check (FR-012):
   - Check for `portify-summary.md` marker
   - Apply collision policy: overwrite portified (with confirmation), abort on non-portified, abort on `main.py` name collision
4. Early unsupported-pattern scan (FR-013):
   - Detect: recursive agent self-orchestration, interactive human decisions mid-pipeline, no stable artifact boundaries, dynamic code generation/eval
   - Emit blocking warning on detection
5. Emit `portify-prerequisites.yaml` contract (FR-014)

**Requirements**: FR-010 through FR-014, FR-047, NFR-013, NFR-014
**Risks mitigated**: RISK-001, RISK-003, RISK-008, RISK-012

### Milestone 2.3: Phase 1 — Workflow Analysis

1. Build component inventory with stable `component_id` (C-NNN) (FR-015)
2. Step decomposition with stable `source_id` (S-NNN) and conservation invariant (FR-016, FR-049)
3. Step classification: pure_programmatic / claude_assisted / hybrid with confidence scoring (FR-017)
   - Flag for user review if confidence < 0.7
4. Dependency DAG with acyclicity validation (FR-018)
5. Gate tier assignment (EXEMPT/LIGHT/STANDARD/STRICT) and mode (BLOCKING/TRAILING) (FR-019)
6. Trailing gate safety escalation (FR-020)
7. Divergence detection for ambiguous step boundaries (FR-050)
8. 7 self-validation checks (6 blocking, 1 advisory) (FR-021)
9. Emit `portify-analysis.md` (< 400 lines) and `portify-analysis.yaml` (FR-022)
10. User review gate — present analysis, allow classification overrides (FR-023)

**Requirements**: FR-015 through FR-023, FR-049, FR-050, NFR-004, NFR-005
**Risks mitigated**: RISK-004, RISK-007

### Milestone 2.4: TodoWrite Integration

1. Define 23 subphase tasks across 5 phases (FR-051)
2. Implement checkpoint triggers: after phase completion, user review gates, before write operations, on failure
3. Wire TodoWrite updates into Phase 0 and Phase 1 execution flow

**Requirements**: FR-051, SC-013

### Phase 2 Exit Criteria

- Contract schemas defined with versioning policy
- Resume semantics validated against synthetic failure
- Phase 0 correctly scans a test workflow and emits valid `portify-prerequisites.yaml`
- Phase 1 produces valid `portify-analysis.yaml` with conservation invariant holding
- Resume from Phase 0 failure correctly re-enters Phase 0
- Unsupported pattern in test workflow aborts before Phase 1

---

## Phase 3: Protocol Core — Phase 2 Implementation (Design)

**Duration**: 3–4 sessions (~5–8 days)
**Goal**: Implement the specification/design phase of the protocol
**Dependencies**: Phase 2 complete (Milestones 2.1–2.4 passing)

### Milestone 3.1: Step Graph Design

1. Source-to-generated step mapping with 1:1, 1:N, N:1, 1:0 recording and justification (FR-024)
2. Coverage invariant enforcement: `|source_step_registry| == |mapped_steps| + |elimination_records|` (FR-025, FR-049)
3. Elimination records with source_id, reason, approved_by fields

**Requirements**: FR-024, FR-025, SC-007

### Milestone 3.2: Model and Gate Design

1. Domain-specific dataclass models extending `PipelineConfig` and `StepResult` (FR-026)
   - Config, Result, Status enum, Monitor state with NDJSON signals
   - Resolve TurnLedger integration per OQ-002 decision
2. Gate design using live `GateCriteria` fields (FR-028):
   - `required_frontmatter_fields`, `min_lines`, `enforcement_tier`, `semantic_checks`
   - Semantic check functions: `Callable[[str], bool]` signature
3. API conformance verification against Phase 0 snapshot hash (RISK-001 mitigation)

**Requirements**: FR-026, FR-028, NFR-003, NFR-011, SC-005, SC-006

### Milestone 3.3: Prompt and Executor Design

1. Prompt design for Claude-assisted steps (FR-027):
   - Input strategy, output sections, frontmatter fields, machine-readable markers
   - Split to `portify-prompts.md` if > 300 lines
2. Pure-programmatic step implementation as full Python code (FR-029)
3. Executor design: sprint-style synchronous supervisor with ThreadPoolExecutor (FR-030)
4. Pattern coverage matrix — verify all required patterns covered, abort on unsupported (FR-031)

**Requirements**: FR-027, FR-029, FR-030, FR-031, NFR-006, NFR-010

### Milestone 3.4: Phase 2 Self-Validation and Output

1. 8 self-validation checks (7 blocking, 1 advisory) (FR-032)
2. Emit `portify-spec.yaml` with step_mapping, module_plan, gate_definitions, pattern_coverage, api_conformance (FR-033)
3. User approval gate before Phase 3 code generation

**Requirements**: FR-032, FR-033

### Phase 3 Exit Criteria

- `portify-spec.yaml` produced from test workflow with valid step mapping
- Coverage invariant holds
- All gate designs reference correct `GateCriteria` field names from API snapshot
- Pattern coverage matrix shows 100% coverage for test workflow patterns

---

## Phase 4: Code Generation and Integration (Phases 3–4)

**Duration**: 4–5 sessions (~7–10 days)
**Goal**: Implement deterministic Python code generation and CLI integration
**Dependencies**: Phase 3 complete

### Milestone 4.1: Phase 3 — Code Generation Engine

1. Generate 12 Python files in strict dependency order (FR-034):
   `models → gates → prompts → config → monitor → process → executor → tui → logging_ → diagnostics → commands → __init__.py`
2. Atomic generation — halt entirely on any file failure (FR-035)
3. Per-file validation (6 checks, 5 blocking, 1 advisory) (FR-036):
   - `ast.parse()` syntax validation
   - Import path verification
   - Base class contract checking (`PipelineConfig`, `StepResult`)
   - `GateCriteria` field name matching against API snapshot
   - `SemanticCheck` signature verification (`Callable[[str], bool]`)
4. Cross-file validation (4 checks, all blocking) (FR-037):
   - Module completeness (all 12 files present)
   - Circular import detection (import graph acyclicity)
   - `__init__.py` export matching
   - Step count matching against spec
5. Emit `portify-codegen.yaml` (FR-038)

**Requirements**: FR-034 through FR-038, NFR-001, NFR-002, NFR-007, NFR-011, NFR-012
**Risks mitigated**: RISK-005, RISK-001
**Success criteria validated**: SC-003, SC-004, SC-005, SC-006, SC-008

### Milestone 4.2: Phase 4 — CLI Integration

1. Patch `main.py` with import and `app.add_command()` (FR-039)
   - Abort on naming collision
2. Integration smoke test (FR-040):
   - Module imports successfully
   - Click command group exists
   - Command name matches registration
3. Generate structural test file `test_<name>_structure.py` in `tests/` (FR-041):
   - Step graph completeness
   - Gate definitions
   - Model consistency
   - Command registration
4. Write `portify-summary.md` (FR-042):
   - File inventory, CLI usage, step graph, known limitations, resume command template
5. Emit `portify-integration.yaml` contract

**Requirements**: FR-039 through FR-042, SC-009
**Risks mitigated**: RISK-008

### Milestone 4.3: Name Normalization and Collision Policy

1. Implement naming convention derivation (FR-046):
   - kebab-case (CLI), snake_case (Python), PascalCase (classes), UPPER_SNAKE (config)
   - Strip `sc-` prefix and `-protocol` suffix
2. Collision policy enforcement (FR-047):
   - Check `portify-summary.md` marker for prior portification
   - Never overwrite non-portified code (NFR-013)

**Requirements**: FR-046, FR-047, NFR-012, NFR-013, SC-012

### Phase 4 Exit Criteria

- Generated module for test workflow passes all AST checks
- No circular imports
- `main.py` patching succeeds and smoke test passes
- Structural test file generated and passes
- Return contract emitted with all fields populated

---

## Phase 5: Validation, Testing, and Cleanup

**Duration**: 2–3 sessions (~4–6 days)
**Goal**: End-to-end validation with golden fixtures, negative-path testing, cleanup, and sync verification
**Dependencies**: Phase 4 complete

### Milestone 5.1: Golden Fixture Tests and Negative-Path Validation

Golden fixtures (SC-014):

1. **Simple sequential skill**: Basic skill portification, all phases pass
2. **Batched audit skill**: Parallel step groups, trailing gates, complex DAG
3. **Adversarial multi-agent skill**: Multi-domain, high step count, N:1 mappings
4. **Intentionally unsupported skill**: Contains dynamic code gen pattern — correctly aborts in Phase 0

Each fixture validates:
- Determinism (SC-002): repeated runs produce identical `source_step_registry`, `step_mapping`, and `module_plan`
- All blocking checks pass or halt with correct failure state (SC-001)
- Return contract always emitted (SC-010)
- Step conservation invariant holds (SC-007)

Negative-path fixtures (comprehensive failure-scenario coverage):

5. **Stale-ref fixture**: Ref files with deliberately wrong field names — blocks before Phase 1
6. **API-drift fixture**: Modified API signatures between snapshot and generation — blocks at conformance check
7. **Name collision fixture**: Pre-existing non-portified code at output path — aborts with correct error
8. **Non-portified collision fixture**: Pre-existing human-written code at output path — never overwrites

### Milestone 5.2: MCP Degradation Testing

Runs in parallel with Milestone 5.1.

1. Simulate MCP server unavailability for each server (Auggie, Serena, Sequential, Context7)
2. Verify graceful degradation to native tools (NFR-008)
3. Verify advisory warnings logged in phase contracts
4. Verify no phase hard-blocks on MCP unavailability

**Risks mitigated**: RISK-006

### Milestone 5.3: Resume Protocol Validation

Runs in parallel with Milestone 5.1.

1. Simulate failures at each phase boundary (0→1, 1→2, 2→3, 3→4)
2. Verify resume correctly skips completed phases
3. Verify resume re-validates completed phase contracts (not blindly trusted)
4. Verify `resume_command` template in return contract is correct and executable

**Requirements**: FR-052, SC-001
**Risks mitigated**: RISK-009

### Milestone 5.4: Cleanup and Sync

1. Remove old `sc-cli-portify/` directory — deprecated in Phase 1, removed now after all validation passes
2. Run `make verify-sync` — confirm `src/` and `.claude/` match for protocol directory (FR-006)
3. Final `make test` — all existing tests still pass
4. Final `make lint` — no ruff violations in new/modified files

### Phase 5 Exit Criteria

- All 4 golden fixture tests pass
- All 4 negative-path fixtures produce correct failure behavior
- MCP degradation produces advisory warnings, not failures
- Resume from each phase boundary works correctly
- `make verify-sync` passes
- `make test` passes
- Old `sc-cli-portify/` removed

---

## Risk Assessment

### High Severity

| Risk | Phase Mitigated | Strategy |
|------|----------------|----------|
| RISK-001: Live API drift | Phase 1 (M1.1), Phase 4 (M4.1), Phase 5 (M5.1) | Snapshot with hash verification at every phase boundary; API-drift negative fixture validates detection |
| RISK-002: Ref file staleness | **Phase 1 (M1.1)** — hard prerequisite | Update refs before any other work; stale-ref detector blocks generation; stale-ref negative fixture validates detection |
| RISK-003: Unsupported pattern | Phase 2 (M2.2), Phase 5 (M5.1) | Early scan in Phase 0 before analysis investment; unsupported-skill golden fixture validates abort |

### Medium Severity

| Risk | Phase Mitigated | Strategy |
|------|----------------|----------|
| RISK-004: Step conservation violation | Phase 2 (M2.3), Phase 3 (M3.1) | Divergence detection and conservation equation enforcement at both phases |
| RISK-005: Circular imports | Phase 4 (M4.1) | Strict generation order and import graph acyclicity check |
| RISK-006: MCP unavailability | Phase 5 (M5.2) | Graceful degradation with advisory warnings; no hard MCP dependency outside local validation |
| RISK-007: Low confidence classification | Phase 2 (M2.3) | User review with evidence and override capability at confidence < 0.7 |
| RISK-008: Name collision | Phase 2 (M2.2), Phase 4 (M4.2), Phase 5 (M5.1) | Collision check at Phase 0 entry and Phase 4 integration; collision negative fixture validates abort |
| RISK-009: Resume state corruption | Phase 5 (M5.3) | Re-validate contracts on resume; compare filesystem state and snapshot hash |

### Low Severity

| Risk | Phase Mitigated | Strategy |
|------|----------------|----------|
| RISK-010: Human review bottleneck | By design | `--dry-run` for preview (Phases 0-2 only); approval gates are intentional safety |
| RISK-011: Template coverage gap | Phase 3 (M3.3) | Explicit coverage matrix with abort on gap |
| RISK-012: Non-portified collision | Phase 4 (M4.3), Phase 5 (M5.1) | `portify-summary.md` marker detection; non-portified collision negative fixture validates behavior |

**Highest-risk item requiring immediate attention**: RISK-002 (ref file staleness). The current `refs/pipeline-spec.md` and `refs/code-templates.md` have confirmed API drift from the live pipeline. This must be resolved first in Phase 1, Milestone 1.1.

---

## Resource Requirements and Dependencies

### Internal Dependencies

| Dependency | Status | Required By |
|-----------|--------|-------------|
| `superclaude.cli.pipeline.models` | Exists | Phase 2 (API snapshot) |
| `superclaude.cli.pipeline.gates` | Exists | Phase 2 (API snapshot) |
| `superclaude.cli.main` (Click app) | Exists | Phase 4 (integration) |
| `tasklist.md` command/protocol pattern | Exists | Phase 1 (reference architecture) |
| `refs/analysis-protocol.md` | Exists | Phase 2 (Phase 1 analysis) |

### External Dependencies

| Dependency | Required? | Fallback |
|-----------|-----------|----------|
| Python `ast` module | Hard | Standard library, always available |
| `concurrent.futures.ThreadPoolExecutor` | Hard | Standard library, always available |
| MCP: Auggie (codebase-retrieval) | Soft | Native file read tools |
| MCP: Serena | Soft | Native grep/glob tools |
| MCP: Sequential | Soft | Native Claude reasoning |
| MCP: Context7 | Soft | WebSearch fallback |

### Tooling

- `uv` for all Python operations
- `make verify-sync` for sync validation
- `make test` / `uv run pytest` for test execution
- `make lint` for code quality

### Non-Code Prerequisites

1. Resolve all blocking open questions (OQ-002, 003, 004, 007, 008) before Phase 2
2. Define contract schema versioning policy (Milestone 2.1)
3. Define ownership of ref file maintenance
4. Extract step boundary algorithm into `refs/analysis-protocol.md` (OQ-010) before Phase 3

---

## Success Criteria and Validation Approach

### Validation Matrix

| Criterion | Validated In | Method |
|-----------|-------------|--------|
| SC-001: All phases pass or halt resumably | Phase 5 (M5.1, M5.3) | Golden fixtures and resume testing |
| SC-002: Deterministic output | Phase 5 (M5.1) | Repeat fixture runs, diff `source_step_registry`, `step_mapping`, `module_plan` |
| SC-003: All files pass `ast.parse()` | Phase 4 (M4.1) | Per-file validation check |
| SC-004: Acyclic import graph | Phase 4 (M4.1) | Cross-file validation check |
| SC-005: GateCriteria field match | Phase 4 (M4.1) | Per-file validation against snapshot |
| SC-006: SemanticCheck signature correct | Phase 4 (M4.1) | Per-file signature verification |
| SC-007: Step conservation invariant | Phase 2 (M2.3), Phase 3 (M3.1) | Equation check at both phases |
| SC-008: Module imports cleanly | Phase 4 (M4.2) | Smoke test |
| SC-009: Click command accessible | Phase 4 (M4.2) | Smoke test |
| SC-010: Return contract always emitted | Phase 5 (M5.1) | All fixture runs including failures |
| SC-011: Unsupported pattern aborts early | Phase 5 (M5.1) | Golden fixture #4 (unsupported skill) |
| SC-012: Non-portified code safe | Phase 4 (M4.3), Phase 5 (M5.1) | Collision policy test and negative fixture |
| SC-013: 23 TodoWrite tasks tracked | Phase 2 (M2.4) | Task count verification |
| SC-014: Golden fixtures pass | Phase 5 (M5.1) | All 4 golden fixtures and 4 negative-path fixtures |

### Acceptance Gate

Do not declare completion until all pass:

1. **Golden fixtures**: all 4 positive scenarios produce correct output
2. **Negative fixtures**: all 4 failure scenarios produce correct abort/error behavior
3. **Determinism**: repeated runs produce identical enumerated artifacts
4. **Safety**: collision and unsupported-path enforcement validated
5. **Integration**: command visible and functional in CLI
6. **Contracts**: emitted on both success and failure paths
7. **Resume**: works correctly from every phase boundary
8. **Sync**: `make verify-sync` includes new protocol structure
9. **Tests**: `make test` passes with no regressions

---

## Timeline Summary

| Phase | Milestones | Sessions | Days (approx.) | Cumulative Sessions | Cumulative Days |
|-------|-----------|----------|----------------|--------------------:|----------------:|
| **Phase 1**: Foundation | M1.1–M1.3 | 2–3 | 3–5 | 2–3 | 3–5 |
| **Phase 2**: Phase 0 and 1 | M2.1–M2.4 | 3–4 | 5–8 | 5–7 | 8–13 |
| **Phase 3**: Phase 2 (Design) | M3.1–M3.4 | 3–4 | 5–8 | 8–11 | 13–21 |
| **Phase 4**: Phases 3–4 (CodeGen) | M4.1–M4.3 | 4–5 | 7–10 | 12–16 | 20–31 |
| **Phase 5**: Validation and Cleanup | M5.1–M5.4 | 2–3 | 4–6 | 14–19 | 24–37 |

**Total**: 14–19 sessions / 24–37 days

**Critical path**: M1.1 → M2.2 → M2.3 → M3.1–M3.4 → M4.1 → M5.1

**Parallelization opportunities**:
- M1.1 (ref alignment) and M1.2 (command/protocol split) run in parallel
- M2.1 (contract infrastructure) and M1.3 (OQ resolution) overlap
- M5.1 (golden fixtures), M5.2 (MCP degradation), and M5.3 (resume validation) run in parallel
- Golden fixture preparation can begin during Phase 3 (fixture definitions, not execution)
