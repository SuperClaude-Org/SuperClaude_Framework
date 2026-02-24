# TASKLIST — sc:roadmap Adversarial Pipeline Remediation Sprint

## Metadata & Artifact Paths

- **TASKLIST_ROOT**: `.dev/releases/current/v2.01-Roadmap-v3/`
- **Tasklist Path**: `TASKLIST_ROOT/tasklist/tasklist-P1.md`
- **Execution Log Path**: `TASKLIST_ROOT/tasklist/execution-log.md`
- **Checkpoint Reports Path**: `TASKLIST_ROOT/tasklist/checkpoints/`
- **Evidence Root**: `TASKLIST_ROOT/tasklist/evidence/`
- **Artifacts Root**: `TASKLIST_ROOT/tasklist/artifacts/`
- **Feedback Log Path**: `TASKLIST_ROOT/tasklist/feedback-log.md`

---

## Source Snapshot

- Roadmap restores full adversarial pipeline functionality for `sc:roadmap --multi-roadmap --agents` by addressing 3 root causes: invocation wiring gap (RC1), return contract data flow (RC4), and specification-execution gap (RC2).
- Sprint modifies 4 files across 3 skill packages (`sc-roadmap`, `sc-adversarial`, `roadmap` command).
- 4 work milestones (M1–M4) and 2 validation checkpoints (V1, V2); critical path: M1 → M2 → M3 → V2.
- M3 and M4 execute in parallel after prerequisites, with file-conflict constraint: Task 3.2 before Task 2.4 on `adversarial-integration.md`.
- Pre-implementation gate (Task 0.0) empirically determines whether primary Skill tool invocation path is viable before committing to full sprint plan.
- **Deferred scope**: FR-017 (Sprint 0 Debt Register initialization) is explicitly out of sprint scope; triggers before v2.1 kickoff.

---

## Deterministic Rules Applied

1. **Phase buckets**: Created from roadmap milestone headings (M1, M2, V1, M3, M4, V2) in appearance order, with M4 and M3 swapped to satisfy explicit file-conflict dependency (Task 3.2 before Task 2.4 on adversarial-integration.md). Renumbered sequentially Phase 1–6 with no gaps.
2. **Task IDs**: Zero-padded `T<PP>.<TT>` format (e.g., T01.01). Ordering preserves roadmap appearance within each phase, with dependency-driven reordering where explicit.
3. **Checkpoint cadence**: End-of-phase checkpoint after each phase (6 total). No mid-phase checkpoints needed (no phase exceeds 5 tasks before the end).
4. **Clarification Tasks**: One systemic clarification task (T01.03) created for tier classification ambiguity on executable specification files (.md files that function as code).
5. **Deliverable Registry**: 22 deliverables assigned D-0001 through D-0022 in task order.
6. **Effort mapping**: Computed from text length (≥120 chars), split status, effort keywords, and dependency words per Section 5.2.1.
7. **Risk mapping**: Computed from security, data, auth, performance, and cross-cutting keyword matches per Section 5.2.2.
8. **Tier classification**: Applied `/sc:task-unified` algorithm with compound phrase overrides, keyword matching, and context boosters. `*.md` path booster NOT applied to executable specification files (SKILL.md, roadmap.md, adversarial-integration.md) — these are functionally executable code, not documentation. Per tie-breaker rule 3 (reversibility), this interpretation is noted as a deterministic choice.
9. **Verification routing**: STRICT → Sub-agent (quality-engineer), STANDARD → Direct test execution, LIGHT → Quick sanity check, EXEMPT → Skip.
10. **MCP requirements**: Propagated from tier per Section 5.5.
11. **Traceability matrix**: All 22 roadmap items mapped to tasks, deliverables, tiers, and confidence.
12. **Phase reorder note**: M4 (Return Contract) placed before M3 (Specification Rewrite) to satisfy explicit dependency: M4 Task 3.2 must complete before M3 Task 2.4 (same-file conflict on adversarial-integration.md). Recorded per Section 4.9.

