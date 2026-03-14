# Phase 5 -- Adversarial Comparisons

Run adversarial comparisons for all 8 defined IC-to-LW comparison pairs using `/sc:adversarial`, producing defensible evidence-backed verdicts. Comparison pairs are independent and may run up to 4 concurrently. This is the most token-intensive phase (~40K tokens estimated).

---

### T05.01 -- Run /sc:adversarial for All 8 Comparison Pairs

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | Adversarial comparisons are the primary analytical mechanism; each comparison-*.md file becomes direct input to the Phase 6 strategy synthesis |
| Effort | L |
| Risk | High |
| Risk Drivers | analysis (adversarial debates, dual-repo evidence contestation, most token-intensive phase; end-to-end scope) |
| Tier | STRICT |
| Confidence | [█████████-] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0018/spec.md`
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0018/evidence.md`

**Deliverables:**
- D-0018: 8 comparison-*.md files (one per comparison pair) at `artifacts/`, plus index at `artifacts/D-0018/spec.md`; each file contains debating positions, dual-repo `file:line` evidence, verdict with conditions and confidence score, explicit verdict class, and "adopt patterns not mass" verification

**Steps:**
1. **[PLANNING]** Load context: review D-0010 (component-map.md) for the 8 comparison pairs; review D-0012 and D-0015 (IC and LW strategy corpora) as inputs per pair; review OQ-007 resolution (D-0021) for pair count
2. **[PLANNING]** Check dependencies: D-0012 complete (Phase 3 gate SC-002 passed); D-0015 complete (Phase 4 gate SC-003 passed); D-0010 defines pair assignments
3. **[EXECUTION]** For each of the 8 comparison pairs, invoke `/sc:adversarial` with: IC component strategy as advocate input, LW component strategy as advocate input, dual-repo evidence from Auggie MCP
4. **[EXECUTION]** Each comparison-*.md must contain: (a) debating positions (IC advocate vs. LW advocate), (b) `file:line` evidence from both repositories, (c) clear verdict with conditions and confidence score, (d) explicit verdict class: IC stronger / LW stronger / split by context / no clear winner / discard both, (e) "adopt patterns not mass" verification
5. **[EXECUTION]** Run up to 4 comparison pairs concurrently
6. **[EXECUTION]** Write comparison files to `artifacts/` directory (naming: `comparison-<component-group>.md`)
7. **[VERIFICATION]** Sub-agent (quality-engineer): verify all 8 files exist, each with dual-repo evidence, explicit verdict class, and patterns-not-mass verification field
8. **[COMPLETION]** Write index of produced files to `artifacts/D-0018/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0018/spec.md` exists as index listing all 8 comparison-*.md filenames and verdict classes
- All 8 comparison-*.md files contain non-trivial verdicts with explicit conditions and confidence scores (not placeholder verdicts)
- Every comparison file has `file:line` evidence from both `/config/workspace/IronClaude` and `/config/workspace/llm-workflows`
- All 8 comparison files include "adopt patterns not mass" verification confirming no mass import pattern was recommended

**Validation:**
- Manual check: 8 comparison-*.md files exist; each contains a verdict class keyword (IC stronger/LW stronger/split/no clear winner/discard both) and a confidence score
- Evidence: linkable artifact produced (`artifacts/D-0018/spec.md`, `artifacts/D-0018/evidence.md`)

**Dependencies:** T02.03, T03.03, T04.03
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier STRICT — multi-file adversarial analysis with security-adjacent implications. Sub-Agent Delegation Required: Risk=High + STRICT tier. Actual token costs may vary 2x based on evidence contestation intensity.

---

### T05.02 -- Document No-Clear-Winner Verdicts with Condition-Specific Reasoning

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019 |
| Why | "No clear winner" verdicts without explicit conditions would be useless to Phase 6 synthesis; condition-specific reasoning transforms ambiguous verdicts into actionable planning inputs |
| Effort | S |
| Risk | Medium |
| Risk Drivers | analysis (condition-specific reasoning required; must be non-trivial per gate criteria) |
| Tier | STRICT |
| Confidence | [████████--] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena; Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0019/notes.md`

**Deliverables:**
- D-0019: Condition-specific reasoning records at `artifacts/D-0019/notes.md` for all comparison pairs that received "no clear winner" verdict class

**Steps:**
1. **[PLANNING]** Load context: review D-0018 (8 comparison-*.md files) for any "no clear winner" verdicts; identify which pairs received this verdict class
2. **[PLANNING]** Check dependencies: D-0018 must be complete
3. **[EXECUTION]** For each "no clear winner" verdict, extract and document: (a) conditions under which IC approach is preferable, (b) conditions under which LW approach is preferable, (c) explicit context factors that change the verdict
4. **[EXECUTION]** Verify each "no clear winner" record has at least two distinct condition sets (not a single generic statement)
5. **[EXECUTION]** If no "no clear winner" verdicts exist among the 8 pairs, record that fact explicitly with the verdict class distribution
6. **[VERIFICATION]** Sub-agent (quality-engineer): verify all "no clear winner" verdicts have condition-specific reasoning; no verdict accepted as "acceptable" without explicit conditions
7. **[COMPLETION]** Write condition-specific reasoning records to `artifacts/D-0019/notes.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0019/notes.md` exists; if "no clear winner" verdicts exist, each has at least two distinct condition sets documented
- No "no clear winner" verdict is accepted without at least one explicitly named condition factor
- Records are reproducible: same comparison files produce same condition extraction
- If zero "no clear winner" verdicts exist, evidence record states verdict class distribution across all 8 pairs

**Validation:**
- Manual check: all "no clear winner" entries in `artifacts/D-0019/notes.md` contain the word "condition" or "when" with specific context factors named
- Evidence: linkable artifact produced (`artifacts/D-0019/notes.md`)

**Dependencies:** T05.01
**Rollback:** TBD (if not specified in roadmap)

---

### T05.03 -- Resolve OQ-004: Discard-Both Verdict Handling for Phase 7

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | OQ-004 prevents "discard both" verdicts from becoming planning gaps; Phase 7 must produce IC-native improvement items for any discard-both outcome, not placeholders |
| Effort | XS |
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
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0020/notes.md`

