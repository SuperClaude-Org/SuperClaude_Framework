# Phase 2 -- Integration: Discovery, Process, CLI

Wire resolution into the existing pipeline without breaking backward compatibility. Milestones 2.1 (discovery) and 2.2 (process) can run in parallel since they depend only on Phase 1 models. Milestone 2.3 (CLI/config) depends on both 2.1 and 2.2.

---

### T02.01 -- Implement Agent Extraction with 6 AGENT_PATTERNS and Build ComponentTree

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023, R-024 |
| Why | Extract agent references from SKILL.md using all 6 spec-defined regex patterns and assemble the ComponentTree |
| Effort | M |
| Risk | Medium |
| Risk Drivers | regex pattern complexity, cross-cutting scope (6 patterns across SKILL.md formats) |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0021, D-0022 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0021/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0022/evidence.md

**Deliverables:**
1. Agent extraction in `src/superclaude/cli/cli_portify/discover_components.py` using 6 AGENT_PATTERNS: backtick-agent notation, YAML arrays, spawn/delegate/invoke verbs, `uses` references, model-parenthetical patterns, `agents/` path patterns
2. `ComponentTree` builder function that assembles the tree from a `ResolvedTarget` using discovered command, skill, and agent entries

**Steps:**
1. **[PLANNING]** Read existing `discover_components.py` to understand current discovery patterns and extension points
2. **[PLANNING]** Review the 6 AGENT_PATTERNS from the spec to ensure regex accuracy
3. **[EXECUTION]** Add compiled `re.Pattern` constants for all 6 agent extraction patterns at module level in `discover_components.py`
4. **[EXECUTION]** Implement agent extraction function that applies all 6 patterns to SKILL.md content and returns `list[AgentEntry]`
5. **[EXECUTION]** Implement `build_component_tree(resolved: ResolvedTarget) -> ComponentTree` that reads command, skill, discovers agents
6. **[VERIFICATION]** Write tests in `tests/cli_portify/test_discover.py` with synthetic SKILL.md fixtures covering all 6 patterns
7. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/ -v` to confirm all tests pass
8. **[COMPLETION]** Record evidence of pattern matching accuracy across all 6 forms

**Acceptance Criteria:**
- All 6 AGENT_PATTERNS are implemented as compiled `re.Pattern` constants in `discover_components.py`
- Agent extraction against a synthetic SKILL.md containing all 6 pattern forms returns correct agent names for each
- `build_component_tree()` returns a `ComponentTree` with populated `command`, `skill`, and `agents` fields
- `uv run pytest tests/cli_portify/ -v` exits 0 with all existing and new tests passing

**Validation:**
- `uv run pytest tests/cli_portify/test_discover.py -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0021/evidence.md`

**Dependencies:** T01.03 (needs ComponentTree, AgentEntry), T01.07 (needs ResolvedTarget)
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/discover_components.py`
**Notes:** Preserve one-way discovery depth per architect focus. No recursive agent-to-agent expansion in this release.

---

### T02.02 -- Handle Missing Agents and Implement --include-agent Deduplication

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025, R-026 |
| Why | Ensure missing agent references are observable but non-fatal, and CLI-override agents deduplicate correctly |
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
| Deliverable IDs | D-0023, D-0024 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0023/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0024/evidence.md

**Deliverables:**
1. Missing agent handler in `discover_components.py`: sets `found=False` on `AgentEntry`, emits `WARN_MISSING_AGENTS` warning, continues without error
2. `--include-agent` deduplication algorithm in discovery logic (Step R3): `referenced_in="cli-override"` takes precedence over auto-discovered agents with same name

**Steps:**
1. **[PLANNING]** Read `AgentEntry` dataclass to confirm `found` field availability
2. **[PLANNING]** Design deduplication strategy: CLI-override agents replace auto-discovered agents with matching names
3. **[EXECUTION]** Implement missing agent handling in the agent extraction loop: when agent directory does not exist, create `AgentEntry(found=False)` and log warning
4. **[EXECUTION]** Implement deduplication in `build_component_tree()`: merge CLI-override agent list with auto-discovered list, CLI-override wins on name collision
5. **[VERIFICATION]** Write tests for missing agent warning behavior and dedup precedence in `tests/cli_portify/test_discover.py`
6. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/ -v` to confirm all tests pass
7. **[COMPLETION]** Record evidence of warning emission and dedup behavior

**Acceptance Criteria:**
- Missing agent reference produces `AgentEntry` with `found=False` and logs warning containing `WARN_MISSING_AGENTS`
- Pipeline continues successfully when agents are missing (non-fatal behavior)
- CLI-override agent with `referenced_in="cli-override"` replaces auto-discovered agent with same name
- `uv run pytest tests/cli_portify/ -v` exits 0 with all existing and new tests passing

**Validation:**
- `uv run pytest tests/cli_portify/test_discover.py -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0023/evidence.md`

**Dependencies:** T02.01
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/discover_components.py`

---

