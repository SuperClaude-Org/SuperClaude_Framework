# TASKLIST — sc:roadmap Adversarial Pipeline Remediation Sprint

## Metadata & Artifact Paths

- **TASKLIST_ROOT**: `.dev/releases/current/v2.01-Roadmap-v3/`
- **Tasklist Path**: `TASKLIST_ROOT/tasklist/tasklist.md`
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

## Phase 2: Invocation Wiring Restoration

Enable skill-to-skill invocation by adding the Skill tool to allowed-tools and implementing the complete Wave 2 step 3 rewrite with atomic sub-steps, Skill tool call syntax, and structured fallback protocol. This is the critical path milestone — all downstream phases depend on it.

### T02.01 — Add Skill to allowed-tools in Roadmap Command

**Roadmap Item ID(s):** R-004
**Why:** Without `Skill` in the allowed-tools list, the roadmap command cannot invoke any skill, making the entire adversarial pipeline non-functional.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None
**Tier:** `LIGHT`
**Confidence:** `[██--------] 17%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Quick sanity check (~100 tokens, 10s)
**MCP Requirements:** `Required: None | Preferred: None`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** D-0004
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0004/evidence.md`

**Deliverables:**
1. `Skill` appended to the `allowed-tools` line in `src/superclaude/commands/roadmap.md`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/commands/roadmap.md` and locate the `allowed-tools` frontmatter line
2. **[PLANNING]** Confirm `Skill` is not already present in the list
3. **[EXECUTION]** Append `Skill` to the existing tool list, preserving all existing tools
4. **[VERIFICATION]** Run: `grep -q "Skill" src/superclaude/commands/roadmap.md && echo "PASS" || echo "FAIL"` — expect PASS
5. **[COMPLETION]** Record grep result in D-0004 artifact

**Acceptance Criteria:**
- `Skill` appears in the `allowed-tools` line of `src/superclaude/commands/roadmap.md`
- All pre-existing tools in the list are unchanged
- Grep verification returns PASS
- Change traceable to D-0004 artifact

**Validation:**
- `grep -q "Skill" src/superclaude/commands/roadmap.md && echo "PASS" || echo "FAIL"` returns PASS
- Evidence: D-0004 artifact with grep output

**Dependencies:** T01.02
**Rollback:** TBD
**Notes:** Tier conflict: LIGHT (0.1 from single-file booster) vs STANDARD (0.2 from "add" keyword) → resolved to LIGHT by priority rule (LIGHT rank 3 > STANDARD rank 4). Confidence low due to keyword sparsity.

---

### T02.02 — Add Skill to allowed-tools in sc-roadmap SKILL.md

**Roadmap Item ID(s):** R-005
**Why:** The SKILL.md file's allowed-tools list controls what tools the skill can use during execution. `Skill` must be present for cross-skill invocation to function.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None
**Tier:** `LIGHT`
**Confidence:** `[██--------] 17%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Quick sanity check (~100 tokens, 10s)
**MCP Requirements:** `Required: None | Preferred: None`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** D-0005
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0005/evidence.md`

**Deliverables:**
1. `Skill` appended to the `allowed-tools` line in `src/superclaude/skills/sc-roadmap/SKILL.md`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/skills/sc-roadmap/SKILL.md` and locate the `allowed-tools` frontmatter line
2. **[PLANNING]** Confirm `Skill` is not already present in the list
3. **[EXECUTION]** Append `Skill` to the existing tool list, preserving all existing tools
4. **[VERIFICATION]** Run: `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md && echo "PASS" || echo "FAIL"` — expect PASS
5. **[COMPLETION]** Record grep result in D-0005 artifact

**Acceptance Criteria:**
- `Skill` appears in the `allowed-tools` line of `src/superclaude/skills/sc-roadmap/SKILL.md`
- All pre-existing tools in the list are unchanged
- Grep verification returns PASS
- Change traceable to D-0005 artifact

**Validation:**
- `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md && echo "PASS" || echo "FAIL"` returns PASS
- Evidence: D-0005 artifact with grep output

**Dependencies:** T01.02
**Rollback:** TBD
**Notes:** Same tier conflict resolution as T02.01.

---

### T02.03 — Rewrite Wave 2 Step 3: Skill Invocation + Fallback + Return Contract Routing

