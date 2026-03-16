# Phase 6 -- Smoke Validation and Release Gate

Validate operational behavior under realistic execution conditions. This phase is a **hard blocking gate** -- not a release-readiness check that can be skipped under schedule pressure. SC-004 and SC-005 are blocking criteria; the branch does not merge until both are verified.

---

### T06.01 -- Trigger Context Exhaustion Smoke Test and Verify PASS_RECOVERED

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029 |
| Why | PASS_RECOVERED must be visible in operator screen output during actual context exhaustion -- this is the behavioral validation that logging routing works under realistic conditions, not just in unit tests. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (end-to-end behavior), performance (context exhaustion) |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0021/evidence.md

**Deliverables:**
- D-0021: Smoke test evidence showing PASS_RECOVERED visible in operator screen output during context exhaustion scenario, not ERROR

**Steps:**
1. **[PLANNING]** Identify or create a phase configuration that approaches prompt limits to trigger context exhaustion
2. **[EXECUTION]** Trigger context exhaustion on a phase approaching prompt limits
3. **[EXECUTION]** Capture operator screen output during the exhaustion event
4. **[VERIFICATION]** Verify `PASS_RECOVERED` appears in operator screen output (not `ERROR`)
5. **[COMPLETION]** Record screen output capture as evidence

**Acceptance Criteria:**
- Context exhaustion triggered on a phase approaching prompt limits
- `PASS_RECOVERED` visible in operator screen output at TASKLIST_ROOT/artifacts/D-0021/evidence.md
- Status is not `ERROR` — recovery routing works correctly under realistic conditions
- Smoke test evidence is reproducible (scenario documented)

**Validation:**
- Manual check: PASS_RECOVERED appears in operator screen output during context exhaustion
- Evidence: TASKLIST_ROOT/artifacts/D-0021/evidence.md produced with screen output capture

**Dependencies:** T05.04
**Rollback:** TBD
**Notes:** SC-004 implementation. Hard blocking gate — branch does not merge until verified.

---

### T06.02 -- Verify Isolation Enforcement and Cleanup

| Field | Value |
|---|---|
| Roadmap Item IDs | R-030, R-031 |
| Why | This is the primary system objective of the sprint: tasklist-index.md must be mechanically unreachable by isolated subprocesses, and no stale isolation directories must remain after execution. Silent failure (Risk H2) is the highest-severity risk. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (subprocess boundary), data isolation |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0022/evidence.md

**Deliverables:**
- D-0022: Isolation enforcement evidence confirming: (1) `tasklist-index.md` is not resolvable by the isolated subprocess during practical execution, (2) ~14K token reduction per phase confirmed, (3) no stale `.isolation/phase-*` directories remain after execution

**Steps:**
1. **[PLANNING]** Design verification approach for subprocess file resolution scope
2. **[EXECUTION]** Run sprint execution with isolation enabled; attempt to resolve `tasklist-index.md` from subprocess context
3. **[EXECUTION]** Verify `tasklist-index.md` is mechanically unreachable (not just instructionally)
4. **[EXECUTION]** After execution completes, verify no `.isolation/phase-*` directories remain in `config.results_dir`
5. **[VERIFICATION]** Sub-agent (quality-engineer) validates isolation enforcement evidence
6. **[COMPLETION]** Document token reduction estimate (~14K per phase) and enforcement evidence

**Acceptance Criteria:**
- `tasklist-index.md` unreachable in practical subprocess execution at TASKLIST_ROOT/artifacts/D-0022/evidence.md
- ~14K token reduction per phase confirmed
- No stale `.isolation/phase-*` directories present after execution completes
- Evidence reviewed by quality-engineer sub-agent

**Validation:**
- Manual check: tasklist-index.md not resolvable in isolated subprocess; no stale dirs remain
- Evidence: TASKLIST_ROOT/artifacts/D-0022/evidence.md produced

**Dependencies:** T05.04
**Rollback:** TBD — if isolation is not enforced, the sprint objective is not met
**Notes:** SC-005 implementation. Hard blocking gate. Risk H2 (silent failure) mitigation. This is the primary system objective.

---

### T06.03 -- Final Diff Review and Release-Ready Documentation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032, R-033 |
| Why | Final diff review across all 7 modified files ensures no unintended changes shipped; release-ready documentation provides the go/no-go conclusion. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0023/spec.md

**Deliverables:**
- D-0023: Release-ready document with diff review across all 7 modified files (`sprint/process.py`, `pipeline/process.py`, `sprint/executor.py`, `sprint/prompt.py`, `sprint/monitor.py`, `sprint/logging_.py`, `sprint/diagnostics.py`) plus 1 new test file, with go/no-go conclusion

**Steps:**
1. **[PLANNING]** List all 7 modified files and 1 new file from the roadmap Resource Requirements table
2. **[EXECUTION]** Review diff for each file: `sprint/process.py`, `pipeline/process.py`, `sprint/executor.py`, `sprint/prompt.py`, `sprint/monitor.py`, `sprint/logging_.py`, `sprint/diagnostics.py`
3. **[EXECUTION]** Review new file: `tests/sprint/test_phase8_halt_fix.py`
4. **[EXECUTION]** Verify no unintended changes beyond the roadmap scope
5. **[VERIFICATION]** Document go/no-go conclusion
6. **[COMPLETION]** Write release-ready document

**Acceptance Criteria:**
- Release-ready document at TASKLIST_ROOT/artifacts/D-0023/spec.md covers all 7 modified files + 1 new test file (8 total, per roadmap Resource Requirements table)
- Diff review confirms changes match roadmap requirements only
- Go/no-go conclusion documented with supporting evidence; branch confirmed merge-ready
- No unintended changes beyond roadmap scope identified

**Validation:**
- Manual check: All 8 files reviewed with diff summary documented
- Evidence: TASKLIST_ROOT/artifacts/D-0023/spec.md produced

**Dependencies:** T06.01, T06.02
**Rollback:** TBD
**Notes:** Milestone M6.3. Go/no-go documented; branch ready for merge to v2.25.7-phase8.

---

### Checkpoint: End of Phase 6

**Purpose:** Confirm all behavioral validation criteria are met, isolation is enforced, and the branch is release-ready.

**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P06-END.md

**Verification:**
- Recovery status PASS_RECOVERED visible in operator output (M6.1, SC-004)
- Isolation verified: tasklist-index.md unreachable in practical execution; ~14K token reduction per phase confirmed (M6.2, SC-005)
- Go/no-go documented; branch ready for merge (M6.3)

**Exit Criteria:**
- SC-004 (PASS_RECOVERED visible) and SC-005 (token reduction achieved) both satisfied — hard blocking gate
- All 7 modified files and 1 new file diff-reviewed
- Release-ready conclusion documented at TASKLIST_ROOT/artifacts/D-0023/spec.md
