# Phase 4 -- Subprocess Orchestration Core

Introduce the executor-managed Claude integration safely, with subprocess isolation, path scoping, monitoring, and gate enforcement. This phase is a prerequisite gate (M3) before content steps -- build the platform, stabilize it, then build on it.

### T04.01 -- Implement PortifyProcess Extending ClaudeProcess

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | All Claude-assisted steps (3-7) depend on a subprocess wrapper that manages --add-dir scoping, exit codes, stdout/stderr capture, and timeout state. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | model (data keyword), subprocess scope |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0017/spec.md

**Deliverables:**
1. `PortifyProcess` class in `src/superclaude/cli/cli_portify/process.py` extending `pipeline.ClaudeProcess` with: `--add-dir` for both work directory and workflow path, prompt construction with `@path` references, exit code/stdout/stderr/timeout/diagnostics capture

**Steps:**
1. **[PLANNING]** Read `pipeline.process.ClaudeProcess` to confirm `extra_args` API and extension pattern
2. **[PLANNING]** Identify path scoping requirements: work directory + workflow path both passed via `--add-dir`
3. **[EXECUTION]** Implement `PortifyProcess` extending `ClaudeProcess` with dual `--add-dir` support
4. **[EXECUTION]** Implement prompt construction with `@path` references to prior artifacts
5. **[EXECUTION]** Implement capture of exit code, stdout, stderr, timeout state, and diagnostics
6. **[VERIFICATION]** Test PortifyProcess instantiation and argument construction with mock paths
7. **[COMPLETION]** Document subprocess lifecycle and path scoping behavior

**Acceptance Criteria:**
- `PortifyProcess` class exists in `src/superclaude/cli/cli_portify/process.py` and extends `pipeline.ClaudeProcess`
- `--add-dir` is passed for both work directory and workflow path in subprocess arguments
- Prompt construction supports `@path` references to prior step artifacts
- Exit code, stdout, stderr, timeout state, and diagnostics are all captured after subprocess execution

**Validation:**
- `uv run pytest tests/cli_portify/test_process.py -v` exits 0
- Evidence: linkable artifact produced at D-0017/spec.md

**Dependencies:** T02.01, T02.04
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Critical Path Override: Yes -- models/ path in process wrapper. Risk driven by subprocess scope management (R-5).

---

### T04.02 -- Implement Prompt Builder Framework

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | Each Claude-assisted step requires a dedicated prompt builder that constructs @path references, output contracts, frontmatter expectations, and retry augmentation. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (all Claude steps) |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0018/spec.md

**Deliverables:**
1. Prompt builder framework in `src/superclaude/cli/cli_portify/prompts.py` with: one builder per Claude-assisted step (Steps 3-7), input references via `@path` to prior artifacts, step-specific output contracts and frontmatter expectations, retry augmentation for targeted failures (especially placeholder residue)

**Steps:**
1. **[PLANNING]** Identify the 5 Claude-assisted steps requiring prompt builders: analyze-workflow, design-pipeline, synthesize-spec, brainstorm-gaps, panel-review
2. **[PLANNING]** Map prior artifact dependencies for each step's `@path` references
3. **[EXECUTION]** Implement base prompt builder class with @path reference construction and output contract embedding
4. **[EXECUTION]** Implement per-step prompt builder subclasses for Steps 3-7
5. **[EXECUTION]** Implement retry augmentation logic that includes specific remaining placeholder names on failure
6. **[VERIFICATION]** Test prompt builders produce valid prompt strings with correct @path references for each step
7. **[COMPLETION]** Document prompt builder API and per-step prompt structure

**Acceptance Criteria:**
- Prompt builders exist for all 5 Claude-assisted steps (Steps 3-7)
- Each builder constructs prompts with `@path` references to prior artifacts from the correct step
- Output contracts and frontmatter expectations are embedded in each prompt
- Retry augmentation supports targeted failures (especially `{{SC_PLACEHOLDER:*}}` placeholder residue) in retry prompts

**Validation:**
- `uv run pytest tests/cli_portify/test_prompts.py -v` exits 0
- Evidence: linkable artifact produced at D-0018/spec.md

**Dependencies:** T04.01
**Rollback:** TBD (if not specified in roadmap)

---

### T04.03 -- Implement Monitoring, Diagnostics, and Failure Classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | Monitoring provides observability into subprocess behavior and enables failure classification for targeted retries and resume. |
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
| Deliverable IDs | D-0019, D-0020, D-0048 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0019/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0020/spec.md
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0048/spec.md

**Deliverables:**
1. NDJSON/JSONL event logging module in `src/superclaude/cli/cli_portify/monitor.py` using signal vocabulary constants from D-0004/D-0010
2. Failure classification system supporting 7 types: timeout, missing artifact, malformed frontmatter, gate failure, user rejection, budget exhaustion, partial artifact
3. Markdown report generation from diagnostic data

**Steps:**
1. **[PLANNING]** Load signal vocabulary constants (D-0004/D-0010) for event types
2. **[PLANNING]** Identify 7 failure types from roadmap: timeout, missing artifact, malformed frontmatter, gate failure, user rejection, budget exhaustion, partial artifact
3. **[EXECUTION]** Implement NDJSON event logger with signal extraction from subprocess output
4. **[EXECUTION]** Implement timing capture for phases and individual steps
5. **[EXECUTION]** Implement failure classification enum and classifier logic for all 7 types
6. **[EXECUTION]** Implement markdown report generation from captured diagnostic data
7. **[VERIFICATION]** Test event logging produces valid NDJSON and failure classification assigns correct types
8. **[COMPLETION]** Document monitoring API and failure type definitions

