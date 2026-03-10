---
spec_source: "refactoring-spec-cli-portify.md"
complexity_score: 0.92
primary_persona: architect
---

# CLI Portify v2 — Project Roadmap

## Executive Summary

This roadmap covers the refactoring of the `sc-cli-portify` skill from a monolithic skill into a command/protocol split architecture, with contract-driven phase boundaries, live API conformance checking, deterministic code generation with AST verification, and comprehensive failure routing with resume semantics.

**Scope**: 70 requirements (52 functional, 18 non-functional) across 7 domains, enterprise complexity (0.92). The work produces a 5-phase portification pipeline that transforms SuperClaude skill/command/agent workflows into programmatic CLI pipelines with validated Python code generation.

**Critical path**: Ref file remediation → Command/Protocol split → Phase 0-1 implementation → Phase 2 implementation → Phase 3-4 implementation → Golden fixture tests.

**Key architectural decisions**:
- Contract-driven phase boundaries (YAML, not prose) — phases are independently resumable
- Live API snapshot with hash verification prevents drift-induced generation errors
- Atomic generation with AST validation ensures no partial/broken output
- 7 supported patterns only — explicit boundary prevents aspirational scope creep

**Open questions (10) must be resolved before Phase 2 implementation begins.** OQ-002 (TurnLedger), OQ-003 (dry-run behavior), and OQ-007 (approval gate mechanism) are blocking for design work.

---

## Phase 1: Foundation & Prerequisite Remediation

**Duration estimate**: 2–3 working sessions
**Goal**: Eliminate known drift, establish the split architecture, resolve blocking open questions

### Milestone 1.1: Ref File API Alignment (RISK-002 mitigation)

1. Read live `models.py` and `gates.py` to capture current API signatures
2. Update `refs/pipeline-spec.md`:
   - Fix tier casing: `tier="strict"` → `enforcement_tier="STRICT"`
   - Align `GateCriteria` field names to match live dataclass
   - Correct `SemanticCheck` contract: `Callable[[str], bool]` signature, not `tuple[bool, str]`
3. Update `refs/code-templates.md`:
   - Align all import paths to `superclaude.cli.pipeline.models` / `.gates`
   - Fix gate template to use actual `GateCriteria` constructor fields
   - Verify all 12 file templates reference correct base classes
4. **Validation**: Diff ref files against live API — zero field name mismatches

**Requirements covered**: FR-048, NFR-003, NFR-018
**Risks mitigated**: RISK-002 (ref file staleness)

### Milestone 1.2: Command/Protocol Split

1. Create `src/superclaude/skills/sc-cli-portify-protocol/` directory structure:
   - `SKILL.md` (migrated from `sc-cli-portify/SKILL.md`)
   - `__init__.py`
   - `refs/` (moved from `sc-cli-portify/refs/` — now contains updated files from M1.1)
2. Create `src/superclaude/commands/cli-portify.md` (thin command shim):
   - Parse arguments: `--workflow`, `--name`, `--output`, `--dry-run`, `--skip-integration`
   - Input validation with 6 error codes (MISSING_WORKFLOW, INVALID_PATH, AMBIGUOUS_PATH, OUTPUT_NOT_WRITABLE, NAME_COLLISION, DERIVATION_FAILED)
   - Delegate to `Skill sc:cli-portify-protocol`
3. Promote YAML frontmatter in `SKILL.md`: name, description, category, complexity, allowed-tools, mcp-servers, personas, argument-hint
4. Ensure `make verify-sync` covers `sc-cli-portify-protocol/` directory
5. **Do not** delete `sc-cli-portify/` yet — defer to Phase 5

**Requirements covered**: FR-001 through FR-006, FR-044, FR-045, FR-046
**Pattern reference**: `tasklist.md` / `sc-tasklist-protocol/` split

### Milestone 1.3: Open Question Resolution

Resolve before proceeding to Phase 2:

