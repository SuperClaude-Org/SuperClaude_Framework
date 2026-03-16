# Phase 6 -- Strategy Synthesis

Synthesize all 8 adversarial comparison verdicts into a unified architectural strategy document organized under five principles. This phase has no parallelism — it depends on all Phase 5 outputs and produces the single merged-strategy.md that governs all Phase 7 improvement planning.

---

### T06.01 -- Synthesize 8 Comparison Verdicts into merged-strategy.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | merged-strategy.md is the single authoritative architectural guidance document that Phase 7 improvement plans must trace to; it must cover all 8 verdicts with no gaps |
| Effort | L |
| Risk | Medium |
| Risk Drivers | analysis (synthesis across 8 adversarial outputs; cross-component consistency required) |
| Tier | STANDARD |
| Confidence | [███████---] 74% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0022/spec.md`

**Deliverables:**
- D-0022: `merged-strategy.md` at `artifacts/D-0022/spec.md` synthesizing all 8 adversarial verdicts into cross-component architectural guidance

**Steps:**
1. **[PLANNING]** Load context: review D-0018 (8 comparison-*.md files with verdicts); review D-0019 (no-clear-winner conditions); review D-0020 (discard-both directions)
2. **[PLANNING]** Check dependencies: D-0018, D-0019, D-0020, D-0021 all complete (Phase 5 gate SC-004 passed)
3. **[EXECUTION]** Read all 8 comparison-*.md verdict classes and confidence scores
4. **[EXECUTION]** Identify cross-component patterns and tensions across verdicts
5. **[EXECUTION]** Draft merged-strategy.md synthesizing all 8 verdicts into coherent guidance (do not simply list verdicts; synthesize into strategic direction)
6. **[EXECUTION]** Verify all 8 comparison verdicts are represented in the synthesis (no orphaned comparison)
7. **[VERIFICATION]** Direct test: merged-strategy.md exists; count of comparison references = 8 (all pairs covered)
8. **[COMPLETION]** Write merged-strategy.md to `artifacts/D-0022/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0022/spec.md` exists with synthesized content covering all 8 comparison pairs
- All 8 comparison pair names from D-0010 appear in merged-strategy.md (no orphaned comparisons)
- Synthesis is non-trivial: not a list of 8 separate verdicts but integrated cross-component guidance
- Document is reproducible given the same 8 comparison files as input

**Validation:**
- Direct test: count references to comparison pair names in `artifacts/D-0022/spec.md` >= 8; file size > 0
- Evidence: linkable artifact produced (`artifacts/D-0022/spec.md`)

**Dependencies:** T05.01, T05.02, T05.03, T05.04
**Rollback:** TBD (if not specified in roadmap)

---

### T06.02 -- Organize Guidance Under Five Architectural Principles

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | Principle-centric organization makes merged-strategy.md architecturally reusable across future sprints and preserves direct component traceability for Phase 7 planners |
| Effort | M |
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
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0023/evidence.md`

**Deliverables:**
- D-0023: Verification record at `artifacts/D-0023/evidence.md` confirming merged-strategy.md contains all five architectural principle sections with component references explicitly preserved within each

**Steps:**
1. **[PLANNING]** Load context: review D-0022 (merged-strategy.md draft); identify the five required principle sections from roadmap: Evidence integrity, Deterministic gates, Restartability, Bounded complexity, Scalable quality enforcement
2. **[PLANNING]** Check dependencies: D-0022 must be complete
3. **[EXECUTION]** Verify that merged-strategy.md contains exactly five sections with these headings (or equivalent): Evidence integrity, Deterministic gates, Restartability, Bounded complexity, Scalable quality enforcement
4. **[EXECUTION]** For each principle section, verify component references are explicitly preserved (specific IC component group names appear within the section)
5. **[EXECUTION]** If any section is missing or component references are absent: add the section or references to merged-strategy.md
6. **[EXECUTION]** Verify the Phase 1→6 traceability chain is maintained: each principle section references the component(s) it governs
7. **[VERIFICATION]** Direct test: five section headings present in merged-strategy.md; each section contains at least one IC component group reference by name
8. **[COMPLETION]** Write verification confirmation to `artifacts/D-0023/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0023/evidence.md` exists confirming all five principle sections are present in merged-strategy.md with component references
- Merged-strategy.md contains sections for: Evidence integrity, Deterministic gates, Restartability, Bounded complexity, Scalable quality enforcement (five sections, all present)
- Each principle section contains at least one named IC component group reference (not generic references)
- Verification is reproducible: same merged-strategy.md content produces same section presence confirmation

**Validation:**
- Direct test: grep merged-strategy.md for each of the five principle heading keywords; all five return matches
- Evidence: linkable artifact produced (`artifacts/D-0023/evidence.md`)

**Dependencies:** T06.01
**Rollback:** TBD (if not specified in roadmap)

---

