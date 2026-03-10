# Phase 3 -- Protocol Design

Implement the specification/design phase of the protocol — step graph mapping with coverage invariants, domain-specific model and gate design with API conformance verification, prompt/executor design, and self-validation. This phase produces `portify-spec.yaml`, the primary input to code generation.

---

### T03.01 -- Implement Step Mapping with Coverage Invariant Enforcement

| Field | Value |
|---|---|
| Roadmap Item IDs | R-050, R-051, R-052, R-053 |
| Why | Source-to-generated step mapping with coverage invariant enforcement ensures no analysis steps are lost or duplicated during the design transformation. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data integrity (coverage invariant equation), cross-cutting (step mapping consumed by code generation) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0022/spec.md

**Deliverables:**
- Source-to-generated step mapping engine supporting 1:1, 1:N, N:1, and 1:0 (elimination) mappings with justification per mapping (FR-024)
- Coverage invariant enforcement: `|source_step_registry| == |mapped_steps| + |elimination_records|` (FR-025, FR-049)
- Elimination record structure: source_id, reason, approved_by fields

**Steps:**
1. **[PLANNING]** Define mapping types (1:1, 1:N, N:1, 1:0) with justification requirements per type
2. **[PLANNING]** Define coverage invariant equation and violation detection logic
3. **[EXECUTION]** Implement step mapping engine that records mapping type and justification for each source-to-generated pair
4. **[EXECUTION]** Implement elimination record generation for 1:0 mappings with required fields (source_id, reason, approved_by)
5. **[EXECUTION]** Implement coverage invariant enforcement: compute equation after mapping, halt on violation
6. **[VERIFICATION]** Run against Phase 1 analysis output — verify invariant holds: source count = mapped count + eliminated count
7. **[COMPLETION]** Record step mapping specification and invariant verification in D-0022/spec.md

**Acceptance Criteria:**
- Step mapping engine correctly records all 4 mapping types (1:1, 1:N, N:1, 1:0) with justifications
- Coverage invariant `|source_step_registry| == |mapped_steps| + |elimination_records|` verified for test workflow
- All elimination records contain non-empty source_id, reason, and approved_by fields
- Step mapping specification documented in D-0022/spec.md

**Validation:**
- Manual check: coverage invariant equation holds for test workflow output
- Evidence: linkable artifact produced at D-0022/spec.md

**Dependencies:** T02.09 (Phase 1 analysis output provides source step registry)
**Rollback:** Revert step mapping engine implementation

---

### T03.02 -- Design Domain Models, Gates, and API Conformance Verification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-054, R-055, R-056, R-057 |
| Why | Domain-specific dataclass models and gate designs must extend the live API correctly; API conformance verification prevents drift-induced generation errors. |
| Effort | L |
| Risk | High |
| Risk Drivers | data/schema (model extension, gate fields), security-adjacent (API conformance, drift detection) |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes (models/ path) |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0023/spec.md

**Deliverables:**
- Domain-specific dataclass model designs extending `PipelineConfig` and `StepResult` with Config, Result, Status enum, Monitor state with NDJSON signals (FR-026); TurnLedger integration per OQ-002 resolution
- Gate designs using live `GateCriteria` fields: `required_frontmatter_fields`, `min_lines`, `enforcement_tier`, `semantic_checks` with `Callable[[str], bool]` signature (FR-028)
- API conformance verification against Phase 0 api-snapshot.yaml hash (RISK-001 mitigation)

**Steps:**
1. **[PLANNING]** Read Phase 0 api-snapshot.yaml to capture current API surface for conformance checking
2. **[PLANNING]** Review OQ-002 resolution from decisions.yaml for TurnLedger integration decision
3. **[EXECUTION]** Design domain dataclass models extending PipelineConfig and StepResult with domain-specific fields
4. **[EXECUTION]** Design gate definitions using live GateCriteria fields with Callable[[str], bool] semantic check signature
5. **[EXECUTION]** Implement API conformance verification: compare designed models/gates against api-snapshot.yaml hash; halt on drift
6. **[VERIFICATION]** Verify all designed models extend correct base classes and all gate definitions use valid GateCriteria field names
7. **[COMPLETION]** Record model designs, gate definitions, and conformance results in D-0023/spec.md

**Acceptance Criteria:**
- All domain models extend `PipelineConfig` or `StepResult` base classes with valid field types
- All gate designs reference correct `GateCriteria` field names from api-snapshot.yaml
- All semantic check functions use `Callable[[str], bool]` signature exclusively
- API conformance verification passes: snapshot hash matches, no drift detected

**Validation:**
- Manual check: model and gate designs cross-referenced against api-snapshot.yaml field names — zero mismatches
- Evidence: linkable artifact produced at D-0023/spec.md

**Dependencies:** T03.01 (step mapping provides the design input), T02.04 (api-snapshot.yaml from Phase 0)
**Rollback:** Revert model and gate design artifacts
**Notes:** Mitigates RISK-001 (live API drift). TurnLedger integration depends on OQ-002 resolution.

---

### T03.03 -- Design Prompts, Executor, and Pattern Coverage Matrix

| Field | Value |
|---|---|
| Roadmap Item IDs | R-058, R-059, R-060, R-061, R-062 |
| Why | Prompt design governs Claude-assisted step quality; executor design determines runtime behavior; pattern coverage matrix ensures no required patterns are missed. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | cross-cutting (prompts/executor affect all generated pipelines), performance (executor ThreadPoolExecutor design) |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0024/spec.md

