# Phase 3 -- Validation, Artifacts & Compatibility Proof

Full test coverage, artifact enrichment, and backward-compatibility proof. This phase adds validation checks to `validate_config.py`, enriches the `component-inventory.md` artifact, and runs comprehensive test streams (unit, integration, regression, non-functional) to prove the release is complete.

---

### T03.01 -- Add Validation Checks 5 and 6 to validate_config.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-038, R-039 |
| Why | Encode system invariants for command-skill link validity and agent existence into the validation pipeline |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0032, D-0033 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0032/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0033/evidence.md

**Deliverables:**
1. Validation check 5 in `validate_config.py`: command-to-skill link validity -- verify that if `command_path` is set, the linked skill directory exists (or warn)
2. Validation check 6 in `validate_config.py`: referenced agent existence -- verify each agent in `ComponentTree.agents` has `found=True` (or warn with `WARN_MISSING_AGENTS`)

**Steps:**
1. **[PLANNING]** Read existing `validate_config.py` to understand the validation check pattern (checks 1-4)
2. **[PLANNING]** Design checks 5 and 6 to follow the same pattern: check condition, add warning/error to result
3. **[EXECUTION]** Add check 5: if `config.command_path` is set and `config.skill_dir` is None, add `ERR_BROKEN_ACTIVATION` to validation result
4. **[EXECUTION]** Add check 6: iterate `config.component_tree.agents`, for each with `found=False` add `WARN_MISSING_AGENTS` warning to result
5. **[VERIFICATION]** Write tests for both checks in `tests/cli_portify/test_validate.py` (valid, broken link, missing agent scenarios)
6. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/ -v` to confirm all tests pass
7. **[COMPLETION]** Record evidence of check behavior

**Acceptance Criteria:**
- Check 5 detects broken command-skill link and produces `ERR_BROKEN_ACTIVATION` in validation result
- Check 6 detects missing agents and produces `WARN_MISSING_AGENTS` warning per missing agent
- Both checks are additive -- existing checks 1-4 remain unchanged and unaffected
- `uv run pytest tests/cli_portify/test_validate.py -v` exits 0 with all tests passing

**Validation:**
- `uv run pytest tests/cli_portify/test_validate.py -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0032/evidence.md`

**Dependencies:** T02.06 (needs ValidateConfigResult with new fields)
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/validate_config.py`
**Notes:** Validation encodes system invariants, not only user messaging per architect focus.

---

### T03.02 -- Extend to_dict() with All New Fields

| Field | Value |
|---|---|
| Roadmap Item IDs | R-040 |
| Why | Ensure downstream contract/resume telemetry has complete data by including all new fields in serialized output |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0034/evidence.md

**Deliverables:**
1. Extended `to_dict()` on `ValidateConfigResult` including `warnings`, `command_path`, `skill_dir`, `target_type`, and `agent_count` fields

**Steps:**
1. **[PLANNING]** Read existing `to_dict()` implementation on `ValidateConfigResult`
2. **[PLANNING]** Identify all new fields that need serialization
3. **[EXECUTION]** Add `warnings`, `command_path`, `skill_dir`, `target_type`, `agent_count` to `to_dict()` return value
4. **[EXECUTION]** Handle `Path` objects by converting to `str` in the dict output
5. **[VERIFICATION]** Write round-trip test: construct result, call `to_dict()`, verify all fields present with correct types
6. **[COMPLETION]** Record evidence of serialization completeness

**Acceptance Criteria:**
- `to_dict()` output contains keys: `warnings`, `command_path`, `skill_dir`, `target_type`, `agent_count`
- All `Path` values are serialized as `str` in dict output (no `Path` objects in serialized form)
- Round-trip test in `tests/cli_portify/test_validate.py` confirms all fields present
- `uv run pytest tests/cli_portify/test_validate.py -v` exits 0 with all tests passing

**Validation:**
- `uv run pytest tests/cli_portify/test_validate.py -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0034/evidence.md`

