# Phase 2 -- State Variable Invariant Registry and FMEA Pass

Implement Proposals 1 and 2 as a combined analytical milestone. The invariant registry defines expected state truth for variables; FMEA models failure propagation for computations. Both share trigger detection infrastructure (text scanning over deliverable descriptions) and cross-link findings. This is the milestone that would have caught both source bugs: the wrong-operand state mutation and the zero/empty sentinel ambiguity.

---

### T02.01 -- Implement InvariantEntry data structure with constrained grammar predicates

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009, R-010 |
| Why | The invariant registry requires a data structure to hold variable_name, scope, invariant_predicate (constrained grammar), mutation_sites list, and verification_deliverable_ids. Constrained grammar prevents ambiguous free-form predicates (R-006 mitigation). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema, model |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0011, D-0012 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0011/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0012/evidence.md

**Deliverables:**
1. `InvariantEntry` data structure with fields: `variable_name`, `scope`, `invariant_predicate` (constrained grammar: `variable_name comparison_op expression [AND|OR ...]`), `mutation_sites` (list of `MutationSite(location, expression, context)`), `verification_deliverable_ids` (list) (D-0011)
2. Test suite: empty `mutation_sites` valid, `verification_deliverable_ids` can cross milestones, serialization round-trip preserves all fields, duplicate `variable_name` within same scope warns (D-0012)

**Steps:**
1. **[PLANNING]** Review M1 deliverable schema (T01.01) to ensure InvariantEntry integrates with `metadata` attachment point
2. **[PLANNING]** Define constrained grammar specification: `variable_name comparison_op expression [AND|OR ...]`
3. **[EXECUTION]** Implement `InvariantEntry` dataclass with all required fields and constrained grammar validation
4. **[EXECUTION]** Implement `MutationSite` dataclass with location, expression, context fields
5. **[EXECUTION]** Add duplicate variable_name warning within same scope and free-form predicate rejection with validation error
6. **[VERIFICATION]** Run four-scenario test suite via sub-agent quality-engineer
7. **[COMPLETION]** Document data structure specification and constrained grammar in spec artifact at D-0011 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0011/spec.md` exists documenting InvariantEntry fields, constrained grammar syntax, and MutationSite structure
- `invariant_predicate` field rejects free-form text that does not match the constrained grammar pattern
- Serialization round-trip (serialize -> deserialize) preserves all InvariantEntry fields including nested MutationSite objects
- Duplicate `variable_name` within the same scope produces a warning (not an error) to allow cross-milestone tracking

**Validation:**
- Manual check: instantiate InvariantEntry with valid constrained predicate and one with free-form text; verify acceptance/rejection
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0012/evidence.md`

**Dependencies:** T01.01
**Rollback:** Remove InvariantEntry and MutationSite data structures
**Notes:** Constrained grammar decision from adversarial Round 2 (V1 architecture retained). Free-form predicates rejected with validation error.

---

### T02.02 -- Implement state variable detector scanning deliverable descriptions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011, R-012 |
| Why | The detector scans deliverable descriptions for state variable introduction patterns (self._ assignments, counter/offset/cursor introductions, type replacements). Low-confidence detections are flagged for human review rather than silently dropped (R-004 mitigation). |
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
| Deliverable IDs | D-0013, D-0014 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0013/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0014/evidence.md

**Deliverables:**
1. State variable detector function returning `(variable_name, deliverable_id, introduction_type)` tuples for: `self._*` assignments, "introduce variable", "add counter/offset/cursor/flag", "replace X with Y" where Y is state-tracking type (D-0013)
2. Test suite: "Replace boolean with int offset" -> replacement, "Add replay guard flag" -> flag, "Document offset behavior" -> not detected, "Introduce cursor for pagination" -> cursor, multiple variables in one deliverable handled (D-0014)

**Steps:**
1. **[PLANNING]** Review T01.03 behavioral detection patterns for overlap; state variable detector is complementary (detects variables, not verbs)
2. **[PLANNING]** Compile detection patterns: self._ assignments, introduction keywords, type replacement patterns
3. **[EXECUTION]** Implement state variable detector with extensible synonym dictionary
4. **[EXECUTION]** Add low-confidence detection flagging for ambiguous patterns (R-004 mitigation)
5. **[EXECUTION]** Handle multiple variable introductions within a single deliverable description
6. **[VERIFICATION]** Run five-scenario test suite via sub-agent quality-engineer
7. **[COMPLETION]** Document detection patterns and synonym dictionary in spec artifact at D-0013 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0013/spec.md` exists documenting all detection patterns, synonym dictionary, and confidence flagging behavior
- "Replace boolean with int offset" detected as replacement type with variable name extracted
- "Document offset behavior" not detected (documentation exclusion)
- Low-confidence detections flagged for human review with confidence score rather than silently dropped

**Validation:**
- Manual check: run detector on all five test descriptions and verify tuple outputs match expected results
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0014/evidence.md`

