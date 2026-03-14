# Phase 1 -- Foundation: Pre-work, Models & Resolution Core

Establish delivery guardrails, data models, and the deterministic resolution algorithm. Before code changes begin, produce lightweight artifacts formalizing the continuous testing contract. Then implement the `TargetInputType` enum, `ResolvedTarget` dataclass, `ComponentTree`, and the full `resolve_target()` algorithm in `resolution.py` with tests for all 6 input forms.

---

### T01.01 -- Produce Pre-work Artifacts (Change Map, Compat Checklist, Test Matrix)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001, R-002, R-003 |
| Why | Formalize delivery guardrails before any code changes; enumerate impacted files, confirm constraints, and identify test coverage gaps |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0001, D-0002, D-0003 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0001/spec.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0002/spec.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0003/spec.md

**Deliverables:**
1. Change map enumerating all impacted files: `models.py`, new `resolution.py`, `discover_components.py`, `process.py`, `cli.py`, `config.py`, `validate_config.py`, tests
2. Compatibility checklist confirming: no `pipeline/`/`sprint/` edits, no async code, existing skill-directory behavior unchanged, `resolve_workflow_path()` untouched
3. Test matrix outline cataloging existing tests and identifying coverage gaps for new resolution paths

**Steps:**
1. **[PLANNING]** Read existing `src/superclaude/cli/cli_portify/` directory structure and identify all files that will be modified or created
2. **[PLANNING]** Read `pipeline/` and `sprint/` directories to document the no-modification boundary
3. **[EXECUTION]** Write change map listing each file, its modification type (new/extend/unchanged), and scope of changes
4. **[EXECUTION]** Write compatibility checklist with explicit pass/fail assertions for each constraint from the spec
5. **[EXECUTION]** Catalog existing test files under `tests/cli_portify/` and identify which resolution paths lack coverage
6. **[COMPLETION]** Store all three artifacts under `TASKLIST_ROOT/artifacts/`

**Acceptance Criteria:**
- Change map artifact at `TASKLIST_ROOT/artifacts/D-0001/spec.md` lists all 7+ impacted files with modification type
- Compatibility checklist artifact at `TASKLIST_ROOT/artifacts/D-0002/spec.md` contains explicit assertions for each constraint
- Test matrix artifact at `TASKLIST_ROOT/artifacts/D-0003/spec.md` identifies coverage gaps for all 6 input forms
- All three artifacts are internally consistent (files referenced in change map appear in test matrix)

**Validation:**
- Manual check: each artifact contains the required sections as described in roadmap Milestone 1.0
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0001/`, `D-0002/`, `D-0003/`

**Dependencies:** None
**Rollback:** TBD (planning artifacts only)
**Notes:** These artifacts formalize the continuous testing contract: `uv run pytest` must pass at every subsequent milestone boundary.

---

### T01.02 -- Define TargetInputType Enum and ResolvedTarget Dataclass in models.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004, R-005 |
| Why | Establish the core data types for the 6 input forms and their resolved representation |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0004, D-0005 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0004/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0005/evidence.md

**Deliverables:**
1. `TargetInputType` enum in `src/superclaude/cli/cli_portify/models.py` with 5 values: `COMMAND_NAME`, `COMMAND_PATH`, `SKILL_DIR`, `SKILL_NAME`, `SKILL_FILE`
2. `ResolvedTarget` dataclass in `src/superclaude/cli/cli_portify/models.py` with fields: `input_form`, `input_type`, `command_path`, `skill_dir`, `project_root`, `commands_dir`, `skills_dir`, `agents_dir`

**Steps:**
1. **[PLANNING]** Read existing `src/superclaude/cli/cli_portify/models.py` to understand current dataclass patterns and imports
2. **[PLANNING]** Confirm no existing `TargetInputType` or `ResolvedTarget` definitions to avoid collision
3. **[EXECUTION]** Add `TargetInputType` enum with exactly the 5 spec-defined values using Python `enum.Enum`
4. **[EXECUTION]** Add `ResolvedTarget` dataclass with all spec-required fields using `@dataclass` with type annotations (`Path | None` for optional paths)
5. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/` to confirm existing tests still pass after models.py modification
6. **[COMPLETION]** Record evidence of enum values and dataclass fields