**Deliverables:**
- D-0020: OQ-004 resolution record at `artifacts/D-0020/notes.md` listing all "discard both" verdict pairs and their assigned IC-native improvement item scope

**Steps:**
1. **[PLANNING]** Load context: review D-0018 (8 comparison-*.md files) for any "discard both" verdict classes; identify which pairs received this verdict
2. **[PLANNING]** Apply resolution: for each "discard both" verdict, Phase 7 (T07.04) shall produce an IC-native improvement item with explicit rationale; placeholder omission is not permitted
3. **[EXECUTION]** List all "discard both" pairs with their component names
4. **[EXECUTION]** For each pair, record the intended IC-native improvement direction (what would replace both approaches)
5. **[EXECUTION]** If zero "discard both" verdicts exist, record that fact explicitly
6. **[VERIFICATION]** Sub-agent (quality-engineer): verify each "discard both" pair has an assigned IC-native improvement direction; no omissions
7. **[COMPLETION]** Write OQ-004 resolution to `artifacts/D-0020/notes.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0020/notes.md` exists with complete list of "discard both" pairs and their IC-native improvement directions
- Zero "discard both" verdicts are left without an IC-native improvement direction assignment
- Resolution is stable: same comparison files produce same discard-both list
- Document explicitly references Phase 7 (T07.04) as the responsible execution task

**Validation:**
- Manual check: every "discard both" entry in `artifacts/D-0020/notes.md` has a non-empty IC-native improvement direction field
- Evidence: linkable artifact produced (`artifacts/D-0020/notes.md`)

**Dependencies:** T05.01
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier STRICT due to multi-file analysis scope. OQ-004 resolution is a prerequisite for T07.04; must be complete before Phase 7.

---

### T05.04 -- Resolve OQ-007: Comparison Pair Count Cap Decision

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | OQ-007 enforces the 8-pair cap to prevent scope inflation; if Phase 2 inventory revealed a critical gap, a 9th pair may be authorized, but this must be documented |
| Effort | XS |
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
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0021/notes.md`

**Deliverables:**
- D-0021: OQ-007 resolution record at `artifacts/D-0021/notes.md` confirming pair count (8 or authorized higher count) with justification from Phase 2 inventory evidence

**Steps:**
1. **[PLANNING]** Load context: review D-0010 (component-map.md) for defined comparison pairs; review D-0008 (IC inventory) for any Phase 2 critical gap discoveries
2. **[PLANNING]** Apply rule: cap at 8 unless Phase 2 inventory revealed a critical gap requiring an additional pair
3. **[EXECUTION]** Count comparison pairs executed in T05.01
4. **[EXECUTION]** If count = 8: record as default cap applied
5. **[EXECUTION]** If count > 8: record the critical gap from Phase 2 that authorized the additional pair(s), with D-0008 evidence reference
6. **[VERIFICATION]** Sub-agent (quality-engineer): verify pair count is ≤ 8 or that any excess pairs have documented critical-gap justification from D-0008
7. **[COMPLETION]** Write OQ-007 resolution to `artifacts/D-0021/notes.md`

**Acceptance Criteria:**
- File `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0021/notes.md` exists with final pair count and justification
- If pair count > 8, each additional pair has a critical-gap evidence reference from D-0008
- Resolution is stable: same evidence produces same pair count decision
- Pair count matches the actual count of comparison-*.md files produced in T05.01

**Validation:**
- Manual check: pair count in `artifacts/D-0021/notes.md` matches file count from `ls artifacts/comparison-*.md | wc -l`
- Evidence: linkable artifact produced (`artifacts/D-0021/notes.md`)

**Dependencies:** T05.01
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier STRICT due to STRICT tier task set context; this is a decision-recording task but in a STRICT compliance phase.

---

### Checkpoint: End of Phase 5

**Purpose:** Gate validation (SC-004) that all adversarial comparisons are complete with defensible, evidence-backed, condition-specific verdicts before synthesis begins.
**Checkpoint Report Path:** `.dev/releases/current/cross-framework-deep-analysis/checkpoints/CP-P05-END.md`

**Verification:**
- 8 comparison-*.md files exist in `artifacts/`; each contains dual-repo `file:line` evidence, explicit verdict class, and patterns-not-mass verification (D-0018)
- All "no clear winner" verdicts have condition-specific reasoning documented in D-0019
- OQ-004 and OQ-007 resolutions recorded at D-0020 and D-0021 respectively

**Exit Criteria:**
- Gate SC-004 passes: 8 files produced, each with dual-repo evidence, non-trivial verdict with explicit conditions, patterns-not-mass verified
- D-0020 confirms every "discard both" verdict has an IC-native improvement direction assigned for Phase 7 (T07.04)
- D-0021 confirms pair count matches OQ-007 resolution rule
