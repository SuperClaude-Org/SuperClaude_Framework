---
spec_source: "refactoring-spec-cli-portify.md"
generated: "2026-03-08T00:00:00Z"
generator: "requirements-extraction-agent"
functional_requirements: 52
nonfunctional_requirements: 18
total_requirements: 70
complexity_score: 0.92
complexity_class: "enterprise"
domains_detected: 7
risks_identified: 12
dependencies_identified: 9
success_criteria_count: 14
extraction_mode: "full"
pipeline_diagnostics: {elapsed_seconds: 146.0, started_at: "2026-03-08T15:59:34.710170+00:00", finished_at: "2026-03-08T16:02:00.730983+00:00"}
---

## Functional Requirements

**FR-001**: Implement command/protocol split — thin command shim (`commands/cli-portify.md`) delegates to full protocol skill (`sc-cli-portify-protocol/SKILL.md`), following the tasklist pattern. (§1.1)

**FR-002**: Migrate current `sc-cli-portify/SKILL.md` to `sc-cli-portify-protocol/SKILL.md` and move `refs/` into the protocol directory. (§1.1)

**FR-003**: Create new `commands/cli-portify.md` with input validation and `Skill sc:cli-portify-protocol` invocation. (§1.1)

**FR-004**: Deprecate and remove old `sc-cli-portify/` directory after migration completes. (§1.1)

**FR-005**: Promote commented metadata into real YAML frontmatter fields including name, description, category, complexity, allowed-tools, mcp-servers, personas, and argument-hint. (§1.2)

**FR-006**: Ensure both `src/` and `.claude/` copies include `__init__.py` and that `make verify-sync` covers the protocol directory. (§1.3)

**FR-007**: Every phase must emit two artifacts: a human review document (`.md`) and a machine-readable contract (`.yaml`). (§2.0)

**FR-008**: Each `.yaml` contract must include the unified common header: phase, status, timestamp, resume_checkpoint, and validation_status fields. (§2.0)

**FR-009**: Next phase entry criteria must validate the incoming contract before proceeding. (§2.0)

**FR-010**: Phase 0 must resolve workflow path from `--workflow` argument, locating command `.md`, skill `SKILL.md`, and all refs/rules/templates/scripts. Abort with disambiguation error on multiple candidates. (§2.1)

**FR-011**: Phase 0 must snapshot live pipeline API by reading `models.py` and `gates.py`, extracting `SemanticCheck`, `GateCriteria`, `gate_passed()`, `PipelineConfig`, `Step`, `StepResult`, and `GateMode` signatures. Store as `api-snapshot.yaml`. (§2.1)

**FR-012**: Phase 0 must check output directory collision and apply naming policy per §11. (§2.1)

**FR-013**: Phase 0 must perform early unsupported-pattern scan detecting: recursive agent self-orchestration, interactive human decisions mid-pipeline, no stable artifact boundaries, and dynamic code generation/eval patterns. Emit blocking warning on detection. (§2.1)

**FR-014**: Phase 0 must emit `portify-prerequisites.yaml` contract with workflow_path, component_count, api_snapshot_path, unsupported_patterns_detected, output_directory, and collision_policy_applied. (§2.1)

**FR-015**: Phase 1 must build component inventory with stable `component_id` (C-NNN), paths, line counts, and purposes. (§2.2)

**FR-016**: Phase 1 must decompose workflow into steps with stable `source_id` (S-NNN), enforcing the conservation invariant — every source operation maps to exactly one source_id. (§2.2)

**FR-017**: Phase 1 must classify each step as pure_programmatic, claude_assisted, or hybrid with confidence score (0.0-1.0). Flag for user review if confidence < 0.7 with justification and evidence. (§2.2)

**FR-018**: Phase 1 must map dependencies as a DAG with data flow edges and validate acyclicity. (§2.2)

**FR-019**: Phase 1 must extract and assign gate tier (EXEMPT/LIGHT/STANDARD/STRICT) and mode (BLOCKING/TRAILING) for each step output. (§2.2)

