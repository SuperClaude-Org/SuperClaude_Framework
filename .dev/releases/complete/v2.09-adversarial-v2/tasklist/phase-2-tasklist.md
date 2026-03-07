# Phase 2 -- Architecture & Protocol Quality Ph1

Implement both parallel workstreams: Track A's Meta-Orchestrator structural layer (inline shorthand parser, YAML loader, DAG builder, cycle detection, reference integrity, dry-run) and Track B Phase 1 protocol improvements (shared assumption extraction, synthetic diff points, advocate prompt update, three-level taxonomy, coverage check, convergence formula update).

---

### T02.01 -- Implement inline shorthand parser for pipeline phase definitions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | The inline shorthand parser enables users to define multi-phase pipelines directly in the CLI using `phase1 -> phase2 | phase3` syntax with `generate:<agents>` and `compare` phase types. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [█████████░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0005/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0005/evidence.md

**Deliverables:**
- Inline shorthand parser that accepts `phase1 -> phase2 | phase3` syntax and returns a structured phase list with `generate:<agents>` and `compare` phase type support

**Steps:**
1. **[PLANNING]** Review Spec1 "Inline Shorthand" section for all syntax examples and edge cases
2. **[PLANNING]** Identify parser output schema: structured phase list with phase type, agent list, and dependency edges
3. **[EXECUTION]** Implement tokenizer for `->` (sequential), `|` (parallel), `generate:<agents>`, and `compare` tokens
4. **[EXECUTION]** Implement parser that builds structured phase list from token stream
5. **[EXECUTION]** Add error handling for malformed shorthand: descriptive error messages for ambiguous or invalid syntax
6. **[VERIFICATION]** Test parser against all Spec1 inline shorthand examples; verify structured output matches expected phase definitions
7. **[COMPLETION]** Document parser grammar and output schema in D-0005/spec.md

**Acceptance Criteria:**
- Parser correctly parses all inline shorthand examples from Spec1 Section "Inline Shorthand" and returns structured phase list
- `generate:<agents>` phase type extracts agent identifiers; `compare` phase type is recognized without agents
- Malformed input (missing arrows, unmatched pipes) produces descriptive error message identifying the syntax issue
- Parser grammar and output schema documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0005/spec.md`

**Validation:**
- Manual check: run parser against all Spec1 shorthand examples; verify structured output matches expected definitions
- Evidence: linkable artifact produced (D-0005/spec.md with grammar specification)

**Dependencies:** T01.01 (pipeline flag detection stub)
**Rollback:** Remove parser implementation; revert SKILL.md meta-orchestrator section

---

### T02.02 -- Implement YAML pipeline file loader with schema validation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | Users must be able to define complex pipelines via YAML files (`--pipeline @path.yaml`) with full schema validation rejecting unknown or missing fields. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [█████████░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0006/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0006/evidence.md

**Deliverables:**
- YAML pipeline file loader that reads `--pipeline @path.yaml`, validates against phase schema, and produces the same structured phase list as the inline parser

**Steps:**
1. **[PLANNING]** Extract YAML schema requirements from Spec1: required fields, optional fields, phase type constraints
2. **[PLANNING]** Define schema validation rules: required fields cause rejection on absence; unknown fields cause rejection
3. **[EXECUTION]** Implement YAML file reader triggered by `--pipeline @<path>` pattern detection
4. **[EXECUTION]** Implement schema validator checking required/optional/unknown fields per phase definition
5. **[EXECUTION]** Convert validated YAML structure to the same structured phase list format as inline parser output
6. **[VERIFICATION]** Load the 3-phase example YAML from Spec1 without errors; verify rejection of YAML with unknown/missing fields
7. **[COMPLETION]** Document YAML schema specification and validation rules in D-0006/spec.md

**Acceptance Criteria:**
- Loader successfully parses the 3-phase example YAML from Spec1 and produces correct structured phase list
- YAML with unknown fields produces descriptive rejection error naming the unknown field
- YAML with missing required fields produces descriptive rejection error naming the missing field
- Schema specification documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0006/spec.md`

**Validation:**
- Manual check: load Spec1 3-phase YAML example; verify structured output; test rejection of invalid YAML
- Evidence: linkable artifact produced (D-0006/spec.md with schema specification)

