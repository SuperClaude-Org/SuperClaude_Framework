# TASKLIST — sc:roadmap Adversarial Pipeline Remediation

## Phase 1: Pre-Implementation Gates and Probing

**Phase Goal**: Empirically determine Skill tool viability before writing a single line of implementation code. This phase treats the runtime environment as an unknown — every assumption about cross-skill invocation, constraint semantics, and dependency availability is treated as a hypothesis to be proven or disproven. The outputs of Phase 1 are not artifacts but decisions: does the primary path (Skill-to-Skill invocation) work, and are the six prerequisites satisfied? These decisions gate everything in Phase 2 and beyond. No implementation begins until all four tasks complete and the end-of-phase checkpoint passes.

---

### T01.01 — Skill Tool Cross-Skill Invocation Probe

**Roadmap Item IDs**: R-002, R-003

**Why**: The entire primary implementation path depends on whether a skill can successfully invoke another skill via the `Skill` tool from inside a running skill context. This has never been empirically verified in the current environment. If cross-skill invocation is blocked, the Wave 2 Step 3 rewrite (T02.02) must use the fallback-only variant. This probe produces the binary gate decision that routes the sprint.

**Effort**: S
**Risk**: Medium
**Risk Drivers**: Cross-cutting scope — the probe exercises runtime behavior that affects the entire pipeline design; an inconclusive result requires manual follow-up before the sprint can proceed.

**Tier**: EXEMPT
**Confidence**: [=========-] 85%
**Requires Confirmation**: No
**Critical Path Override**: No
**Verification Method**: Skip (EXEMPT — read-only probe, no code changes)
**MCP Requirements**: Sequential (structured probe design and result analysis)
**Fallback Allowed**: Yes — if Task agent dispatch is unavailable, run manual test by inspecting Skill tool documentation and known constraint patterns
**Sub-Agent Delegation**: Required — dispatch a Task agent with a focused prompt to exercise the Skill tool and report observable behavior

**Deliverable IDs**: D-0001
**Artifacts**: `probe-results.md` written to `.dev/releases/current/v2.02-Roadmap-v3/` documenting exact invocation attempt, observed output, and constraint determination
**Deliverables**: Binary decision: PRIMARY_PATH_VIABLE or FALLBACK_ONLY, documented with evidence

**Steps**:
1. [PREPARE] Draft Task agent prompt: "Using the Skill tool, attempt to invoke skill `sc:adversarial` from within a neutral context. Record: (a) whether invocation succeeds, (b) any error message verbatim, (c) whether the constraint `skill already running` fires, (d) what triggers that constraint — same skill name, any skill, or same instance."
2. [EXECUTE] Dispatch the Task agent with the drafted prompt and capture the complete response.
3. [ANALYZE] Parse the Task agent response against three outcome categories: full success (cross-skill invocation works), partial success (invocation works with restrictions), or blocked (invocation fails with constraint or error).
4. [DOCUMENT] Write `probe-results.md` with verbatim Task agent output, outcome category, and the binary decision value.
5. [GATE] If outcome is BLOCKED, flag sprint for variant selection in T01.04. If outcome is full or partial success, proceed to T01.02.

**Acceptance Criteria**:
1. Task agent was dispatched with a prompt that explicitly exercises the Skill tool in a cross-skill invocation context.
2. The probe result is documented in `probe-results.md` with verbatim output — no paraphrasing of error messages.
3. A single binary decision value (PRIMARY_PATH_VIABLE or FALLBACK_ONLY) is recorded and unambiguous.
4. The probe result is referenced in T01.04's decision gate input.

**Validation**:
1. `probe-results.md` exists in the target directory and contains the binary decision value on a clearly labeled line.
2. The Task agent output captured in `probe-results.md` is sufficient to reconstruct the reasoning without re-running the probe.