**Dependencies:** T01.01
**Rollback:** Remove state variable detector function
**Notes:** R-004 mitigation: extensible synonym dictionary. Low-confidence detections flagged rather than dropped.

---

### T02.03 -- Implement mutation inventory generator enumerating write paths per detected variable

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013, R-014 |
| Why | For each detected state variable, the mutation inventory enumerates all deliverables that write to it. This cross-references all roadmap deliverables (not just the introducing deliverable) to catch mutations that happen far from the variable's birth. |
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
| Deliverable IDs | D-0015, D-0016 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0015/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0016/evidence.md

**Deliverables:**
1. Mutation inventory generator parsing descriptions for mutation indicators ("update X", "increment X", "reset X", "set X to", "advance X by", "clear X") and cross-referencing all roadmap deliverables (D-0015)
2. Test suite: variable introduced in D2.3 and mutated in D3.1 and D4.2 -> 3 mutation sites, no mutations beyond birth -> 1 site, mutation sites include deliverable ID, ambiguous mutations flagged rather than silently dropped (D-0016)

**Steps:**
1. **[PLANNING]** Load state variable detector output from T02.02 to identify variables requiring mutation inventory
2. **[PLANNING]** Compile mutation indicator patterns: update, increment, reset, set-to, advance-by, clear
3. **[EXECUTION]** Implement mutation inventory generator scanning all deliverable descriptions for mutation indicators per variable
4. **[EXECUTION]** Generate MutationSite entries with deliverable_id, expression, and context
5. **[EXECUTION]** Add ambiguous mutation flagging for unclear write patterns (R-004 mitigation)
6. **[VERIFICATION]** Run four-scenario test suite via sub-agent quality-engineer
7. **[COMPLETION]** Document mutation indicator patterns and cross-referencing logic in spec artifact at D-0015 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0015/spec.md` exists documenting mutation indicator patterns and cross-reference algorithm
- Variable with mutations across 3 deliverables produces 3 MutationSite entries with correct deliverable IDs
- Variable with no mutations beyond birth produces exactly 1 MutationSite (the birth site)
- Ambiguous mutations flagged for human review rather than silently dropped or incorrectly classified

**Validation:**
- Manual check: verify mutation inventory for a variable introduced in one deliverable and mutated in two others
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0016/evidence.md`

**Dependencies:** T02.02
**Rollback:** Remove mutation inventory generator; invariant checks limited to birth-site only
**Notes:** Cross-references ALL roadmap deliverables, not just those in the introducing milestone.

---

### T02.04 -- Implement verification deliverable emitter generating invariant_check deliverables

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015, R-016 |
| Why | For each mutation site, the emitter generates a `kind=invariant_check` deliverable with the variable name, invariant predicate, specific mutation being verified, and edge cases (zero, negative, empty, boundary). These deliverables are inserted into the correct milestone by mutation site location. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema, multi-file |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0017, D-0018 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0017/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0018/evidence.md

**Deliverables:**
1. Verification deliverable emitter generating `kind=invariant_check` deliverables with IDs following `D{milestone}.{seq}.inv` pattern, each including variable name, invariant predicate, mutation reference, and edge cases (zero, empty, boundary minimum) (D-0017)
2. Test suite: 3 mutation sites -> 3 invariant_check deliverables, each references correct predicate, edge cases include zero/empty/boundary, deliverables inserted into correct milestone. Release Gate Rule 3: each verify deliverable contains state assertion (D-0018)

**Steps:**
1. **[PLANNING]** Load mutation inventory from T02.03 and InvariantEntry data from T02.01
2. **[PLANNING]** Define ID scheme: `D{milestone}.{seq}.inv` for invariant_check deliverables
3. **[EXECUTION]** Implement emitter generating one invariant_check deliverable per mutation site
4. **[EXECUTION]** Include edge cases: zero, negative, empty, boundary for each invariant check
5. **[EXECUTION]** Insert generated deliverables into correct milestone based on mutation site location; cap at 5 per variable (R-005)
6. **[VERIFICATION]** Run four-scenario test suite via sub-agent quality-engineer; verify Release Gate Rule 3 compliance
7. **[COMPLETION]** Document emitter logic and ID scheme in spec artifact at D-0017 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0017/spec.md` exists documenting emitter logic, ID scheme, and edge case generation
- 3 mutation sites produce exactly 3 invariant_check deliverables with correct milestone placement
- Each generated deliverable references the specific invariant predicate from the registry
- Each generated verify deliverable contains at least one state assertion (Release Gate Rule 3 compliance)

**Validation:**
- Manual check: verify 3 mutation sites produce 3 deliverables with correct IDs, predicates, and milestone placement
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0018/evidence.md`