### T02.03 -- Add additional_dirs to PortifyProcess with Directory Cap and Consolidation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027, R-028, R-029, R-030 |
| Why | Extend subprocess invocation with agent source directories while preventing overflow via deterministic two-tier consolidation |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (subprocess args), performance (directory cap) |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0025, D-0026 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0025/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0026/evidence.md

**Deliverables:**
1. `additional_dirs` parameter on `PortifyProcess` that builds `--add-dir` args from `ComponentTree.all_source_dirs` with deduplication
2. Directory cap at 10 with two-tier consolidation: Tier 1 uses `os.path.commonpath()` to merge directories sharing common ancestors (only when common parent contains no more than 3x total file count); Tier 2 selects top 10 by component count

**Steps:**
1. **[PLANNING]** Read existing `PortifyProcess` class in `src/superclaude/cli/cli_portify/process.py` to understand subprocess invocation pattern
2. **[PLANNING]** Design the two-tier consolidation algorithm with deterministic ordering
3. **[EXECUTION]** Add `additional_dirs: list[Path] | None = None` parameter to `PortifyProcess.__init__()` or relevant method
4. **[EXECUTION]** Implement `--add-dir` arg construction from deduplicated directory list
5. **[EXECUTION]** Implement Tier 1 consolidation: group dirs by `os.path.commonpath()`, merge only when common parent file count <= 3x constituent file count
6. **[EXECUTION]** Implement Tier 2 consolidation: if still >10 after Tier 1, select top 10 by component count (deterministic sort)
7. **[EXECUTION]** Record consolidation decisions in `resolution_log` (dict or structured log)
8. **[VERIFICATION]** Write tests for 0, 5, 15 directory inputs including Tier 2 fallback in `tests/cli_portify/test_process.py`
9. **[COMPLETION]** Record evidence of consolidation behavior and cap enforcement

**Acceptance Criteria:**
- `PortifyProcess` accepts `additional_dirs` parameter and produces correct `--add-dir` args in subprocess command
- With 15 input directories, consolidation reduces to <=10 with deterministic selection logged in `resolution_log`
- Tier 1 consolidation only merges when common parent file count <= 3x constituent total
- `uv run pytest tests/cli_portify/ -v` exits 0 with all existing and new tests passing

**Validation:**
- `uv run pytest tests/cli_portify/test_process.py -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0025/evidence.md`

**Dependencies:** T01.03 (needs ComponentTree.all_source_dirs), T01.07 (needs ResolvedTarget)
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/process.py`
**Notes:** This is a containment boundary per architect focus. The two-tier consolidation ensures robustness for skills referencing agents scattered across unrelated directories.

---

### T02.04 -- Verify additional_dirs=None Preserves Exact v2.24 Behavior (SC-11)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031 |
| Why | Prove that the new parameter does not alter existing subprocess behavior when not used |
| Effort | S |
| Risk | Medium |
| Risk Drivers | backward-compatibility validation, breaking change risk |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0027/evidence.md

**Deliverables:**
1. Backward-compatibility test proving `additional_dirs=None` produces identical subprocess command to v2.24 behavior

**Steps:**
1. **[PLANNING]** Read existing process invocation tests to understand the expected v2.24 subprocess command shape
2. **[PLANNING]** Identify specific assertions that would detect any behavioral change
3. **[EXECUTION]** Write test in `tests/cli_portify/test_process.py` that constructs `PortifyProcess` with `additional_dirs=None` and asserts subprocess args match v2.24 baseline
4. **[EXECUTION]** Compare generated subprocess command with and without `additional_dirs` parameter
5. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/test_process.py -v` and confirm backward-compat test passes
6. **[COMPLETION]** Record evidence of command equivalence

**Acceptance Criteria:**
- Test in `tests/cli_portify/test_process.py` explicitly asserts `additional_dirs=None` produces identical subprocess args to v2.24
- No `--add-dir` flags appear in subprocess command when `additional_dirs=None`
- `uv run pytest tests/cli_portify/test_process.py -v` exits 0 with backward-compat test passing
- Test is labeled with SC-11 reference in docstring or comment

