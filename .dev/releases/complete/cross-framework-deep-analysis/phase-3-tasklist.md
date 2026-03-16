# Phase 3 -- IronClaude Strategy Extraction

Produce the full IronClaude strategy corpus with balanced trade-off analysis and evidence-backed claims. Per OQ-006 resolution, this phase may run concurrently with Phase 4 if parallelism is confirmed; otherwise execute Phase 3 then Phase 4 sequentially.

---

### T03.01 -- Produce 8 strategy-ic-*.md Files for IC Component Groups

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | The IC strategy corpus is the primary input for all adversarial comparisons in Phase 5; each document must capture design philosophy, execution model, and system qualities |
| Effort | L |
| Risk | Medium |
| Risk Drivers | data (8 strategy documents; broad Auggie queries required across all component groups) |
| Tier | STANDARD |
| Confidence | [███████---] 74% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0012/spec.md`

**Deliverables:**
- D-0012: 8 strategy-ic-*.md files (one per IC component group) documented at `artifacts/D-0012/spec.md`, each covering design philosophy, execution model, quality enforcement, error handling, extension points, and system qualities

**Steps:**
1. **[PLANNING]** Load context: review D-0008 (IC component inventory) for the 8 component groups and their file paths; review D-0011 (OQ-002) for pipeline-analysis scope
2. **[PLANNING]** Check dependencies: D-0008 must be complete; D-0011 must be recorded
3. **[EXECUTION]** For each of the 8 IC component groups, produce `strategy-ic-<component-name>.md` covering: (a) design philosophy and why the current design exists, (b) execution model, (c) quality enforcement mechanism, (d) error handling strategy, (e) extension points, (f) system qualities: maintainability, checkpoint reliability, extensibility boundaries, operational determinism
4. **[EXECUTION]** Use Auggie MCP `codebase-retrieval` queries against `/config/workspace/IronClaude` to gather evidence for each component; record `file:line` citations
5. **[EXECUTION]** Per-component extraction can run concurrently (up to 6 concurrent per roadmap AC-012 recommendation)
6. **[EXECUTION]** Write all 8 strategy files to `artifacts/` directory (naming: `strategy-ic-roadmap-pipeline.md`, `strategy-ic-cleanup-audit.md`, `strategy-ic-sprint-executor.md`, `strategy-ic-pm-agent.md`, `strategy-ic-adversarial-pipeline.md`, `strategy-ic-task-unified.md`, `strategy-ic-quality-agents.md`, `strategy-ic-pipeline-analysis.md`)
7. **[VERIFICATION]** Direct test: count strategy-ic-*.md files produced = 8; each file is non-empty
8. **[COMPLETION]** Write index of produced files to `artifacts/D-0012/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0012/spec.md` exists as an index listing all 8 strategy-ic-*.md filenames with paths
- 8 strategy-ic-*.md files exist in `artifacts/`, each with non-empty content covering all 6 required sections (design philosophy, execution model, quality enforcement, error handling, extension points, system qualities)
- All strategy files are produced within `artifacts/` directory; no files written outside this boundary
- File count and names are reproducible: same component list from D-0008 produces same 8 filenames

**Validation:**
- Direct test: count files matching `artifacts/strategy-ic-*.md` equals 8; each file size > 0
- Evidence: linkable artifact produced (`artifacts/D-0012/spec.md` as index)

**Dependencies:** T02.01, T02.04
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Scheduling depends on OQ-006 resolution (D-0005): if Confirmed-Parallel, this phase runs concurrently with Phase 4; if Default-Sequential, Phase 3 completes before Phase 4 begins.

---

### T03.02 -- Enforce Anti-Sycophancy Compliance on IC Strategies

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | NFR-002 mandates every strength claim in IC strategy docs has a paired weakness/trade-off; any unpaired strength fails gate review and blocks Phase 5 comparisons |
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
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0013/evidence.md`

**Deliverables:**
- D-0013: Anti-sycophancy compliance log at `artifacts/D-0013/evidence.md` with per-component pass/fail status for strength-weakness pairing requirement

