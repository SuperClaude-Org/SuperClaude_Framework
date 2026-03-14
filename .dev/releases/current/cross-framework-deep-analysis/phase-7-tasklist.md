# Phase 7 -- Improvement Planning

Produce the full improvement portfolio and cross-component dependency graph for all 8 IC component groups. Per-component improvement plans may run in parallel; improve-master.md is produced sequentially after all component plans are complete.

---

### T07.01 -- Produce 8 improve-*.md Component Improvement Plan Files

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | Component-level improvement plans are the primary planning deliverables of the sprint; each item must be implementation-ready with file paths, P-tier, effort, and patterns-not-mass field |
| Effort | L |
| Risk | Medium |
| Risk Drivers | analysis (8 improvement plan documents; structural leverage priority ordering required) |
| Tier | STANDARD |
| Confidence | [███████---] 74% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0026/spec.md`

**Deliverables:**
- D-0026: 8 improve-*.md files (one per IC component group) at `artifacts/`, each containing improvement plan items with required fields; index at `artifacts/D-0026/spec.md`

**Steps:**
1. **[PLANNING]** Load context: review D-0022 (merged-strategy.md) as the traceability source; review D-0008 (IC inventory) for component-specific file paths; review D-0018 (comparison verdicts) for adoption decisions
2. **[PLANNING]** Check dependencies: D-0022 complete (Phase 6 gate SC-005 passed); D-0025 confirms zero contradictions
3. **[EXECUTION]** For each of the 8 IC component groups, produce `improve-<component-name>.md` with improvement items, each containing: (a) specific file paths and change description, (b) rationale tracing to merged strategy principle, (c) priority P0/P1/P2/P3, (d) effort XS/S/M/L/XL, (e) dependencies, (f) acceptance criteria, (g) risk assessment, (h) classification: "strengthen existing code" vs. "add new code", (i) for LW-pattern adoptions: `patterns_not_mass: true` field + "why not full import" sentence
4. **[EXECUTION]** Apply structural leverage priority ordering within each file: gate integrity > evidence verification > restartability/resume > traceability automation > artifact schema reliability
5. **[EXECUTION]** Per-component plans can run concurrently
6. **[EXECUTION]** Write all improve files to `artifacts/` directory (naming: `improve-<component-name>.md`)
7. **[VERIFICATION]** Direct test: count improve-*.md files = 8; each is non-empty; each contains P-tier and effort fields
8. **[COMPLETION]** Write index of produced files to `artifacts/D-0026/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0026/spec.md` exists as index listing all 8 improve-*.md filenames
- All 8 improve-*.md files exist; every improvement item contains: file paths, P-tier (P0/P1/P2/P3), effort (XS/S/M/L/XL), rationale tracing to a named merged strategy principle
- Every LW-pattern adoption item has `patterns_not_mass: true` field and a "why not full import" sentence
- Priority ordering within each file follows the structural leverage sequence from roadmap

**Validation:**
- Direct test: count files matching `artifacts/improve-*.md` equals 8; grep for `patterns_not_mass` in each LW-adoption item returns a match
- Evidence: linkable artifact produced (`artifacts/D-0026/spec.md` as index)

**Dependencies:** T06.01, T06.04
**Rollback:** TBD (if not specified in roadmap)

---

### T07.02 -- Apply Structural Leverage Priority Ordering to All Improvement Items

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | Priority ordering ensures the most impactful improvements (gate integrity, evidence verification) are identified and planned first, reducing downstream cascade risk |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [███████---] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0027/evidence.md`

**Deliverables:**
- D-0027: Priority ordering verification record at `artifacts/D-0027/evidence.md` confirming all 8 improve-*.md files apply the structural leverage sequence

**Steps:**
1. **[PLANNING]** Load context: review D-0026 (8 improve-*.md files); identify the five structural leverage categories: gate integrity, evidence verification, restartability/resume, traceability automation, artifact schema reliability
2. **[PLANNING]** Check dependencies: D-0026 must be complete
3. **[EXECUTION]** For each improve-*.md, verify that items are ordered with gate integrity items (P0 priority) before evidence verification items (P1), before restartability items (P1/P2), before traceability automation (P2), before artifact schema reliability (P2/P3)
4. **[EXECUTION]** Record any files where ordering deviates; correct ordering in those files
5. **[EXECUTION]** Verify the overall cross-file priority distribution is reasonable (not all items at P0)
6. **[VERIFICATION]** Direct test: in each improve-*.md, the first item is classified as gate integrity (P0) or has a higher-priority category than the last item
7. **[COMPLETION]** Write priority ordering verification to `artifacts/D-0027/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0027/evidence.md` exists confirming structural leverage priority ordering is applied in all 8 improve-*.md files
- No improve-*.md has P3 items listed before P0 items without documented justification
- Priority distribution across all items is documented (count by P-tier)
- Verification is reproducible: same improve files produce same ordering assessment

**Validation:**
- Direct test: in each improve-*.md, first improvement item has higher or equal priority to last item (P0 ≤ P1 ≤ P2 ≤ P3 ordering)
- Evidence: linkable artifact produced (`artifacts/D-0027/evidence.md`)

**Dependencies:** T07.01
**Rollback:** TBD (if not specified in roadmap)

---

