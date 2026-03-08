# Phase 2 -- Contract Infrastructure and Analysis

Implement the contract-driven phase boundary system, Phase 0 prerequisite scanning, and Phase 1 workflow analysis engine. This phase produces the foundational infrastructure that all downstream code generation depends on — contract schemas, resume semantics, API snapshots, component inventories, and dependency DAGs.

---

### T02.01 -- Define Contract Schemas and Versioning Policy

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018, R-019, R-020, R-026 |
| Why | Contract-driven phase boundaries require a versioned schema system; all downstream phases read and validate incoming contracts. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data/schema (versioning policy, backward-compatibility rules), cross-cutting (affects all 5 phases) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0010/spec.md

**Deliverables:**
- Contract schema versioning policy document defining: `schema_version` field format, backward-compatibility rules (additive fields allowed, field removal requires major version bump), version validation on contract read with actionable error messages
- YAML contract common header schema definition (`schema_version`, `phase`, `status`, `timestamp`, `resume_checkpoint`, `validation_status`)
- Null-field policy: unreached fields explicitly set to `null`

**Steps:**
1. **[PLANNING]** Review Phase 1 decisions.yaml for contract-related OQ resolutions (OQ-004, OQ-007)
2. **[PLANNING]** Identify all 6 contract types that need schemas: portify-prerequisites, portify-analysis, portify-spec, portify-codegen, portify-integration, return contract
3. **[EXECUTION]** Define schema_version format (semantic versioning "1.0") and backward-compatibility rules
4. **[EXECUTION]** Define YAML common header schema with all required fields and their types
5. **[EXECUTION]** Document null-field policy: fields for unreached phases set to `null`, not omitted
6. **[VERIFICATION]** Validate schema definition is self-consistent: no conflicting field types, no ambiguous status values
7. **[COMPLETION]** Record complete schema specification in D-0010/spec.md

**Acceptance Criteria:**
- Schema versioning policy exists in D-0010/spec.md with explicit backward-compatibility rules
- Common header schema defines all 6 required fields with YAML types and allowed values
- Null-field policy documented: unreached fields = `null`, not absent
- Policy is referenced by downstream Phase 0 and Phase 1 contract emission tasks

**Validation:**
- Manual check: schema document parseable as valid YAML when header fields are instantiated
- Evidence: linkable artifact produced at D-0010/spec.md

**Dependencies:** T01.09 (OQ-004 and OQ-007 resolutions inform schema design)
**Rollback:** Delete schema specification document

---

### T02.02 -- Define Per-Phase Contract Schemas

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | Each phase boundary requires a specific contract schema; Phase 0 through Phase 4 plus the return contract need defined field sets. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | data/schema (6 contract schemas), cross-cutting (contracts used across all phases) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0011/spec.md

**Deliverables:**
- Schema definitions for all 6 per-phase contracts: `portify-prerequisites.yaml`, `portify-analysis.yaml`, `portify-spec.yaml`, `portify-codegen.yaml`, `portify-integration.yaml`, and return contract structure (FR-043: status, failure_phase, failure_type, generated_files, counts, api_snapshot_hash, resume_command, warnings, phase_contracts)

**Steps:**
1. **[PLANNING]** Map each contract to its producing phase and consuming phase
2. **[PLANNING]** Identify required fields from roadmap FR references (FR-014, FR-022, FR-033, FR-038, FR-042, FR-043)
3. **[EXECUTION]** Define `portify-prerequisites.yaml` schema (Phase 0 output): workflow_path, api_snapshot, collision_status, pattern_scan_result
4. **[EXECUTION]** Define remaining 4 phase contract schemas plus return contract with all FR-043 fields
5. **[EXECUTION]** Define `portify-integration.yaml` per OQ-004 resolution: main_py_patched, command_registered, test_file_generated, smoke_test_passed
6. **[VERIFICATION]** Cross-validate all schemas: every field produced by one phase is consumed or recorded by the next
7. **[COMPLETION]** Record all 6 schema definitions in D-0011/spec.md

**Acceptance Criteria:**
- All 6 contract schemas defined with typed field declarations in D-0011/spec.md
- Return contract includes all FR-043 fields: status, failure_phase, failure_type, generated_files, counts, api_snapshot_hash, resume_command, warnings, phase_contracts
- `portify-integration.yaml` matches OQ-004 resolution: main_py_patched, command_registered, test_file_generated, smoke_test_passed
- Cross-phase field coverage verified: no consuming phase references undefined fields

**Validation:**
- Manual check: instantiate each schema as YAML — all fields present, types consistent
- Evidence: linkable artifact produced at D-0011/spec.md

