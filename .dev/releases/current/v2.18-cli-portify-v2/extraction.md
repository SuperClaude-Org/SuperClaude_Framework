Now I have the full spec. Let me produce the requirements extraction document.

---

```yaml
---
functional_requirements: 87
complexity_score: 0.92
complexity_class: enterprise
---
```

# Requirements Extraction: sc:cli-portify v2.0

## 1. Functional Requirements

### Architecture & File Structure
1. **FR-001**: Split current monolithic skill into thin command shim (`commands/cli-portify.md`) and full protocol skill (`skills/sc-cli-portify-protocol/SKILL.md`) following the tasklist pattern.
2. **FR-002**: Migrate current `sc-cli-portify/SKILL.md` to `sc-cli-portify-protocol/SKILL.md`.
3. **FR-003**: Migrate current `sc-cli-portify/refs/` into the protocol directory.
4. **FR-004**: Create new `commands/cli-portify.md` with input validation and `Skill sc:cli-portify-protocol` invocation.
5. **FR-005**: Deprecate and remove old `sc-cli-portify/` directory after migration.
6. **FR-006**: Promote commented metadata into real YAML frontmatter fields (name, description, category, complexity, allowed-tools, mcp-servers, personas, argument-hint).
7. **FR-007**: Both `src/` and `.claude/` copies must include `__init__.py`; `make verify-sync` must cover the protocol directory.

### Phase Contract Model
8. **FR-008**: Every phase (0-4) must emit two artifacts: a human review `.md` document and a machine-readable `.yaml` contract.
9. **FR-009**: Every `.yaml` contract must include the unified schema fields: `phase`, `status`, `timestamp`, `resume_checkpoint`, `validation_status` (with `blocking_checks_passed`, `blocking_checks_total`, `advisory_warnings`).
10. **FR-010**: Each phase's entry criteria must validate the incoming contract from the previous phase before proceeding.

### Phase 0: Prerequisites
11. **FR-011**: Resolve workflow path — locate command `.md`, skill `SKILL.md`, all refs/rules/templates/scripts from the `--workflow` argument.
12. **FR-012**: If workflow path resolves to multiple candidates, abort with disambiguation error.
13. **FR-013**: Snapshot live pipeline API by reading `models.py` and `gates.py`, extracting `SemanticCheck`, `GateCriteria`, `gate_passed()`, `PipelineConfig`, `Step`, `StepResult`, `GateMode` signatures.
14. **FR-014**: Store API snapshot as `api-snapshot.yaml`.
15. **FR-015**: Check output collision — if target directory exists, apply naming policy (§11.2).
16. **FR-016**: Perform early unsupported-pattern scan detecting: recursive agent self-orchestration, interactive human decisions mid-pipeline, no stable artifact boundaries, dynamic code generation/eval patterns.
17. **FR-017**: Emit blocking warning before investing analysis effort if unsupported patterns detected.
18. **FR-018**: Any prerequisite failure must abort with error code and corrective action, producing no partial output.
19. **FR-019**: Emit `portify-prerequisites.yaml` contract with fields: `workflow_path`, `component_count`, `api_snapshot_path`, `unsupported_patterns_detected`, `output_directory`, `collision_policy_applied`.

### Phase 1: Workflow Analysis
20. **FR-020**: Build component inventory with paths, line counts, purposes; assign stable `component_id` (C-NNN) to each.
21. **FR-021**: Decompose workflow into steps using step boundary algorithm; assign stable `source_id` (S-NNN) to each.
22. **FR-022**: Enforce conservation invariant: every source operation maps to exactly one `source_id`; no `source_id` created without tracing to a specific source location.
23. **FR-023**: Classify each step as pure_programmatic, claude_assisted, or hybrid with confidence score (0.0-1.0).
24. **FR-024**: Flag steps with classification confidence < 0.7 for user review with justification.
25. **FR-025**: Provide evidence (specific lines/patterns) supporting each classification.
26. **FR-026**: Map dependencies as a DAG with data flow edges; validate acyclicity.
27. **FR-027**: Extract and assign gate tier + mode for each step output.
28. **FR-028**: Check trailing gate safety — escalate TRAILING to BLOCKING if downstream step consumes that output as prompt context.
29. **FR-029**: Perform 7 self-validation checks before writing output (6 blocking, 1 advisory).
30. **FR-030**: Emit `portify-analysis.md` (under 400 lines) and `portify-analysis.yaml` with component_inventory, source_step_registry, dependency_graph, parallel_groups, validation_results.
31. **FR-031**: Present analysis to user for review; allow user to override classifications or flag missing steps.
32. **FR-032**: On self-validation failure, set `status: failed`, list failing checks, suggest corrections; resumable from Phase 1.

