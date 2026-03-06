# Phase 5 -- Documentation & Spec Alignment

Write the mandatory CHANGELOG entry with migration guide, update spec prose to reflect 0.8 (Tier 4 edits), and add budget guidance per panel recommendation. Documentation changes are made only after tests confirm code correctness.

---

### T05.01 -- Write CHANGELOG entry for v2.0.0 with migration guide

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031 |
| Why | Mandatory per panel consensus (item 5): CHANGELOG entry documents behavioral changes and provides migration path for users relying on old defaults |
| Effort | S |
| Risk | Medium |
| Risk Drivers | migration |
| Tier | STRICT |
| Confidence | `[████████--] 43%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0026/spec.md`

**Deliverables:**
- CHANGELOG entry for v2.0.0 with Changed section (max_turns 50→100, reimbursement_rate 0.5→0.8), Migration Guide, and Budget Guidance

**Steps:**
1. **[PLANNING]** Read spec §11 CHANGELOG template (spec lines 374-397) for required structure and content
2. **[PLANNING]** Identify the CHANGELOG file location in the repository
3. **[EXECUTION]** Write CHANGELOG entry following spec §11 template with three sections: Changed, Migration Guide, Budget Guidance
4. **[EXECUTION]** Include: max_turns change (50→100) with phase timeout implications (6,300s→12,300s), reimbursement_rate change (0.5→0.8) with budget sustainability improvement
5. **[EXECUTION]** Include migration guide: how to preserve old behavior via explicit `--max-turns=50` override
6. **[VERIFICATION]** Verify CHANGELOG entry matches spec §11 template structure
7. **[COMPLETION]** Record entry in D-0026 artifact

**Acceptance Criteria:**
- CHANGELOG entry exists with v2.0.0 header, Changed section, Migration Guide section, and Budget Guidance section matching spec §11 template
- Entry documents both `max_turns` and `reimbursement_rate` changes with rationale
- Migration guide includes explicit override command: `superclaude sprint run <index> --max-turns 50`
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0026/spec.md`

**Validation:**
- Manual check: CHANGELOG entry contains all three required sections (Changed, Migration Guide, Budget Guidance)
- Evidence: CHANGELOG entry text captured in artifact

**Dependencies:** T04.01-T04.10 (test suite must be passing before documenting)
**Rollback:** Remove the added CHANGELOG entry
**Notes:** Tier conflict: [STRICT vs EXEMPT] → resolved to STRICT by priority rule ("migration" keyword triggers STRICT; docs path triggers EXEMPT; STRICT wins). SC-006 traceability.

---

### T05.02 -- Update unified-spec-v1.0.md §3.1 rate to 0.80

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032 |
| Why | Spec §3.1 states `reimbursement_rate: float = 0.90` but implementation uses 0.80; must align to prevent spec-implementation drift (panel consensus item 2) |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | `[████████████] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0027/evidence.md`

**Deliverables:**
- `unified-spec-v1.0.md` line 178 updated from `reimbursement_rate: float = 0.90` to `reimbursement_rate: float = 0.80`

**Steps:**
1. **[PLANNING]** Locate the prior spec file (`unified-audit-gating-v1.2.1/unified-spec-v1.0.md`) and confirm line 178 content
2. **[EXECUTION]** Edit line 178 to read `reimbursement_rate: float = 0.80`
3. **[VERIFICATION]** Confirm edit is correct: line 178 now reads `0.80`
4. **[COMPLETION]** Record evidence in D-0027 artifact

**Acceptance Criteria:**
- `unified-spec-v1.0.md` line 178 reads `reimbursement_rate: float = 0.80`
- No other lines in §3.1 were modified beyond the rate value
- Spec now matches implementation value (0.80)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0027/evidence.md`

**Validation:**
- Manual check: `grep -n 'reimbursement_rate' unified-spec-v1.0.md` shows `0.80` at line 178
- Evidence: grep output captured in evidence artifact

**Dependencies:** T04.01-T04.10 (tests confirm code correctness before updating spec)
**Rollback:** Revert line 178 to `reimbursement_rate: float = 0.90`

---

### T05.03 -- Update unified-spec-v1.0.md §3.4 proof to rate=0.80

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033 |
| Why | Spec §3.4 proof uses rate=0.90 math (2.8 turns/task, ~129 drain); must be corrected to rate=0.80 (4 turns/task, 184 drain) per spec §4.4 |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | `[████████████] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0028/evidence.md`

