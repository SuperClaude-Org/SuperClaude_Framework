# Phase 1 -- Discovery and Architecture Lock

Scoped discovery phase resolving structurally-impactful open questions before implementation begins. Validates existing pipeline infrastructure patterns, locks architectural decisions for SIGINT handling, hash algorithms, and step wiring, and defines the canonical finding lifecycle model.

---

### T01.01 -- Review Pipeline Foundation and Confirm State Schema

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001, R-002 |
| Why | Understanding existing pipeline patterns (execute_pipeline, execute_roadmap, validate_executor, step/gate/state models, resume flow, hash usage) is prerequisite for all downstream implementation. State schema version must be confirmed before extending it. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema |
| Tier | EXEMPT |
| Confidence | `[████████--]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0001/notes.md`

**Deliverables:**
- Pipeline foundation review notes documenting: `execute_pipeline()` step model, `execute_roadmap()` extension points, `validate_executor.py` ClaudeProcess patterns, gate/state models, resume flow, hash usage patterns, current `schema_version` value

**Steps:**
1. **[PLANNING]** Identify the source files to review: `executor.py`, `validate_executor.py`, `pipeline/models.py`, `roadmap/models.py`, `.roadmap-state.json` schema
2. **[PLANNING]** List specific questions to answer: schema_version value, step registration pattern, gate evaluation pattern, hash algorithm used, resume skip logic
3. **[EXECUTION]** Read `executor.py` focusing on `execute_pipeline()` and `execute_roadmap()` — document step model, state save pattern, and resume flow
4. **[EXECUTION]** Read `validate_executor.py` — document ClaudeProcess usage pattern, parallel agent spawning, result collection
5. **[EXECUTION]** Read pipeline and roadmap model files — document GateCriteria, SemanticCheck, Step dataclass shapes
6. **[VERIFICATION]** Confirm schema_version value and additive-extension compatibility
7. **[COMPLETION]** Write review notes to `D-0001/notes.md` with findings organized by topic

**Acceptance Criteria:**
- File `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0001/notes.md` exists with sections for each reviewed component
- Review notes cover all 6 review targets: execute_pipeline, execute_roadmap, validate_executor, gate/state models, resume flow, hash patterns
- Current schema_version value is documented with compatibility assessment
- No unresolved ambiguities about extension points for new steps

**Validation:**
- Manual check: review notes contain concrete findings (not placeholders) for each pipeline component
- Evidence: linkable artifact produced at `D-0001/notes.md`

**Dependencies:** None
**Rollback:** N/A (read-only discovery)
**Notes:** This is a read-only review task. Tier classified EXEMPT because all operations are analysis/exploration with no code modifications.

---

