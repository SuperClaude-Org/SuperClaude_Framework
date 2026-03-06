# Phase 2 -- Shell & CLI Alignment

Apply the 5 panel-identified edits (Tier 1.5) in shell scripts and roadmap CLI to eliminate configuration drift between Python defaults and external entry points. These locations were identified by the expert panel (Wiegers, Round 1) as hidden coupling points.

---

### T02.01 -- Set execute-sprint.sh MAX_TURNS to 100

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | Shell script hardcodes `MAX_TURNS=50`, creating configuration drift with the Python default of 100 set in Phase 1 |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[██████████] 55%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0008/evidence.md`

**Deliverables:**
- `MAX_TURNS` variable set to `100` at `.dev/releases/execute-sprint.sh:47`

**Steps:**
1. **[PLANNING]** Read `.dev/releases/execute-sprint.sh` and locate line 47 containing `MAX_TURNS=50`
2. **[PLANNING]** Confirm this is the default assignment, not an override or conditional
3. **[EXECUTION]** Edit `.dev/releases/execute-sprint.sh:47` to read `MAX_TURNS=100`
4. **[VERIFICATION]** Run `grep -n 'MAX_TURNS=50' .dev/releases/execute-sprint.sh` and confirm zero matches
5. **[COMPLETION]** Record evidence in D-0008 artifact

**Acceptance Criteria:**
- File `.dev/releases/execute-sprint.sh` line 47 reads `MAX_TURNS=100`
- No other `MAX_TURNS` assignments in the script were modified (line 32 has `MAX_TURNS=200` explicit override — Tier 3, no change)
- Edit is a single-value replacement
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0008/evidence.md`

**Validation:**
- Manual check: `grep -n 'MAX_TURNS' .dev/releases/execute-sprint.sh` shows `100` at line 47 and `200` at line 32 (unchanged)
- Evidence: grep output captured in evidence artifact

**Dependencies:** T01.01-T01.07 (Phase 1 must be complete; Python defaults established first)
**Rollback:** Revert line 47 to `MAX_TURNS=50`
**Notes:** FR-008 traceability. Panel-identified hidden coupling point (Wiegers, Round 1).

---

### T02.02 -- Update execute-sprint.sh help text to "default: 100"

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | Help text must accurately reflect the new `MAX_TURNS` default for script users |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[██████████] 55%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0009/evidence.md`

**Deliverables:**
- Help text at `.dev/releases/execute-sprint.sh:14` updated to reference "default: 100"

**Steps:**
1. **[PLANNING]** Read `.dev/releases/execute-sprint.sh` and locate line 14 containing help text with "default: 50"
2. **[PLANNING]** Confirm this is the usage/help section of the script
3. **[EXECUTION]** Edit `.dev/releases/execute-sprint.sh:14` to replace "default: 50" with "default: 100"
4. **[VERIFICATION]** Run `grep -n 'default: 50' .dev/releases/execute-sprint.sh` and confirm zero matches
5. **[COMPLETION]** Record evidence in D-0009 artifact

**Acceptance Criteria:**
- File `.dev/releases/execute-sprint.sh` line 14 help text reads "default: 100"
- No other help text strings in the script were modified
- Edit is a string replacement within the help/usage section only
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0009/evidence.md`

**Validation:**
- Manual check: `grep -n 'default: 100' .dev/releases/execute-sprint.sh` shows match at line 14
- Evidence: grep output captured in evidence artifact

**Dependencies:** T02.01 (help text should match the variable default in the same file)
**Rollback:** Revert line 14 help text to "default: 50"

---

### T02.03 -- Update rerun-incomplete-phases.sh comment to "max_turns (100)"

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | Historical context comment references the old default value; must be updated for accuracy |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | LIGHT |
| Confidence | `[██████████] 72%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Quick sanity check |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0010/evidence.md`

**Deliverables:**
- Comment at `scripts/rerun-incomplete-phases.sh:4` updated to read "max_turns (100)"

**Steps:**
1. **[PLANNING]** Read `scripts/rerun-incomplete-phases.sh` and locate line 4 containing "max_turns (50)"
2. **[EXECUTION]** Edit `scripts/rerun-incomplete-phases.sh:4` to replace "max_turns (50)" with "max_turns (100)"
3. **[VERIFICATION]** Quick sanity check: line 4 reads "max_turns (100)"
4. **[COMPLETION]** Record evidence in D-0010 artifact

