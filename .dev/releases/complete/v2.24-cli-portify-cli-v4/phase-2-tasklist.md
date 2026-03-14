# Phase 2 -- Foundation and CLI Skeleton

Build the non-Claude substrate so orchestration rests on stable, well-typed primitives. This phase produces the configuration layer, CLI registration, contract model, shared utilities, and foundation unit tests.

### T02.01 -- Implement PortifyConfig and PortifyStepResult Domain Models

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | All subsequent phases depend on well-typed configuration and step result models that extend the existing pipeline architecture. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema, model (data keywords) |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0005, D-0006 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0005/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0006/spec.md

**Deliverables:**
1. `PortifyConfig` class in `src/superclaude/cli/cli_portify/config.py` extending `PipelineConfig` with: workflow path resolution (directory containing `SKILL.md`), CLI name derivation (strip `sc-`/`-protocol`, kebab/snake conversion), output directory writability check, name collision detection
2. `PortifyStepResult` class in `src/superclaude/cli/cli_portify/models.py` extending `StepResult` with: step metadata, artifact paths, gate tier metadata, timeout settings (per-iteration and total budget per Phase 1 decision), review flags, resume metadata (typed fields, not generic dict)

**Steps:**
1. **[PLANNING]** Read `pipeline.models` to confirm `PipelineConfig` and `StepResult` APIs via import test
2. **[PLANNING]** Load Phase 1 decision record (D-0001) for timeout and resume metadata shape decisions
3. **[EXECUTION]** Implement `PortifyConfig` with workflow path resolution, CLI name derivation, output directory writability check, name collision detection
4. **[EXECUTION]** Implement `PortifyStepResult` with step metadata, artifact paths, gate tier metadata, timeout settings, review flags, typed resume metadata
5. **[EXECUTION]** Add type annotations and dataclass/attrs definitions consistent with existing pipeline patterns
6. **[VERIFICATION]** Run `uv run pytest tests/` to verify models compile and integrate with pipeline architecture
7. **[COMPLETION]** Document model APIs and field semantics

**Acceptance Criteria:**
- `PortifyConfig` class exists in `src/superclaude/cli/cli_portify/config.py` and successfully extends `PipelineConfig`
- `PortifyStepResult` class exists in `src/superclaude/cli/cli_portify/models.py` and successfully extends `StepResult`
- Both classes import and instantiate without error: `from superclaude.cli.cli_portify.config import PortifyConfig` succeeds
- Resume metadata uses typed fields (not generic dict) per Phase 1 decision

**Validation:**
- `uv run pytest tests/cli_portify/test_models.py` exits 0
- Evidence: linkable artifact produced at D-0005/spec.md and D-0006/spec.md

**Dependencies:** T01.01, T01.02
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Critical Path Override: Yes -- models/ path detected. Tier conflict: model vs implement -> resolved to STRICT by priority rule.

---

### T02.02 -- Register cli_portify_group in main.py CLI Entry Point

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | The CLI command group must be registered so all subsequent steps can be invoked via the `superclaude` command. |
| Effort | S |
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
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0007/spec.md