**Dependencies**: None — this is the first task in the sprint.
**Rollback**: No code was changed; delete `probe-results.md` if the probe must be re-run from scratch.
**Notes**: If the Task tool itself is unavailable, attempt to infer Skill tool behavior from existing documentation in `src/superclaude/skills/` and record the inference with a confidence qualifier in `probe-results.md`. An inferred result must be flagged as UNVERIFIED and must trigger a manual confirmation step before T01.04 proceeds.

---

### T01.02 — Determine "Skill Already Running" Constraint Semantics

**Roadmap Item IDs**: R-002, R-004

**Why**: The phrase "skill already running" appears in known Skill tool behavior but its precise scope is undefined. It may mean: the same skill name cannot be invoked twice, any skill invocation is blocked while one is active, or the same skill instance cannot be re-entered. The distinction changes how the fallback protocol in T02.02 must be structured. This task resolves that ambiguity before any implementation prose is written.

**Effort**: XS
**Risk**: Low
**Risk Drivers**: Finding is informational; worst case is ambiguity persists and T02.02 must document the uncertainty explicitly.

**Tier**: EXEMPT
**Confidence**: [=========] 90%
**Requires Confirmation**: No
**Critical Path Override**: No
**Verification Method**: Skip (EXEMPT — investigation only, no code changes)
**MCP Requirements**: Sequential (structured semantic analysis of constraint behavior)
**Fallback Allowed**: Yes — if direct observation is unavailable, analyze Skill tool source documentation and existing skill invocation patterns
**Sub-Agent Delegation**: Optional — may be performed inline or delegated to a Task agent if T01.01 agent output was inconclusive on this specific question

**Deliverable IDs**: D-0002
**Artifacts**: Constraint semantics finding appended to `probe-results.md` as a labeled section
**Deliverables**: One of three semantic labels: SAME_NAME_BLOCKED, ANY_SKILL_BLOCKED, or SAME_INSTANCE_BLOCKED — with supporting evidence

**Steps**:
1. [REVIEW] Re-read T01.01 Task agent output for any constraint error messages or behavioral clues about scope.
2. [INVESTIGATE] If T01.01 output is inconclusive on constraint semantics, review `src/superclaude/skills/` documentation and any existing skill invocation examples for constraint references.
3. [CLASSIFY] Assign one of three semantic labels based on evidence: SAME_NAME_BLOCKED (only the same-named skill is blocked), ANY_SKILL_BLOCKED (any concurrent skill invocation is blocked), SAME_INSTANCE_BLOCKED (only re-entrant calls to the same running instance are blocked).
4. [DOCUMENT] Append constraint semantics finding to `probe-results.md` under heading `## Constraint Semantics`.

**Acceptance Criteria**:
1. One of the three semantic labels is assigned and documented with at least one piece of supporting evidence.
2. The finding is appended to `probe-results.md` in a clearly labeled section — not a separate file.
3. The semantic label directly informs the fallback protocol design in T02.02 (the connection is noted explicitly).
4. If the finding is AMBIGUOUS, that is recorded as a label with a note that T02.02 must document both interpretations in the fallback prose.

**Validation**:
1. `probe-results.md` contains a `## Constraint Semantics` section with a labeled finding after T01.02 completes.
2. The finding is traceable to at least one source: Task agent output, skill documentation, or existing invocation pattern.

**Dependencies**: T01.01 (probe-results.md must exist before this task runs).
**Rollback**: No code changed; finding can be revised by re-running investigation and updating the relevant section of `probe-results.md`.
**Notes**: If T01.01 returned FALLBACK_ONLY, this task still runs — the constraint semantics determine whether the fallback protocol needs to handle re-entrant blocking or only cross-skill blocking, which affects fallback step wording in T02.02.

---

### T01.03 — Prerequisite Validation: 6 Dependency Checks

**Roadmap Item IDs**: R-002, R-005

**Why**: Phase 2 implementation tasks assume six dependencies are present and functional. Discovering a missing dependency mid-implementation causes a blocked sprint with incomplete file edits. This task front-loads all six checks so Phase 2 begins from a verified baseline.