**Acceptance Criteria:**
- File `scripts/rerun-incomplete-phases.sh` line 4 reads "max_turns (100)"
- No other lines in the script were modified (line 32 `MAX_TURNS=200` is Tier 3 — no change)
- Comment-only change with no functional impact
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0010/evidence.md`

**Validation:**
- Manual check: `head -5 scripts/rerun-incomplete-phases.sh` shows "max_turns (100)" at line 4
- Evidence: command output captured in evidence artifact

**Dependencies:** T01.01-T01.07 (Phase 1 must be complete)
**Rollback:** Revert line 4 to "max_turns (50)"
**Notes:** Tier classified as LIGHT — comment-only update with no functional impact. FR-010 traceability.

---

### T02.04 -- Set roadmap CLI --max-turns default to 100

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | Roadmap CLI entry point must match sprint pipeline defaults to prevent cross-layer configuration drift |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[██████████] 55%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0011/evidence.md`

**Deliverables:**
- Roadmap CLI `--max-turns` option default changed from `50` to `100` at `src/superclaude/cli/roadmap/commands.py:75`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/commands.py` and locate line 75 containing `default=50`
2. **[PLANNING]** Confirm this is the roadmap CLI `--max-turns` Click option definition
3. **[EXECUTION]** Edit `src/superclaude/cli/roadmap/commands.py:75` to read `default=100`
4. **[VERIFICATION]** Run `grep -n 'default=50' src/superclaude/cli/roadmap/commands.py` and confirm zero matches
5. **[COMPLETION]** Record evidence in D-0011 artifact

**Acceptance Criteria:**
- File `src/superclaude/cli/roadmap/commands.py` line 75 reads `default=100`
- The Click option definition for `--max-turns` is the only changed line
- Change is backwards-compatible (explicit `--max-turns=50` still works)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0011/evidence.md`

**Validation:**
- Manual check: `grep -n 'default=' src/superclaude/cli/roadmap/commands.py` shows `100` at line 75
- Evidence: grep output captured in evidence artifact

**Dependencies:** T01.01-T01.07 (Phase 1 Python defaults established first)
**Rollback:** Revert line 75 to `default=50`
**Notes:** Panel-identified location (Wiegers, Round 1). FR-011 traceability.

---

### T02.05 -- Update roadmap CLI --max-turns help text to "Default: 100"

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | Help text must accurately reflect the new default value for roadmap CLI users |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[██████████] 55%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0012/evidence.md`

**Deliverables:**
- Roadmap CLI `--max-turns` help text updated to "Default: 100" at `src/superclaude/cli/roadmap/commands.py:76`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/commands.py` and locate line 76 containing help text with "Default: 50"
2. **[EXECUTION]** Edit `src/superclaude/cli/roadmap/commands.py:76` to replace "Default: 50" with "Default: 100"
3. **[VERIFICATION]** Run `grep -n 'Default: 50' src/superclaude/cli/roadmap/commands.py` and confirm zero matches
4. **[COMPLETION]** Record evidence in D-0012 artifact

**Acceptance Criteria:**
- File `src/superclaude/cli/roadmap/commands.py` line 76 help string reads "Default: 100"
- No other help text strings in the file were modified
- String replacement is exact ("50" → "100" within help text context only)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0012/evidence.md`

**Validation:**
- Manual check: `grep -n 'Default: 100' src/superclaude/cli/roadmap/commands.py` shows match at line 76
- Evidence: grep output captured in evidence artifact

**Dependencies:** T02.04 (help text should match the default value in the same file)
**Rollback:** Revert line 76 help text to "Default: 50"

---

### Checkpoint: End of Phase 2

**Purpose:** Gate for Phase 3 — confirm all 5 Tier 1.5 shell/CLI edits are applied, establishing full configuration alignment before source integrity validation.
**Checkpoint Report Path:** `.dev/releases/current/unified-audit-gating-v2/checkpoints/CP-P02-END.md`

**Verification:**
- All 5 deliverables (D-0008 through D-0012) have evidence artifacts confirming the edit
- `grep -rn 'MAX_TURNS=50' .dev/releases/` returns zero matches (only `MAX_TURNS=200` explicit override remains)
- `grep -rn 'default=50\|Default: 50\|default: 50' src/superclaude/cli/roadmap/` returns zero matches

**Exit Criteria:**
- All 12 source edits (Phase 1 + Phase 2) are in place
- No configuration drift between Python defaults, CLI defaults, and shell script defaults
- Phase 3 (validation) is unblocked