**Validation:**
- `uv run pytest tests/cli_portify/test_process.py -v -k "v2_24 or backward or sc_11"`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0027/evidence.md`

**Dependencies:** T02.03
**Rollback:** `git checkout -- tests/cli_portify/test_process.py`

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.04

**Purpose:** Verify discovery and process integration are complete and backward-compatible before wiring CLI.

**Checkpoint Report Path:** .dev/releases/current/v2.24.1-cli-portify-cli-v5/checkpoints/CP-P02-T01-T04.md

**Verification:**
- All 6 AGENT_PATTERNS extract agents correctly from synthetic SKILL.md
- Directory consolidation produces <=10 dirs with deterministic selection logged
- `additional_dirs=None` preserves exact v2.24 behavior (SC-11)

**Exit Criteria:**
- Component tree assembly functional with command + skill + agents
- Process invocation tested with 0, 5, 15 directories
- `uv run pytest tests/cli_portify/` exits 0 with all tests passing

---

### T02.05 -- Change CLI Argument to TARGET and Add New CLI Options

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032, R-033, R-034, R-035 |
| Why | Update CLI interface from single WORKFLOW_PATH to flexible TARGET with directory overrides and agent options |
| Effort | M |
| Risk | Medium |
| Risk Drivers | backward-compatibility risk (CLI argument rename), multi-file scope |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0028, D-0029 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0028/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0029/evidence.md

**Deliverables:**
1. CLI argument changed from `WORKFLOW_PATH` to `TARGET` in `src/superclaude/cli/cli_portify/cli.py` with `--commands-dir`, `--skills-dir`, `--agents-dir` override options
2. `--include-agent` option with empty-string filtering and `--save-manifest` option added to CLI

**Steps:**
1. **[PLANNING]** Read existing `cli.py` Click command definition and identify the `WORKFLOW_PATH` argument
2. **[PLANNING]** Assess backward-compatibility: existing skill-directory inputs must still resolve identically via the resolver
3. **[EXECUTION]** Change Click argument from `WORKFLOW_PATH` to `TARGET` in the command decorator
4. **[EXECUTION]** Add `--commands-dir`, `--skills-dir`, `--agents-dir` Click options with `type=click.Path(exists=True)`
5. **[EXECUTION]** Add `--include-agent` Click option (multiple=True) with empty-string filtering in callback
6. **[EXECUTION]** Add `--save-manifest` Click option with `type=click.Path()`
7. **[VERIFICATION]** Write CLI integration tests in `tests/cli_portify/test_cli.py` for new options and legacy invocation
8. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/ -v` to confirm all tests pass
9. **[COMPLETION]** Record evidence of CLI interface changes and backward-compat behavior

**Acceptance Criteria:**
- CLI accepts `TARGET` as positional argument (replacing `WORKFLOW_PATH`) per `--help` output
- `--commands-dir`, `--skills-dir`, `--agents-dir` options appear in `--help` and pass values to config
- `--include-agent` filters empty strings and accepts multiple values
- Existing skill-directory invocations (e.g., `superclaude portify ./path/to/skill/`) continue to work identically

**Validation:**
- `uv run pytest tests/cli_portify/test_cli.py -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0028/evidence.md`

**Dependencies:** T02.01, T02.02, T02.03 (needs discovery, process integration wired before CLI exposes them)
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/cli.py`
**Notes:** CLI is the highest user-visible risk area per architect focus. Minimize surprise by preserving existing success paths.

---

### T02.06 -- Extend load_portify_config() and ValidateConfigResult

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036, R-037 |
| Why | Wire new parameters through config loading and expose resolution metadata in validation results |
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
| Deliverable IDs | D-0030, D-0031 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0030/evidence.md
- .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0031/evidence.md

**Deliverables:**
1. Extended `load_portify_config()` in `config.py` accepting and passing through: `target`, `commands_dir`, `skills_dir`, `agents_dir`, `include_agents`, `save_manifest_path`
2. Extended `ValidateConfigResult` with `command_path`, `skill_dir`, `target_type`, `agent_count`, `warnings` fields

**Steps:**
1. **[PLANNING]** Read existing `load_portify_config()` in `config.py` and `ValidateConfigResult` in `validate_config.py`
2. **[PLANNING]** Map new CLI options to `PortifyConfig` fields through config loading
3. **[EXECUTION]** Add parameters to `load_portify_config()` signature and wire to `PortifyConfig` constructor
4. **[EXECUTION]** Add `command_path`, `skill_dir`, `target_type`, `agent_count`, `warnings` fields to `ValidateConfigResult`
5. **[VERIFICATION]** Write config round-trip tests in `tests/cli_portify/test_config.py`
6. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/ -v` to confirm all tests pass
7. **[COMPLETION]** Record evidence of config passthrough behavior

**Acceptance Criteria:**
- `load_portify_config()` accepts all new parameters and produces a `PortifyConfig` with corresponding fields populated
- `ValidateConfigResult` includes `command_path`, `skill_dir`, `target_type`, `agent_count`, and `warnings` fields
- Config round-trip test: create config from CLI args, validate, confirm all fields preserved in result
- `uv run pytest tests/cli_portify/ -v` exits 0 with all existing and new tests passing

**Validation:**
- `uv run pytest tests/cli_portify/test_config.py -v`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0030/evidence.md`

**Dependencies:** T02.05 (needs CLI to pass new params)
**Rollback:** `git checkout -- src/superclaude/cli/cli_portify/config.py src/superclaude/cli/cli_portify/validate_config.py`

---

### Checkpoint: End of Phase 2

**Purpose:** Confirm all Phase 2 deliverables are complete: component tree + process integration + CLI stable with full backward compatibility.

**Checkpoint Report Path:** .dev/releases/current/v2.24.1-cli-portify-cli-v5/checkpoints/CP-P02-END.md

**Verification:**
- CLI accepts all new options and resolves targets through the full pipeline (resolution -> discovery -> process)
- Existing skill-directory invocations produce identical behavior to v2.24
- `uv run pytest tests/cli_portify/` exits 0 with all tests (existing + new) passing

**Exit Criteria:**
- Component tree + process integration + CLI stable (Checkpoint B from roadmap)
- All new CLI options functional with correct config passthrough
- No modifications to `pipeline/` or `sprint/` directories