**FR-020**: Phase 1 must check trailing gate safety — escalate TRAILING to BLOCKING if any downstream step consumes the output as prompt context. (§2.2)

**FR-021**: Phase 1 must pass 7 self-validation checks (6 blocking, 1 advisory) before writing output. (§2.2)

**FR-022**: Phase 1 must emit `portify-analysis.md` (under 400 lines) and `portify-analysis.yaml` with component_inventory, source_step_registry, dependency_graph, parallel_groups, and validation_results. (§2.2)

**FR-023**: Phase 1 must present analysis to user for review with ability to override classifications or flag missing steps. (§2.2)

**FR-024**: Phase 2 must design step graph mapping each source_id to generated Step(s), recording 1:1, 1:N, N:1, or 1:0 (elimination) mappings with justification. (§2.3)

**FR-025**: Phase 2 must enforce coverage invariant: `source_step_registry` count == mapped steps + elimination_records. (§2.3)

**FR-026**: Phase 2 must design domain-specific dataclass models conforming to live API snapshot — Config extending `PipelineConfig`, Result extending `StepResult`, Status enum, Monitor state with NDJSON signals, and `TurnLedger` integration. (§2.3)

**FR-027**: Phase 2 must design prompts for each Claude-assisted step specifying input strategy, output sections, frontmatter fields, machine-readable markers, and structural requirements. Split to `portify-prompts.md` if collectively > 300 lines. (§2.3)

**FR-028**: Phase 2 must design gates using live `GateCriteria` field names: `required_frontmatter_fields`, `min_lines`, `enforcement_tier`, `semantic_checks`. Semantic check functions must use `Callable[[str], bool]` signature. (§2.3)

**FR-029**: Phase 2 must implement pure-programmatic steps as full Python code, not descriptions. (§2.3)

**FR-030**: Phase 2 must design executor as sprint-style synchronous supervisor with ThreadPoolExecutor for batch parallelism. (§2.3)

**FR-031**: Phase 2 must assess pattern coverage by verifying code templates cover all required patterns. Build coverage matrix. Abort if any unsupported pattern is found. (§2.3)

**FR-032**: Phase 2 must pass 8 self-validation checks (7 blocking, 1 advisory) before writing output. (§2.3)

**FR-033**: Phase 2 must emit `portify-spec.yaml` with step_mapping, module_plan, gate_definitions, pattern_coverage, and api_conformance. Present to user for approval before Phase 3. (§2.3)

**FR-034**: Phase 3 must generate Python files in dependency order: models → gates → prompts → config → monitor → process → executor → tui → logging_ → diagnostics → commands → `__init__.py`. (§2.4)

**FR-035**: Phase 3 must enforce atomic generation — halt and record failure if any file fails mid-generation. (§2.4)

**FR-036**: Phase 3 must perform 6 per-file validation checks (5 blocking, 1 advisory) including `ast.parse`, import verification, base class contracts, `GateCriteria` field name matching, and `SemanticCheck` signature verification. (§2.4)

**FR-037**: Phase 3 must perform 4 cross-file validation checks (all blocking) including module completeness, circular import detection, `__init__.py` export matching, and step count matching. (§2.4)

**FR-038**: Phase 3 must emit `portify-codegen.yaml` with generated_files list and validation_results. (§2.4)

**FR-039**: Phase 4 must patch `main.py` with import and `app.add_command()`, aborting on naming collision. (§2.5)

**FR-040**: Phase 4 must run integration smoke test — verify module imports, Click command group exists, and command name matches registration. (§2.5)

**FR-041**: Phase 4 must generate structural test file (`test_<name>_structure.py`) validating step graph completeness, gate definitions, model consistency, and command registration. (§2.5)

**FR-042**: Phase 4 must write `portify-summary.md` with file inventory, CLI usage, step graph, known limitations, and resume command template. (§2.5)

