# Phase 4 -- Cross-Deliverable Data Flow Tracing

Implement Proposal 5 (Cross-Deliverable Data Flow Tracing). Construct a data flow graph following each mutable state variable through all deliverables that read or write it. Extract implicit cross-milestone contracts, promote them to explicit acceptance criteria, and detect conflicts where writer semantics diverge from reader assumptions. Conditional on roadmaps with 6+ milestones (configurable via `--dataflow-threshold`; override with `--force-dataflow`). Includes pilot requirement before general enablement.

---

### T04.01 -- Implement data flow graph builder with cross-milestone edges and cycle detection

| Field | Value |
|---|---|
| Roadmap Item IDs | R-033, R-034 |
| Why | The graph builder constructs a directed graph where nodes are (deliverable_id, variable_name, operation) tuples with operation in {birth, write, read}. Edges connect writes to subsequent reads. Cross-milestone edges are annotated with milestone boundary. Cycle detection and dead write warnings are included. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | multi-file, performance |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0039, D-0040 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0039/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0040/evidence.md

**Deliverables:**
1. Data flow graph builder using adjacency list representation with nodes as `(deliverable_id, variable_name, operation)` tuples, directed edges from writes to reads, cross-milestone edge annotation, cycle detection, dead write warnings, and 100-deliverable performance warning (D-0039)
2. Test suite: M1.D1->M2.D3->M3.D1 chain -> 3-node + 2 cross-milestone edges, same-deliverable birth+read -> 2-node + no cross-milestone, read before birth -> error, dead write -> warning, empty deliverable list -> empty graph (D-0040)

**Steps:**
1. **[PLANNING]** Review M2 invariant registry output (T02.09) for variable mutation site data to feed graph construction
2. **[PLANNING]** Select adjacency list representation for O(V+E) graph operations (R-012 mitigation)
3. **[EXECUTION]** Implement directed graph with (deliverable_id, variable_name, operation) nodes and write->read edges
4. **[EXECUTION]** Add cross-milestone edge annotation and cycle detection algorithm
5. **[EXECUTION]** Add dead write detection (write node with no subsequent read edge) and 100-deliverable performance warning
6. **[VERIFICATION]** Run five-scenario test suite via sub-agent quality-engineer
7. **[COMPLETION]** Document graph structure, algorithm complexity, and performance characteristics in spec artifact at D-0039 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0039/spec.md` exists documenting graph structure, node/edge schema, cycle detection algorithm, and performance characteristics
- M1.D1->M2.D3->M3.D1 variable chain produces 3-node graph with 2 cross-milestone edges correctly annotated
- Read-before-birth condition produces error (not silent acceptance)
- Dead write (write with no subsequent read) produces warning with the dead write's deliverable_id

**Validation:**
- Manual check: construct graph for 3-deliverable cross-milestone chain; verify node count, edge count, and cross-milestone annotation
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0040/evidence.md`

**Dependencies:** T02.09, T03.03
**Rollback:** Remove graph builder; data flow analysis is manual
**Notes:** R-012 mitigation: adjacency list representation, 100-deliverable warning, --skip-dataflow flag, intermediate result caching.

---

### T04.02 -- Implement implicit contract extractor for cross-milestone edges

| Field | Value |
|---|---|
| Roadmap Item IDs | R-035, R-036 |
| Why | For each cross-milestone edge, the extractor parses writer semantics ("set X to mean Y") and reader assumptions ("assumes X is", "when X equals"). Below 60% confidence -> UNSPECIFIED with mandatory human review. This is the component most subject to natural language limitations (R-013). |
| Effort | L |
| Risk | High |
| Risk Drivers | system-wide, multi-file |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0041, D-0042 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0041/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0042/evidence.md

