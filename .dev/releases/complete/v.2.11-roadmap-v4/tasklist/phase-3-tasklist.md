# Phase 3 -- Guard and Sentinel Analysis

Implement Proposal 3 (Guard and Sentinel Analysis). For each deliverable introducing conditional logic (guards, sentinels, flags, early returns), enumerate all states of the guard variable, detect ambiguous states where one value maps to multiple semantic meanings, and require disambiguation or documented accepted risk. M3 depends on M2 for FMEA severity classification to determine whether guard ambiguity constitutes silent corruption.

---

### T03.01 -- Implement guard and sentinel analyzer with state enumeration and ambiguity detection

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027, R-028 |
| Why | The analyzer detects guards (if/else, early return, sentinel values, flag checks) and type changes (bool->int, enum->string). For each guard, it enumerates all possible values and semantic meanings, flagging ambiguity when one value maps to multiple meanings (e.g., `0` means both "no events" and "start offset"). Bool->int type changes always trigger transition analysis. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | multi-file |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0031, D-0032 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0031/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0032/evidence.md

**Deliverables:**
1. Guard and sentinel analyzer detecting guards (if/else, early return, sentinel values, flag checks), type changes (bool->int, enum->string), enumerating all guard values with semantic meanings, and flagging ambiguity when one value maps to multiple meanings (D-0031)
2. Test suite: "Replace boolean replay guard with integer offset" -> ambiguity for value `0`, boolean with clear semantics -> no flag, enum with exhaustive match -> no flag, integer without documented zero/negative semantics -> flagged, bool->int always triggers transition analysis (D-0032)

**Steps:**
1. **[PLANNING]** Review M1 behavioral detection heuristic (T01.03) for overlap; guard analyzer is complementary (detects conditional logic, not computational verbs)
2. **[PLANNING]** Compile guard detection patterns: if/else, early return, sentinel values, flag checks, type changes
3. **[EXECUTION]** Implement guard detector identifying conditional logic patterns in deliverable descriptions
4. **[EXECUTION]** Implement state enumerator listing all possible values and semantic meanings per guard variable
5. **[EXECUTION]** Implement ambiguity detector: flag when one value maps to multiple meanings; bool->int always triggers transition analysis
6. **[VERIFICATION]** Run five-scenario test suite via sub-agent quality-engineer
7. **[COMPLETION]** Document guard detection patterns and ambiguity criteria in spec artifact at D-0031 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0031/spec.md` exists documenting guard detection patterns, state enumeration algorithm, and ambiguity flagging criteria
- "Replace boolean replay guard with integer offset" produces ambiguity flag for value `0` with both semantic meanings documented
- Boolean guard with clear true/false semantics produces no ambiguity flag
- Bool->int type change always triggers transition analysis regardless of ambiguity status

**Validation:**
- Manual check: run analyzer on all five test descriptions and verify state enumeration and ambiguity flagging outputs
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0032/evidence.md`

**Dependencies:** T01.03, T02.09
**Rollback:** Remove guard analyzer; guard ambiguity detection is manual
**Notes:** R-009 mitigation: `@no-ambiguity-check` annotation suppresses detection with documented rationale. R-010: seed with known archetypes.

---

### T03.02 -- Implement guard resolution requirement with disambiguation deliverables and Release Gate Rule 2

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029, R-030 |
| Why | Ambiguous guards generate guard_test deliverables requiring: explicit documentation of every guard value's semantic meaning, test that each semantic state maps to exactly one value, and for type transitions, test that all pre-transition semantic states have post-transition equivalents. Unresolved ambiguity activates Release Gate Rule 2 with mandatory owner field. |
| Effort | M |
| Risk | High |
| Risk Drivers | system-wide, breaking change |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0033, D-0034 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0033/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0034/evidence.md