**Roadmap Item ID(s):** R-006, R-007, R-008
**Why:** Wave 2 step 3 currently contains a single compressed "Invoke sc:adversarial" instruction with no tool-call syntax, no fallback, and no return contract handling. This merged task (from original Tasks 1.3+1.4+2.2 per T04 Opt 1) rewrites step 3 as a single atomic edit with 6 sub-steps, Skill tool call syntax, structured fallback, and YAML return contract routing.
**Effort:** `XL`
**Risk:** `Medium`
**Risk Drivers:** data (schema)
**Tier:** `STRICT`
**Confidence:** `[███-------] 34%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Sub-agent (quality-engineer), 3-5K tokens, 60s
**MCP Requirements:** `Required: Sequential, Serena | Preferred: Context7`
**Fallback Allowed:** `No`
**Sub-Agent Delegation:** `Recommended`
**Deliverable IDs:** D-0006, D-0007, D-0008
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0006/spec.md`
- `TASKLIST_ROOT/tasklist/artifacts/D-0007/spec.md`
- `TASKLIST_ROOT/tasklist/artifacts/D-0008/spec.md`

**Deliverables:**
1. Wave 2 step 3 decomposed into sub-steps 3a–3f: (3a) parse agents, (3b) expand variants, (3c) debate-orchestrator for ≥3 agents, (3d) Skill tool call OR fallback, (3e) consume return-contract.yaml with status routing, (3f) skip template if adversarial succeeded
2. Fallback protocol covering 3 error types with 3 invocation steps (F1, F2/3, F4/5), each with defined input/output/failure action, minimum quality threshold (≥100 words for analysis artifacts), and `fallback_mode: true` in return contract
3. Return contract routing in step 3e with missing-file guard, three-status routing (success/partial/failed), convergence threshold 0.6, YAML parse error handling, and canonical schema comment

**Steps:**
1. **[PLANNING]** Read current Wave 2 step 3 in `src/superclaude/skills/sc-roadmap/SKILL.md`; identify exact replacement boundaries
2. **[PLANNING]** Check T01.01 result to determine primary path (Skill tool call) vs fallback-only variant
3. **[EXECUTION]** Write sub-steps 3a–3c: parse `--agents` list, expand into variant parameters, add debate-orchestrator if agents ≥ 3
4. **[EXECUTION]** Write sub-step 3d: Skill tool call with `skill: "sc:adversarial"` and arguments; fallback trigger on 3 error types (tool not in allowed-tools, skill not found, skill already running); WARNING emission before fallback; F1 variant generation, F2/3 diff analysis + single-round debate (merged), F4/5 base selection + merge + contract (merged)
5. **[EXECUTION]** Write sub-step 3e: consume return-contract.yaml with missing-file guard, three-status routing, convergence threshold 0.6, YAML parse error → `status: failed`
6. **[EXECUTION]** Write sub-step 3f: skip template-based generation if adversarial succeeded/partial
7. **[VERIFICATION]** Verify: 6 sub-steps present, each uses exactly one glossary verb, Skill call syntax present, 3 fallback error types covered, missing-file guard present, convergence threshold 0.6 present, skip-template instruction present
8. **[COMPLETION]** Document sub-step structure and fallback state machine in D-0006, D-0007, D-0008 artifacts

**Acceptance Criteria:**
- 6 sub-steps (3a–3f) present in Wave 2 step 3, each using exactly one verb from the execution vocabulary glossary
- Fallback protocol covers 3 error types; F1 produces ≥2 variant files; F2/3 produces diff-analysis.md with labeled sections; F4/5 produces base-selection.md + merged-output.md + return-contract.yaml with `fallback_mode: true`
- Step 3e contains missing-file guard, three-status routing, convergence threshold 0.6, and YAML parse error handling
- Convergence score in fallback return contract is fixed sentinel 0.5 with YAML comment "# estimated, not measured"

**Validation:**
- Manual check: 7-point structural audit checklist (per Verification Test 2) passes
- Evidence: D-0006, D-0007, D-0008 artifacts with sub-step and fallback documentation

**Dependencies:** T02.01, T02.02, T01.01
**Rollback:** TBD
**Notes:** Merged from Tasks 1.3+1.4+2.2 per T04 Opt 1. Risk R-014 (scope creep) mitigated by single atomic edit with clear sub-step boundaries. If T01.01 returns "primary path blocked," step 3d's Skill tool call is removed and fallback becomes the primary mechanism. Tier conflict: STRICT (0.4 from "schema") vs STANDARD (0.4 from "modify"+"create") → resolved to STRICT by priority rule.

---

### Checkpoint: End of Phase 2

**Purpose:** Confirm invocation wiring is complete before validation and downstream implementation.
**Checkpoint Report Path:** `TASKLIST_ROOT/tasklist/checkpoints/CP-P02-END.md`
**Verification:**
- `Skill` present in allowed-tools of both `roadmap.md` and `SKILL.md` (T02.01, T02.02 grep results)
- Wave 2 step 3 contains 6 sub-steps (3a–3f) with Skill tool call syntax and fallback protocol
- Return contract routing in step 3e is structurally complete