**Deliverables:**
1. Implicit contract extractor producing `ImplicitContract(variable, writer_deliverable, reader_deliverable, writer_semantics, reader_assumption)` tuples, with confidence scoring per extraction and UNSPECIFIED classification below 60% confidence (D-0041)
2. Test suite: writer "set offset to events delivered" + reader "assumes offset equals events processed" -> contract captured, no explicit semantics -> `writer_semantics=UNSPECIFIED` (flagged), both UNSPECIFIED -> highest-risk classification, confidence scoring calibrated (not all 0.5 or 1.0) (D-0042)

**Steps:**
1. **[PLANNING]** Load data flow graph from T04.01 to identify cross-milestone edges requiring contract extraction
2. **[PLANNING]** Define writer semantic parsing patterns: "set X to mean Y", "X represents Z after this operation"
3. **[EXECUTION]** Implement writer semantics parser scanning deliverable descriptions for semantic declarations
4. **[EXECUTION]** Implement reader assumption parser scanning for "assumes X is", "when X equals", "based on X"
5. **[EXECUTION]** Add confidence scoring with 60% threshold: below -> UNSPECIFIED with mandatory human review flag
6. **[VERIFICATION]** Run four-scenario test suite via sub-agent quality-engineer including confidence calibration verification
7. **[COMPLETION]** Document extraction patterns, confidence scoring, and UNSPECIFIED handling in spec artifact at D-0041 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0041/spec.md` exists documenting ImplicitContract structure, extraction patterns, confidence scoring algorithm, and UNSPECIFIED threshold
- Writer "set offset to events delivered" paired with reader "assumes offset equals events processed" produces captured contract with both semantics populated
- Extraction below 60% confidence produces UNSPECIFIED classification with mandatory human review flag
- Confidence scores are calibrated across the 0.0-1.0 range (not all clustered at 0.5 or 1.0)

**Validation:**
- Manual check: run extractor on test writer/reader pair; verify ImplicitContract fields and confidence score
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0042/evidence.md`

**Dependencies:** T04.01
**Rollback:** Remove implicit contract extractor; cross-milestone contracts are manual review only
**Notes:** R-013 acknowledged: implicit contract extraction from natural language has fundamental reliability limits. UNSPECIFIED below 60% with mandatory human review is the mitigation.

---

### T04.03 -- Implement conflict detector for writer/reader semantic divergence

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037, R-038 |
| Why | The conflict detector flags contracts where writer semantics diverge from reader assumptions: direct contradiction, scope mismatch (filtered subset vs full set), type mismatch, completeness mismatch. Cross-references M2 invariant predicates and failure mode tables to enrich detection. |
| Effort | L |
| Risk | High |
| Risk Drivers | system-wide, multi-file |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0043, D-0044 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0043/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0044/evidence.md

**Deliverables:**
1. Conflict detector identifying: direct contradiction, scope mismatch, type mismatch, completeness mismatch between writer semantics and reader assumptions, with M2 invariant predicate and failure mode table cross-referencing, and suggested resolution action per conflict (D-0043)
2. Test suite: "offset tracks filtered events" vs "offset tracks all events" -> scope mismatch, "flag is boolean" vs "flag is integer" -> type mismatch, identical semantics -> no conflict, unspecified writer semantics -> always conflicts (cannot verify compatibility) (D-0044)

**Steps:**
1. **[PLANNING]** Load implicit contracts from T04.02 and M2 invariant predicates/failure mode tables from T02.09
2. **[PLANNING]** Define conflict categories: direct contradiction, scope mismatch, type mismatch, completeness mismatch
3. **[EXECUTION]** Implement conflict detection for each category with extensible synonym dictionary (R-014 mitigation)
4. **[EXECUTION]** Add M2 cross-referencing: invariant predicates enrich scope detection, failure mode tables enrich completeness detection
5. **[EXECUTION]** Generate suggested resolution action per detected conflict
6. **[VERIFICATION]** Run four-scenario test suite via sub-agent quality-engineer
7. **[COMPLETION]** Document conflict categories, detection algorithms, and synonym dictionary in spec artifact at D-0043 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0043/spec.md` exists documenting conflict categories, detection algorithms, synonym dictionary, and resolution suggestion format
- "offset tracks filtered events" vs "offset tracks all events" detected as scope mismatch
- Identical writer semantics and reader assumptions produce no conflict classification
- Unspecified writer semantics always produce conflict (cannot verify compatibility with unknown semantics)

**Validation:**
- Manual check: run conflict detector on all four test scenarios; verify conflict classification and resolution suggestions
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0044/evidence.md`