**Dependencies:** T01.01 (pipeline flag detection stub)
**Rollback:** Remove YAML loader; revert pipeline file handling

---

### T02.03 -- Implement DAG builder from phase definitions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | The DAG builder constructs a directed acyclic graph from phase definitions, identifying parallel phases (same dependency level) and sequential gates (dependency edges) for execution scheduling. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0007/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0007/evidence.md

**Deliverables:**
- DAG builder that accepts structured phase list and produces a directed acyclic graph with nodes (phases) and edges (dependencies), identifying parallelizable phase groups

**Steps:**
1. **[PLANNING]** Define DAG data structure: nodes (phase ID, type, config), edges (dependency relationships), levels (parallelization groups)
2. **[PLANNING]** Review structured phase list output from T02.01/T02.02 to confirm input contract
3. **[EXECUTION]** Implement DAG construction: create nodes from phase definitions, create edges from `depends_on` fields
4. **[EXECUTION]** Implement level assignment: topological sort to identify parallelizable phase groups at each dependency level
5. **[EXECUTION]** Implement DAG serialization for dry-run output and manifest consumption
6. **[VERIFICATION]** Verify DAG correctly identifies parallel phases and sequential gates for 3-phase canonical workflow
7. **[COMPLETION]** Document DAG data structure and construction algorithm in D-0007/spec.md

**Acceptance Criteria:**
- DAG builder produces correct graph for 3-phase canonical workflow: `generate -> generate -> compare` with proper dependency edges
- Parallel phases (same dependency level) are correctly identified and grouped
- Sequential gates (dependency edges) enforce execution ordering between levels
- DAG structure documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0007/spec.md`

**Validation:**
- Manual check: build DAG from 3-phase canonical workflow; verify node/edge/level structure
- Evidence: linkable artifact produced (D-0007/spec.md with DAG algorithm)

**Dependencies:** T02.01 (inline parser), T02.02 (YAML loader)
**Rollback:** Remove DAG builder; downstream M4 tasks become blocked

---

### T02.04 -- Implement cycle detection with descriptive error messages

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | Circular dependencies in pipeline definitions must be detected and reported with descriptive error messages showing the exact cycle path. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0008/spec.md

**Deliverables:**
- Cycle detection integrated into DAG builder that aborts with descriptive error on circular dependency, showing the exact cycle path

**Steps:**
1. **[PLANNING]** Review DAG builder output (T02.03) to identify integration point for cycle detection
2. **[PLANNING]** Define error message format: `"Circular dependency detected: A -> B -> A"`
3. **[EXECUTION]** Implement DFS-based cycle detection during DAG construction
4. **[EXECUTION]** Format error message showing the exact cycle path when detected
5. **[VERIFICATION]** Test with `A -> B -> A` input; verify error message matches `"Circular dependency detected: A -> B -> A"`
6. **[COMPLETION]** Document cycle detection algorithm in D-0008/spec.md

**Acceptance Criteria:**
- Input `A -> B -> A` produces error `"Circular dependency detected: A -> B -> A"`
- Cycle detection runs during DAG construction before any phase execution begins
- Longer cycles (A -> B -> C -> A) are detected and reported with full path
- Algorithm documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0008/spec.md`

**Validation:**
- Manual check: test cycle detection with A -> B -> A and longer cycle inputs; verify error messages
- Evidence: linkable artifact produced (D-0008/spec.md)

**Dependencies:** T02.03 (DAG builder)
**Rollback:** Remove cycle detection from DAG builder

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.04

**Purpose:** Verify Track A parser and DAG foundation is correct before proceeding with remaining architecture and protocol tasks.
**Checkpoint Report Path:** .dev/releases/current/2.09-adversarial-v2/tasklist/checkpoints/CP-P02-T01-T04.md

**Verification:**
- Inline shorthand parser handles all Spec1 examples (T02.01)
- YAML loader validates and rejects invalid schemas (T02.02)
- DAG builder produces correct graph with cycle detection (T02.03, T02.04)

**Exit Criteria:**
- All 4 tasks completed with deliverables D-0005 through D-0008 produced
- Parser and loader produce identical structured phase list format
- Cycle detection error messages match specified format

---