**Effort**: S
**Risk**: Low
**Risk Drivers**: Any failed check blocks Phase 2 and requires remediation steps that are outside this sprint's scope; failure mode is a clean stop, not data corruption.

**Tier**: EXEMPT
**Confidence**: [=========-] 85%
**Requires Confirmation**: No
**Critical Path Override**: No
**Verification Method**: Skip (EXEMPT — validation checks only, no code changes)
**MCP Requirements**: None required; Bash tool sufficient for all six checks
**Fallback Allowed**: No — all six checks must pass or the sprint must pause for remediation
**Sub-Agent Delegation**: No — checks are fast and sequential

**Deliverable IDs**: D-0003
**Artifacts**: `prereq-validation.md` written to `.dev/releases/current/v2.02-Roadmap-v3/` with pass/fail result for each of the six checks
**Deliverables**: PREREQS_PASS or PREREQS_FAIL with itemized check results

**Steps**:
1. [CHECK-1] Verify `sc:adversarial` skill is installed: confirm `src/superclaude/skills/sc-adversarial/SKILL.md` exists and is non-empty.
2. [CHECK-2] Verify `sc:roadmap` skill is installed: confirm `src/superclaude/skills/sc-roadmap/SKILL.md` exists and is non-empty.
3. [CHECK-3] Verify `adversarial-integration.md` is present: locate the file in the repository and confirm it is reachable from the roadmap skill context.
4. [CHECK-4] Verify `make sync-dev` is available: confirm `Makefile` contains a `sync-dev` target.
5. [CHECK-5] Verify `make verify-sync` is available: confirm `Makefile` contains a `verify-sync` target.
6. [CHECK-6] Verify T01.01 is documented: confirm `probe-results.md` exists and contains a binary decision value on a labeled line.
7. [DOCUMENT] Write `prereq-validation.md` with each check labeled CHECK-1 through CHECK-6, its result (PASS or FAIL), and the evidence command or path used.
8. [GATE] If any check returns FAIL, set overall result to PREREQS_FAIL and halt Phase 2 pending remediation.

**Acceptance Criteria**:
1. All six checks are run and individually documented — no check is skipped or assumed to pass without verification.
2. Each check result in `prereq-validation.md` includes the exact path, command output, or evidence that produced the PASS or FAIL verdict.
3. The overall result (PREREQS_PASS or PREREQS_FAIL) is on the first non-header line of `prereq-validation.md`.
4. A PREREQS_FAIL result includes a remediation note for each failing check identifying who or what must resolve it before Phase 2 can begin.

**Validation**:
1. `prereq-validation.md` exists and contains exactly six labeled check results with an overall verdict.
2. Every PASS result is traceable to a file path or command output — no result is asserted without evidence.

**Dependencies**: T01.01 (CHECK-6 depends on probe-results.md).
**Rollback**: No code changed; re-run checks after remediation and overwrite `prereq-validation.md`.
**Notes**: CHECK-3 (adversarial-integration.md) may require searching beyond the immediate skill directory if the file is stored in a docs or integration subdirectory. Use Glob to locate it rather than assuming a fixed path.

---

### T01.04 — Sprint Variant Decision Gate

**Roadmap Item IDs**: R-002, R-006

**Why**: The sprint has two implementation variants: primary (Skill-to-Skill invocation using the `Skill` tool) and fallback-only (direct prose instructions without Skill tool dependency). The correct variant cannot be selected without T01.01 and T01.03 results. This task synthesizes those results into a single documented decision that Phase 2 will execute against. Skipping this gate would allow Phase 2 to begin against an unresolved ambiguity.

**Effort**: XS
**Risk**: Medium
**Risk Drivers**: Cross-cutting scope — the decision made here propagates to T02.02 design, fallback protocol wording, and sub-step structure; an incorrect decision requires revisiting T02.02 in full.