**FR-043**: Return contract must be emitted on every invocation including failures, with status, failure_phase, failure_type, generated_files, counts, api_snapshot_hash, resume_command, warnings, and phase_contracts. (§3)

**FR-044**: Command shim must parse arguments: `--workflow`, `--name`, `--output`, `--dry-run`, `--skip-integration`. (§10.1)

**FR-045**: Command shim must perform input validation with 6 defined error codes: MISSING_WORKFLOW, INVALID_PATH, AMBIGUOUS_PATH, OUTPUT_NOT_WRITABLE, NAME_COLLISION, DERIVATION_FAILED. (§10.2)

**FR-046**: Name normalization must follow conventions: kebab-case (CLI), snake_case (Python package), PascalCase (class names), UPPER_SNAKE (config prefix). Derivation strips `sc-` prefix and `-protocol` suffix. (§11.1)

**FR-047**: Collision policy must check for previous portification via `portify-summary.md`, offer overwrite/abort for portified code, always abort for non-portified code, and always abort on main.py command name collision. (§11.2)

**FR-048**: Ref files `refs/pipeline-spec.md` and `refs/code-templates.md` must be updated to match live API field names before the protocol can be used. (§12)

**FR-049**: Step conservation invariant must hold: `|source_step_registry| == |mapped_steps| + |elimination_records|`. Elimination records require source_id, reason, and approved_by. (§7)

**FR-050**: Divergence detection must flag ambiguous source operations matching multiple step boundary conditions, present split options to user, and record chosen interpretation. (§7.3)

**FR-051**: TodoWrite integration must track 23 subphase tasks across 5 phases with checkpoint triggers after phase completion, user review gates, before write operations, and on failure. (§5)

**FR-052**: Resume protocol must read latest phase contract, skip completed phases (validating contracts still valid), resume from failed phase, and include `resume_command` template in return contract. (§6.2)

## Non-Functional Requirements

**NFR-001**: All generated code must be syntactically valid Python verifiable via `ast.parse()`. (§2.4)

**NFR-002**: Generated code must have no circular imports — import graph must be acyclic. (§2.4)

**NFR-003**: All model and gate field names in generated code must match the live pipeline API snapshot captured at runtime. (§9)

**NFR-004**: Same inputs must produce same `source_step_registry`, same `step_mapping`, and same `module_plan` — deterministic output. (§13)

**NFR-005**: Human-readable analysis output (`portify-analysis.md`) must be under 400 lines. (§2.2)

**NFR-006**: Prompts collectively > 300 lines must be split to separate `portify-prompts.md` file. (§2.3)

**NFR-007**: Each generated file must import from `superclaude.cli.pipeline` for shared base types — no reimplementation of pipeline primitives. (§2.4)

**NFR-008**: MCP server unavailability must not block phase execution — degrade to native tools with advisory warning logged in phase contract. (§4)

**NFR-009**: All failures must produce a return contract with `status: "failed"`, `failure_phase` set, and unreached fields set to `null`. (§3)

**NFR-010**: The protocol must only process workflows whose patterns are covered by the pattern coverage matrix (§8) — no aspirational "any workflow" claim. (§13)

**NFR-011**: Generated code must extend correct pipeline base types (`PipelineConfig`, `StepResult`) — no standalone reimplementations. (§2.4)

**NFR-012**: Naming must follow consistent conventions across all contexts: kebab-case CLI, snake_case Python, PascalCase classes, UPPER_SNAKE config. (§11.1)

**NFR-013**: Never overwrite non-portified (human-written) code in target directories. (§11.2)

**NFR-014**: Original skill/command/agent source files must never be modified. (§14)

**NFR-015**: Phase contracts must use stable, versioned YAML schemas with common header fields. (§2.0)

**NFR-016**: All phases must have explicit entry and exit criteria with validation. (§2.1–2.5)

**NFR-017**: Classification STRICT for the command — multi-file code generation with pipeline API dependencies requires full compliance enforcement. (§10.1)