**Steps:**
1. **[PLANNING]** Load context: review D-0012 (8 strategy-ic-*.md files) as input; apply NFR-002 rule: every strength claim must have a paired weakness/trade-off
2. **[PLANNING]** Check dependencies: D-0012 must be complete
3. **[EXECUTION]** For each of the 8 strategy-ic-*.md files, scan for strength claims (keywords: "advantage", "benefit", "strength", "enables", "improves", "faster", "reliable")
4. **[EXECUTION]** For each strength claim found, verify a paired weakness or trade-off is stated in the same document (within the same section or immediately adjacent)
5. **[EXECUTION]** Record per-component result: Pass (all strengths paired) or Fail (unpaired strength found, with specific text citation)
6. **[EXECUTION]** For any Fail: note the specific unpaired claim for correction before Phase 5 gates
7. **[VERIFICATION]** Direct test: all 8 components show Pass in compliance log; no Fail entries remain uncorrected
8. **[COMPLETION]** Write compliance log to `artifacts/D-0013/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0013/evidence.md` exists with per-component pass/fail rows for all 8 components
- All 8 components show Pass status (no unpaired strength claims remain)
- Compliance check is reproducible: same strategy files produce same pass/fail results
- Any initial Fail entries are documented with the specific uncorrected claim text for traceability

**Validation:**
- Direct test: count Pass rows in `artifacts/D-0013/evidence.md` equals 8; zero uncorrected Fail rows
- Evidence: linkable artifact produced (`artifacts/D-0013/evidence.md`)

**Dependencies:** T03.01
**Rollback:** TBD (if not specified in roadmap)

---

### T03.03 -- Attach file:line Evidence from Auggie MCP to IC Strategy Claims

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | NFR-003 mandates all strategic claims in IC strategy documents are backed by verifiable `file:line` evidence from Auggie MCP; unverified claims fail Phase 7 formal validation |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (evidence verification across all 8 strategy files with Auggie MCP queries) |
| Tier | STRICT |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0014/evidence.md`

**Deliverables:**
- D-0014: Evidence citation audit at `artifacts/D-0014/evidence.md` confirming all strategic claims in 8 strategy-ic-*.md files have attached `file:line` citations from Auggie MCP

**Steps:**
1. **[PLANNING]** Load context: review D-0012 (8 strategy-ic-*.md files); identify all strategic claims requiring evidence
2. **[PLANNING]** Check dependencies: D-0012 complete; D-0001 confirms Auggie MCP availability
3. **[EXECUTION]** For each strategic claim in each of the 8 strategy files, verify a `file:line` citation is present
4. **[EXECUTION]** For any claim missing citation: execute Auggie MCP `codebase-retrieval` query to find the supporting evidence; attach the citation to the strategy document
5. **[EXECUTION]** For any claim where Auggie MCP cannot find evidence (fallback condition per OQ-008): annotate claim as fallback-derived; note which OQ-008 criterion triggered fallback
6. **[EXECUTION]** Produce summary: total claims audited, claims with direct Auggie evidence, claims with fallback annotation
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify 100% of strategic claims have either a `file:line` citation or explicit fallback annotation
8. **[COMPLETION]** Write evidence citation audit to `artifacts/D-0014/evidence.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0014/evidence.md` exists with audit summary: total claims, claims with direct evidence, claims with fallback annotation
- 100% of strategic claims in 8 strategy-ic-*.md files have either a `file:line` citation or explicit fallback annotation (zero unannotated claims)
- Evidence audit is reproducible within session: same strategy files + same Auggie queries produce same citation coverage
- Fallback-annotated claims explicitly state the OQ-008 criterion that triggered fallback

**Validation:**
- Manual check: `artifacts/D-0014/evidence.md` summary shows 0 unannotated claims; all fallback annotations include OQ-008 criterion reference
- Evidence: linkable artifact produced (`artifacts/D-0014/evidence.md`)

**Dependencies:** T03.01, T03.02
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier STRICT due to data-verification scope across multiple files and mandatory Auggie MCP evidence requirement per NFR-003. Fallback Not Allowed for STRICT verification — sub-agent must confirm 100% coverage.

---

### Checkpoint: End of Phase 3

**Purpose:** Gate validation (SC-002) that the IC strategy corpus is complete, anti-sycophancy compliant, and evidence-backed before adversarial comparisons begin.
**Checkpoint Report Path:** `.dev/releases/current/cross-framework-deep-analysis/checkpoints/CP-P03-END.md`

**Verification:**
- 8 strategy-ic-*.md files exist in `artifacts/` with non-empty content covering all 6 required sections (D-0012)
- Anti-sycophancy compliance log at `artifacts/D-0013/evidence.md` shows Pass for all 8 components
- Evidence audit at `artifacts/D-0014/evidence.md` shows 100% of strategic claims have `file:line` citation or explicit fallback annotation

**Exit Criteria:**
- Gate SC-002 passes: 8 files produced, each with strength-weakness pairing verified and `file:line` evidence attached to strategic claims
- No uncorrected anti-sycophancy failures in D-0013 (all 8 components Pass)
- D-0014 confirms zero unannotated claims across all 8 strategy files