**Acceptance Criteria:**
- `TargetInputType` enum in `src/superclaude/cli/cli_portify/models.py` contains exactly 5 members matching spec values
- `ResolvedTarget` dataclass has all 8 spec-required fields with correct type annotations
- `uv run pytest tests/cli_portify/` exits 0 with all existing tests passing
- Both types are importable: `from superclaude.cli.cli_portify.models import TargetInputType, ResolvedTarget`

**Validation:**
- `uv run pytest tests/cli_portify/ -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Dependencies:** T01.01
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/models.py`
**Notes:** Critical path override: models.py is in the models/ domain. These types are foundational -- all subsequent tasks depend on them.

---

### T01.03 -- Define Component Entry Dataclasses and ComponentTree in models.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006, R-007 |
| Why | Define the tiered component hierarchy (Command/Skill/Agent entries) and the tree that aggregates them |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0006, D-0007 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0006/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0007/evidence.md

**Deliverables:**
1. `CommandEntry` (Tier 0), `SkillEntry` (Tier 1), `AgentEntry` (Tier 2) dataclasses in `models.py`
2. `ComponentTree` dataclass with `command`, `skill`, `agents` fields plus `component_count`, `total_lines`, `all_source_dirs` computed properties

**Steps:**
1. **[PLANNING]** Read existing `models.py` to identify existing `ComponentEntry`/`ComponentInventory` patterns to extend consistently
2. **[PLANNING]** Confirm tier numbering convention (0=command, 1=skill, 2=agent) matches existing usage
3. **[EXECUTION]** Add `CommandEntry`, `SkillEntry`, `AgentEntry` dataclasses with tier-appropriate fields
4. **[EXECUTION]** Add `ComponentTree` dataclass with `command: CommandEntry | None`, `skill: SkillEntry | None`, `agents: list[AgentEntry]` fields
5. **[EXECUTION]** Implement `component_count`, `total_lines`, `all_source_dirs` as `@property` computed properties on `ComponentTree`
6. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/` to confirm existing tests still pass
7. **[COMPLETION]** Record evidence of dataclass fields and computed property behavior

**Acceptance Criteria:**
- `CommandEntry`, `SkillEntry`, `AgentEntry` dataclasses exist in `models.py` with tier designations matching spec
- `ComponentTree` has `component_count` property returning integer count of non-None components + agent count
- `ComponentTree.all_source_dirs` returns deduplicated list of `Path` objects from all component source directories
- `uv run pytest tests/cli_portify/` exits 0 with all existing tests passing

**Validation:**
- `uv run pytest tests/cli_portify/ -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0006/evidence.md`

**Dependencies:** T01.02
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/models.py`

---

### T01.04 -- Extend PortifyConfig and Augment derive_cli_name() in models.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008, R-009 |
| Why | Wire new resolution fields into the existing config and ensure CLI name derivation prefers resolved command name with backward compat |
| Effort | M |
| Risk | Medium |
| Risk Drivers | model/schema extension, backward-compatibility concern |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0008, D-0009 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0008/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0009/evidence.md

**Deliverables:**
1. Extended `PortifyConfig` with fields: `target_input`, `target_type`, `command_path`, `commands_dir`, `skills_dir`, `agents_dir`, `project_root`, `include_agents`, `save_manifest_path`, `component_tree`
2. Updated `derive_cli_name()` that prefers resolved command name when available, falling back to existing behavior

