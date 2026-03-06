# Refactoring Specification: sc:cli-portify v2.0

**Status**: DRAFT — Design outline for review
**Source**: Spec panel review findings (`cli-portify-specreview.md`)
**Peer references**: sc:tasklist-protocol, sc:roadmap-protocol, sc:adversarial-protocol

---

## 1. Architecture Refactor

### 1.1 Command/Protocol Split (C1)

Adopt the tasklist pattern: thin command shim delegates to full protocol skill.

**New files**:

| File | Role | Peer reference |
|------|------|----------------|
| `src/superclaude/commands/cli-portify.md` | Thin command: argument parsing, input validation, protocol invocation | `commands/tasklist.md` |
| `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` | Full generation protocol | `skills/sc-tasklist-protocol/SKILL.md` |
| `src/superclaude/skills/sc-cli-portify-protocol/refs/` | Reference files (migrated from current) | — |

**Migration path**:
- Current `sc-cli-portify/SKILL.md` becomes `sc-cli-portify-protocol/SKILL.md`
- Current `sc-cli-portify/refs/` moves into protocol directory
- New `commands/cli-portify.md` created with input validation + `Skill sc:cli-portify-protocol` invocation
- Old `sc-cli-portify/` directory deprecated and removed after migration

### 1.2 Frontmatter (M1)

Promote commented metadata into real frontmatter fields:

```yaml
---
name: sc:cli-portify-protocol
description: "Workflow-to-CLI pipeline compiler protocol — converts inference-based SuperClaude workflows into deterministic CLI pipelines with validated code generation"
category: development
complexity: high
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
mcp-servers: [sequential, serena, context7, auggie-mcp]
personas: [architect, analyzer, backend]
argument-hint: "--workflow <skill-name-or-path> [--name <cli-name>] [--output <dir>]"
---
```

### 1.3 Sync/Package Layout (N1)

Both `src/` and `.claude/` copies include `__init__.py`. `make verify-sync` covers the protocol directory.

---

## 2. Phase Architecture (5 phases: 0-4)

Retain the analysis → spec → generation → integration decomposition (Fowler: "conceptually right"). Add Phase 0 prerequisites and contract boundaries between all phases.

### 2.0 Phase Contract Model (C3)

Every phase emits **two** artifacts:

| Artifact | Format | Consumer |
|----------|--------|----------|
| Human review document | `.md` | User approval gate |
| Machine-readable contract | `.yaml` | Next phase entry validation |

The `.yaml` contract has a stable schema per phase. The next phase's entry criteria validates the incoming contract before proceeding. This eliminates the "re-interpret prose" leak identified by Fowler.

**Contract schema fields** (unified across phases):

```yaml
# Common header in every phase contract
phase: <0|1|2|3|4>
status: <completed|failed|skipped>
timestamp: <ISO-8601>
resume_checkpoint: <phase marker>
validation_status:
  blocking_checks_passed: <int>
  blocking_checks_total: <int>
  advisory_warnings: <list[str]>
```

### 2.1 Phase 0: Prerequisites

**Purpose**: Validate environment, snapshot live API contracts, detect unsupported patterns early.

**Entry criteria**: `--workflow` argument provided.

**Behavioral instructions**:

1. **Resolve workflow path** — Locate command `.md`, skill `SKILL.md`, all refs/rules/templates/scripts. If path resolves to multiple candidates, abort with disambiguation error (guard gap: "workflow resolves").
2. **Snapshot live pipeline API** — Read `src/superclaude/cli/pipeline/models.py` and `gates.py`. Extract:
   - `SemanticCheck` fields: `name: str`, `check_fn: Callable[[str], bool]`, `failure_message: str`
   - `GateCriteria` fields: `required_frontmatter_fields: list[str]`, `min_lines: int`, `enforcement_tier: Literal[...]`, `semantic_checks: list[SemanticCheck] | None`
   - `gate_passed()` signature: `(output_file: Path, criteria: GateCriteria) -> tuple[bool, str | None]`
   - All `PipelineConfig`, `Step`, `StepResult`, `GateMode` signatures
   - Store as `api-snapshot.yaml` — used by Phase 3 for contract verification (C4)