**Tier**: EXEMPT
**Confidence**: [========] 80%
**Requires Confirmation**: Yes — the selected variant must be acknowledged before Phase 2 begins
**Critical Path Override**: No
**Verification Method**: Skip (EXEMPT — planning decision, no code changes)
**MCP Requirements**: Sequential (decision synthesis across multiple probe outputs)
**Fallback Allowed**: No — a variant must be selected; ambiguity is not a valid output
**Sub-Agent Delegation**: No — decision synthesis is a single-agent reasoning task

**Deliverable IDs**: D-0004
**Artifacts**: `sprint-variant.md` written to `.dev/releases/current/v2.02-Roadmap-v3/` with decision, rationale, and Phase 2 routing instructions
**Deliverables**: One of two variant labels: PRIMARY_VARIANT or FALLBACK_VARIANT, with routing instructions for T02.02

**Steps**:
1. [INPUT] Read `probe-results.md` binary decision value (PRIMARY_PATH_VIABLE or FALLBACK_ONLY) and constraint semantics label.
2. [INPUT] Read `prereq-validation.md` overall result (PREREQS_PASS or PREREQS_FAIL).
3. [DECIDE] Apply decision logic: if probe result is PRIMARY_PATH_VIABLE AND prereqs result is PREREQS_PASS, select PRIMARY_VARIANT. If either is negative, select FALLBACK_VARIANT.
4. [DOCUMENT] Write `sprint-variant.md` with: selected variant, decision inputs (verbatim values from probe-results.md and prereq-validation.md), rationale, and specific routing instructions for T02.02 (which sub-steps to implement, which fallback levels to activate).
5. [CONFIRM] Present `sprint-variant.md` to the user for acknowledgment before Phase 2 begins.

**Acceptance Criteria**:
1. The selected variant is one of PRIMARY_VARIANT or FALLBACK_VARIANT — no conditional or deferred decisions are recorded.
2. The decision inputs are cited verbatim from `probe-results.md` and `prereq-validation.md` — no re-interpretation.
3. `sprint-variant.md` contains explicit routing instructions that T02.02 can follow without re-reading Phase 1 artifacts.
4. The user has acknowledged the variant selection before any Phase 2 task begins.

**Validation**:
1. `sprint-variant.md` exists and contains a single variant label on a clearly marked line followed by routing instructions.
2. The routing instructions reference specific sub-step IDs (3a-3f) and fallback levels (F1, F2/3, F4/5) by name.

**Dependencies**: T01.01 (probe-results.md), T01.02 (constraint semantics in probe-results.md), T01.03 (prereq-validation.md).
**Rollback**: If the selected variant is later found incorrect, re-run T01.01 with a more targeted probe and regenerate this decision; do not amend Phase 2 tasks mid-execution.
**Notes**: If the user does not acknowledge within the session, Phase 2 must not begin. The confirmation requirement is a hard gate, not a soft recommendation.

---

## Phase 1 End-of-Phase Checkpoint

**Checkpoint ID**: CP-P1
**Cumulative Task Count**: 4

**Gate Conditions — all must be true before Phase 2 begins**:

| # | Condition | Evidence Required |
|---|-----------|------------------|
| 1 | T01.01 complete | `probe-results.md` exists with binary decision value |
| 2 | T01.02 complete | `probe-results.md` contains `## Constraint Semantics` section with labeled finding |
| 3 | T01.03 complete | `prereq-validation.md` exists with six check results and overall verdict |
| 4 | T01.04 complete | `sprint-variant.md` exists with variant label and routing instructions |
| 5 | User acknowledgment | T01.04 confirmation received in session |
| 6 | No PREREQS_FAIL unresolved | If PREREQS_FAIL was recorded, remediation must be documented before proceeding |

**On Checkpoint Pass**: Proceed to Phase 2. Provide `sprint-variant.md` routing instructions as the first input to T02.01.

**On Checkpoint Fail**: Do not begin Phase 2. Document which gate condition failed and the remediation action required.
