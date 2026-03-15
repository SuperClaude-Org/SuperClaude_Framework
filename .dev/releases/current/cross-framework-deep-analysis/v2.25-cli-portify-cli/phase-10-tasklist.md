# Phase 10 -- CLI Integration

Expose the feature through the main CLI. Implement Click command group, wire options, register in main.py, and verify module generation order compliance.

### T10.01 -- Implement Click Command Group with run Subcommand

| Field | Value |
|---|---|
| Roadmap Item IDs | R-113 |
| Why | FR-049 requires Click command group with run subcommand exposing cli-portify through the main CLI. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0056 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0056/spec.md

**Deliverables:**
- `src/superclaude/cli/cli_portify/commands.py` with Click command group and `run` subcommand

**Steps:**
1. **[PLANNING]** Review existing Click command patterns in `src/superclaude/cli/` for convention adherence
2. **[PLANNING]** Define command group structure: `cli-portify` group with `run` subcommand
3. **[EXECUTION]** Implement Click group using `@click.group()` decorator in `commands.py`
4. **[EXECUTION]** Implement `run` subcommand with Click command decorator
5. **[VERIFICATION]** Write test: `superclaude cli-portify run --help` displays expected options
6. **[COMPLETION]** Document command structure in D-0056/spec.md

**Acceptance Criteria:**
- `commands.py` defines Click command group `cli-portify` with `run` subcommand (FR-049)
- Command group follows existing `src/superclaude/cli/` Click patterns
- `superclaude cli-portify run --help` displays usage information
- `run` subcommand accepts a required positional argument for the workflow path (skill directory to portify)
- CLI `run` subcommand returns correct exit codes mapped from PortifyOutcome values: 0 for success, non-zero for failure/halted/interrupted (SC-013)
- Command structure documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0056/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_cli_command"` exits 0
- Evidence: linkable artifact produced at D-0056/spec.md

**Dependencies:** T09.03 (diagnostics), T08.06 (convergence complete)
**Rollback:** TBD (if not specified in roadmap)

---

### T10.02 -- Wire CLI Options

| Field | Value |
|---|---|
| Roadmap Item IDs | R-114 |
| Why | The run subcommand must expose: --name, --output, --max-turns (default 200), --model, --dry-run, --resume, --debug. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0057 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0057/spec.md

**Deliverables:**
- Click options wired to run subcommand: `--name` (string), `--output` (path), `--max-turns` (int, default 200), `--model` (string), `--dry-run` (flag), `--resume` (string), `--debug` (flag)

**Steps:**
1. **[PLANNING]** Define option types and defaults: --max-turns default 200, --dry-run as boolean flag, --resume accepts step-id
2. **[PLANNING]** Map options to executor parameters from Phase 3
3. **[EXECUTION]** Wire all 7 Click options to run subcommand with correct types and defaults
4. **[EXECUTION]** Connect options to executor initialization: pass config, enable dry-run, set resume point
5. **[VERIFICATION]** Write tests: each option is correctly parsed and passed to executor
6. **[COMPLETION]** Document CLI options in D-0057/spec.md

**Acceptance Criteria:**
- All 7 options wired: --name, --output, --max-turns (default 200), --model, --dry-run, --resume, --debug
- --max-turns defaults to 200 when not specified
- --dry-run and --debug are boolean flags; --resume accepts step-id string
- CLI options documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0057/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_cli_options"` exits 0
- Evidence: linkable artifact produced at D-0057/spec.md

**Dependencies:** T10.01
**Rollback:** TBD (if not specified in roadmap)

---

### T10.03 -- Implement --dry-run Phase Type Filtering

| Field | Value |
|---|---|
| Roadmap Item IDs | R-115 |
| Why | FR-037 and SC-012 require --dry-run to limit execution to PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION phase types only. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide (execution filtering) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0058 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0058/spec.md

**Deliverables:**
- --dry-run integration test verifying only PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION phase types execute; no SYNTHESIS or CONVERGENCE artifacts produced

**Steps:**
1. **[PLANNING]** Review dry-run filtering from T03.04 executor implementation
2. **[PLANNING]** Confirm allowed phase types: PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION
3. **[EXECUTION]** Wire CLI --dry-run flag to executor dry-run mode
4. **[EXECUTION]** Verify executor filters exclude SYNTHESIS and CONVERGENCE phase types
5. **[VERIFICATION]** Write integration test: --dry-run produces no Phase 3-4 (synthesis/convergence) artifacts (SC-012)
6. **[COMPLETION]** Document dry-run behavior in D-0058/spec.md