| OQ | Resolution approach | Blocking? |
|----|-------------------|-----------|
| OQ-001 | Confirm spec typo — §5.3 → §11.2. Document in protocol. | No |
| OQ-002 | Inspect codebase for `TurnLedger`. If absent from pipeline API, remove from spec. | **Yes** for Phase 2 |
| OQ-003 | Define: `--dry-run` = execute Phases 0-2 only, emit contracts, no code generation. `--skip-integration` = skip Phase 4. | **Yes** for Phase 2 |
| OQ-004 | Define `portify-integration.yaml` schema: `main_py_patched`, `command_registered`, `test_file_generated`, `smoke_test_passed`. | **Yes** for Phase 2 |
| OQ-005 | Set `batch_dynamic: false` always (dynamic fan-out unsupported). Remove field or make constant. | No |
| OQ-006 | Verify `refs/analysis-protocol.md` exists (confirmed — it does). | No |
| OQ-007 | Approval gates use TodoWrite checkpoint pattern: write contract → mark task "awaiting review" → user resumes. | **Yes** for Phase 2 |
| OQ-008 | Default `--output` to `src/superclaude/cli/<derived_name>/`. | No |
| OQ-009 | Structural tests go to `tests/` per project convention. | No |
| OQ-010 | Extract step boundary algorithm from current `SKILL.md` and document explicitly in `refs/analysis-protocol.md`. | **Yes** for Phase 3 |

**Exit criteria**: All 10 OQs have documented resolutions. Blocking OQs (002, 003, 004, 007, 010) have implementation decisions recorded in a `decisions.yaml` file.

---

## Phase 2: Protocol Core — Phase 0 & Phase 1 Implementation

**Duration estimate**: 3–4 working sessions
**Goal**: Implement the prerequisite scanning (Phase 0) and workflow analysis (Phase 1) portions of the protocol
**Dependencies**: Phase 1 complete, all blocking OQs resolved

### Milestone 2.1: Contract Infrastructure

1. Define YAML contract common header schema:
   ```yaml
   phase: <int>
   status: "passed" | "failed" | "skipped"
   timestamp: <ISO8601>
   resume_checkpoint: <string>
   validation_status: {blocking_passed: <int>, blocking_failed: <int>, advisory: [...]}
   ```
2. Implement contract validation logic — next phase reads and validates incoming contract before proceeding
3. Implement return contract structure (FR-043): status, failure_phase, failure_type, generated_files, counts, api_snapshot_hash, resume_command, warnings, phase_contracts
4. Implement resume protocol (FR-052): read latest contract, validate completed phases, resume from failure point

**Requirements covered**: FR-007, FR-008, FR-009, FR-043, FR-052, NFR-009, NFR-015, NFR-016

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

**Requirements covered**: FR-010 through FR-014, FR-047, NFR-013, NFR-014
**Risks mitigated**: RISK-001 (API drift — snapshot captures baseline), RISK-003 (unsupported patterns caught early), RISK-008 (name collision), RISK-012 (non-portified collision)

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

**Requirements covered**: FR-015 through FR-023, FR-049, FR-050, NFR-004, NFR-005
**Risks mitigated**: RISK-004 (step conservation), RISK-007 (low confidence classification)

### Milestone 2.4: TodoWrite Integration

1. Define 23 subphase tasks across 5 phases (FR-051)
2. Implement checkpoint triggers: after phase completion, user review gates, before write operations, on failure
3. Wire TodoWrite updates into Phase 0 and Phase 1 execution flow

**Requirements covered**: FR-051, SC-013

**Phase 2 exit criteria**:
- Phase 0 correctly scans a test workflow and emits valid `portify-prerequisites.yaml`
- Phase 1 produces valid `portify-analysis.yaml` with conservation invariant holding
- Resume from Phase 0 failure correctly re-enters Phase 0
- Unsupported pattern in test workflow aborts before Phase 1

---

## Phase 3: Protocol Core — Phase 2 Implementation (Design)

**Duration estimate**: 3–4 working sessions
**Goal**: Implement the specification/design phase of the protocol
**Dependencies**: Phase 2 complete (Milestones 2.1–2.4 passing)