**NFR-018**: Ref file drift from live API must produce blocking warnings — generation cannot proceed with stale references. (§9.3)

## Complexity Assessment

**Complexity Score**: 0.92 / 1.0
**Complexity Class**: Enterprise

**Scoring Rationale**:

| Factor | Score | Weight | Contribution |
|--------|-------|--------|-------------|
| Phase count (5 phases with inter-phase contracts) | 0.95 | 0.20 | 0.190 |
| Validation density (30+ blocking checks across phases) | 0.95 | 0.15 | 0.143 |
| Code generation with AST verification | 0.90 | 0.15 | 0.135 |
| Live API contract verification at runtime | 0.90 | 0.10 | 0.090 |
| Multi-domain: code gen, CLI, testing, AST, YAML contracts | 0.90 | 0.10 | 0.090 |
| Resume/failure routing (9 failure types, resumable) | 0.85 | 0.10 | 0.085 |
| Step conservation invariant with elimination tracking | 0.90 | 0.05 | 0.045 |
| Pattern coverage matrix with abort triggers | 0.85 | 0.05 | 0.043 |
| MCP server orchestration across 4 servers, 5 phases | 0.85 | 0.05 | 0.043 |
| Multi-file output (12+ Python modules + tests + contracts) | 0.90 | 0.05 | 0.045 |
| **Weighted Total** | | | **0.909** |

This is enterprise-grade due to: contract-driven phase boundaries with machine-readable validation, live API conformance checking, deterministic code generation with AST verification, comprehensive failure routing with resume semantics, and multi-server MCP orchestration.

## Architectural Constraints

1. **Command/Protocol Split Pattern**: Must follow the `tasklist.md` pattern — thin command shim with full protocol skill. No monolithic skill files. (§1.1)

2. **Pipeline API Conformance**: All generated code must extend `superclaude.cli.pipeline` base types (`PipelineConfig`, `Step`, `StepResult`, `GateMode`). Generated code must import from, not reimplement, pipeline primitives. (§2.4, §9)

3. **Contract-Driven Phase Boundaries**: Phases communicate exclusively through YAML contracts. No "re-interpret prose" pattern. Next phase validates incoming contract before starting. (§2.0)

4. **File Generation Order**: Strict dependency order: models → gates → prompts → config → monitor → process → executor → tui → logging_ → diagnostics → commands → `__init__.py`. (§2.4)

5. **Atomic Generation**: If any file fails mid-generation in Phase 3, halt entirely. No partial module output. (§2.4)

6. **Sync Layout**: Both `src/superclaude/` and `.claude/` must contain identical copies. `make verify-sync` must cover the protocol directory. (§1.3)

7. **Click Framework**: CLI integration uses Click command groups registered via `app.add_command()` in `main.py`. (§2.5)

8. **ThreadPoolExecutor for Parallelism**: Executor design mandates sprint-style synchronous supervisor with ThreadPoolExecutor for batch parallelism only. (§2.3)

9. **Supported Pattern Boundary**: Only the 7 supported patterns (sequential, batch parallel, conditional skip, pure programmatic, Claude-assisted, hybrid, static fan-out) can be generated. (§8.1)

10. **Boundary Exclusions**: Must not execute generated pipelines, modify source workflows, create new skills/agents, or generate LLM content quality tests. (§14)

## Risk Inventory

**RISK-001** (High): **Live API Drift** — `models.py` or `gates.py` may change between Phase 0 snapshot and Phase 3 generation, causing contract mismatches. *Mitigation*: API snapshot with hash-based verification at each phase boundary (§9). Re-snapshot and re-validate if hashes differ.

**RISK-002** (High): **Ref File Staleness** — `refs/pipeline-spec.md` and `refs/code-templates.md` already have known API drift (§12). If not updated before use, all generated code will use wrong field names. *Mitigation*: Mandatory ref file update as prerequisite; drift detection blocks generation (§9.3).