**Dependencies:** T02.01 (common header schema must be defined first)
**Rollback:** Delete schema definitions

---

### T02.03 -- Implement Contract Validation, Return Contract, and Resume Protocol

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022, R-023, R-024, R-025 |
| Why | Contract validation prevents corrupted state propagation; resume protocol enables failure recovery without re-executing completed phases. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | data integrity (contract validation), breaking (resume from failure), cross-cutting (all phases use contracts) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0012, D-0013 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0012/evidence.md
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0013/evidence.md

**Deliverables:**
- Contract validation logic: next phase reads incoming contract, validates schema_version compatibility, checks required fields present, rejects incompatible versions with actionable error
- Return contract structure implementing FR-043 fields
- Resume protocol (FR-052): read latest contract, validate completed phase contracts, resume from failure point
- Synthetic failure validation proving resume mechanics work independently of phase implementations

**Steps:**
1. **[PLANNING]** Define validation logic interface: input contract path → validated contract data or error
2. **[PLANNING]** Define resume protocol interface: resume_checkpoint → phase to resume from + validated prior contracts
3. **[EXECUTION]** Implement contract validation: schema version check, required field presence, status enum validation
4. **[EXECUTION]** Implement return contract assembly: aggregate phase contracts into final return contract with FR-043 fields
5. **[EXECUTION]** Implement resume protocol: read latest contract, identify failure point, re-validate completed phases
6. **[EXECUTION]** Create synthetic failure scenario: Phase 0 succeeds → Phase 1 fails → resume skips Phase 0
7. **[VERIFICATION]** Run synthetic failure validation — resume correctly re-enters at Phase 1, not Phase 0
8. **[COMPLETION]** Record validation logic specification in D-0012 and synthetic test results in D-0013

**Acceptance Criteria:**
- Contract validation rejects contracts with incompatible schema_version and missing required fields
- Return contract contains all FR-043 fields populated from phase contract aggregation
- Resume from synthetic Phase 1 failure correctly skips completed Phase 0 and re-enters Phase 1
- Synthetic failure validation results documented in D-0013/evidence.md

**Validation:**
- Manual check: synthetic failure scenario produces correct resume behavior
- Evidence: linkable artifacts produced at D-0012/evidence.md and D-0013/evidence.md

**Dependencies:** T02.01, T02.02 (schemas must be defined before validation logic)
**Rollback:** Revert contract validation and resume protocol implementations

---

### T02.04 -- Implement Phase 0 Prerequisite Scanning

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027, R-028, R-029, R-030 |
| Why | Phase 0 scans the workflow, captures the live API snapshot, and checks for collisions before any analysis investment. |
| Effort | L |
| Risk | High |
| Risk Drivers | data integrity (API snapshot hash), security-adjacent (collision policy), cross-cutting (snapshot used by all downstream phases) |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes (models/ path) |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0014, D-0015 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0014/evidence.md
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0015/spec.md

**Deliverables:**
- Phase 0 prerequisite scanner implementing: workflow path resolution from `--workflow` (FR-010), live API snapshot from `models.py`/`gates.py` with content hash stored as `api-snapshot.yaml` (FR-011), output directory collision check with `portify-summary.md` marker detection (FR-012)
- `api-snapshot.yaml` schema with extracted signatures: `SemanticCheck`, `GateCriteria`, `gate_passed()`, `PipelineConfig`, `Step`, `StepResult`, `GateMode`

**Steps:**
1. **[PLANNING]** Define Phase 0 execution flow: path resolution → API snapshot → collision check → pattern scan → contract emission
2. **[PLANNING]** Identify all 7 API signatures to extract from models.py and gates.py
3. **[EXECUTION]** Implement workflow path resolution: locate command .md, skill SKILL.md, all refs/rules/templates/scripts; abort with AMBIGUOUS_PATH on multiple candidates
4. **[EXECUTION]** Implement live API snapshot: read models.py/gates.py, extract 7 signatures, store as api-snapshot.yaml with SHA-256 content hash
5. **[EXECUTION]** Implement collision check: detect portify-summary.md marker, apply policy (overwrite portified with confirmation, abort on non-portified, abort on main.py name collision)
6. **[VERIFICATION]** Run Phase 0 against a test workflow — verify path resolution succeeds, API snapshot contains all 7 signatures with hash, collision check behaves correctly
7. **[COMPLETION]** Record Phase 0 execution results in D-0014 and API snapshot schema in D-0015