**Dependencies:** T02.01, T02.02, T02.03
**Rollback:** Remove verification deliverable emitter; invariant checks are manual
**Notes:** R-005 mitigation: cap at 5 invariant_check deliverables per variable. Configurable via --max-invariant-checks.

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.04

**Purpose:** Verify invariant registry pipeline components are functional before FMEA implementation.
**Checkpoint Report Path:** .dev/releases/current/v.2.11-roadmap-v4/tasklist/checkpoints/CP-P02-T01-T04.md
**Verification:**
- InvariantEntry data structure validates constrained grammar and rejects free-form predicates
- State variable detector correctly identifies variables from deliverable descriptions
- Mutation inventory cross-references all deliverables and flags ambiguous mutations
**Exit Criteria:**
- All four tasks (T02.01-T02.04) have passing test suites
- No false negatives on state variable detection for known bug patterns (wrong-operand, sentinel ambiguity)
- Verification deliverable emitter cap at 5 per variable is enforced

---

### T02.05 -- Implement invariant registry pipeline integration as post-decomposition pass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017, R-018 |
| Why | The invariant registry pass runs after M1 decomposition, reads Implement deliverables, detects state variables, generates invariant entries, emits verification deliverables, and appends the invariant registry section to roadmap output. |
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
| Deliverable IDs | D-0019, D-0020 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0019/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0020/evidence.md

**Deliverables:**
1. Invariant registry pipeline pass registered after M1 decomposition, reading Implement deliverables, running state variable detection -> mutation inventory -> verification emitter, appending invariant registry section to output (D-0019)
2. Integration test: spec with state variable introductions -> invariant registry section present, invariant_check deliverables in correct milestones, entries cross-reference generated deliverables by ID (D-0020)

**Steps:**
1. **[PLANNING]** Review pipeline execution order from T01.04 to identify correct insertion point (after decomposition, before output formatting)
2. **[PLANNING]** Verify all pipeline components (T02.01-T02.04) are available as dependencies
3. **[EXECUTION]** Register invariant registry pass in pipeline: detection -> inventory -> emission -> section append
4. **[EXECUTION]** Ensure pass is idempotent and does not interfere with decomposition pass output
5. **[EXECUTION]** Generate invariant registry output section with variable tables and cross-references
6. **[VERIFICATION]** Run integration test via sub-agent quality-engineer: spec with state variables produces correct registry and deliverables
7. **[COMPLETION]** Document pipeline position and integration behavior in spec artifact at D-0019 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0019/spec.md` exists documenting pipeline position, pass order, and idempotency guarantees
- Integration test input with state variable introductions produces invariant registry section in output
- Generated invariant_check deliverables appear in correct milestones with cross-references to registry entries
- Pass is idempotent: running twice produces identical output

**Validation:**
- Manual check: run pipeline on spec with 2 state variables; verify registry section and invariant_check deliverables in output
- Evidence: linkable integration test log artifact produced at `TASKLIST_ROOT/artifacts/D-0020/evidence.md`

**Dependencies:** T01.04, T02.01, T02.02, T02.03, T02.04
**Rollback:** Remove invariant registry pass from pipeline; M2 analysis is manual
**Notes:** This is the first analytical pass in the pipeline. M2 combined pass (T02.09) merges this with FMEA.

---

### T02.06 -- Implement FMEA input domain enumerator for computational deliverables

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019, R-020 |
| Why | For each computational deliverable, the enumerator generates up to 8 input domains prioritizing degenerate cases (empty, zero, null, boundary). This feeds the FMEA failure mode classifier to detect silent corruption paths. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0021, D-0022 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0021/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0022/evidence.md

**Deliverables:**
1. FMEA input domain enumerator triggered by computational verbs, generating domain list: normal, empty, null/None, zero, negative, duplicate, out-of-order, single-element, maximum-size, with limit of 8 domains per computation and degenerate case prioritization (D-0021)
2. Test suite: "filter events by type" -> normal/empty/filter-removes-all/filter-removes-none/single-element minimum, "count active sessions" -> normal/zero/single/large-count, non-computational -> empty list, multiple computations -> separate domain lists (D-0022)

**Steps:**
1. **[PLANNING]** Review computational verb list from T01.03 behavioral detection heuristic for trigger conditions
2. **[PLANNING]** Define domain enumeration order: degenerate cases first (empty, zero, null), then boundary (single, max), then normal
3. **[EXECUTION]** Implement domain enumerator returning ordered list of up to 8 domains per computation
4. **[EXECUTION]** Add non-computational exclusion (empty list returned for non-computational deliverables)
5. **[VERIFICATION]** Run four-scenario test suite verifying domain lists for filter, count, non-computational, and multi-computation cases
6. **[COMPLETION]** Document domain enumeration algorithm and prioritization rules in spec artifact at D-0021 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0021/spec.md` exists documenting domain enumeration algorithm, prioritization order, and 8-domain limit
- "filter events by type" produces at minimum: normal, empty, filter-removes-all, filter-removes-none, single-element domains
- Non-computational deliverable descriptions produce empty domain list
- Maximum 8 domains per computation enforced with degenerate cases prioritized

