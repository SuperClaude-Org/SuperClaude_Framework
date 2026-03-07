Now I have the full spec. Let me produce the extraction document.

---
functional_requirements: 87
complexity_score: 0.92
complexity_class: enterprise
---

## 1. Functional Requirements

### Architecture & Migration (FR-001 to FR-008)

1. **FR-001**: Split current monolithic skill into thin command shim (`commands/cli-portify.md`) and full protocol skill (`skills/sc-cli-portify-protocol/SKILL.md`) following the tasklist pattern. (§1.1)
2. **FR-002**: Migrate current `sc-cli-portify/SKILL.md` to `sc-cli-portify-protocol/SKILL.md` and move `refs/` into the protocol directory. (§1.1)
3. **FR-003**: Create new command shim with input validation and `Skill sc:cli-portify-protocol` invocation. (§1.1)
4. **FR-004**: Deprecate and remove old `sc-cli-portify/` directory after migration. (§1.1)
5. **FR-005**: Promote commented metadata into real YAML frontmatter fields with specified schema (name, description, category, complexity, allowed-tools, mcp-servers, personas, argument-hint). (§1.2)
6. **FR-006**: Both `src/` and `.claude/` copies must include `__init__.py`. (§1.3)
7. **FR-007**: `make verify-sync` must cover the protocol directory. (§1.3)
8. **FR-008**: Command shim must parse arguments: `--workflow`, `--name`, `--output`, `--dry-run`, `--skip-integration`. (§10.1)

### Phase Contract Model (FR-009 to FR-014)

9. **FR-009**: Every phase must emit two artifacts: a human review document (`.md`) and a machine-readable contract (`.yaml`). (§2.0)
10. **FR-010**: Each `.yaml` contract must include the unified header fields: `phase`, `status`, `timestamp`, `resume_checkpoint`, and `validation_status` block. (§2.0)
11. **FR-011**: Next phase's entry criteria must validate the incoming contract before proceeding. (§2.0)
12. **FR-012**: Return contract must be emitted on every invocation including failures. (§3)
13. **FR-013**: Return contract must include all specified fields: `output_directory`, `status`, `failure_phase`, `failure_type`, `generated_files`, `source_step_count`, `generated_step_count`, `elimination_count`, `api_snapshot_hash`, `resume_command`, `resume_phase`, `warnings`, `phase_contracts`. (§3)
14. **FR-014**: On pipeline abort, return contract must set `status: "failed"`, `failure_phase` to the failing phase, and unreached fields to `null`. (§3)

### Phase 0: Prerequisites (FR-015 to FR-024)

15. **FR-015**: Resolve workflow path — locate command `.md`, skill `SKILL.md`, all refs/rules/templates/scripts. (§2.1)
16. **FR-016**: If path resolves to multiple candidates, abort with disambiguation error. (§2.1)
17. **FR-017**: Snapshot live pipeline API from `models.py` and `gates.py`, extracting `SemanticCheck`, `GateCriteria`, `gate_passed()`, `PipelineConfig`, `Step`, `StepResult`, `GateMode` signatures. (§2.1)
18. **FR-018**: Store API snapshot as `api-snapshot.yaml`. (§2.1)
19. **FR-019**: Check output collision — if target directory exists, apply naming policy per §11. (§2.1)
20. **FR-020**: Perform early unsupported-pattern scan detecting: recursive self-orchestration, interactive mid-pipeline decisions, no stable artifact boundaries, dynamic code eval. (§2.1)
21. **FR-021**: Emit blocking warning on unsupported pattern detection before investing analysis effort. (§2.1)
22. **FR-022**: Emit `portify-prerequisites.yaml` contract with specified fields. (§2.1)
23. **FR-023**: Any prerequisite failure must abort with error code and corrective action, no partial output. (§2.1)
24. **FR-024**: Mark Phase 0 complete via TodoWrite on success. (§2.1)

### Phase 1: Workflow Analysis (FR-025 to FR-042)

