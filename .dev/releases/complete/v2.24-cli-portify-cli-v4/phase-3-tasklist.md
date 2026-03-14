# Phase 3 -- Fast Deterministic Steps

Implement the two pure-programmatic steps (validate-config and discover-components) for reliable early-phase execution and fast failure detection. These steps run without Claude subprocesses.

### T03.01 -- Implement validate-config Step (Step 1)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | Step 1 validates workflow path, derives CLI name, checks output writability, and detects collisions -- all without Claude. Fast failure prevents wasted subprocess time. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0012, D-0013 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0012/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0013/spec.md

**Deliverables:**
1. `validate_config` step implementation in `src/superclaude/cli/cli_portify/steps/validate_config.py` that: resolves workflow path to directory containing `SKILL.md`, derives CLI name (strip `sc-`, strip `-protocol`, normalize kebab/snake), validates output directory writability, detects name collisions with existing non-portified CLI modules
2. `validate-config-result.json` output artifact with validation results and derived CLI name

**Steps:**
1. **[PLANNING]** Load PortifyConfig (D-0005) to understand workflow path resolution API
2. **[PLANNING]** Identify 4 failure scenarios from SC-001: invalid path, missing SKILL.md, non-writable output, name collision
3. **[EXECUTION]** Implement workflow path resolution: resolve to valid skill directory containing `SKILL.md`
4. **[EXECUTION]** Implement CLI name derivation: strip `sc-`/`-protocol`, convert to kebab-case and snake_case variants
5. **[EXECUTION]** Implement output directory writability check and name collision detection against existing CLI modules
6. **[EXECUTION]** Write `validate-config-result.json` with validation status and derived name
7. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/test_validate_config.py -v` to verify <1s completion and correct error codes
8. **[COMPLETION]** Document step behavior and error codes

**Acceptance Criteria:**
- `validate-config` completes under 1s for valid and invalid inputs (SC-001)
- Correct error codes returned for all 4 failure scenarios: invalid path, missing SKILL.md, non-writable output, name collision
- `validate-config-result.json` is written with derived CLI name and validation status
- Step runs without any Claude subprocess invocation

**Validation:**
- `uv run pytest tests/cli_portify/test_validate_config.py -v` exits 0 with timing assertions
- Evidence: linkable artifact produced at D-0012/spec.md and D-0013/spec.md

**Dependencies:** T02.01, T02.04
**Rollback:** TBD (if not specified in roadmap)

---

### T03.02 -- Implement discover-components Step (Step 2)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | Step 2 inventories all skill components to provide accurate input for Claude-assisted analysis in Phase 5. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0014, D-0015 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0014/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0015/spec.md

**Deliverables:**
1. `discover_components` step implementation in `src/superclaude/cli/cli_portify/steps/discover_components.py` that inventories: `SKILL.md`, `refs/`, `rules/`, `templates/`, `scripts/`, matching command files with accurate line counting per component
2. `component-inventory.md` output artifact with YAML frontmatter containing `source_skill` and `component_count` fields

**Steps:**
1. **[PLANNING]** Load validate-config result (D-0013) to get resolved workflow path
2. **[PLANNING]** Identify all component types from roadmap: SKILL.md, refs/, rules/, templates/, scripts/, command files
3. **[EXECUTION]** Implement directory traversal to discover all components under the workflow path and locate matching command files
4. **[EXECUTION]** Implement accurate line counting for each discovered component file
5. **[EXECUTION]** Generate `component-inventory.md` with YAML frontmatter (`source_skill`, `component_count`) and per-component entries
6. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/test_discover_components.py -v` to verify <5s completion and frontmatter accuracy
7. **[COMPLETION]** Document discovery behavior and output format

**Acceptance Criteria:**
- `discover-components` completes under 5s for valid skill directories (SC-002)
- `component-inventory.md` contains valid YAML frontmatter with `source_skill` and `component_count` fields
- Line counts are accurate for each discovered component
- Step runs without any Claude subprocess invocation

**Validation:**
- `uv run pytest tests/cli_portify/test_discover_components.py -v` exits 0 with timing assertions
- Evidence: linkable artifact produced at D-0014/spec.md and D-0015/spec.md

**Dependencies:** T03.01
**Rollback:** TBD (if not specified in roadmap)

---

### T03.03 -- Implement Deterministic Gate Checks for Steps 1-2

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | Gate checks enforce runtime limits and structural validation for the deterministic steps before Claude-assisted steps begin. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0016/spec.md

**Deliverables:**
1. EXEMPT gate implementations for Steps 1-2: runtime limits as advisory/performance checks, structure validation for inventory output frontmatter and line counts

**Steps:**
1. **[PLANNING]** Load gate engine API from `pipeline.gates.gate_passed()` to understand integration pattern
2. **[PLANNING]** Identify gate criteria from SC-001 (config <1s, 4 error paths) and SC-002 (discovery <5s, frontmatter, line counts)
3. **[EXECUTION]** Implement EXEMPT gate for validate-config: timing advisory, error code coverage
4. **[EXECUTION]** Implement EXEMPT gate for discover-components: timing advisory, frontmatter structure validation
5. **[VERIFICATION]** Verify gates return `tuple[bool, str]` per NFR-004
6. **[COMPLETION]** Document gate criteria and advisory behavior

**Acceptance Criteria:**
- Gate functions exist for Steps 1 and 2, each returning `tuple[bool, str]` per NFR-004
- Gates enforce timing advisories (<1s for Step 1, <5s for Step 2)
- Inventory structure validation checks for YAML frontmatter presence and line count format
- Gates integrate with `pipeline.gates.gate_passed()` validation engine

**Validation:**
- Manual check: gate functions return tuple[bool, str] and integrate with pipeline.gates
- Evidence: linkable artifact produced at D-0016/spec.md

**Dependencies:** T02.04, T04.05
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 3

**Purpose:** Verify both deterministic steps complete successfully without Claude subprocesses, producing correct artifacts with passing gates.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P03-END.md
**Verification:**
- `validate-config` completes under 1s with correct failure codes for all 4 scenarios
- `discover-components` produces accurate inventory with valid frontmatter
- Both steps run without Claude subprocesses
**Exit Criteria:**
- `uv run pytest tests/cli_portify/test_validate_config.py tests/cli_portify/test_discover_components.py -v` exits 0
- Unit coverage exists for success and failure matrices (M2 criterion)
- Gate checks integrate with pipeline.gates and return tuple[bool, str]