**RISK-003** (High): **Unsupported Pattern in Target Workflow** — Workflow may contain patterns not in coverage matrix (§8.2), wasting analysis effort before abort. *Mitigation*: Early pattern scan in Phase 0 (§2.1) catches common unsupported patterns before full analysis.

**RISK-004** (Medium): **Step Conservation Violation** — Complex workflows may have ambiguous step boundaries where one source operation maps to multiple classifications. *Mitigation*: Divergence detection (§7.3) flags ambiguity for user resolution. Conservation equation enforced at Phase 1 and Phase 2.

**RISK-005** (Medium): **Circular Import in Generated Code** — 12+ modules with cross-references may inadvertently create import cycles. *Mitigation*: Strict generation order (§2.4), cross-file validation check #8, import graph acyclicity verification.

**RISK-006** (Medium): **MCP Server Unavailability** — Auggie, Serena, Sequential, or Context7 may be unreachable during execution. *Mitigation*: Graceful degradation to native tools with advisory warnings logged (§4). No phase hard-blocks on MCP availability.

**RISK-007** (Medium): **Classification Confidence Below Threshold** — Steps with confidence < 0.7 require user review, potentially blocking automated execution. *Mitigation*: Present justification and evidence; allow user override (§2.2).

**RISK-008** (Medium): **main.py Command Name Collision** — Target CLI name may already exist. *Mitigation*: Collision check with `NAME_COLLISION` abort in both Phase 0 (§2.1) and Phase 4 (§2.5).

**RISK-009** (Medium): **Resume State Corruption** — Phase contracts may become inconsistent if filesystem is modified between failure and resume. *Mitigation*: Resume protocol re-validates completed phase contracts before resuming (§6.2).

**RISK-010** (Low): **Human Review Bottleneck** — User approval gates after Phase 1 and Phase 2 introduce latency in the pipeline. *Mitigation*: Design choice — approval gates are intentional for safety. `--dry-run` available for preview without commitment.

**RISK-011** (Low): **Template Coverage Gap** — New workflow patterns may emerge that aren't in the supported matrix. *Mitigation*: Pattern coverage assessment (§8) with explicit unsupported list and abort. Templates can be extended over time.

**RISK-012** (Low): **Output Directory Collision with Non-Portified Code** — Target directory may contain human-written code that resembles portified output. *Mitigation*: Check for `portify-summary.md` marker (§11.2). Never overwrite without marker.

## Dependency Inventory

1. **`superclaude.cli.pipeline.models`** — Provides `PipelineConfig`, `Step`, `StepResult`, `GateMode`, `SemanticCheck` base types. Generated code extends these. (§2.1, §9.1)

2. **`superclaude.cli.pipeline.gates`** — Provides `GateCriteria` dataclass and `gate_passed()` function. Generated gates must use, not reimplement, this module. (§2.1, §9.1)

3. **`superclaude.cli.main` (Click app)** — The CLI entry point where generated command groups are registered via `app.add_command()`. (§2.5)

4. **Python `ast` module** — Used for Phase 3 post-generation validation: syntax checking (`ast.parse`), import resolution, signature verification. (§2.4)

5. **Python `concurrent.futures.ThreadPoolExecutor`** — Mandated parallelism mechanism for generated executor modules. (§2.3)

6. **MCP Server: Auggie (codebase-retrieval)** — Used in Phase 0 and Phase 1 for component discovery and API reading. (§4)

7. **MCP Server: Serena** — Used in Phase 0 (API extraction), Phase 3 (symbol verification), Phase 4 (integration verification). (§4)

8. **MCP Server: Sequential** — Used in Phase 1 (classification conflicts) and Phase 2 (executor design). (§4)

9. **MCP Server: Context7** — Used in Phase 2 for external library API lookup if workflow references external libs. (§4)

## Success Criteria

**SC-001**: All 5 phases (0–4) either pass all blocking checks or halt with a resumable failure state with correct `failure_type` and `resume_command`. (§13)