25. **FR-025**: Build component inventory with paths, line counts, purposes; assign stable `component_id` (C-NNN). (§2.2)
26. **FR-026**: Decompose workflow into steps using step boundary algorithm; assign stable `source_id` (S-NNN). (§2.2)
27. **FR-027**: Enforce conservation invariant: every source operation maps to exactly one source_id; no source_id created without tracing to a specific location. (§2.2)
28. **FR-028**: Classify each step as pure programmatic, Claude-assisted, or hybrid with confidence score (0.0-1.0). (§2.2)
29. **FR-029**: If classification confidence < 0.7, flag for user review with justification. (§2.2)
30. **FR-030**: Provide evidence (specific lines/patterns) supporting each classification. (§2.2)
31. **FR-031**: Map dependencies as a DAG with data flow edges and validate acyclicity. (§2.2)
32. **FR-032**: Extract and assign gate tier + mode for each step output. (§2.2)
33. **FR-033**: Check trailing gate safety — escalate to BLOCKING if downstream step consumes TRAILING gate output as prompt context. (§2.2)
34. **FR-034**: Self-validation check 1: every workflow behavioral instruction has ≥1 source_id (blocking). (§2.2)
35. **FR-035**: Self-validation check 2: every source_id has exactly one classification (blocking). (§2.2)
36. **FR-036**: Self-validation check 3: classification confidence ≥ 0.7 for all steps, or user-reviewed (blocking). (§2.2)
37. **FR-037**: Self-validation check 4: dependency graph is acyclic (blocking). (§2.2)
38. **FR-038**: Self-validation check 5: every step with downstream consumers has BLOCKING gate (blocking). (§2.2)
39. **FR-039**: Self-validation check 6: no orphan source_ids (blocking). (§2.2)
40. **FR-040**: Self-validation check 7: component inventory covers all files in skill directory (advisory). (§2.2)
41. **FR-041**: Emit `portify-analysis.md` (under 400 lines) and `portify-analysis.yaml` with specified schema. (§2.2)
42. **FR-042**: Present analysis to user for review; user may override classifications or flag missing steps. (§2.2)

### Phase 2: Pipeline Specification (FR-043 to FR-060)

43. **FR-043**: Map each source_id to generated step(s) recording 1:1, 1:N, N:1, or 1:0 mappings with justifications. (§2.3)
44. **FR-044**: Enforce coverage invariant: `source_step_registry count == mapped steps + elimination_records`. (§2.3)
45. **FR-045**: Design domain-specific dataclass models conforming to live API snapshot (Config extending PipelineConfig, Result extending StepResult, Status enum, Monitor state, TurnLedger integration). (§2.3)
46. **FR-046**: Design prompts for each Claude-assisted step specifying: input strategy, output sections, frontmatter fields, markers, structural requirements. (§2.3)
47. **FR-047**: If prompts collectively exceed 300 lines, split to separate `portify-prompts.md` file (strict `>` comparator). (§2.3)
48. **FR-048**: Design gates using live `GateCriteria` field names from API snapshot. (§2.3)
49. **FR-049**: Semantic check functions must use `Callable[[str], bool]` signature. (§2.3)
50. **FR-050**: Implement pure-programmatic steps as full Python code, not descriptions. (§2.3)
51. **FR-051**: Design executor as sprint-style synchronous supervisor with ThreadPoolExecutor for batch parallelism. (§2.3)
52. **FR-052**: Assess pattern coverage by building coverage matrix against `refs/code-templates.md`. (§2.3)
53. **FR-053**: If any step requires an unsupported pattern, perform blocking abort before code generation. (§2.3)
54. **FR-054**: Plan CLI integration: Click command group, main.py import, naming. (§2.3)
55. **FR-055**: Phase 2 self-validation: 7 blocking checks + 1 advisory check as specified. (§2.3)
56. **FR-056**: Emit `portify-spec.md`, optional `portify-prompts.md`, and `portify-spec.yaml` with specified schema. (§2.3)
57. **FR-057**: Present spec to user for approval before Phase 3. (§2.3)
58. **FR-058**: API conformance check: snapshot hash, all fields valid, mismatch list. (§2.3)
59. **FR-059**: Coverage invariant failure lists unmapped source_ids and is resumable. (§2.3)
60. **FR-060**: API conformance failure lists mismatches with live vs spec values. (§2.3)

### Phase 3: Code Generation (FR-061 to FR-074)

61. **FR-061**: Generate files in dependency order: models → gates → prompts → config → monitor → process → executor → tui → logging_ → diagnostics → commands → `__init__.py`. (§2.4)
62. **FR-062**: Each generated file must import from `superclaude.cli.pipeline` for shared base types. (§2.4)
63. **FR-063**: Atomic generation: if any file fails mid-generation, halt and record failure (do not proceed). (§2.4)
64. **FR-064**: Per-file check 1: Python syntax valid via `ast.parse(source)` (blocking). (§2.4)
65. **FR-065**: Per-file check 2: no undefined names in imports (blocking). (§2.4)
66. **FR-066**: Per-file check 3: base class contracts satisfied (blocking). (§2.4)
67. **FR-067**: Per-file check 4: `GateCriteria` field names match snapshot (blocking). (§2.4)
68. **FR-068**: Per-file check 5: `SemanticCheck` signature correct (blocking). (§2.4)
69. **FR-069**: Per-file check 6: `gate_passed()` not re-implemented, imported from pipeline.gates (advisory). (§2.4)
70. **FR-070**: Cross-file check 7: all planned modules from Phase 2 emitted (blocking). (§2.4)
71. **FR-071**: Cross-file check 8: no circular imports (blocking). (§2.4)
72. **FR-072**: Cross-file check 9: `__init__.py` exports match commands.py expectations (blocking). (§2.4)
73. **FR-073**: Cross-file check 10: step count matches Phase 2 step_mapping (blocking). (§2.4)
74. **FR-074**: Emit `portify-codegen.yaml` contract with per-file and cross-file validation results. (§2.4)

