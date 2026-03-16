# Phase 4 -- Diagnostics and Status Fixes

Make outcome handling architecturally consistent across logging and diagnostics. Fix PASS_RECOVERED routing, consolidate path resolution in FailureClassifier, and complete the PASS_RECOVERED parity audit. This phase can proceed concurrently with Phase 3 after Phase 1 completes.

---

### T04.01 -- Route PASS_RECOVERED to INFO Branch in SprintLogger

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | PASS_RECOVERED must appear in operator screen output as a success-class result, not be silently dropped or routed to ERROR. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0013/evidence.md

**Deliverables:**
- D-0013: `PhaseStatus.PASS_RECOVERED` added to the INFO routing branch in `SprintLogger.write_phase_result()` in `src/superclaude/cli/sprint/logging_.py` (same branch as `PASS` and `PASS_NO_REPORT`)

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/logging_.py` and locate `SprintLogger.write_phase_result()` method
2. **[PLANNING]** Identify the existing INFO routing branch that handles `PASS` and `PASS_NO_REPORT`
3. **[EXECUTION]** Add `PhaseStatus.PASS_RECOVERED` to the INFO routing branch condition
4. **[VERIFICATION]** `uv run pytest tests/sprint/ -v --tb=short` exits 0
5. **[COMPLETION]** Record evidence of PASS_RECOVERED INFO routing

**Acceptance Criteria:**
- `PhaseStatus.PASS_RECOVERED` appears in the same routing branch as `PASS` and `PASS_NO_REPORT` in `write_phase_result()`
- PASS_RECOVERED status produces INFO-level output visible to operators
- `uv run pytest tests/sprint/ -v --tb=short` exits 0
- No changes to other PhaseStatus routing branches

**Validation:**
- Manual check: `uv run pytest tests/sprint/ -v --tb=short` exits 0
- Evidence: TASKLIST_ROOT/artifacts/D-0013/evidence.md produced

**Dependencies:** T01.01
**Rollback:** Remove PASS_RECOVERED from INFO branch
**Notes:** FR-013 implementation. Milestone M4.1.

---

### T04.02 -- Add config to DiagnosticBundle and Update FailureClassifier

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022, R-023 |
| Why | FailureClassifier uses hardcoded output-file path construction which breaks when directory layouts change. Consolidating path resolution around SprintConfig via DiagnosticBundle makes it canonical and maintainable. |
| Effort | M |
| Risk | Low |
| Risk Drivers | refactor (multi-file scope change) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0014, D-0015 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0014/evidence.md
- TASKLIST_ROOT/artifacts/D-0015/evidence.md

**Deliverables:**
- D-0014: `config: SprintConfig | None = None` keyword-only parameter added to `DiagnosticBundle` in `src/superclaude/cli/sprint/diagnostics.py` with `None` default and deprecation warning when `config=None` is used
- D-0015: `FailureClassifier.classify()` updated to use `bundle.config.output_file(bundle.phase_result.phase)` instead of hardcoded path construction; falls back to legacy path with deprecation warning if `config is None`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/diagnostics.py` and locate `DiagnosticBundle` class and `FailureClassifier.classify()` method
2. **[PLANNING]** Identify current hardcoded path construction in `FailureClassifier.classify()`
3. **[EXECUTION]** Add `*, config: SprintConfig | None = None` keyword-only parameter to `DiagnosticBundle`
4. **[EXECUTION]** Add deprecation warning when `DiagnosticBundle` is constructed with `config=None`: `warnings.warn("DiagnosticBundle.config=None is deprecated; pass SprintConfig", DeprecationWarning)`
5. **[EXECUTION]** Update `FailureClassifier.classify()` to use `bundle.config.output_file(bundle.phase_result.phase)` when `bundle.config` is not None
6. **[EXECUTION]** If `bundle.config is None`: use existing hardcoded path as fallback and emit deprecation warning via `warnings.warn()`
7. **[VERIFICATION]** Verify all existing DiagnosticBundle construction sites still compile with None default
8. **[COMPLETION]** Record evidence of config-driven path resolution and deprecation warnings