**Deliverables:**
1. Guard resolution generating `kind=guard_test` deliverables for ambiguous guards: documentation of every guard value's semantic meaning, uniqueness test (each semantic state maps to exactly one value), type transition mapping test (all pre-transition states have post-transition equivalents), and Release Gate Rule 2 enforcement (unresolved ambiguity -> mandatory owner + review date) (D-0033)
2. Test suite: ambiguous integer guard -> >=2 guard_test deliverables + release gate warning with mandatory owner, unambiguous boolean -> zero guard deliverables, bool->3-state enum -> transition mapping deliverable, accepted-risk rationale is non-empty string with owner name (D-0034)

**Steps:**
1. **[PLANNING]** Load guard analyzer output from T03.01 to identify ambiguous guards requiring resolution
2. **[PLANNING]** Define guard_test deliverable template: semantic documentation + uniqueness test + transition mapping
3. **[EXECUTION]** Implement guard_test deliverable generation for each ambiguous guard
4. **[EXECUTION]** Implement Release Gate Rule 2: unresolved ambiguity produces blocking warning with mandatory owner field and review date
5. **[EXECUTION]** Implement accepted-risk pathway: requires non-empty rationale string with owner name
6. **[VERIFICATION]** Run four-scenario test suite via sub-agent quality-engineer including release gate verification
7. **[COMPLETION]** Document guard resolution logic and Rule 2 enforcement in spec artifact at D-0033 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0033/spec.md` exists documenting guard_test generation, Release Gate Rule 2 trigger conditions, and accepted-risk pathway
- Ambiguous integer guard produces at minimum 2 guard_test deliverables (semantic documentation + uniqueness test) plus release gate warning
- Unambiguous boolean guard produces zero guard_test deliverables and no release gate warning
- Accepted-risk rationale requires non-empty string with owner name (empty string or missing owner rejected)

**Validation:**
- Manual check: verify guard_test output for ambiguous integer, unambiguous boolean, and bool->3-state enum scenarios
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0034/evidence.md`

**Dependencies:** T03.01, T02.09
**Rollback:** Remove guard resolution and Rule 2 enforcement; guard ambiguity is informational only
**Notes:** R-011 mitigation: Release Gate Rule 2 is a blocking condition, not advisory. Pipeline must fail to advance without owner assignment.

---

### T03.03 -- Integrate guard analysis as post-generation pass after M2 combined pass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031, R-032 |
| Why | Guard analysis runs after M2 combined pass, cross-referencing invariant predicates (to verify guard variables have registered invariants) and FMEA severity (to determine if guard ambiguity elevation to silent corruption is warranted). Output: guard analysis section with state enumeration tables, ambiguity flags, and gate warnings. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | pipeline, multi-file |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0035, D-0036 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0035/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0036/evidence.md

**Deliverables:**
1. Guard analysis pipeline pass registered after M2 combined pass, cross-referencing invariant predicates and FMEA severity, producing guard analysis section with state enumeration tables, ambiguity flags, guard_test deliverables in correct milestones, and gate warnings (D-0035)
2. Integration tests: (1) roadmap with type-migration deliverable (bool->int) -> guard analysis section present, ambiguity for `0` detected, release gate warning with mandatory owner field, guard_test deliverables in correct milestone; (2) boolean guard with clear semantics -> no ambiguity flags, no release gate (D-0036)

