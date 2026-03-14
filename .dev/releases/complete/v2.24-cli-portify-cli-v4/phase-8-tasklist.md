# Phase 8 -- Validation and Release

Prove the implementation meets both functional and non-functional requirements before merge. This phase covers unit tests, integration tests, compliance verification, SC validation matrix, evidence package, and developer documentation.

### T08.01 -- Write Unit Test Layer for All Deterministic Logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | Unit tests cover deterministic logic: validation rules, naming derivation, gate functions, score calculations (including 7.0/6.9 boundary), contract defaults, hashing, resume command generation. |
| Effort | M |
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
| Deliverable IDs | D-0040 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0040/spec.md

**Deliverables:**
1. Comprehensive unit test suite in `tests/cli_portify/` covering: path validation, naming derivation (strip sc-/protocol, kebab/snake conversion), frontmatter parsing, score math (overall = mean of 4 dimensions +/- 0.01 per SC-008), boundary tests (7.0 true / 6.9 false per SC-009), gate result helpers (tuple[bool, str]), section hashing, resume command generation, contract defaults, convergence engine (standalone)

**Steps:**
1. **[PLANNING]** Identify all deterministic logic components requiring unit tests from Phases 2-6
2. **[PLANNING]** Map SC criteria to specific test cases: SC-008 (score math), SC-009 (boundary), SC-010 (contract paths)
3. **[EXECUTION]** Write naming derivation tests: sc-brainstorm-protocol -> brainstorm, kebab-case and snake_case variants
4. **[EXECUTION]** Write score boundary tests: 7.0 true, 6.9 false (SC-009); overall = mean(4 dims) +/- 0.01 (SC-008)
5. **[EXECUTION]** Write contract default tests: all 4 exit paths emit populated contracts (SC-010)
6. **[EXECUTION]** Write gate function, hashing, resume command, and convergence engine tests
7. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/ -v --tb=short` and verify all unit tests pass
8. **[COMPLETION]** Record test count and coverage metrics

**Acceptance Criteria:**
- `uv run pytest tests/cli_portify/ -v` exits 0 with all unit tests passing
- Score boundary test verifies 7.0 true and 6.9 false (SC-009)
- Score math test verifies overall = mean(clarity, completeness, testability, consistency) +/- 0.01 (SC-008)
- Contract default tests verify all 4 exit paths (success, partial, failed, dry_run) emit populated contracts (SC-010)

**Validation:**
- `uv run pytest tests/cli_portify/ -v --tb=short` exits 0
- Evidence: linkable artifact produced at D-0040/spec.md

**Dependencies:** T07.03, T07.04
**Rollback:** TBD (if not specified in roadmap)

---

### T08.02 -- Write Integration Test Layer for Orchestration Flows

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029 |
| Why | Integration tests verify end-to-end orchestration: happy path, --dry-run, review rejection, brainstorm fallback, panel fallback, convergence boundaries, template missing, timeout behavior. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (end-to-end flows), performance (integration test timing) |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0041 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0041/spec.md

**Deliverables:**
1. Integration test suite in `tests/cli_portify/integration/` covering: full happy path (using mock harness), `--dry-run` halts after Step 4 with correct contract (SC-011), review rejection produces USER_REJECTED, brainstorm fallback activates when skill missing, panel fallback and marker parsing, convergence boundary cases (converge at iteration 1, escalate at max), template missing triggers fail-fast, timeout behavior for per-iteration and total budget

**Steps:**
1. **[PLANNING]** Identify all integration test scenarios from roadmap exit criteria and SC matrix
2. **[PLANNING]** Configure mock harness (D-0021) for each test scenario
3. **[EXECUTION]** Write happy path integration test using mock harness
4. **[EXECUTION]** Write --dry-run test: verify phases 3-4 marked skipped in contract (SC-011)
5. **[EXECUTION]** Write review rejection, brainstorm/panel fallback, convergence boundary, template missing, and timeout tests
6. **[VERIFICATION]** Run `uv run pytest tests/cli_portify/integration/ -v` and verify all integration tests pass
7. **[COMPLETION]** Record integration test coverage across all exit paths

**Acceptance Criteria:**
- `uv run pytest tests/cli_portify/integration/ -v` exits 0 with all integration tests passing
- Happy path test produces all 9 output artifacts through mock harness
- --dry-run test verifies phases 3-4 marked `skipped` in contract (SC-011)
- Convergence boundary tests cover: converge at iteration 1, escalate at max_convergence, budget exhaustion

**Validation:**
- `uv run pytest tests/cli_portify/integration/ -v` exits 0
- Evidence: linkable artifact produced at D-0041/spec.md

**Dependencies:** T08.01, T04.04
**Rollback:** TBD (if not specified in roadmap)

---

### T08.03 -- Run Compliance Verification Checks

| Field | Value |
|---|---|
| Roadmap Item IDs | R-030 |
| Why | Architectural constraints must be verified: zero async def/await in cli_portify/ (SC-012), zero diffs in pipeline/sprint (SC-013), gate signatures compliant, runner-authored truth enforced. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | compliance (architectural constraints) |
| Tier | STANDARD |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0042 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0042/spec.md

**Deliverables:**
1. Compliance verification results documenting: (a) zero `async def`/`await` in `src/superclaude/cli/cli_portify/` via `grep -r "async def\|await" src/superclaude/cli/cli_portify/` (SC-012), (b) zero diffs in `pipeline/` and `sprint/` via `git diff --name-only` (SC-013), (c) all gate functions return `tuple[bool, str]`, (d) no Claude-directed sequencing in runner code

**Steps:**
1. **[PLANNING]** Define compliance check commands from SC-012 and SC-013
2. **[PLANNING]** Identify gate function signatures to verify tuple[bool, str] return type
3. **[EXECUTION]** Run `grep -r "async def\|await" src/superclaude/cli/cli_portify/` and verify zero matches (SC-012)
4. **[EXECUTION]** Run `git diff --name-only` filtered to pipeline/ and sprint/ and verify zero changes (SC-013)
5. **[EXECUTION]** Verify all gate functions in gates.py return tuple[bool, str] via static inspection
6. **[VERIFICATION]** All 4 compliance checks pass with zero violations
7. **[COMPLETION]** Record compliance check results as evidence

**Acceptance Criteria:**
- `grep -r "async def\|await" src/superclaude/cli/cli_portify/` returns zero matches (SC-012)
- `git diff --name-only` shows zero changes in `pipeline/` and `sprint/` directories (SC-013)
- All gate functions in `src/superclaude/cli/cli_portify/gates.py` return `tuple[bool, str]`
- No Claude-directed sequencing found in runner code (manual review)

**Validation:**
- `grep -r "async def\|await" src/superclaude/cli/cli_portify/` returns empty (SC-012)
- Evidence: linkable artifact produced at D-0042/spec.md with grep and git diff output

**Dependencies:** T08.01
**Rollback:** TBD (if not specified in roadmap)

---

### T08.04 -- Validate SC Criteria Matrix (SC-001 through SC-016)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031 |
| Why | The SC validation matrix provides traceability from each functional requirement to its test layer and validation method. All 16 criteria must be satisfied. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | compliance (cross-reference validation), cross-cutting scope (all criteria) |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0043 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0043/spec.md

**Deliverables:**
1. SC validation matrix cross-reference report mapping each SC criterion (SC-001 through SC-016) to: test layer (Unit/Integration/Static), validation method, test file/function, pass/fail status, evidence reference

**Steps:**
1. **[PLANNING]** Load SC validation matrix from roadmap (SC-001 through SC-016)
2. **[PLANNING]** Map each SC criterion to implemented tests from T08.01, T08.02, T08.03
3. **[EXECUTION]** Execute all referenced test commands for SC-001 through SC-016
4. **[EXECUTION]** Record pass/fail status for each criterion with evidence paths
5. **[EXECUTION]** Generate cross-reference report linking SC criteria to test results
6. **[VERIFICATION]** Verify all 16 SC criteria are either satisfied or explicitly waived with evidence
7. **[COMPLETION]** Write validation matrix report to D-0043/spec.md

**Acceptance Criteria:**
- All 16 SC criteria (SC-001 through SC-016) have documented test results with pass/fail status
- Each criterion maps to a specific test file/function in the test suite
- SC-015 validates has_section_12 structural content (heading-only rejection, findings table acceptance, zero-gap acceptance)
- SC-016 validates per-iteration independent timeout behavior

**Validation:**
- `uv run pytest tests/cli_portify/ -v` exits 0 as baseline for all SC criteria
- Evidence: linkable artifact produced at D-0043/spec.md with per-criterion pass/fail matrix

**Dependencies:** T08.01, T08.02, T08.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: Phase 8 / Tasks T08.01-T08.04

**Purpose:** Verify all tests pass and compliance checks are satisfied before evidence packaging.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P08-T01-T04.md
**Verification:**
- Unit test suite passes with coverage of all deterministic logic
- Integration test suite covers all exit paths including boundary cases
- All 16 SC criteria are satisfied or explicitly waived
**Exit Criteria:**
- `uv run pytest tests/cli_portify/ -v` exits 0 with all tests passing
- Zero async/await violations (SC-012) and zero base-module modifications (SC-013)
- SC validation matrix report documents all 16 criteria

---

### T08.05 -- Assemble Evidence Package for Release Readiness

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Why | The evidence package provides verifiable proof that all functional and non-functional requirements are met before merge. |
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
| Deliverable IDs | D-0044 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0044/spec.md

**Deliverables:**
1. Evidence package containing: (a) test results for all functional criteria (SC-001 through SC-016), (b) example output artifacts from happy path run, (c) failure-path contract samples (partial, failed, dry_run), (d) `git diff` proof for no base-module modifications, (e) grep proof for no async usage, (f) boundary test evidence (7.0 gate, convergence termination, placeholder elimination, dry-run stop)

**Steps:**
1. **[PLANNING]** Collect all test results from T08.01, T08.02, T08.03, T08.04
2. **[PLANNING]** Identify example output artifacts from happy path integration test
3. **[EXECUTION]** Assemble test results with pass/fail status for each SC criterion
4. **[EXECUTION]** Collect failure-path contract samples from integration tests
5. **[EXECUTION]** Collect git diff and grep proofs from compliance verification (T08.03)
6. **[VERIFICATION]** Verify evidence package is complete: all SC criteria have evidence, all proof types present
7. **[COMPLETION]** Write evidence package summary to D-0044/spec.md

**Acceptance Criteria:**
- Evidence package contains test results for all 16 SC criteria
- Happy path example output artifacts are included
- Failure-path contract samples cover partial, failed, and dry_run states
- git diff proof shows zero base-module modifications; grep proof shows zero async usage

**Validation:**
- Manual check: evidence package contains all 6 evidence types listed in roadmap
- Evidence: linkable artifact produced at D-0044/spec.md

**Dependencies:** T08.04
**Rollback:** TBD (if not specified in roadmap)

---

### T08.06 -- Write Developer Documentation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033 |
| Why | Developer documentation ensures the cli_portify command is discoverable and usable by implementers. |
| Effort | S |
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
| Deliverable IDs | D-0045 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0045/spec.md

**Deliverables:**
1. Developer documentation covering: command help text, example invocation, artifact expectations, troubleshooting notes for common failure scenarios

**Steps:**
1. **[PLANNING]** Collect CLI help text from --help output
2. **[PLANNING]** Identify common failure scenarios from T07.04 failure-path handling
3. **[EXECUTION]** Write command usage documentation with example invocations
4. **[EXECUTION]** Write artifact expectations documentation explaining each output file
5. **[EXECUTION]** Write troubleshooting notes for the 7 failure types
6. **[VERIFICATION]** Review documentation for completeness and accuracy against implementation
7. **[COMPLETION]** Write developer documentation to D-0045/spec.md

**Acceptance Criteria:**
- Documentation includes command help text matching `uv run superclaude cli-portify --help` output
- At least 2 example invocations are documented (basic and with --dry-run)
- Artifact expectations section covers all 9 output artifacts
- Troubleshooting notes cover all 7 failure types from T07.04

**Validation:**
- Manual check: documentation covers help text, examples, artifact expectations, and troubleshooting
- Evidence: linkable artifact produced at D-0045/spec.md

**Dependencies:** T08.05
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 8

**Purpose:** Verify release-ready implementation with all SC criteria satisfied, evidence package complete, and merge candidate ready.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P08-END.md
**Verification:**
- All SC criteria satisfied or explicitly waived with evidence
- No architectural constraint violations remain
- Evidence package is complete with all 6 evidence types
**Exit Criteria:**
- `uv run pytest tests/cli_portify/ -v` exits 0 with all tests passing (M7 criterion)
- SC validation matrix (D-0043) shows all 16 criteria satisfied
- Developer documentation (D-0045) covers usage, artifacts, and troubleshooting
