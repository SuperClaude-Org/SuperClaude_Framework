# Phase 4 -- llm-workflows Strategy Extraction

Produce the llm-workflows strategic reference corpus with explicit cost and rigor analysis. Per OQ-006 resolution, this phase may run concurrently with Phase 3 if parallelism is confirmed; otherwise execute after Phase 3 completes. Analysis is restricted to prompt-defined component list and verified paths from Phase 2.

---

### T04.01 -- Produce 11 strategy-lw-*.md Files for LW Components

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | The LW strategy corpus provides the reference material for adversarial comparisons; each document must categorize patterns as directly adoptable, conditionally adoptable, or reject |
| Effort | L |
| Risk | Medium |
| Risk Drivers | data (11 strategy documents; path verification required per D-0009) |
| Tier | STANDARD |
| Confidence | [███████---] 74% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0015/spec.md`

**Deliverables:**
- D-0015: 11 strategy-lw-*.md files (one per LW component from `artifacts/prompt.md`) documented at `artifacts/D-0015/spec.md`, each covering rigor analysis, cost/overhead analysis, execution model, and pattern categorization

**Steps:**
1. **[PLANNING]** Load context: review D-0009 (LW path verification with dual-status tracking) for verified LW component paths; review `artifacts/prompt.md` for the 11 component definitions
2. **[PLANNING]** Check dependencies: D-0009 complete; only `path_verified=true` components enter analysis; `strategy_analyzable=degraded` components are annotated as such
3. **[EXECUTION]** For each of the 11 LW components (excluding `path_verified=false` entries), produce `strategy-lw-<component-name>.md` covering: (a) what is rigorous about this component, (b) what is bloated/slow/expensive (complexity overhead, operational drag, maintenance burden, token/runtime expense), (c) execution model and quality enforcement, (d) extension points, (e) categorization: directly adoptable / conditionally adoptable / reject
4. **[EXECUTION]** Use Auggie MCP `codebase-retrieval` queries against `/config/workspace/llm-workflows` for each component; record `file:line` citations
5. **[EXECUTION]** Per-component extraction can run concurrently
6. **[EXECUTION]** For `strategy_analyzable=degraded` components, annotate degraded evidence explicitly in the strategy document
7. **[EXECUTION]** Write all strategy files to `artifacts/` directory
8. **[VERIFICATION]** Direct test: count strategy-lw-*.md files = 11 (or fewer if stale paths excluded); each non-empty and includes both rigor and cost dimensions
9. **[COMPLETION]** Write index of produced files to `artifacts/D-0015/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0015/spec.md` exists as index listing all produced strategy-lw-*.md filenames with paths and `strategy_analyzable` status
- Each strategy-lw-*.md file contains both rigor and cost dimensions (non-empty) plus pattern categorization (directly adoptable/conditionally adoptable/reject)
- Analysis is restricted to prompt-defined component list; no components added beyond `artifacts/prompt.md` scope
- Degraded-evidence components are annotated; stale-path components are excluded with explicit exclusion note in index

**Validation:**
- Direct test: count files matching `artifacts/strategy-lw-*.md` matches expected count from D-0009 verified paths; each file size > 0
- Evidence: linkable artifact produced (`artifacts/D-0015/spec.md` as index)

**Dependencies:** T02.02, T02.04
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Scheduling depends on OQ-006 resolution (D-0005). Restriction to verified paths implements OQ-001 resolution: stale paths cannot enter analysis unmarked.

---

### T04.02 -- Confirm Scope Restriction to Prompt-Defined Component List

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | Scope restriction prevents analysis drift beyond the defined llm-workflows boundary; any component added outside `artifacts/prompt.md` would corrupt the comparison pairs |
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
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0016/evidence.md`

**Deliverables:**
- D-0016: Scope restriction confirmation log at `artifacts/D-0016/evidence.md` verifying no LW components were analyzed beyond `artifacts/prompt.md` scope plus verified Phase 2 paths