**Steps:**
1. **[PLANNING]** Review pipeline execution order: M1 decomposition -> M2 combined pass -> M3 guard analysis
2. **[PLANNING]** Identify cross-reference points: invariant predicates (M2) for guard variable invariant checking, FMEA severity (M2) for silent corruption elevation
3. **[EXECUTION]** Register guard analysis pass in pipeline after M2 combined pass
4. **[EXECUTION]** Implement cross-referencing: verify guard variables have registered invariants; use FMEA severity for ambiguity elevation to silent corruption
5. **[EXECUTION]** Generate guard analysis output section: state enumeration tables, ambiguity flags, gate warnings
6. **[VERIFICATION]** Run both integration tests via sub-agent quality-engineer: type-migration and clear-boolean scenarios
7. **[COMPLETION]** Document pipeline position, cross-reference schema, and output format in spec artifact at D-0035 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0035/spec.md` exists documenting pipeline position, cross-reference schema, and output section format
- Type-migration (bool->int) deliverable produces guard analysis section with ambiguity for `0` and release gate warning with mandatory owner
- Boolean guard with clear semantics produces no ambiguity flags and no release gate warning
- Guard analysis cross-references M2 invariant predicates and FMEA severity correctly

**Validation:**
- Manual check: run pipeline on spec with bool->int type migration; verify guard analysis section and release gate warning in output
- Evidence: linkable integration test log artifact produced at `TASKLIST_ROOT/artifacts/D-0036/evidence.md`

**Dependencies:** T02.09, T03.01, T03.02
**Rollback:** Remove guard analysis pass from pipeline; M3 analysis is manual
**Notes:** Pipeline order: decomposition (M1) -> invariant+FMEA (M2) -> guard analysis (M3) -> data flow (M4).

---

### T03.04 -- Validate Release Gate Rule 2 enforcement and Phase 3 exit criteria

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031 |
| Why | Release Gate Rule 2 requires that unresolved guard ambiguity with no owner is a blocking condition. This task validates enforcement and confirms Phase 3 exit criteria before M4 begins. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | system-wide |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0037, D-0038 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0037/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0038/evidence.md

**Deliverables:**
1. Release Gate Rule 2 enforcement validation: confirm unresolved guard ambiguity without owner assignment blocks pipeline advancement to M4 (D-0037)
2. Phase 3 milestone exit criteria validation report: all deliverables D-0031 through D-0036 complete, guard analysis produces correct output, sentinel ambiguity bug pattern caught (D-0038)

**Steps:**
1. **[PLANNING]** Collect all guard ambiguity findings from T03.03 pipeline output
2. **[PLANNING]** Define enforcement criteria: unresolved ambiguity without owner = blocking condition
3. **[EXECUTION]** Verify pipeline refuses to advance to M4 pass when unresolved ambiguity has no owner
4. **[EXECUTION]** Verify known bug pattern (bool->int sentinel ambiguity for `_replayed_event_offset`) caught by guard analysis
5. **[VERIFICATION]** Confirm all deliverables D-0031 through D-0036 complete with passing evidence
6. **[COMPLETION]** Document enforcement validation results and Phase 3 exit status in evidence artifact

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0037/spec.md` exists documenting Rule 2 enforcement verification and blocking behavior
- Unresolved guard ambiguity without owner blocks pipeline advancement; pipeline does not proceed to M4
- Known bug pattern (sentinel ambiguity: `_replayed_event_offset = len(plan.tail_events)` = 0 on empty tail) caught by guard analysis
- All deliverables D-0031 through D-0036 complete with passing evidence artifacts

**Validation:**
- Manual check: attempt pipeline advancement with unresolved guard ambiguity without owner; verify blocking
- Evidence: linkable validation report artifact produced at `TASKLIST_ROOT/artifacts/D-0038/evidence.md`

**Dependencies:** T03.03
**Rollback:** N/A (validation task; no code changes)
**Notes:** Gate task. Phase 4 must not begin until this task passes. R-011 mitigation validated here.

---

### Checkpoint: End of Phase 3

**Purpose:** Gate Phase 4 entry. Confirm all Phase 3 deliverables are complete, Release Gate Rule 2 is enforced, and sentinel ambiguity bug pattern is caught.
**Checkpoint Report Path:** .dev/releases/current/v.2.11-roadmap-v4/tasklist/checkpoints/CP-P03-END.md
**Verification:**
- All four tasks (T03.01-T03.04) completed with evidence artifacts at intended paths
- Guard analysis produces correct output for type-migration and clear-boolean scenarios
- Sentinel ambiguity bug pattern (bool->int for `_replayed_event_offset`) caught during planning
**Exit Criteria:**
- Release Gate Rule 2 validated: unresolved ambiguity without owner blocks advancement
- Guard analysis cross-references M2 invariant predicates and FMEA severity correctly
- Pipeline ready for M4: decomposition -> invariant+FMEA -> guard analysis -> (next: data flow tracing)