---

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (≤ 20 words) |
|---|---|---|
| R-001 | Phase 1 | Skill Tool Probe result documented (Task 0.0) |
| R-002 | Phase 1 | Prerequisite Validation checklist completed (Task 0.1) |
| R-003 | Phase 1 | Sprint variant decision |
| R-004 | Phase 2 | `Skill` in allowed-tools — roadmap command (Task 1.1) |
| R-005 | Phase 2 | `Skill` in allowed-tools — SKILL.md (Task 1.2) |
| R-006 | Phase 2 | Wave 2 step 3 rewritten as sub-steps 3a-3f (Task 1.3 — merged) |
| R-007 | Phase 2 | Fallback protocol with 3 invocation steps (F1, F2/3, F4/5) |
| R-008 | Phase 2 | Return contract routing in step 3e |
| R-009 | Phase 3 | Verification Test 1: Skill Tool Availability |
| R-010 | Phase 3 | Verification Test 2: Wave 2 Step 3 Structural Audit |
| R-011 | Phase 5 | Verb-to-tool execution vocabulary glossary (Task 2.1) |
| R-012 | Phase 5 | Wave 1A step 2 fixed (Task 2.3) |
| R-013 | Phase 5 | adversarial-integration.md pseudo-CLI converted (Task 2.4) |
| R-014 | Phase 4 | Return Contract write instruction in sc:adversarial SKILL.md (Task 3.1) |
| R-015 | Phase 4 | Dead code removal — subagent_type lines (Task 3.1 appended scope) |
| R-016 | Phase 4 | Return Contract Consumption section in adversarial-integration.md (Task 3.2) |
| R-017 | Phase 4 | Post-Adversarial Artifact Existence Gate (Tier 1) in adversarial-integration.md (Task 3.3) |
| R-018 | Phase 6 | Verification Test 3: Return contract schema consistency |
| R-019 | Phase 6 | Verification Test 3.5: Cross-reference field consistency |
| R-020 | Phase 6 | Verification Test 4: Pseudo-CLI elimination |
| R-021 | Phase 6 | Verification Test 6: Tier 1 quality gate structure audit |
| R-022 | Phase 6 | Sync and quality gates |