### T01.02 -- Resolve Structural Open Questions (SIGINT, Hash, Step Wiring)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | Three structural decisions must be locked before Phase 2: SIGINT behavior during remediation agents, hash algorithm for source_report_hash, and step wiring design (remediate via ClaudeProcess vs certify via execute_pipeline). |
| Effort | M |
| Risk | Low |
| Risk Drivers | subprocess signal behavior (ClaudeProcess SIGINT handling uncertain) |
| Tier | EXEMPT |
| Confidence | `[███████---]` 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0002/spec.md`

**Deliverables:**
- Structural decisions document covering: (1) SIGINT strategy — whether ClaudeProcess requires signal forwarding or snapshot-based manual recovery suffices, (2) Hash algorithm — SHA-256 confirmed with no conflicts, (3) Step wiring — remediate uses ClaudeProcess directly, certify uses execute_pipeline()

**Steps:**
1. **[PLANNING]** List the three structural questions from roadmap §7 OQ-001, OQ-002, OQ-003
2. **[PLANNING]** Identify evidence needed: ClaudeProcess signal handling behavior, existing hash patterns in pipeline, validate_executor wiring pattern
3. **[EXECUTION]** Investigate ClaudeProcess subprocess cleanup on SIGINT — determine if `.pre-remediate` files suffice for manual recovery
4. **[EXECUTION]** Verify SHA-256 is consistent with existing hash patterns in the pipeline codebase
5. **[EXECUTION]** Confirm step wiring: validate_executor uses ClaudeProcess directly (precedent for remediate); standard steps use execute_pipeline (precedent for certify)
6. **[VERIFICATION]** Cross-check each decision against roadmap §7 resolved answers
7. **[COMPLETION]** Write decisions document to `D-0002/spec.md` with per-question resolution and evidence

**Acceptance Criteria:**
- File `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0002/spec.md` exists with 3 decision sections
- SIGINT strategy is validated against actual ClaudeProcess behavior (not assumed)
- SHA-256 confirmed as hash algorithm with no conflict evidence
- Step wiring design matches validate_executor precedent

**Validation:**
- Manual check: each decision cites evidence from codebase review (T01.01 findings)
- Evidence: linkable artifact produced at `D-0002/spec.md`

**Dependencies:** T01.01
**Rollback:** N/A (decision artifact, no code changes)
**Notes:** Per roadmap §7, these are resolved OQs with expected answers. Task validates the expected answers against codebase evidence. Confidence 72% reflects genuine uncertainty in ClaudeProcess SIGINT/signal-forwarding behavior — subprocess cleanup behavior may differ from documentation. Hash algorithm (OQ-002) and step wiring (OQ-003) have pre-determined answers per roadmap §7; confidence would be higher if ClaudeProcess signal behavior were pre-validated.

---

### T01.03 -- Define Finding Lifecycle Model

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | The canonical finding status lifecycle (PENDING → FIXED / FAILED / SKIPPED) must be defined before the Finding dataclass is implemented in Phase 2. This establishes valid state transitions. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0003/spec.md`

**Deliverables:**
- Finding lifecycle model definition: valid statuses (PENDING, FIXED, FAILED, SKIPPED), valid transitions, terminal states, initial state assignment rules

**Steps:**
1. **[PLANNING]** Extract lifecycle requirements from roadmap Phase 0 key action #4 and spec §2.3.1
2. **[PLANNING]** Identify all status values and which transitions are valid
3. **[EXECUTION]** Define state machine: PENDING (initial) → FIXED (agent success) | FAILED (agent failure/timeout) | SKIPPED (filtered out or NO_ACTION_REQUIRED)
4. **[EXECUTION]** Document terminal states: FIXED, FAILED, SKIPPED are all terminal (no further transitions)
5. **[VERIFICATION]** Verify lifecycle covers all scenarios from roadmap §2.3.2-§2.3.8 (filtering, execution, rollback)
6. **[COMPLETION]** Write lifecycle model to `D-0003/spec.md`

**Acceptance Criteria:**
- File `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0003/spec.md` exists with lifecycle state machine
- All four status values (PENDING, FIXED, FAILED, SKIPPED) are defined with transition rules
- Lifecycle covers filtering (→SKIPPED), success (→FIXED), failure (→FAILED), and rollback (→FAILED) scenarios
- No ambiguous transitions remain

**Validation:**
- Manual check: lifecycle model accounts for every finding outcome described in roadmap §2.3
- Evidence: linkable artifact produced at `D-0003/spec.md`

**Dependencies:** None
**Rollback:** N/A (design artifact)

---

### Checkpoint: End of Phase 1

**Milestone:** M0 — Architecture decisions locked
**Purpose:** Verify all architectural decisions are locked and no structural ambiguity remains before implementation begins.
**Checkpoint Report Path:** `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/CP-P01-END.md`
**Verification:**
- Pipeline foundation review notes (D-0001) cover all 6 review targets with concrete findings
- Structural decisions document (D-0002) resolves SIGINT, hash, and step wiring with codebase evidence
- Finding lifecycle model (D-0003) defines complete state machine with no ambiguous transitions
**Exit Criteria:**
- SIGINT strategy validated against ClaudeProcess behavior
- SHA-256 confirmed as hash algorithm
- No structural ambiguity remains for Phases 2-4