### Phase 2: Pipeline Specification
33. **FR-033**: Design step graph mapping each `source_id` to generated step(s) with recorded mapping types (1:1, 1:N, N:1, 1:0 elimination).
34. **FR-034**: Enforce coverage invariant: `source_step_registry` count == mapped steps + elimination_records.
35. **FR-035**: Design domain-specific dataclass models conforming to live API snapshot: Config extending `PipelineConfig`, Result extending `StepResult`, Status enum, Monitor state with NDJSON signals, `TurnLedger` integration.
36. **FR-036**: Design prompts for each Claude-assisted step specifying input embedding strategy, required output sections/frontmatter, machine-readable markers, structural requirements for gate checking.
37. **FR-037**: Split prompts to `portify-prompts.md` when collectively > 300 lines (strict `>` not `>=`).
38. **FR-038**: Design gates using live `GateCriteria` field names from API snapshot with correct types.
39. **FR-039**: Semantic check functions must use `Callable[[str], bool]` signature (not `tuple[bool, str]`).
40. **FR-040**: Implement pure-programmatic steps as full Python code, not descriptions.
41. **FR-041**: Design executor as sprint-style synchronous supervisor with `ThreadPoolExecutor` for batch parallelism.
42. **FR-042**: Build pattern coverage matrix verifying code templates cover all required patterns; blocking abort if unsupported pattern found.
43. **FR-043**: Plan CLI integration: Click command group, main.py import, naming.
44. **FR-044**: Perform 8 self-validation checks before writing (7 blocking, 1 advisory).
45. **FR-045**: Emit `portify-spec.md`, optional `portify-prompts.md`, and `portify-spec.yaml` with step_mapping, module_plan, gate_definitions, pattern_coverage, api_conformance.
46. **FR-046**: Present spec to user for approval before Phase 3.

### Phase 3: Code Generation
47. **FR-047**: Generate files in dependency order: models → gates → prompts → config → monitor → process → executor → tui → logging_ → diagnostics → commands → `__init__.py`.
48. **FR-048**: Each generated file must import from `superclaude.cli.pipeline` for shared base types.
49. **FR-049**: Atomic generation — if any file fails mid-generation, halt; do not proceed to next file.
50. **FR-050**: Per-file validation: Python syntax via `ast.parse()` (blocking).
51. **FR-051**: Per-file validation: no undefined names in imports (blocking).
52. **FR-052**: Per-file validation: base class contracts satisfied — generated classes extend correct pipeline base types (blocking).
53. **FR-053**: Per-file validation: `GateCriteria` field names match API snapshot (blocking).
54. **FR-054**: Per-file validation: `SemanticCheck` signature correct via AST check (blocking).
55. **FR-055**: Per-file validation: `gate_passed()` not re-implemented, imported from `pipeline.gates` (advisory).
56. **FR-056**: Cross-file validation: all planned modules from Phase 2 emitted (blocking).
57. **FR-057**: Cross-file validation: no circular imports — build import graph, verify acyclic (blocking).
58. **FR-058**: Cross-file validation: `__init__.py` exports match `commands.py` expectations (blocking).
59. **FR-059**: Cross-file validation: step count in generated code matches Phase 2 `step_mapping` (blocking).
60. **FR-060**: Emit `portify-codegen.yaml` with generated_files details and validation_results.

### Phase 4: Integration & Validation
61. **FR-061**: Patch `main.py` with import and `app.add_command()`.
62. **FR-062**: Collision check on `main.py` — abort with naming conflict if command name already exists.
63. **FR-063**: Enforce naming rules: kebab-case for CLI name, snake_case for Python module, PascalCase for class names.
64. **FR-064**: Run integration smoke test: module imports without error, Click command group exists, command name matches expected registration.
65. **FR-065**: Generate structural test file (`test_<name>_structure.py`) validating step graph completeness, gate definitions, model consistency, command registration.
66. **FR-066**: Write `portify-summary.md` with file inventory, CLI usage, step graph, known limitations, resume command template.
67. **FR-067**: Perform 5 post-write validation checks (4 blocking, 1 advisory).

