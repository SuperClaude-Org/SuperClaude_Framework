# Phase 4 -- Code Generation and Integration

Implement deterministic Python code generation producing 12 files with AST validation, per-file and cross-file verification, CLI integration via main.py patching, structural test generation, and name normalization with collision policy enforcement. This phase produces working, importable, CLI-accessible code.

---

### T04.01 -- Implement 12-File Code Generation in Dependency Order

| Field | Value |
|---|---|
| Roadmap Item IDs | R-069, R-070, R-071 |
| Why | The code generation engine is the core deliverable — it must produce all 12 Python files atomically in strict dependency order to prevent partial or broken output. |
| Effort | XL |
| Risk | High |
| Risk Drivers | data integrity (atomic generation, dependency order), breaking (halt on any failure), cross-cutting (12 files, all interconnected) |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | Yes (models/ path) |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0027/evidence.md

**Deliverables:**
- 12 generated Python files in strict dependency order: `models.py` → `gates.py` → `prompts.py` → `config.py` → `monitor.py` → `process.py` → `executor.py` → `tui.py` → `logging_.py` → `diagnostics.py` → `commands.py` → `__init__.py` (FR-034)
- Atomic generation semantics: halt entirely on any file failure, no partial output (FR-035)

**Subtasks (XL decomposition):**
1. Generate foundation files (models.py, gates.py, prompts.py) from portify-spec.yaml step mapping and model designs
2. Generate configuration and monitoring files (config.py, monitor.py) from domain model specifications
3. Generate execution files (process.py, executor.py, tui.py, logging_.py) from executor design
4. Generate integration files (diagnostics.py, commands.py, __init__.py) from module plan and export registry

**Steps:**
1. **[PLANNING]** Read portify-spec.yaml to extract step_mapping, module_plan, and gate_definitions
2. **[PLANNING]** Establish file generation order with dependency validation between files
3. **[EXECUTION]** Generate foundation files: models.py (domain dataclasses), gates.py (GateCriteria instances), prompts.py (prompt templates)
4. **[EXECUTION]** Generate configuration files: config.py (PipelineConfig extension), monitor.py (NDJSON monitoring)
5. **[EXECUTION]** Generate execution files: process.py (step processing), executor.py (ThreadPoolExecutor supervisor), tui.py (terminal UI), logging_.py (structured logging)
6. **[EXECUTION]** Generate integration files: diagnostics.py (health checks), commands.py (Click command group), __init__.py (module exports)
7. **[VERIFICATION]** Verify all 12 files generated; atomic semantics enforced (no partial output on failure)
8. **[COMPLETION]** Record file generation results and dependency order verification in D-0027/evidence.md

**Acceptance Criteria:**
- All 12 Python files generated in correct dependency order as specified in FR-034
- Atomic generation enforced: any single file generation failure halts entire process with no partial output written
- Each generated file contains valid Python (parseable by `ast.parse()`) before next file generation begins
- Generation order and file list documented in D-0027/evidence.md

**Validation:**
- `uv run python -c "import ast; [ast.parse(open(f).read()) for f in generated_files]"` exits 0 for all 12 files
- Evidence: linkable artifact produced at D-0027/evidence.md

**Dependencies:** T03.05 (portify-spec.yaml must be emitted and approved)
**Rollback:** Delete all generated files in output directory

---

### T04.02 -- Implement Per-File and Cross-File Validation Checks

| Field | Value |
|---|---|
| Roadmap Item IDs | R-072, R-073 |
| Why | Per-file validation catches individual file errors; cross-file validation catches integration errors like circular imports and missing exports. |
| Effort | L |
| Risk | High |
| Risk Drivers | data integrity (AST validation, import graph), cross-cutting (validation spans all 12 files) |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes (models/ path) |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0028/evidence.md

**Deliverables:**
- Per-file validation implementing 6 checks (5 blocking, 1 advisory) per FR-036: `ast.parse()` syntax validation, import path verification, base class contract checking (`PipelineConfig`, `StepResult`), `GateCriteria` field name matching against API snapshot, `SemanticCheck` signature verification (`Callable[[str], bool]`)
- Cross-file validation implementing 4 checks (all blocking) per FR-037: module completeness (all 12 files), circular import detection (import graph acyclicity), `__init__.py` export matching, step count matching against spec

