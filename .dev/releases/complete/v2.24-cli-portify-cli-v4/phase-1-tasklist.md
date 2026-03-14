# Phase 1 -- Architecture Confirmation

Resolve blocking spec ambiguities and lock module layout before code changes. This lightweight phase has asymmetric payoff: a small upfront investment prevents costly rework when late-phase decisions force model changes that ripple backward.

### T01.01 -- Resolve Blocking Spec Ambiguities

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | Timeout semantics, resume behavior, and scoring precision must have concrete answers before implementation begins to prevent rework. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0001/spec.md

**Deliverables:**
1. Decision record documenting resolution of: (a) per-iteration independent timeout vs total divided by `max_convergence`, (b) resume behavior for partially written `synthesize-spec` (re-run vs skip), (c) scoring precision and 7.0 boundary rounding behavior, (d) authoritative module layout confirmation (18-module per DEV-001)

**Steps:**
1. **[PLANNING]** Load roadmap Section "Phase 0" and identify the 4 blocking ambiguities listed
2. **[PLANNING]** Check if DEV-001 accepted deviation document exists and extract its module layout decision
3. **[EXECUTION]** Draft decision for timeout semantics: per-iteration independent timeout (default 300s) as stated in roadmap Phase 5
4. **[EXECUTION]** Draft decision for resume behavior: prefer re-running `synthesize-spec` over trusting partially gated output as stated in roadmap Phase 4
5. **[EXECUTION]** Draft decision for scoring precision: 7.0 boundary (7.0 true, 6.9 false) as stated in SC-009
6. **[EXECUTION]** Draft decision for module layout: 18-module structure per DEV-001 confirmation
7. **[VERIFICATION]** Review decision record to confirm all 4 ambiguities have concrete answers with blocking-phase annotations
8. **[COMPLETION]** Write decision record to `D-0001/spec.md` with per-question `[Blocking Phase N]` or `[Advisory]` annotations

**Acceptance Criteria:**
- File `.dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0001/spec.md` exists and contains resolutions for all 4 ambiguities
- Each decision includes rationale derived from roadmap text or DEV-001
- Each decision is triaged as (1) must-resolve, (2) safe defaults, or (3) defer-to-follow-up, with `[Blocking Phase N]` or `[Advisory]` annotations
- Decision record is referenced in subsequent phase tasks

**Validation:**
- Manual check: decision record contains 4 resolution entries with blocking-phase annotations
- Evidence: linkable artifact produced at D-0001/spec.md

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Roadmap explicitly provides answers for most ambiguities; this task documents them formally.

---

### T01.02 -- Freeze 18-Module Architecture with Ownership Boundaries

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | The 18-module `cli_portify/` structure must be confirmed and ownership boundaries defined before any code is written. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0002/spec.md

**Deliverables:**
1. Final module map for `src/superclaude/cli/cli_portify/` with 18 modules listed, each assigned to an ownership boundary: config/model layer, step implementations, process wrapper, monitor/logging, contract emission, CLI integration

**Steps:**
1. **[PLANNING]** Load roadmap Section 4.1 (18 modules) and Section 4.6 (13 files) references
2. **[PLANNING]** Confirm DEV-001 resolves the conflict in favor of 18-module structure
3. **[EXECUTION]** List all 18 modules with their filenames under `src/superclaude/cli/cli_portify/`
4. **[EXECUTION]** Assign each module to one of the 6 ownership boundaries from roadmap
5. **[VERIFICATION]** Verify module count equals 18 and all 6 ownership categories are represented
6. **[COMPLETION]** Write final module map to `D-0002/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0002/spec.md` exists with exactly 18 module entries
- Each module is assigned to exactly one ownership boundary
- All 6 ownership categories (config/model, step implementations, process wrapper, monitor/logging, contract emission, CLI integration) have at least one module
- Module map is consistent with roadmap Section 4.1

**Validation:**
- Manual check: module map contains 18 entries covering 6 ownership boundaries
- Evidence: linkable artifact produced at D-0002/spec.md

