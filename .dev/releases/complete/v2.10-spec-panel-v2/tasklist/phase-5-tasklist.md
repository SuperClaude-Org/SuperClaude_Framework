# Phase 5 -- Validation and Release

Phase 5 is Gate B: end-to-end validation of all capabilities (SP-1 through SP-4) working together, integration point verification, cumulative overhead measurement, quality metric validation, and go/no-go release decision.

---

### T05.01 -- Execute End-to-End Validation Suite and Assemble Gate B Evidence

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033, R-034, R-035 |
| Why | Gate B requires end-to-end validation on 3 representative specs, cumulative overhead measurement (<25% standard, <40% correctness focus), and a consolidated evidence pack. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | end-to-end validation scope, performance (cumulative overhead) |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0032, D-0033, D-0034 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0032/evidence.md`
- `TASKLIST_ROOT/artifacts/D-0033/evidence.md`
- `TASKLIST_ROOT/artifacts/D-0034/evidence.md`

**Deliverables:**
1. End-to-end validation suite results on 3 representative specifications: correctness-heavy spec, pipeline-heavy spec, baseline spec (no state/pipelines)
2. Gate B evidence pack: end-to-end metrics dashboard, risk review (R-1 through R-6), integration verification report
3. Cumulative overhead measurement: <25% without `--focus correctness`; <40% with `--focus correctness` per D7.3

**Steps:**
1. **[PLANNING]** Select 3 representative specifications per D7.1: one correctness-heavy, one pipeline-heavy, one baseline
2. **[PLANNING]** Define expected outputs per spec type: correctness-heavy should produce State Variable Registry + boundary table + Whittaker findings; pipeline-heavy should produce Quantity Flow Diagram + CRITICAL findings; baseline should produce standard output with no correctness artifacts
3. **[EXECUTION]** Run spec-panel on all 3 specs: baseline mode and `--focus correctness` mode; capture full outputs
4. **[EXECUTION]** Measure cumulative token overhead for both modes against original baseline (pre-enhancement)
5. **[EXECUTION]** Compile Gate B evidence pack: metrics dashboard, risk review against R-1 through R-6, integration verification
6. **[VERIFICATION]** Verify overhead <25% (standard) and <40% (correctness focus) per SC-004; all expected outputs present per spec type
7. **[COMPLETION]** Record validation results and evidence pack at intended artifact paths

**Acceptance Criteria:**
- Validation results at `TASKLIST_ROOT/artifacts/D-0032/evidence.md` cover all 3 spec types with expected outputs verified
- Gate B evidence pack at `TASKLIST_ROOT/artifacts/D-0033/evidence.md` contains metrics dashboard, R-1 through R-6 risk review, and integration verification
- Cumulative overhead at `TASKLIST_ROOT/artifacts/D-0034/evidence.md` shows <25% standard and <40% correctness focus per SC-004
- Traceable to R-033, R-034, R-035 via D-0032, D-0033, D-0034

**Validation:**
- Manual check: All 3 spec validations documented; overhead within budget; evidence pack contains all required sections
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0032/evidence.md`, `D-0033/evidence.md`, `D-0034/evidence.md`

**Dependencies:** T04.06 (Phase 4 overhead validated), T03.02 (Gate A passed)
**Rollback:** N/A (validation task; no specification changes)

---

### T05.02 -- Verify Integration Points and Quality Metrics

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036, R-037 |
| Why | D7.4 requires all 5 integration points to produce valid parseable output; D7.5 requires quality metrics: formulaic <50%, FP <30%, findings >=2, GAP >0. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | multi-component integration, audit |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0035, D-0036 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0035/evidence.md`
- `TASKLIST_ROOT/artifacts/D-0036/evidence.md`

**Deliverables:**
1. Integration point verification: all 5 points (SP-3→AD-1, SP-2→AD-2, SP-1→AD-5, SP-4→RM-3, SP-2→RM-2) produce valid parseable output per D7.4
2. Quality metric validation: formulaic entries <50% (SC-005), auto-suggestion FP rate <30% (NFR-8), adversarial findings >=2 per mutable-state review (SC-003), GAP cells >0 per review with guard conditions (SC-002)

**Steps:**
1. **[PLANNING]** Identify each of the 5 integration points and their expected output formats
2. **[PLANNING]** Define quality metric measurement methodology for each of the 4 metrics
3. **[EXECUTION]** Verify each integration point produces machine-parseable output that downstream consumers can parse
4. **[EXECUTION]** Measure quality metrics from the 3 representative spec runs (T05.01): count formulaic entries, measure FP rate, count adversarial findings, count GAP cells
5. **[VERIFICATION]** Verify all 5 integration points produce valid output; all 4 quality metrics meet thresholds
6. **[COMPLETION]** Record verification results and quality measurements in evidence artifacts

**Acceptance Criteria:**
- Integration verification at `TASKLIST_ROOT/artifacts/D-0035/evidence.md` confirms all 5 integration points produce valid parseable output
- Quality metrics at `TASKLIST_ROOT/artifacts/D-0036/evidence.md` show: formulaic <50%, FP <30%, findings >=2 per mutable-state review, GAP >0 per guard-condition review
- Each integration point tested with representative output from T05.01 validation runs
- Traceable to R-036 and R-037 via D-0035 and D-0036

**Validation:**
- Manual check: All 5 integration points verified; all 4 quality metrics documented with pass/fail against thresholds
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0035/evidence.md` and `TASKLIST_ROOT/artifacts/D-0036/evidence.md`

