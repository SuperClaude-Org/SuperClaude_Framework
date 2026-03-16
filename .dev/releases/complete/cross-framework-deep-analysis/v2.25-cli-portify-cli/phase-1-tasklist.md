# Phase 1 -- Architecture Confirmation

Confirm design assumptions before coding to avoid rework on contract-critical areas. Resolve open questions that materially affect interfaces. Establish architecture baseline. This phase blocks all implementation phases.

### T01.01 -- Validate Target Architecture and Confirm Base Type Imports

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001, R-002 |
| Why | Framework base types (PipelineConfig, Step, StepResult, GateCriteria, GateMode, SemanticCheck) must be importable and stable before domain model work begins. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | architecture, system-wide, depends |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0001/notes.md

**Deliverables:**
- Architecture validation notes documenting import paths and API stability for all 6 base types

**Steps:**
1. **[PLANNING]** Load existing SuperClaude CLI framework structure; identify `src/superclaude/` module layout
2. **[PLANNING]** Check that PipelineConfig, Step, StepResult, GateCriteria, GateMode, SemanticCheck are locatable in the codebase
3. **[EXECUTION]** Attempt Python import of each base type; record module path and version
4. **[EXECUTION]** Document the public interface contract for each base type (methods, fields, signatures)
5. **[EXECUTION]** Identify any unstable or deprecated APIs that would affect domain model inheritance
6. **[VERIFICATION]** Verify all 6 base types import without error via `uv run python -c "from superclaude... import ..."`
7. **[COMPLETION]** Write architecture validation notes to D-0001/notes.md

**Acceptance Criteria:**
- All 6 base types (PipelineConfig, Step, StepResult, GateCriteria, GateMode, SemanticCheck) import successfully via `uv run python -c` with zero errors
- No deprecated or unstable APIs identified in base type public interfaces that would break domain model extension
- Import paths and interface contracts documented with specific module locations
- Architecture validation notes written to .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0001/notes.md

**Validation:**
- Manual check: `uv run python -c "from superclaude.<module> import PipelineConfig, Step, StepResult, GateCriteria, GateMode, SemanticCheck"` exits 0
- Evidence: linkable artifact produced at D-0001/notes.md

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Critical path item per roadmap — D-008 dependency. Must complete before Phase 3 domain model work.

---

### T01.02 -- Resolve Contract-Affecting Blocking Open Questions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003, R-004 |
| Why | 5 blocking OQs (OQ-001, OQ-003, OQ-004, OQ-009, OQ-011) materially affect interfaces; unresolved questions cause rework in Phases 2-3. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | architecture, system-wide, blocked |
| Tier | STRICT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0002/spec.md

**Deliverables:**
- Open question resolution list with blocking/non-blocking classification for all 14 OQs, with binding answers for OQ-001, OQ-003, OQ-004, OQ-009, OQ-011

**Steps:**
1. **[PLANNING]** Enumerate all 14 open questions from roadmap with their blocking classification
2. **[PLANNING]** Identify which OQs have cross-phase dependencies (OQ-002 affects process.py Phase 2, OQ-013 affects executor Phase 2)
3. **[EXECUTION]** Resolve OQ-001 (TurnLedger semantics): define what constitutes "one turn"
4. **[EXECUTION]** Resolve OQ-003 (phase_contracts schema), OQ-004 (api_snapshot_hash algorithm), OQ-009 (failure_type enum values), OQ-011 (--debug flag behavior)
5. **[EXECUTION]** Assess OQ-002 (kill signal mechanism) and OQ-013 (PASS_NO_SIGNAL retry) as potential additional blockers
6. **[VERIFICATION]** Verify all 5 mandatory blocking OQs have concrete, implementable answers with no ambiguity
7. **[COMPLETION]** Write resolution list to D-0002/spec.md with blocking/non-blocking classification

**Acceptance Criteria:**
- All 5 contract-affecting OQs (OQ-001, OQ-003, OQ-004, OQ-009, OQ-011) have concrete resolutions documented in D-0002/spec.md
- OQ-002 and OQ-013 assessed with blocking/non-blocking determination recorded
- Each resolution includes the specific data types, enum values, or behavioral rules that downstream phases will implement
- Resolution list written to .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0002/spec.md

**Validation:**
- Manual check: each of the 5 blocking OQ resolutions provides an implementable answer (no "TBD" or "to be decided")
- Evidence: linkable artifact produced at D-0002/spec.md