**Exit Criteria:**
- Both grep verification tests return PASS
- All three deliverables (D-0006, D-0007, D-0008) are documented
- Sprint variant (from T01.01) has been applied if needed

---

## Phase 3: Wiring Validation Checkpoint

Validate that the invocation wiring (Phase 1 + Phase 2) is structurally correct before proceeding to return contract implementation and specification rewrite. All checks are read-only static analysis.

### T03.01 — Skill Tool Availability Verification

**Roadmap Item ID(s):** R-009
**Why:** Confirms the Skill tool is present in allowed-tools for both files, providing a structural gate before downstream work.
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
**Deliverable IDs:** D-0009
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0009/evidence.md`

**Deliverables:**
1. Verification Test 1 result: both grep commands return PASS for `roadmap.md` and `SKILL.md`

**Steps:**
1. **[PLANNING]** Identify both target files for grep verification
2. **[EXECUTION]** Run: `grep -q "Skill" src/superclaude/commands/roadmap.md && echo "PASS" || echo "FAIL"`
3. **[EXECUTION]** Run: `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md && echo "PASS" || echo "FAIL"`
4. **[COMPLETION]** Record both results in D-0009 artifact

**Acceptance Criteria:**
- Both grep commands return PASS
- Results are documented with exact command output
- No false positives (Skill appears specifically in allowed-tools context)
- Evidence traceable to D-0009

**Validation:**
- Manual check: Both grep commands return PASS
- Evidence: D-0009 artifact with command outputs

**Dependencies:** T02.01, T02.02
**Rollback:** TBD

---

### T03.02 — Wave 2 Step 3 Structural Audit

**Roadmap Item ID(s):** R-010
**Why:** Validates the step 3 rewrite meets the specification before downstream phases build on top of it.
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
**Deliverable IDs:** D-0010
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0010/evidence.md`

**Deliverables:**
1. 7-point manual checklist result for Verification Test 2

**Steps:**
1. **[PLANNING]** Load the 7-point checklist from Verification Test 2 specification
2. **[EXECUTION]** Check 1: Count sub-steps in Wave 2 step 3 — expect 6 (3a through 3f)
3. **[EXECUTION]** Check 2–3: Verify each sub-step uses exactly one glossary verb; verify step 3d contains Skill tool call syntax
4. **[EXECUTION]** Check 4–7: Verify fallback covers 3 error types; step 3e missing-file guard present; convergence threshold 0.6 present; step 3f skip-template instruction present
5. **[COMPLETION]** Record all 7 checklist items with pass/fail in D-0010 artifact

**Acceptance Criteria:**
- All 7 checklist items pass
- Each check documented with specific evidence (line references or text excerpts)
- Audit is read-only (no file modifications)
- Evidence traceable to D-0010

**Validation:**
- Manual check: 7-point checklist fully completed with all items passing
- Evidence: D-0010 artifact with audit results

**Dependencies:** T02.03
**Rollback:** TBD

---

### Checkpoint: End of Phase 3

**Purpose:** Confirm invocation wiring is structurally validated before return contract implementation.
**Checkpoint Report Path:** `TASKLIST_ROOT/tasklist/checkpoints/CP-P03-END.md`
**Verification:**
- Verification Test 1 (T03.01) returns PASS for both files
- Verification Test 2 (T03.02) 7-point checklist fully passes
- No structural issues found in Wave 2 step 3

**Exit Criteria:**
- Both verification tests pass without issues
- No blockers identified for Phase 4 or Phase 5
- Phase 2 work confirmed ready for downstream consumption

---

## Phase 4: Return Contract Transport Mechanism

Establish the file-based return-contract.yaml convention enabling sc:adversarial to transport structured pipeline results back to sc:roadmap, with producer-consumer schema alignment and a Tier 1 artifact existence gate. Phase 4 is sequenced before Phase 5 to satisfy the file-conflict constraint: Task 3.2 must complete before Task 2.4 (both modify adversarial-integration.md).

### T04.01 — Add Return Contract Write Instruction to sc:adversarial

**Roadmap Item ID(s):** R-014, R-015
**Why:** Without a write instruction, sc:adversarial has no mechanism to transport structured results back to sc:roadmap. The return contract schema defines the 9-field interface between producer and consumer. Dead code removal (subagent_type lines) is appended to this task to be completed in the same editing session.
**Effort:** `L`
**Risk:** `Medium`
**Risk Drivers:** data (schema)
**Tier:** `STRICT`
**Confidence:** `[███-------] 34%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Sub-agent (quality-engineer), 3-5K tokens, 60s
**MCP Requirements:** `Required: Sequential, Serena | Preferred: Context7`
**Fallback Allowed:** `No`
**Sub-Agent Delegation:** `Recommended`
**Deliverable IDs:** D-0011, D-0012
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0011/spec.md`
- `TASKLIST_ROOT/tasklist/artifacts/D-0012/evidence.md`

