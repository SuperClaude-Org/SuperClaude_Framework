# Phase 4 -- Gate System

Create the enforcement system that prevents low-quality or structurally invalid artifacts from propagating. Implement all 12 gates with complete per-gate check mapping.

### T04.01 -- Implement All 12 Gates (G-000 through G-011) in gates.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-049, R-052 |
| Why | FR-045 and FR-046 require all 12 gates with frontmatter field checks, minimum line counts, STANDARD/STRICT tier assignment, and GateMode.BLOCKING enforcement. |
| Effort | XL |
| Risk | High |
| Risk Drivers | system-wide, end-to-end |
| Tier | STRICT |
| Confidence | [█████████░] 92% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0024/spec.md

**Deliverables:**
- `src/superclaude/cli/cli_portify/gates.py` with all 12 gate implementations (G-000 through G-011) including per-gate semantic checks, tier assignment, and GateMode.BLOCKING enforcement

**Steps:**
1. **[PLANNING]** Map per-gate check requirements from roadmap gate mapping table (G-000 through G-011)
2. **[PLANNING]** Review GateCriteria and GateMode base types from T01.01 for inheritance contract
3. **[EXECUTION]** Implement G-000 (has_valid_yaml_config), G-001 (has_component_inventory), G-002 (EXIT_RECOMMENDATION)
4. **[EXECUTION]** Implement G-003 (EXIT_RECOMMENDATION + has_required_analysis_sections), G-004 (has_approval_status), G-005 (EXIT_RECOMMENDATION)
5. **[EXECUTION]** Implement G-006 (return type pattern), G-007 (EXIT_RECOMMENDATION), G-008 (EXIT_RECOMMENDATION + step-count consistency)
6. **[EXECUTION]** Implement G-009 (has_approval_status), G-010 (EXIT_RECOMMENDATION + has_zero_placeholders + has_brainstorm_section), G-011 (has_quality_scores + has_criticals_addressed)
7. **[VERIFICATION]** Write unit tests: each gate passes with valid input and fails with invalid input; tier assignments correct
8. **[COMPLETION]** Document per-gate check mapping in D-0024/spec.md

**Acceptance Criteria:**
- All 12 gates (G-000 through G-011) implemented in `gates.py` with correct semantic checks per roadmap gate mapping table
- Each gate has STANDARD or STRICT tier assignment and uses GateMode.BLOCKING enforcement
- G-010 validates zero `{{SC_PLACEHOLDER:*}}` sentinels and Section 12 brainstorm presence
- G-011 validates quality scores (clarity, completeness, testability, consistency, overall) and all CRITICAL findings marked [INCORPORATED] or [DISMISSED]
- Gate retry logic correctly distinguishes PASS_NO_SIGNAL (triggers retry — result file present, no EXIT_RECOMMENDATION) from PASS_NO_REPORT (no retry — treated as passing outcome) per roadmap retry semantics note

**Validation:**
- `uv run pytest tests/ -k "test_gates"` exits 0 with passing and failing input tests for all 12 gates
- Evidence: linkable artifact produced at D-0024/spec.md

**Dependencies:** T03.01, T03.06
**Rollback:** TBD (if not specified in roadmap)
**Notes:** XL effort — roadmap notes G-000 through G-005 and G-006 through G-011 can be parallelized by separate engineers.

---

### T04.02 -- Implement Semantic Check Functions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-050 |
| Why | FR-047 and AC-004 require semantic check functions returning tuple[bool, str] for reusable validation across gates. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide (reused across gates) |
| Tier | STRICT |
| Confidence | [████████░░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0025/spec.md

**Deliverables:**
- Semantic check helper functions returning `tuple[bool, str]`: has_valid_yaml_config, has_component_inventory, has_required_analysis_sections, has_approval_status, has_zero_placeholders, has_brainstorm_section, has_quality_scores, has_criticals_addressed

**Steps:**
1. **[PLANNING]** Enumerate all distinct semantic checks referenced by gates G-000 through G-011
2. **[PLANNING]** Define return contract: `tuple[bool, str]` where str is diagnostic message on failure
3. **[EXECUTION]** Implement `has_valid_yaml_config()`: validates YAML with required fields (workflow_path, cli_name, output_dir)
4. **[EXECUTION]** Implement remaining semantic checks: has_component_inventory, has_required_analysis_sections, has_approval_status, has_zero_placeholders, has_brainstorm_section, has_quality_scores, has_criticals_addressed
5. **[VERIFICATION]** Write unit tests: each check returns (True, "") on valid input and (False, "<diagnostic>") on invalid input
6. **[COMPLETION]** Document semantic check catalog in D-0025/spec.md

**Acceptance Criteria:**
- All semantic check functions return `tuple[bool, str]` per FR-047 and AC-004
- `has_required_analysis_sections` checks for: Source Components, Step Graph, Parallel Groups, Gates Summary, Data Flow, Classifications, Recommendations
- `has_zero_placeholders` scans for `{{SC_PLACEHOLDER:*}}` sentinels and returns False with placeholder names on any match
- Semantic check catalog documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0025/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_semantic_checks"` exits 0
- Evidence: linkable artifact produced at D-0025/spec.md

**Dependencies:** T04.01
**Rollback:** TBD (if not specified in roadmap)

---

### T04.03 -- Implement Gate Diagnostics Formatting

| Field | Value |
|---|---|
| Roadmap Item IDs | R-051 |
| Why | Gate failures must produce well-formatted diagnostic output for debugging. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0026/spec.md

**Deliverables:**
- Gate diagnostics formatter producing structured failure reports with gate ID, check name, diagnostic message, and remediation guidance

**Steps:**
1. **[PLANNING]** Define diagnostics output format: gate ID, failed check name, diagnostic message, suggested fix
2. **[PLANNING]** Review how diagnostics integrate with execution log and TUI display
3. **[EXECUTION]** Implement diagnostics formatter consuming semantic check `tuple[bool, str]` results
4. **[EXECUTION]** Format output for both machine-readable (JSONL) and human-readable (markdown) logging
5. **[VERIFICATION]** Write unit tests: diagnostics formatter produces correct output for gate failures
6. **[COMPLETION]** Document diagnostics format in D-0026/spec.md

**Acceptance Criteria:**
- Gate diagnostics formatter produces structured output with: gate ID, failed check name, diagnostic message from semantic check, remediation guidance
- Output formats compatible with both execution-log.jsonl (machine) and execution-log.md (human)
- Diagnostics are deterministic and well-diagnosed per roadmap requirement
- Diagnostics format documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0026/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_gate_diagnostics"` exits 0
- Evidence: linkable artifact produced at D-0026/spec.md

**Dependencies:** T04.01, T04.02
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 4

**Purpose:** Verify all 12 gates validate correctly against synthetic test data; gate failures are deterministic, well-diagnosed, and block invalid outputs.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P04-END.md

**Verification:**
- All 12 gates (G-000 through G-011) pass with valid test data and fail with invalid test data
- Semantic check functions return correct tuple[bool, str] for all implemented checks
- Gate diagnostics produce structured, actionable failure reports

**Exit Criteria:**
- Milestone M3 satisfied: all 12 gates validate correctly; gate failures are deterministic and well-diagnosed
- All 3 tasks (T04.01-T04.03) completed with deliverables D-0024 through D-0026 produced
- Super-milestone A (Foundations) complete: roadmap Phases 0-3 / tasklist Phases 1-4 done
