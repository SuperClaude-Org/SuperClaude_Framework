# Phase 1 -- Foundation & Backward Compat Guard

Establish the structural baseline for the v2.07 release: confirm backward compatibility contract, document the SKILL.md integration plan for both tracks, set up testing scaffolding, and write the `--pipeline` flag detection stub that gates all pipeline mode logic.

---

### T01.01 -- Add `--pipeline` flag detection stub to SKILL.md step_0 guard

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | The `--pipeline` flag must route to the meta-orchestrator section while leaving existing Mode A/B behavior unchanged; this is the foundational gate for all Track A work. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking change (step_0 guard modifies CLI entry point), multi-file (SKILL.md + tests) |
| Tier | STRICT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0001/spec.md
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0001/evidence.md

**Deliverables:**
- `--pipeline` flag detection stub added to SKILL.md before existing mode parsing logic; flag presence routes to meta-orchestrator section, absence routes to existing Mode A/B behavior unchanged

**Steps:**
1. **[PLANNING]** Read current SKILL.md to identify exact location of mode parsing entry point (Mode A/B dispatch)
2. **[PLANNING]** Identify all existing CLI flag handling to ensure `--pipeline` does not conflict with existing flags
3. **[EXECUTION]** Add step_0 guard block before existing mode parsing: if `--pipeline` flag is present, set `pipeline_mode=true` and skip to meta-orchestrator section placeholder
4. **[EXECUTION]** Add meta-orchestrator section placeholder in SKILL.md (empty section with comment "Meta-Orchestrator: implemented in M2/M4")
5. **[EXECUTION]** Verify Mode A invocation without `--pipeline` produces identical output to pre-change baseline
6. **[VERIFICATION]** Run Mode A and Mode B invocations without `--pipeline` flag; confirm zero diff against baseline outputs
7. **[COMPLETION]** Document the step_0 guard logic and flag routing behavior in D-0001/spec.md