**Acceptance Criteria:**
- NDJSON event logger produces valid JSONL output using signal vocabulary constants
- All 7 failure types are classifiable: timeout, missing artifact, malformed frontmatter, gate failure, user rejection, budget exhaustion, partial artifact
- Timing capture records per-phase and per-step durations
- Markdown report generation produces readable diagnostic summaries

**Validation:**
- `uv run pytest tests/cli_portify/test_monitor.py -v` exits 0
- Evidence: linkable artifact produced at D-0019/spec.md, D-0020/spec.md, D-0048/spec.md

**Dependencies:** T02.04, T04.01
**Rollback:** TBD (if not specified in roadmap)

---

### T04.04 -- Build Claude Subprocess Mock Harness

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | A mock harness that returns known-good outputs enables unit testing of all Claude-assisted steps without actual Claude invocations, dramatically reducing development iteration time. |
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
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0021/spec.md

**Deliverables:**
1. Claude subprocess mock harness in `tests/cli_portify/fixtures/mock_harness.py` returning known-good outputs for each step type (analyze-workflow, design-pipeline, synthesize-spec, brainstorm-gaps, panel-review)

**Steps:**
1. **[PLANNING]** Identify expected output format for each of the 5 Claude-assisted steps from roadmap
2. **[PLANNING]** Define known-good output fixtures with correct frontmatter and required sections
3. **[EXECUTION]** Implement mock harness that intercepts PortifyProcess subprocess calls
4. **[EXECUTION]** Create fixture outputs for: portify-analysis.md, portify-spec.md, synthesized spec, brainstorm findings, panel-report.md
5. **[EXECUTION]** Include edge case fixtures: partial output, malformed frontmatter, timeout simulation
6. **[VERIFICATION]** Verify mock harness produces outputs that pass gate checks for each step
7. **[COMPLETION]** Document mock harness usage for Phases 5-6 testing

**Acceptance Criteria:**
- Mock harness returns known-good outputs for all 5 Claude-assisted step types
- Mock outputs pass their respective gate checks (STRICT gates for Steps 3-5, STANDARD for Step 6, STRICT for Step 7)
- Edge case fixtures exist for partial output, malformed frontmatter, and timeout scenarios
- Harness integrates with PortifyProcess to intercept subprocess calls

**Validation:**
- `uv run pytest tests/cli_portify/test_mock_harness.py -v` exits 0
- Evidence: linkable artifact produced at D-0021/spec.md

**Dependencies:** T04.01, T04.02
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.04

**Purpose:** Verify subprocess platform components are functional before gate engine integration.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P04-T01-T04.md
**Verification:**
- PortifyProcess extends ClaudeProcess with dual --add-dir support
- Prompt builders produce valid prompts for all 5 Claude-assisted steps
- Mock harness returns outputs that pass gate checks
**Exit Criteria:**
- `uv run pytest tests/cli_portify/test_process.py tests/cli_portify/test_prompts.py tests/cli_portify/test_mock_harness.py -v` exits 0
- Monitoring emits valid NDJSON events
- Failure classification covers all 7 types

---

### T04.05 -- Implement Gate Engine Bindings

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | Gate functions validate step outputs and enforce EXEMPT/STANDARD/STRICT tier compliance. All gates must return tuple[bool, str] per NFR-004. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (all gates), compliance |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0022/spec.md

**Deliverables:**
1. Gate engine bindings in `src/superclaude/cli/cli_portify/gates.py` with: all gate functions returning `tuple[bool, str]` per NFR-004, structural and semantic validators for STRICT/STANDARD outputs, integration with `pipeline.gates.gate_passed()` validation engine, EXEMPT/STANDARD/STRICT tier enforcement

**Steps:**
1. **[PLANNING]** Read `pipeline.gates.gate_passed()` to confirm integration API
2. **[PLANNING]** Map gate criteria from SC-001 through SC-007 to gate function implementations
3. **[EXECUTION]** Implement gate functions for each step: SC-001 (config), SC-002 (discovery), SC-003 (analysis), SC-004 (design), SC-005 (synthesis), SC-006 (brainstorm), SC-007 (panel-review)
4. **[EXECUTION]** Implement structural validators for frontmatter fields and section presence
5. **[EXECUTION]** Implement semantic validators for STRICT tier: section count, data flow diagram, frontmatter field counts
6. **[VERIFICATION]** Test all gate functions with known-good and known-bad inputs from mock harness
7. **[COMPLETION]** Document gate function signatures and validation criteria

**Acceptance Criteria:**
- All gate functions return `tuple[bool, str]` per NFR-004
- Gate functions exist for SC-001 through SC-007 covering all 7 steps
- STRICT gates enforce: required section count (SC-003), frontmatter field counts (SC-004), zero placeholder sentinels (SC-005), convergence terminal state (SC-007)
- Gates integrate with `pipeline.gates.gate_passed()` validation engine

**Validation:**
- `uv run pytest tests/cli_portify/test_gates.py -v` exits 0
- Evidence: linkable artifact produced at D-0022/spec.md

**Dependencies:** T02.04, T04.04
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 4

**Purpose:** Verify controlled subprocess platform is ready to support content generation steps. This milestone (M3) explicitly gates Phase 5.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P04-END.md
**Verification:**
- Claude-assisted steps can be executed in harness with mocked subprocess behavior
- Monitoring emits consistent machine-readable NDJSON records
- Gate engine integration is stable and deterministic
**Exit Criteria:**
- Mock harness produces realistic outputs for all 5 step types (M3 criterion)
- All gate functions return tuple[bool, str] and integrate with pipeline.gates
- `uv run pytest tests/cli_portify/ -v` exits 0 for all Phase 4 tests