---

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | Skill Tool Probe result document | EXEMPT | Skip | `TASKLIST_ROOT/tasklist/artifacts/D-0001/evidence.md` | S | Low |
| D-0002 | T01.01 | R-003 | Sprint variant decision record | EXEMPT | Skip | `TASKLIST_ROOT/tasklist/artifacts/D-0002/notes.md` | S | Low |
| D-0003 | T01.02 | R-002 | Prerequisite Validation checklist | EXEMPT | Skip | `TASKLIST_ROOT/tasklist/artifacts/D-0003/evidence.md` | S | Low |
| D-0004 | T02.01 | R-004 | Skill in allowed-tools (roadmap.md) | LIGHT | Sanity check | `TASKLIST_ROOT/tasklist/artifacts/D-0004/evidence.md` | S | Low |
| D-0005 | T02.02 | R-005 | Skill in allowed-tools (SKILL.md) | LIGHT | Sanity check | `TASKLIST_ROOT/tasklist/artifacts/D-0005/evidence.md` | S | Low |
| D-0006 | T02.03 | R-006 | Wave 2 step 3 sub-steps 3a-3f | STRICT | Sub-agent | `TASKLIST_ROOT/tasklist/artifacts/D-0006/spec.md` | XL | Medium |
| D-0007 | T02.03 | R-007 | Fallback protocol (F1, F2/3, F4/5) | STRICT | Sub-agent | `TASKLIST_ROOT/tasklist/artifacts/D-0007/spec.md` | XL | Medium |
| D-0008 | T02.03 | R-008 | Return contract routing in step 3e | STRICT | Sub-agent | `TASKLIST_ROOT/tasklist/artifacts/D-0008/spec.md` | XL | Medium |
| D-0009 | T03.01 | R-009 | Skill Tool Availability test result | EXEMPT | Skip | `TASKLIST_ROOT/tasklist/artifacts/D-0009/evidence.md` | XS | Low |
| D-0010 | T03.02 | R-010 | Wave 2 Step 3 Structural Audit result | EXEMPT | Skip | `TASKLIST_ROOT/tasklist/artifacts/D-0010/evidence.md` | S | Low |
| D-0011 | T04.01 | R-014 | Return Contract write instruction (9 fields) | STRICT | Sub-agent | `TASKLIST_ROOT/tasklist/artifacts/D-0011/spec.md` | L | Medium |
| D-0012 | T04.01 | R-015 | Dead code removal (subagent_type lines) | STRICT | Sub-agent | `TASKLIST_ROOT/tasklist/artifacts/D-0012/evidence.md` | L | Medium |
| D-0013 | T04.02 | R-016 | Return Contract Consumption section | STRICT | Sub-agent | `TASKLIST_ROOT/tasklist/artifacts/D-0013/spec.md` | M | Medium |
| D-0014 | T04.03 | R-017 | Tier 1 Artifact Existence Gate | STANDARD | Direct test | `TASKLIST_ROOT/tasklist/artifacts/D-0014/spec.md` | S | Low |
| D-0015 | T05.01 | R-011 | Verb-to-tool execution vocabulary glossary | STANDARD | Direct test | `TASKLIST_ROOT/tasklist/artifacts/D-0015/spec.md` | S | Low |
| D-0016 | T05.02 | R-012 | Wave 1A step 2 fix (Skill tool pattern) | STANDARD | Direct test | `TASKLIST_ROOT/tasklist/artifacts/D-0016/spec.md` | S | Low |
| D-0017 | T05.03 | R-013 | Pseudo-CLI conversion to Skill tool format | STANDARD | Direct test | `TASKLIST_ROOT/tasklist/artifacts/D-0017/evidence.md` | S | Low |
| D-0018 | T06.01 | R-018 | Schema consistency test result | EXEMPT | Skip | `TASKLIST_ROOT/tasklist/artifacts/D-0018/evidence.md` | M | Medium |
| D-0019 | T06.02 | R-019 | Cross-reference field consistency result | EXEMPT | Skip | `TASKLIST_ROOT/tasklist/artifacts/D-0019/evidence.md` | S | Low |
| D-0020 | T06.03 | R-020 | Pseudo-CLI elimination test result | EXEMPT | Skip | `TASKLIST_ROOT/tasklist/artifacts/D-0020/evidence.md` | XS | Low |
| D-0021 | T06.04 | R-021 | Tier 1 quality gate audit result | EXEMPT | Skip | `TASKLIST_ROOT/tasklist/artifacts/D-0021/evidence.md` | S | Low |
| D-0022 | T06.05 | R-022 | Sync and quality gates result | STANDARD | Direct test | `TASKLIST_ROOT/tasklist/artifacts/D-0022/evidence.md` | S | Low |

---

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome | Tier Distribution |
|---|---|---:|---|---|
| 1 | Foundation & Prerequisites | T01.01–T01.03 | Skill tool viability confirmed; prerequisites validated | EXEMPT: 3, STRICT: 0, STANDARD: 0, LIGHT: 0 |
| 2 | Invocation Wiring Restoration | T02.01–T02.03 | Skill tool in allowed-tools; Wave 2 step 3 rewritten with invocation + fallback | STRICT: 1, STANDARD: 0, LIGHT: 2, EXEMPT: 0 |
| 3 | Wiring Validation Checkpoint | T03.01–T03.02 | Invocation wiring structurally verified | EXEMPT: 2, STRICT: 0, STANDARD: 0, LIGHT: 0 |
| 4 | Return Contract Transport Mechanism | T04.01–T04.03 | Producer-consumer return contract established with Tier 1 gate | STRICT: 2, STANDARD: 1, LIGHT: 0, EXEMPT: 0 |
| 5 | Specification Rewrite with Executable Instructions | T05.01–T05.03 | Ambiguous specs replaced with executable tool-call instructions | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 6 | Integration Validation & Acceptance | T06.01–T06.05 | End-to-end validation; sync and quality gates pass | EXEMPT: 4, STANDARD: 1, LIGHT: 0, STRICT: 0 |

---

## Phase 1: Foundation & Prerequisites

Validate that the Skill tool can be called cross-skill, confirm all external dependencies are present, and establish whether the primary invocation path or fallback-only variant applies to the remainder of the sprint. This phase is the decision gate for all subsequent work.