### Milestone 3.1: Step Graph Design

1. Source-to-generated step mapping with 1:1, 1:N, N:1, 1:0 recording and justification (FR-024)
2. Coverage invariant enforcement: `|source_step_registry| == |mapped_steps| + |elimination_records|` (FR-025, FR-049)
3. Elimination records with source_id, reason, approved_by fields

**Requirements covered**: FR-024, FR-025, SC-007

### Milestone 3.2: Model & Gate Design

1. Domain-specific dataclass models extending `PipelineConfig` and `StepResult` (FR-026)
   - Config, Result, Status enum, Monitor state with NDJSON signals
   - Resolve TurnLedger integration per OQ-002 decision
2. Gate design using live `GateCriteria` fields (FR-028):
   - `required_frontmatter_fields`, `min_lines`, `enforcement_tier`, `semantic_checks`
   - Semantic check functions: `Callable[[str], bool]` signature
3. API conformance verification against Phase 0 snapshot hash (RISK-001 mitigation)

**Requirements covered**: FR-026, FR-028, NFR-003, NFR-011, SC-005, SC-006

### Milestone 3.3: Prompt & Executor Design

1. Prompt design for Claude-assisted steps (FR-027):
   - Input strategy, output sections, frontmatter fields, machine-readable markers
   - Split to `portify-prompts.md` if > 300 lines
2. Pure-programmatic step implementation as full Python code (FR-029)
3. Executor design: sprint-style synchronous supervisor with ThreadPoolExecutor (FR-030)
4. Pattern coverage matrix — verify all required patterns covered, abort on unsupported (FR-031)

**Requirements covered**: FR-027, FR-029, FR-030, FR-031, NFR-006, NFR-010

### Milestone 3.4: Phase 2 Self-Validation & Output

1. 8 self-validation checks (7 blocking, 1 advisory) (FR-032)
2. Emit `portify-spec.yaml` with step_mapping, module_plan, gate_definitions, pattern_coverage, api_conformance (FR-033)
3. User approval gate before Phase 3 code generation

**Requirements covered**: FR-032, FR-033

**Phase 3 exit criteria**:
- `portify-spec.yaml` produced from test workflow with valid step mapping
- Coverage invariant holds
- All gate designs reference correct `GateCriteria` field names from API snapshot
- Pattern coverage matrix shows 100% coverage for test workflow patterns

---

## Phase 4: Code Generation & Integration (Phases 3–4)

**Duration estimate**: 4–5 working sessions
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

**Requirements covered**: FR-034 through FR-038, NFR-001, NFR-002, NFR-007, NFR-011, NFR-012
**Risks mitigated**: RISK-005 (circular imports), RISK-001 (API drift — hash re-check)
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

**Requirements covered**: FR-039 through FR-042, SC-009
**Risks mitigated**: RISK-008 (name collision)

### Milestone 4.3: Name Normalization & Collision Policy

1. Implement naming convention derivation (FR-046):
   - kebab-case (CLI), snake_case (Python), PascalCase (classes), UPPER_SNAKE (config)
   - Strip `sc-` prefix and `-protocol` suffix
2. Collision policy enforcement (FR-047):
   - Check `portify-summary.md` marker for prior portification
   - Never overwrite non-portified code (NFR-013)

**Requirements covered**: FR-046, FR-047, NFR-012, NFR-013, SC-012

**Phase 4 exit criteria**:
- Generated module for test workflow passes all AST checks
- No circular imports
- `main.py` patching succeeds and smoke test passes
- Structural test file generated and passes
- Return contract emitted with all fields populated

---

## Phase 5: Validation, Testing & Cleanup

**Duration estimate**: 2–3 working sessions
**Goal**: End-to-end validation with golden fixtures, cleanup, sync verification
**Dependencies**: Phase 4 complete

### Milestone 5.1: Golden Fixture Tests (SC-014)

1. **Simple sequential skill**: Basic skill portification, all phases pass
2. **Batched audit skill**: Parallel step groups, trailing gates, complex DAG
3. **Adversarial multi-agent skill**: Multi-domain, high step count, N:1 mappings
4. **Intentionally unsupported skill**: Contains dynamic code gen pattern → correctly aborts in Phase 0