**Deliverables:**
- Prompt templates for Claude-assisted steps: input strategy, output sections, frontmatter fields, machine-readable markers; split to `portify-prompts.md` if > 300 lines (FR-027)
- Pure-programmatic step implementation designs as full Python code specifications (FR-029)
- Executor design: sprint-style synchronous supervisor with `ThreadPoolExecutor` for parallel steps (FR-030)
- Pattern coverage matrix verifying all 7 supported patterns covered; abort on gap (FR-031)

**Steps:**
1. **[PLANNING]** Enumerate all 7 supported patterns from roadmap specification
2. **[PLANNING]** Identify Claude-assisted vs pure-programmatic steps from Phase 1 classification
3. **[EXECUTION]** Design prompt templates with input strategy, output sections, frontmatter fields, and machine-readable markers
4. **[EXECUTION]** Design pure-programmatic step implementations as Python code specifications
5. **[EXECUTION]** Design executor: synchronous supervisor loop with ThreadPoolExecutor for independent step groups
6. **[EXECUTION]** Build pattern coverage matrix: map each of 7 patterns to covering step designs; identify gaps
7. **[VERIFICATION]** Verify pattern coverage matrix shows 100% coverage for test workflow patterns; no gaps detected
8. **[COMPLETION]** Record prompt templates, executor design, and coverage matrix in D-0024/spec.md

**Acceptance Criteria:**
- Prompt templates defined for all Claude-assisted steps with input/output/frontmatter specifications
- Executor design specifies synchronous supervisor with ThreadPoolExecutor integration
- Pattern coverage matrix shows 100% coverage of all 7 supported patterns for test workflow
- If prompts exceed 300 lines, they are split to separate `portify-prompts.md` file

**Validation:**
- Manual check: pattern coverage matrix has no gaps; all 7 patterns have at least one covering step design
- Evidence: linkable artifact produced at D-0024/spec.md

**Dependencies:** T03.01, T03.02 (step mapping and model designs inform prompt and executor design)
**Rollback:** Revert prompt, executor, and coverage matrix design artifacts

---

### T03.04 -- Confirm: T03.05 Tier Classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-063, R-064, R-065 |
| Why | Tier classification confidence for T03.05 (self-validation and portify-spec.yaml emission) requires confirmation. |
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
- Confirmed tier selection for T03.05

**Steps:**
1. **[PLANNING]** Review T03.05 scope: 8 self-validation checks and portify-spec.yaml emission
2. **[EXECUTION]** Confirm or override STRICT tier (self-validation with blocking checks suggests STRICT)
3. **[COMPLETION]** Record confirmation

**Acceptance Criteria:**
- Tier decision recorded with justification
- T03.05 unblocked for execution
- Override reason documented if changed
- Decision captured in execution log

**Validation:**
- Manual check: tier confirmation recorded
- Evidence: decision captured in execution log

**Dependencies:** None
**Rollback:** N/A

---

### T03.05 -- Implement Phase 2 Self-Validation and Emit portify-spec.yaml

| Field | Value |
|---|---|
| Roadmap Item IDs | R-063, R-064, R-065, R-066 |
| Why | Phase 2 self-validation ensures design consistency before code generation; portify-spec.yaml is the primary input to Phase 3 code generation. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data integrity (8 self-validation checks, 7 blocking), cross-cutting (spec consumed by code generation) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0025, D-0026 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0025/spec.md
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0026/evidence.md

**Deliverables:**
- 8 self-validation checks implementation (7 blocking, 1 advisory) (FR-032)
- `portify-spec.yaml` emission with step_mapping, module_plan, gate_definitions, pattern_coverage, api_conformance fields (FR-033)
- User approval gate before Phase 3 code generation begins

**Steps:**
1. **[PLANNING]** Define 8 self-validation check specifications: which are blocking (7) vs advisory (1)
2. **[PLANNING]** Define portify-spec.yaml schema per contract from T02.02
3. **[EXECUTION]** Implement 8 self-validation checks verifying step mapping consistency, model validity, gate correctness, coverage completeness
4. **[EXECUTION]** Implement portify-spec.yaml emission with all required fields
5. **[EXECUTION]** Implement user approval gate: present spec summary, require explicit approval before Phase 3
6. **[VERIFICATION]** Run against test workflow — verify all 7 blocking checks pass, spec YAML is valid, approval gate prompts user
7. **[COMPLETION]** Record validation results in D-0025 and spec YAML content in D-0026

**Acceptance Criteria:**
- All 7 blocking self-validation checks pass for test workflow; advisory check logged
- `portify-spec.yaml` contains step_mapping, module_plan, gate_definitions, pattern_coverage, api_conformance fields
- `portify-spec.yaml` parseable as valid YAML conforming to contract schema
- User approval gate blocks Phase 3 entry until explicit approval received

**Validation:**
- Manual check: portify-spec.yaml parseable as valid YAML with all required fields present
- Evidence: linkable artifacts produced at D-0025/spec.md and D-0026/evidence.md

**Dependencies:** T03.01, T03.02, T03.03 (all design tasks must complete before validation)
**Rollback:** Revert self-validation and spec emission implementations

---

### Checkpoint: End of Phase 3

**Purpose:** Gate Phase 4 (code generation) entry by confirming all design artifacts are consistent, complete, and approved.
**Checkpoint Report Path:** .dev/releases/current/v2.18-cli-portify-v2/checkpoints/CP-P03-END.md
**Verification:**
- portify-spec.yaml produced from test workflow with valid step mapping and module plan
- Coverage invariant holds: |source_step_registry| == |mapped_steps| + |elimination_records|
- All gate designs reference correct GateCriteria field names from API snapshot
**Exit Criteria:**
- Pattern coverage matrix shows 100% coverage for test workflow patterns
- All 7 blocking Phase 2 self-validation checks pass
- User approval gate confirms design before code generation
