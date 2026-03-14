# Phase 2 -- Component Inventory and Mapping

Establish the canonical component truth source by performing Auggie MCP discovery across both repositories and producing a verified cross-framework mapping. All downstream phases depend on this inventory; discoveries made in later phases must be flagged as inventory gaps, not silently absorbed.

---

### T02.01 -- Auggie MCP Discovery for IronClaude 8 Component Groups

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | The IC component inventory is the foundation for all comparison, strategy, and improvement artifacts; must be evidence-backed with verified file paths |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data, analysis (broad Auggie queries required; stale paths possible) |
| Tier | STRICT |
| Confidence | [████████--] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0008/spec.md`
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0008/evidence.md`

**Deliverables:**
- D-0008: IC component inventory document at `artifacts/D-0008/spec.md` covering all 8 groups with verified file paths, exposed interfaces, internal dependencies, and extension points

**Steps:**
1. **[PLANNING]** Load context: identify the 8 IC component groups from roadmap (roadmap pipeline, cleanup-audit CLI, sprint executor, PM agent, adversarial pipeline, task-unified tier system, quality agents, pipeline analysis subsystem)
2. **[PLANNING]** Check dependencies: confirm Auggie MCP is available (from D-0001); if fallback active, note all results as fallback-derived
3. **[EXECUTION]** Execute Auggie MCP `codebase-retrieval` query against `/config/workspace/IronClaude` for each of the 8 component groups
4. **[EXECUTION]** For each component, record: verified file paths (`file:line` format), exposed interfaces, internal dependencies, extension points
5. **[EXECUTION]** Record system qualities: maintainability, checkpoint reliability, extensibility boundaries, operational determinism
6. **[EXECUTION]** Annotate any component where Auggie coverage confidence is degraded (per OQ-008 multi-criteria)
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify all 8 groups are represented with at least one `file:line` evidence citation each
8. **[COMPLETION]** Write inventory to `artifacts/D-0008/spec.md`; write evidence citations to `artifacts/D-0008/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0008/spec.md` exists with all 8 component group sections, each containing at least one verified `file:line` citation
- Every component entry includes: file paths, interfaces, internal dependencies, extension points (four fields non-empty)
- Inventory is reproducible within session: same Auggie queries return the same file paths
- Any component with degraded Auggie coverage is explicitly annotated with the OQ-008 criterion that triggered degradation

**Validation:**
- Manual check: count component group headings in `artifacts/D-0008/spec.md` equals 8; each has `file:line` evidence
- Evidence: linkable artifact produced (`artifacts/D-0008/spec.md`, `artifacts/D-0008/evidence.md`)

**Dependencies:** T01.01 (Auggie MCP connectivity confirmed)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier STRICT due to multi-file scope and data-discovery keywords. Fallback Not Allowed per roadmap architecture — STRICT compliance required for canonical truth source.

---

### T02.02 -- Verify llm-workflows Paths via Auggie MCP with Dual-Status Tracking

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | Stale llm-workflows paths in prompt.md would silently corrupt Phase 4 strategy extraction; dual-status tracking (path_verified / strategy_analyzable) prevents hidden gaps |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data, analysis (stale paths are medium probability per RISK-003) |
| Tier | STRICT |
| Confidence | [████████--] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0009/spec.md`
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0009/evidence.md`

**Deliverables:**
- D-0009: LW path verification record at `artifacts/D-0009/spec.md` with dual-status tracking for every path entry in `artifacts/prompt.md`

**Steps:**
1. **[PLANNING]** Load context: read `artifacts/prompt.md` to extract all llm-workflows component paths; identify the 11 LW components
2. **[PLANNING]** Check dependencies: confirm Auggie MCP availability for llm-workflows (from D-0001); confirm `artifacts/prompt.md` is readable (from D-0003)
3. **[EXECUTION]** For each path entry in `artifacts/prompt.md`, execute Auggie MCP `codebase-retrieval` query against `/config/workspace/llm-workflows`
4. **[EXECUTION]** Record `path_verified` status: `true` if path resolves in repo, `false` if stale
5. **[EXECUTION]** Record `strategy_analyzable` status: `true` if evidence sufficient for strategy extraction; `degraded` if Auggie evidence partial; `false` if path stale
6. **[EXECUTION]** Flag all stale paths with explicit annotation; do NOT modify `artifacts/prompt.md`
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify every path entry has both `path_verified` and `strategy_analyzable` fields with non-null values
8. **[COMPLETION]** Write dual-status tracking table to `artifacts/D-0009/spec.md`; write verification evidence to `artifacts/D-0009/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0009/spec.md` exists with dual-status table covering all paths from `artifacts/prompt.md`
- Every row has both `path_verified` and `strategy_analyzable` fields with explicit values (true/false/degraded)
- Stale paths (`path_verified=false`) are annotated; `artifacts/prompt.md` is not modified
- Verification is reproducible: same Auggie queries return the same path_verified results within session

**Validation:**
- Manual check: row count in dual-status table >= 11 (all LW components covered); no row has empty status fields
- Evidence: linkable artifact produced (`artifacts/D-0009/spec.md`, `artifacts/D-0009/evidence.md`)