**Deliverables:**
1. "Return Contract (MANDATORY)" section as final pipeline step in `src/superclaude/skills/sc-adversarial/SKILL.md` with 9 fields: schema_version, status, convergence_score, merged_output_path, artifacts_dir, unresolved_conflicts (integer), base_variant, failure_stage, fallback_mode. YAML null for unreached values. Write-on-failure instruction. Example YAML block.
2. Dead code removal: both `subagent_type: "general-purpose"` lines deleted from `task_dispatch_config` YAML blocks

**Steps:**
1. **[PLANNING]** Read `src/superclaude/skills/sc-adversarial/SKILL.md`; locate the end of the pipeline steps and the two `subagent_type` lines
2. **[PLANNING]** Confirm `unresolved_conflicts` type resolution: integer (per reflection-final.md IMP-06), overriding current line 349 `list[string]`
3. **[EXECUTION]** Add "Return Contract (MANDATORY)" section with 9 field definitions, null semantics, write-on-failure instruction, and example YAML block
4. **[EXECUTION]** Delete both `subagent_type: "general-purpose"` lines from `task_dispatch_config` blocks
5. **[VERIFICATION]** Verify: section exists as final step, 9 fields defined, null used for unreached values, write-on-failure explicit, `fallback_mode` field present, example YAML provided
6. **[VERIFICATION]** Run: `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` — expect 0
7. **[COMPLETION]** Document schema and dead code removal in D-0011, D-0012 artifacts

**Acceptance Criteria:**
- "Return Contract (MANDATORY)" section exists as final pipeline step with all 9 fields
- YAML null (`~`) used for unreached values (not -1 or "")
- Write-on-failure instruction is explicit; example YAML block provided
- `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` returns 0

**Validation:**
- Manual check: 9 fields present with correct types; null semantics correct; write-on-failure instruction explicit
- Evidence: D-0011 spec artifact; D-0012 evidence artifact with grep output

**Dependencies:** T01.02
**Rollback:** TBD
**Notes:** `unresolved_conflicts` type resolved from `list[string]` to `integer` per reflection-final.md IMP-06. Tier conflict: STRICT (0.4 from "schema") vs STANDARD (0.4 from "add"+"remove") → resolved to STRICT by priority rule.

---

### T04.02 — Add Return Contract Consumption Section to adversarial-integration.md

**Roadmap Item ID(s):** R-016
**Why:** The consumer side must know how to read, validate, and route on the return contract produced by sc:adversarial. Without this section, step 3e has no reference for implementation.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** data (schema)
**Tier:** `STRICT`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Sub-agent (quality-engineer), 3-5K tokens, 60s
**MCP Requirements:** `Required: Sequential, Serena | Preferred: Context7`
**Fallback Allowed:** `No`
**Sub-Agent Delegation:** `Recommended`
**Deliverable IDs:** D-0013
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0013/spec.md`

**Deliverables:**
1. "Return Contract Consumption" section in `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` with: read instruction, schema_version validation, three-status routing (success/partial/failed), missing-file guard, convergence threshold 0.6, `fallback_mode` routing with differentiated user warning, and example YAML blocks for success and failure

**Steps:**
1. **[PLANNING]** Read `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`; identify insertion point
2. **[PLANNING]** Cross-reference T04.01's 9-field schema to ensure consumer-producer alignment
3. **[EXECUTION]** Add "Return Contract Consumption" section with read instruction, schema_version validation, three-status routing, missing-file guard, convergence threshold 0.6
4. **[EXECUTION]** Add `fallback_mode` differentiated warning: "Output produced by degraded fallback (single-round debate, no convergence tracking). Quality is substantially reduced compared to full adversarial pipeline."
5. **[EXECUTION]** Add example YAML blocks for success and failure return contracts
6. **[VERIFICATION]** Verify all 7 required elements present: read instruction, schema_version validation, three-status routing, missing-file guard, convergence threshold, fallback_mode routing, example YAML
7. **[COMPLETION]** Document consumption section in D-0013 artifact

**Acceptance Criteria:**
- Read instruction, schema_version validation, and three-status routing are present
- Missing-file guard treats absent file as `status: failed, failure_stage: 'transport'`
- Convergence threshold specified as 0.6 (60%)
- `fallback_mode: true` routing includes differentiated user warning distinct from `status: partial`

**Validation:**
- Manual check: All 7 elements present; consumer field references match producer schema
- Evidence: D-0013 spec artifact with section content

**Dependencies:** T04.01
**Rollback:** TBD
**Notes:** Must complete before T05.03 (file-conflict constraint on adversarial-integration.md).

---

### T04.03 — Add Post-Adversarial Artifact Existence Gate (Tier 1)

**Roadmap Item ID(s):** R-017
**Why:** Provides pre-YAML-parsing defense against timeout/context-exhaustion scenarios where the return contract may never be written. The gate checks artifact existence before attempting YAML parsing.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** `Required: None | Preferred: Sequential, Context7`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** D-0014
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0014/spec.md`