**Deliverables:**
1. `cli_portify_group` Click group registered in `src/superclaude/cli/main.py` via `app.add_command()` with options: workflow path, output directory, `--dry-run`, `--skip-review`, `--start`, convergence/budget controls, timeout controls

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/main.py` to identify existing command registration pattern
2. **[PLANNING]** Identify all CLI options from roadmap: workflow path, output directory, --dry-run, --skip-review, --start, convergence/budget controls, timeout controls
3. **[EXECUTION]** Create `src/superclaude/cli/cli_portify/__init__.py` with `cli_portify_group` Click group
4. **[EXECUTION]** Register group in `main.py` via `app.add_command(cli_portify_group)`
5. **[EXECUTION]** Define all Click options with types and defaults
6. **[VERIFICATION]** Run `uv run superclaude cli-portify --help` to verify CLI parses correctly
7. **[COMPLETION]** Document CLI options and usage

**Acceptance Criteria:**
- `uv run superclaude cli-portify --help` exits 0 and displays all defined options
- Options include: workflow path (required), output directory, --dry-run, --skip-review, --start, convergence controls, timeout controls
- Registration follows existing `app.add_command()` pattern in main.py
- No modifications to existing CLI commands or groups

**Validation:**
- `uv run superclaude cli-portify --help` exits 0 with expected options listed
- Evidence: linkable artifact produced at D-0007/spec.md

**Dependencies:** T02.01
**Rollback:** TBD (if not specified in roadmap)

---

### T02.03 -- Implement Contract Schema and Resume Command Generation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | All exit paths must emit populated contracts (NFR-009) and resumable failures must generate resume commands. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema (data keyword) |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0008, D-0009 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0008/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0009/spec.md

**Deliverables:**
1. Contract schema defining `success`, `partial`, `failed`, `dry_run` states with all fields populated on every exit path per NFR-009
2. Resume command generation logic that produces `--start` commands for resumable failure steps with suggested budget

**Steps:**
1. **[PLANNING]** Load artifact contract (D-0003) for output field definitions
2. **[PLANNING]** Identify all exit paths from roadmap: success, partial (ESCALATED), failed, dry_run
3. **[EXECUTION]** Implement contract dataclass with fields for: status, steps completed, artifacts produced, gate results, timing, resume command (if applicable)
4. **[EXECUTION]** Implement default population logic ensuring all failure paths emit populated contracts
5. **[EXECUTION]** Implement resume command generation: `--start <step>` with suggested budget based on remaining work
6. **[VERIFICATION]** Test contract emission for all 4 exit states, verify no field is None/empty on failure paths
7. **[COMPLETION]** Document contract schema and resume command format

**Acceptance Criteria:**
- Contract objects emit for all 4 exit states (`success`, `partial`, `failed`, `dry_run`) with no None/empty fields
- Resume command generation produces valid `--start <step>` commands for Steps 5-7 (resumable steps)
- `dry_run` contracts mark phases 3-4 as `skipped` per roadmap specification
- Contract schema is serializable to JSON for machine-readable output

**Validation:**
- `uv run pytest tests/cli_portify/test_contracts.py` exits 0 covering all 4 exit states
- Evidence: linkable artifact produced at D-0008/spec.md and D-0009/spec.md

**Dependencies:** T02.01, T01.03
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Critical Path Override: Yes -- models/ path in contract schema.

---

### T02.04 -- Implement Shared Utility Layer

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | Shared utilities (frontmatter parsing, file checks, hashing, signal constants) are used across all subsequent phases. |
| Effort | S |
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
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0010/spec.md

**Deliverables:**
1. Shared utility module in `src/superclaude/cli/cli_portify/utils.py` containing: frontmatter parsing helpers, file existence/writability checks, section hashing utilities for additive-only verification (NFR-008), line counting and artifact rendering helpers, signal vocabulary constants from D-0004

**Steps:**
1. **[PLANNING]** Load signal vocabulary (D-0004) and artifact contract (D-0003) for constants and parsing rules
2. **[PLANNING]** Identify utility needs from Phases 3-6 step descriptions
3. **[EXECUTION]** Implement frontmatter parsing using PyYAML with validation
4. **[EXECUTION]** Implement file existence/writability checks, line counting, and artifact rendering helpers
5. **[EXECUTION]** Implement section hashing utilities for additive-only verification per NFR-008
6. **[VERIFICATION]** Run utility function smoke tests to verify correct parsing and hashing behavior
7. **[COMPLETION]** Document utility API

**Acceptance Criteria:**
- File `src/superclaude/cli/cli_portify/utils.py` exists with frontmatter parsing, file checks, section hashing, line counting, and signal constants
- Frontmatter parser correctly handles YAML frontmatter delimited by `---`
- Section hashing produces deterministic hashes for identical content
- Signal constants include all 6 values from D-0004

**Validation:**
- Manual check: all 5 utility categories (frontmatter, file checks, hashing, line counting, signal constants) are implemented
- Evidence: linkable artifact produced at D-0010/spec.md

**Dependencies:** T01.03, T01.04
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier classified EXEMPT because this is a utility/helper layer with no security or data integrity impact. Tier conflict: implement vs utility-only scope -> resolved to EXEMPT by read-only/helper nature.

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.04

**Purpose:** Verify foundation layer is operational before proceeding to unit tests and deterministic steps.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P02-T01-T04.md
**Verification:**
- PortifyConfig and PortifyStepResult compile and integrate with pipeline architecture
- CLI command parses correctly with all defined options
- Contract objects emit for all 4 exit states with populated defaults
**Exit Criteria:**
- `uv run superclaude cli-portify --help` exits 0
- Contract emission tests pass for success, partial, failed, dry_run
- Shared utilities are importable and functional

---

### T02.05 -- Write Unit Tests for Config Validation and Contract Emission

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | Config validation must complete <1s with all error code paths covered, and contract emission must be verified for mocked success and failure flows. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0011/spec.md

**Deliverables:**
1. Unit test suite in `tests/cli_portify/test_config.py` and `tests/cli_portify/test_contracts.py` covering: config validation <1s timing assertion, all error code paths (4 failure scenarios per SC-001), contract emission for mocked success and failure flows

**Steps:**
1. **[PLANNING]** Identify all error code paths from SC-001: invalid workflow path, missing SKILL.md, non-writable output, name collision
2. **[PLANNING]** Identify contract emission test cases: success, partial, failed, dry_run
3. **[EXECUTION]** Write config validation tests with timing assertions (<1s)
4. **[EXECUTION]** Write contract emission tests for all 4 exit states
5. **[EXECUTION]** Write error code path tests for all 4 failure scenarios
6. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/ -v` and verify all tests pass
7. **[COMPLETION]** Record test coverage metrics

**Acceptance Criteria:**
- `uv run pytest tests/cli_portify/test_config.py tests/cli_portify/test_contracts.py -v` exits 0 with all tests passing
- Config validation tests include timing assertion (<1s per SC-001)
- All 4 error code paths tested: invalid workflow path, missing SKILL.md, non-writable output, name collision
- Contract emission tests cover success, partial, failed, dry_run states

**Validation:**
- `uv run pytest tests/cli_portify/ -v` exits 0
- Evidence: linkable artifact produced at D-0011/spec.md

**Dependencies:** T02.01, T02.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 2

**Purpose:** Verify CLI and model foundation is fully operational with tested config validation and contract emission before proceeding to deterministic pipeline steps.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P02-END.md
**Verification:**
- CLI command parses correctly with all options
- Base config/result types compile and integrate with current architecture
- Contract objects emit for mocked success and failure flows
**Exit Criteria:**
- `uv run superclaude cli-portify --help` exits 0 (M1 criterion)
- `uv run pytest tests/cli_portify/ -v` exits 0 with config and contract tests passing
- All 4 error code paths for config validation are tested