**Steps:**
1. **[PLANNING]** Read `PortifyConfig` current definition and `derive_cli_name()` implementation in `models.py`
2. **[PLANNING]** Identify all call sites of `derive_cli_name()` to assess backward-compatibility risk
3. **[EXECUTION]** Add new fields to `PortifyConfig` with `None` defaults to preserve backward compatibility
4. **[EXECUTION]** Modify `derive_cli_name()` to check `self.command_path` first; if present, derive name from command filename; else fall back to existing logic
5. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/` to confirm existing derive_cli_name() behavior unchanged for legacy inputs
6. **[COMPLETION]** Record evidence of new fields and backward-compat test results

**Acceptance Criteria:**
- `PortifyConfig` contains all 10 spec-required fields with `None` defaults where appropriate
- `derive_cli_name()` returns command-derived name when `command_path` is set, and original behavior when `command_path` is `None`
- `uv run pytest tests/cli_portify/` exits 0 with all existing tests passing (backward compat proof)
- New fields are type-annotated and documented with inline comments referencing spec requirement IDs

**Validation:**
- `uv run pytest tests/cli_portify/ -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Dependencies:** T01.03
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/models.py`

---

### T01.05 -- Implement to_flat_inventory(), to_manifest_markdown(), and Error Constants

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010, R-011, R-012 |
| Why | Provide the boundary conversion from Path-based models to legacy str-based inventory, manifest output, and typed error codes |
| Effort | S |
| Risk | Medium |
| Risk Drivers | backward-compatibility boundary (Path to str conversion) |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010, D-0011, D-0012 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0010/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0011/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0012/evidence.md

**Deliverables:**
1. `to_flat_inventory()` method on `ComponentTree` that converts to backward-compatible `ComponentInventory` (Path to str at boundary)
2. `to_manifest_markdown()` method on `ComponentTree` that produces human-readable Markdown output
3. Error code constants at module level: `ERR_TARGET_NOT_FOUND`, `ERR_AMBIGUOUS_TARGET`, `ERR_BROKEN_ACTIVATION`, `WARN_MISSING_AGENTS`

**Steps:**
1. **[PLANNING]** Read existing `ComponentInventory` class to understand the str-based interface contract
2. **[PLANNING]** Identify the exact Path-to-str conversion points needed
3. **[EXECUTION]** Implement `to_flat_inventory()` on `ComponentTree` converting all `Path` fields to `str` for `ComponentInventory` construction
4. **[EXECUTION]** Implement `to_manifest_markdown()` producing Markdown with frontmatter fields and component listing
5. **[EXECUTION]** Add module-level string constants for the 4 error codes in `models.py`
6. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/` to confirm round-trip equivalence with existing inventory outputs
7. **[COMPLETION]** Record evidence of conversion boundary behavior

**Acceptance Criteria:**
- `to_flat_inventory()` produces a `ComponentInventory` instance whose fields are all `str` type (no `Path` leakage)
- `to_manifest_markdown()` returns a string containing YAML frontmatter with `source_command`, `source_skill`, `component_count` keys
- All 4 error code constants are importable: `from superclaude.cli.cli_portify.models import ERR_TARGET_NOT_FOUND, ERR_AMBIGUOUS_TARGET, ERR_BROKEN_ACTIVATION, WARN_MISSING_AGENTS`
- `uv run pytest tests/cli_portify/` exits 0 with all existing tests passing

**Validation:**
- `uv run pytest tests/cli_portify/ -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0010/evidence.md`

**Dependencies:** T01.04
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/models.py`

---

### Checkpoint: Phase 1 / Tasks T01.01-T01.05

**Purpose:** Verify all models.py additions are complete, backward-compatible, and tested before proceeding to resolution algorithm.

**Checkpoint Report Path:** .dev/releases/current/v2.24.1-cli-portify-cli-v5/checkpoints/CP-P01-T01-T05.md

**Verification:**
- All 5 new types (`TargetInputType`, `ResolvedTarget`, `CommandEntry`/`SkillEntry`/`AgentEntry`, `ComponentTree`) are importable
- `to_flat_inventory()` round-trip produces equivalent output to existing `ComponentInventory` construction
- `uv run pytest tests/cli_portify/` exits 0 with zero test failures

**Exit Criteria:**
- All dataclass fields match spec requirements (verified by import test)
- `derive_cli_name()` backward compatibility confirmed (existing test passes unchanged)
- Error code constants are defined and importable

---

### T01.06 -- Write Unit Tests for Dataclass Construction, Round-trip, and Error Codes

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | Validate all new model types before building the resolution algorithm on top of them |
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
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0013/evidence.md

**Deliverables:**
1. Unit test file covering: `TargetInputType` enum membership, `ResolvedTarget` construction with valid/invalid fields, `ComponentTree` computed properties, `to_flat_inventory()` round-trip equivalence, error code constant values

**Steps:**
1. **[PLANNING]** Read existing test patterns in `tests/cli_portify/` for fixture and assertion conventions
2. **[PLANNING]** Enumerate test cases: enum membership (5 values), dataclass construction (valid + missing required fields), computed properties (empty tree, full tree), round-trip (Path->str->verify), error codes (4 constants)
3. **[EXECUTION]** Write test functions in `tests/cli_portify/test_models.py` (or extend existing test file)
4. **[EXECUTION]** Include parametrized tests for all `TargetInputType` enum values
5. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/test_models.py -v` and confirm all new tests pass
6. **[COMPLETION]** Record test count and pass/fail evidence