**Deliverables:**
1. "Post-Adversarial Artifact Existence Gate (Tier 1)" section in `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` with 4 sequential checks, each with defined failure treatment, positioned before YAML parsing, using path variable references

**Steps:**
1. **[PLANNING]** Read `adversarial-integration.md`; identify position before Return Contract Consumption section (YAML parsing)
2. **[PLANNING]** Confirm 4 check targets: directory existence, diff-analysis.md, merged-output.md, return-contract.yaml
3. **[EXECUTION]** Add "Post-Adversarial Artifact Existence Gate (Tier 1)" section with 4 sequential checks using path variables (`<output-dir>/adversarial/`)
4. **[EXECUTION]** Define failure treatments: check 1 → `status: failed, failure_stage: "pipeline_not_started"`; check 2 → `failure_stage: "diff_analysis"`; check 3 → `status: partial, convergence_score: 0.0`; check 4 → apply missing-file guard from T04.02
5. **[VERIFICATION]** Verify: section heading exists, positioned before YAML parsing, 4 checks in order, path variables used, failure treatments defined
6. **[COMPLETION]** Document gate structure in D-0014 artifact

**Acceptance Criteria:**
- Section heading "Post-Adversarial Artifact Existence Gate (Tier 1)" exists
- 4 existence checks in specified order with correct failure treatments
- Gate positioned before YAML parsing in the Return Contract Consumption section
- Path variable references used throughout (not hardcoded literals)

**Validation:**
- Manual check: 7-point checklist (per Verification Test 6) passes
- Evidence: D-0014 spec artifact

**Dependencies:** T04.02
**Rollback:** TBD

---

### Checkpoint: End of Phase 4

**Purpose:** Confirm return contract producer and consumer are aligned before specification rewrite.
**Checkpoint Report Path:** `TASKLIST_ROOT/tasklist/checkpoints/CP-P04-END.md`
**Verification:**
- Return Contract write instruction exists in sc:adversarial SKILL.md with 9 fields
- Return Contract Consumption section exists in adversarial-integration.md with status routing
- Tier 1 artifact existence gate exists and is positioned before YAML parsing

**Exit Criteria:**
- Producer (T04.01) and consumer (T04.02) field sets are aligned
- Zero `subagent_type` lines remain in sc:adversarial SKILL.md
- Phase 5 file-conflict dependency satisfied (T04.02 complete → T05.03 unblocked)

---

## Phase 5: Specification Rewrite with Executable Instructions

Eliminate specification ambiguity by adding a verb-to-tool execution vocabulary, fixing Wave 1A's "Invoke" ambiguity, and converting adversarial-integration.md from standalone pseudo-CLI syntax to Skill tool call format. Sequenced after Phase 4 to satisfy file-conflict constraint on adversarial-integration.md.

### T05.01 — Add Verb-to-Tool Execution Vocabulary Glossary

