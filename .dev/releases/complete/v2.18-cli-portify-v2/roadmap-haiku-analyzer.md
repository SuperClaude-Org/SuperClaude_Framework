---
spec_source: "refactoring-spec-cli-portify.md"
complexity_score: 0.92
primary_persona: analyzer
---

# 1. Executive Summary

This roadmap delivers an enterprise-grade portification workflow for `sc-cli-portify` that converts inference-heavy SuperClaude workflows into deterministic, resumable CLI pipelines while preserving strict safety, API conformance, and auditability.

The initiative is high risk and high complexity because it combines:

- 5 contract-driven phases with resumable execution
- 70 total requirements across 7 technical domains
- live API snapshotting and drift protection
- deterministic multi-file code generation
- CLI integration into an existing Click application
- strict collision handling and non-destructive guarantees
- human review gates at critical interpretation boundaries

## Primary analyzer concerns

1. **API drift is the top delivery risk.**
   - The roadmap must block on stale refs and continuously verify against the live pipeline API.
2. **Spec ambiguity is a material execution risk.**
   - Open questions around `TurnLedger`, `--dry-run`, `--skip-integration`, Phase 4 schema, output defaults, and test placement should be resolved before Phase 3.
3. **Determinism and invariant preservation are core quality gates.**
   - Step conservation, mapping coverage, import acyclicity, and schema stability must be enforced as release blockers.
4. **Unsafe workflows must fail early.**
   - Unsupported patterns should abort in Phase 0 before downstream analysis or generation effort is spent.
5. **Human approval is intentional, not overhead.**
   - Review gates after analysis and design reduce misclassification risk and prevent bad code generation from becoming expensive rework.

## Strategic recommendation

Deliver this project in two macro-tracks:

- **Track A: Foundation hardening**
  - command/protocol split, metadata normalization, sync integrity, ref drift correction, contract schemas
- **Track B: Portification engine**
  - phased workflow discovery, mapping, generation, integration, resumability, validation

This sequencing reduces risk by establishing trustworthy primitives before enabling code generation.

---

# 2. Phased Implementation Plan with Milestones

## Phase A. Foundation Realignment and Spec Hardening

### Objectives
Establish the structural and governance prerequisites required for safe portification.

### Scope
- FR-001 to FR-006
- FR-048
- NFR-014 to NFR-018
- architectural constraints around command/protocol split and sync layout

### Key work items
1. **Implement command/protocol split**
   - Move `sc-cli-portify/SKILL.md` to `sc-cli-portify-protocol/SKILL.md`
   - Move `refs/` under protocol directory
   - Create thin `commands/cli-portify.md` shim
   - Remove deprecated legacy directory after migration validation

2. **Promote commented metadata to YAML frontmatter**
   - Standardize:
     - `name`
     - `description`
     - `category`
     - `complexity`
     - `allowed-tools`
     - `mcp-servers`
     - `personas`
     - `argument-hint`

3. **Repair source/dev-copy integrity**
   - Ensure `__init__.py` exists in both `src/` and `.claude/` copies
   - Extend `make verify-sync` coverage for protocol layout

4. **Correct ref drift before protocol use**
   - Update:
     - `refs/pipeline-spec.md`
     - `refs/code-templates.md`
   - Align to live API field names and signatures

5. **Resolve spec ambiguities**
   - Clarify OQ-001 through OQ-010 before generation implementation proceeds

### Milestone
**M1 — Foundation Ready**
- Protocol structure migrated
- command shim present
- metadata normalized
- sync verification updated
- stale refs corrected
- unresolved blocking ambiguities triaged

### Exit criteria
- No legacy structural conflicts remain
- Protocol and command are discoverable from both `src/` and `.claude/`
- Ref files verified against live API
- Open questions categorized into:
  - must-resolve-before-Phase-1
  - must-resolve-before-Phase-2
  - must-resolve-before-Phase-3

### Timeline estimate
- **3–5 working days**

---

## Phase B. Contract Framework and Phase Schema Establishment

### Objectives
Create the contract layer that all subsequent phases rely on.