Each fixture validates:
- Determinism (SC-002): repeated runs produce identical output
- All blocking checks pass or halt with correct failure state (SC-001)
- Return contract always emitted (SC-010)
- Step conservation invariant holds (SC-007)

### Milestone 5.2: MCP Degradation Testing

1. Simulate MCP server unavailability for each server (Auggie, Serena, Sequential, Context7)
2. Verify graceful degradation to native tools (NFR-008)
3. Verify advisory warnings logged in phase contracts
4. Verify no phase hard-blocks on MCP unavailability

**Risks mitigated**: RISK-006 (MCP unavailability)

### Milestone 5.3: Resume Protocol Validation

1. Simulate failures at each phase boundary (0→1, 1→2, 2→3, 3→4)
2. Verify resume correctly skips completed phases
3. Verify resume re-validates completed phase contracts
4. Verify `resume_command` template in return contract is correct and executable

**Requirements covered**: FR-052, SC-001
**Risks mitigated**: RISK-009 (resume state corruption)

### Milestone 5.4: Cleanup & Sync

1. Deprecate and remove old `sc-cli-portify/` directory (FR-004)
2. Run `make verify-sync` — confirm `src/` and `.claude/` match for protocol directory (FR-006)
3. Final `make test` — all existing tests still pass
4. Final `make lint` — no ruff violations in new/modified files

**Phase 5 exit criteria**:
- All 4 golden fixture tests pass
- MCP degradation produces advisory warnings, not failures
- Resume from each phase boundary works correctly
- `make verify-sync` passes
- `make test` passes
- Old `sc-cli-portify/` removed

---

## Risk Assessment & Mitigation Summary

| Risk | Severity | Phase Mitigated | Strategy |
|------|----------|----------------|----------|
| RISK-001: Live API Drift | High | Phase 1 (M1.1), Phase 4 (M4.1) | Snapshot + hash verification at every phase boundary |
| RISK-002: Ref File Staleness | High | **Phase 1 (M1.1)** — prerequisite | Update refs before any other work; drift detection blocks generation |
| RISK-003: Unsupported Pattern | High | Phase 2 (M2.2) | Early scan in Phase 0 before analysis investment |
| RISK-004: Step Conservation | Medium | Phase 2 (M2.3), Phase 3 (M3.1) | Divergence detection + conservation equation enforcement |
| RISK-005: Circular Imports | Medium | Phase 4 (M4.1) | Strict generation order + import graph acyclicity check |
| RISK-006: MCP Unavailability | Medium | Phase 5 (M5.2) | Graceful degradation with advisory warnings |
| RISK-007: Low Confidence Classification | Medium | Phase 2 (M2.3) | User review with evidence and override capability |
| RISK-008: Name Collision | Medium | Phase 2 (M2.2), Phase 4 (M4.2) | Collision check at Phase 0 entry and Phase 4 integration |
| RISK-009: Resume Corruption | Medium | Phase 5 (M5.3) | Re-validate contracts on resume |
| RISK-010: Human Review Bottleneck | Low | By design | `--dry-run` for preview; approval gates are intentional safety |
| RISK-011: Template Coverage Gap | Low | Phase 3 (M3.3) | Explicit coverage matrix with abort on gap |
| RISK-012: Non-Portified Collision | Low | Phase 4 (M4.3) | `portify-summary.md` marker detection |

**Highest-risk item requiring immediate attention**: RISK-002 (ref file staleness). The current `refs/pipeline-spec.md` and `refs/code-templates.md` have confirmed API drift from the live pipeline. This must be resolved first in Phase 1, Milestone 1.1. All downstream work depends on accurate reference files.

---

## Resource Requirements & Dependencies

### Internal Dependencies (Must Exist)