**Roadmap Item ID(s):** R-011
**Why:** Without a glossary, "Invoke" and other verbs are ambiguous — Claude cannot deterministically map specification language to tool calls. The glossary provides the missing translation layer.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** `Required: None | Preferred: Sequential, Context7`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** D-0015
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0015/spec.md`

**Deliverables:**
1. "Execution Vocabulary" glossary section before Wave 0 in `src/superclaude/skills/sc-roadmap/SKILL.md` with 4 mappings: "Invoke skill" = Skill tool, "Dispatch agent" = Task tool, "Read ref" = Read tool, "Write artifact" = Write tool. Scope statement present.

**Steps:**
1. **[PLANNING]** Read `src/superclaude/skills/sc-roadmap/SKILL.md`; locate insertion point before Wave 0
2. **[PLANNING]** Identify all verbs used in Wave 0–4 and fallback protocol F1–F5 that need glossary entries
3. **[EXECUTION]** Insert "Execution Vocabulary" section with mapping table (4 entries) and scope statement: "This glossary covers tool-call verbs used in pipeline orchestration steps (Wave 0-4). It does NOT cover prose descriptions, comments, or documentation references."
4. **[EXECUTION]** Verify every verb in Wave 0–4 and F1–F5 appears in glossary
5. **[VERIFICATION]** Count glossary entries; verify scope statement; verify position before Wave 0
6. **[COMPLETION]** Document glossary in D-0015 artifact

**Acceptance Criteria:**
- Glossary section exists before Wave 0 with 4 verb-to-tool mappings
- Scope statement present per T02-G6
- Every verb used in Wave 0–4 appears in the glossary
- Glossary verbs also cover fallback protocol steps F1–F5

**Validation:**
- Manual check: Glossary present before Wave 0 with 4 mappings and scope statement
- Evidence: D-0015 spec artifact

**Dependencies:** T02.03
**Rollback:** TBD

---

### T05.02 — Fix Wave 1A Step 2 "Invoke" Ambiguity

**Roadmap Item ID(s):** R-012
**Why:** Wave 1A step 2 uses bare "Invoke sc:adversarial" without specifying which tool to use. This creates the same ambiguity that caused the original pipeline failure.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** `Required: None | Preferred: Sequential, Context7`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** D-0016
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0016/spec.md`

**Deliverables:**
1. Wave 1A step 2 rewritten with Skill tool call pattern matching Wave 2 step 3d, including fallback protocol and glossary-consistent verb

**Steps:**
1. **[PLANNING]** Read Wave 1A step 2 in `src/superclaude/skills/sc-roadmap/SKILL.md`; identify the "Invoke sc:adversarial" text
2. **[PLANNING]** Reference T02.03's step 3d pattern as the template for replacement
3. **[EXECUTION]** Replace "Invoke sc:adversarial" with Skill tool call pattern: `skill: "sc:adversarial"` with appropriate args for the `--specs` path
4. **[EXECUTION]** Add the same fallback protocol from step 3d
5. **[VERIFICATION]** Verify Wave 1A step 2 uses glossary-consistent verb and matches Wave 2 pattern
6. **[COMPLETION]** Document change in D-0016 artifact

**Acceptance Criteria:**
- "Invoke sc:adversarial" replaced with Skill tool call pattern
- Fallback protocol present in Wave 1A step 2
- Glossary-consistent verb used
- Pattern matches Wave 2 step 3d

**Validation:**
- Manual check: Wave 1A step 2 uses Skill tool call syntax matching step 3d pattern
- Evidence: D-0016 spec artifact

**Dependencies:** T05.01
**Rollback:** TBD

---

### T05.03 — Convert adversarial-integration.md Pseudo-CLI Invocation Patterns

**Roadmap Item ID(s):** R-013
**Why:** Standalone pseudo-CLI syntax (`sc:adversarial --compare --depth`) is not executable by Claude Code. Converting to Skill tool call format eliminates the ambiguity.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None
**Tier:** `STANDARD`
**Confidence:** `[████------] 40%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** `Required: None | Preferred: Sequential, Context7`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** D-0017
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0017/evidence.md`

**Deliverables:**
1. All standalone pseudo-CLI invocation examples in `adversarial-integration.md` converted to Skill tool call format (`skill: "sc:adversarial", args: "..."`); both Multi-Spec Consolidation and Multi-Roadmap Generation subsections covered

**Steps:**
1. **[PLANNING]** Read `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`; identify all standalone `sc:adversarial --` invocation patterns
2. **[PLANNING]** Confirm file-conflict dependency: T04.02 must be complete (adversarial-integration.md already has Return Contract Consumption section)
3. **[EXECUTION]** Convert each standalone invocation example to Skill tool call format with `skill` and `args` fields. `--flag` syntax within `args: "..."` is correct and expected — do NOT remove flags from within args strings.
4. **[EXECUTION]** Cover both Multi-Spec Consolidation and Multi-Roadmap Generation subsections
5. **[VERIFICATION]** Run: `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` — expect 0
6. **[COMPLETION]** Record grep result in D-0017 artifact

**Acceptance Criteria:**
- All standalone invocation examples wrapped in Skill tool call format
- `args` strings within Skill tool calls MAY contain `--flag` syntax (this is correct)
- `grep -c "sc:adversarial --" adversarial-integration.md` returns 0
- Both Multi-Spec Consolidation and Multi-Roadmap Generation subsections covered

**Validation:**
- `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` returns 0
- Evidence: D-0017 evidence artifact with grep output

**Dependencies:** T04.02, T05.01
**Rollback:** TBD
**Notes:** File-conflict dependency: T04.02 (adds new section to adversarial-integration.md) must complete before this task (modifies existing sections in the same file).