**Acceptance Criteria:**
- Phase 0 resolves workflow path and aborts with AMBIGUOUS_PATH when multiple candidates found
- `api-snapshot.yaml` contains extracted signatures for all 7 API surfaces with SHA-256 content hash
- Collision check correctly distinguishes portified (overwrite OK) from non-portified (abort) directories
- Phase 0 results documented in D-0014/evidence.md with test workflow output

**Validation:**
- Manual check: api-snapshot.yaml parseable as valid YAML with all 7 signature fields present
- Evidence: linkable artifacts produced at D-0014/evidence.md and D-0015/spec.md

**Dependencies:** T02.01, T02.02 (contract schemas for portify-prerequisites.yaml emission)
**Rollback:** Revert Phase 0 implementation
**Notes:** Mitigates RISK-001 (API drift), RISK-003 (unsupported patterns), RISK-008 (name collision), RISK-012 (non-portified collision).

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.04

**Purpose:** Verify contract infrastructure and Phase 0 implementation before proceeding to Phase 1 workflow analysis.
**Checkpoint Report Path:** .dev/releases/current/v2.18-cli-portify-v2/checkpoints/CP-P02-T01-T04.md
**Verification:**
- Contract schemas defined with versioning policy and null-field rules
- Resume semantics validated against synthetic failure scenario
- Phase 0 correctly scans a test workflow and emits valid portify-prerequisites.yaml
**Exit Criteria:**
- All 6 per-phase contract schemas defined and cross-validated
- Synthetic failure resume correctly re-enters at failed phase
- API snapshot contains all 7 required signatures with content hash

---

### T02.05 -- Confirm: T02.06 Tier Classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031, R-032 |
| Why | Tier classification confidence for T02.06 (unsupported-pattern scan) is below threshold; confirm STANDARD tier is appropriate. |
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
- Confirmed tier selection for T02.06

**Steps:**
1. **[PLANNING]** Review T02.06 scope: unsupported-pattern scan and contract emission
2. **[EXECUTION]** Confirm or override STANDARD tier
3. **[COMPLETION]** Record confirmation

**Acceptance Criteria:**
- Tier decision recorded with justification
- T02.06 unblocked for execution
- Override reason documented if changed
- Decision captured in execution log

**Validation:**
- Manual check: tier confirmation recorded
- Evidence: decision captured in execution log

**Dependencies:** None
**Rollback:** N/A

---

### T02.06 -- Implement Phase 0 Unsupported-Pattern Scan and Contract Emission

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031, R-032 |
| Why | Early detection of unsupported patterns (recursive self-orchestration, interactive mid-pipeline decisions, dynamic code gen) prevents wasted analysis investment. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting (pattern detection affects all downstream phases) |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0016/evidence.md

**Deliverables:**
- Unsupported-pattern scanner detecting 4 patterns: recursive agent self-orchestration, interactive human decisions mid-pipeline, no stable artifact boundaries, dynamic code generation/eval
- `portify-prerequisites.yaml` contract emission completing Phase 0 output

**Steps:**
1. **[PLANNING]** Define detection heuristics for each of the 4 unsupported patterns
2. **[PLANNING]** Define portify-prerequisites.yaml emission format per contract schema from T02.02
3. **[EXECUTION]** Implement pattern scanner: scan workflow text for indicators of each unsupported pattern
4. **[EXECUTION]** Implement blocking warning emission on unsupported pattern detection
5. **[EXECUTION]** Implement portify-prerequisites.yaml contract emission with all Phase 0 results
6. **[VERIFICATION]** Test with a workflow containing an unsupported pattern — verify blocking warning emitted and Phase 1 not entered
7. **[COMPLETION]** Record scan results and contract emission verification in D-0016/evidence.md

**Acceptance Criteria:**
- Scanner detects all 4 unsupported patterns when present in test workflow text
- Blocking warning emitted on detection with specific pattern identified
- `portify-prerequisites.yaml` emitted with valid schema on successful scan
- Unsupported pattern in test workflow aborts before Phase 1 entry

**Validation:**
- Manual check: unsupported pattern in test input produces blocking warning and prevents Phase 1
- Evidence: linkable artifact produced at D-0016/evidence.md

**Dependencies:** T02.04 (Phase 0 infrastructure must exist)
**Rollback:** Revert pattern scanner implementation

---

### T02.07 -- Build Component Inventory, Step Decomposition, and Classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033, R-034, R-035, R-036 |
| Why | Phase 1 analysis produces the component inventory and step decomposition that all downstream design and code generation depends on. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | data integrity (conservation invariant), cross-cutting (step IDs used throughout) |
| Tier | STRICT |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0017/evidence.md