**SC-002**: Same input workflow produces identical `source_step_registry`, `step_mapping`, and `module_plan` across repeated runs (determinism). (§13)

**SC-003**: All generated Python files pass `ast.parse()` without error. (§2.4)

**SC-004**: Generated import graph is acyclic — no circular imports detected. (§2.4)

**SC-005**: All `GateCriteria` field names in generated code match the live API snapshot captured in Phase 0. Zero mismatches. (§9)

**SC-006**: All `SemanticCheck` functions use `Callable[[str], bool]` signature, not `tuple[bool, str]`. (§2.3, §2.4)

**SC-007**: Step conservation invariant holds: `|source_step_registry| == |mapped_steps| + |elimination_records|` at Phase 1 and Phase 2. (§7)

**SC-008**: Generated module imports successfully in isolation without error. (§2.5)

**SC-009**: Click command group is accessible and command name matches expected registration after main.py patching. (§2.5)

**SC-010**: Return contract is emitted on every invocation — success, partial failure, and full failure. (§3)

**SC-011**: Unsupported patterns detected in Phase 0 produce a blocking abort before analysis effort is invested. (§2.1)

**SC-012**: Non-portified code is never overwritten — collision policy correctly identifies portification markers. (§11.2)

**SC-013**: All 23 TodoWrite subphase tasks are tracked and updated through execution. (§5)

**SC-014**: Golden fixture tests pass: simple sequential skill, batched audit skill, adversarial multi-agent skill, and intentionally unsupported skill (correctly aborts). (§16)

## Open Questions

**OQ-001**: **Phase 0 collision policy reference error** — §2.1 references "Section 5.3" for naming policy, but the document has no §5.3. The collision policy is actually in §11.2. Is this a spec typo, or is there missing content for §5.3?

**OQ-002**: **`TurnLedger` integration** — §2.3 mentions `TurnLedger` integration in model design, but this type is not mentioned in the API snapshot (§9.1) or anywhere else in the spec. Is `TurnLedger` part of the pipeline API? Where is it defined?

**OQ-003**: **`--dry-run` and `--skip-integration` behavior** — §10.1 lists these as command arguments but no behavioral specification is provided. What does `--dry-run` produce? Does `--skip-integration` skip only Phase 4 or also parts of Phase 3?

**OQ-004**: **Phase contract `portify-integration.yaml` schema** — Phase 4 mentions emitting this contract (§2.5) but no schema is provided, unlike Phases 0–3 which have explicit YAML schemas. What fields should this contract contain?

**OQ-005**: **Batch dynamic flag in parallel groups** — The Phase 1 contract includes `batch_dynamic: <true|false>` for parallel groups, but dynamic fan-out is listed as unsupported (§8.2). Under what conditions would `batch_dynamic: true` be valid?

**OQ-006**: **`refs/analysis-protocol.md` existence** — Phase 1 loads `refs/analysis-protocol.md` (§2.2) but the spec doesn't define its contents or confirm it exists. Is this a new file to create, or an existing reference?

**OQ-007**: **User approval gate mechanism** — Phases 1 and 2 require user approval (§2.2, §2.3). What is the technical mechanism? Is this a CLI prompt, a file-based gate, or TodoWrite-based? How does the protocol pause and resume across the approval boundary?

**OQ-008**: **`--output` default behavior** — If `--output` is not provided, where is the generated module placed? The spec doesn't define a default output directory.

**OQ-009**: **Structural test placement** — Phase 4 generates `test_<name>_structure.py` (§2.5) but doesn't specify the target directory. Should it go in `tests/` following project conventions, or alongside the generated module?

**OQ-010**: **Step boundary algorithm reference** — §2.2 says "Apply step boundary algorithm (unchanged from current spec)" but does not define it. Is this algorithm documented in the current `sc-cli-portify/SKILL.md` or its refs? If the current spec is being replaced, this algorithm needs explicit documentation.