**Validation:**
- Manual check: run enumerator on "filter events by type" and "count active sessions"; verify domain lists match expected output
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0022/evidence.md`

**Dependencies:** T01.03
**Rollback:** Remove domain enumerator; FMEA operates without input domain enumeration
**Notes:** R-007 mitigation: 8-domain limit prevents combinatorial explosion. Configurable via --max-fmea-domains.

---

### T02.07 -- Implement FMEA failure mode classifier with dual detection signal

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021, R-022 |
| Why | The classifier uses two independent signals: (1) cross-reference against invariant predicates to detect invariant violations without error output, and (2) independent "no error path" detection for computations that produce wrong values silently. Silent corruption = highest severity. This dual signal prevents circular dependency on M2 registry completeness. |
| Effort | L |
| Risk | High |
| Risk Drivers | multi-file, system-wide, breaking change |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0023, D-0024 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0023/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0024/evidence.md

**Deliverables:**
1. FMEA failure mode classifier with Signal 1 (invariant cross-reference: violation without error = silent corruption) and Signal 2 (independent no-error-path detection: computation returns value without exception on degenerate input = potential silent corruption). Outputs: detection difficulty (immediate/delayed/silent) + severity (data loss, wrong state, degraded, cosmetic) (D-0023)
2. Test suite: "offset advances by wrong amount, no error raised" -> silent corruption + highest severity, "TypeError on null input" -> immediate + medium, "filter returns empty instead of raising on invalid predicate" -> delayed + high, Signal 2 independently detects silent corruption even when no invariant predicate registered (D-0024)

**Steps:**
1. **[PLANNING]** Load invariant registry data from T02.05 for Signal 1 cross-reference; load domain enumerator output from T02.06 for failure path analysis
2. **[PLANNING]** Define severity classification matrix: silent corruption = highest regardless of downstream impact
3. **[EXECUTION]** Implement Signal 1: cross-reference computation outputs against invariant predicates; violations without error -> silent corruption
4. **[EXECUTION]** Implement Signal 2: independent no-error-path detection for degenerate inputs that return values without exceptions
5. **[EXECUTION]** Combine both signals into unified severity classification; silent corruption from either signal = highest severity
6. **[VERIFICATION]** Run four-scenario test suite via sub-agent quality-engineer including Signal 2 independence verification
7. **[COMPLETION]** Document dual signal architecture and severity matrix in spec artifact at D-0023 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0023/spec.md` exists documenting dual signal architecture, severity matrix, and detection difficulty classifications
- "offset advances by wrong amount, no error raised" classified as silent corruption with highest severity
- Signal 2 independently detects silent corruption even when no invariant predicate is registered for the variable being analyzed
- All four detection difficulty levels (immediate, delayed, silent) and four severity levels (data loss, wrong state, degraded, cosmetic) are classifiable

