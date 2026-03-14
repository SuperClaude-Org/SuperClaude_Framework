# Patch Checklist
Generated: 2026-03-13
Total edits: 7 across 4 files

## File-by-file edit checklist

- phase-3-tasklist.md
  - [ ] Change T03.01 Tier from STANDARD to EXEMPT (from finding H1)
  - [ ] Change T03.01 Verification Method from "Direct test execution" to "Skip verification" (from finding H1)
  - [ ] Change T03.01 MCP Requirements from "Preferred: Sequential, Context7" to "None" (from finding H1)
  - [ ] Change T03.01 Fallback Allowed from "Yes" to "Yes" (no change needed, already Yes)
  - [ ] Change T03.01 Step 3 wording to include "valid skill directory" (from finding M1)
  - [ ] Change T03.02 Step 3 to mention matching command files explicitly (from finding L2)

- phase-6-tasklist.md
  - [ ] Change T06.01 Tier from STRICT to STANDARD (from finding H2)
  - [ ] Change T06.01 Verification Method from "Sub-agent (quality-engineer)" to "Direct test execution" (from finding H2)
  - [ ] Change T06.01 MCP Requirements from "Required: Sequential, Serena | Preferred: Context7" to "Preferred: Sequential, Context7" (from finding H2)
  - [ ] Change T06.01 Fallback Allowed from "No" to "Yes" (from finding H2)
  - [ ] Change T06.01 Sub-Agent Delegation from "Required" to "None" (from finding H2)

- phase-1-tasklist.md
  - [ ] Change T01.01 acceptance criterion 3 to include triage categories (from finding M3)
  - [ ] Change T01.04 Step 4 to note extension trigger condition (from finding L1)

- phase-4-tasklist.md
  - [ ] Change T04.02 acceptance criterion 4 to broaden retry augmentation scope (from finding M2)

- tasklist-index.md
  - [ ] Update Phase 3 tier distribution to EXEMPT: 2, STANDARD: 1 (from finding H1)
  - [ ] Update Phase 6 tier distribution to STRICT: 2, STANDARD: 3 (from finding H2)

## Cross-file consistency sweep
- [ ] Verify Deliverable Registry entries for T03.01 reflect EXEMPT tier (from H1)
- [ ] Verify Deliverable Registry entries for T06.01 reflect STANDARD tier (from H2)
- [ ] Verify Traceability Matrix entries for R-010 reflect EXEMPT tier (from H1)
- [ ] Verify Traceability Matrix entries for R-021 reflect STANDARD tier (from H2)

---

## Precise diff plan

### 1) phase-3-tasklist.md

#### Section/heading to change
- T03.01 metadata table and Step 3

#### Planned edits

**A. Tier field (H1)**
Current issue: `| Tier | STANDARD |`
Change: Replace STANDARD with EXEMPT
Diff intent: `| Tier | EXEMPT |`

**B. Verification Method field (H1)**
Current issue: `| Verification Method | Direct test execution |`
Change: Replace with Skip verification
Diff intent: `| Verification Method | Skip verification |`

**C. MCP Requirements field (H1)**
Current issue: `| MCP Requirements | Preferred: Sequential, Context7 |`
Change: Replace with None
Diff intent: `| MCP Requirements | None |`

**D. Step 3 wording (M1)**
Current issue: `3. **[EXECUTION]** Implement workflow path resolution: verify directory exists and contains \`SKILL.md\``
Change: Add "valid skill directory" framing
Diff intent: `3. **[EXECUTION]** Implement workflow path resolution: resolve to valid skill directory containing \`SKILL.md\``

**E. T03.02 Step 3 wording (L2)**
Current issue: `3. **[EXECUTION]** Implement directory traversal to discover all components under the workflow path`
Change: Add matching command files
Diff intent: `3. **[EXECUTION]** Implement directory traversal to discover all components under the workflow path and locate matching command files`

### 2) phase-6-tasklist.md

#### Section/heading to change
- T06.01 metadata table

#### Planned edits

**A. Tier field (H2)**
Current issue: `| Tier | STRICT |`
Change: Replace STRICT with STANDARD
Diff intent: `| Tier | STANDARD |`