**Deliverables:**
- Component inventory engine producing stable `component_id` (C-NNN) identifiers (FR-015)
- Step decomposition engine with stable `source_id` (S-NNN) and conservation invariant enforcement (FR-016, FR-049)
- Step classification engine: pure_programmatic / claude_assisted / hybrid with confidence scoring; flags for user review if confidence < 0.7 (FR-017)

**Steps:**
1. **[PLANNING]** Define component_id (C-NNN) and source_id (S-NNN) assignment algorithm
2. **[PLANNING]** Define conservation invariant equation and enforcement mechanism
3. **[EXECUTION]** Implement component inventory builder with stable C-NNN identifiers
4. **[EXECUTION]** Implement step decomposition with S-NNN identifiers and conservation invariant check
5. **[EXECUTION]** Implement step classification with confidence scoring and user review flagging at < 0.7
6. **[VERIFICATION]** Run against test workflow — verify conservation invariant holds and all steps have classifications
7. **[COMPLETION]** Record inventory, decomposition, and classification results in D-0017/evidence.md

**Acceptance Criteria:**
- Component inventory assigns unique C-NNN IDs to all detected components in test workflow
- Step decomposition assigns unique S-NNN IDs with conservation invariant holding: `|source_steps| == |classified_steps|`
- Classification engine produces pure_programmatic/claude_assisted/hybrid labels with confidence scores
- Steps with confidence < 0.7 flagged for user review

**Validation:**
- Manual check: conservation invariant equation verified for test workflow output
- Evidence: linkable artifact produced at D-0017/evidence.md

**Dependencies:** T02.04 (Phase 0 must successfully scan workflow first)
**Rollback:** Revert component inventory and step decomposition implementations

---

### T02.08 -- Build Dependency DAG, Gate Assignment, and Trailing Gate Safety

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037, R-038, R-039 |
| Why | The dependency DAG determines execution order; gate assignments enforce quality boundaries between steps; trailing gate safety prevents dangerous deferred checks. |
| Effort | L |
| Risk | High |
| Risk Drivers | data integrity (DAG acyclicity), security-adjacent (gate tier assignment, safety escalation) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0018/evidence.md

**Deliverables:**
- Dependency DAG builder with acyclicity validation (FR-018)
- Gate tier assignment engine: EXEMPT/LIGHT/STANDARD/STRICT tiers and BLOCKING/TRAILING modes (FR-019)
- Trailing gate safety escalation logic (FR-020): escalate trailing gates to blocking when safety-critical

**Steps:**
1. **[PLANNING]** Define DAG construction algorithm from step decomposition output
2. **[PLANNING]** Define gate tier assignment criteria and trailing gate safety escalation rules
3. **[EXECUTION]** Implement DAG builder with cycle detection (topological sort — detect and reject cycles)
4. **[EXECUTION]** Implement gate tier assignment using step classification and dependency context
5. **[EXECUTION]** Implement trailing gate safety escalation: detect safety-critical trailing gates and escalate to BLOCKING
6. **[VERIFICATION]** Run against test workflow — verify DAG is acyclic, all gates have tiers assigned, no unsafe trailing gates
7. **[COMPLETION]** Record DAG structure, gate assignments, and safety escalation results in D-0018/evidence.md

**Acceptance Criteria:**
- DAG builder produces acyclic graph for test workflow; cycle detection correctly rejects cyclic inputs
- All steps in DAG have gate tier (EXEMPT/LIGHT/STANDARD/STRICT) and mode (BLOCKING/TRAILING) assigned
- Trailing gate safety escalation correctly identifies and escalates safety-critical trailing gates
- DAG structure and gate assignments documented in D-0018/evidence.md

**Validation:**
- Manual check: topological sort of DAG succeeds with no cycles; gate assignments consistent with step classifications
- Evidence: linkable artifact produced at D-0018/evidence.md

**Dependencies:** T02.07 (step decomposition and classification must exist)
**Rollback:** Revert DAG builder and gate assignment implementations

---

### T02.09 -- Implement Analysis Output, Self-Validation, and Review Gate

| Field | Value |
|---|---|
| Roadmap Item IDs | R-040, R-041, R-042, R-043 |
| Why | Phase 1 analysis output is the primary artifact consumed by Phase 2 design; self-validation ensures internal consistency; user review gate prevents automated propagation of errors. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data integrity (7 self-validation checks), cross-cutting (analysis output consumed by Phase 2) |
| Tier | STRICT |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0019, D-0020 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0019/evidence.md
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0020/spec.md