**Acceptance Criteria:**
- File `.claude/skills/sc-adversarial-protocol/SKILL.md` contains a step_0 guard that checks for `--pipeline` flag before mode parsing
- Mode A and Mode B invocations without `--pipeline` produce output identical to pre-change baseline (zero regressions)
- `--pipeline` flag presence sets routing variable to meta-orchestrator section without executing Mode A/B logic
- Guard logic documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0001/spec.md`

**Validation:**
- Manual check: invoke `/sc:adversarial` with and without `--pipeline` flag; verify routing behavior matches acceptance criteria
- Evidence: linkable artifact produced (D-0001/spec.md with guard logic documentation)

**Dependencies:** None
**Rollback:** Remove step_0 guard block from SKILL.md; revert to pre-change state
**Notes:** STRICT tier due to multi-file modification of CLI entry point with breaking change potential.

---

### T01.02 -- Document Mode A/B backward compatibility regression baseline

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | A regression baseline with >=5 canonical invocations and expected outputs is required before any SKILL.md modifications begin, to catch regressions in V1 and V2. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0002/spec.md

**Deliverables:**
- Regression baseline document listing >=5 canonical Mode A/B invocation patterns with their expected return contract values

**Steps:**
1. **[PLANNING]** Identify all existing Mode A and Mode B invocation patterns from SKILL.md and existing tests
2. **[PLANNING]** Select >=5 representative invocations covering: Mode A basic, Mode A with flags, Mode B basic, Mode B with flags, edge cases
3. **[EXECUTION]** Execute each invocation and capture the full return contract output
4. **[EXECUTION]** Record each invocation command, input parameters, and expected output in structured table format
5. **[VERIFICATION]** Confirm all 5+ invocations are documented with input/output pairs
6. **[COMPLETION]** Write baseline document to D-0002/spec.md

**Acceptance Criteria:**
- Document at `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0002/spec.md` contains >=5 canonical invocation patterns
- Each invocation includes: command string, input parameters, expected return contract values
- Both Mode A (compare) and Mode B (generate) invocation types are represented
- Document is structured as a table for automated regression comparison

**Validation:**
- Manual check: verify document contains >=5 invocation patterns with complete input/output pairs
- Evidence: linkable artifact produced (D-0002/spec.md)

**Dependencies:** None
**Rollback:** N/A (documentation artifact, non-destructive)
**Notes:** EXEMPT tier -- read-only documentation task with no code modifications.

---

### T01.03 -- Create SKILL.md Track A/B integration sequencing plan

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | Track A (meta-orchestrator) and Track B (protocol quality) both modify SKILL.md; a sequencing plan must enumerate all modification sites and resolve merge conflicts before changes begin. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | cross-cutting scope (system-wide SKILL.md modification plan) |
| Tier | STANDARD |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0003/spec.md

**Deliverables:**
- Integration sequencing plan specifying the order of Track A and Track B SKILL.md modifications with all conflict sites enumerated

**Steps:**
1. **[PLANNING]** Read SKILL.md and identify all sections that Track A (meta-orchestrator) will add or modify
2. **[PLANNING]** Read SKILL.md and identify all sections that Track B (protocol quality) will modify
3. **[EXECUTION]** Map each modification site with section name, line range, and which track owns it
4. **[EXECUTION]** Identify overlapping modification sites and classify conflict risk (none/low/medium/high)
5. **[EXECUTION]** Define sequencing order: which track's modifications apply first at each conflict site
6. **[VERIFICATION]** Verify no blocking conflicts remain: every modification site has a clear owner and sequence
7. **[COMPLETION]** Write sequencing plan to D-0003/spec.md

**Acceptance Criteria:**
- Plan at `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0003/spec.md` lists all SKILL.md modification sites for both tracks
- Each modification site has: section name, approximate line range, owning track, conflict risk level
- Zero blocking conflicts remain at plan completion (all conflicts have resolution strategy)
- Plan specifies merge order for each overlapping section

**Validation:**
- Manual check: verify plan covers all SKILL.md sections modified by M2, M3, M4, and M5 deliverables
- Evidence: linkable artifact produced (D-0003/spec.md)

**Dependencies:** None
**Rollback:** N/A (planning artifact, non-destructive)

---

### T01.04 -- Create test scaffolding stubs for SC-001 through SC-010

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | All 10 success criteria need test case stubs with input/expected-output pairs before implementation begins, enabling test-driven development across M2-M5. |
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
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- .dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0004/spec.md

**Deliverables:**
- Test scaffolding with stubs for SC-001 through SC-010, each containing input specification and expected output assertions

**Steps:**
1. **[PLANNING]** Extract all 10 success criteria (SC-001 through SC-010) from the roadmap with their measurable conditions
2. **[PLANNING]** Identify which milestone each SC validates (SC-001: M2/M4/V2, SC-002: M2, etc.)
3. **[EXECUTION]** Create test stub file for each SC with: test name, input parameters, expected output assertions, skip annotation
4. **[EXECUTION]** Add input/expected-output pairs based on roadmap acceptance criteria descriptions
5. **[EXECUTION]** Annotate each stub with the milestone(s) that will implement the tested behavior
6. **[VERIFICATION]** Verify all 10 SC stubs exist with non-empty input/output specifications
7. **[COMPLETION]** Document test scaffolding structure in D-0004/spec.md

**Acceptance Criteria:**
- Test scaffolding directory contains stubs for all 10 success criteria (SC-001 through SC-010)
- Each stub specifies: test function name, input parameters, expected output/assertion, skip reason referencing implementing milestone
- Stubs are runnable (can be executed with skip annotations) without errors
- Scaffolding structure documented in `.dev/releases/current/2.09-adversarial-v2/tasklist/artifacts/D-0004/spec.md`

**Validation:**
- Manual check: verify 10 test stubs exist with complete input/expected-output pairs
- Evidence: linkable artifact produced (D-0004/spec.md with scaffolding structure)

**Dependencies:** None
**Rollback:** Remove test scaffolding files

---

### Checkpoint: End of Phase 1

**Purpose:** Verify foundation artifacts are complete and backward compatibility baseline is established before Track A/B work begins.
**Checkpoint Report Path:** .dev/releases/current/2.09-adversarial-v2/tasklist/checkpoints/CP-P01-END.md

**Verification:**
- `--pipeline` flag detection stub exists in SKILL.md and routes correctly (T01.01)
- Backward compatibility baseline document contains >=5 canonical invocations (T01.02)
- Integration sequencing plan has zero blocking conflicts (T01.03)

**Exit Criteria:**
- All 4 Phase 1 tasks completed with deliverables D-0001 through D-0004 produced
- Mode A/B invocations without `--pipeline` produce unchanged output
- Test scaffolding for SC-001 through SC-010 is runnable with skip annotations