| Dependency | Status | Required By |
|-----------|--------|-------------|
| `superclaude.cli.pipeline.models` | ✅ Exists | Phase 2 (API snapshot) |
| `superclaude.cli.pipeline.gates` | ✅ Exists | Phase 2 (API snapshot) |
| `superclaude.cli.main` (Click app) | ✅ Exists | Phase 4 (integration) |
| `tasklist.md` command/protocol pattern | ✅ Exists | Phase 1 (reference architecture) |
| `refs/analysis-protocol.md` | ✅ Exists | Phase 2 (Phase 1 analysis) |

### External Dependencies (Runtime)

| Dependency | Required? | Fallback |
|-----------|-----------|----------|
| Python `ast` module | Hard — no fallback | Standard library, always available |
| `concurrent.futures.ThreadPoolExecutor` | Hard — no fallback | Standard library, always available |
| MCP: Auggie (codebase-retrieval) | Soft | Native file read tools |
| MCP: Serena | Soft | Native grep/glob tools |
| MCP: Sequential | Soft | Native Claude reasoning |
| MCP: Context7 | Soft | WebSearch fallback |

### Tooling Requirements

- `uv` for all Python operations
- `make verify-sync` for sync validation
- `make test` / `uv run pytest` for test execution
- `make lint` for code quality

---

## Success Criteria Validation Matrix

| Criterion | Validated In | Method |
|-----------|-------------|--------|
| SC-001: All phases pass or halt resumably | Phase 5 (M5.1, M5.3) | Golden fixtures + resume testing |
| SC-002: Deterministic output | Phase 5 (M5.1) | Repeat fixture runs, diff output |
| SC-003: All files pass `ast.parse()` | Phase 4 (M4.1) | Per-file validation check |
| SC-004: Acyclic import graph | Phase 4 (M4.1) | Cross-file validation check |
| SC-005: GateCriteria field match | Phase 4 (M4.1) | Per-file validation against snapshot |
| SC-006: SemanticCheck signature correct | Phase 4 (M4.1) | Per-file signature verification |
| SC-007: Step conservation invariant | Phase 2 (M2.3), Phase 3 (M3.1) | Equation check at both phases |
| SC-008: Module imports cleanly | Phase 4 (M4.2) | Smoke test |
| SC-009: Click command accessible | Phase 4 (M4.2) | Smoke test |
| SC-010: Return contract always emitted | Phase 5 (M5.1) | All fixture runs including failures |
| SC-011: Unsupported pattern aborts early | Phase 5 (M5.1) | Fixture #4 (unsupported skill) |
| SC-012: Non-portified code safe | Phase 4 (M4.3) | Collision policy test |
| SC-013: 23 TodoWrite tasks tracked | Phase 2 (M2.4) | Task count verification |
| SC-014: Golden fixtures pass | Phase 5 (M5.1) | All 4 fixtures |

---

## Timeline Summary

| Phase | Milestones | Sessions | Cumulative |
|-------|-----------|----------|------------|
| **Phase 1**: Foundation | M1.1–M1.3 | 2–3 | 2–3 |
| **Phase 2**: Phase 0 & 1 | M2.1–M2.4 | 3–4 | 5–7 |
| **Phase 3**: Phase 2 (Design) | M3.1–M3.4 | 3–4 | 8–11 |
| **Phase 4**: Phases 3–4 (CodeGen) | M4.1–M4.3 | 4–5 | 12–16 |
| **Phase 5**: Validation & Cleanup | M5.1–M5.4 | 2–3 | 14–19 |

**Total**: 14–19 working sessions

**Critical path**: M1.1 (ref alignment) → M2.2 (Phase 0) → M2.3 (Phase 1) → M3.1–M3.4 (Phase 2) → M4.1 (code generation) → M5.1 (golden fixtures)

**Parallelization opportunities**:
- M1.2 (command/protocol split) and M1.1 (ref alignment) can proceed in parallel
- M2.1 (contract infrastructure) and M1.3 (OQ resolution) can overlap
- M5.1 (golden fixtures) and M5.2 (MCP degradation) can run in parallel
- M5.3 (resume validation) can run in parallel with M5.4 (cleanup)