**Steps:**
1. **[PLANNING]** Define per-file check specifications with blocking/advisory classification
2. **[PLANNING]** Define cross-file check specifications and import graph construction algorithm
3. **[EXECUTION]** Implement per-file checks: ast.parse(), import path verification, base class checking, GateCriteria field matching, SemanticCheck signature verification
4. **[EXECUTION]** Implement cross-file checks: module completeness (12 files present), import graph acyclicity via topological sort, __init__.py export matching, step count matching
5. **[EXECUTION]** Wire validation into code generation pipeline: per-file checks run after each file, cross-file checks run after all files generated
6. **[VERIFICATION]** Run validation suite against generated test workflow files — all 5 blocking per-file and 4 blocking cross-file checks pass
7. **[COMPLETION]** Record per-file and cross-file validation results in D-0028/evidence.md

**Acceptance Criteria:**
- All 5 blocking per-file checks pass for each of the 12 generated files
- All 4 blocking cross-file checks pass: 12 files present, no circular imports, exports match, step count matches spec
- `GateCriteria` field names in generated gates match api-snapshot.yaml exactly
- `SemanticCheck` functions in generated code use `Callable[[str], bool]` signature exclusively

**Validation:**
- `uv run python -c "ast.parse(open(f).read())"` succeeds for all 12 files
- Evidence: linkable artifact produced at D-0028/evidence.md

**Dependencies:** T04.01 (files must be generated before validation)
**Rollback:** Revert validation implementation (generated files unaffected)
**Notes:** Mitigates RISK-001 (API drift) and RISK-005 (circular imports). Validates SC-003, SC-004, SC-005, SC-006.

---

### T04.03 -- Confirm: T04.04 Tier Classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-074 |
| Why | Tier classification confidence for T04.04 (contract emission) is below threshold; confirm STANDARD tier is appropriate. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [██████████] 95% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | — |

**Deliverables:**
- Confirmed tier selection for T04.04

**Steps:**
1. **[PLANNING]** Review T04.04 scope: emit portify-codegen.yaml contract
2. **[EXECUTION]** Confirm or override STANDARD tier
3. **[COMPLETION]** Record confirmation

**Acceptance Criteria:**
- Tier decision recorded with justification
- T04.04 unblocked for execution
- Override reason documented if changed
- Decision captured in execution log

**Validation:**
- Manual check: tier confirmation recorded
- Evidence: decision captured in execution log

**Dependencies:** None
**Rollback:** N/A

---

### T04.04 -- Emit portify-codegen.yaml Contract

| Field | Value |
|---|---|
| Roadmap Item IDs | R-074 |
| Why | The codegen contract records code generation results for downstream integration and return contract aggregation. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0029/evidence.md

**Deliverables:**
- `portify-codegen.yaml` contract emitted with: generated file list, per-file validation results, cross-file validation results, api_snapshot_hash, step count (FR-038)

**Steps:**
1. **[PLANNING]** Define portify-codegen.yaml schema per contract definition from T02.02
2. **[EXECUTION]** Assemble codegen contract from T04.01 generation results and T04.02 validation results
3. **[EXECUTION]** Include api_snapshot_hash, file list, per-file and cross-file check results
4. **[VERIFICATION]** Validate emitted YAML against contract schema
5. **[COMPLETION]** Record contract emission verification in D-0029/evidence.md

**Acceptance Criteria:**
- `portify-codegen.yaml` exists and conforms to per-phase contract schema
- Contract includes complete file list of all 12 generated files
- All per-file and cross-file validation results recorded in contract
- api_snapshot_hash present and matches Phase 0 snapshot

**Validation:**
- Manual check: portify-codegen.yaml parseable as valid YAML with all required fields
- Evidence: linkable artifact produced at D-0029/evidence.md

**Dependencies:** T04.01, T04.02 (generation and validation must complete)
**Rollback:** Delete portify-codegen.yaml

---

### T04.05 -- Patch main.py and Run Integration Smoke Test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-075, R-076, R-077 |
| Why | CLI integration makes the generated pipeline accessible as a Click command; smoke test proves the integration works end-to-end. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking (patching main.py), data integrity (command registration) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0030/evidence.md