**Dependencies:** T04.02, T02.09
**Rollback:** Remove conflict detector; cross-milestone contract conflicts are manual review only
**Notes:** R-014 mitigation: extensible synonym dictionary (e.g., "total" == "count"). Per-project customizable.

---

### T04.04 -- Implement cross-milestone verification emitter and integrate data flow tracing as final pipeline pass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-039, R-040, R-041, R-042 |
| Why | Generates contract_test deliverables for conflicts and high-risk implicit contracts, inserted into reader's milestone. Integrates data flow tracing as the final pipeline pass, running after guard analysis. Conditional: below 6-milestone threshold produces summary only with M2 reference. |
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
| Deliverable IDs | D-0045, D-0046 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0045/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0046/evidence.md

**Deliverables:**
1. Cross-milestone verification emitter generating `kind=contract_test` deliverables for conflicts and high-risk contracts, inserted into reader's milestone, plus pipeline integration as final post-generation pass reading all deliverables including M1/M2/M3 generated deliverables, with conditional threshold (6+ milestones = full tracing, below = summary with M2 reference) (D-0045)
2. Integration tests: (1) 6+ milestones: trace section present, contracts listed, conflicts flagged, contract_test deliverables in correct milestones; (2) 3 milestones: skip summary with M2 reference, no contract_test deliverables generated (D-0046)

