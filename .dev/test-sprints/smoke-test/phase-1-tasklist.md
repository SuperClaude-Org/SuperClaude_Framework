# Phase 1 -- Validation: Source Integrity

Verify all 12 source edits from the unified-audit-gating-v2 release are correctly applied, no residual old values remain, and the configuration is internally consistent. This is a read-only validation phase.

---

### T03.01 -- Grep verification: no remaining max_turns default of 50

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | Ensures no residual `max_turns.*50` default patterns remain in source files after Phase 1 and Phase 2 edits |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | `[████████████] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification (read-only operation) |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- `.dev/test-sprints/smoke-test/artifacts/D-0013/evidence.md`

**Deliverables:**
- Grep report confirming zero `max_turns.*50` default matches in source files (excluding explicit test fixtures)

**Steps:**
1. **[PLANNING]** Identify all source directories to scan: `src/superclaude/cli/`, `.dev/releases/`, `scripts/`
2. **[EXECUTION]** Run `grep -rn 'max_turns.*=.*50\|MAX_TURNS.*=.*50\|max_turns (50)\|default.*50' src/superclaude/cli/ .dev/releases/execute-sprint.sh scripts/rerun-incomplete-phases.sh`
3. **[EXECUTION]** Filter results: exclude lines in test fixtures (files matching `tests/`) and explicit overrides (e.g., `MAX_TURNS=200`)
4. **[VERIFICATION]** Confirm zero matches remain in default declarations
5. **[COMPLETION]** Capture full grep output as evidence in D-0013 artifact

**Acceptance Criteria:**
- `grep -rn 'max_turns.*=.*50' src/superclaude/cli/` returns zero matches
- `grep -n 'MAX_TURNS=50' .dev/releases/execute-sprint.sh` returns zero matches
- `grep -n 'max_turns (50)' scripts/rerun-incomplete-phases.sh` returns zero matches
- Evidence recorded in `.dev/test-sprints/smoke-test/artifacts/D-0013/evidence.md`

**Validation:**
- Manual check: all three grep commands return zero matches (exit code 1, no output)
- Evidence: complete grep output (or empty output confirmation) captured in evidence artifact

**Dependencies:** None
**Rollback:** N/A (read-only verification)

---

### T03.02 -- Grep verification: no remaining reimbursement_rate default of 0.5

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | Ensures no residual `reimbursement_rate.*0.5` default patterns remain in source files |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | `[████████████] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification (read-only operation) |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- `.dev/test-sprints/smoke-test/artifacts/D-0014/evidence.md`

**Deliverables:**
- Grep report confirming zero `reimbursement_rate.*0.5` default matches in source files (excluding explicit test fixtures)

**Steps:**
1. **[PLANNING]** Identify scan scope: `src/superclaude/cli/sprint/models.py` (primary) and broader `src/superclaude/cli/`
2. **[EXECUTION]** Run `grep -rn 'reimbursement_rate.*=.*0.5' src/superclaude/cli/`
3. **[EXECUTION]** Filter results: exclude lines in test fixtures that intentionally use `reimbursement_rate=0.5`
4. **[VERIFICATION]** Confirm zero matches remain in default declarations
5. **[COMPLETION]** Capture full grep output as evidence in D-0014 artifact

**Acceptance Criteria:**
- `grep -rn 'reimbursement_rate.*=.*0.5' src/superclaude/cli/` returns zero matches in default declarations
- Evidence recorded in `.dev/test-sprints/smoke-test/artifacts/D-0014/evidence.md`

**Validation:**
- Manual check: grep command returns zero matches for source default declarations
- Evidence: complete grep output captured in evidence artifact

**Dependencies:** None
**Rollback:** N/A (read-only verification)

---

### T03.03 -- Cross-reference all 12 FRs against file:line targets

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | Provides positive verification that each of the 12 FRs (FR-001 through FR-012) has been correctly applied at its target location |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | `[████████████] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification (read-only operation) |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- `.dev/test-sprints/smoke-test/artifacts/D-0015/evidence.md`

**Deliverables:**
- Cross-reference report: each of the 12 FRs verified at its target file:line with expected value confirmed

**Steps:**
1. **[PLANNING]** Compile the 12 FR target locations from spec
2. **[EXECUTION]** For each FR, read the target file at the target line and confirm the expected value:
   - FR-001: `pipeline/models.py:175` → `max_turns: int = 100`
   - FR-002: `sprint/models.py:285` → `max_turns: int = 100`
   - FR-003: `sprint/commands.py:54` → `default=100`
   - FR-004: `sprint/commands.py:55` → help text "default: 100"
   - FR-005: `sprint/config.py:108` → `max_turns: int = 100`
   - FR-006: `pipeline/process.py:43` → `max_turns: int = 100`
   - FR-007: `sprint/models.py:476` → `reimbursement_rate: float = 0.8`
   - FR-008: `execute-sprint.sh:47` → `MAX_TURNS=100`
   - FR-009: `execute-sprint.sh:14` → "default: 100"
   - FR-010: `rerun-incomplete-phases.sh:4` → "max_turns (100)"
   - FR-011: `roadmap/commands.py:75` → `default=100`
   - FR-012: `roadmap/commands.py:76` → "Default: 100"
3. **[VERIFICATION]** Confirm all 12 FRs verified with expected value at expected location
4. **[COMPLETION]** Record 12-row verification table in D-0015 artifact

**Acceptance Criteria:**
- All 12 FRs confirmed: each target file:line contains the expected value
- Zero discrepancies between spec targets and actual file contents
- Verification table includes FR ID, file, line, expected value, and actual value for each entry
- Evidence recorded in `.dev/test-sprints/smoke-test/artifacts/D-0015/evidence.md`

**Validation:**
- Manual check: 12-row verification table has "PASS" for every FR
- Evidence: complete verification table captured in evidence artifact

**Dependencies:** None
**Rollback:** N/A (read-only verification)

---

### Checkpoint: End of Phase 1

**Purpose:** Confirm all 12 FRs are correctly applied at their target locations.
**Checkpoint Report Path:** `.dev/test-sprints/smoke-test/checkpoints/CP-P01-END.md`

**Verification:**
- D-0013 grep report shows zero residual `max_turns.*50` defaults
- D-0014 grep report shows zero residual `reimbursement_rate.*0.5` defaults
- D-0015 cross-reference table shows all 12 FRs verified at target locations

**Exit Criteria:**
- All 3 validation deliverables (D-0013, D-0014, D-0015) have evidence artifacts
- Zero discrepancies detected across all 12 source edit locations