### Phase 4: Integration & Validation (FR-075 to FR-085)

75. **FR-075**: Patch `main.py` with import and `app.add_command()`. (§2.5)
76. **FR-076**: Collision check: if command name already exists in main.py, abort with naming conflict error. (§2.5)
77. **FR-077**: Apply naming rules: kebab-case for CLI, snake_case for Python module, PascalCase for classes. (§2.5)
78. **FR-078**: Run integration smoke test: module imports without error, Click command group exists, command name matches. (§2.5)
79. **FR-079**: Generate structural test (`test_<name>_structure.py`) validating step graph completeness, gate definitions, model consistency, command registration. (§2.5)
80. **FR-080**: Write `portify-summary.md` with file inventory, CLI usage, step graph, known limitations, resume command template. (§2.5)
81. **FR-081**: Post-write check 1: main.py patch applies cleanly (blocking). (§2.5)
82. **FR-082**: Post-write check 2: generated module imports successfully (blocking). (§2.5)
83. **FR-083**: Post-write check 3: Click command group accessible (blocking). (§2.5)
84. **FR-084**: Post-write check 4: structural test file syntactically valid (blocking). (§2.5)
85. **FR-085**: Emit `portify-integration.yaml` contract. (§2.5)

### Input Validation & Error Handling (FR-086 to FR-087)

86. **FR-086**: Command shim must validate inputs and emit structured error codes: MISSING_WORKFLOW, INVALID_PATH, AMBIGUOUS_PATH, OUTPUT_NOT_WRITABLE, NAME_COLLISION, DERIVATION_FAILED. (§10.2)
87. **FR-087**: Classify the command as STRICT compliance tier (multi-file code generation with pipeline API dependencies). (§10.1)

---

## 2. Non-Functional Requirements

1. **NFR-001**: Determinism — same inputs must produce same `source_step_registry`, same `step_mapping`, and same `module_plan`. (§13)
2. **NFR-002**: Completeness — all required phases either pass blocking checks or halt with a resumable failure state. (§13)
3. **NFR-003**: Scope limitation — only workflows whose patterns are covered by the pattern coverage matrix (§8). (§13, §14)
4. **NFR-004**: MCP graceful degradation — if an MCP server is unavailable, phase may proceed with native tools but must log degradation in `advisory_warnings`. (§4)
5. **NFR-005**: Progress visibility — TodoWrite integration at phase and subphase level with 23 tracked subtasks. (§5)
6. **NFR-006**: Checkpoint triggers must fire after each phase completion, after user review gates, before any write operation, and on any failure. (§5.2)
7. **NFR-007**: Resumability — every failure state must be resumable from the failed phase via `resume_command` in the return contract. (§6.2)
8. **NFR-008**: Human-readable analysis output must be under 400 lines. (§2.2)
9. **NFR-009**: Non-destructive — never overwrite non-portified code; never modify original skill/command/agent files. (§11.2, §14)
10. **NFR-010**: Boundary respect — will not execute generated pipelines, create new skills/agents, generate code for unsupported patterns, or generate LLM content quality tests. (§14)
11. **NFR-011**: Ref file currency — ref files must be audited and updated against live API before protocol use. (§12)
12. **NFR-012**: Convention alignment — follow peer patterns from sc:tasklist-protocol, sc:roadmap-protocol, sc:adversarial-protocol. (§1.1)
13. **NFR-013**: Name normalization conventions must be consistently applied: kebab-case (CLI), snake_case (Python), PascalCase (classes), UPPER_SNAKE (config). (§11.1)
14. **NFR-014**: API drift detection — if ref files reference field names/signatures not matching live API snapshot, emit blocking warning. (§9.3)

---

## 3. Complexity Assessment

**Score: 0.92 / 1.0** — **Enterprise-class complexity**

**Justification**:

- **Phase count**: 5 distinct phases (0-4) with strict entry/exit criteria and machine-readable contracts between each
- **Validation depth**: 34 distinct validation checks across phases (28 blocking, 6 advisory), each with specified method and blocking behavior
- **Multi-layer contracts**: Phase contracts, return contracts, API snapshots, elimination records — 4+ contract types with interdependencies
- **Live API verification**: Runtime extraction and hashing of pipeline API signatures with drift detection across 3 phases
- **Conservation invariant**: Mathematical equality constraint (`|source_step_registry| == |mapped_steps| + |elimination_records|`) enforced across phases
- **Pattern coverage matrix**: 7 supported + 5 unsupported patterns with detection logic and abort triggers
- **Failure taxonomy**: 9 distinct failure types with per-type remediation paths and resume semantics
- **MCP orchestration**: 4 MCP servers mapped across phases with degradation logging
- **Code generation**: 12+ Python modules generated in dependency order with per-file AST validation and cross-file circular import detection
- **Cross-cutting concerns**: Naming normalization, collision detection, sync verification, progress tracking all interact across phases

---

## 4. Key Architectural Constraints

1. **Contract-driven phase boundaries**: Phases communicate exclusively via typed YAML contracts with stable schemas. No prose reinterpretation between phases. (§2.0)
2. **Live API as single source of truth**: All generated code must conform to the live `models.py` and `gates.py` signatures captured in Phase 0, not to ref file descriptions. (§9)
3. **Dependency-ordered generation**: Files must be generated in the specified order (models → ... → `__init__.py`) to ensure import resolution. (§2.4)
4. **Atomic generation**: Failure in any file halts the entire generation pipeline — no partial module output. (§2.4)
5. **Step conservation invariant**: Every source operation must be accounted for — either mapped to a generated step or explicitly eliminated with a record. (§7)
6. **Command/protocol separation**: Thin command shim handles validation only; full logic resides in the protocol skill. (§1.1)
7. **Supported pattern gate**: Code generation is blocked if any step requires an unsupported pattern — full analysis must complete first, then abort before Phase 2. (§8.3)
8. **User approval gates**: Phase 1 output requires user review, Phase 2 requires user approval — pipeline cannot auto-advance through these gates. (§2.2, §2.3)
9. **Import from shared pipeline**: Generated code must extend base types from `superclaude.cli.pipeline`, not redefine them. (§2.4)
10. **Collision safety**: Never overwrite human-written code; only previously-portified directories may be overwritten with user consent. (§11.2)

---

## 5. Open Questions & Ambiguities

1. **§2.1 references §5.3 for collision policy** but §5.3 does not exist — the actual collision policy is in §11.2. Likely a section numbering error from an earlier draft.
2. **TurnLedger integration** (§2.3 item 2) is mentioned as a model requirement but its interface/contract is not specified anywhere in this document. What fields and behavior does TurnLedger provide?
3. **`portify-integration.yaml`** (§2.5) is mentioned as an output artifact but its schema is never defined, unlike all other phase contracts which have explicit YAML schemas.
4. **`--dry-run` and `--skip-integration` flags** (§10.1) are listed as command arguments but their behavioral effects are not specified. What does dry-run produce? Does skip-integration stop after Phase 3?
5. **Step boundary algorithm** (§2.2 item 2) is described as "unchanged from current spec" but the current algorithm is not included or referenced by specific path. What defines a step boundary?
6. **NDJSON signals** (§2.3 item 2) for monitor state are mentioned without schema specification. What events are signaled and in what format?
7. **`refs/analysis-protocol.md`** and **`refs/code-templates.md`** are referenced as loaded during phases but their expected contents/schemas are not specified in this document.
8. **Batch dynamic flag** (`batch_dynamic: true|false` in §2.2 parallel groups) — the semantics of dynamic batching are not defined. How does it differ from static fan-out?
9. **Resume across sessions**: §6.2 describes resume semantics but does not specify whether contracts must be persisted to disk or if they are session-scoped. If the LLM session ends, can a new session resume?
10. **Phase 2 "optional_included" and "optional_excluded" modules** (§2.3 contract) — the criteria for including/excluding optional modules is not specified.
11. **User approval mechanism**: The spec says "present to user for review" (§2.2) and "present to user for approval" (§2.3) but does not specify the interaction pattern — is this a blocking prompt, a file write awaiting confirmation, or something else?
12. **Overwrite collision policy value "suffix"** appears in the Phase 0 contract (`collision_policy_applied: <none|suffix|overwrite>`) but only "overwrite or abort" is described in §11.2. What does the "suffix" policy do?