**Acceptance Criteria:**
- `DiagnosticBundle` accepts `config: SprintConfig | None = None` as keyword-only parameter in `src/superclaude/cli/sprint/diagnostics.py`
- `FailureClassifier.classify()` uses `bundle.config.output_file(bundle.phase_result.phase)` when config is available
- `config=None` path logs deprecation warning and falls back to legacy hardcoded path
- All existing `DiagnosticBundle` construction sites compile unchanged with None default

**Validation:**
- Manual check: `uv run pytest tests/sprint/ -v --tb=short` exits 0
- Evidence: TASKLIST_ROOT/artifacts/D-0014/evidence.md and TASKLIST_ROOT/artifacts/D-0015/evidence.md produced

**Dependencies:** T01.01
**Rollback:** Revert DiagnosticBundle config parameter and FailureClassifier path changes
**Notes:** FR-014/FR-015 implementation. Milestones M4.2, M4.3. Deprecation warning adopted from Variant A for long-term migration value.

---

### T04.03 -- Complete PASS_RECOVERED Parity Grep Audit

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | All `PhaseStatus.PASS` switch sites must handle `PASS_RECOVERED` consistently. The grep audit from T01.01 (D-0002) identifies gaps; this task resolves them. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0016/notes.md

**Deliverables:**
- D-0016: PASS_RECOVERED parity audit document listing all `PhaseStatus.PASS` switch sites identified in D-0002, confirming parity with `PASS_RECOVERED` handling at each site, with any remaining gaps documented or resolved

**Steps:**
1. **[PLANNING]** Read D-0002 (PhaseStatus.PASS grep audit from T01.01) to get the inventory of switch sites
2. **[EXECUTION]** For each identified switch site, check whether `PASS_RECOVERED` is handled alongside `PASS`
3. **[EXECUTION]** Resolve any parity gaps found (add `PASS_RECOVERED` handling where missing)
4. **[EXECUTION]** Document all sites and their parity status
5. **[VERIFICATION]** All switch sites have `PASS_RECOVERED` parity or documented exemption
6. **[COMPLETION]** Record audit results in D-0016

**Acceptance Criteria:**
- PASS_RECOVERED parity audit document at TASKLIST_ROOT/artifacts/D-0016/notes.md lists all PhaseStatus.PASS switch sites
- Each site marked as "parity confirmed" or "gap resolved" or "documented with rationale"
- No remaining unresolved parity gaps at blocking severity
- `uv run pytest tests/sprint/ -v --tb=short` exits 0

**Validation:**
- Manual check: All PhaseStatus.PASS switch sites reviewed and documented
- Evidence: TASKLIST_ROOT/artifacts/D-0016/notes.md produced

**Dependencies:** T01.01, T04.01
**Rollback:** TBD
**Notes:** Milestone M4.4. Named task — blocking deliverable for Phase 5 per roadmap; Phase 5 tasks T05.01-T05.04 must not begin until T04.03 is accepted. Audit scope is the PhaseStatus.PASS switch sites identified in M1.0 (D-0002). Treats PASS_RECOVERED as a policy invariant going forward.

---

### Checkpoint: End of Phase 4

**Purpose:** Confirm diagnostics and status consistency fixes are complete: PASS_RECOVERED routing, config-driven path resolution, and parity audit.

**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P04-END.md

**Verification:**
- PASS_RECOVERED routes through INFO branch and is screen-visible as a success-class result (M4.1)
- FailureClassifier uses SprintConfig-canonical path resolution (M4.2)
- DiagnosticBundle backward-compatible with None default; config=None logs deprecation (M4.3)

**Exit Criteria:**
- Milestones M4.1, M4.2, M4.3, M4.4 all satisfied
- `uv run pytest tests/sprint/ -v --tb=short` exits 0
- PASS_RECOVERED parity audit complete with all gaps documented or resolved