---

### Checkpoint: End of Phase 5

**Purpose:** Confirm specification rewrite is complete and all pseudo-CLI syntax eliminated before integration validation.
**Checkpoint Report Path:** `TASKLIST_ROOT/tasklist/checkpoints/CP-P05-END.md`
**Verification:**
- Execution vocabulary glossary exists before Wave 0 with 4 mappings
- Wave 1A step 2 uses Skill tool call pattern (no bare "Invoke")
- Zero standalone `sc:adversarial --` patterns remain in adversarial-integration.md

**Exit Criteria:**
- All glossary verbs are used consistently in Wave 0–4 and F1–F5
- Pseudo-CLI elimination verified by grep returning 0
- No specification ambiguity remains in sc:roadmap's invocation instructions

---

## Phase 6: Integration Validation & Acceptance

Validate end-to-end pipeline functionality, schema consistency between producer and consumer, all Definition of Done criteria, and sync/quality gates before sprint completion. All tasks except T06.05 are read-only verification.

### T06.01 — Return Contract Schema Consistency Test

**Roadmap Item ID(s):** R-018
**Why:** Producer (sc:adversarial) and consumer (adversarial-integration.md) must have identical field sets to prevent runtime mismatches.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** data (schema)
**Tier:** `EXEMPT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** `No`
**Critical Path Override:** `No`
**Verification Method:** Skip verification (EXEMPT)
**MCP Requirements:** `Required: None | Preferred: None`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** D-0018
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0018/evidence.md`

**Deliverables:**
1. Schema consistency test result confirming producer and consumer field sets are identical

**Steps:**
1. **[PLANNING]** Identify field extraction locations in both producer and consumer files
2. **[EXECUTION]** Extract field names from producer: sc:adversarial SKILL.md "Return Contract (MANDATORY)" section
3. **[EXECUTION]** Extract field names from consumer: adversarial-integration.md "Return Contract Consumption" section
4. **[EXECUTION]** Diff the two field sets; verify `base_variant`, `failure_stage`, and cross-reference comments present in both
5. **[COMPLETION]** Record diff result in D-0018 artifact

**Acceptance Criteria:**
- Identical field sets in both producer and consumer files
- `base_variant` present in both; `failure_stage` present in both
- Cross-reference comments present in both
- `unresolved_conflicts` typed as `integer` in both

**Validation:**
- Manual check: Field-by-field comparison shows exact match
- Evidence: D-0018 artifact with extracted field lists and diff result

**Dependencies:** T04.01, T04.02
**Rollback:** TBD

---

### T06.02 — Cross-Reference Field Consistency Test

**Roadmap Item ID(s):** R-019
**Why:** Fields referenced in Wave 2 step 3e (consumer) must exist in the producer schema. Convergence threshold must be consistent between step 3e and adversarial-integration.md.
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
**Deliverable IDs:** D-0019
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0019/evidence.md`

**Deliverables:**
1. Cross-reference validation result confirming all consumer-referenced fields exist in producer schema and thresholds are consistent

**Steps:**
1. **[PLANNING]** Identify all fields referenced in Wave 2 step 3e
2. **[EXECUTION]** List fields referenced by consumer (step 3e): status, convergence_score, etc.
3. **[EXECUTION]** List fields defined by producer (sc:adversarial Return Contract section)
4. **[EXECUTION]** Confirm every consumer-referenced field exists in producer schema; confirm convergence threshold consistency (0.6 in step 3e matches 60% in adversarial-integration.md)
5. **[COMPLETION]** Record cross-reference results in D-0019 artifact

**Acceptance Criteria:**
- Every field referenced in step 3e exists in the producer schema
- Convergence threshold is consistent: 0.6 in step 3e = 60% in adversarial-integration.md
- No orphaned field references in either direction
- Evidence documented with specific field-by-field mapping

**Validation:**
- Manual check: All consumer-referenced fields exist in producer schema; thresholds match
- Evidence: D-0019 artifact with cross-reference mapping

**Dependencies:** T02.03, T04.01
**Rollback:** TBD

---

### T06.03 — Pseudo-CLI Elimination Test

**Roadmap Item ID(s):** R-020
**Why:** Confirms no residual pseudo-CLI invocation syntax remains after T05.03's conversion.
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
**Deliverable IDs:** D-0020
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0020/evidence.md`

**Deliverables:**
1. Grep test result confirming zero standalone `sc:adversarial --` patterns remain

**Steps:**
1. **[PLANNING]** Identify target file and grep pattern
2. **[EXECUTION]** Run: `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`
3. **[COMPLETION]** Record result in D-0020 artifact — expect 0