**Dependencies:** T01.01
**Rollback:** TBD (if not specified in roadmap)

---

### T01.03 -- Define Artifact Contract for Output Names and Locations

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | Standardizing output artifact names, locations, and frontmatter rules prevents integration issues in later phases. |
| Effort | XS |
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
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0003/spec.md

**Deliverables:**
1. Step/artifact interface table defining: output artifact names (`validate-config-result.json`, `component-inventory.md`, `portify-analysis.md`, `portify-spec.md`, synthesized release spec, brainstorm findings, `panel-report.md`, return contract, NDJSON logs), frontmatter parsing/validation behavior, failure/default population rules for contracts

**Steps:**
1. **[PLANNING]** Collect all 9 artifact outputs listed in roadmap "Artifact Outputs" section
2. **[PLANNING]** Identify frontmatter requirements from each step description
3. **[EXECUTION]** Define naming convention, output directory location, and expected format for each artifact
4. **[EXECUTION]** Define frontmatter parsing rules and validation behavior
5. **[EXECUTION]** Define failure/default population rules per NFR-009
6. **[VERIFICATION]** Cross-reference artifact names against step descriptions in Phases 2-5
7. **[COMPLETION]** Write artifact contract to `D-0003/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0003/spec.md` exists and covers all 9 artifact outputs from roadmap
- Each artifact has defined: filename, directory, format, frontmatter schema
- Failure/default population rules specified for contract objects per NFR-009
- Artifact names match those used in roadmap step descriptions

**Validation:**
- Manual check: all 9 artifacts from roadmap Section "Artifact Outputs" have entries
- Evidence: linkable artifact produced at D-0003/spec.md

**Dependencies:** T01.01
**Rollback:** TBD (if not specified in roadmap)

---

### T01.04 -- Define Minimal Signal Vocabulary Constants

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | Signal vocabulary constants must be defined before Phase 3 monitoring implementation to ensure consistent event logging. |
| Effort | XS |
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
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0004/spec.md

**Deliverables:**
1. Signal vocabulary constants definition: `step_start`, `step_complete`, `step_error`, `step_timeout`, `gate_pass`, `gate_fail` with note that vocabulary extends during Phase 4 when subprocess behavior is understood

**Steps:**
1. **[PLANNING]** Load roadmap Phase 0 work item 4 for signal vocabulary requirements
2. **[PLANNING]** Identify extension points noted for Phase 3
3. **[EXECUTION]** Define 6 initial signal constants with string values and usage context
4. **[EXECUTION]** Document extension policy: vocabulary extends during Phase 4 (subprocess orchestration) when subprocess behavior is understood
5. **[VERIFICATION]** Verify all 6 constants from roadmap are defined
6. **[COMPLETION]** Write signal vocabulary to `D-0004/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/v2.24-cli-portify-cli-v4/artifacts/D-0004/spec.md` exists with exactly 6 signal constants
- Constants match roadmap: `step_start`, `step_complete`, `step_error`, `step_timeout`, `gate_pass`, `gate_fail`
- Extension policy for Phase 4 documented
- Constants are referenced by Phase 4 monitoring implementation (T04.03)

**Validation:**
- Manual check: 6 constants defined matching roadmap specification
- Evidence: linkable artifact produced at D-0004/spec.md

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 1

**Purpose:** Verify all architecture decisions are recorded and the implementation foundation is locked before code changes begin.
**Checkpoint Report Path:** .dev/releases/current/v2.24-cli-portify-cli-v4/checkpoints/CP-P01-END.md
**Verification:**
- All 4 blocking ambiguities have documented resolutions with blocking-phase annotations
- 18-module architecture map is frozen with ownership boundaries
- Artifact contract covers all 9 output artifacts from roadmap
**Exit Criteria:**
- Decision record (D-0001) produced with per-question blocking-phase annotations
- Final module map (D-0002) confirms 18-module structure
- Signal vocabulary (D-0004) defines 6 initial constants