**Dependencies:** T01.01
**Rollback:** TBD (if not specified in roadmap)

---

### T01.03 -- Confirm Prompt Splitting, Overwrite Rules, and Non-Blocking OQs

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005, R-006, R-007 |
| Why | Prompt splitting threshold location and overwrite marker rules affect multiple downstream phases; OQ-007 and OQ-014 must be documented as non-blocking. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0003/notes.md

**Deliverables:**
- Design decision confirmations for prompt splitting location, overwrite marker rules, and non-blocking OQ documentation

**Steps:**
1. **[PLANNING]** Review executor vs. prompt builder boundary for prompt splitting threshold
2. **[PLANNING]** Review existing `Generated by` / `Portified from` marker conventions in codebase
3. **[EXECUTION]** Decide prompt splitting threshold location (executor vs. prompt builder) and document rationale
4. **[EXECUTION]** Confirm overwrite rules: only overwrite modules containing `Generated by` / `Portified from` in `__init__.py`
5. **[EXECUTION]** Document OQ-007 (agent discovery warning behavior) and OQ-014 (workdir cleanup policy) as non-blocking for their respective phases
6. **[VERIFICATION]** Verify decisions are consistent with Phase 6 (synthesis) and Phase 9 (CLI integration) requirements
7. **[COMPLETION]** Write decision confirmations to D-0003/notes.md

**Acceptance Criteria:**
- Prompt splitting threshold location decided as either executor or prompt builder with documented rationale in D-0003/notes.md
- Overwrite rules confirmed with specific marker strings (`Generated by` / `Portified from`) and file location (`__init__.py`)
- OQ-007 and OQ-014 documented as non-blocking with phase assignments
- Decision notes written to .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0003/notes.md

**Validation:**
- Manual check: each decision is unambiguous and references the downstream phases it affects
- Evidence: linkable artifact produced at D-0003/notes.md

**Dependencies:** T01.01
**Rollback:** TBD (if not specified in roadmap)

---

### T01.04 -- Produce Architecture Baseline Package

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008, R-009, R-010, R-011 |
| Why | Consolidate Phase 0 outputs into a reviewable baseline package that gates entry to implementation phases. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0004/spec.md

**Deliverables:**
- Architecture baseline package containing: architecture decision notes, finalized interface assumptions, open question resolution list, updated implementation checklist

**Steps:**
1. **[PLANNING]** Collect outputs from T01.01, T01.02, T01.03
2. **[PLANNING]** Identify any gaps between resolved OQs and implementation checklist requirements
3. **[EXECUTION]** Assemble architecture decision notes from T01.01 validation results
4. **[EXECUTION]** Compile finalized interface assumptions with verified import paths
5. **[EXECUTION]** Consolidate open question resolution list with blocking/non-blocking classifications
6. **[EXECUTION]** Update implementation checklist reflecting Phase 0 decisions, resolved OQs, and confirmed architecture assumptions
7. **[COMPLETION]** Write consolidated architecture baseline to D-0004/spec.md

**Acceptance Criteria:**
- Architecture baseline document at D-0004/spec.md contains all 4 deliverable sections: decision notes, interface assumptions, OQ resolution, implementation checklist
- All contract-affecting blocking OQs marked as resolved with implementable answers
- No blocking unknowns remain for Phase 2-3 core module implementation
- Document written to .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0004/spec.md

**Validation:**
- Manual check: architecture baseline reviewed and no blocking unknowns identified
- Evidence: linkable artifact produced at D-0004/spec.md

**Dependencies:** T01.01, T01.02, T01.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 1

**Purpose:** Verify architecture baseline is approved, all contract-affecting blocking OQs are resolved, and no blocking unknowns remain for implementation phases.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P01-END.md

**Verification:**
- All 6 framework base types import successfully with documented interface contracts
- All 5 contract-affecting blocking OQs (OQ-001, OQ-003, OQ-004, OQ-009, OQ-011) have concrete resolutions
- Architecture baseline package (D-0004) contains all required sections with no TBD entries

**Exit Criteria:**
- Milestone M0 satisfied: architecture baseline approved; contract-affecting blocking OQs resolved
- All 4 tasks (T01.01-T01.04) completed with deliverables D-0001 through D-0004 produced
- No blocking unknowns remain for Phase 2 (Prerequisites) or Phase 3 (Core Pipeline)