### T02.05 -- Implement reference integrity validation for depends_on phase IDs

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | All `depends_on` phase IDs in pipeline definitions must reference existing phases; unknown phase IDs must produce descriptive error messages. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0009/spec.md

**Deliverables:**
- Reference integrity validator that checks all `depends_on` phase IDs exist in the phase list and produces `"Unknown phase reference: <id>"` for invalid references

**Steps:**
1. **[PLANNING]** Review DAG builder (T02.03) to identify where depends_on references are resolved
2. **[PLANNING]** Define error message format: `"Unknown phase reference: <id>"`
3. **[EXECUTION]** Implement validation pass: collect all phase IDs, then check each depends_on reference against the set
4. **[EXECUTION]** Report all invalid references (not just the first) in a single error message
5. **[VERIFICATION]** Test with unknown phase ID in depends_on; verify error message matches format
6. **[COMPLETION]** Document validation logic in D-0009/spec.md

**Acceptance Criteria:**
- Unknown phase ID in `depends_on` produces `"Unknown phase reference: <id>"` error
- All invalid references are reported in a single validation pass (not fail-fast on first)
- Valid phase definitions with correct depends_on references pass validation without errors
- Validation logic documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0009/spec.md`

**Validation:**
- Manual check: test with valid and invalid depends_on references; verify error messages
- Evidence: linkable artifact produced (D-0009/spec.md)

**Dependencies:** T02.03 (DAG builder)
**Rollback:** Remove reference integrity validation from DAG builder

---

### T02.06 -- Implement dry-run render for pipeline execution plan

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | Dry-run mode validates the DAG and outputs the execution plan to console/file without executing phases, enabling pre-flight cost estimation and plan review (SC-002). |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0010/spec.md

**Deliverables:**
- Dry-run render that validates DAG, outputs execution plan (phase order, parallelization groups, estimated token costs) to console/file, and exits without executing any phases

**Steps:**
1. **[PLANNING]** Define dry-run output format: phase execution order, parallelization groups, estimated costs per phase
2. **[PLANNING]** Identify the DAG builder output (T02.03) fields needed for execution plan rendering
3. **[EXECUTION]** Implement dry-run flag detection (`--dry-run` or `--pipeline-dry-run`)
4. **[EXECUTION]** Implement execution plan renderer: topological order, parallel groups, phase configs, token estimates
5. **[EXECUTION]** Add output routing: console by default, file output with `--output <path>` option
6. **[VERIFICATION]** Verify dry-run output matches actual execution plan for 3-phase canonical workflow (SC-002)
7. **[COMPLETION]** Document dry-run output format in D-0010/spec.md

**Acceptance Criteria:**
- Dry-run for 3-phase canonical workflow produces execution plan matching actual execution order (SC-002)
- Output includes: phase execution order, parallelization groups, phase types, agent assignments
- No phases are executed during dry-run (exit after plan output)
- Output format documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0010/spec.md`

**Validation:**
- Manual check: compare dry-run output for canonical workflow against actual execution plan
- Evidence: linkable artifact produced (D-0010/spec.md)

**Dependencies:** T02.03 (DAG builder)
**Rollback:** Remove dry-run render functionality

---