**Acceptance Criteria:**
- --dry-run limits execution to PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION phase types (FR-037, SC-012)
- No SYNTHESIS or CONVERGENCE phase artifacts produced during dry-run
- Integration test validates no Phase 3-4 artifacts exist after dry-run execution
- Dry-run behavior documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0058/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_dry_run_integration"` exits 0
- Evidence: linkable artifact produced at D-0058/spec.md

**Dependencies:** T10.02
**Rollback:** TBD (if not specified in roadmap)

---

### T10.04 -- Register in src/superclaude/cli/main.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-116 |
| Why | FR-048 and AC-005 require registration in main.py via main.add_command(cli_portify_group) to make the command available through the superclaude CLI. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0059 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0059/spec.md

**Deliverables:**
- Registration of cli_portify command group in `src/superclaude/cli/main.py` via `main.add_command(cli_portify_group)`

**Steps:**
1. **[PLANNING]** Review existing command registrations in `src/superclaude/cli/main.py`
2. **[PLANNING]** Confirm import path for cli_portify command group
3. **[EXECUTION]** Add import of cli_portify_group from `src/superclaude/cli/cli_portify/commands.py`
4. **[EXECUTION]** Add `main.add_command(cli_portify_group)` registration call
5. **[VERIFICATION]** Verify `superclaude cli-portify run --help` is accessible from the main CLI entry point
6. **[COMPLETION]** Document registration in D-0059/spec.md

**Acceptance Criteria:**
- `main.add_command(cli_portify_group)` added to `src/superclaude/cli/main.py` (FR-048, AC-005)
- `superclaude cli-portify run` is invokable from the main CLI entry point
- Import follows existing convention in main.py
- Registration documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0059/spec.md

**Validation:**
- `uv run superclaude cli-portify run --help` exits 0 with usage output
- Evidence: linkable artifact produced at D-0059/spec.md

**Dependencies:** T10.01
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: Phase 10 / Tasks T10.01-T10.04

**Purpose:** Verify CLI command is registered and invokable with correct options and dry-run filtering.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P10-T01-T04.md

**Verification:**
- `superclaude cli-portify run --help` displays all 7 options with correct defaults
- --dry-run limits execution to correct phase types (SC-012)
- Command registered in main.py and accessible from CLI entry point

**Exit Criteria:**
- Milestone M9 (partial): CLI command invokable and wired
- SC-012 (--dry-run limits to correct phase types) validated via integration test
- All 4 tasks completed with proper Click integration

---

### T10.05 -- Implement Prompt Splitting and Verify Module Generation Order

| Field | Value |
|---|---|
| Roadmap Item IDs | R-117, R-118 |
| Why | FR-050 requires prompt splitting to portify-prompts.md when aggregate prompt exceeds 300 lines. NFR-006 and AC-012 require module generation order verification. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████░░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0060 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0060/spec.md

**Deliverables:**
- Prompt splitting logic: if aggregate prompt length exceeds 300 lines, split to `portify-prompts.md`
- Module generation order verification: assert order matches mandated sequence from T03.03

**Steps:**
1. **[PLANNING]** Define prompt aggregation: count total lines across all prompt builders
2. **[PLANNING]** Review mandated generation order from T03.03
3. **[EXECUTION]** Implement prompt length check: if aggregate > 300 lines, split to portify-prompts.md (FR-050, AC-010)
4. **[EXECUTION]** Implement generation order verification asserting mandated sequence (NFR-006, AC-012)
5. **[VERIFICATION]** Write tests: prompt under 300 lines stays inline; prompt over 300 lines splits; generation order matches
6. **[COMPLETION]** Document prompt splitting and order verification in D-0060/spec.md

**Acceptance Criteria:**
- Prompts exceeding 300 aggregate lines split to `portify-prompts.md` (FR-050, AC-010)
- Prompts under 300 lines remain inline without splitting
- Module generation order verified: models → gates → prompts → config → inventory → monitor → process → executor → tui → logging_ → diagnostics → commands → __init__
- Splitting and order verification documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0060/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_prompt_splitting"` exits 0
- Evidence: linkable artifact produced at D-0060/spec.md

**Dependencies:** T10.04
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 10

**Purpose:** Verify superclaude cli-portify run is invokable and wired into the application with all options, prompt splitting, and generation order compliance.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P10-END.md

**Verification:**
- `superclaude cli-portify run` is invokable with all 7 options functional
- --dry-run and --resume flags work correctly end-to-end
- Module generation order matches mandated sequence

**Exit Criteria:**
- Milestone M9 satisfied: CLI command invokable and wired into application
- All 5 tasks (T10.01-T10.05) completed with deliverables D-0056 through D-0060 produced
- Prompt splitting and generation order verification in place