**Steps:**
1. **[PLANNING]** Load context: review `artifacts/prompt.md` for the canonical 11 LW component list; review D-0009 for verified paths; review D-0015 for produced strategy files
2. **[PLANNING]** Check dependencies: D-0015 must be complete
3. **[EXECUTION]** List all strategy-lw-*.md files produced in T04.01
4. **[EXECUTION]** Cross-reference each produced file against `artifacts/prompt.md` component list + D-0009 verified paths
5. **[EXECUTION]** Flag any strategy file that does not correspond to a prompt-defined component
6. **[VERIFICATION]** Direct test: all produced strategy-lw-*.md files have a corresponding entry in `artifacts/prompt.md`; zero out-of-scope files
7. **[COMPLETION]** Write scope restriction confirmation to `artifacts/D-0016/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0016/evidence.md` exists confirming all strategy-lw-*.md files correspond to prompt-defined components
- Zero strategy-lw-*.md files exist for components not in `artifacts/prompt.md`
- Confirmation is reproducible: same file list + same prompt.md produces same cross-reference result
- Exclusion log (stale-path components not analyzed) is present in evidence

**Validation:**
- Direct test: no strategy-lw-*.md filename lacks a corresponding entry in `artifacts/prompt.md`
- Evidence: linkable artifact produced (`artifacts/D-0016/evidence.md`)

**Dependencies:** T04.01
**Rollback:** TBD (if not specified in roadmap)

---

### T04.03 -- Enforce Anti-Sycophancy and Evidence Rules on LW Strategies

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | NFR-002 and NFR-003 apply identically to LW strategies as they do to IC strategies; unchecked LW sycophancy would bias Phase 5 adversarial verdicts |
| Effort | S |
| Risk | Medium |
| Risk Drivers | analysis (cross-cutting compliance check across 11 files; same rigor as Phase 3) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0017/evidence.md`

**Deliverables:**
- D-0017: Anti-sycophancy and evidence compliance log at `artifacts/D-0017/evidence.md` with per-component pass/fail for all 11 LW strategy files

**Steps:**
1. **[PLANNING]** Load context: review D-0015 (all strategy-lw-*.md files); apply NFR-002 (strength-weakness pairing) and NFR-003 (`file:line` evidence)
2. **[PLANNING]** Check dependencies: D-0015 and D-0016 complete
3. **[EXECUTION]** For each strategy-lw-*.md file, scan for unpaired strength claims (same method as T03.02 for IC files)
4. **[EXECUTION]** For each strategy-lw-*.md file, verify all strategic claims have `file:line` citations or explicit fallback annotations (same method as T03.03)
5. **[EXECUTION]** Record per-component result: Anti-sycophancy (Pass/Fail), Evidence coverage (Pass/Fail with count)
6. **[EXECUTION]** For any Fail: flag for correction before Phase 5 may begin
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify all 11 (or analyzed count) components show Pass for both compliance dimensions
8. **[COMPLETION]** Write compliance log to `artifacts/D-0017/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0017/evidence.md` exists with per-component pass/fail rows for all analyzed LW components covering both NFR-002 and NFR-003
- All analyzed components show Pass for anti-sycophancy (zero unpaired strength claims)
- All analyzed components show Pass for evidence coverage (100% claims with citation or fallback annotation)
- Compliance check results are reproducible given the same strategy files

**Validation:**
- Manual check: `artifacts/D-0017/evidence.md` shows zero uncorrected Fail entries for any analyzed LW component
- Evidence: linkable artifact produced (`artifacts/D-0017/evidence.md`)

**Dependencies:** T04.01, T04.02
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier STRICT because compliance enforcement spans multiple LW strategy files (>2 files affected). Tier conflict note: "analyze" keyword (EXEMPT) vs. cross-file scope (STRICT) → resolved to STRICT by priority rule.

---

### Checkpoint: End of Phase 4

**Purpose:** Gate validation (SC-003) that the LW strategy corpus is complete, restricted to prompt scope, anti-sycophancy compliant, and evidence-backed.
**Checkpoint Report Path:** `.dev/releases/current/cross-framework-deep-analysis/checkpoints/CP-P04-END.md`

**Verification:**
- Strategy-lw-*.md files exist in `artifacts/` covering all verified LW components from D-0009; each includes rigor and cost dimensions (D-0015)
- Scope restriction log at `artifacts/D-0016/evidence.md` confirms zero out-of-scope files
- Compliance log at `artifacts/D-0017/evidence.md` shows Pass for both NFR-002 and NFR-003 across all analyzed LW components

**Exit Criteria:**
- Gate SC-003 passes: 11 files produced (or documented-reduced count from stale paths), each covering both rigor and cost dimensions with paired strengths/weaknesses and evidence
- D-0016 confirms scope restriction; D-0017 confirms compliance
- No upstream Phase 3 gate failures outstanding (Phase 3 gate SC-002 must also be confirmed before Phase 5 begins)