### Scope
- FR-007 to FR-009
- FR-043
- FR-052
- NFR-009, NFR-015, NFR-016

### Key work items
1. **Define unified YAML contract header**
   - Required fields:
     - `phase`
     - `status`
     - `timestamp`
     - `resume_checkpoint`
     - `validation_status`

2. **Define per-phase contract schemas**
   - `portify-prerequisites.yaml`
   - `portify-analysis.yaml`
   - `portify-spec.yaml`
   - `portify-codegen.yaml`
   - Phase 4 integration contract schema
   - return contract schema for success and failure

3. **Implement contract validation entry gates**
   - Each phase validates prior phase contract before execution
   - Invalid or stale contracts force halt or re-run

4. **Implement resume protocol design**
   - Read latest phase contract
   - validate contract freshness
   - skip already-completed valid phases
   - resume from failed phase
   - always emit `resume_command`

5. **Define null-field policy on failures**
   - unreached fields explicitly set to `null`

### Milestone
**M2 — Contract System Operational**
- Stable, versioned phase contracts exist
- Entry/exit validation is enforceable
- Failure and resume semantics are defined

### Exit criteria
- Contract schemas are machine-validated
- Resume behavior works across synthetic failure cases
- Return contract emitted for success and failure paths

### Timeline estimate
- **2–4 working days**

---

## Phase C. Phase 0 Prerequisites Engine

### Objectives
Build the early-fail safety layer that determines whether a workflow is portifiable.

### Scope
- FR-010 to FR-014
- FR-045 to FR-047
- RISK-001, RISK-002, RISK-003, RISK-008, RISK-012

### Key work items
1. **Workflow path resolution**
   - Resolve `--workflow`
   - locate command file
   - locate `SKILL.md`
   - locate refs/rules/templates/scripts
   - fail on ambiguous matches

2. **Live API snapshotting**
   - Read `models.py` and `gates.py`
   - capture signatures for:
     - `SemanticCheck`
     - `GateCriteria`
     - `gate_passed()`
     - `PipelineConfig`
     - `Step`
     - `StepResult`
     - `GateMode`
   - emit `api-snapshot.yaml`

3. **Collision policy enforcement**
   - detect existing output
   - distinguish portified vs non-portified content
   - honor naming and overwrite policy
   - block on `main.py` command collision

4. **Unsupported pattern scan**
   - detect:
     - recursive agent self-orchestration
     - human interactive decision dependencies
     - missing stable artifact boundaries
     - dynamic code generation/eval
   - emit blocking warning and abort when required

5. **Emit prerequisites contract**
   - include:
     - `workflow_path`
     - `component_count`
     - `api_snapshot_path`
     - `unsupported_patterns_detected`
     - `output_directory`
     - `collision_policy_applied`

### Milestone
**M3 — Safe-to-Analyze Gate**
- Only valid, supported workflows advance
- API and path assumptions are proven, not guessed

### Exit criteria
- All 6 command shim error codes handled
- `api-snapshot.yaml` reproducible
- unsupported pattern detection validated on negative fixtures

### Timeline estimate
- **3–4 working days**

---

## Phase D. Phase 1 Workflow Analysis and Source Model Extraction

### Objectives
Create the authoritative decomposition of the source workflow.

### Scope
- FR-015 to FR-023
- FR-049 to FR-051
- NFR-004, NFR-005
- RISK-004, RISK-007

### Key work items
1. **Build component inventory**
   - assign stable `component_id` values (`C-NNN`)
   - capture paths, line counts, purpose

2. **Construct source step registry**
   - assign stable `source_id` values (`S-NNN`)
   - enforce source operation conservation

3. **Classify each step**
   - `pure_programmatic`
   - `claude_assisted`
   - `hybrid`
   - confidence score with evidence
   - review flag when confidence < 0.7

4. **Build dependency DAG**
   - data-flow edges
   - acyclicity validation
   - parallel group extraction

5. **Assign gate policy**
   - tier: `EXEMPT|LIGHT|STANDARD|STRICT`
   - mode: `BLOCKING|TRAILING`
   - auto-escalate unsafe trailing gates