**Deliverables:**
- Divergence detection for ambiguous step boundaries (FR-050)
- 7 self-validation checks implementation (6 blocking, 1 advisory) (FR-021)
- `portify-analysis.md` output (< 400 lines) and `portify-analysis.yaml` contract emission (FR-022)
- User review gate: present analysis to user, allow classification overrides (FR-023)

**Steps:**
1. **[PLANNING]** Define 7 self-validation check specifications: which are blocking (6) vs advisory (1)
2. **[PLANNING]** Define portify-analysis.md format (< 400 lines) and portify-analysis.yaml schema
3. **[EXECUTION]** Implement divergence detection for ambiguous step boundaries
4. **[EXECUTION]** Implement 7 self-validation checks with blocking/advisory classification
5. **[EXECUTION]** Implement portify-analysis.md and portify-analysis.yaml emission
6. **[EXECUTION]** Implement user review gate: present analysis summary, accept classification overrides
7. **[VERIFICATION]** Run against test workflow — verify all 6 blocking checks pass, analysis output < 400 lines, review gate prompts user
8. **[COMPLETION]** Record validation results in D-0019 and analysis output specification in D-0020

**Acceptance Criteria:**
- All 6 blocking self-validation checks pass for test workflow; advisory check logged
- `portify-analysis.md` is < 400 lines and contains component inventory, step graph, gate assignments
- `portify-analysis.yaml` conforms to per-phase contract schema from T02.02
- User review gate presents analysis and accepts tier classification overrides

**Validation:**
- Manual check: portify-analysis.md line count < 400; portify-analysis.yaml parseable as valid YAML
- Evidence: linkable artifacts produced at D-0019/evidence.md and D-0020/spec.md

**Dependencies:** T02.07, T02.08 (component inventory, DAG, and gates must be built)
**Rollback:** Revert analysis output and validation implementations

---

### T02.10 -- Wire TodoWrite Integration for Phases 0-1

| Field | Value |
|---|---|
| Roadmap Item IDs | R-044, R-045, R-046, R-047 |
| Why | TodoWrite integration provides execution tracking and checkpoint triggering throughout the Phase 0-1 pipeline. |
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
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0021/evidence.md

**Deliverables:**
- 23 subphase task definitions distributed across 5 phases (FR-051)
- Checkpoint trigger implementation: after phase completion, user review gates, before write operations, on failure
- TodoWrite update wiring into Phase 0 and Phase 1 execution flow

**Steps:**
1. **[PLANNING]** Define 23 subphase tasks with descriptions and phase assignments
2. **[PLANNING]** Define checkpoint trigger conditions and their TodoWrite update payloads
3. **[EXECUTION]** Implement subphase task definitions as structured data consumable by TodoWrite
4. **[EXECUTION]** Wire checkpoint triggers into Phase 0 execution flow (after scan, after snapshot, after collision check)
5. **[EXECUTION]** Wire checkpoint triggers into Phase 1 execution flow (after inventory, after DAG, after validation, after review)
6. **[VERIFICATION]** Run Phase 0 and Phase 1 — verify TodoWrite tasks created and checkpoints triggered at correct points
7. **[COMPLETION]** Record TodoWrite integration verification in D-0021/evidence.md

**Acceptance Criteria:**
- 23 subphase tasks defined with phase assignments covering all 5 phases
- Checkpoint triggers fire after phase completion, at user review gates, before write operations, and on failure
- TodoWrite updates visible during Phase 0 and Phase 1 execution
- Task count verified: exactly 23 subphase tasks defined

**Validation:**
- Manual check: run Phase 0-1 pipeline and verify TodoWrite task creation and checkpoint triggering
- Evidence: linkable artifact produced at D-0021/evidence.md

**Dependencies:** T02.04 through T02.09 (Phase 0-1 implementation must exist for wiring)
**Rollback:** Revert TodoWrite integration hooks

---

### Checkpoint: End of Phase 2

**Purpose:** Gate Phase 3 entry by confirming contract infrastructure, Phase 0, and Phase 1 implementations are complete and validated.
**Checkpoint Report Path:** .dev/releases/current/v2.18-cli-portify-v2/checkpoints/CP-P02-END.md
**Verification:**
- Contract schemas defined with versioning policy and resume semantics validated against synthetic failure
- Phase 0 correctly scans a test workflow and emits valid portify-prerequisites.yaml
- Phase 1 produces valid portify-analysis.yaml with conservation invariant holding
**Exit Criteria:**
- Resume from Phase 0 failure correctly re-enters Phase 0 without re-executing nothing
- Unsupported pattern in test workflow aborts before Phase 1 analysis begins
- All 7 Phase 1 self-validation checks pass for test workflow (6 blocking + 1 advisory)