**Dependencies:** T03.01
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/validate_config.py`
**Notes:** Completeness is mandatory per spec -- incomplete serialization would cause downstream contract/resume telemetry to lose data silently. Missing fields must be treated as a contract violation, not best-effort.

---

### T03.03 -- Enrich component-inventory.md Artifact

| Field | Value |
|---|---|
| Roadmap Item IDs | R-041 |
| Why | Provide richer artifact output with command section, agents table, cross-tier data flow, and resolution log |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0035 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0035/evidence.md

**Deliverables:**
1. Enriched `component-inventory.md` generation with: Command section, Agents table, Cross-Tier Data Flow section, Resolution Log section, and explicit frontmatter fields (`source_command`, `source_skill`, `component_count`, `total_lines`, `agent_count`, `has_command`, `has_skill`, `duration_seconds`)

**Steps:**
1. **[PLANNING]** Read existing `component-inventory.md` generation logic to understand current output format
2. **[PLANNING]** Map new sections to data sources: Command section from `ComponentTree.command`, Agents table from `ComponentTree.agents`, etc.
3. **[EXECUTION]** Add YAML frontmatter generation with all spec-required fields
4. **[EXECUTION]** Add Command section rendering from `CommandEntry` data
5. **[EXECUTION]** Add Agents table rendering from `list[AgentEntry]` with name, source, found status
6. **[EXECUTION]** Add Cross-Tier Data Flow section showing command -> skill -> agents relationships
7. **[EXECUTION]** Add Resolution Log section rendering from `resolution_log` data
8. **[VERIFICATION]** Write test validating enriched artifact contains all required sections and frontmatter keys
9. **[COMPLETION]** Record evidence of artifact enrichment

**Acceptance Criteria:**
- Generated `component-inventory.md` contains YAML frontmatter with all 8 spec-required keys
- Command section present when `ComponentTree.command` is not None
- Agents table lists all discovered agents with name, source directory, and found status
- `uv run pytest tests/cli_portify/ -v` exits 0 with all existing and new tests passing

**Validation:**
- `uv run pytest tests/cli_portify/ -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0035/evidence.md`

**Dependencies:** T02.01 (needs ComponentTree builder), T03.01 (needs validation enrichment for consistent output)
**Rollback:** TBD (artifact generation code location dependent on implementation)

---

### T03.04 -- Write Stream A Unit Tests (Resolver, Models, Regex, Consolidation)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-042 |
| Why | Comprehensive unit validation across all new modules to ensure correctness at the function level |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0036 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0036/evidence.md

**Deliverables:**
1. Stream A unit test suite covering: resolver tests for all 6 input forms and all failure modes; model conversion and round-trip tests; regex extraction tests (all 6 agent patterns); directory consolidation tests (both tiers)

**Steps:**
1. **[PLANNING]** Inventory existing tests from T01.06, T01.09, T02.01 to identify gaps in Stream A coverage
2. **[PLANNING]** Create test matrix: 6 input forms x (success + failure), 4 error codes, 5 model types, 6 regex patterns, 2 consolidation tiers
3. **[EXECUTION]** Fill any gaps in resolver tests (ensure all 6 forms have dedicated parametrized test cases)
4. **[EXECUTION]** Fill any gaps in model conversion tests (ensure round-trip fidelity for all model types)
5. **[EXECUTION]** Fill any gaps in regex tests (ensure each of 6 AGENT_PATTERNS has a dedicated test with synthetic input)
6. **[EXECUTION]** Fill any gaps in consolidation tests (ensure both Tier 1 and Tier 2 paths exercised)
7. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/ -v --tb=short` and confirm all Stream A tests pass
8. **[COMPLETION]** Record test count and coverage evidence

**Acceptance Criteria:**
- All 6 input forms have dedicated resolver tests with success and failure cases
- All 4 error codes have dedicated tests verifying exact error code values
- All 6 AGENT_PATTERNS have dedicated regex tests with synthetic SKILL.md content
- `uv run pytest tests/cli_portify/ -v` exits 0 with all Stream A tests passing