**Dependencies:** T01.01, T01.03
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Resolves OQ-001 (LW path staleness handling) per roadmap. Stale-path items cannot enter Phase 4 unmarked.

---

### T02.03 -- Produce component-map.md with IC-to-LW Mappings

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | The cross-framework mapping document is the traceability backbone connecting IC components to LW counterparts for all 8 comparison pairs in Phase 5 |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [███████---] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0010/spec.md`

**Deliverables:**
- D-0010: `component-map.md` at `artifacts/D-0010/spec.md` with ≥8 IC-to-LW cross-framework mappings and explicit IC-only component annotations

**Steps:**
1. **[PLANNING]** Load context: review D-0008 (IC inventory) and D-0009 (LW path verification) as inputs
2. **[PLANNING]** Check dependencies: D-0008 and D-0009 must be complete before this task begins
3. **[EXECUTION]** For each of the 8 IC component groups, identify the corresponding LW component(s) from the verified path list
4. **[EXECUTION]** Create mapping entries: IC component → LW counterpart(s) → mapping type (direct / functional analog / partial / no counterpart)
5. **[EXECUTION]** Annotate IC-only components (no LW counterpart) explicitly
6. **[EXECUTION]** Verify mapping count: ≥8 IC-to-LW mappings must be present
7. **[VERIFICATION]** Direct test: count mapping rows in component-map.md ≥ 8; IC-only annotations present
8. **[COMPLETION]** Write component-map.md to `artifacts/D-0010/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0010/spec.md` exists with a mapping table containing ≥8 IC-to-LW rows
- All IC-only components (no LW counterpart) are explicitly annotated in the document
- Mapping is reproducible: same input inventories produce the same mapping table
- All mapping entries reference verified LW paths (from D-0009 `path_verified=true` entries only)

**Validation:**
- Direct test: count mapping rows in `artifacts/D-0010/spec.md` >= 8; IC-only annotation section present
- Evidence: linkable artifact produced (`artifacts/D-0010/spec.md`)

**Dependencies:** T02.01, T02.02
**Rollback:** TBD (if not specified in roadmap)

---

### T02.04 -- Resolve OQ-002: Pipeline-Analysis Granularity Decision

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | OQ-002 determines whether pipeline-analysis is treated as a single component group or split into subsystems for comparison; decision must be recorded before Phase 3 begins |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0011/notes.md`

**Deliverables:**
- D-0011: OQ-002 decision record at `artifacts/D-0011/notes.md` stating whether pipeline-analysis is kept as single group or split, with evidence from Phase 2 inventory

**Steps:**
1. **[PLANNING]** Load context: review D-0008 IC inventory results for the pipeline analysis subsystem component
2. **[PLANNING]** Apply decision rule: keep as single group unless Phase 2 inventory revealed >3 distinct subsystems warranting separate comparison treatment
3. **[EXECUTION]** Count distinct pipeline-analysis subsystems found in D-0008
4. **[EXECUTION]** Apply rule: if count ≤ 3, keep as single group; if count > 3, split into subsystems
5. **[VERIFICATION]** Manual check: decision record states outcome with subsystem count from D-0008 as evidence
6. **[COMPLETION]** Write OQ-002 decision to `artifacts/D-0011/notes.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0011/notes.md` exists with OQ-002 decision (single-group or split) and subsystem count evidence from D-0008
- Decision applies the roadmap's default rule deterministically
- Decision is stable: same D-0008 evidence produces same decision
- Decision is referenced in Phase 3 and Phase 5 files where pipeline-analysis scope is declared

**Validation:**
- Manual check: `artifacts/D-0011/notes.md` contains decision keyword (single-group or split) with numeric evidence
- Evidence: linkable artifact produced (`artifacts/D-0011/notes.md`)

**Dependencies:** T02.01
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier EXEMPT — planning/decision resolution task. Roadmap specifies default: keep as single group unless evidence from Phase 2 proves otherwise.

---

### Checkpoint: End of Phase 2

**Purpose:** Gate validation (SC-001) that the canonical component inventory is complete and trustworthy before any strategy extraction begins.
**Checkpoint Report Path:** `.dev/releases/current/cross-framework-deep-analysis/checkpoints/CP-P02-END.md`

**Verification:**
- IC inventory at `artifacts/D-0008/spec.md` contains ≥8 component groups each with at least one `file:line` citation
- LW path verification at `artifacts/D-0009/spec.md` has dual-status table covering all paths from `artifacts/prompt.md` with no empty status fields
- `artifacts/D-0010/spec.md` (component-map.md) contains ≥8 IC-to-LW mappings with IC-only annotations present

**Exit Criteria:**
- Gate SC-001 passes: ≥8 IC components, ≥11 LW components, ≥8 cross-framework mappings, IC-only annotations present, all file paths explicitly verified or flagged stale
- OQ-002 resolved at `artifacts/D-0011/notes.md` (pipeline-analysis granularity decision recorded)
- No downstream phase (Phase 3, 4) may begin until all four task deliverables (D-0008 through D-0011) are confirmed present and non-empty