### T02.07 -- Implement shared assumption extraction sub-phase in Step 1

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | AD-2 addresses the "agreement = no scrutiny" blind spot by extracting implicit shared assumptions from variant agreements and classifying them as STATED/UNSTATED/CONTRADICTED. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (system-wide protocol modification), performance (overhead constraint NFR-004) |
| Tier | STRICT |
| Confidence | [█████████░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0011/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0011/evidence.md

**Deliverables:**
- Shared assumption extraction sub-phase added to Step 1 of the adversarial debate protocol: identifies agreement points, enumerates assumptions behind each, classifies as STATED/UNSTATED/CONTRADICTED

**Steps:**
1. **[PLANNING]** Review existing Step 1 (diff analysis) to identify insertion point for assumption extraction sub-phase
2. **[PLANNING]** Define extraction algorithm: scan agreement points, enumerate implicit assumptions, classify each
3. **[EXECUTION]** Implement agreement identification: detect diff points where all variants agree
4. **[EXECUTION]** Implement assumption enumeration: for each agreement, extract underlying preconditions
5. **[EXECUTION]** Implement classification logic: STATED (explicit in variants), UNSTATED (implicit), CONTRADICTED (inconsistent)
6. **[VERIFICATION]** Test AC-AD2-1: 3 variants assuming 1:1 event-widget mapping produces UNSTATED precondition surfaced
7. **[COMPLETION]** Document extraction algorithm and classification rules in D-0011/spec.md

**Acceptance Criteria:**
- AC-AD2-1 passes: 3 variants assuming 1:1 event-widget mapping results in UNSTATED precondition being surfaced
- Classification produces STATED/UNSTATED/CONTRADICTED labels for each extracted assumption
- Extraction sub-phase integrates into Step 1 without disrupting existing diff analysis output
- Extraction algorithm documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0011/spec.md`

**Validation:**
- Manual check: run AC-AD2-1 test scenario; verify UNSTATED precondition is surfaced with correct classification
- Evidence: linkable artifact produced (D-0011/spec.md with algorithm documentation)

**Dependencies:** T01.03 (integration sequencing plan)
**Rollback:** Remove extraction sub-phase from Step 1; revert to original diff analysis

---

### T02.09 -- Promote UNSTATED preconditions to synthetic [SHARED-ASSUMPTION] diff points

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | UNSTATED preconditions must become synthetic diff points (A-NNN scheme) added to diff-analysis.md Shared Assumptions section, included in the convergence denominator. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (modifies convergence calculation denominator) |
| Tier | STRICT |
| Confidence | [█████████░] 86% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0012/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0012/evidence.md

**Deliverables:**
- Promotion logic converting UNSTATED assumptions to `[SHARED-ASSUMPTION]` tagged diff points with A-NNN identifiers, added to diff-analysis.md and included in convergence denominator

**Steps:**
1. **[PLANNING]** Define A-NNN identifier scheme: sequential assignment starting from A-001 per debate session
2. **[PLANNING]** Identify diff-analysis.md structure and location of Shared Assumptions section
3. **[EXECUTION]** Implement promotion: convert each UNSTATED precondition to a `[SHARED-ASSUMPTION]` diff point with A-NNN ID
4. **[EXECUTION]** Add promoted points to diff-analysis.md Shared Assumptions section in structured table format
5. **[EXECUTION]** Update convergence denominator calculation to include A-NNN points in total_diff_points
6. **[VERIFICATION]** Test AC-AD2-3: verify convergence denominator includes A-NNN points after promotion
7. **[COMPLETION]** Document promotion logic and A-NNN scheme in D-0012/spec.md

**Acceptance Criteria:**
- AC-AD2-3 passes: convergence denominator includes A-NNN points in total_diff_points calculation
- Each UNSTATED precondition receives a unique A-NNN identifier (sequential, no gaps)
- Promoted points appear in diff-analysis.md Shared Assumptions section with structured table format
- A-NNN scheme documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0012/spec.md`

**Validation:**
- Manual check: verify A-NNN points appear in diff-analysis.md and convergence denominator after promotion
- Evidence: linkable artifact produced (D-0012/spec.md with promotion logic)

**Dependencies:** T02.07 (shared assumption extraction)
**Rollback:** Remove promotion logic; revert convergence denominator calculation

---

### T02.09 -- Update advocate prompt template with ACCEPT/REJECT/QUALIFY for shared assumptions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | Advocates must explicitly respond to each [SHARED-ASSUMPTION] point with ACCEPT/REJECT/QUALIFY; omissions must be flagged in the transcript. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0013/spec.md

**Deliverables:**
- Updated advocate prompt template requiring ACCEPT/REJECT/QUALIFY response for each [SHARED-ASSUMPTION] point, with omission detection and flagging

**Steps:**
1. **[PLANNING]** Review existing advocate prompt template to identify insertion point for shared assumption handling
2. **[PLANNING]** Define omission detection logic: compare A-NNN IDs in prompt vs A-NNN IDs in response
3. **[EXECUTION]** Add shared assumption section to advocate prompt listing all A-NNN points with ACCEPT/REJECT/QUALIFY requirement
4. **[EXECUTION]** Implement omission detection: flag missing A-NNN responses in transcript with warning
5. **[VERIFICATION]** Test AC-AD2-4: verify omitted shared assumption responses are flagged in transcript
6. **[COMPLETION]** Document updated template in D-0013/spec.md

**Acceptance Criteria:**
- AC-AD2-4 passes: omitted shared assumption responses are flagged in transcript
- Advocate prompt includes all A-NNN points with explicit ACCEPT/REJECT/QUALIFY instruction
- Omission detection identifies which specific A-NNN IDs were not addressed
- Updated template documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0013/spec.md`

**Validation:**
- Manual check: run advocate round with deliberate A-NNN omission; verify flagging in transcript
- Evidence: linkable artifact produced (D-0013/spec.md)

**Dependencies:** T02.09 (synthetic diff points with A-NNN scheme)
**Rollback:** Revert advocate prompt template to pre-change version

---

### Checkpoint: Phase 2 / Tasks T02.05-T02.09

**Purpose:** Verify Track A validation and Track B assumption extraction are functional before taxonomy and convergence modifications.
**Checkpoint Report Path:** .dev/releases/current/2.09-adversarial-v2/tasklist/checkpoints/CP-P02-T05-T09.md

**Verification:**
- Reference integrity and dry-run produce correct outputs (T02.05, T02.06)
- Shared assumption extraction surfaces UNSTATED preconditions (T02.07, T02.09)
- Advocate prompt correctly flags omitted shared assumption responses (T02.09)

**Exit Criteria:**
- All 5 tasks completed with deliverables D-0009 through D-0013 produced
- AC-AD2-1 through AC-AD2-4 test scenarios pass
- Dry-run output matches expected execution plan (SC-002 partial)

---

### T02.10 -- Define three-level taxonomy (L1/L2/L3) in SKILL.md with auto-tag signals

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | AD-5 requires a three-level debate topic taxonomy (L1/L2/L3) with auto-tag signals to ensure state-mechanics-level debate cannot be bypassed; A-NNN points with state/guard/boundary terms auto-tag as L3. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [█████████░] 86% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0014/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0014/evidence.md

**Deliverables:**
- Three-level taxonomy (L1/L2/L3) defined in SKILL.md with >=5 auto-tag signals per level, including A-NNN auto-tagging rules for L3

**Steps:**
1. **[PLANNING]** Review Spec2 AD-5 for taxonomy level definitions and auto-tag signal requirements
2. **[PLANNING]** Identify SKILL.md section for taxonomy definition per integration sequencing plan (T01.03)
3. **[EXECUTION]** Define L1 (surface), L2 (structural), L3 (state mechanics) levels with descriptions and >=5 auto-tag signals each
4. **[EXECUTION]** Implement auto-tag logic: scan diff point text for level-specific signal terms
5. **[EXECUTION]** Add A-NNN auto-tag rule: shared assumption points containing state/guard/boundary terms auto-tag as L3 (AC-AD5-3)
6. **[VERIFICATION]** Verify each level has >=5 auto-tag signals; verify A-NNN L3 auto-tagging for state/guard/boundary terms
7. **[COMPLETION]** Document taxonomy definition and auto-tag rules in D-0014/spec.md

**Acceptance Criteria:**
- SKILL.md contains L1/L2/L3 taxonomy definition with >=5 auto-tag signals per level
- AC-AD5-3 passes: A-NNN points with state/guard/boundary terms are auto-tagged as L3
- Auto-tag signals are mutually exclusive (each signal maps to exactly one level) or priority-ordered
- Taxonomy documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0014/spec.md`

**Validation:**
- Manual check: verify taxonomy definition in SKILL.md; test A-NNN auto-tagging with state/guard/boundary terms
- Evidence: linkable artifact produced (D-0014/spec.md)

**Dependencies:** T01.03 (integration sequencing plan), T02.09 (A-NNN scheme)
**Rollback:** Remove taxonomy section from SKILL.md

---

### T02.11 -- Implement post-round taxonomy coverage check and forced round trigger

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | AD-5 requires a post-round check that blocks convergence when a taxonomy level has zero coverage and triggers a forced debate round targeting the uncovered level. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | performance (forced round adds overhead), cross-cutting scope (modifies convergence gating) |
| Tier | STRICT |
| Confidence | [█████████░] 86% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0015/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0015/evidence.md

**Deliverables:**
- Post-round taxonomy coverage check that blocks convergence when any level has zero coverage, plus forced round trigger dispatching a targeted debate round for the uncovered level

**Steps:**
1. **[PLANNING]** Review convergence calculation to identify check insertion point (after each debate round)
2. **[PLANNING]** Define forced round dispatch: which level, prompt template, depth constraint
3. **[EXECUTION]** Implement coverage check: after each round, count diff points per taxonomy level
4. **[EXECUTION]** Implement convergence gate: if any level has zero coverage, block convergence regardless of score
5. **[EXECUTION]** Implement forced round trigger: dispatch debate round targeting uncovered level with level-specific prompt
6. **[VERIFICATION]** Test AC-AD5-1: verify 87% convergence is blocked when L3 has zero coverage; verify forced L3 round triggers
7. **[COMPLETION]** Document coverage check and forced round logic in D-0015/spec.md

**Acceptance Criteria:**
- AC-AD5-1 passes: 87% convergence blocked when L3 has zero coverage; forced L3 round triggered
- AC-AD5-4 passes: forced round still triggers at depth=quick when L3 has zero coverage
- Coverage check runs after each debate round and before convergence assessment
- Logic documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0015/spec.md`

**Validation:**
- Manual check: run debate to 87% convergence with L3 at zero coverage; verify block and forced round
- Evidence: linkable artifact produced (D-0015/spec.md)

**Dependencies:** T02.10 (taxonomy definition)
**Rollback:** Remove coverage check and forced round trigger; revert convergence gating

---

### T02.12 -- Update convergence formula with taxonomy gate and A-NNN denominator

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | The convergence formula must include the taxonomy coverage gate AND A-NNN points in the total_diff_points denominator to ensure shared assumptions affect convergence scoring. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0016/spec.md

**Deliverables:**
- Updated convergence formula that includes taxonomy coverage gate as a boolean pre-condition and A-NNN points in total_diff_points denominator

**Steps:**
1. **[PLANNING]** Review current convergence formula to identify denominator and gate logic
2. **[PLANNING]** Define formula update: `total_diff_points = original_diff_points + A_NNN_count`; taxonomy gate is boolean AND with score threshold
3. **[EXECUTION]** Update convergence denominator to include A-NNN count from T02.09
4. **[EXECUTION]** Add taxonomy gate: convergence requires `all_levels_covered AND score >= threshold`
5. **[VERIFICATION]** Test: convergence with A-NNN points changes denominator correctly; taxonomy gate blocks when level uncovered
6. **[COMPLETION]** Document updated formula in D-0016/spec.md

**Acceptance Criteria:**
- Convergence denominator includes A-NNN points: `total_diff_points = original + A_NNN_count`
- Taxonomy gate is applied: convergence requires all taxonomy levels to have >0 coverage
- Formula change is backward compatible: debates without shared assumptions produce identical convergence scores
- Updated formula documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0016/spec.md`

**Validation:**
- Manual check: compute convergence with and without A-NNN points; verify denominator change
- Evidence: linkable artifact produced (D-0016/spec.md)

**Dependencies:** T02.09 (A-NNN points), T02.11 (taxonomy coverage check)
**Rollback:** Revert convergence formula to pre-change version

---

### Checkpoint: End of Phase 2

**Purpose:** Verify all Track A architecture (DAG pipeline) and Track B Phase 1 protocol improvements are complete and independently functional before integration testing.
**Checkpoint Report Path:** .dev/releases/current/2.09-adversarial-v2/tasklist/checkpoints/CP-P02-END.md

**Verification:**
- Track A: inline parser, YAML loader, DAG builder, cycle detection, reference integrity, dry-run all produce correct output (T02.01-T02.06)
- Track B Phase 1: shared assumption extraction, A-NNN promotion, advocate prompt, taxonomy, coverage check, convergence formula all pass their AC assertions (T02.07-T02.12)
- AC-AD2-1 through AC-AD2-4 and AC-AD5-1 through AC-AD5-4 pass

**Exit Criteria:**
- All 12 Phase 2 tasks completed with deliverables D-0005 through D-0016 produced
- Both Track A and Track B workstreams independently functional
- No regressions in existing Mode A/B behavior (verified against T01.02 baseline)