**Deliverables:**
- `unified-spec-v1.0.md` §3.4 (lines 225-235) updated: title changed to "The 80% Reimbursement Rate", proof math corrected to rate=0.80 (4 turns/task, 184 drain, 16 margin)

**Steps:**
1. **[PLANNING]** Read `unified-spec-v1.0.md` lines 225-235 containing the current rate=0.90 proof
2. **[EXECUTION]** Update §3.4 title from "The 90% Reimbursement Rate" to "The 80% Reimbursement Rate"
3. **[EXECUTION]** Replace proof math per spec §4.4 correction: `net_cost = 8 - floor(8 * 0.80) + 2 = 4`, `46 tasks * 4 = 184 drain`, `200 - 184 = 16 margin`
4. **[VERIFICATION]** Confirm mathematical accuracy: `floor(8 * 0.80) = floor(6.4) = 6`, `8 - 6 + 2 = 4`, `46 * 4 = 184`, `200 - 184 = 16`
5. **[COMPLETION]** Record evidence in D-0028 artifact

**Acceptance Criteria:**
- `unified-spec-v1.0.md` §3.4 title reads "The 80% Reimbursement Rate"
- Proof shows: `net_cost_per_task = 8 - 6 + 2 = 4`, `46-task drain = 184`, `margin = 16`
- Mathematical derivation is correct and matches spec §4.1-§4.2
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0028/evidence.md`

**Validation:**
- Manual check: §3.4 proof math matches spec §4.1 derivation (floor model with rate=0.80)
- Evidence: updated spec text captured in evidence artifact

**Dependencies:** T05.02 (§3.1 rate update should precede §3.4 proof update for consistency)
**Rollback:** Revert lines 225-235 to original rate=0.90 proof

---

### T05.04 -- Add budget guidance note for >40 task sprints

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Why | Panel recommendation (Nygard, Round 2; consensus item 3): 16-turn margin is tight; document `initial_budget ≥ 250` for >40 tasks at rate=0.8 |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | `[████████████] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0029/evidence.md`

**Deliverables:**
- Budget guidance note added to spec or CHANGELOG: recommend `initial_budget ≥ 250` for sprints with >40 tasks at rate=0.8

**Steps:**
1. **[PLANNING]** Determine placement: budget guidance should appear in both CHANGELOG (T05.01) and spec addendum
2. **[EXECUTION]** Add budget guidance section to spec: "For sprints with >40 tasks at rate=0.8: recommend `initial_budget ≥ 250`" with supporting math (16-turn margin at budget=200 is tight)
3. **[EXECUTION]** Include secondary recommendation: "For sprints with ≤20 tasks: `initial_budget=200` provides comfortable margin"
4. **[VERIFICATION]** Confirm guidance text matches Nygard's recommendation (Round 2) and spec §4.2 math
5. **[COMPLETION]** Record evidence in D-0029 artifact

**Acceptance Criteria:**
- Budget guidance note exists in spec or documentation with `initial_budget ≥ 250` recommendation for >40 tasks
- Guidance includes supporting rationale (16-turn margin at budget=200)
- Guidance is framed as recommendation (not code change) per panel consensus
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0029/evidence.md`

**Validation:**
- Manual check: budget guidance text exists with specific numeric recommendation (≥250)
- Evidence: guidance text captured in evidence artifact

**Dependencies:** T05.01 (CHANGELOG should include budget guidance; this task ensures spec coverage)
**Rollback:** Remove the added guidance note

---

### Checkpoint: End of Phase 5

**Purpose:** Gate for Phase 6 — confirm all documentation deliverables are complete before end-to-end validation.
**Checkpoint Report Path:** `.dev/releases/current/unified-audit-gating-v2/checkpoints/CP-P05-END.md`

**Verification:**
- D-0026 CHANGELOG entry exists with all three required sections
- D-0027 and D-0028 spec prose updates are mathematically correct and internally consistent
- D-0029 budget guidance note includes specific numeric recommendation

**Exit Criteria:**
- All 4 documentation deliverables (D-0026 through D-0029) have evidence artifacts
- SC-006 (CHANGELOG entry) and SC-007 (spec prose updated) are satisfied
- Phase 6 (end-to-end validation) is unblocked