**Acceptance Criteria:**
- Grep returns 0 matches
- Result documented with exact command output
- Test covers the correct file path
- Evidence traceable to D-0020

**Validation:**
- `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` returns 0
- Evidence: D-0020 artifact with grep output

**Dependencies:** T05.03
**Rollback:** TBD

---

### T06.04 — Tier 1 Quality Gate Structure Audit

**Roadmap Item ID(s):** R-021
**Why:** Confirms the artifact existence gate is correctly positioned and contains all required checks before the sprint's structural integrity is accepted.
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
**Deliverable IDs:** D-0021
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0021/evidence.md`

**Deliverables:**
1. 7-point checklist result for Verification Test 6

**Steps:**
1. **[PLANNING]** Load the 7-point checklist from Verification Test 6 specification
2. **[EXECUTION]** Check 1: Locate "Post-Adversarial Artifact Existence Gate (Tier 1)" section heading
3. **[EXECUTION]** Check 2–3: Confirm section appears BEFORE YAML parsing instructions; confirm check 1 targets directory existence with `failure_stage: "pipeline_not_started"`
4. **[EXECUTION]** Check 4–6: Confirm check 2 targets diff-analysis.md, check 3 targets merged-output.md with `status: partial`, check 4 targets return-contract.yaml with missing-file guard
5. **[EXECUTION]** Check 7: Confirm all path references use variable form (`<output-dir>/adversarial/`)
6. **[COMPLETION]** Record all 7 checklist items with pass/fail in D-0021 artifact

**Acceptance Criteria:**
- All 7 checklist items pass
- Section is positioned before YAML parsing
- Path variables used throughout (not hardcoded literals)
- All 4 existence checks have defined failure treatments

**Validation:**
- Manual check: 7-point checklist fully completed with all items passing
- Evidence: D-0021 artifact with audit results

**Dependencies:** T04.03
**Rollback:** TBD

---

### T06.05 — Sync and Quality Gates

**Roadmap Item ID(s):** R-022
**Why:** Final validation that all changes are properly synced between `src/` and `.claude/`, no tests are broken, linting passes, and remaining DoD criteria are met.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None
**Tier:** `STANDARD`
**Confidence:** `[██████----] 60%`
**Requires Confirmation:** `Yes`
**Critical Path Override:** `No`
**Verification Method:** Direct test execution (300-500 tokens, 30s)
**MCP Requirements:** `Required: None | Preferred: Sequential, Context7`
**Fallback Allowed:** `Yes`
**Sub-Agent Delegation:** `None`
**Deliverable IDs:** D-0022
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/tasklist/artifacts/D-0022/evidence.md`

**Deliverables:**
1. Sync and quality gates result: `make sync-dev && make verify-sync` passes, `uv run pytest` passes (no regressions), `make lint` passes, every glossary verb used in Wave 0–4, zero `subagent_type` lines remain

**Steps:**
1. **[PLANNING]** Identify all quality gate commands and DoD checks
2. **[EXECUTION]** Run: `make sync-dev && make verify-sync` — expect success
3. **[EXECUTION]** Run: `uv run pytest` — expect all tests pass (no regressions)
4. **[EXECUTION]** Run: `make lint` — expect pass
5. **[EXECUTION]** Verify: every glossary verb appears in Wave 0–4; `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` returns 0
6. **[VERIFICATION]** Confirm all DoD criteria from roadmap are met
7. **[COMPLETION]** Record all gate results in D-0022 artifact

**Acceptance Criteria:**
- `make sync-dev && make verify-sync` passes (`.claude/` mirrors match `src/superclaude/`)
- `uv run pytest` passes with no regressions
- `make lint` passes
- Zero `subagent_type` lines remain in any modified file

**Validation:**
- `make sync-dev && make verify-sync && uv run pytest && make lint` — all exit code 0
- Evidence: D-0022 artifact with command outputs

**Dependencies:** T06.01, T06.02, T06.03, T06.04
**Rollback:** TBD

---

### Checkpoint: End of Phase 6

**Purpose:** Confirm all validation tests pass and sprint is ready for acceptance.
**Checkpoint Report Path:** `TASKLIST_ROOT/tasklist/checkpoints/CP-P06-END.md`
**Verification:**
- Verification Tests 3, 3.5, 4, 6 all pass (T06.01–T06.04)
- Sync and quality gates pass (T06.05)
- All Definition of Done criteria from roadmap are satisfied

**Exit Criteria:**
- All 18 tasks completed with evidence artifacts
- All 6 phase checkpoints passed
- Sprint ready for end-to-end invocation test (Verification Test 5 — post-sprint, manual)

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