6. **Implement 7 self-validation checks**
   - 6 blocking
   - 1 advisory

7. **Generate outputs**
   - `portify-analysis.md` under 400 lines
   - `portify-analysis.yaml`

8. **User review checkpoint**
   - allow classification override
   - allow missing-step correction
   - persist chosen interpretations

9. **TodoWrite integration**
   - track 23 subphase tasks
   - checkpoint after phase completion and review gates

### Milestone
**M4 — Analyzed Source of Truth**
- Source workflow fully inventoried
- step registry stable and reviewable
- dependency graph validated

### Exit criteria
- Conservation invariant holds
- DAG is acyclic
- confidence exceptions surfaced to user
- outputs deterministic across repeated runs

### Timeline estimate
- **4–6 working days**

---

## Phase E. Phase 2 Generation Specification and Coverage Design

### Objectives
Translate workflow analysis into a precise, API-conformant generation blueprint.

### Scope
- FR-024 to FR-033
- NFR-003, NFR-006, NFR-010, NFR-011, NFR-012
- RISK-001, RISK-003, RISK-011

### Key work items
1. **Design step graph mapping**
   - support:
     - `1:1`
     - `1:N`
     - `N:1`
     - `1:0`
   - record justification
   - record elimination approvals

2. **Enforce mapping coverage invariant**
   - registry count equals mapped plus eliminated

3. **Design generated models**
   - `Config` extends `PipelineConfig`
   - `Result` extends `StepResult`
   - `Status` enum
   - monitor state with NDJSON signals
   - `TurnLedger` integration once clarified

4. **Design prompt specifications**
   - input strategy
   - output sections
   - frontmatter fields
   - markers
   - structural requirements
   - split to `portify-prompts.md` if >300 lines

5. **Design gate definitions**
   - exact `GateCriteria` field names
   - `Callable[[str], bool]` semantic checks
   - tier and enforcement design

6. **Implement pure-programmatic steps as real Python**
   - no prose-only placeholders

7. **Design executor model**
   - sprint-style synchronous supervisor
   - `ThreadPoolExecutor` for batch parallelism only

8. **Build pattern coverage matrix**
   - prove templates cover all supported patterns
   - abort on unsupported pattern gap

9. **Run 8 self-validation checks**
   - 7 blocking
   - 1 advisory

10. **Emit and review**
   - `portify-spec.yaml`
   - approval gate before codegen

### Milestone
**M5 — Codegen Blueprint Approved**
- Full mapping, models, prompts, gates, and executor architecture approved

### Exit criteria
- API conformance proven against snapshot
- pattern coverage complete
- user approval captured
- no unresolved unsupported patterns remain

### Timeline estimate
- **4–6 working days**

---

## Phase F. Phase 3 Deterministic Code Generation and Validation

### Objectives
Generate the implementation artifacts in strict dependency order with zero partial-state tolerance.

### Scope
- FR-034 to FR-038
- NFR-001, NFR-002, NFR-007
- RISK-001, RISK-005

### Key work items
1. **Generate files in required order**
   1. `models`
   2. `gates`
   3. `prompts`
   4. `config`
   5. `monitor`
   6. `process`
   7. `executor`
   8. `tui`
   9. `logging_`
   10. `diagnostics`
   11. `commands`
   12. `__init__.py`

2. **Enforce atomic generation**
   - stop on first failure
   - write failure contract
   - preserve resumability

3. **Run per-file validation**
   - `ast.parse`
   - import verification
   - base-class contract checks
   - `GateCriteria` field name matching
   - `SemanticCheck` signature verification
   - advisory quality check

4. **Run cross-file validation**
   - module completeness
   - circular import detection
   - `__init__.py` export accuracy
   - step count matching

5. **Emit codegen contract**
   - generated files
   - validation results

### Milestone
**M6 — Generated Module Structurally Valid**
- Generated package exists and passes structural validation

### Exit criteria
- all files parse cleanly
- import graph acyclic
- no base-type reimplementation
- generated outputs match approved mapping counts