**Acceptance Criteria:**
- Test file at `tests/cli_portify/test_models.py` contains tests for all 5 model types plus error codes
- `uv run pytest tests/cli_portify/test_models.py -v` exits 0 with all tests passing
- Round-trip test verifies `ComponentTree -> to_flat_inventory() -> ComponentInventory` field equivalence
- Error code tests verify exact string values of all 4 constants

**Validation:**
- `uv run pytest tests/cli_portify/test_models.py -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0013/evidence.md`

**Dependencies:** T01.05
**Rollback:** `git checkout -- tests/cli_portify/test_models.py`

---

### T01.07 -- Implement resolve_target() Core with Input Classification and Guards

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014, R-015, R-016, R-017 |
| Why | Build the core resolution function that classifies inputs into 6 forms and applies input guards |
| Effort | M |
| Risk | Medium |
| Risk Drivers | multi-file scope (new resolution.py), model/schema domain |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0014, D-0015 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0014/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0015/evidence.md

**Deliverables:**
1. `resolve_target(target: str, ...) -> ResolvedTarget` function in new `src/superclaude/cli/cli_portify/resolution.py` with `time.monotonic()` timing and input classification for all 6 forms
2. Input guards: `sc:` prefix stripping with empty-after-strip guard raising `ERR_TARGET_NOT_FOUND`; empty/whitespace/None guard raising `ERR_TARGET_NOT_FOUND`

**Steps:**
1. **[PLANNING]** Review the 6 input form definitions from the spec to establish classification rules
2. **[PLANNING]** Design the classification order: path-based forms first (filesystem check), then name-based forms (prefix/convention check)
3. **[EXECUTION]** Create `src/superclaude/cli/cli_portify/resolution.py` with `resolve_target()` function signature
4. **[EXECUTION]** Implement `sc:` prefix stripping (strip, check empty remainder, raise `ERR_TARGET_NOT_FOUND` if empty)
5. **[EXECUTION]** Implement empty/whitespace/None guard as first check in `resolve_target()`
6. **[EXECUTION]** Implement input classification logic for all 6 forms using filesystem existence checks and naming convention matching
7. **[EXECUTION]** Wrap function body with `time.monotonic()` start/end for timing measurement
8. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/` to confirm no regression; write initial smoke test for `resolve_target()`
9. **[COMPLETION]** Record evidence of classification logic and timing implementation

**Acceptance Criteria:**
- `resolve_target()` function exists in `src/superclaude/cli/cli_portify/resolution.py` accepting a `target: str` parameter
- `resolve_target("")` and `resolve_target("   ")` and `resolve_target(None)` all raise error with code `ERR_TARGET_NOT_FOUND`
- `resolve_target("sc:")` (empty after strip) raises error with code `ERR_TARGET_NOT_FOUND`
- `resolve_target()` completes in <1 second for valid inputs (verified via `time.monotonic()` delta)
- `resolution.py` contains no side effects and no I/O beyond file reads (purity constraint per architect focus)

**Validation:**
- `uv run pytest tests/cli_portify/ -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0014/evidence.md`

**Dependencies:** T01.02, T01.05 (needs `ResolvedTarget` type and error constants)
**Rollback:** `git rm src/superclaude/cli/cli_portify/resolution.py`
**Notes:** Keep resolution.py pure -- no side effects, no I/O beyond file reads. Log all resolution decisions for debugging.

---

### T01.08 -- Implement Ambiguity Detection, Command-Skill Link, and Backward Resolution

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018, R-019, R-020 |
| Why | Complete the resolution algorithm with cross-type linking and deterministic precedence rules |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (command-skill-agent linking), ambiguity detection complexity |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0016, D-0017, D-0018 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0016/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0017/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0018/evidence.md

**Deliverables:**
1. Ambiguity detection in `resolution.py` raising `ERR_AMBIGUOUS_TARGET` with command-first policy when a target matches both command and skill
2. Command-to-skill link via `## Activation` section parsing in command files, matching `Skill sc:<name>-protocol` pattern
3. Skill-to-command backward resolution via `sc-`/`-protocol` stripping heuristic in `resolution.py`