3. **Check output collision** — If target directory exists, apply naming policy (see Section 5.3).
4. **Early unsupported-pattern scan** — Read the skill's behavioral flow. If any of these patterns are detected, emit a blocking warning before investing analysis effort:
   - Recursive agent self-orchestration
   - Interactive human decisions mid-pipeline (not between phases)
   - No stable artifact boundaries
   - Dynamic code generation/eval patterns

**Exit criteria**: All prerequisites pass. Emit `api-snapshot.yaml`. TodoWrite: mark Phase 0 complete.

**Failure routing**: Any prerequisite failure → abort with error code and corrective action. No partial output.

**Contract emitted**: `portify-prerequisites.yaml`
```yaml
phase: 0
status: completed
workflow_path: <resolved path>
component_count: <int>
api_snapshot_path: <path to api-snapshot.yaml>
unsupported_patterns_detected: []
output_directory: <resolved path>
collision_policy_applied: <none|suffix|overwrite>
```

### 2.2 Phase 1: Workflow Analysis

**Purpose**: Decompose the target workflow into a machine-checkable step registry with classifications, dependencies, and gates.

**Entry criteria**: Phase 0 contract validates (status: completed, api_snapshot exists).

**Refs loaded**: `refs/analysis-protocol.md`

**Behavioral instructions**:

1. **Discover components** — Build component inventory with paths, line counts, purposes. Every component gets a stable `component_id` (C-NNN).
2. **Decompose into steps** — Apply step boundary algorithm (unchanged from current spec). Every source step gets a stable `source_id` (S-NNN). **Conservation invariant (C5)**: every source operation maps to exactly one source_id. No source_id may be created without tracing to a specific location in the workflow.
3. **Classify each step** — Pure programmatic / Claude-assisted / Hybrid. Classification includes:
   - Confidence score (0.0-1.0)
   - If confidence < 0.7: flag for user review with justification
   - Evidence: specific lines/patterns that support classification (Whittaker Zero/Empty defense)
4. **Map dependencies and parallel groups** — DAG with data flow edges. Validate acyclicity.
5. **Extract and assign gates** — Tier + mode for each step output.
6. **Check trailing gate safety** — For each TRAILING gate: verify no downstream step consumes this output as prompt context. If so, escalate to BLOCKING (Whittaker Sentinel Collision defense).

**Self-validation (pre-write)** — All must pass before writing output:

| # | Check | Blocks write? |
|---|-------|--------------|
| 1 | Every workflow behavioral instruction has ≥1 source_id | Yes |
| 2 | Every source_id has exactly one classification | Yes |
| 3 | Classification confidence ≥ 0.7 for all steps, or user-reviewed | Yes |
| 4 | Dependency graph is acyclic | Yes |
| 5 | Every step with downstream consumers has BLOCKING gate | Yes |
| 6 | No orphan source_ids (referenced but not classified) | Yes |
| 7 | Component inventory covers all files in skill directory | Advisory |

**Output artifacts**:
- `portify-analysis.md` — Human-readable. Under 400 lines.
- `portify-analysis.yaml` — Machine contract.

**Contract emitted**: `portify-analysis.yaml`
```yaml
phase: 1
status: completed
component_inventory:
  - id: "C-001"
    path: <relative path>
    type: <command|skill|ref|rule|template|script|agent>
    line_count: <int>
    purpose: <string>
source_step_registry:
  - id: "S-001"
    name: <step name>
    source_location: <file:line range>
    classification: <pure_programmatic|claude_assisted|hybrid>
    classification_confidence: <float 0.0-1.0>
    classification_evidence: <string>
    produces_artifacts: [<artifact names>]
    consumes_artifacts: [<artifact names>]
    gate_tier: <EXEMPT|LIGHT|STANDARD|STRICT>
    gate_mode: <BLOCKING|TRAILING>
    parallel_group: <group-id or null>
dependency_graph:
  edges:
    - from: "S-001"
      to: "S-002"
      artifact: <artifact name>
parallel_groups:
  - id: "PG-001"
    steps: ["S-003", "S-004", "S-005"]
    batch_dynamic: <true|false>
validation_results:
  checks_passed: <int>
  checks_total: <int>
  advisory_warnings: [<strings>]
```