**Deliverables:**
- Patched `src/superclaude/cli/main.py` with import statement and `app.add_command()` call for generated pipeline (FR-039); aborts on naming collision
- Integration smoke test results (FR-040): module imports successfully, Click command group exists, command name matches registration

**Steps:**
1. **[PLANNING]** Read current `src/superclaude/cli/main.py` to identify insertion points for import and command registration
2. **[PLANNING]** Determine derived command name from T04.08 name normalization (or use --name argument)
3. **[EXECUTION]** Add import statement for generated module to main.py
4. **[EXECUTION]** Add `app.add_command()` call with generated command group; check for naming collision first
5. **[EXECUTION]** Run smoke test: verify module imports, Click command group exists, name matches registration
6. **[VERIFICATION]** All 3 smoke test assertions pass; no naming collision detected
7. **[COMPLETION]** Record patch diff and smoke test results in D-0030/evidence.md

**Acceptance Criteria:**
- `main.py` contains import statement for generated pipeline module
- `app.add_command()` registered with correct command name derived from --name or normalization
- Smoke test passes: module imports without error, Click command group accessible, name matches
- No naming collision with existing commands in main.py

**Validation:**
- `uv run python -c "from superclaude.cli.main import app; assert '<name>' in [c.name for c in app.commands.values()]"` exits 0
- Evidence: linkable artifact produced at D-0030/evidence.md

**Dependencies:** T04.01, T04.02 (generated files must pass validation before integration)
**Rollback:** `git checkout -- src/superclaude/cli/main.py`
**Notes:** Mitigates RISK-008 (name collision).

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.05

**Purpose:** Verify code generation, validation, and CLI integration before proceeding to structural tests and documentation.
**Checkpoint Report Path:** .dev/releases/current/v2.18-cli-portify-v2/checkpoints/CP-P04-T01-T05.md
**Verification:**
- All 12 Python files generated and pass AST validation
- No circular imports detected in import graph
- Smoke test passes: module imports, command registered, name matches
**Exit Criteria:**
- portify-codegen.yaml emitted with all validation results
- main.py patched and functional with generated command
- Atomic generation semantics verified (partial failure halts completely)

---

### T04.06 -- Confirm: T04.07 Tier Classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-078, R-079, R-080 |
| Why | Tier classification confidence for T04.07 (structural tests and summary) is below threshold; confirm STANDARD tier. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [██████████] 95% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | — |

**Deliverables:**
- Confirmed tier selection for T04.07

**Steps:**
1. **[PLANNING]** Review T04.07 scope: structural test file, summary, integration contract
2. **[EXECUTION]** Confirm or override STANDARD tier
3. **[COMPLETION]** Record confirmation

**Acceptance Criteria:**
- Tier decision recorded with justification
- T04.07 unblocked for execution
- Override reason documented if changed
- Decision captured in execution log

**Validation:**
- Manual check: tier confirmation recorded
- Evidence: decision captured in execution log

**Dependencies:** None
**Rollback:** N/A

---

### T04.07 -- Generate Structural Test File, portify-summary.md, and Integration Contract

| Field | Value |
|---|---|
| Roadmap Item IDs | R-078, R-079, R-080 |
| Why | Structural tests validate the generated pipeline architecture; summary provides documentation; integration contract completes Phase 4 output chain. |
| Effort | M |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0031/spec.md

**Deliverables:**
- Generated structural test file `tests/test_<name>_structure.py` testing: step graph completeness, gate definitions, model consistency, command registration (FR-041)
- `portify-summary.md` containing: file inventory, CLI usage, step graph visualization, known limitations, resume command template (FR-042)
- `portify-integration.yaml` contract with: main_py_patched, command_registered, test_file_generated, smoke_test_passed

**Steps:**
1. **[PLANNING]** Define structural test assertions from generated pipeline: step count, gate count, model fields, command name
2. **[PLANNING]** Define portify-summary.md sections and portify-integration.yaml fields
3. **[EXECUTION]** Generate `tests/test_<name>_structure.py` with structural assertions for step graph, gates, models, and command
4. **[EXECUTION]** Write `portify-summary.md` with file inventory, CLI usage instructions, step graph, limitations, and resume template
5. **[EXECUTION]** Emit `portify-integration.yaml` contract with all OQ-004 fields
6. **[VERIFICATION]** Run structural test: `uv run pytest tests/test_<name>_structure.py` exits 0
7. **[COMPLETION]** Record test results and summary content in D-0031/spec.md