**Validation:**
- `uv run pytest tests/cli_portify/ -v --tb=short`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0036/evidence.md`

**Dependencies:** T01.09, T02.01, T02.03 (builds on tests from those tasks)
**Rollback:** TBD (test files only)

---

### Checkpoint: Phase 3 / Tasks T03.01-T03.04

**Purpose:** Verify validation checks, artifact enrichment, and unit test coverage are complete before integration and regression testing.

**Checkpoint Report Path:** .dev/releases/current/v2.24.1-cli-portify-cli-v5/checkpoints/CP-P03-T01-T04.md

**Verification:**
- Validation checks 5 and 6 correctly detect broken links and missing agents
- Enriched `component-inventory.md` contains all spec-required sections and frontmatter
- Stream A unit tests achieve full coverage of resolver, models, regex, and consolidation

**Exit Criteria:**
- All validation checks (1-6) functional
- `to_dict()` serialization complete with all new fields
- All Stream A unit tests passing

---

### T03.05 -- Write Stream B Integration Tests (CLI, Validation, Manifest, Process)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-043 |
| Why | Validate end-to-end integration of new features through CLI invocation |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0037 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0037/evidence.md

**Deliverables:**
1. Stream B integration test suite covering: CLI invocation tests with new and legacy inputs; validation result shape tests; manifest and inventory artifact tests; process invocation tests with and without `additional_dirs`

**Steps:**
1. **[PLANNING]** Design integration test scenarios: new TARGET forms, legacy WORKFLOW_PATH forms, option combinations
2. **[PLANNING]** Identify fixture requirements: temporary directories with command/skill/agent files
3. **[EXECUTION]** Write CLI invocation tests using Click's `CliRunner` for: bare name, prefixed name, command path, skill dir, skill name, SKILL.md path
4. **[EXECUTION]** Write validation result shape tests verifying all new fields appear in `ValidateConfigResult`
5. **[EXECUTION]** Write manifest artifact test verifying `--save-manifest` produces readable Markdown file
6. **[EXECUTION]** Write process invocation tests with `additional_dirs=None` and `additional_dirs=[list]`
7. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/ -v --tb=short` and confirm all Stream B tests pass
8. **[COMPLETION]** Record test count and integration coverage evidence

**Acceptance Criteria:**
- CLI invocation tests cover all 6 input forms via Click's `CliRunner`
- Validation result tests confirm `command_path`, `skill_dir`, `target_type`, `agent_count`, `warnings` fields present
- Manifest test confirms `--save-manifest` writes valid Markdown file
- `uv run pytest tests/cli_portify/ -v` exits 0 with all Stream B tests passing