**Present to user for review. User may override classifications or flag missing steps.**

**Failure routing**:
- Self-validation fails → `status: failed`, list failing checks, suggest corrections. Resumable from Phase 1.
- Unsupported pattern discovered during analysis → `status: failed`, `unsupported_patterns: [...]`, abort with explanation.

### 2.3 Phase 2: Pipeline Specification

**Purpose**: Convert the validated analysis into code-ready specifications with concrete models, gates, executor design, and pure-programmatic implementations.

**Entry criteria**: Phase 1 contract validates (status: completed, all blocking checks passed).

**Refs loaded**: `refs/pipeline-spec.md`

**Behavioral instructions**:

1. **Design Step graph** — Map each source_id to generated Step(s). Record the mapping:
   - 1:1 mapping (most common)
   - 1:N split (with justification)
   - N:1 collapse (with justification)
   - 1:0 elimination (with justification — becomes elimination_record)

   **Coverage invariant (C5)**: `source_step_registry` count == mapped steps + elimination_records. No unmapped source_ids.

2. **Design models** — Domain-specific dataclasses. Must conform to live API snapshot from Phase 0:
   - Config extending `PipelineConfig`
   - Result extending `StepResult`
   - Status enum
   - Monitor state with NDJSON signals
   - `TurnLedger` integration

3. **Design prompts** — For each Claude-assisted step. Each prompt specifies:
   - Input files/context embedding strategy (inline < 50KB, `--file` for larger)
   - Required output sections and frontmatter fields
   - Machine-readable markers
   - Structural requirements the gate will check
   - **Boundary condition**: prompts collectively > 300 lines → split to `portify-prompts.md` (use `>` not `>=` as comparator — guard gap fix)