### Return Contract
68. **FR-068**: Emit mandatory return contract on every invocation (including failures) with fields: `output_directory`, `status`, `failure_phase`, `failure_type`, `generated_files`, `source_step_count`, `generated_step_count`, `elimination_count`, `api_snapshot_hash`, `resume_command`, `resume_phase`, `warnings`, `phase_contracts`.
69. **FR-069**: On pipeline abort at any phase, write return contract with `status: "failed"`, `failure_phase` set, unreached fields set to `null`.

### Command Shim
70. **FR-070**: Parse arguments: `--workflow`, `--name`, `--output`, `--dry-run`, `--skip-integration`.
71. **FR-071**: Validate workflow path resolves to valid skill directory.
72. **FR-072**: Validate output parent directory exists and is writable.
73. **FR-073**: Normalize names (kebab-case for CLI, snake_case for module).
74. **FR-074**: Detect collisions (target directory exists).
75. **FR-075**: Emit specific error codes for validation failures: `MISSING_WORKFLOW`, `INVALID_PATH`, `AMBIGUOUS_PATH`, `OUTPUT_NOT_WRITABLE`, `NAME_COLLISION`, `DERIVATION_FAILED`.
76. **FR-076**: Invoke `Skill sc:cli-portify-protocol` with validated context.

### Naming & Collision Policy
77. **FR-077**: Derive names by stripping `sc-` prefix and `-protocol` suffix, then applying convention per context.
78. **FR-078**: If target directory exists and was previously portified (contains `portify-summary.md`), offer overwrite or abort.
79. **FR-079**: If target directory exists and is human-written code, always abort.
80. **FR-080**: `main.py` command name collision always aborts with `NAME_COLLISION`.

### MCP Usage
81. **FR-081**: Map MCP servers to phases as specified (Auggie for 0/1, Serena for 0/3/4, Sequential for 1/2, Context7 for 2).
82. **FR-082**: If MCP server unavailable, proceed with native tools but log degradation in phase contract `advisory_warnings`.

### Progress Tracking
83. **FR-083**: Maintain TodoWrite entries at phase and subphase level (21+ discrete items across 5 phases).
84. **FR-084**: Checkpoint after each phase completion, user review gates, before write operations, and on any failure.

### Failure Routing & Resume
85. **FR-085**: Support 9 distinct failure status types with per-type remediation paths.
86. **FR-086**: Record `resume_checkpoint` in each phase contract; on resume: read latest contract, validate completed phases, resume from failed phase.
87. **FR-087**: Include `resume_command` template in return contract.

---

## 2. Non-Functional Requirements

### Determinism & Reproducibility
1. **NFR-001**: Same inputs must produce same `source_step_registry`, same `step_mapping`, and same `module_plan` (§13).
2. **NFR-002**: Step conservation invariant must hold: `|source_step_registry| == |mapped_steps| + |elimination_records|` (§7.1).

### Correctness & Safety
3. **NFR-003**: Never overwrite non-portified (human-written) code (§11.2).
4. **NFR-004**: All generated code must be syntactically valid Python (verified via `ast.parse`).
5. **NFR-005**: All generated code must be import-resolvable with no circular dependencies.
6. **NFR-006**: All generated models/gates must conform to live pipeline API contracts (not stale refs).

### Scope Constraints
7. **NFR-007**: Only workflows whose patterns are covered by the pattern coverage matrix (§8) are supported — not "any workflow."
8. **NFR-008**: Must not execute the generated pipeline, modify original workflow files, or create new skills/agents (§14).
9. **NFR-009**: Only structural tests generated — no LLM content quality tests.

### Measurability
10. **NFR-010**: All required phases must either pass blocking checks or halt with a resumable failure state — no silent partial completion.
11. **NFR-011**: Replace all aspirational claims with verifiable, measurable requirements (§13).

### API Compatibility
12. **NFR-012**: Ref files (`pipeline-spec.md`, `code-templates.md`) must be updated to match live API before protocol use (§12).
13. **NFR-013**: Drift detection: if refs reference field names/signatures not matching live API snapshot, emit blocking warning with full mismatch list.

### Compliance Tier
14. **NFR-014**: Command classified as STRICT — multi-file code generation with pipeline API dependencies (§10.1).

### Documentation
15. **NFR-015**: Human-readable analysis document must be under 400 lines (§2.2).
16. **NFR-016**: Prompts split to separate file when exceeding 300 lines (§2.3).

---

## 3. Complexity Assessment

**Score: 0.92 — Enterprise**