### T06.03 -- Add Rigor-Without-Bloat Section and Document Discard Decisions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | The "rigor without bloat" section is a mandatory gate criterion (SC-005); discard decision documentation enforces the patterns-not-mass invariant at synthesis level |
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
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0024/notes.md`

**Deliverables:**
- D-0024: Verification record at `artifacts/D-0024/notes.md` confirming merged-strategy.md contains: (a) explicit "rigor without bloat" section, (b) all discard decisions documented with justification, (c) "adopt patterns not mass" verified at synthesis level

**Steps:**
1. **[PLANNING]** Load context: review D-0022 (merged-strategy.md); review D-0018 (comparison verdicts for discard decisions)
2. **[PLANNING]** Check dependencies: D-0022 and D-0023 complete
3. **[EXECUTION]** Verify merged-strategy.md contains a "Rigor Without Bloat" section (or equivalent heading); add if missing
4. **[EXECUTION]** Enumerate all discard decisions from D-0018 (LW patterns discarded, discard-both verdicts from D-0020)
5. **[EXECUTION]** Verify each discard decision appears in merged-strategy.md with a justification sentence stating why the pattern was discarded
6. **[EXECUTION]** Verify merged-strategy.md contains a "patterns not mass" verification statement at synthesis level
7. **[VERIFICATION]** Direct test: "rigor without bloat" heading present; all discard decisions from D-0018 appear with justification text
8. **[COMPLETION]** Write verification record to `artifacts/D-0024/notes.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0024/notes.md` exists confirming "rigor without bloat" section and all discard decisions with justification are present in merged-strategy.md
- Every discard decision from D-0018 has a corresponding justification sentence in merged-strategy.md (zero undocumented discards)
- "Adopt patterns not mass" is explicitly verified at the synthesis level in merged-strategy.md
- Verification is reproducible: same merged-strategy.md content produces same presence confirmations

**Validation:**
- Direct test: grep merged-strategy.md for "rigor without bloat" (case-insensitive) returns a match; discard count in D-0024 matches discard count from D-0018
- Evidence: linkable artifact produced (`artifacts/D-0024/notes.md`)

**Dependencies:** T06.01, T06.02
**Rollback:** TBD (if not specified in roadmap)

---

### T06.04 -- Run Internal Contradiction Review and Orphan Check

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | No component area may be orphaned or contradicted in merged-strategy.md; a contradiction or gap here propagates into all 8 improvement plans in Phase 7 |
| Effort | S |
| Risk | Medium |
| Risk Drivers | analysis (cross-artifact consistency check; end-to-end traceability verification) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0025/evidence.md`

**Deliverables:**
- D-0025: Contradiction review report at `artifacts/D-0025/evidence.md` confirming: (a) no internal contradictions in merged-strategy.md, (b) no orphaned IC component areas, (c) cross-artifact consistency with D-0018 verdicts

**Steps:**
1. **[PLANNING]** Load context: review D-0022 (merged-strategy.md); review D-0008 (8 IC component groups); review D-0018 (8 comparison verdicts)
2. **[PLANNING]** Check dependencies: D-0022, D-0023, D-0024 all complete
3. **[EXECUTION]** Check merged-strategy.md for internal contradictions: scan for conflicting guidance statements within the same document (e.g., "always gate X" vs. "gate X only when Y" in different sections)
4. **[EXECUTION]** Check for orphaned IC component areas: verify all 8 IC component groups from D-0008 appear in at least one principle section of merged-strategy.md
5. **[EXECUTION]** Check cross-artifact consistency: verify each comparison verdict from D-0018 is reflected (consistently) in merged-strategy.md
6. **[EXECUTION]** Record any contradictions, orphans, or inconsistencies found; resolve by updating merged-strategy.md
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify zero contradictions, zero orphaned IC component areas, and zero inconsistencies with D-0018 verdicts
8. **[COMPLETION]** Write contradiction review report to `artifacts/D-0025/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0025/evidence.md` exists with contradiction review results showing zero unresolved contradictions
- All 8 IC component groups from D-0008 appear in at least one principle section of merged-strategy.md (zero orphaned areas)
- All 8 comparison verdicts from D-0018 are consistently reflected in merged-strategy.md (zero inconsistencies)
- Review is reproducible: same merged-strategy.md content produces same contradiction/orphan scan results

**Validation:**
- Manual check: `artifacts/D-0025/evidence.md` shows zero unresolved contradictions, zero orphaned IC component groups
- Evidence: linkable artifact produced (`artifacts/D-0025/evidence.md`)

**Dependencies:** T06.01, T06.02, T06.03
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier STRICT due to cross-artifact consistency scope (references multiple files: D-0022, D-0008, D-0018). Tier conflict: "review" (EXEMPT) vs. >2 files affected (STRICT) → resolved to STRICT by priority rule.

---

### Checkpoint: End of Phase 6

**Purpose:** Gate validation (SC-005) that merged-strategy.md is complete, internally consistent, and suitable as the authoritative input for all Phase 7 improvement plans.
**Checkpoint Report Path:** `.dev/releases/current/cross-framework-deep-analysis/checkpoints/CP-P06-END.md`

**Verification:**
- `artifacts/D-0022/spec.md` (merged-strategy.md) exists covering all 8 comparison verdicts
- Five architectural principle sections present with component references preserved (D-0023)
- "Rigor without bloat" section present; all discard decisions documented with justification (D-0024)

**Exit Criteria:**
- Gate SC-005 passes: rigor-without-bloat section present, all five principle sections cover relevant components, no orphaned areas, discard decisions justified, internal consistency verified (D-0025)
- D-0025 confirms zero unresolved contradictions and zero orphaned IC component groups
- No Phase 7 work may begin until D-0025 reports clean review