4. **Design gates** — For each output artifact. Must use live `GateCriteria` field names from API snapshot:
   - `required_frontmatter_fields: list[str]`
   - `min_lines: int`
   - `enforcement_tier: Literal["STRICT", "STANDARD", "LIGHT", "EXEMPT"]`
   - `semantic_checks: list[SemanticCheck] | None`
   - Semantic check functions: `Callable[[str], bool]` (not `tuple[bool, str]` — that's the gate_passed return, not the check_fn signature)

5. **Implement pure-programmatic steps** — Full Python code, not descriptions.

6. **Design executor** — Sprint-style synchronous supervisor. ThreadPoolExecutor for batch parallelism. All design decisions documented against live API.

7. **Assess pattern coverage** — For each step design, verify the code templates in `refs/code-templates.md` cover the required pattern. Build coverage matrix (M5):

| Pattern | Template available | Module needed | Status |
|---------|-------------------|---------------|--------|
| Sequential step | Yes | executor.py | Covered |
| Batch parallel | Yes | executor.py | Covered |
| Dynamic fan-out | No | — | **Unsupported** |
| ... | ... | ... | ... |

   If any step requires an unsupported pattern → blocking abort before code generation.

8. **Plan integration** — Click command group, main.py import, naming.

**Self-validation (pre-write)**:

| # | Check | Blocks write? |
|---|-------|--------------|
| 1 | Every source_id mapped to step(s) or elimination_record | Yes |
| 2 | source_id count == mapped + eliminated | Yes |
| 3 | All model fields use live API field names from snapshot | Yes |
| 4 | All gate criteria use live `GateCriteria` fields | Yes |
| 5 | All semantic checks use `Callable[[str], bool]` signature | Yes |
| 6 | Pattern coverage matrix has no "unsupported" entries | Yes |
| 7 | Pure-programmatic steps have complete Python code | Yes |
| 8 | Prompt count matches Claude-assisted + hybrid step count | Advisory |

**Output artifacts**:
- `portify-spec.md` (+ optional `portify-prompts.md`) — Human-readable code spec.
- `portify-spec.yaml` — Machine contract.

**Contract emitted**: `portify-spec.yaml`
```yaml
phase: 2
status: completed
step_mapping:
  - source_id: "S-001"
    generated_steps: ["step_inventory"]
    mapping_type: "1:1"
  - source_id: "S-007"
    generated_steps: []
    mapping_type: "elimination"
    elimination_reason: "Merged into S-006 — same artifact"
module_plan:
  required: [models, gates, prompts, config, executor, monitor, process, tui, logging_, diagnostics, commands, __init__]
  optional_included: [inventory, filtering]
  optional_excluded: []
gate_definitions:
  - step: "step_inventory"
    tier: "LIGHT"
    mode: "BLOCKING"
    semantic_checks: []
pattern_coverage:
  all_covered: true
  unsupported: []
api_conformance:
  snapshot_hash: <hash of api-snapshot.yaml>
  all_fields_valid: true
  mismatches: []
```

**Present to user for approval before Phase 3.**

**Failure routing**:
- Coverage invariant fails → `status: failed`, list unmapped source_ids. Resumable.
- API conformance fails → `status: failed`, list mismatches with live vs spec. Correctable.
- Unsupported pattern → `status: failed`, list unsupported patterns. Abort with explanation.

### 2.4 Phase 3: Code Generation

**Purpose**: Emit syntactically valid, import-resolvable, contract-compatible Python files.

**Entry criteria**: Phase 2 contract validates (status: completed, all_covered: true, all_fields_valid: true).

**Refs loaded**: `refs/code-templates.md`

**Behavioral instructions**:

1. **Generate files in dependency order**: models → gates → prompts → config → monitor → process → executor → tui → logging_ → diagnostics → commands → `__init__`.py
2. Each file imports from `superclaude.cli.pipeline` for shared base types.
3. **Atomic generation**: If any file fails mid-generation, do not proceed to next file. Record failure and halt.

**Post-generation validation (per file)**:

| # | Check | Method | Blocks? |
|---|-------|--------|---------|
| 1 | Python syntax valid | `ast.parse(source)` | Yes |
| 2 | No undefined names in imports | Parse import statements, verify targets exist in package or stdlib | Yes |
| 3 | Base class contracts satisfied | Verify generated classes extend correct pipeline base types | Yes |
| 4 | `GateCriteria` field names match snapshot | String comparison against api-snapshot.yaml | Yes |
| 5 | `SemanticCheck` signature correct | AST check: check_fn is `Callable[[str], bool]` | Yes |
| 6 | `gate_passed()` not re-implemented | Verify import from pipeline.gates, not redefined | Advisory |

**Post-generation validation (cross-file)**:

| # | Check | Method | Blocks? |
|---|-------|--------|---------|
| 7 | All planned modules from Phase 2 were emitted | Compare file list to module_plan | Yes |
| 8 | No circular imports | Build import graph, verify acyclic | Yes |
| 9 | Package `__init__.py` exports match commands.py expectations | AST parse both files | Yes |
| 10 | Step count in generated code matches Phase 2 step_mapping | Count Step definitions | Yes |

**Output artifacts**:
- Generated Python files in target directory
- `portify-codegen.yaml` — Machine contract

**Contract emitted**: `portify-codegen.yaml`
```yaml
phase: 3
status: completed
generated_files:
  - path: <relative path>
    lines: <int>
    syntax_valid: true
    imports_valid: true
    contract_check: passed
validation_results:
  per_file_checks_passed: <int>
  per_file_checks_total: <int>
  cross_file_checks_passed: <int>
  cross_file_checks_total: <int>
  failures: []
```

**Failure routing**:
- `ast.parse` fails → `status: compile_failed`, include file path + error. Resumable from that file.
- Import resolution fails → `status: import_failed`, include unresolved imports. Resumable.
- Contract mismatch → `status: contract_failed`, include expected vs actual. Correctable by updating refs.
- Circular import → `status: import_failed`, include cycle path. Requires manual intervention.

### 2.5 Phase 4: Integration & Validation

**Purpose**: Wire the generated module into the CLI, run contract tests, produce summary.

**Entry criteria**: Phase 3 contract validates (status: completed, all checks passed).

**Behavioral instructions**:

1. **Patch `main.py`** — Add import and `app.add_command()`.
   - **Collision check**: If command name already exists in main.py, abort with naming conflict error (guard gap fix).
   - **Naming rules**: kebab-case for CLI name, snake_case for Python module name, PascalCase for class names.
2. **Run integration smoke test** — Import the new module in an isolated context. Verify:
   - Module imports without error
   - Exported Click command group exists
   - Command name matches expected registration
3. **Generate structural test** — Validates:
   - Step graph completeness (all steps defined)
   - Gate definitions present for all gated steps
   - Model consistency (config fields, result fields)
   - Command registration
4. **Write `portify-summary.md`** — File inventory, CLI usage, step graph, known limitations, resume command template.

**Self-validation (post-write)**:

| # | Check | Blocks? |
|---|-------|---------|
| 1 | main.py patch applies cleanly | Yes |
| 2 | Generated module imports successfully | Yes |
| 3 | Click command group is accessible | Yes |
| 4 | Structural test file is syntactically valid | Yes |
| 5 | Summary file written and non-empty | Advisory |

**Output artifacts**:
- Patched `main.py`
- `test_<name>_structure.py`
- `portify-summary.md`
- `portify-integration.yaml` — Machine contract

---

## 3. Return Contract (C3, per adversarial pattern)

**Mandatory on every invocation**, including failures.

```yaml
return_contract:
  output_directory: <path>
  status: <success|partial|failed>
  failure_phase: <null|0|1|2|3|4>
  failure_type: <null|prerequisite_failed|analysis_incomplete|spec_invalid|
                 compile_failed|import_failed|contract_failed|
                 integration_failed|unsupported_pattern>
  generated_files: [<paths>]
  source_step_count: <int>
  generated_step_count: <int>
  elimination_count: <int>
  api_snapshot_hash: <string>
  resume_command: <string|null>
  resume_phase: <int|null>
  warnings: [<strings>]
  phase_contracts: [<paths to .yaml files>]
```

**Write-on-failure**: If the pipeline aborts at any phase, write the return contract with `status: "failed"`, `failure_phase` set, and all unreached fields set to `null`.

---

## 4. MCP Usage Contract (M2)

Phase-level MCP server mapping, following roadmap-protocol's wave-level pattern.

| Phase | MCP Server | Purpose |
|-------|-----------|---------|
| 0 | Auggie (codebase-retrieval) | Locate workflow components, read live pipeline API |
| 0 | Serena | Symbol-level API signature extraction from models.py/gates.py |
| 1 | Auggie (codebase-retrieval) | Discover agents, trace data flow across files |
| 1 | Sequential | Classification conflict resolution (when confidence < 0.7) |
| 2 | Context7 | Framework/library API lookup if workflow references external libs |
| 2 | Sequential | Complex executor design decisions |
| 3 | Serena | Verify generated code symbols against pipeline module |
| 4 | Serena | Verify main.py integration patch correctness |

**Rule**: If an MCP server is unavailable, the phase may proceed with native tools only, but must log the degradation in the phase contract's `advisory_warnings`.

---

## 5. Progress Tracking Contract (M3)

TodoWrite integration at phase and subphase level.

### 5.1 Required TodoWrite Updates

```
Phase 0: Prerequisites
  ├─ [pending] Resolve workflow path
  ├─ [pending] Snapshot pipeline API
  ├─ [pending] Check output collision
  └─ [pending] Early pattern scan

Phase 1: Workflow Analysis
  ├─ [pending] Discover components
  ├─ [pending] Decompose into steps
  ├─ [pending] Classify steps
  ├─ [pending] Map dependencies
  ├─ [pending] Extract gates
  ├─ [pending] Self-validation
  └─ [pending] User review

Phase 2: Pipeline Specification
  ├─ [pending] Design step graph
  ├─ [pending] Design models
  ├─ [pending] Design prompts
  ├─ [pending] Design gates
  ├─ [pending] Implement programmatic steps
  ├─ [pending] Design executor
  ├─ [pending] Assess pattern coverage
  ├─ [pending] Self-validation
  └─ [pending] User approval

Phase 3: Code Generation
  ├─ [pending] Generate files (12+ modules)
  ├─ [pending] Per-file validation
  └─ [pending] Cross-file validation

Phase 4: Integration
  ├─ [pending] Patch main.py
  ├─ [pending] Integration smoke test
  ├─ [pending] Generate structural test
  └─ [pending] Write summary
```

### 5.2 Checkpoint Triggers

- After each phase completion
- After user review/approval gates
- Before any write operation
- On any failure (preserve resume state)

---

## 6. Failure Routing & Resume Protocol (M6)

### 6.1 Failure Status Model

| Status | Phase | Blocking? | Remediation |
|--------|-------|-----------|-------------|
| `prerequisite_failed` | 0 | Yes | Fix input, re-run |
| `analysis_incomplete` | 1 | Yes | Review uncovered steps, re-run Phase 1 |
| `unsupported_pattern` | 0-2 | Yes | Simplify workflow or extend templates |
| `spec_invalid` | 2 | Yes | Fix spec, re-run Phase 2 |
| `template_mismatch` | 2 | Yes | Add template or abort |
| `compile_failed` | 3 | Yes | Fix generated code at failure point, resume |
| `import_failed` | 3 | Yes | Fix imports, resume from failed file |
| `contract_failed` | 3 | Yes | Update refs to match live API, re-run Phase 3 |
| `integration_failed` | 4 | Yes | Fix integration, re-run Phase 4 |

### 6.2 Resume Semantics

Each phase contract records `resume_checkpoint`. On resume:
1. Read latest phase contract
2. Skip completed phases (validate their contracts still valid)
3. Resume from the failed phase
4. Return contract includes `resume_command` template

---

## 7. Step Conservation Invariant (C5)

**Hard rule**: Every source workflow instruction that constitutes an action must have a stable `source_id`.

### 7.1 Conservation equation

```
|source_step_registry| == |mapped_steps| + |elimination_records|
```

### 7.2 Elimination records

When a source step is intentionally not mapped to a generated step:

```yaml
elimination_records:
  - source_id: "S-007"
    reason: "Merged into S-006 — both produce same artifact"
    approved_by: <user|self-validation>
```

### 7.3 Divergence detection (Whittaker defense)

If a single source operation matches multiple step boundary conditions simultaneously:
1. Flag as ambiguous
2. Present both split options to user
3. Record chosen interpretation in analysis contract
4. This prevents non-deterministic splitting across runs

---

## 8. Pattern Coverage Matrix (M5)

### 8.1 Supported Patterns

| Pattern | Template | Modules | Notes |
|---------|----------|---------|-------|
| Sequential steps | Yes | executor.py | Standard linear flow |
| Batch parallelism | Yes | executor.py | ThreadPoolExecutor |
| Conditional skip | Yes | executor.py | Flag-based step skip |
| Pure programmatic | Yes | Any module | Direct function call |
| Claude-assisted | Yes | prompts.py, process.py | Subprocess + gate |
| Hybrid | Yes | Multiple | Setup → Claude → validate |
| Static fan-out | Yes | executor.py | Known batch count |

### 8.2 Unsupported Patterns (abort triggers)

| Pattern | Why unsupported | Detection |
|---------|----------------|-----------|
| Recursive self-orchestration | Agent calls itself | Agent delegation graph has cycle |
| Interactive mid-pipeline | Requires human input during step | Step has "ask user" / "prompt user" mid-execution |
| Dynamic code eval | Generated code runs `eval()` | Source step uses dynamic code generation |
| Dynamic fan-out (unknown N at design time) | Template assumes fixed step registry | Batch count determined by runtime data |
| Multi-return contract | Step returns multiple typed artifacts | Source step has polymorphic output |

### 8.3 Boundary handling

If a workflow contains a mix of supported and unsupported patterns:
- Analyze fully (Phase 1 completes)
- Flag unsupported patterns in analysis contract
- Abort before Phase 2 with clear explanation of which steps are unsupported and why

---

## 9. Live API Verification (C4)

### 9.1 API Snapshot Schema

Captured in Phase 0 from live source code:

```yaml
api_snapshot:
  captured_at: <ISO-8601>
  source_files:
    - path: src/superclaude/cli/pipeline/models.py
      hash: <sha256>
    - path: src/superclaude/cli/pipeline/gates.py
      hash: <sha256>
  contracts:
    SemanticCheck:
      fields: {name: str, check_fn: "Callable[[str], bool]", failure_message: str}
    GateCriteria:
      fields: {required_frontmatter_fields: "list[str]", min_lines: int, enforcement_tier: "Literal[...]", semantic_checks: "list[SemanticCheck] | None"}
    gate_passed:
      signature: "(output_file: Path, criteria: GateCriteria) -> tuple[bool, str | None]"
    PipelineConfig:
      fields: <extracted>
    Step:
      fields: <extracted>
    StepResult:
      fields: <extracted>
    GateMode:
      values: [BLOCKING, TRAILING]
```

### 9.2 Verification Points

- **Phase 2**: All model/gate designs checked against snapshot
- **Phase 3**: All generated code checked against snapshot (field names, signatures)
- **Phase 4**: Integration patch checked against live main.py structure

### 9.3 Drift Detection

If `refs/pipeline-spec.md` or `refs/code-templates.md` reference field names or signatures that don't match the live API snapshot, emit a blocking warning and list all mismatches. The refs must be updated before generation proceeds.

---

## 10. Command Shim Design

### 10.1 `commands/cli-portify.md` Structure

Following `commands/tasklist.md` pattern:

```yaml
---
name: cli-portify
description: "Port inference-based workflows into programmatic CLI pipelines"
category: development
complexity: high
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
mcp-servers: [sequential, serena, context7, auggie-mcp]
personas: [architect, analyzer, backend]
version: "2.0.0"
---
```

**Responsibilities**:
1. Parse arguments: `--workflow`, `--name`, `--output`, `--dry-run`, `--skip-integration`
2. Input validation (all failures emit error_code + message):
   - Workflow path resolves to valid skill directory
   - Output parent directory exists and is writable
   - Name normalization (kebab-case for CLI, snake_case for module)
   - Collision detection (target directory exists)
3. Invoke: `Skill sc:cli-portify-protocol` with validated context
4. **Classification**: STRICT — multi-file code generation with pipeline API dependencies

### 10.2 Input Validation Error Codes

| Error Code | Condition |
|------------|-----------|
| `MISSING_WORKFLOW` | `--workflow` not provided |
| `INVALID_PATH` | Path doesn't resolve to a skill directory |
| `AMBIGUOUS_PATH` | Multiple candidates match |
| `OUTPUT_NOT_WRITABLE` | Output parent directory not writable |
| `NAME_COLLISION` | CLI command name already exists in main.py |
| `DERIVATION_FAILED` | Cannot derive CLI name from workflow |

---

## 11. Naming and Collision Policy (M7)

### 11.1 Name Normalization

| Context | Convention | Example |
|---------|-----------|---------|
| CLI subcommand | kebab-case | `cleanup-audit` |
| Python package | snake_case | `cleanup_audit` |
| Class names | PascalCase | `CleanupAuditConfig` |
| Config prefix | UPPER_SNAKE | `CLEANUP_AUDIT_` |

**Derivation from workflow name**: Strip `sc-` prefix, strip `-protocol` suffix, apply convention.

### 11.2 Collision Policy

If target package directory already exists:
1. Check if it was generated by a previous portification (look for `portify-summary.md`)
2. If yes: offer overwrite or abort (user choice)
3. If no (human-written code): abort — never overwrite non-portified code
4. Main.py command name collision: always abort with `NAME_COLLISION`

---

## 12. Ref File Updates Required

The spec review found concrete API drift in `refs/pipeline-spec.md`. Before the protocol can be used:

| Ref file | Issue | Fix |
|----------|-------|-----|
| `refs/pipeline-spec.md` | Uses `GateCriteria(tier=..., required_frontmatter=[...])` | Update to `GateCriteria(enforcement_tier=..., required_frontmatter_fields=[...])` |
| `refs/pipeline-spec.md` | Semantic functions returning `(bool, str)` | Update: `check_fn` is `Callable[[str], bool]`; `gate_passed()` returns `tuple[bool, str \| None]` |
| `refs/code-templates.md` | Template examples may use stale field names | Audit all templates against api-snapshot |

---

## 13. Measurable Claims (N2)

Replace aspirational language with verifiable requirements:

| Old claim | New claim |
|-----------|-----------|
| "ensure 100% completion" | "all required phases either pass blocking checks or halt with a resumable failure state" |
| "consistency between runs" | "same inputs produce same source_step_registry, same step_mapping, and same module_plan" |
| "any workflow" | "any workflow whose patterns are covered by the pattern coverage matrix (Section 8)" |

---

## 14. Boundaries (N3, updated)

### Will Do
- Analyze SuperClaude skill/command/agent workflows whose patterns are in the coverage matrix
- Decompose into machine-checkable pipeline specification
- Validate generated code against live pipeline API contracts
- Generate complete CLI subcommand module with structural tests
- Wire module into CLI infrastructure
- Abort cleanly with resume guidance on unsupported patterns

### Will Not Do
- Execute the generated pipeline
- Modify original skill/command/agent files
- Create new skills or agents
- Generate code for unsupported patterns (Section 8.2)
- Make architectural decisions about the workflow's logic
- Generate LLM content quality tests (only structural)

---

## 15. Mapping to Spec Review Findings

| Finding | Severity | Section | Status |
|---------|----------|---------|--------|
| C1. Missing command entry point | CRITICAL | §1.1, §10 | Addressed |
| C2. No generation self-validation | CRITICAL | §2.2-2.5 (self-validation tables) | Addressed |
| C3. Phase interfaces leak | CRITICAL | §2.0, §3 | Addressed |
| C4. Pipeline API drift | CRITICAL | §9, §12 | Addressed |
| C5. No step conservation | CRITICAL | §7 | Addressed |
| M1. Commented metadata | MAJOR | §1.2 | Addressed |
| M2. MCP undeclared | MAJOR | §4 | Addressed |
| M3. No progress tracking | MAJOR | §5 | Addressed |
| M4. Vague import verification | MAJOR | §2.4 (Phase 3 validation), §2.5 | Addressed |
| M5. Template applicability | MAJOR | §8 | Addressed |
| M6. No failure routing | MAJOR | §6 | Addressed |
| M7. Output location underspecified | MAJOR | §11 | Addressed |
| N1. Sync inconsistency | MINOR | §1.3 | Addressed |
| N2. Non-measurable claims | MINOR | §13 | Addressed |
| N3. Boundaries too broad | MINOR | §14 | Addressed |

---

## 16. Downstream Inputs

### For `/sc:roadmap`
Themes: convention alignment, deterministic generation engine, contract-driven phase boundaries, validation harness, template coverage expansion, pipeline API compatibility safeguards.

### For `/sc:tasklist`
Tasks: create command shim, protocol rename/migration, phase contract schemas, self-check matrix implementation, compile/import/AST validation, coverage mapping checks, golden fixture test suite, unsupported-pattern matrix.

### For Testing Strategy
- **Generator-process tests**: decomposition completeness, classification reproducibility, phase contract validity, failure routing correctness
- **Generated-code tests**: syntax compilation, import smoke tests, pipeline primitive compatibility, command registration validation
- **Golden-fixture tests**: simple sequential skill, batched audit skill, adversarial multi-agent skill, intentionally unsupported skill