**Acceptance Criteria:**
- `tests/test_<name>_structure.py` exists in `tests/` directory and passes when run with pytest
- `portify-summary.md` exists and contains all 5 required sections (inventory, usage, graph, limitations, resume)
- `portify-integration.yaml` contains all 4 OQ-004 fields (main_py_patched, command_registered, test_file_generated, smoke_test_passed)
- Structural test verifies step graph completeness and command registration

**Validation:**
- `uv run pytest tests/test_<name>_structure.py -v` exits 0
- Evidence: linkable artifact produced at D-0031/spec.md

**Dependencies:** T04.05 (CLI integration must be complete before structural tests)
**Rollback:** Delete generated test file, summary, and integration contract

---

### T04.08 -- Implement Name Normalization and Collision Policy Enforcement

| Field | Value |
|---|---|
| Roadmap Item IDs | R-081, R-082, R-083 |
| Why | Consistent naming conventions across kebab-case, snake_case, PascalCase, and UPPER_SNAKE prevent naming errors; collision policy prevents accidental code overwrites. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking (collision policy prevents overwrites), data integrity (naming consistency) |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0032/evidence.md

**Deliverables:**
- Name normalization engine: derives kebab-case (CLI), snake_case (Python), PascalCase (classes), UPPER_SNAKE (config) from input name; strips `sc-` prefix and `-protocol` suffix (FR-046)
- Collision policy enforcement: checks `portify-summary.md` marker for prior portification; never overwrites non-portified code (FR-047, NFR-013)

**Steps:**
1. **[PLANNING]** Define normalization rules: input name → 4 case variants; prefix/suffix stripping rules
2. **[PLANNING]** Define collision detection logic: portify-summary.md marker presence/absence → action
3. **[EXECUTION]** Implement normalization: input "sc-cli-portify-protocol" → "cli-portify" (stripped) → kebab: "cli-portify", snake: "cli_portify", pascal: "CliPortify", upper: "CLI_PORTIFY"
4. **[EXECUTION]** Implement collision policy: detect marker → overwrite if portified (with confirmation), abort if non-portified, abort on main.py name collision
5. **[VERIFICATION]** Test normalization with edge cases; test collision policy with portified and non-portified directories
6. **[COMPLETION]** Record normalization examples and collision test results in D-0032/evidence.md

**Acceptance Criteria:**
- Normalization produces correct 4-case variants: kebab, snake, PascalCase, UPPER_SNAKE for test inputs
- `sc-` prefix and `-protocol` suffix correctly stripped before case conversion
- Collision policy correctly distinguishes portified (marker present) from non-portified (no marker) directories
- Non-portified code at output path causes abort, never overwrite (NFR-013 verified)

**Validation:**
- Manual check: normalization of "sc-cli-portify-protocol" produces "cli-portify", "cli_portify", "CliPortify", "CLI_PORTIFY"
- Evidence: linkable artifact produced at D-0032/evidence.md

**Dependencies:** None (normalization engine is self-contained; used by T04.01 and T04.05)
**Rollback:** Revert normalization and collision policy implementations
**Notes:** Mitigates RISK-008 (name collision) and RISK-012 (non-portified collision). Validates SC-012.

---

### Checkpoint: End of Phase 4

**Purpose:** Gate Phase 5 (validation and cleanup) entry by confirming code generation, integration, and naming are complete and functional.
**Checkpoint Report Path:** .dev/releases/current/v2.18-cli-portify-v2/checkpoints/CP-P04-END.md
**Verification:**
- Generated module passes all AST checks and has no circular imports
- main.py patching succeeds and smoke test passes
- Structural test file generated and passes with pytest
**Exit Criteria:**
- Return contract emittable with all fields populated from Phase 0-4 results
- Name normalization produces correct 4-case variants for test inputs
- Collision policy correctly prevents overwriting non-portified code