### Timeline estimate
- **5–7 working days**

---

## Phase G. Phase 4 CLI Integration, Structural Testing, and Handoff

### Objectives
Integrate generated module into the CLI safely and produce operational handoff artifacts.

### Scope
- FR-039 to FR-042
- FR-044
- SC-008 to SC-014
- RISK-008, RISK-009, RISK-010

### Key work items
1. **Patch `main.py` safely**
   - import generated command
   - register via `app.add_command()`
   - abort on collision

2. **Run integration smoke tests**
   - module imports
   - Click command group exists
   - registered name matches expected command

3. **Generate structural test file**
   - verify:
     - step graph completeness
     - gate definitions
     - model consistency
     - command registration
   - place in approved test directory once clarified

4. **Write handoff summary**
   - file inventory
   - CLI usage
   - step graph summary
   - known limitations
   - resume command template

5. **Emit final return contract**
   - success or failure state
   - phase contracts
   - warnings
   - resume info
   - generated counts
   - snapshot hash

### Milestone
**M7 — Integrated and Reviewable CLI Feature**
- command is registered, structurally testable, and documented

### Exit criteria
- smoke tests pass
- structural tests generated
- final summary written
- return contract complete

### Timeline estimate
- **2–4 working days**

---

## Phase H. Determinism, Golden Fixtures, and Release Validation

### Objectives
Validate that the workflow behaves consistently and safely across representative inputs.

### Scope
- SC-001 to SC-014
- especially SC-002 and SC-014

### Key work items
1. **Golden fixture suite**
   - simple sequential skill
   - batched audit skill
   - adversarial multi-agent skill
   - intentionally unsupported skill

2. **Determinism testing**
   - repeated runs produce identical:
     - `source_step_registry`
     - `step_mapping`
     - `module_plan`

3. **Failure-path validation**
   - emit return contract on all failure modes
   - validate resume from each phase boundary

4. **Collision safety tests**
   - portified overwrite handling
   - non-portified overwrite rejection
   - `main.py` name collision rejection

5. **Operational readiness review**
   - confirm strict compliance classification
   - validate TodoWrite coverage
   - verify MCP degradation warnings are advisory, not blocking

### Milestone
**M8 — Release Readiness**
- deterministic, resumable, and safe behavior proven against golden scenarios

### Exit criteria
- all success criteria met
- no unresolved high-risk defects
- known limitations documented

### Timeline estimate
- **3–5 working days**

---

# 3. Risk Assessment and Mitigation Strategies

## High Risks

### 1. Live API Drift
**Impact:** Generated code becomes incompatible with pipeline primitives.  
**Probability:** High.  
**Severity:** High.

**Mitigations**
- Snapshot API signatures in Phase 0
- compute and store snapshot hash
- verify hash at each phase boundary
- force re-snapshot and invalidate downstream contracts on drift
- treat drift as blocking, not advisory

**Owner**
- Pipeline integration lead

---

### 2. Ref File Staleness
**Impact:** Design and generation use incorrect field names and signatures.  
**Probability:** High.  
**Severity:** High.

**Mitigations**
- update refs before protocol activation
- add explicit stale-ref detector against live API
- require passing ref validation in Foundation phase
- prevent Phase 1 start when refs are stale

**Owner**
- Protocol maintainer

---

### 3. Unsupported Workflow Patterns
**Impact:** Large analysis investment lost; generated output invalid.  
**Probability:** Medium to High.  
**Severity:** High.

**Mitigations**
- perform unsupported pattern scan in Phase 0
- maintain explicit supported-pattern matrix
- abort before analysis when unsupported features are present
- include negative fixtures in validation suite

**Owner**
- Analysis engine owner

---

## Medium Risks

### 4. Step Conservation Violation
**Impact:** Incomplete or duplicated workflow translation.  
**Mitigations**
- stable `source_id` registry
- conservation checks in Phases 1 and 2
- divergence review workflow with explicit interpretation capture

### 5. Circular Imports in Generated Code
**Impact:** Generated package fails import validation.  
**Mitigations**
- strict module generation order
- dependency-aware design review in Phase 2
- graph-based circular import detection in Phase 3