**Steps:**
1. **[PLANNING]** Load conflict detector output from T04.03 and data flow graph from T04.01
2. **[PLANNING]** Define conditional threshold: 6+ milestones = full tracing; below = summary only (configurable via --dataflow-threshold)
3. **[EXECUTION]** Implement contract_test deliverable generation for conflicts and high-risk contracts; insert into reader's milestone
4. **[EXECUTION]** Register data flow tracing as final pipeline pass (after guard analysis); reads all deliverables
5. **[EXECUTION]** Implement conditional logic: below threshold -> summary section with M2 invariant registry reference
6. **[VERIFICATION]** Run both integration tests via sub-agent quality-engineer: 6+ milestone and 3 milestone scenarios
7. **[COMPLETION]** Document pipeline position, conditional threshold, and output format in spec artifact at D-0045 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0045/spec.md` exists documenting emitter logic, pipeline position, conditional threshold, and output section format
- 6+ milestone roadmap produces data flow trace section with contracts, conflicts, and contract_test deliverables in reader milestones
- 3 milestone roadmap produces skip summary with M2 invariant registry reference and zero contract_test deliverables
- Pipeline execution order is complete: decomposition -> invariant+FMEA -> guard analysis -> data flow tracing

**Validation:**
- Manual check: run complete pipeline on 6+ milestone spec; verify all four pass outputs present in correct order
- Evidence: linkable integration test log artifact produced at `TASKLIST_ROOT/artifacts/D-0046/evidence.md`

**Dependencies:** T04.01, T04.02, T04.03, T03.03
**Rollback:** Remove data flow tracing pass from pipeline; cross-milestone analysis limited to M2 per-variable tracking
**Notes:** Conditional activation from adversarial consensus: both variants agreed 6+ milestone threshold is appropriate.

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.04

**Purpose:** Verify data flow tracing pipeline is functional before pilot execution.
**Checkpoint Report Path:** .dev/releases/current/v.2.11-roadmap-v4/tasklist/checkpoints/CP-P04-T01-T04.md
**Verification:**
- Data flow graph builder produces correct graphs for cross-milestone variable chains
- Implicit contract extractor handles both specified and UNSPECIFIED semantics correctly
- Conflict detector identifies scope, type, and completeness mismatches
**Exit Criteria:**
- All four tasks (T04.01-T04.04) have passing test suites with evidence artifacts
- Complete pipeline (4 passes) runs end-to-end on test input
- Conditional threshold correctly activates/deactivates data flow tracing

---

### T04.05 -- Execute pilot on high-complexity roadmap and record go/no-go decision

| Field | Value |
|---|---|
| Roadmap Item IDs | R-043, R-044 |
| Why | Before general enablement of data flow tracing, a pilot must be executed on one high-complexity roadmap (6+ milestones) to measure runtime overhead, defects detected vs would-have-been-missed, and false positive rate. The go/no-go decision is a hard gate blocking general enablement. |
| Effort | M |
| Risk | High |
| Risk Drivers | system-wide, performance |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0047, D-0048 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0047/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0048/evidence.md

**Deliverables:**
1. Pilot execution on one high-complexity roadmap (6+ milestones): runtime overhead measured, defects detected vs would-have-been-missed count, false positive rate measured, overall effectiveness assessment (D-0047)
2. Pilot go/no-go decision documented with evidence: overhead measurement, defect detection rate, false positive count, recommendation (enable/refine/disable), conditions for general enablement (D-0048)

**Steps:**
1. **[PLANNING]** Select high-complexity roadmap with 6+ milestones for pilot execution
2. **[PLANNING]** Define measurement criteria: runtime overhead, defect detection rate, false positive rate
3. **[EXECUTION]** Run complete pipeline (all 4 passes) on selected roadmap and record runtime
4. **[EXECUTION]** Analyze data flow tracing output: count defects detected, false positives, and would-have-been-missed defects
5. **[VERIFICATION]** Compare overhead and detection rates against go/no-go thresholds
6. **[COMPLETION]** Document go/no-go decision with all measurements and recommendation in evidence artifact at D-0048 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0047/spec.md` exists documenting pilot roadmap selection, measurement methodology, and raw results
- Runtime overhead measured in absolute terms (seconds) and relative to non-data-flow pipeline execution
- Go/no-go decision at `TASKLIST_ROOT/artifacts/D-0048/evidence.md` includes: overhead measurement, defect detection rate, false positive count, and explicit recommendation (enable/refine/disable)
- General enablement blocked until go/no-go deliverable (D-0048) is accepted

**Validation:**
- Manual check: verify pilot measurements are recorded with specific numbers (not estimates or ranges)
- Evidence: linkable go/no-go decision artifact produced at `TASKLIST_ROOT/artifacts/D-0048/evidence.md`

**Dependencies:** T04.04
**Rollback:** If go/no-go = disable, remove data flow tracing pass from pipeline; revert to M2 per-variable tracking
**Notes:** R-015 mitigation: D-0048 is a hard gate. General enablement blocked until this deliverable accepted. Pilot-first approach from V2 adversarial variant.

---

### Checkpoint: End of Phase 4

**Purpose:** Final project gate. Confirm all Phase 4 deliverables are complete, pilot executed, and go/no-go decision recorded.
**Checkpoint Report Path:** .dev/releases/current/v.2.11-roadmap-v4/tasklist/checkpoints/CP-P04-END.md
**Verification:**
- All five tasks (T04.01-T04.05) completed with evidence artifacts at intended paths
- Complete pipeline (decomposition -> invariant+FMEA -> guard analysis -> data flow tracing) runs end-to-end
- Pilot go/no-go decision documented with measurements and recommendation
**Exit Criteria:**
- Go/no-go decision accepted with evidence-based recommendation
- All five success criteria (SC-001 through SC-005) from roadmap are achievable by the pipeline
- All three release gates (Rule 1: silent corruption block, Rule 2: guard ambiguity gate, Rule 3: verify deliverable quality) enforced