**Justification:**
- **5-phase pipeline** with strict contract boundaries between each phase, entry/exit criteria, and machine-readable YAML contracts — this is a compiler-like architecture.
- **30+ self-validation checks** across phases (blocking and advisory), including AST parsing, import graph analysis, and API conformance verification.
- **9 distinct failure types** with per-type remediation paths and resume-from-failure semantics.
- **Live API snapshot verification** — generated code must be validated against runtime-extracted type signatures, not static documentation.
- **Step conservation invariant** with formal equation, elimination records, and divergence detection — mathematical guarantees on transformation fidelity.
- **Multi-MCP orchestration** across 4 servers with graceful degradation.
- **Code generation** of 12+ Python modules in dependency order with per-file and cross-file validation.
- **Atomic generation** semantics (halt on first failure, no partial output).
- **Pattern coverage matrix** acting as a capability gate — unsupported patterns cause deterministic aborts.
- The spec addresses 15 findings from a prior review (5 CRITICAL, 7 MAJOR, 3 MINOR), indicating this is a hardened second-pass design.

---

## 4. Key Architectural Constraints

1. **Command/Protocol separation**: Thin shim handles parsing/validation only; all logic lives in the protocol skill. Mirrors existing `tasklist` pattern.
2. **Contract-driven phase boundaries**: Phases communicate exclusively via typed YAML contracts, not prose documents. Eliminates "re-interpret prose" leak.
3. **Live API as source of truth**: Generated code is validated against runtime-extracted API signatures (`api-snapshot.yaml`), not against reference documentation. Ref files are explicitly marked as potentially drifted and must be updated.
4. **Dependency-ordered generation**: Files generated in strict order (models → gates → ... → `__init__.py`). Each file imports from `superclaude.cli.pipeline` for shared base types.
5. **Atomic failure semantics**: No partial output on Phase 0 failure. Mid-generation file failure halts entire Phase 3. Return contract always emitted.
6. **Unsupported patterns are hard aborts**: 5 specific patterns (recursive orchestration, interactive mid-pipeline, dynamic eval, dynamic fan-out, multi-return) cause deterministic abort — no fallback or degraded mode.
7. **User gates between phases**: Phase 1 analysis presented for user review; Phase 2 spec requires user approval before code generation begins.
8. **Naming convention enforcement**: Strict kebab-case/snake_case/PascalCase/UPPER_SNAKE rules derived algorithmically from workflow name.

---

## 5. Open Questions & Ambiguities

1. **`--dry-run` behavior undefined**: §10.1 lists `--dry-run` as a command argument but the spec never defines what dry-run mode produces. Does it stop after Phase 1? Phase 2? Does it emit contracts but no code?

2. **`--skip-integration` scope unclear**: Listed as a command argument (§10.1) but not referenced in any phase. Presumably skips Phase 4, but this should be explicit — does it still emit a return contract? What status?

3. **Section 5.3 referenced but doesn't exist**: Phase 0 (§2.1, item 3) references "Section 5.3" for collision naming policy, but §5 covers Progress Tracking. The actual collision policy is in §11.2. This is a cross-reference error.

4. **`TurnLedger` integration undefined**: Phase 2 model design (§2.3, item 2) requires `TurnLedger` integration but this type is never defined in the spec nor included in the API snapshot schema (§9.1).

5. **Elimination record approval**: §7.2 shows `approved_by: <user|self-validation>` but the spec doesn't clarify when user approval is required vs. when self-validation can auto-approve eliminations.

6. **Phase 4 contract schema missing**: §2.5 mentions `portify-integration.yaml` as an output but never defines its contract schema (unlike Phases 0-3 which have explicit YAML schemas).

7. **`portify-summary.md` detection heuristic**: §11.2 uses presence of `portify-summary.md` to determine if a directory was previously portified. This could produce false positives if a user manually creates this file.

8. **Resume validation of completed phases**: §6.2 says "validate their contracts still valid" for completed phases on resume, but doesn't specify what happens if a previously-completed phase's contract is now invalid (e.g., source files changed between runs).

9. **Parallel group dynamic batching**: The analysis contract (§2.2) includes `batch_dynamic: <true|false>` per parallel group, but dynamic fan-out is listed as unsupported (§8.2). The relationship between `batch_dynamic` and the unsupported pattern is unclear.

10. **Ref file update ownership**: §12 identifies concrete API drift in ref files as a prerequisite fix, but doesn't specify whether the protocol itself should update refs (auto-fix) or whether this is a manual pre-condition the user must satisfy before running the tool.