**Steps:**
1. **[PLANNING]** Read existing command file format to understand `## Activation` section structure and `Skill sc:<name>-protocol` pattern
2. **[PLANNING]** Design ambiguity detection: when target matches both command name and skill name, apply command-first policy
3. **[EXECUTION]** Implement ambiguity detection logic in `resolve_target()` that checks both command and skill namespaces
4. **[EXECUTION]** Implement `## Activation` parsing that reads command .md files and extracts `Skill sc:<name>-protocol` references
5. **[EXECUTION]** Implement skill-to-command backward resolution: given skill dir name, strip `sc-` prefix and `-protocol` suffix to derive candidate command name
6. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/` to confirm no regression
7. **[COMPLETION]** Record evidence of precedence logic and linking behavior

**Acceptance Criteria:**
- `resolve_target("roadmap")` when both `commands/sc/roadmap.md` and `skills/sc-roadmap-protocol/` exist resolves to command (command-first policy)
- Command-to-skill link correctly parses `## Activation` section and finds the associated skill directory
- Skill-to-command backward resolution correctly derives `roadmap` from `sc-roadmap-protocol` directory name
- `uv run pytest tests/cli_portify/` exits 0 with all existing tests passing

**Validation:**
- `uv run pytest tests/cli_portify/ -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0016/evidence.md`

**Dependencies:** T01.07
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/resolution.py`
**Notes:** Log all resolution decisions (which input form detected, why command-first applied) for debugging user-reported issues.

---

### T01.09 -- Handle Edge Cases and Write Resolution Tests for All 6 Input Forms

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021, R-022 |
| Why | Cover standalone command, standalone skill, multi-skill commands, and comprehensive test coverage for all input forms |
| Effort | S |
| Risk | Medium |
| Risk Drivers | edge case complexity, multi-form test matrix |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0019, D-0020 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0019/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0020/evidence.md

**Deliverables:**
1. Edge case handling in `resolution.py`: standalone command (`skill=None`), standalone skill (`command=None`), multi-skill commands (primary only, secondaries warned)
2. Test file covering all 6 input forms, all error codes, edge cases, and resolution timing (<1s assertion)

**Steps:**
1. **[PLANNING]** Enumerate edge cases: command with no linked skill, skill with no linked command, command linking to multiple skills
2. **[PLANNING]** Design test matrix: 6 input forms x success/failure, 4 error codes, 3 edge cases, timing assertion
3. **[EXECUTION]** Implement standalone command handling: set `skill_dir=None` in `ResolvedTarget`, continue without error
4. **[EXECUTION]** Implement standalone skill handling: set `command_path=None` in `ResolvedTarget`, continue without error
5. **[EXECUTION]** Implement multi-skill detection: use first `Skill sc:<name>-protocol` match as primary, emit warning for secondaries
6. **[EXECUTION]** Write comprehensive test file `tests/cli_portify/test_resolution.py` with parametrized tests for all 6 forms
7. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/test_resolution.py -v` and confirm all tests pass with timing <1s
8. **[COMPLETION]** Record test count, pass/fail results, and timing evidence

**Acceptance Criteria:**
- `resolve_target()` returns `ResolvedTarget` with `skill_dir=None` for standalone commands without error
- `resolve_target()` returns `ResolvedTarget` with `command_path=None` for standalone skills without error
- `tests/cli_portify/test_resolution.py` contains tests for all 6 input forms, all 4 error codes, and timing assertion
- `uv run pytest tests/cli_portify/test_resolution.py -v` exits 0 with all tests passing

**Validation:**
- `uv run pytest tests/cli_portify/test_resolution.py -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0019/evidence.md`

**Dependencies:** T01.08
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/resolution.py tests/cli_portify/test_resolution.py`

---

### Checkpoint: End of Phase 1

**Purpose:** Confirm all Phase 1 deliverables are complete: models stable, resolution algorithm functional for all 6 input forms, all existing tests pass.

**Checkpoint Report Path:** .dev/releases/current/v2.24.1-cli-portify-cli-v5/checkpoints/CP-P01-END.md

**Verification:**
- `uv run pytest tests/cli_portify/` exits 0 with all tests (existing + new) passing
- All 6 input forms resolve correctly with deterministic behavior (verified by `test_resolution.py`)
- `TargetInputType`, `ResolvedTarget`, `ComponentTree`, error constants all importable and functional

**Exit Criteria:**
- Models + resolver stable, all 6 input forms resolve correctly (Checkpoint A from roadmap)
- No modifications to `pipeline/` or `sprint/` directories (verified by `git diff --name-only`)
- `grep -r "async def\|await" src/superclaude/cli/cli_portify/resolution.py` returns empty