### T01.01 — Skill Tool Probe

**Roadmap Item ID(s):** R-001, R-003
**Why:** Empirically determines whether the Skill tool can invoke a second skill while one is running, which decides the sprint's invocation strategy (primary path vs. fallback-only variant).
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None
**Tier:** `EXEMPT`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Skip verification (EXEMPT)
**MCP Requirements:** `Required: None | Preferred: None`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** D-0001, D-0002
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0001/evidence.md`
- `TASKLIST_ROOT/tasklist/artifacts/D-0002/notes.md`

**Deliverables:**
1. Skill Tool Probe result document recording decision gate outcome: primary path viable, "skill already running" block, or "tool not available"
2. Sprint variant decision: if primary path blocked, fallback-only variant applied per roadmap L92–L111 task modification table

**Steps:**
1. **[PLANNING]** Load sprint-spec context; identify the three decision gate outcomes (success, "skill already running", "tool not available")
2. **[PLANNING]** Confirm sc:adversarial is installed and available as a target skill
3. **[EXECUTION]** Dispatch a Task agent with prompt: "Use the Skill tool with `skill: 'sc:adversarial'`. Report the exact result: success, error message, or tool not available."
4. **[EXECUTION]** Test from main agent context: attempt `Skill tool` call to invoke sc:adversarial while sc:roadmap context is active. Record whether "skill already running" constraint applies to same-name, any-skill, or same-instance.
5. **[VERIFICATION]** Document the decision gate result with exact error messages (if any)
6. **[COMPLETION]** If primary path blocked, apply fallback-only sprint variant modifications per roadmap task modification table within 30 minutes

**Acceptance Criteria:**
- Decision gate result recorded with one of three outcomes: primary path viable, "skill already running" block, or "tool not available"
- If primary path non-viable: fallback-only modifications applied and documented
- Probe completed in <15 minutes
- Result traceable to D-0001 and D-0002 artifacts

**Validation:**
- Manual check: Decision gate result recorded with exact outcome
- Evidence: D-0001 artifact produced with probe results; D-0002 artifact produced with sprint variant decision

**Dependencies:** None
**Rollback:** TBD
**Notes:** T04 Opt 4 (conditional deferral) depends on this result: if primary path viable, full G2 fallback validation deferred to follow-up sprint.

---

### T01.02 — Prerequisite Validation

**Roadmap Item ID(s):** R-002
**Why:** Confirms all external dependencies are present and correctly configured before any file edits begin, preventing mid-sprint blockers.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None
**Tier:** `EXEMPT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** `No`
**Critical Path Override:** `No`
**Verification Method:** Skip verification (EXEMPT)
**MCP Requirements:** `Required: None | Preferred: None`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** D-0003
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0003/evidence.md`

**Deliverables:**
1. Prerequisite Validation checklist with all 6 checks documented as pass/fail

**Steps:**
1. **[PLANNING]** Load checklist of 6 prerequisite checks from roadmap
2. **[EXECUTION]** Check 1: Verify `src/superclaude/skills/sc-adversarial/SKILL.md` exists and is readable
3. **[EXECUTION]** Check 2: Verify `src/superclaude/skills/sc-roadmap/SKILL.md` exists and is readable
4. **[EXECUTION]** Check 3: Verify `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` exists
5. **[EXECUTION]** Check 4–5: Verify `make sync-dev` and `make verify-sync` targets are available
6. **[EXECUTION]** Check 6: Confirm Task 0.0 (T01.01) result has been documented
7. **[COMPLETION]** Record all 6 checks with pass/fail in D-0003 artifact

**Acceptance Criteria:**
- All 6 checks documented with pass/fail result; no check left unanswered
- If checks 1–3 fail: fix installation before proceeding
- If checks 4–5 fail: manual sync steps documented as substitute
- Checklist traceable to D-0003 artifact

**Validation:**
- Manual check: All 6 prerequisite checks have documented pass/fail results
- Evidence: D-0003 artifact produced with complete checklist

**Dependencies:** T01.01
**Rollback:** TBD
**Notes:** Blocks all Phase 2+ tasks. If check 6 fails, complete T01.01 first.

---

### T01.03 — Clarify: Tier Classification for Executable Specification Files

**Roadmap Item ID(s):** R-001 (systemic)
**Why:** The `*.md` path booster (+0.5 toward EXEMPT) was designed for documentation files but applies to all .md files by the algorithm. This sprint exclusively modifies executable specification files (.md files that Claude Code interprets as code). Confirming whether EXEMPT booster applies affects verification routing for 9+ tasks.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None
**Tier:** `EXEMPT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** `No`
**Critical Path Override:** `No`
**Verification Method:** Skip verification (EXEMPT)
**MCP Requirements:** `Required: None | Preferred: None`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** (none — decision artifact only)
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/T01.03/notes.md`

**Deliverables:**
1. Confirmed tier classification policy for executable specification files

**Steps:**
1. **[PLANNING]** Identify all tasks that modify .md files functioning as executable specifications
2. **[EXECUTION]** Determine whether `*.md` EXEMPT booster applies to SKILL.md, roadmap.md, adversarial-integration.md
3. **[COMPLETION]** Record decision; update affected task tiers if needed

**Acceptance Criteria:**
- Decision recorded: EXEMPT booster applies or does not apply to executable spec files
- Impacts identified: list of tasks whose tier may change
- Policy documented for reuse in future sprints
- Decision traceable to artifact

**Validation:**
- Manual check: Decision documented with rationale
- Evidence: Notes artifact produced

**Dependencies:** None
**Rollback:** TBD
**Notes:** This tasklist applies the interpretation that `*.md` booster does NOT apply to executable specification files (per tie-breaker rule 3: reversible). All affected task tiers are computed without the booster. If stakeholder confirms booster applies, tiers for T02.01, T02.02, T04.03, T05.01–T05.03 shift toward EXEMPT.

---

### Checkpoint: End of Phase 1

**Purpose:** Confirm foundation and prerequisites are established before proceeding to implementation phases.
**Checkpoint Report Path:** `TASKLIST_ROOT/tasklist/checkpoints/CP-P01-END.md`
**Verification:**
- T01.01 decision gate result is documented with clear outcome
- T01.02 prerequisite checklist shows all 6 checks with pass/fail
- T01.03 tier classification policy is documented

**Exit Criteria:**
- Sprint variant (primary or fallback-only) is determined and sprint plan updated accordingly
- All 3 prerequisite skill files confirmed readable
- `make sync-dev` and `make verify-sync` confirmed available (or manual substitute documented)

---


## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | EXEMPT | 40% | `TASKLIST_ROOT/tasklist/artifacts/D-0001/evidence.md` |
| R-002 | T01.02 | D-0003 | EXEMPT | 80% | `TASKLIST_ROOT/tasklist/artifacts/D-0003/evidence.md` |
| R-003 | T01.01 | D-0002 | EXEMPT | 40% | `TASKLIST_ROOT/tasklist/artifacts/D-0002/notes.md` |
| R-004 | T02.01 | D-0004 | LIGHT | 17% | `TASKLIST_ROOT/tasklist/artifacts/D-0004/evidence.md` |
| R-005 | T02.02 | D-0005 | LIGHT | 17% | `TASKLIST_ROOT/tasklist/artifacts/D-0005/evidence.md` |
| R-006 | T02.03 | D-0006 | STRICT | 34% | `TASKLIST_ROOT/tasklist/artifacts/D-0006/spec.md` |
| R-007 | T02.03 | D-0007 | STRICT | 34% | `TASKLIST_ROOT/tasklist/artifacts/D-0007/spec.md` |
| R-008 | T02.03 | D-0008 | STRICT | 34% | `TASKLIST_ROOT/tasklist/artifacts/D-0008/spec.md` |
| R-009 | T03.01 | D-0009 | EXEMPT | 80% | `TASKLIST_ROOT/tasklist/artifacts/D-0009/evidence.md` |
| R-010 | T03.02 | D-0010 | EXEMPT | 80% | `TASKLIST_ROOT/tasklist/artifacts/D-0010/evidence.md` |
| R-011 | T05.01 | D-0015 | STANDARD | 40% | `TASKLIST_ROOT/tasklist/artifacts/D-0015/spec.md` |
| R-012 | T05.02 | D-0016 | STANDARD | 40% | `TASKLIST_ROOT/tasklist/artifacts/D-0016/spec.md` |
| R-013 | T05.03 | D-0017 | STANDARD | 40% | `TASKLIST_ROOT/tasklist/artifacts/D-0017/evidence.md` |
| R-014 | T04.01 | D-0011 | STRICT | 34% | `TASKLIST_ROOT/tasklist/artifacts/D-0011/spec.md` |
| R-015 | T04.01 | D-0012 | STRICT | 34% | `TASKLIST_ROOT/tasklist/artifacts/D-0012/evidence.md` |
| R-016 | T04.02 | D-0013 | STRICT | 40% | `TASKLIST_ROOT/tasklist/artifacts/D-0013/spec.md` |
| R-017 | T04.03 | D-0014 | STANDARD | 40% | `TASKLIST_ROOT/tasklist/artifacts/D-0014/spec.md` |
| R-018 | T06.01 | D-0018 | EXEMPT | 80% | `TASKLIST_ROOT/tasklist/artifacts/D-0018/evidence.md` |
| R-019 | T06.02 | D-0019 | EXEMPT | 80% | `TASKLIST_ROOT/tasklist/artifacts/D-0019/evidence.md` |
| R-020 | T06.03 | D-0020 | EXEMPT | 80% | `TASKLIST_ROOT/tasklist/artifacts/D-0020/evidence.md` |
| R-021 | T06.04 | D-0021 | EXEMPT | 80% | `TASKLIST_ROOT/tasklist/artifacts/D-0021/evidence.md` |
| R-022 | T06.05 | D-0022 | STANDARD | 60% | `TASKLIST_ROOT/tasklist/artifacts/D-0022/evidence.md` |

---

## Execution Log Template

**Intended Path:** `TASKLIST_ROOT/tasklist/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (≤ 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | T01.01 | EXEMPT | D-0001, D-0002 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T01.01/` |
| | T01.02 | EXEMPT | D-0003 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T01.02/` |
| | T01.03 | EXEMPT | — | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T01.03/` |
| | T02.01 | LIGHT | D-0004 | | `grep -q "Skill" src/superclaude/commands/roadmap.md` | TBD | `TASKLIST_ROOT/tasklist/evidence/T02.01/` |
| | T02.02 | LIGHT | D-0005 | | `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md` | TBD | `TASKLIST_ROOT/tasklist/evidence/T02.02/` |
| | T02.03 | STRICT | D-0006, D-0007, D-0008 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T02.03/` |
| | T03.01 | EXEMPT | D-0009 | | `grep -q "Skill" (both files)` | TBD | `TASKLIST_ROOT/tasklist/evidence/T03.01/` |
| | T03.02 | EXEMPT | D-0010 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T03.02/` |
| | T04.01 | STRICT | D-0011, D-0012 | | `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` | TBD | `TASKLIST_ROOT/tasklist/evidence/T04.01/` |
| | T04.02 | STRICT | D-0013 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T04.02/` |
| | T04.03 | STANDARD | D-0014 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T04.03/` |
| | T05.01 | STANDARD | D-0015 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T05.01/` |
| | T05.02 | STANDARD | D-0016 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T05.02/` |
| | T05.03 | STANDARD | D-0017 | | `grep -c "sc:adversarial --" adversarial-integration.md` | TBD | `TASKLIST_ROOT/tasklist/evidence/T05.03/` |
| | T06.01 | EXEMPT | D-0018 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T06.01/` |
| | T06.02 | EXEMPT | D-0019 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T06.02/` |
| | T06.03 | EXEMPT | D-0020 | | `grep -c "sc:adversarial --" adversarial-integration.md` | TBD | `TASKLIST_ROOT/tasklist/evidence/T06.03/` |
| | T06.04 | EXEMPT | D-0021 | | Manual | TBD | `TASKLIST_ROOT/tasklist/evidence/T06.04/` |
| | T06.05 | STANDARD | D-0022 | | `make sync-dev && make verify-sync && uv run pytest && make lint` | TBD | `TASKLIST_ROOT/tasklist/evidence/T06.05/` |

---

## Checkpoint Report Template

For each checkpoint created under Section 4.8, execution must produce one report using this template (do not fabricate contents).

**Template:**

```markdown
# Checkpoint Report — <Checkpoint Title>

**Checkpoint Report Path:** TASKLIST_ROOT/tasklist/checkpoints/<deterministic-name>.md
**Scope:** <tasks covered>

## Status
- Overall: Pass | Fail | TBD

## Verification Results
- <aligned to checkpoint Verification bullet 1>
- <aligned to checkpoint Verification bullet 2>
- <aligned to checkpoint Verification bullet 3>

## Exit Criteria Assessment
- <aligned to checkpoint Exit Criteria bullet 1>
- <aligned to checkpoint Exit Criteria bullet 2>
- <aligned to checkpoint Exit Criteria bullet 3>

## Issues & Follow-ups
- <List blocking issues; reference T<PP>.<TT> and D-####>

## Evidence
- <Bullet list of evidence paths under TASKLIST_ROOT/tasklist/evidence/>
```

**Checkpoint Report Paths:**
- `TASKLIST_ROOT/tasklist/checkpoints/CP-P01-END.md`
- `TASKLIST_ROOT/tasklist/checkpoints/CP-P02-END.md`
- `TASKLIST_ROOT/tasklist/checkpoints/CP-P03-END.md`
- `TASKLIST_ROOT/tasklist/checkpoints/CP-P04-END.md`
- `TASKLIST_ROOT/tasklist/checkpoints/CP-P05-END.md`
- `TASKLIST_ROOT/tasklist/checkpoints/CP-P06-END.md`

---

## Feedback Collection Template

Track tier classification accuracy and execution quality for calibration learning.

**Intended Path:** `TASKLIST_ROOT/tasklist/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (≤ 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| T01.01 | EXEMPT | | | | | |
| T01.02 | EXEMPT | | | | | |
| T01.03 | EXEMPT | | | | | |
| T02.01 | LIGHT | | | | | |
| T02.02 | LIGHT | | | | | |
| T02.03 | STRICT | | | | | |
| T03.01 | EXEMPT | | | | | |
| T03.02 | EXEMPT | | | | | |
| T04.01 | STRICT | | | | | |
| T04.02 | STRICT | | | | | |
| T04.03 | STANDARD | | | | | |
| T05.01 | STANDARD | | | | | |
| T05.02 | STANDARD | | | | | |
| T05.03 | STANDARD | | | | | |
| T06.01 | EXEMPT | | | | | |
| T06.02 | EXEMPT | | | | | |
| T06.03 | EXEMPT | | | | | |
| T06.04 | EXEMPT | | | | | |
| T06.05 | STANDARD | | | | | |

**Field definitions:**
- `Override Tier`: Leave blank if no override; else the user-selected tier
- `Override Reason`: Brief justification (e.g., "Involved auth paths", "Actually trivial")
- `Completion Status`: `clean | minor-issues | major-issues | failed`
- `Quality Signal`: `pass | partial | rework-needed`
- `Time Variance`: `under-estimate | on-target | over-estimate`

---

## Glossary

| Term | Definition (from roadmap) |
|---|---|
| Skill tool | Claude Code tool that invokes a named skill (e.g., `skill: "sc:adversarial"`) |
| Return contract | File-based YAML transport mechanism (`return-contract.yaml`) enabling structured result passing between skills |
| Fallback protocol | 3-step inline execution (F1, F2/3, F4/5) activated when Skill tool invocation fails |
| Execution vocabulary | Verb-to-tool glossary mapping specification verbs to concrete tool calls |
| Pseudo-CLI syntax | Standalone `sc:adversarial --flag` invocation format that is not executable by Claude Code |
| Convergence score | 0.0–1.0 metric in return contract indicating adversarial pipeline convergence quality |
| Tier 1 gate | Artifact existence quality gate checking 4 files before YAML parsing |
| Primary path | Direct Skill tool invocation of sc:adversarial (preferred if Task 0.0 probe succeeds) |
| Fallback-only variant | Sprint adaptation when primary Skill tool path is blocked; fallback becomes sole invocation mechanism |