**Validation:**
- `uv run pytest tests/cli_portify/ -v --tb=short`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0037/evidence.md`

**Dependencies:** T02.05, T02.06, T03.01 (needs full CLI + config + validation pipeline)
**Rollback:** TBD (test files only)
**Notes:** Stream B tests must also exercise success criteria SC-8 (missing agents warn, don't fail), SC-9 (to_flat_inventory() equivalence), and SC-11 (additional_dirs=None preserves v2.24) to ensure integration-level coverage of these cross-cutting requirements.

---

### T03.06 -- Run Stream C Regression and Stream D Non-Functional Verification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-044 |
| Why | Prove backward compatibility and non-functional requirements are satisfied |
| Effort | M |
| Risk | Medium |
| Risk Drivers | backward-compatibility proof, cross-cutting system-wide verification |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0038 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0038/evidence.md

**Deliverables:**
1. Stream C regression proof: existing test suite passes unchanged, old skill-directory flows match prior behavior, no `pipeline/`/`sprint/` changes
2. Stream D non-functional verification: resolution timing <1s, no `async def`/`await` in new code, no `pipeline/`/`sprint/` modifications, directory cap respected with deterministic selection logged in `resolution_log`

**Steps:**
1. **[PLANNING]** Identify the full existing test suite to run for regression (all tests that existed before v2.24.1 changes)
2. **[PLANNING]** List all non-functional verification commands from the roadmap
3. **[EXECUTION]** Run `uv run pytest` (full suite) and verify zero failures in pre-existing tests
4. **[EXECUTION]** Run `grep -r "async def\|await" src/superclaude/cli/cli_portify/` and verify empty output (NFR-003)
5. **[EXECUTION]** Run `git diff --name-only` against `pipeline/` and `sprint/` directories and verify no changes (NFR-002)
6. **[EXECUTION]** Run resolution timing test and verify <1s completion (NFR-001)
7. **[EXECUTION]** Run directory cap test with >10 dirs input and verify cap respected (NFR-005)
8. **[VERIFICATION]** Collect all evidence artifacts: test output logs, grep output, git diff output, timing results
9. **[COMPLETION]** Record comprehensive regression and NFR evidence

**Acceptance Criteria:**
- `uv run pytest` exits 0 with all existing tests passing unchanged (Stream C)
- `grep -r "async def\|await" src/superclaude/cli/cli_portify/` returns empty output
- `git diff --name-only` shows no changes in `pipeline/` or `sprint/` directories
- Resolution timing test using `time.monotonic()` assertions completes in <1 second (NFR-001)

**Validation:**
- `uv run pytest -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0038/evidence.md`

**Dependencies:** T03.04, T03.05 (all test streams must be in place)
**Rollback:** N/A (verification only, no code changes)
**Notes:** This task proves all 12 success criteria and 7 release gate items from the roadmap.

---

### T03.07 -- Verify All Success Criteria and Release Gate

| Field | Value |
|---|---|
| Roadmap Item IDs | R-042, R-043, R-044 |
| Why | Final verification that all 12 success criteria and 7 release gate items are satisfied |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0036, D-0037, D-0038 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0036/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0037/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0038/evidence.md

**Deliverables:**
1. Verification checklist confirming all 12 success criteria (SC-1 through SC-12)
2. Release gate confirmation of all 7 gate items

**Steps:**
1. **[PLANNING]** Enumerate all 12 success criteria from the roadmap
2. **[PLANNING]** Enumerate all 7 release gate items from the roadmap
3. **[EXECUTION]** For each success criterion, reference the specific test or evidence that proves it
4. **[EXECUTION]** For each release gate item, reference the specific test stream output
5. **[VERIFICATION]** Cross-reference all evidence artifacts to ensure completeness
6. **[COMPLETION]** Produce final release readiness summary

**Acceptance Criteria:**
- All 12 success criteria (SC-1 through SC-12) have linked evidence artifacts
- All 7 release gate items have explicit pass/fail determination with evidence
- `uv run pytest` final run exits 0 as comprehensive proof
- No outstanding warnings or errors in validation pipeline output

**Validation:**
- Manual check: all 12 SC items and 7 gate items have linked evidence
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0036/`, `D-0037/`, `D-0038/`

**Dependencies:** T03.06
**Rollback:** N/A (verification only)

---

### Checkpoint: End of Phase 3

**Purpose:** Confirm all Phase 3 deliverables are complete: all validation streams green, regression and NFR proof complete. Release is ready.

**Checkpoint Report Path:** .dev/releases/current/v2.24.1-cli-portify-cli-v5/checkpoints/CP-P03-END.md

**Verification:**
- All ~37 new tests pass (Streams A & B verified in T03.04 and T03.05)
- All existing tests pass unchanged (Stream C verified in T03.06)
- All non-functional requirements verified (Stream D verified in T03.06)

**Exit Criteria:**
- All 12 success criteria verified with linked evidence (Checkpoint C from roadmap)
- All 7 release gate items passed
- Zero outstanding warnings or errors