**Validation:**
- Manual check: verify classifier output for all four test scenarios including Signal 2 independence case
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0024/evidence.md`

**Dependencies:** T02.05, T02.06
**Rollback:** Remove FMEA classifier; failure mode analysis is manual
**Notes:** Dual signal architecture retained from V1 adversarial variant. Signal 2 independence prevents circular dependency on registry completeness.

---

### T02.08 -- Implement FMEA deliverable promotion for failure modes above severity threshold

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023, R-024 |
| Why | Failure modes at or above "wrong state" severity are promoted to fmea_test deliverables. Below-threshold modes become accepted risk in metadata. High-severity findings trigger Release Gate Rule 1 (block downstream progression). |
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
| Deliverable IDs | D-0025, D-0026 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0025/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0026/evidence.md

**Deliverables:**
1. FMEA deliverable promotion generating `kind=fmea_test` deliverables for failure modes at/above "wrong state" severity, with below-threshold modes recorded as accepted risk in metadata with documented rationale, and Release Gate Rule 1 triggering for silent corruption findings (D-0025)
2. Test suite: silent corruption -> promoted fmea_test + release gate triggered, cosmetic -> accepted risk in metadata, promoted deliverable includes detection mechanism, configurable threshold, zero above-threshold -> no promotion and no accepted-risk entries (D-0026)

**Steps:**
1. **[PLANNING]** Load FMEA classifier output from T02.07 to determine promotion candidates
2. **[PLANNING]** Define promotion threshold: "wrong state" and above (wrong state, data loss, silent corruption)
3. **[EXECUTION]** Implement promotion logic: above-threshold -> fmea_test deliverable; below-threshold -> accepted risk in metadata
4. **[EXECUTION]** Add Release Gate Rule 1 trigger for silent corruption: blocks downstream milestone progression
5. **[EXECUTION]** Handle edge case: zero failure modes above threshold -> no promotion and no accepted-risk entries
6. **[VERIFICATION]** Run five-scenario test suite via sub-agent quality-engineer
7. **[COMPLETION]** Document promotion logic and threshold configuration in spec artifact at D-0025 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0025/spec.md` exists documenting promotion threshold, fmea_test generation, and Release Gate Rule 1 trigger conditions
- Silent corruption finding produces promoted fmea_test deliverable AND triggers Release Gate Rule 1
- Cosmetic severity finding recorded as accepted risk in deliverable metadata with documented rationale
- Promotion threshold configurable for future tuning

**Validation:**
- Manual check: verify promotion output for silent corruption, cosmetic, and zero-findings scenarios
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0026/evidence.md`

**Dependencies:** T02.07
**Rollback:** Remove promotion logic; all FMEA findings are informational only
**Notes:** R-008 mitigation: Release Gate Rule 1 ensures FMEA findings are acted on. Silent corruption = blocking condition.

---

### T02.09 -- Integrate invariant registry and FMEA as combined pipeline pass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025, R-026 |
| Why | Both passes share deliverable scanning infrastructure and must cross-link findings: invariant registry rows connect to corresponding fmea_test deliverables. The combined pass is idempotent and runs after M1 decomposition. |
| Effort | L |
| Risk | High |
| Risk Drivers | pipeline, multi-file, system-wide |
| Tier | STRICT |
| Confidence | [█████████-] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0027, D-0028 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0027/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0028/evidence.md

**Deliverables:**
1. Combined invariant registry + FMEA pipeline pass with shared scanning infrastructure, cross-linking invariant entries to fmea_test deliverables, idempotent execution, and correct pipeline positioning after M1 decomposition (D-0027)
2. Integration test: spec with state variable introductions and computational deliverables -> both invariant registry and FMEA failure mode tables present, cross-links correct, silent corruption findings trigger Release Gate Rule 1 (D-0028)

**Steps:**
1. **[PLANNING]** Review pipeline positions for invariant registry pass (T02.05) and FMEA components (T02.06-T02.08) to merge into single combined pass
2. **[PLANNING]** Design shared scanning infrastructure: single pass over deliverable descriptions feeding both detector chains
3. **[EXECUTION]** Merge invariant registry and FMEA into single pipeline pass with shared scanning
4. **[EXECUTION]** Implement cross-linking: invariant registry rows reference corresponding fmea_test deliverable IDs where applicable
5. **[EXECUTION]** Ensure combined pass is idempotent and produces identical output on repeated execution
6. **[VERIFICATION]** Run integration test via sub-agent quality-engineer: verify both output sections, cross-links, and release gate triggering
7. **[COMPLETION]** Document combined pass architecture and cross-linking schema in spec artifact at D-0027 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0027/spec.md` exists documenting combined pass architecture, shared scanning infrastructure, and cross-linking schema
- Integration test produces both invariant registry section and FMEA failure mode tables in output
- Cross-links between invariant entries and fmea_test deliverables are bidirectional and correct
- Silent corruption findings trigger Release Gate Rule 1 (downstream milestone progression blocked)