**B. Verification Method field (H2)**
Current issue: `| Verification Method | Sub-agent (quality-engineer) |`
Change: Replace with Direct test execution
Diff intent: `| Verification Method | Direct test execution |`

**C. MCP Requirements field (H2)**
Current issue: `| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |`
Change: Replace with Preferred
Diff intent: `| MCP Requirements | Preferred: Sequential, Context7 |`

**D. Fallback Allowed field (H2)**
Current issue: `| Fallback Allowed | No |`
Change: Replace with Yes
Diff intent: `| Fallback Allowed | Yes |`

**E. Sub-Agent Delegation field (H2)**
Current issue: `| Sub-Agent Delegation | Required |`
Change: Replace with None
Diff intent: `| Sub-Agent Delegation | None |`

### 3) phase-1-tasklist.md

#### Section/heading to change
- T01.01 acceptance criteria, T01.04 Step 4

#### Planned edits

**A. T01.01 acceptance criterion 3 (M3)**
Current issue: `- Each decision has a \`[Blocking Phase N]\` or \`[Advisory]\` annotation`
Change: Add triage categories
Diff intent: `- Each decision is triaged as (1) must-resolve, (2) safe defaults, or (3) defer-to-follow-up, with \`[Blocking Phase N]\` or \`[Advisory]\` annotations`

**B. T01.04 Step 4 (L1)**
Current issue: `4. **[EXECUTION]** Document extension policy for Phase 4 additions`
Change: Note trigger condition
Diff intent: `4. **[EXECUTION]** Document extension policy: vocabulary extends during Phase 4 (subprocess orchestration) when subprocess behavior is understood`

### 4) phase-4-tasklist.md

#### Section/heading to change
- T04.02 acceptance criteria

#### Planned edits

**A. T04.02 acceptance criterion 4 (M2)**
Current issue: `- Retry augmentation includes specific placeholder names (for \`{{SC_PLACEHOLDER:*}}\` residue) in retry prompts`
Change: Broaden to targeted failures
Diff intent: `- Retry augmentation supports targeted failures (especially \`{{SC_PLACEHOLDER:*}}\` placeholder residue) in retry prompts`

### 5) tasklist-index.md

#### Section/heading to change
- Phase Files table, Deliverable Registry, Traceability Matrix

#### Planned edits

**A. Phase 3 tier distribution (H1)**
Current issue: `| 3 | phase-3-tasklist.md | Fast Deterministic Steps | T03.01-T03.03 | STRICT: 0, STANDARD: 2, LIGHT: 0, EXEMPT: 1 |`
Change: T03.01 moves from STANDARD to EXEMPT
Diff intent: `| 3 | phase-3-tasklist.md | Fast Deterministic Steps | T03.01-T03.03 | STRICT: 0, STANDARD: 1, LIGHT: 0, EXEMPT: 2 |`

**B. Phase 6 tier distribution (H2)**
Current issue: `| 6 | phase-6-tasklist.md | Quality Amplification | T06.01-T06.05 | STRICT: 3, STANDARD: 2, LIGHT: 0, EXEMPT: 0 |`
Change: T06.01 moves from STRICT to STANDARD
Diff intent: `| 6 | phase-6-tasklist.md | Quality Amplification | T06.01-T06.05 | STRICT: 2, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |`

**C. Deliverable Registry: D-0012, D-0013 tier (H1)**
Current issue: Tier column shows STANDARD for D-0012 and D-0013
Change: Update to EXEMPT
Diff intent: Change Tier to EXEMPT and Verification to Skip for D-0012, D-0013

**D. Deliverable Registry: D-0028, D-0029, D-0049 tier (H2)**
Current issue: Tier column shows STRICT for D-0028, D-0029, D-0049
Change: Update to STANDARD
Diff intent: Change Tier to STANDARD and Verification to Direct test for D-0028, D-0029, D-0049

**E. Traceability Matrix: R-010 tier (H1)**
Current issue: Tier shows STANDARD for R-010
Change: Update to EXEMPT
Diff intent: Change Tier to EXEMPT for R-010

**F. Traceability Matrix: R-021 tier (H2)**
Current issue: Tier shows STRICT for R-021
Change: Update to STANDARD
Diff intent: Change Tier to STANDARD for R-021