**Dependencies:** T05.01 (validation suite provides the data for integration and quality checks)
**Rollback:** N/A (verification task; no specification changes)

---

### T05.03 -- Issue Go/No-Go Decision with Rollback Plan and Release Documentation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-038 |
| Why | D7.6 requires explicit go/no-go decision with rationale and rollback plan; D7.7 requires release documentation (changelog, version bump, migration notes). |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0037, D-0038, D-0039 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0037/spec.md`
- `TASKLIST_ROOT/artifacts/D-0038/spec.md`
- `TASKLIST_ROOT/artifacts/D-0039/spec.md`

**Deliverables:**
1. Go/no-go decision record with explicit rationale referencing Gate B evidence per D7.6
2. Rollback plan specifying reversion steps for each phase (remove Whittaker persona, remove boundary table, remove correctness focus, remove pipeline analysis) documented before release authorization per D7.6
3. Release documentation: updated changelog with all 4 capabilities (SP-1 through SP-4), version bump, migration notes if any per D7.7

**Steps:**
1. **[PLANNING]** Review Gate B evidence pack (D-0033), integration verification (D-0035), and quality metrics (D-0036)
2. **[PLANNING]** Assess all evidence against release criteria: overhead within budget, integration points valid, quality metrics met
3. **[EXECUTION]** Write go/no-go decision record with rationale referencing specific evidence artifacts
4. **[EXECUTION]** Write rollback plan: phase-by-phase reversion steps (Phase 1 persona removal, Phase 2 boundary table removal, Phase 4 correctness focus and pipeline analysis removal)
5. **[EXECUTION]** Write release documentation: changelog entries for SP-1 through SP-4, version bump, migration notes (if breaking changes exist)
6. **[VERIFICATION]** Verify decision references evidence; rollback plan covers all phases; changelog covers all 4 capabilities
7. **[COMPLETION]** Record all three deliverables at intended artifact paths

**Acceptance Criteria:**
- Go/no-go decision at `TASKLIST_ROOT/artifacts/D-0037/spec.md` contains explicit decision with evidence-based rationale
- Rollback plan at `TASKLIST_ROOT/artifacts/D-0038/spec.md` specifies reversion steps for each phase
- Release documentation at `TASKLIST_ROOT/artifacts/D-0039/spec.md` includes changelog for SP-1 through SP-4 with version bump
- Traceable to R-038 via D-0037, D-0038, D-0039

**Validation:**
- Manual check: Decision record, rollback plan, and release documentation are complete with all required sections
- Evidence: linkable artifacts produced at `TASKLIST_ROOT/artifacts/D-0037/spec.md`, `D-0038/spec.md`, `D-0039/spec.md`

**Dependencies:** T05.02 (integration and quality verification complete)
**Rollback:** N/A (decision and documentation task)

---

### Checkpoint: End of Phase 5

**Purpose:** Confirm Gate B is complete: end-to-end validation passed, integration verified, quality metrics met, release decision issued.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P05-END.md`

**Verification:**
- End-to-end validation suite passed on all 3 representative specs (D-0032)
- All 5 integration points produce valid parseable output (D-0035)
- All 4 quality metrics meet thresholds (D-0036)

**Exit Criteria:**
- All deliverables D-0032 through D-0039 have evidence artifacts
- Go/no-go decision issued with evidence-based rationale (D-0037)
- Rollback plan documented (D-0038) and release documentation complete (D-0039)