### T07.03 -- Produce improve-master.md with Cross-Component Dependency Graph

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | The cross-component dependency graph in improve-master.md separates prerequisites from optional refinements, enabling the v3.0 planning team to identify critical path items across all components |
| Effort | M |
| Risk | Medium |
| Risk Drivers | analysis (cross-component dependency graph; end-to-end scope across 8 component plans) |
| Tier | STRICT |
| Confidence | [████████--] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0028/spec.md`

**Deliverables:**
- D-0028: `improve-master.md` at `artifacts/D-0028/spec.md` containing: aggregated improvement item summary, cross-component dependency graph isolating prerequisites from optional refinements

**Steps:**
1. **[PLANNING]** Load context: review D-0026 (all 8 improve-*.md files); review D-0027 (priority ordering) as input
2. **[PLANNING]** Check dependencies: D-0026 and D-0027 complete
3. **[EXECUTION]** Aggregate all improvement items from the 8 component files into a master list
4. **[EXECUTION]** Identify cross-component dependencies: items in one component's improvement plan that require another component to be improved first (prerequisites)
5. **[EXECUTION]** Produce dependency graph distinguishing: (a) prerequisite items (must be done before dependent work), (b) optional refinements (can be done independently)
6. **[EXECUTION]** Verify no circular dependencies exist in the graph
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify dependency graph covers all 8 components; no circular dependencies; prerequisites and optional refinements are explicitly labeled
8. **[COMPLETION]** Write improve-master.md to `artifacts/D-0028/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0028/spec.md` exists as improve-master.md with aggregated improvement items and dependency graph
- All 8 IC component groups have at least one improvement item represented in improve-master.md
- Dependency graph explicitly labels prerequisites vs. optional refinements (no unlabeled dependencies)
- No circular dependencies exist in the dependency graph

**Validation:**
- Manual check: `artifacts/D-0028/spec.md` contains dependency graph section; all 8 component group names appear; no A→B→C→A circular chains
- Evidence: linkable artifact produced (`artifacts/D-0028/spec.md`)

**Dependencies:** T07.01, T07.02
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier STRICT due to cross-component scope (>2 files) and dependency graph construction. Tier conflict: "produce" (STANDARD) vs. cross-file scope >2 files (STRICT +0.3) → resolved to STRICT by context booster.

---

### T07.04 -- Produce IC-Native Improvement Items for Discard-Both Verdicts

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029 |
| Why | OQ-004 resolution prohibits placeholder omission for "discard both" verdict pairs; IC-native improvement items ensure these gaps are addressed in the improvement portfolio |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0029/evidence.md`

**Deliverables:**
- D-0029: IC-native improvement items for all "discard both" verdict pairs at `artifacts/D-0029/evidence.md`, each with explicit rationale tracing to OQ-004 resolution (D-0020)

**Steps:**
1. **[PLANNING]** Load context: review D-0020 (OQ-004 resolution listing all "discard both" pairs and IC-native improvement directions); review the relevant improve-*.md files from D-0026
2. **[PLANNING]** Check dependencies: D-0020 complete (OQ-004 resolved); D-0026 complete
3. **[EXECUTION]** For each "discard both" pair listed in D-0020, verify that a corresponding IC-native improvement item exists in the relevant improve-*.md file
4. **[EXECUTION]** If any "discard both" pair lacks an IC-native improvement item: add the item to the appropriate improve-*.md file with explicit rationale ("discard both verdict — OQ-004 resolution — IC-native improvement")
5. **[EXECUTION]** Record the complete list of IC-native items produced/verified for "discard both" pairs
6. **[EXECUTION]** If D-0020 shows zero "discard both" verdicts: record that fact and mark this task complete
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify every "discard both" pair from D-0020 has a corresponding IC-native improvement item; zero omissions
8. **[COMPLETION]** Write IC-native improvement item records to `artifacts/D-0029/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0029/evidence.md` exists with complete list of "discard both" pairs and their IC-native improvement item locations
- Zero "discard both" pairs are without an IC-native improvement item in improve-master.md or the relevant component improve file
- Each IC-native item includes explicit rationale tracing to OQ-004 resolution (D-0020)
- Evidence is reproducible: same D-0020 list produces same IC-native item mapping

**Validation:**
- Manual check: count entries in `artifacts/D-0029/evidence.md` equals count of "discard both" verdicts in D-0020; each entry references a specific improve-*.md file and item
- Evidence: linkable artifact produced (`artifacts/D-0029/evidence.md`)

**Dependencies:** T05.03, T07.01, T07.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 7

**Purpose:** Gate validation (SC-006) that the full improvement portfolio is complete, traceable, and implementation-ready before formal adversarial validation begins.
**Checkpoint Report Path:** `.dev/releases/current/cross-framework-deep-analysis/checkpoints/CP-P07-END.md`

**Verification:**
- 8 improve-*.md files exist in `artifacts/`; each has P-tier, effort, file paths, and patterns_not_mass status for all LW-sourced items (D-0026)
- improve-master.md at `artifacts/D-0028/spec.md` contains dependency graph with prerequisites vs. optional refinements labeled (D-0028)
- D-0029 confirms all "discard both" verdict pairs have IC-native improvement items; zero omissions

**Exit Criteria:**
- Gate SC-006 passes: 9 documents (8 component + 1 master), every item has P-tier + effort + file paths + `patterns_not_mass` status + "why not full import" where applicable, dependency graph present
- D-0027 confirms structural leverage priority ordering applied across all 8 component plans
- D-0028 dependency graph has zero circular dependencies confirmed by sub-agent verification