### 6. MCP Server Unavailability
**Impact:** Reduced analysis richness or doc lookup failure.  
**Mitigations**
- native-tool fallback paths
- advisory warnings in contracts
- avoid hard dependency outside strict local validation primitives

### 7. Low Confidence Classifications
**Impact:** Wrong automation boundary, brittle generation.  
**Mitigations**
- confidence threshold at 0.7
- mandatory evidence and justification
- user override gate before progression

### 8. CLI Name Collision
**Impact:** Integration failure or accidental command override.  
**Mitigations**
- early collision detection
- duplicate check before `main.py` patch
- hard abort on conflict

### 9. Resume State Corruption
**Impact:** Invalid resume results or partial-state confusion.  
**Mitigations**
- revalidate completed contracts on resume
- compare filesystem state and snapshot hash
- invalidate downstream state if inconsistency detected

---

## Low Risks

### 10. Human Review Bottlenecks
**Mitigations**
- constrain review documents to focused summaries
- provide override mechanisms
- support `--dry-run` preview behavior once clarified

### 11. Pattern Coverage Gaps
**Mitigations**
- explicit template coverage matrix
- safe abort for uncovered patterns
- maintain extension backlog

### 12. Output Directory Collision with Human-Written Code
**Mitigations**
- marker-based overwrite policy
- never overwrite non-portified code
- require explicit overwrite path only for prior portified output

---

# 4. Resource Requirements and Dependencies

## Team / Role Requirements

### 1. Analyzer / Workflow Modeling Lead
Responsible for:
- source workflow decomposition
- conservation invariant enforcement
- dependency DAG design
- classification confidence review

### 2. Python / CLI Integration Engineer
Responsible for:
- generated module architecture
- Click integration
- import correctness
- structural test creation

### 3. Pipeline Contract Engineer
Responsible for:
- live API snapshotting
- gate definitions
- contract schema design
- resume and failure routing

### 4. QA / Validation Engineer
Responsible for:
- golden fixtures
- determinism testing
- failure-path validation
- collision safety tests

### 5. Maintainer / Reviewer
Responsible for:
- review gate approvals
- ambiguity resolution
- acceptance against success criteria

## Technical Dependencies

1. **`superclaude.cli.pipeline.models`**
   - base pipeline types
2. **`superclaude.cli.pipeline.gates`**
   - gate primitives and `gate_passed()`
3. **`superclaude.cli.main`**
   - Click registration point
4. **Python `ast`**
   - syntax validation
5. **`ThreadPoolExecutor`**
   - mandated parallelism mechanism
6. **Auggie MCP**
   - codebase discovery support
7. **Serena MCP**
   - semantic verification support
8. **Sequential MCP**
   - structured classification/design reasoning
9. **Context7 MCP**
   - external library lookup if needed

## Environment / Process Requirements

- UV-based Python execution for all test and script runs
- synced `src/` and `.claude/` development copies
- deterministic filesystem expectations for resume
- no modification of original source workflows
- strict non-destructive collision handling

## Recommended non-code prerequisites

1. Resolve open questions before codegen implementation.
2. Define contract schema versioning policy.
3. Define ownership of ref file maintenance.
4. Agree on placement for generated structural tests.
5. Define exact user approval mechanism across pause/resume boundaries.

---

# 5. Success Criteria and Validation Approach

## Success Criteria Mapping

### Functional success
1. All 5 execution phases complete or fail with resumable contracts.
2. Command/protocol split implemented correctly.
3. Every invocation emits a return contract.
4. User review gates function at analysis and spec phases.
5. Structural tests are generated and valid.

### Quality success
1. All generated Python parses via `ast.parse()`.
2. Import graph is acyclic.
3. `GateCriteria` field names exactly match live API snapshot.
4. `SemanticCheck` signatures use `Callable[[str], bool]`.
5. Deterministic outputs across repeated runs.

### Safety success
1. Unsupported workflows fail in Phase 0.
2. Non-portified code is never overwritten.
3. `main.py` collisions always abort.
4. Resume only proceeds from valid contracts.