**Validation:**
- Manual check: run combined pass on spec with 2 state variables and 3 computations; verify both output sections and cross-links
- Evidence: linkable integration test log artifact produced at `TASKLIST_ROOT/artifacts/D-0028/evidence.md`

**Dependencies:** T02.05, T02.06, T02.07, T02.08
**Rollback:** Revert to separate invariant registry and FMEA passes; lose cross-linking
**Notes:** M2 grouping decision from adversarial Round 3: both advocates agreed P1+P2 share trigger detection infrastructure.

---

### Checkpoint: Phase 2 / Tasks T02.05-T02.09

**Purpose:** Verify combined invariant registry + FMEA pass is functional before exit criteria validation.
**Checkpoint Report Path:** .dev/releases/current/v.2.11-roadmap-v4/tasklist/checkpoints/CP-P02-T05-T09.md
**Verification:**
- Combined pass produces invariant registry section and FMEA failure mode tables for test inputs
- Cross-links between invariant entries and fmea_test deliverables are correct
- Release Gate Rule 1 triggers correctly on silent corruption findings
**Exit Criteria:**
- All five tasks (T02.05-T02.09) have passing test suites with evidence artifacts
- Combined pass is idempotent (running twice produces identical output)
- Known bug patterns (wrong-operand, sentinel ambiguity) caught by the combined analytical pass

---

### T02.10 -- Validate Release Gate Rule 1 enforcement and Phase 2 exit criteria

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | Release Gate Rule 1 requires that silent corruption findings block downstream milestone progression. This task validates enforcement and confirms Phase 2 exit criteria before M3 begins. |
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
| Deliverable IDs | D-0029, D-0030 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0029/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0030/evidence.md

**Deliverables:**
1. Release Gate Rule 1 enforcement validation: confirm that silent corruption FMEA findings block downstream progression until mitigated or explicitly accepted with named owner and documented rationale (D-0029)
2. Phase 2 milestone exit criteria validation report: all deliverables D-0011 through D-0028 complete, known bug patterns caught, combined pass idempotent (D-0030)

**Steps:**
1. **[PLANNING]** Collect all FMEA findings from T02.09 combined pass output classified as silent corruption
2. **[PLANNING]** Define enforcement criteria: progression blocked = pipeline refuses to advance to M3 pass without resolution or acceptance
3. **[EXECUTION]** Verify that silent corruption findings produce blocking conditions in pipeline execution
4. **[EXECUTION]** Verify that explicit acceptance requires named owner and documented rationale (not empty strings)
5. **[VERIFICATION]** Confirm known bug patterns (wrong-operand: `_loaded_start_index -= mounted`, sentinel ambiguity: `_replayed_event_offset = len(plan.tail_events)`) caught by combined pass
6. **[COMPLETION]** Document enforcement validation results and Phase 2 exit status in evidence artifact

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0029/spec.md` exists documenting Rule 1 enforcement verification and blocking behavior
- Silent corruption findings produce blocking conditions; pipeline does not advance to M3 without resolution
- Known bug pattern (wrong-operand state mutation) caught by invariant registry during planning
- All deliverables D-0011 through D-0028 complete with passing evidence artifacts

**Validation:**
- Manual check: attempt pipeline advancement with unresolved silent corruption finding; verify blocking behavior
- Evidence: linkable validation report artifact produced at `TASKLIST_ROOT/artifacts/D-0030/evidence.md`

**Dependencies:** T02.09
**Rollback:** N/A (validation task; no code changes)
**Notes:** Gate task. Phase 3 must not begin until this task passes. R-008 mitigation validated here.

---

### Checkpoint: End of Phase 2

**Purpose:** Gate Phase 3 entry. Confirm all Phase 2 deliverables are complete, Release Gate Rule 1 is enforced, and both source bug patterns are caught by the analytical passes.
**Checkpoint Report Path:** .dev/releases/current/v.2.11-roadmap-v4/tasklist/checkpoints/CP-P02-END.md
**Verification:**
- All ten tasks (T02.01-T02.10) completed with evidence artifacts at intended paths
- Combined invariant registry + FMEA pass produces correct output for test inputs
- Both source bug patterns (wrong-operand, sentinel ambiguity) caught during planning
**Exit Criteria:**
- Release Gate Rule 1 validated: silent corruption findings block downstream progression
- Constrained grammar rejects free-form invariant predicates
- FMEA dual signal architecture verified: Signal 2 independently detects silent corruption without invariant predicates