## Validation Approach

### Phase-level validation
- Each phase has:
  - explicit entry criteria
  - explicit exit criteria
  - blocking and advisory checks
  - contract emission

### Structural validation
- `ast.parse()` per file
- import verification
- base-class extension verification
- cross-file export and step-count checks

### Behavioral validation
- smoke test generated CLI command registration
- validate module importability
- validate command name alignment

### Determinism validation
- run same workflow repeatedly
- compare:
  - source registry
  - step mapping
  - module plan
  - contract outputs where expected

### Negative-path validation
- unsupported workflow fixture
- stale ref fixture
- API drift fixture
- name collision fixture
- non-portified directory collision fixture

### Resume validation
- inject failures after each phase
- verify resume restarts at correct phase
- verify already-completed phases are revalidated, not blindly trusted

## Recommended acceptance gate

Do not declare completion until all of the following pass:

1. **Golden fixtures:** all 4 scenarios
2. **Determinism:** repeated identical outputs
3. **Safety:** collision and unsupported-path enforcement
4. **Integration:** command visible in CLI
5. **Contracts:** emitted on success and failure
6. **Sync:** `make verify-sync` includes new protocol structure

---

# 6. Timeline Estimates per Phase

## Summary Timeline

| Phase | Name | Estimate |
|---|---|---:|
| A | Foundation realignment and spec hardening | 3–5 days |
| B | Contract framework and schemas | 2–4 days |
| C | Phase 0 prerequisites engine | 3–4 days |
| D | Phase 1 workflow analysis | 4–6 days |
| E | Phase 2 generation specification | 4–6 days |
| F | Phase 3 code generation | 5–7 days |
| G | Phase 4 integration and handoff | 2–4 days |
| H | Determinism and release validation | 3–5 days |

## Total Estimated Delivery Window

- **Optimistic:** 26 working days
- **Likely:** 30–35 working days
- **Conservative:** 41 working days

## Timeline assumptions

1. Open questions are resolved before or during Phases A–B.
2. Live pipeline API remains stable or drift is detected early.
3. Review gates are answered promptly.
4. No major unsupported patterns are discovered late in Phase 2.
5. Golden fixture creation can proceed in parallel with Phases E–G.

## Schedule compression opportunities

If timeline pressure exists, the safest parallelization options are:

1. **Parallel track 1**
   - command/protocol split
   - metadata promotion
   - sync verification changes

2. **Parallel track 2**
   - contract schema drafting
   - return contract schema
   - resume protocol design

3. **Parallel track 3**
   - golden fixture preparation
   - unsupported-pattern test fixture creation

## Timeline risks

1. **Unresolved ambiguity risk**
   - Open questions extending into Phase 2 or 3 will likely delay design approval.
2. **API drift risk**
   - Midstream pipeline changes can invalidate prior contracts.
3. **Review latency risk**
   - Human gate delays can stretch elapsed calendar time more than implementation time.
4. **Coverage gap risk**
   - Discovering uncovered workflow patterns in Phase 2 may force redesign.

---

# Recommended Immediate Next Actions

1. **Resolve blocking open questions first**
   - especially OQ-002, OQ-003, OQ-004, OQ-008, OQ-009, OQ-010
2. **Execute Foundation phase before any generation work**
   - split protocol
   - fix refs
   - extend sync verification
3. **Treat API snapshot and ref alignment as hard gates**
   - no exceptions
4. **Implement contracts before feature logic**
   - resumability and safety depend on them
5. **Prepare golden fixtures early**
   - use them as design pressure tests throughout the project, not only at the end

# Analyzer Recommendation

This project should be managed as a **strict, gated delivery program**, not a loose feature implementation. The highest-leverage control points are:

- early unsupported-pattern detection
- live API drift blocking
- invariant checks in Phases 1 and 2
- atomic code generation
- resumable failure contracts
- user review gates before irreversible generation steps

If those controls are implemented first and enforced consistently, the roadmap is achievable despite the enterprise-level complexity.
